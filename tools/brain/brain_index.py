#!/usr/bin/env python3
"""Portable semantic and hybrid search CLI for the brain repository.

Uses Google's flagship gemini-embedding-2 model via the Gemini API to generate
dense embeddings (768 dimensions), paired with SQLite BLOB storage and FTS5
for sub-millisecond local vector and full-text search.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import numpy as np
except ImportError:
    sys.exit("Error: 'numpy' is required. Install with: pip install numpy")

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("Error: 'google-genai' is required. Install with: pip install google-genai")


sys.path.insert(0, str(Path(__file__).resolve().parent))
from brain_repo import get_brain_root

REPO_ROOT = get_brain_root()
CACHE_DIR = REPO_ROOT / "agent" / "cache"
DB_PATH = CACHE_DIR / "brain-index.db"

DEFAULT_MODEL = "gemini-embedding-2"
DEFAULT_DIMS = 768
DEFAULT_WORKERS = 5
DEFAULT_SEARCH_LIMIT = 5

DEFAULT_INDEX_DIRS = (
    "notes",
    "profile",
    "projects",
    "skills",
    "discussions",
    "agent/context",
    "agent/model",
    "cowork",
    "journal",
    "inbox",
)

EXCLUDE_PATTERNS = (
    "/.git/",
    "/.obsidian/",
    "/agent/cache/",
    "/agent/tools/",
    "/.system_generated/",
    "/node_modules/",
    "/dist/",
)


@dataclass
class MarkdownChunk:
    rel_path: str
    chunk_index: int
    heading: str
    start_line: int
    end_line: int
    content: str
    content_hash: str


# -----------------------------------------------------------------------------
# Database Schema & Management
# -----------------------------------------------------------------------------

def get_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Connect to SQLite and ensure the schema exists."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rel_path TEXT UNIQUE NOT NULL,
                file_hash TEXT NOT NULL,
                mtime REAL NOT NULL,
                title TEXT,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                indexed_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                rel_path TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                heading TEXT,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                embedding BLOB NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
            CREATE INDEX IF NOT EXISTS idx_chunks_rel_path ON chunks(rel_path);

            CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(
                heading,
                rel_path,
                content,
                tokenize = 'porter unicode61'
            );
        """)

        # Set default meta if empty
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', '1')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('model_name', ?)",
            (DEFAULT_MODEL,),
        )
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('dimensions', ?)",
            (str(DEFAULT_DIMS),),
        )

    return conn


