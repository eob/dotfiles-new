#!/bin/bash
# Apply macOS system defaults
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"

bash "${DOTFILES_DIR}/scripts/macos-defaults.sh"
echo "macOS defaults applied."
