#!/bin/bash
# Symlink zshrc
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"

ln -sf "${DOTFILES_DIR}/zsh/zshrc" "${HOME}/.zshrc"
echo "Linked zshrc."
