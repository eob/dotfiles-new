#!/usr/bin/env python3
"""Compile, export, and deliver durable research reports to e-readers (Kindle / EPUB / PDF).

Usage:
  brain report compile <file> [--format epub|pdf] [--title "Title"] [--author "Author"] [--out <path>]
  brain report send <file> [--to email] [--format epub|pdf] [--title "Title"]
  brain report list
  brain report clean
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import smtplib
import subprocess
import sys
import tempfile
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from brain_repo import get_brain_root
except ImportError:
    def get_brain_root() -> Path:
        return Path.cwd()

DEFAULT_KINDLE_EMAIL = os.environ.get("KINDLE_EMAIL")
DEFAULT_AUTHOR = os.environ.get("BRAIN_AUTHOR", "Edward Benson")

KINDLE_EINK_CSS = """
/* Kindle E-Ink Reading Stylesheet */
@page {
    margin: 5% 5%;
}

body {
    font-family: "Bookerly", "Georgia", "Charis SIL", serif;
    font-size: 1.0em;
    line-height: 1.45;
    margin: 0;
    padding: 0;
    color: #111111;
    text-align: justify;
}

h1, h2, h3, h4, h5, h6 {
    font-family: "Amazon Ember", "Helvetica Neue", "Arial", sans-serif;
    font-weight: bold;
    color: #000000;
    text-align: left;
}

h1 {
    font-size: 1.65em;
    margin-top: 1.4em;
    margin-bottom: 0.6em;
    page-break-before: always;
    break-before: page;
}

h2 {
    font-size: 1.3em;
    margin-top: 1.2em;
    margin-bottom: 0.5em;
    page-break-before: always;
    break-before: page;
}

h3 {
    font-size: 1.1em;
    margin-top: 1.0em;
    margin-bottom: 0.4em;
}

p {
    margin-top: 0.4em;
    margin-bottom: 0.6em;
}

blockquote {
    margin: 0.9em 0;
    padding: 0.5em 0.9em;
    border-left: 3px solid #555555;
    background-color: #f7f7f7;
    font-style: normal;
}

blockquote p {
    margin: 0.2em 0;
}

pre, code {
    font-family: "Amazon Ember Mono", "Courier Prime", "Courier New", monospace;
}

code {
    font-size: 0.88em;
    background-color: #efefef;
    padding: 1px 4px;
    border-radius: 2px;
}

pre {
    font-size: 0.80em;
    background-color: #f4f4f4;
    border: 1px solid #d0d0d0;
    padding: 0.6em;
    white-space: pre-wrap;
    word-wrap: break-word;
    line-height: 1.25;
    margin: 0.9em 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1.0em 0;
    font-size: 0.84em;
}

th, td {
    border: 1px solid #777777;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
}

th {
    background-color: #e5e5e5;
    font-weight: bold;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1.0em auto;
}

