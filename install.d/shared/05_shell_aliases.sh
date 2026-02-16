#!/bin/bash
# Add shell aliases to bashrc for non-zsh sessions
set -euo pipefail

ALIAS_LINE='alias c="claude --dangerously-skip-permissions"'
if [[ -f "${HOME}/.bashrc" ]] && ! grep -qF "$ALIAS_LINE" "${HOME}/.bashrc"; then
  echo "$ALIAS_LINE" >>"${HOME}/.bashrc"
fi

echo "Shell aliases ready."