def get_meta_value(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    cur = conn.execute("SELECT value FROM meta WHERE key = ?", (key,))
    row = cur.fetchone()
    return row[0] if row else default


def set_meta_value(conn: sqlite3.Connection, key: str, value: str) -> None:
    with conn:
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


# -----------------------------------------------------------------------------
# Markdown Chunking
# -----------------------------------------------------------------------------

def chunk_markdown(
    content: str,
    rel_path: str,
    min_chars: int = 60,
    max_chars: int = 3000,
) -> tuple[str, list[MarkdownChunk]]:
    """Parse Markdown content into structural, heading-bounded chunks."""
    lines = content.splitlines()
    if not lines:
        return rel_path, []

    # Extract title from # Title or filename
    title = Path(rel_path).stem
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    raw_sections: list[dict[str, Any]] = []
    current_heading = title
    current_lines: list[str] = []
    start_line = 1

    for idx, line in enumerate(lines, 1):
        if re.match(r"^#{1,3}\s+", line) and current_lines:
            chunk_text = "\n".join(current_lines).strip()
            if chunk_text:
                raw_sections.append({
                    "heading": current_heading,
                    "start_line": start_line,
                    "end_line": idx - 1,
                    "content": chunk_text,
                })
            current_heading = re.sub(r"^#{1,3}\s+", "", line).strip()
            current_lines = [line]
            start_line = idx
        else:
            current_lines.append(line)

    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if chunk_text:
            raw_sections.append({
                "heading": current_heading,
                "start_line": start_line,
                "end_line": len(lines),
                "content": chunk_text,
            })

    # Merge tiny header-only sections (< min_chars) forward
    merged_sections: list[dict[str, Any]] = []
    for s in raw_sections:
        if merged_sections and len(merged_sections[-1]["content"]) < min_chars:
            prev = merged_sections.pop()
            s["start_line"] = prev["start_line"]
            s["content"] = prev["content"] + "\n\n" + s["content"]
            if prev["heading"] != s["heading"]:
                s["heading"] = f"{prev['heading']} > {s['heading']}"
        merged_sections.append(s)

    # Subdivide any oversized sections (> max_chars) by paragraphs
    final_chunks: list[MarkdownChunk] = []
    chunk_index = 0

    for sec in merged_sections:
        sec_content = sec["content"]
        if len(sec_content) <= max_chars:
            chash = hashlib.sha256(sec_content.encode("utf-8")).hexdigest()
            final_chunks.append(
                MarkdownChunk(
                    rel_path=rel_path,
                    chunk_index=chunk_index,
                    heading=sec["heading"],
                    start_line=sec["start_line"],
                    end_line=sec["end_line"],
                    content=sec_content,
                    content_hash=chash,
                )
            )
            chunk_index += 1
        else:
            paragraphs = sec_content.split("\n\n")
            cur_p_lines: list[str] = []
            cur_p_start = sec["start_line"]
            running_len = 0

            for p in paragraphs:
                p_len = len(p)
                if running_len + p_len > max_chars and cur_p_lines:
                    p_content = "\n\n".join(cur_p_lines).strip()
                    p_end = cur_p_start + len(p_content.splitlines()) - 1
                    chash = hashlib.sha256(p_content.encode("utf-8")).hexdigest()
                    final_chunks.append(
                        MarkdownChunk(
                            rel_path=rel_path,
                            chunk_index=chunk_index,
                            heading=sec["heading"],
                            start_line=cur_p_start,
                            end_line=p_end,
                            content=p_content,
                            content_hash=chash,
                        )
                    )
                    chunk_index += 1
                    cur_p_start = p_end + 1
                    cur_p_lines = [p]
                    running_len = p_len
                else:
                    cur_p_lines.append(p)
                    running_len += p_len + 2

            if cur_p_lines:
                p_content = "\n\n".join(cur_p_lines).strip()
                p_end = sec["end_line"]
                chash = hashlib.sha256(p_content.encode("utf-8")).hexdigest()
                final_chunks.append(
                    MarkdownChunk(
                        rel_path=rel_path,
                        chunk_index=chunk_index,
                        heading=sec["heading"],
                        start_line=cur_p_start,
                        end_line=p_end,
                        content=p_content,
                        content_hash=chash,
                    )
                )
                chunk_index += 1

    return title, final_chunks


# -----------------------------------------------------------------------------
# Gemini Embedding Client
# -----------------------------------------------------------------------------

def get_gemini_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit(
            "Error: GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.\n"
            "Please ensure your API key is exported in your environment or ~/.zshrc.local."
        )
    return genai.Client(api_key=api_key)


def embed_text(
    client: genai.Client,
    text: str,
    model: str = DEFAULT_MODEL,
    dimensions: int = DEFAULT_DIMS,
) -> np.ndarray:
    """Generate a single embedding vector and return as an L2-normalized numpy array."""
    config = types.EmbedContentConfig(output_dimensionality=dimensions)
    response = client.models.embed_content(
        model=model,
        contents=text,
        config=config,
    )
    raw_vec = response.embeddings[0].values
    vec = np.array(raw_vec, dtype=np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def embed_chunks_batch(
    client: genai.Client,
    chunks: list[MarkdownChunk],
    model: str = DEFAULT_MODEL,
    dimensions: int = DEFAULT_DIMS,
    max_workers: int = DEFAULT_WORKERS,
) -> list[tuple[MarkdownChunk, bytes]]:
    """Embed chunks concurrently with context prefixes, returning (chunk, blob_bytes)."""
    def _worker(chunk: MarkdownChunk) -> tuple[MarkdownChunk, bytes]:
        # Context prefix grounds the embedding in its document and section
        prefixed = f"[Path: {chunk.rel_path} | Heading: {chunk.heading}]\n\n{chunk.content}"
        vec = embed_text(client, prefixed, model=model, dimensions=dimensions)
        return chunk, vec.tobytes()

    results: list[tuple[MarkdownChunk, bytes]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {pool.submit(_worker, c): c for c in chunks}
        for future in concurrent.futures.as_completed(future_map):
            chunk, blob = future.result()
            results.append((chunk, blob))

    # Preserve chunk order
    results.sort(key=lambda x: (x[0].rel_path, x[0].chunk_index))
    return results


# -----------------------------------------------------------------------------
# Document Indexing & Storage
# -----------------------------------------------------------------------------

def delete_document_index(conn: sqlite3.Connection, rel_path: str) -> None:
    """Delete all indexed data for a document, including chunks and FTS entries."""
    with conn:
        cur = conn.execute("SELECT id FROM documents WHERE rel_path = ?", (rel_path,))
        row = cur.fetchone()
        if not row:
            return
        doc_id = row[0]

        # Delete from FTS
        chunk_cur = conn.execute("SELECT id FROM chunks WHERE doc_id = ?", (doc_id,))
        for c_row in chunk_cur.fetchall():
            conn.execute("DELETE FROM fts_chunks WHERE rowid = ?", (c_row[0],))

        # Cascade deletes chunks
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))


def index_single_document(
    conn: sqlite3.Connection,
    client: genai.Client,
    abs_path: Path,
    rel_path: str,
    model: str = DEFAULT_MODEL,
    dimensions: int = DEFAULT_DIMS,
) -> int:
    """Parse, embed, and store a single document. Returns the number of chunks indexed."""
    try:
        content = abs_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [!] Failed to read {rel_path}: {e}", file=sys.stderr)
        return 0

    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    mtime = abs_path.stat().st_mtime
    title, chunks = chunk_markdown(content, rel_path)

    if not chunks:
        # File is empty or no valid chunks
        delete_document_index(conn, rel_path)
        return 0

    # Delete existing index if replacing
    delete_document_index(conn, rel_path)

    # Embed chunks
    embedded = embed_chunks_batch(
        client, chunks, model=model, dimensions=dimensions
    )

    with conn:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cur = conn.execute(
            """
            INSERT INTO documents (rel_path, file_hash, mtime, title, chunk_count, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (rel_path, file_hash, mtime, title, len(embedded), now_iso),
        )
        doc_id = cur.lastrowid

        for chunk, blob in embedded:
            c_cur = conn.execute(
                """
                INSERT INTO chunks (doc_id, rel_path, chunk_index, heading, start_line, end_line, content, content_hash, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id,
                    chunk.rel_path,
                    chunk.chunk_index,
                    chunk.heading,
                    chunk.start_line,
                    chunk.end_line,
                    chunk.content,
                    chunk.content_hash,
                    blob,
                ),
            )
            chunk_rowid = c_cur.lastrowid
            conn.execute(
                "INSERT INTO fts_chunks (rowid, heading, rel_path, content) VALUES (?, ?, ?, ?)",
                (chunk_rowid, chunk.heading, chunk.rel_path, chunk.content),
            )

    return len(embedded)


# -----------------------------------------------------------------------------
# Sweep & Discovery
# -----------------------------------------------------------------------------

def find_markdown_files(
    repo_root: Path = REPO_ROOT,
    include_archive: bool = False,
) -> list[tuple[Path, str]]:
    """Find all eligible Markdown files in the repository."""
    candidates: list[tuple[Path, str]] = []

    for prefix in DEFAULT_INDEX_DIRS:
        dir_path = repo_root / prefix
        if not dir_path.exists():
            continue
        for p in dir_path.rglob("*.md"):
            rel_str = str(p.relative_to(repo_root))
            if any(ex in f"/{rel_str}" for ex in EXCLUDE_PATTERNS):
                continue
            if not include_archive and rel_str.startswith("archive/"):
                continue
            candidates.append((p, rel_str))

    # Also include root-level durable markdown files like AGENTS.md, README.md, CLAUDE.md
    for root_file in ["AGENTS.md", "README.md", "CLAUDE.md"]:
        p = repo_root / root_file
        if p.is_file():
            candidates.append((p, root_file))

    # Deduplicate and sort
    seen = set()
    result = []
    for abs_p, rel_p in sorted(candidates, key=lambda x: x[1]):
        if rel_p not in seen:
            seen.add(rel_p)
            result.append((abs_p, rel_p))

    return result


def cmd_sweep(
    conn: sqlite3.Connection,
    client: genai.Client,
    force: bool = False,
    include_archive: bool = False,
) -> None:
    """Sweep the entire repository, embedding new/modified docs and pruning deleted ones."""
    model = get_meta_value(conn, "model_name", DEFAULT_MODEL) or DEFAULT_MODEL
    dims = int(get_meta_value(conn, "dimensions", str(DEFAULT_DIMS)) or DEFAULT_DIMS)

    # Check model compatibility
    if force:
        print("[*] Force flag active: clearing all existing embeddings...")
        cmd_purge(conn, silent=True)
        conn = get_db()

    all_files = find_markdown_files(REPO_ROOT, include_archive=include_archive)
    on_disk_map = {rel_p: abs_p for abs_p, rel_p in all_files}

    # Fetch currently indexed documents
    cur = conn.execute("SELECT rel_path, file_hash, mtime FROM documents")
    db_docs = {row[0]: (row[1], row[2]) for row in cur.fetchall()}

    to_index: list[tuple[Path, str]] = []
    unchanged_count = 0

    for rel_p, abs_p in on_disk_map.items():
        try:
            content = abs_p.read_text(encoding="utf-8")
            cur_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        except Exception:
            continue

        if rel_p not in db_docs:
            to_index.append((abs_p, rel_p))
        elif db_docs[rel_p][0] != cur_hash:
            to_index.append((abs_p, rel_p))
        else:
            unchanged_count += 1

    # Prune deleted files
    deleted_paths = [rel_p for rel_p in db_docs if rel_p not in on_disk_map]
    for del_p in deleted_paths:
        delete_document_index(conn, del_p)

    print(
        f"[*] Found {len(on_disk_map)} markdown files on disk:\n"
        f"    - {len(to_index)} to index/re-index\n"
        f"    - {unchanged_count} unchanged\n"
        f"    - {len(deleted_paths)} pruned from index"
    )

    if not to_index:
        print("[✓] Brain vector store is fully up to date.")
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        set_meta_value(conn, "last_sweep", now_iso)
        return

    total_chunks_added = 0
    t0 = time.perf_counter()

    for idx, (abs_p, rel_p) in enumerate(to_index, 1):
        print(f"  [{idx}/{len(to_index)}] Indexing: {rel_p} ...", end=" ", flush=True)
        c_count = index_single_document(
            conn, client, abs_p, rel_p, model=model, dimensions=dims
        )
        total_chunks_added += c_count
        print(f"({c_count} chunks)")

    t1 = time.perf_counter()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    set_meta_value(conn, "last_sweep", now_iso)

    print(
        f"\n[✓] Sweep complete: indexed {len(to_index)} files ({total_chunks_added} chunks) "
        f"in {t1 - t0:.2f}s."
    )


# -----------------------------------------------------------------------------
# Search & Query
# -----------------------------------------------------------------------------

@dataclass
class SearchResult:
    score: float
    rel_path: str
    heading: str
    start_line: int
    end_line: int
    content: str
    match_source: str


def search_vectors(
    conn: sqlite3.Connection,
    client: genai.Client,
    query: str,
    limit: int = 10,
    model: str = DEFAULT_MODEL,
    dimensions: int = DEFAULT_DIMS,
) -> list[SearchResult]:
    """Perform dense vector cosine similarity search."""
    cur = conn.execute("SELECT id, rel_path, heading, start_line, end_line, content, embedding FROM chunks")
    rows = cur.fetchall()
    if not rows:
        return []

    # Embed query
    query_vec = embed_text(client, query, model=model, dimensions=dimensions)

    chunk_ids = []
    metadata = []
    vector_list = []

    for r in rows:
        chunk_ids.append(r[0])
        metadata.append((r[1], r[2], r[3], r[4], r[5]))
        vec = np.frombuffer(r[6], dtype=np.float32)
        vector_list.append(vec)

    matrix = np.vstack(vector_list)
    scores = np.dot(matrix, query_vec)

    top_indices = np.argsort(scores)[::-1][:limit]
    results = []
    for idx in top_indices:
        rel_p, heading, start_l, end_l, content = metadata[idx]
        results.append(
            SearchResult(
                score=float(scores[idx]),
                rel_path=rel_p,
                heading=heading,
                start_line=start_l,
                end_line=end_l,
                content=content,
                match_source="vector",
            )
        )
    return results


def search_fts(
    conn: sqlite3.Connection,
    query: str,
    limit: int = 10,
) -> list[SearchResult]:
    """Perform full-text keyword search via SQLite FTS5."""
    clean_q = re.sub(r'[^\w\s\u4e00-\u9fff]', " ", query).strip()
    if not clean_q:
        return []

    terms = clean_q.split()
    fts_query = " OR ".join(f'"{t}"' for t in terms)

    try:
        cur = conn.execute(
            """
            SELECT c.rel_path, c.heading, c.start_line, c.end_line, c.content, bm25(fts_chunks)
            FROM fts_chunks
            JOIN chunks c ON fts_chunks.rowid = c.id
            WHERE fts_chunks MATCH ?
            ORDER BY bm25(fts_chunks)
            LIMIT ?
            """,
            (fts_query, limit),
        )
        rows = cur.fetchall()
    except sqlite3.OperationalError:
        return []

    results = []
    for row in rows:
        bm25_score = float(row[5])
        norm_score = max(0.0, 1.0 / (1.0 + max(0.0, -bm25_score)))
        results.append(
            SearchResult(
                score=norm_score,
                rel_path=row[0],
                heading=row[1],
                start_line=row[2],
                end_line=row[3],
                content=row[4],
                match_source="text",
            )
        )
    return results


def search_hybrid(
    conn: sqlite3.Connection,
    client: genai.Client,
    query: str,
    limit: int = 5,
    model: str = DEFAULT_MODEL,
    dimensions: int = DEFAULT_DIMS,
) -> list[SearchResult]:
    """Combine vector search and FTS keyword search using Reciprocal Rank Fusion (RRF)."""
    vec_results = search_vectors(
        conn, client, query, limit=limit * 2, model=model, dimensions=dimensions
    )
    fts_results = search_fts(conn, query, limit=limit * 2)

    # RRF scoring: RRF(doc) = sum(1 / (60 + rank_i))
    scores: dict[tuple[str, int, int], float] = {}
    item_map: dict[tuple[str, int, int], SearchResult] = {}

    for rank, res in enumerate(vec_results):
        key = (res.rel_path, res.start_line, res.end_line)
        scores[key] = scores.get(key, 0.0) + (1.0 / (60.0 + rank))
        item_map[key] = res

    for rank, res in enumerate(fts_results):
        key = (res.rel_path, res.start_line, res.end_line)
        scores[key] = scores.get(key, 0.0) + (1.0 / (60.0 + rank))
        if key not in item_map:
            item_map[key] = res
        else:
            item_map[key].match_source = "hybrid"

    ranked_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:limit]
    final_results = []
    for k in ranked_keys:
        res = item_map[k]
        res.score = scores[k]
        final_results.append(res)

    return final_results


