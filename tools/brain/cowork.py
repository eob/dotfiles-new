#!/usr/bin/env python3
"""Manage daily cowork logs, task roll-forward, and future date-seeded reminders."""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from brain_repo import get_brain_root

BRAIN_ROOT = get_brain_root()
COWORK_DIR = BRAIN_ROOT / "cowork"
CURRENT_CONTEXT_FILE = BRAIN_ROOT / "profile/current-context.md"

WEEKDAYS = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}


def parse_target_date(date_str: str | None, base_date: datetime.date | None = None) -> datetime.date:
    """Parse a flexible date string (ISO date, today, tomorrow, next tuesday, etc.)."""
    today = base_date or datetime.date.today()
    if not date_str or date_str.lower() in ("today", "now"):
        return today

    query = date_str.strip().lower()

    if query in ("tomorrow", "tmrw"):
        return today + datetime.timedelta(days=1)
    if query == "yesterday":
        return today - datetime.timedelta(days=1)

    # Offset syntax: +3, +3d, +3days, in 3 days
    match_plus = re.match(r"^(?:\+|\bin\s+)?(\d+)\s*(?:d|days?)?$", query)
    if match_plus:
        days = int(match_plus.group(1))
        return today + datetime.timedelta(days=days)

    # ISO syntax: YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", query):
        return datetime.date.fromisoformat(query)

    # Weekday syntax: "tuesday", "next tuesday", "this friday"
    tokens = query.split()
    target_weekday = None

    if tokens[0] in ("next", "this", "on") and len(tokens) > 1 and tokens[1] in WEEKDAYS:
        target_weekday = WEEKDAYS[tokens[1]]
    elif tokens[0] in WEEKDAYS:
        target_weekday = WEEKDAYS[tokens[0]]

    if target_weekday is not None:
        current_weekday = today.weekday()
        days_ahead = (target_weekday - current_weekday) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + datetime.timedelta(days=days_ahead)

    # Fallback attempt standard strptime formats
    for fmt in ("%Y/%m/%d", "%b %d %Y", "%B %d %Y", "%b %d", "%B %d"):
        try:
            parsed = datetime.datetime.strptime(query, fmt).date()
            if fmt in ("%b %d", "%B %d"):
                parsed = parsed.replace(year=today.year)
                if parsed < today:
                    parsed = parsed.replace(year=today.year + 1)
            return parsed
        except ValueError:
            continue

    raise ValueError(f"Could not parse date: '{date_str}'")


def find_cowork_files() -> list[tuple[datetime.date, Path]]:
    """Return all existing daily cowork log files sorted chronologically."""
    logs: list[tuple[datetime.date, Path]] = []
    if not COWORK_DIR.exists():
        return logs

    for path in COWORK_DIR.glob("**/*.md"):
        if path.name.lower() in ("readme.md", "template.md"):
            continue
        match = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
        if match:
            try:
                date_val = datetime.date.fromisoformat(match.group(1))
                logs.append((date_val, path))
            except ValueError:
                continue
    logs.sort(key=lambda item: item[0])
    return logs


def get_log_path_for_date(target_date: datetime.date) -> Path:
    """Return canonical path: cowork/YYYY/YYYY-MM-DD.md."""
    year_dir = COWORK_DIR / str(target_date.year)
    return year_dir / f"{target_date.isoformat()}.md"


def find_previous_log(target_date: datetime.date) -> tuple[datetime.date, Path] | None:
    """Find the most recent cowork log strictly before target_date."""
    logs = [item for item in find_cowork_files() if item[0] < target_date]
    return logs[-1] if logs else None


def extract_incomplete_tasks(log_path: Path) -> list[str]:
    """Extract incomplete checklist items (- [ ] ...) from a previous log file."""
    if not log_path.exists():
        return []

    lines = log_path.read_text(encoding="utf-8").splitlines()
    tasks: list[str] = []
    in_review_section = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and "review" in stripped.lower():
            in_review_section = True
            continue
        if stripped.startswith("## ") and in_review_section:
            in_review_section = False

        if in_review_section:
            continue

        if stripped.startswith("- [ ]") and len(stripped) > 5:
            task_text = stripped[5:].strip()
            # Exclude placeholder notes or generic headers
            if task_text and not task_text.startswith("<!--"):
                tasks.append(task_text)

    return tasks


