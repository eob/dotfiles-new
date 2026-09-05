#!/usr/bin/env python3
"""Run read-only structural checks on the agent memory and its Markdown links."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


sys.path.insert(0, str(Path(__file__).resolve().parent))
from brain_repo import get_brain_root

BRAIN_ROOT = get_brain_root()
CORE_CONTEXT = BRAIN_ROOT / "agent/context/core.md"
CLAIM_LEDGER = BRAIN_ROOT / "agent/model/claims.md"
CORE_LINE_BUDGET = 100

MARKDOWN_SCOPES = (
    "AGENTS.md",
    "README.md",
    "agent/**/*.md",
    "profile/**/*.md",
    ".agents/skills/**/*.md",
    "discussions/**/*.md",
)

LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")
CLAIM_ID_PATTERN = re.compile(r"^`([A-Z]+-\d{3})`$")
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def markdown_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in MARKDOWN_SCOPES:
        files.update(path for path in BRAIN_ROOT.glob(pattern) if path.is_file())
    return sorted(files)


def check_links(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for source in files:
        for raw_link in LINK_PATTERN.findall(source.read_text(encoding="utf-8")):
            link = raw_link.strip().strip("<>")
            if not link or link.startswith(("#", "http://", "https://", "mailto:")):
                continue
            path_part = unquote(link.split("#", 1)[0])
            target = Path(path_part)
            if not target.is_absolute():
                target = source.parent / target
            if not target.exists():
                errors.append(f"broken link: {source.relative_to(BRAIN_ROOT)} -> {raw_link}")
    return errors


def check_claim_ledger() -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    allowed_confidence = {"High", "Medium", "Low", "Unresolved"}
    allowed_volatility = {"Low", "Medium", "High"}
    allowed_sensitivity = {"Ordinary", "Personal", "Sensitive"}

    for line_number, line in enumerate(
        CLAIM_LEDGER.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not re.match(r"^\| `[A-Z]+-\d{3}` ", line):
            continue

        cells = [cell.strip() for cell in line.strip().split("|")[1:-1]]
        if len(cells) != 8:
            errors.append(f"claim row {line_number}: expected 8 fields, found {len(cells)}")
            continue

        claim_id, _claim, _evidence, confidence, volatility, sensitivity, checked, _note = cells
        match = CLAIM_ID_PATTERN.match(claim_id)
        if not match:
            errors.append(f"claim row {line_number}: invalid ID {claim_id}")
            continue
        normalized_id = match.group(1)
        if normalized_id in seen:
            errors.append(f"claim row {line_number}: duplicate ID {normalized_id}")
        seen.add(normalized_id)

        if confidence not in allowed_confidence:
            errors.append(f"claim {normalized_id}: invalid confidence {confidence}")
        if volatility not in allowed_volatility:
            errors.append(f"claim {normalized_id}: invalid volatility {volatility}")
        if sensitivity not in allowed_sensitivity:
            errors.append(f"claim {normalized_id}: invalid sensitivity {sensitivity}")
        if not ISO_DATE_PATTERN.match(checked):
            errors.append(f"claim {normalized_id}: invalid checked date {checked}")

    if not seen:
        errors.append("claim ledger contains no claim rows")
    return errors


def check_core_budget() -> list[str]:
    line_count = len(CORE_CONTEXT.read_text(encoding="utf-8").splitlines())
    if line_count > CORE_LINE_BUDGET:
        return [
            f"core context has {line_count} lines; budget is {CORE_LINE_BUDGET}. "
            "Route detail through the load map."
        ]
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run read-only structural checks on the brain repository."
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Brain root to validate; defaults to the repository containing this script.",
    )
    return parser.parse_args()


def main() -> int:
    global BRAIN_ROOT, CORE_CONTEXT, CLAIM_LEDGER
    args = parse_args()
    if args.root:
        BRAIN_ROOT = args.root.expanduser().resolve()
        CORE_CONTEXT = BRAIN_ROOT / "agent/context/core.md"
        CLAIM_LEDGER = BRAIN_ROOT / "agent/model/claims.md"

    required = (CORE_CONTEXT, CLAIM_LEDGER)
    missing = [path for path in required if not path.is_file()]
    if missing:
        for path in missing:
            print(f"ERROR missing required file: {path}", file=sys.stderr)
        return 2

    files = markdown_files()
    checks = {
        "links": check_links(files),
        "claim-ledger": check_claim_ledger(),
        "core-budget": check_core_budget(),
    }
    failures = 0
    for name, errors in checks.items():
        if errors:
            failures += len(errors)
            print(f"FAIL {name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {name}")

    if failures:
        print(f"Validation failed with {failures} error(s).", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} Markdown files under {BRAIN_ROOT}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