def cmd_search(
    conn: sqlite3.Connection,
    client: genai.Client,
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
    mode: str = "hybrid",
    as_json: bool = False,
    min_score: float = 0.0,
) -> None:
    """Execute a search and render results formatted for human or agent consumption."""
    model = get_meta_value(conn, "model_name", DEFAULT_MODEL) or DEFAULT_MODEL
    dims = int(get_meta_value(conn, "dimensions", str(DEFAULT_DIMS)) or DEFAULT_DIMS)

    if mode == "vector":
        results = search_vectors(conn, client, query, limit=limit, model=model, dimensions=dims)
    elif mode == "text":
        results = search_fts(conn, query, limit=limit)
    else:
        results = search_hybrid(conn, client, query, limit=limit, model=model, dimensions=dims)

    if min_score > 0.0:
        results = [r for r in results if r.score >= min_score]

    if as_json:
        payload = [
            {
                "score": round(r.score, 4),
                "rel_path": r.rel_path,
                "abs_path": str(REPO_ROOT / r.rel_path),
                "heading": r.heading,
                "start_line": r.start_line,
                "end_line": r.end_line,
                "match_source": r.match_source,
                "content": r.content,
            }
            for r in results
        ]
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    if not results:
        print(f"No results found for query: '{query}'")
        return

    print(f"\n🔍 Search results for: \"{query}\" (mode: {mode}, top {len(results)}):\n")
    for idx, r in enumerate(results, 1):
        abs_p = (REPO_ROOT / r.rel_path).resolve()
        link_str = f"[{r.rel_path}#L{r.start_line}-L{r.end_line}](file://{abs_p}#L{r.start_line}-L{r.end_line})"
        print(f"{idx}. {link_str}")
        print(f"   Score: {r.score:.4f} | Section: {r.heading} | Mode: {r.match_source}")

        preview_lines = [l.strip() for l in r.content.splitlines() if l.strip()]
        snippet = " ".join(preview_lines[:3])
        if len(snippet) > 160:
            snippet = snippet[:157] + "..."
        print(f"   Snippet: {snippet}\n")


