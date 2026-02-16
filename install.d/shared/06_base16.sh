#!/bin/bash
# Clone base16-shell if not present
set -euo pipefail

BASE16_DIR="${HOME}/.config/base16-shell"

if [[ ! -d "${BASE16_DIR}" ]]; then
  git clone --quiet https://github.com/chriskempson/base16-shell.git "${BASE16_DIR}"
  echo "Cloned base16-shell."
else
  echo "base16-shell already present."
fi
