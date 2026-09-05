#!/usr/bin/env python3
"""Shared repository resolution utility for the brain toolkit.

Discovers the active brain repository using:
1. $BRAIN_REPO environment variable
2. Directory walk-up from current working directory
3. Standard fallback locations (~/code/brain, ~/brain, /mnt/disks/data/brain)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def get_brain_root() -> Path:
    """Resolve and return the canonical root path of the active brain repository."""
    # 1. Explicit environment variable
    env_path = os.environ.get("BRAIN_REPO")
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if p.exists() and p.is_dir():
            return p
        print(f"Warning: $BRAIN_REPO is set to '{env_path}' but does not exist.", file=sys.stderr)

    # 2. Check current working directory or ancestors (e.g. running inside any subfolder)
    cwd = Path.cwd().resolve()
    for parent in [cwd] + list(cwd.parents):
        if (parent / "agent" / "context").exists() or (parent / "AGENTS.md").exists():
            return parent

    # 3. Standard fallback locations
    candidates = [
        Path.home() / "code" / "brain",
        Path.home() / "brain",
        Path("/mnt/disks/data/brain"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate.resolve()

    raise RuntimeError(
        "Could not locate a brain repository.\n"
        "Please run this command from within a brain repository, or set $BRAIN_REPO.\n"
        "Example: export BRAIN_REPO=\"$HOME/code/brain\""
    )