# -----------------------------------------------------------------------------
# Status & Utility Commands
# -----------------------------------------------------------------------------

def cmd_status(conn: sqlite3.Connection) -> None:
    """Print the health, model specifications, and status of the vector index."""
    model = get_meta_value(conn, "model_name", "none")
    dims = get_meta_value(conn, "dimensions", "none")
    schema = get_meta_value(conn, "schema_version", "unknown")
    last_sweep = get_meta_value(conn, "last_sweep", "never")

    cur = conn.execute("SELECT COUNT(*) FROM documents")
    doc_count = cur.fetchone()[0]

    cur = conn.execute("SELECT COUNT(*) FROM chunks")
    chunk_count = cur.fetchone()[0]

    db_size_kb = (DB_PATH.stat().st_size / 1024) if DB_PATH.exists() else 0.0

    print("🧠 Brain Vector Index Status")
    print("=" * 40)
    print(f"Database location : {DB_PATH.relative_to(REPO_ROOT)}")
    print(f"Database size     : {db_size_kb:.1f} KB")
    print(f"Schema version    : {schema}")
    print(f"Embedding model   : {model}")
    print(f"Vector dimensions : {dims}")
    print(f"Indexed documents : {doc_count}")
    print(f"Total chunks      : {chunk_count}")
    print(f"Last sweep        : {last_sweep}")

    on_disk = find_markdown_files(REPO_ROOT)
    cur = conn.execute("SELECT rel_path, file_hash FROM documents")
    db_map = {row[0]: row[1] for row in cur.fetchall()}

    unindexed = []
    modified = []
    for abs_p, rel_p in on_disk:
        if rel_p not in db_map:
            unindexed.append(rel_p)
        else:
            try:
                chash = hashlib.sha256(abs_p.read_bytes()).hexdigest()
                if chash != db_map[rel_p]:
                    modified.append(rel_p)
            except Exception:
                pass

    if unindexed or modified:
        print("\n⚠️ Filesystem Drift Detected:")
        if unindexed:
            print(f"  Unindexed files ({len(unindexed)}):")
            for p in unindexed[:5]:
                print(f"    + {p}")
            if len(unindexed) > 5:
                print(f"    ... and {len(unindexed) - 5} more")
        if modified:
            print(f"  Modified files ({len(modified)}):")
            for p in modified[:5]:
                print(f"    * {p}")
            if len(modified) > 5:
                print(f"    ... and {len(modified) - 5} more")
        print("\nRun: python3 agent/tools/brain-index.py sweep to synchronize.")
    else:
        print("\n[✓] Index is fully synchronized with disk.")


