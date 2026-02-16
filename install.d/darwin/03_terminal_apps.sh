#!/bin/bash
# Symlink terminal app configs (ghostty, kitty, alacritty)
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"

mkdir -p "${HOME}/.config"
mkdir -p "${HOME}/.config/alacritty"

# ghostty
if [[ -d "${DOTFILES_DIR}/ghostty" ]]; then
  if [[ -L "${HOME}/.config/ghostty" ]]; then
    rm "${HOME}/.config/ghostty"
  fi
  if [[ ! -d "${HOME}/.config/ghostty" ]]; then
    ln -s "${DOTFILES_DIR}/ghostty" "${HOME}/.config/ghostty"
    echo "Linked ghostty config."
  fi
fi

# kitty
if [[ -d "${DOTFILES_DIR}/kitty" ]]; then
  if [[ -L "${HOME}/.config/kitty" ]]; then
    rm "${HOME}/.config/kitty"
  fi
  if [[ ! -d "${HOME}/.config/kitty" ]]; then
    ln -s "${DOTFILES_DIR}/kitty" "${HOME}/.config/kitty"
    echo "Linked kitty config."
  fi
fi

# alacritty
if [[ -d "${DOTFILES_DIR}/alacritty" ]]; then
  for f in "${DOTFILES_DIR}"/alacritty/*.yml; do
    [[ -f "$f" ]] || continue
    ln -sf "$f" "${HOME}/.config/alacritty/$(basename "$f")"
  done
  echo "Linked alacritty config."
fi

# hushlogin
if [[ -f "${DOTFILES_DIR}/other/hushlogin" ]]; then
  ln -sf "${DOTFILES_DIR}/other/hushlogin" "${HOME}/.hushlogin"
  echo "Linked hushlogin."
fi