hr {
    border: 0;
    border-top: 1px solid #999999;
    margin: 1.4em 0;
}
"""


def resolve_export_dir() -> Path:
    """Resolve the canonical report_exports directory inside the active brain repository."""
    try:
        root = get_brain_root()
    except Exception:
        root = Path.cwd()
    export_dir = root / "report_exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def format_month_year(date_val: datetime.date | str | None) -> str:
    """Format a date into a concise 'Mon YYYY' string (e.g. 'Sep 2026')."""
    if not date_val:
        return datetime.date.today().strftime("%b %Y")
    if isinstance(date_val, datetime.date):
        return date_val.strftime("%b %Y")
    
    # Try parsing string ISO date (YYYY-MM-DD)
    m = re.match(r"^(\d{4})-(\d{2})(?:-\d{2})?", str(date_val).strip())
    if m:
        try:
            year, month = int(m.group(1)), int(m.group(2))
            dt = datetime.date(year, month, 1)
            return dt.strftime("%b %Y")
        except ValueError:
            pass
    return datetime.date.today().strftime("%b %Y")


def sanitize_filename(name: str) -> str:
    """Remove unsafe filesystem characters from title."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def parse_and_clean_markdown(file_path: Path) -> tuple[str, str, str, str]:
    """Parse Markdown, strip YAML frontmatter, clean alerts, and formulate concise title.
    
    Returns:
      (concise_title, full_title, author, cleaned_markdown)
    """
    raw_text = file_path.read_text(encoding="utf-8")
    
    frontmatter: dict[str, str] = {}
    body = raw_text
    
    # Match YAML frontmatter
    fm_match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", raw_text, re.DOTALL)
    if fm_match:
        fm_text, body = fm_match.group(1), fm_match.group(2)
        for line in fm_text.splitlines():
            kv = line.split(":", 1)
            if len(kv) == 2:
                key = kv[0].strip().lower()
                val = kv[1].strip().strip('"\'')
                frontmatter[key] = val

    # Clean GitHub Markdown alerts (> [!NOTE] -> > **NOTE:**)
    body = re.sub(
        r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]",
        r"> **\1:**",
        body,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Determine full title
    full_title = frontmatter.get("title")
    if not full_title:
        h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if h1_match:
            full_title = h1_match.group(1).strip()
        else:
            full_title = file_path.stem.replace("-", " ").title()

    # Determine author
    author = frontmatter.get("author", DEFAULT_AUTHOR)

    # Determine date
    date_str = format_month_year(frontmatter.get("created"))

    # Formulate concise title
    # e.g., "Design Benchmarks, UI Reproduction, and Font Identification in the Wild: State of the Art"
    # -> "FontBench and UI Reproduction (Sep 2026)" or main title prefix + (Sep 2026)
    short_title = full_title
    if ":" in short_title:
        short_title = short_title.split(":", 1)[0].strip()
    
    # If the document prominently discusses a core coined topic (like FontBench)
    if "fontbench" in file_path.name.lower() or "fontbench" in full_title.lower():
        if "fontbench" not in short_title.lower():
            short_title = f"{short_title} (FontBench)"
        elif len(short_title) > 35:
            short_title = "FontBench & UI Reproduction"

    if len(short_title) > 42:
        # Truncate cleanly at word boundary
        words = short_title.split()
        short_title = " ".join(words[:5])

    concise_title = f"{short_title} ({date_str})"
    concise_title = sanitize_filename(concise_title)

    return concise_title, full_title, author, body


def compile_report(
    input_path: Path,
    output_format: str = "epub",
    custom_title: str | None = None,
    custom_author: str | None = None,
    output_path: Path | None = None,
) -> Path:
    """Compile a Markdown report to EPUB or PDF using Calibre's ebook-convert."""
    ebook_convert = shutil.which("ebook-convert")
    if not ebook_convert:
        print("Error: 'ebook-convert' not found in PATH.", file=sys.stderr)
        print("Please install calibre (e.g. 'sudo apt-get install calibre').", file=sys.stderr)
        sys.exit(1)

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    export_dir = resolve_export_dir()
    concise_title, full_title, author, cleaned_body = parse_and_clean_markdown(input_path)

    final_title = custom_title if custom_title else concise_title
    final_author = custom_author if custom_author else author
    output_ext = output_format.lower().lstrip(".")

    if output_path:
        target_file = output_path.resolve()
        target_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        target_file = export_dir / f"{sanitize_filename(final_title)}.{output_ext}"

    with tempfile.TemporaryDirectory(prefix="brain-report-") as tmpdir:
        tmp_dir = Path(tmpdir)
        clean_md_path = tmp_dir / "report.md"
        css_path = tmp_dir / "kindle.css"

        clean_md_path.write_text(cleaned_body, encoding="utf-8")
        css_path.write_text(KINDLE_EINK_CSS, encoding="utf-8")

        cmd = [
            ebook_convert,
            str(clean_md_path),
            str(target_file),
            "--title", final_title,
            "--authors", final_author,
            "--language", "en",
            "--extra-css", str(css_path),
        ]

        if output_ext == "epub":
            cmd.extend([
                "--level1-toc", "//h:h1",
                "--level2-toc", "//h:h2",
                "--level3-toc", "//h:h3",
                "--use-auto-toc",
                "--epub-version", "3",
            ])
        elif output_ext == "pdf":
            cmd.extend([
                "--paper-size", "letter",
                "--pdf-page-numbers",
                "--pdf-default-font-size", "12",
                "--pdf-mono-font-size", "10",
            ])

        print(f"⚙️  Compiling '{input_path.name}' → {output_ext.upper()}...")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"Error compiling report:\n{proc.stderr}", file=sys.stderr)
            sys.exit(proc.returncode)

    file_size_kb = target_file.stat().st_size // 1024
    print(f"✓ Generated: {target_file}")
    print(f"  Title: '{final_title}' | Size: {file_size_kb} KB")
    return target_file


