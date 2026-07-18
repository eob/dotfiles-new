#!/bin/bash
# Install CLI tools on Linux. Supports Arch (pacman, e.g. Omarchy) and
# Debian/Ubuntu (apt + curl).
set -euo pipefail

# ---- Arch / Omarchy (pacman) ----------------------------------------------
# Most of these ship with Omarchy already; --needed skips anything present.
if command -v pacman &>/dev/null; then
  echo "Detected pacman (Arch/Omarchy)."
  sudo pacman -S --needed --noconfirm \
    zsh \
    zsh-completions \
    zsh-syntax-highlighting \
    zsh-autosuggestions \
    zellij \
    git-delta \
    fzf \
    zoxide \
    eza
  echo "Arch CLI tools ready."
  exit 0
fi

# ---- Debian / Ubuntu (apt) ------------------------------------------------
apt_updated=false
apt_update_once() {
  if [[ "$apt_updated" == false ]]; then
    sudo apt-get update -qq
    apt_updated=true
  fi
}

if ! command -v fzf &>/dev/null; then
  echo "Installing fzf..."
  apt_update_once
  sudo apt-get install -y -qq fzf >/dev/null
fi

if ! command -v zellij &>/dev/null; then
  echo "Installing zellij..."
  url=$(curl -sSfL https://api.github.com/repos/zellij-org/zellij/releases/latest \
    | grep "browser_download_url" \
    | grep "zellij-x86_64-unknown-linux-musl.tar.gz" \
    | head -n1 | cut -d '"' -f4)
  curl -sSfL "$url" -o /tmp/zellij.tar.gz
  tar -xzf /tmp/zellij.tar.gz -C /tmp
  sudo install -m755 /tmp/zellij /usr/local/bin/zellij
  rm -f /tmp/zellij.tar.gz /tmp/zellij
fi

if ! command -v zoxide &>/dev/null && ! [[ -x "${HOME}/.local/bin/zoxide" ]]; then
  echo "Installing zoxide..."
  curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
fi

if ! command -v delta &>/dev/null; then
  echo "Installing delta..."
  ver="0.18.2"
  deb="/tmp/git-delta_${ver}_amd64.deb"
  curl -sSfL "https://github.com/dandavison/delta/releases/download/${ver}/git-delta_${ver}_amd64.deb" -o "${deb}"
  sudo dpkg -i "${deb}" >/dev/null
  rm -f "${deb}"
fi

if ! command -v eza &>/dev/null; then
  echo "Installing eza..."
  sudo mkdir -p /etc/apt/keyrings
  wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg 2>/dev/null
  echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list >/dev/null
  sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list
  sudo apt-get update -qq
  apt_updated=true
  sudo apt-get install -y -qq eza >/dev/null 2>&1 || true
fi

if [[ ! -d /usr/share/zsh-syntax-highlighting ]]; then
  echo "Installing zsh-syntax-highlighting..."
  apt_update_once
  sudo apt-get install -y -qq zsh-syntax-highlighting >/dev/null 2>&1 || true
fi

if [[ ! -d /usr/share/zsh-autosuggestions ]]; then
  echo "Installing zsh-autosuggestions..."
  apt_update_once
  sudo apt-get install -y -qq zsh-autosuggestions >/dev/null 2>&1 || true
fi

echo "Linux CLI tools ready."