def extract_reminders_from_file(log_path: Path) -> list[str]:
    """Extract existing reminder items from an already-seeded log file."""
    if not log_path.exists():
        return []

    content = log_path.read_text(encoding="utf-8")
    match = re.search(
        r"##\s*📌?\s*Reminders.*?\n(.*?)(?=\n##|\Z)",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return []

    reminders: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]") and len(stripped) > 5:
            reminders.append(stripped[5:].strip())
        elif stripped.startswith("- ") and not stripped.startswith("<!--"):
            reminders.append(stripped[2:].strip())

    return reminders


def build_daily_log_content(
    target_date: datetime.date,
    reminders: list[str],
    rolled_forward: list[str],
    existing_notes: str | None = None,
) -> str:
    """Construct full daily cowork log Markdown document."""
    weekday_name = target_date.strftime("%A")
    iso_date = target_date.isoformat()

    reminders_block = ""
    if reminders:
        reminders_block = "\n".join(f"- [ ] {r}" for r in reminders)
    else:
        reminders_block = "<!-- Pre-seeded reminders for this day will appear here -->\n_No reminders queued for today._"

    rolled_block = ""
    if rolled_forward:
        rolled_block = "\n".join(f"- [ ] {t}" for t in rolled_forward)
    else:
        rolled_block = "_No uncompleted tasks rolled forward._"

    # Discover skills dynamically from active brain repository
    skills_lines = []
    skills_dir = BRAIN_ROOT / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        for skill_path in sorted(skills_dir.iterdir()):
            if skill_path.is_dir() and not skill_path.name.startswith("."):
                name = skill_path.name.replace("-", " ").capitalize()
                log_file = skill_path / "log.md"
                if log_file.exists():
                    skills_lines.append(f"- [ ] **{name}**: Practice session ([skills/{skill_path.name}](../../skills/{skill_path.name}/log.md))")
                else:
                    skills_lines.append(f"- [ ] **{name}**: Daily practice")

    if not skills_lines:
        skills_lines = ["- [ ] Daily deliberate practice / skill session"]
    skills_block = "\n".join(skills_lines)

    content = f"""---
created: {iso_date}
status: growing
tags: [daily-cowork, log]
---

# Daily Cowork Log: {iso_date} ({weekday_name})

## 📌 Reminders & Queued for Today
{reminders_block}

## 🎯 Priorities & Focus Areas
### Primary Objectives
- [ ] 

### Secondary / Exploratory
- [ ] 

### Habits & Skills Practice
{skills_block}

## 💬 Cowork Check-ins & Session Notes
<!-- Real-time notes, decisions, artifacts, and links created during coworking -->

## 🔄 Rolled Forward from Previous Days
{rolled_block}

## 📝 End-of-Day Review & Reflections
- **Shipped**:
- **Carried forward**:
- **Notes for tomorrow**:
"""
    return content


def init_daily_log(target_date: datetime.date) -> tuple[Path, bool]:
    """Initialize or discover the daily log for target_date. Return (path, is_new)."""
    target_path = get_log_path_for_date(target_date)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    prev_info = find_previous_log(target_date)
    rolled_forward: list[str] = []
    if prev_info:
        prev_date, prev_path = prev_info
        raw_incomplete = extract_incomplete_tasks(prev_path)
        rolled_forward = [f"{task} (from {prev_date.isoformat()})" for task in raw_incomplete]

    if target_path.exists():
        # Discovered existing file! May contain pre-seeded reminders.
        existing_content = target_path.read_text(encoding="utf-8")
        existing_reminders = extract_reminders_from_file(target_path)

        # Check if the file is already a fully formed daily log
        if "## 🎯 Priorities & Focus Areas" in existing_content:
            return target_path, False

        # It was just a reminder seed; upgrade to full daily log preserving reminders
        full_content = build_daily_log_content(
            target_date=target_date,
            reminders=existing_reminders,
            rolled_forward=rolled_forward,
        )
        target_path.write_text(full_content, encoding="utf-8")
        return target_path, False

    # Fresh creation
    full_content = build_daily_log_content(
        target_date=target_date,
        reminders=[],
        rolled_forward=rolled_forward,
    )
    target_path.write_text(full_content, encoding="utf-8")
    return target_path, True


