# Brain Toolkit & CLI

The `brain` toolkit is an open, portable command-line interface and local cognitive OS designed for human-agent knowledge work. It provides an asynchronous intake bridge, local hybrid vector search, daily cowork management, and repository synchronization.

---

## 1. Overview & Architecture

The toolkit enforces a strict separation between **the operating code** (public, universal) and **the knowledge data** (private, air-gapped):

* **Code (`~/.dotfiles`)**: Pure general-purpose infrastructure. Contains zero secrets, zero proprietary code, and zero personal notes.
* **Data (`$BRAIN_REPO`)**: Private Markdown repository holding lifelong context, concepts, projects, and discussions.
  * Personal machine: `$BRAIN_REPO = ~/code/brain` (or `/mnt/disks/data/brain`)
  * Enterprise / work machine: `$BRAIN_REPO = ~/code/work-brain`

```text
                                  [~/.dotfiles/bin/brain]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             [Personal Brain Repo]                       [Work Brain Repo]
             $BRAIN_REPO=~/brain                         $BRAIN_REPO=~/work-brain
             - Lifelong personal memory                  - Internal RFCs & design reviews
             - Public writing & side projects            - Monorepo worktrees & tickets
             - Lifelong learning & habits                - Institutional decision records
```

---

## 2. Command Reference

All commands run through the single `brain` binary (located in `bin/brain` and included in `$PATH`):

### Repository Bootstrapping
```sh
# Bootstrap a work brain repository:
brain bootstrap ~/code/work-brain --org Acme --role "Staff Engineer"

# Bootstrap a personal brain repository:
brain bootstrap ~/code/brain --type personal --role "Researcher & Builder"
```

### Knowledge & Search
```sh
brain search "<query>"       # Hybrid vector (Gemini 768d) + FTS5 full-text search
brain embed <path>...        # Embed or re-embed specific markdown notes immediately
brain sweep                  # Incrementally index any modified or newly added notes
brain reindex                # Rebuild the local SQLite vector database from scratch
```

### Linear Intake & Processing
Capture links and ideas on your phone or browser, triage them through Linear, and close tickets with resolution notes:
```sh
brain inbox list             # List open tickets in your Linear inbox
brain inbox next             # Pull the next unhandled ticket with auto-classified intent
brain inbox inspect BRN-18   # View full ticket description and complete comment thread
brain inbox close BRN-18 \
  --summary "..." \
  --trigger "..." \
  --report "notes/report.md" # Close ticket with structured filing & wake-up trigger
```

### Daily Cowork Rhythm
```sh
brain today                  # Initialize today's cowork log and roll forward pending tasks
brain remind "<date>" "<txt>"# Schedule a date-seeded reminder (e.g. "next tuesday")
```

### Repository Health & Synchronization
```sh
brain doctor                 # 4-point health check (links, index cache, Linear API, git)
brain validate               # Validate Markdown links, claims schema, and size budgets
brain sync "[commit-msg]"    # Atomic triple: sweeps index, validates links, commits & pushes
```

---

## 3. Environment & Configuration

Configure credentials in your local shell configuration (e.g. `~/.zshrc.local`):

| Variable | Required By | Description |
|---|---|---|
| `BRAIN_REPO` | Optional | Explicit path to active brain repository. If omitted, the CLI discovers the repo by walking up from the current directory or checking standard fallback paths. |
| `LINEAR_API_KEY` | `brain inbox` | Personal API token for Linear workspace (`lin_api_...`). |
| `GEMINI_API_KEY` | `brain search`, `embed`, `sweep` | Google Gemini API key used for `gemini-embedding-2` dense embeddings. |

---

## 4. Components

* **`brain`** (`bin/brain`): Unified CLI entrypoint and dispatcher.
* **`brain_index.py`**: SQLite vector database with FTS5 keyword indexing and cosine similarity.
* **`brain_inbox.py`**: Pure Python 3 GraphQL client for the Linear API (zero third-party pip dependencies).
* **`cowork.py`**: Daily markdown agenda generator and date-parser for reminders.
* **`validate_brain.py`**: Local markdown link validator and claim ledger checker.
