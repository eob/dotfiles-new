#!/bin/bash
# Symlink tmux config
# --devbox mode: tmux-devbox.conf (C-b prefix, inner session, true color)
# default mode:  tmux.conf (C-a prefix, local session)
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"

if [[ "${DOTFILES_MODE:-default}" == "devbox" ]]; then
  ln -sf "${DOTFILES_DIR}/tmux/tmux-devbox.conf" "${HOME}/.tmux.conf"
else
  ln -sf "${DOTFILES_DIR}/tmux/tmux.conf" "${HOME}/.tmux.conf"
fi

# Reload if tmux is running
if command -v tmux &>/dev/null && tmux info &>/dev/null 2>&1; then
  tmux source-file "${HOME}/.tmux.conf" 2>/dev/null || true
fi

echo "Linked tmux config."