def add_reminder(target_date: datetime.date, reminder_text: str) -> Path:
    """Pre-seed or append a reminder into the daily log for target_date."""
    target_path = get_log_path_for_date(target_date)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    today_iso = datetime.date.today().isoformat()
    entry = f"- [ ] {reminder_text} (queued {today_iso})"

    if not target_path.exists():
        weekday_name = target_date.strftime("%A")
        iso_date = target_date.isoformat()
        seed_content = f"""---
created: {iso_date}
status: seed
tags: [daily-cowork, reminder-seed]
---

# Daily Cowork Log: {iso_date} ({weekday_name})

## 📌 Reminders & Queued for Today
{entry}
"""
        target_path.write_text(seed_content, encoding="utf-8")
        return target_path

    # File exists: update the reminders section or append it
    content = target_path.read_text(encoding="utf-8")
    if "## 📌 Reminders & Queued for Today" in content or "## Reminders" in content:
        # Replace the placeholder if present
        placeholder = "<!-- Pre-seeded reminders for this day will appear here -->\n_No reminders queued for today._"
        if placeholder in content:
            content = content.replace(placeholder, entry)
        else:
            # Find the section header and insert after it
            pattern = r"(##\s*📌?\s*Reminders[^\n]*\n)"
            content = re.sub(pattern, r"\1" + entry + "\n", content, count=1)
    else:
        # Append reminders section
        content += f"\n## 📌 Reminders & Queued for Today\n{entry}\n"

    target_path.write_text(content, encoding="utf-8")
    return target_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage daily cowork logs, task roll-forward, and future reminders."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # today / init
    p_today = subparsers.add_parser("today", help="Initialize or open today's cowork log.")
    p_today.add_argument(
        "--date", "-d", type=str, default=None, help="Specific date to initialize (default: today)"
    )

    # remind
    p_remind = subparsers.add_parser(
        "remind", help="Pre-seed a future daily log with a reminder."
    )
    p_remind.add_argument("date", type=str, help="Target date or expression (e.g. 'next tuesday', 'tomorrow', '2026-09-08')")
    p_remind.add_argument("text", type=str, help="Reminder description")

    # status
    p_status = subparsers.add_parser("status", help="Check status of a daily log.")
    p_status.add_argument("--date", "-d", type=str, default=None, help="Date to inspect (default: today)")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.command in ("today", "init"):
        target_date = parse_target_date(args.date)
        path, is_new = init_daily_log(target_date)
        status_label = "Created new" if is_new else "Discovered/updated"
        print(f"Log path: {path}")
        print(f"Status: {status_label} cowork log for {target_date.isoformat()} ({target_date.strftime('%A')})")

        # Report reminders and rolled tasks
        reminders = extract_reminders_from_file(path)
        if reminders:
            print(f"Reminders discovered ({len(reminders)}):")
            for r in reminders:
                print(f"  - {r}")

        prev_info = find_previous_log(target_date)
        if prev_info:
            rolled = extract_incomplete_tasks(prev_info[1])
            if rolled:
                print(f"Tasks rolled forward from {prev_info[0].isoformat()} ({len(rolled)}):")
                for t in rolled:
                    print(f"  - {t}")
        return 0

    if args.command == "remind":
        try:
            target_date = parse_target_date(args.date)
        except ValueError as err:
            print(f"Error: {err}", file=sys.stderr)
            return 1
        path = add_reminder(target_date, args.text)
        print(f"Scheduled reminder for {target_date.isoformat()} ({target_date.strftime('%A')}):")
        print(f"  File: {path}")
        print(f"  Item: {args.text}")
        return 0

    if args.command == "status":
        target_date = parse_target_date(args.date)
        path = get_log_path_for_date(target_date)
        if not path.exists():
            print(f"No cowork log exists yet for {target_date.isoformat()}. Run 'cowork.py today' to initialize.")
            return 0
        content = path.read_text(encoding="utf-8")
        done = len(re.findall(r"- \[[xX]\]", content))
        pending = len(re.findall(r"- \[ \]", content))
        print(f"Daily log for {target_date.isoformat()} ({path.name}):")
        print(f"  Completed items: {done}")
        print(f"  Pending items:   {pending}")
        reminders = extract_reminders_from_file(path)
        if reminders:
            print(f"  Reminders active: {len(reminders)}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
