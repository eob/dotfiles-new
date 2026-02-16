#!/bin/bash
# Dotfiles installer — runs shared scripts, then platform-specific ones.
# Usage: install.sh [--devbox]
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS="$(uname)"
export DOTFILES_MODE="default"

for arg in "$@"; do
  case "$arg" in
    --devbox) DOTFILES_MODE="devbox" ;;
  esac
done

run_scripts() {
  local dir="$1"
  for script in "${dir}"/*.sh; do
    [[ -f "$script" ]] || continue
    echo "── $(basename "$script") ──"
    bash "$script"
  done
}

echo "=== Shared ==="
run_scripts "${DOTFILES_DIR}/install.d/shared"

case "$OS" in
  Darwin)
    echo ""
    echo "=== macOS ==="
    run_scripts "${DOTFILES_DIR}/install.d/darwin"
    ;;
  Linux)
    echo ""
    echo "=== Linux ==="
    run_scripts "${DOTFILES_DIR}/install.d/linux"
    ;;
  *)
    echo "Unknown OS: $OS — skipping platform scripts."
    ;;
esac

echo ""
echo "Dotfiles install complete. (mode: ${DOTFILES_MODE})"