def send_report(
    input_path: Path,
    recipient: str | None = None,
    output_format: str = "epub",
    custom_title: str | None = None,
) -> None:
    """Compile (if needed) and send the report to Kindle via authenticated SMTP or Web upload."""
    to_email = recipient or os.environ.get("KINDLE_EMAIL")

    # 1. Compile or verify file
    if input_path.suffix.lower() in (".epub", ".pdf"):
        doc_file = input_path.resolve()
        title = custom_title or doc_file.stem
    else:
        doc_file = compile_report(
            input_path=input_path,
            output_format=output_format,
            custom_title=custom_title,
        )
        title = doc_file.stem

    file_size_kb = doc_file.stat().st_size // 1024

    # 2. Check SMTP environment variables
    smtp_host = os.environ.get("BRAIN_SMTP_HOST")
    smtp_user = os.environ.get("BRAIN_SMTP_USER")
    smtp_pass = os.environ.get("BRAIN_SMTP_PASS")
    smtp_port = int(os.environ.get("BRAIN_SMTP_PORT", "587"))
    smtp_from = os.environ.get("BRAIN_SMTP_FROM", smtp_user)
    smtp_ssl = os.environ.get("BRAIN_SMTP_SSL", "").lower() in ("true", "1", "yes")

    if smtp_host and smtp_user and smtp_pass and smtp_from:
        if not to_email:
            print("! Error: Destination Kindle email address not specified.", file=sys.stderr)
            print("  Specify --to <email> or set 'export KINDLE_EMAIL=...' in ~/.zshrc.local.", file=sys.stderr)
            return

        print(f"✉️  Sending '{doc_file.name}' via SMTP ({smtp_host}) to {to_email}...")
        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_from
            msg["To"] = to_email
            msg["Subject"] = f"Report: {title}"

            body_text = f"Attached report: {title}\nDelivered via brain report send."
            msg.attach(MIMEText(body_text, "plain"))

            # Determine MIME type
            ext = doc_file.suffix.lower()
            mime_type = "application/epub+zip" if ext == ".epub" else "application/pdf"
            
            with open(doc_file, "rb") as f:
                part = MIMEApplication(f.read(), Name=doc_file.name)
            part["Content-Disposition"] = f'attachment; filename="{doc_file.name}"'
            msg.attach(part)

            if smtp_ssl:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
                server.starttls()

            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            print(f"✓ Successfully delivered '{doc_file.name}' to {to_email}!")
            return
        except Exception as e:
            print(f"! SMTP delivery failed: {e}", file=sys.stderr)
            print("Falling back to manual upload instructions.", file=sys.stderr)

    # 3. Fallback: Provide direct Send to Kindle upload guidance
    target_display = to_email if to_email else "[Not set - specify --to <email> or export KINDLE_EMAIL]"
    print("\n" + "=" * 65)
    print(" Kindle Delivery Ready")
    print("=" * 65)
    print(f"Local file: {doc_file} ({file_size_kb} KB)")
    print(f"Target address: {target_display}")
    print("\n[Option A: 1-Click Drag & Drop via Browser (Recommended)]")
    print("  Drag and drop the file directly into your browser at:")
    print("  👉 https://www.amazon.com/sendtokindle")
    print("\n[Option B: Automated 1-Click Email Delivery via Terminal]")
    print("  To enable instant automated emailing, add to ~/.zshrc.local:")
    print('    export KINDLE_EMAIL="your-kindle-name@kindle.com"')
    print('    export BRAIN_SMTP_HOST="smtp.gmail.com"')
    print('    export BRAIN_SMTP_PORT=587')
    print('    export BRAIN_SMTP_USER="your-email@gmail.com"')
    print('    export BRAIN_SMTP_PASS="your-16-char-app-password"')
    print("    export BRAIN_SMTP_FROM=\"your-email@gmail.com\"")
    print("\n  Important: Ensure 'your-email@gmail.com' is on your Amazon Whitelist:")
    print("  Amazon.com → Manage Your Content and Devices → Preferences → Personal Document Settings")
    print("=" * 65)


