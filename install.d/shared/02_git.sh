#!/bin/bash
# Symlink git config files
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"

ln -sf "${DOTFILES_DIR}/git/gitignore" "${HOME}/.gitignore"
echo "Linked gitignore."

# Only link gitconfig on macOS — on Linux devboxes the repo typically
# provides its own git identity via .gitconfig or environment variables.
if [[ "$(uname)" == "Darwin" ]]; then
  ln -sf "${DOTFILES_DIR}/git/gitconfig" "${HOME}/.gitconfig"
  echo "Linked gitconfig."
fi
