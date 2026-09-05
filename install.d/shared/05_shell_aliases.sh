#!/bin/bash
# Add shell aliases to bashrc for non-zsh sessions
set -euo pipefail

ALIASES=(
  'alias a="agy --dangerously-skip-permissions"'
  'alias c="claude --dangerously-skip-permissions"'
  'alias x="codex --yolo"'
)

if [[ -f "${HOME}/.bashrc" ]]; then
  for line in "${ALIASES[@]}"; do
    if ! grep -qF "$line" "${HOME}/.bashrc"; then
      echo "$line" >>"${HOME}/.bashrc"
    fi
  done
fi

echo "Shell aliases ready."
