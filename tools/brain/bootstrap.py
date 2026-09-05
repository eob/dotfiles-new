#!/usr/bin/env python3
"""
Bootstrap a new cognitive brain repository from the canonical dotfiles skeleton.

Usage:
  brain bootstrap [TARGET_DIR] [options]

Examples:
  # Bootstrap work brain:
  brain bootstrap ~/code/work-brain --name "Your Name" --type work --org Acme --role "Engineering"

  # Bootstrap personal brain:
  brain bootstrap ~/code/brain --name "Your Name" --type personal --role "Researcher & Builder"
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
SKELETON_DIR = TOOLS_DIR / "skeleton"


def detect_git_user_name() -> str:
    """Attempt to detect user's name from git config."""
    try:
        proc = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=True)
        if name := proc.stdout.strip():
            return name
    except Exception:
        pass
    return "User"


def render_template(content: str, context: dict[str, str]) -> str:
    """Render template text with context dictionary and basic conditionals."""
    # Handle {% if KEY %}...{% endif %}
    def repl_if(match: re.Match) -> str:
        var_name = match.group(1).strip()
        inner_text = match.group(2)
        if context.get(var_name):
            # Evaluate inner placeholders
            for k, v in context.items():
                inner_text = inner_text.replace(f"{{{{{k}}}}}", v)
            return inner_text
        return ""

    content = re.sub(r"{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}", repl_if, content, flags=re.DOTALL)

    # Replace simple variables
    for k, v in context.items():
        content = content.replace(f"{{{{{k}}}}}", v)

    return content


def bootstrap_brain(
    target_path: Path,
    user_name: str,
    repo_type: str,
    org_name: str,
    role_name: str,
    no_git: bool = False,
    force: bool = False,
) -> None:
    target_path = target_path.expanduser().resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    # Check non-empty
    existing_items = [p for p in target_path.iterdir() if p.name != ".git"]
    if existing_items and not force:
        print(
            f"Error: Target directory '{target_path}' is not empty ({len(existing_items)} items found).\n"
            "Use --force to bootstrap anyway.",
            file=sys.stderr,
        )
        sys.exit(1)

    first_name = user_name.split()[0] if user_name else "User"
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repo_name = target_path.name

    context = {
        "USER_NAME": user_name,
        "FIRST_NAME": first_name,
        "REPO_NAME": repo_name,
        "REPO_TYPE": repo_type,
        "ORG_NAME": org_name,
        "ROLE_NAME": role_name,
        "DATE": today_str,
    }

    print(f"\n🚀 Bootstrapping new Brain repository: {target_path}")
    print(f"   • Owner       : {user_name} ({first_name})")
    print(f"   • Type        : {repo_type.upper()}")
    if org_name:
        print(f"   • Organization: {org_name}")
    print(f"   • Role/Focus  : {role_name}")
    print(f"   • Date        : {today_str}\n")

    # Copy and render template files
    file_count = 0
    for root, dirs, files in os.walk(SKELETON_DIR):
        rel_root = Path(root).relative_to(SKELETON_DIR)
        dest_dir = target_path / rel_root
        dest_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            src_file = Path(root) / f
            dest_file = dest_dir / f

            # Read and render content
            try:
                raw_text = src_file.read_text(encoding="utf-8")
                rendered = render_template(raw_text, context)
                dest_file.write_text(rendered, encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(src_file, dest_file)

            file_count += 1

    print(f"[✓] Created skeleton: {file_count} files rendered.")

    # Git initialization
    is_new_git = False
    if not no_git:
        git_dir = target_path / ".git"
        if not git_dir.exists():
            print("[*] Initializing Git repository (branch: main)...")
            subprocess.run(["git", "init", "-b", "main"], cwd=target_path, check=True)
            is_new_git = True

    # Validate structural integrity
    print("[*] Validating repository structure and link integrity...")
    val_proc = subprocess.run(
        [sys.executable, str(TOOLS_DIR / "validate_brain.py"), "--root", str(target_path)]
    )
    if val_proc.returncode != 0:
        print("Warning: Validation warnings encountered during bootstrap.", file=sys.stderr)

    # Initial vector index sweep
    print("[*] Building initial vector index cache...")
    env = dict(os.environ)
    env["BRAIN_REPO"] = str(target_path)
    subprocess.run([sys.executable, str(TOOLS_DIR / "brain_index.py"), "sweep"], env=env)

    # Initial Git commit
    if not no_git and is_new_git:
        print("[*] Creating initial Git commit...")
        subprocess.run(["git", "add", "."], cwd=target_path, check=True)
        commit_msg = f"feat(brain): bootstrap {repo_type} brain repository for {user_name}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=target_path, check=True)

    print(f"\n✨ Brain repository ready at: {target_path}")
    print("\nNext steps to activate:")
    print("----------------------------------------------------------------")
    print(f"1. Set in your shell profile (~/.zshrc or ~/.zshrc.local):")
    print(f"   export BRAIN_REPO=\"{target_path}\"")
    print("\n2. Verify the installation:")
    print("   brain doctor")
    print("\n3. Start your first session:")
    print("   brain today")
    print("----------------------------------------------------------------\n")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap a new cognitive brain repository from dotfiles skeleton.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory for the new brain (defaults to current directory).",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="User's full name (default: auto-detected from git config).",
    )
    parser.add_argument(
        "--type",
        choices=["personal", "work"],
        default=None,
        help="Type of brain: personal or work (default: work if --org is set, else personal).",
    )
    parser.add_argument(
        "--org",
        default="",
        help="Organization or company name (e.g. 'Acme').",
    )
    parser.add_argument(
        "--role",
        default="",
        help="Role or focus domain (e.g. 'Engineering' or 'Founder & Researcher').",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip Git repository initialization and initial commit.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow bootstrapping into a non-empty directory.",
    )

    args = parser.parse_args()

    user_name = args.name or detect_git_user_name()
    org_name = args.org.strip()
    repo_type = args.type or ("work" if org_name else "personal")
    role_name = args.role.strip()
    if not role_name:
        role_name = "Staff Engineer" if repo_type == "work" else "Researcher & Engineer"

    target_path = Path(args.target_dir)

    bootstrap_brain(
        target_path=target_path,
        user_name=user_name,
        repo_type=repo_type,
        org_name=org_name,
        role_name=role_name,
        no_git=args.no_git,
        force=args.force,
    )


if __name__ == "__main__":
    main()
