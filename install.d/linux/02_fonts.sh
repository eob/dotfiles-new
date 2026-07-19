#!/bin/bash
# Install fonts the kaya-web print pipeline depends on (Linux/devbox).
#
# Noto CJK (Sans + Serif, SC/TC/JP/KR) is required by the RBC hanzi reading
# blocks (packages/kaya-projects/src/blocks/hanzi-core.tsx): their print font
# stacks lead with "Noto Sans CJK SC/TC", and Noto Sans CJK is the face that
# carries bopomofo + zhuyin tone marks together. Without it the pagedjs/
# puppeteer render host silently falls back to WenQuanYi Zen Hei (and has no
# serif CJK at all).
set -euo pipefail

# NB: no `grep -q` here — its early exit SIGPIPEs fc-list, which reads as a
# pipeline failure under pipefail and defeats the guard.
if ! fc-list : family 2>/dev/null | grep "Noto Sans CJK" >/dev/null; then
  echo "Installing Noto CJK fonts..."
  sudo apt-get update -qq
  sudo apt-get install -y -qq fonts-noto-cjk fonts-noto-cjk-extra >/dev/null
  fc-cache -f >/dev/null 2>&1 || true
fi

echo "Fonts ready."
