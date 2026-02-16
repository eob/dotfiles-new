#!/bin/bash
# Symlink nvim config
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"

mkdir -p "${HOME}/.config"

# Remove existing symlink or skip if real directory exists
if [[ -L "${HOME}/.config/nvim" ]]; then
  rm "${HOME}/.config/nvim"
fi

if [[ ! -d "${HOME}/.config/nvim" ]]; then
  ln -s "${DOTFILES_DIR}/nvim" "${HOME}/.config/nvim"
  echo "Linked nvim config."
fi
