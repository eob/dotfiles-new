#!/bin/bash
# Install brew packages
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"

if ! command -v brew &>/dev/null; then
  echo "Homebrew not found, skipping."
  exit 0
fi

bash "${DOTFILES_DIR}/scripts/brew-install.sh"
echo "Brew packages installed."