def list_reports() -> None:
    """List compiled reports currently in report_exports/."""
    export_dir = resolve_export_dir()
    files = sorted(
        [f for f in export_dir.iterdir() if f.is_file() and f.suffix.lower() in (".epub", ".pdf")],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )

    if not files:
        print(f"No compiled reports found in {export_dir}.")
        print("Compile one using: brain report compile <path-to-markdown>")
        return

    print(f"=== Compiled Reports in {export_dir.name}/ ===")
    print(f"{'Format':<8} {'Size':<10} {'Updated':<16} {'Filename'}")
    print("-" * 65)
    for f in files:
        size_kb = f"{f.stat().st_size // 1024} KB"
        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        ext = f.suffix.upper().lstrip(".")
        print(f"{ext:<8} {size_kb:<10} {mtime:<16} {f.name}")


def clean_reports() -> None:
    """Remove generated report files in report_exports/."""
    export_dir = resolve_export_dir()
    files = [f for f in export_dir.iterdir() if f.is_file() and f.suffix.lower() in (".epub", ".pdf")]
    if not files:
        print("No files to clean.")
        return
    for f in files:
        f.unlink()
    print(f"Cleaned {len(files)} compiled report file(s) from {export_dir}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile and deliver durable brain reports to Kindle.")
    subparsers = parser.add_subparsers(dest="subcommand", help="Report subcommands")

    # compile
    p_compile = subparsers.add_parser("compile", help="Compile a Markdown note to EPUB or PDF")
    p_compile.add_argument("file", help="Path to markdown report file")
    p_compile.add_argument("--format", choices=["epub", "pdf"], default="epub", help="Target format (default: epub)")
    p_compile.add_argument("--title", help="Override report title (default: auto-detected concise title)")
    p_compile.add_argument("--author", help="Override author name")
    p_compile.add_argument("--out", help="Explicit output path")

    # send
    p_send = subparsers.add_parser("send", help="Send report to Kindle via email or web")
    p_send.add_argument("file", help="Path to markdown or compiled .epub/.pdf file")
    p_send.add_argument("--to", help="Destination Kindle email (defaults to $KINDLE_EMAIL)")
    p_send.add_argument("--format", choices=["epub", "pdf"], default="epub", help="Format to compile if given markdown")
    p_send.add_argument("--title", help="Override title")

    # list
    subparsers.add_parser("list", help="List compiled reports in report_exports/")

    # clean
    subparsers.add_parser("clean", help="Clean compiled reports in report_exports/")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "compile":
        compile_report(
            input_path=Path(args.file),
            output_format=args.format,
            custom_title=args.title,
            custom_author=args.author,
            output_path=Path(args.out) if args.out else None,
        )
    elif args.subcommand == "send":
        send_report(
            input_path=Path(args.file),
            recipient=args.to,
            output_format=args.format,
            custom_title=args.title,
        )
    elif args.subcommand == "list":
        list_reports()
    elif args.subcommand == "clean":
        clean_reports()


if __name__ == "__main__":
    main()
