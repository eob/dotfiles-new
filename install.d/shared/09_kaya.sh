#!/bin/bash
# Install Kaya (kaya, kayad, kaya-tool-server) into ~/.kaya with the official
# installer from kaya-lang.org. Optional: an unsupported platform or a failed
# download warns and moves on rather than aborting the rest of the dotfiles.
set -euo pipefail

# Bump to upgrade, or run with KAYA_VERSION=latest for the stable channel.
KAYA_VERSION="${KAYA_VERSION:-0.1.0}"
KAYA_INSTALL_DIR="${KAYA_INSTALL_DIR:-${HOME}/.kaya}"
export KAYA_VERSION KAYA_INSTALL_DIR

# The installer selects ~/.kaya/current -> versions/<version>-<archive sha256>.
current="$(readlink "${KAYA_INSTALL_DIR}/current" 2>/dev/null || true)"
digest="${current#versions/${KAYA_VERSION}-}"
if [[ "$digest" != "$current" && "$digest" =~ ^[0-9a-f]{64}$ ]]; then
  echo "Kaya ${KAYA_VERSION} already installed."
  exit 0
fi

# The installer refuses a pre-release "flat" install (real binaries in
# ~/.kaya/bin rather than links into ~/.kaya/current). Migrating it means
# stopping its kayad first, so leave that to a human.
if [[ -e "${KAYA_INSTALL_DIR}/bin/kaya" && ! -L "${KAYA_INSTALL_DIR}/bin/kaya" ]]; then
  echo "Skipping Kaya: ${KAYA_INSTALL_DIR}/bin holds a legacy flat install."
  echo "  Stop its kayad and move ${KAYA_INSTALL_DIR}/bin aside, then re-run."
  exit 0
fi

# The installer appends a PATH line to ~/.zshrc unless ~/.kaya/bin is already
# on PATH, and ~/.zshrc is a symlink into this repo. zsh/zshrc adds it itself.
export PATH="${KAYA_INSTALL_DIR}/bin:${PATH}"

echo "Installing Kaya ${KAYA_VERSION}..."
if ! curl -fsSL https://kaya-lang.org/install.sh | bash; then
  echo "Kaya install failed (see above) — skipping."
  exit 0
fi

# Non-zsh sessions (see 05_shell_aliases.sh).
line='export PATH="${HOME}/.kaya/bin:${PATH}"'
if [[ -f "${HOME}/.bashrc" ]] && ! grep -qF '.kaya/bin' "${HOME}/.bashrc"; then
  echo "$line" >>"${HOME}/.bashrc"
fi
