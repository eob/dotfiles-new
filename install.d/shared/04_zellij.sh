#!/bin/bash
# Zellij setup: symlink our minimal config (theme only — everything else stays
# default) and migrate away from the old tmux setup.
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"

# Remove a stale ~/.tmux.conf symlink left by the previous tmux config.
if [[ -L "${HOME}/.tmux.conf" ]]; then
  rm -f "${HOME}/.tmux.conf"
  echo "Removed stale ~/.tmux.conf symlink."
fi

# Symlink the zellij config. If zellij already auto-dumped a real config.kdl,
# back it up first so we don't clobber anything unexpectedly.
mkdir -p "${HOME}/.config/zellij"
target="${HOME}/.config/zellij/config.kdl"
if [[ -e "$target" && ! -L "$target" ]]; then
  mv "$target" "${target}.pre-dotfiles.bak"
  echo "Backed up existing config.kdl -> config.kdl.pre-dotfiles.bak"
fi
ln -sf "${DOTFILES_DIR}/zellij/config.kdl" "$target"

# Symlink the default layout (coconut tab title). Same backup dance.
mkdir -p "${HOME}/.config/zellij/layouts"
layout_target="${HOME}/.config/zellij/layouts/default.kdl"
if [[ -e "$layout_target" && ! -L "$layout_target" ]]; then
  mv "$layout_target" "${layout_target}.pre-dotfiles.bak"
  echo "Backed up existing layouts/default.kdl -> default.kdl.pre-dotfiles.bak"
fi
ln -sf "${DOTFILES_DIR}/zellij/layouts/default.kdl" "$layout_target"

if command -v zellij &>/dev/null; then
  echo "zellij ready (theme: tokyo-night-dark)."
else
  echo "zellij not found — it is installed by the platform CLI tools script."
fi