def cmd_embed(
    conn: sqlite3.Connection,
    client: genai.Client,
    file_paths: list[str],
) -> None:
    """Embed or re-embed specific file paths."""
    model = get_meta_value(conn, "model_name", DEFAULT_MODEL) or DEFAULT_MODEL
    dims = int(get_meta_value(conn, "dimensions", str(DEFAULT_DIMS)) or DEFAULT_DIMS)

    for target in file_paths:
        p = Path(target)
        if not p.is_absolute():
            p = (REPO_ROOT / p).resolve()

        if not p.is_file():
            print(f"[!] File not found: {target}", file=sys.stderr)
            continue

        rel_p = str(p.relative_to(REPO_ROOT))
        print(f"[*] Embedding document: {rel_p} ...", end=" ", flush=True)
        count = index_single_document(conn, client, p, rel_p, model=model, dimensions=dims)
        print(f"done ({count} chunks).")


def cmd_purge(conn: sqlite3.Connection, silent: bool = False) -> None:
    """Clear all stored documents, chunks, and FTS tables."""
    with conn:
        conn.execute("DELETE FROM fts_chunks")
        conn.execute("DELETE FROM chunks")
        conn.execute("DELETE FROM documents")
    prev_iso = conn.isolation_level
    try:
        conn.isolation_level = None
        conn.execute("VACUUM")
    finally:
        conn.isolation_level = prev_iso
    if not silent:
        print("[✓] Vector index and FTS data purged successfully.")


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Semantic & hybrid search CLI for the brain repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sweep and index all markdown files across the brain
  brain sweep

  # Search the brain semantically
  brain search "agent architecture design principles"

  # Hybrid search with JSON output for agent pipelines
  brain search "database schema migration patterns" --json

  # Embed a specific note right after creating or editing it
  brain embed notes/concepts/distributed-state.md

  # Check vector store synchronization and status
  brain index status
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sweep
    sweep_p = subparsers.add_parser("sweep", help="Scan and incrementally index the brain")
    sweep_p.add_argument("--force", action="store_true", help="Re-embed all files from scratch")
    sweep_p.add_argument("--include-archive", action="store_true", help="Include archive/ directory")

    # Embed single or multiple files
    embed_p = subparsers.add_parser("embed", help="Embed or re-embed specific markdown files")
    embed_p.add_argument("paths", nargs="+", help="File paths to embed (relative or absolute)")

    # Search
    search_p = subparsers.add_parser("search", help="Query the brain using vector or hybrid search")
    search_p.add_argument("query", help="Search query string")
    search_p.add_argument("-n", "--limit", type=int, default=DEFAULT_SEARCH_LIMIT, help="Max results (default: 5)")
    search_p.add_argument("--mode", choices=["hybrid", "vector", "text"], default="hybrid", help="Search mode")
    search_p.add_argument("--json", action="store_true", help="Output results as structured JSON")
    search_p.add_argument("--min-score", type=float, default=0.0, help="Minimum score threshold")

    # Status
    subparsers.add_parser("status", help="Show index health, size, and drift status")

    # Reindex
    reindex_p = subparsers.add_parser("reindex", help="Re-embed all documents from scratch")
    reindex_p.add_argument("--include-archive", action="store_true", help="Include archive/ directory")

    # Purge
    subparsers.add_parser("purge", help="Clear all embeddings and reset the index")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    conn = get_db()

    if args.command == "status":
        cmd_status(conn)
        return

    if args.command == "purge":
        cmd_purge(conn)
        return

    # Commands requiring Gemini API Client
    client = get_gemini_client()

    if args.command == "sweep":
        cmd_sweep(conn, client, force=args.force, include_archive=args.include_archive)
    elif args.command == "reindex":
        cmd_sweep(conn, client, force=True, include_archive=args.include_archive)
    elif args.command == "embed":
        cmd_embed(conn, client, args.paths)
    elif args.command == "search":
        cmd_search(
            conn,
            client,
            query=args.query,
            limit=args.limit,
            mode=args.mode,
            as_json=args.json,
            min_score=args.min_score,
        )


if __name__ == "__main__":
    main()
