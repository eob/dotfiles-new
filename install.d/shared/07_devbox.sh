#!/bin/bash
# Scaffold the devbox connection vars into ~/.zshrc.local (gitignored, machine
# specific). Appends a commented template once; never overwrites real values.
set -euo pipefail

LOCAL="${HOME}/.zshrc.local"

if [[ -f "$LOCAL" ]] && grep -q "DEVBOX_IP" "$LOCAL"; then
  echo "devbox vars already present in ~/.zshrc.local."
  exit 0
fi

cat >>"$LOCAL" <<'EOF'

# --- devbox (used by `devbox` and `devbox-ssh`) -----------------------------
# Fill these in, then `source ~/.zshrc`.
export DEVBOX_IP=""          # devbox public IP / host
export DEVBOX_USERNAME=""    # ssh username
# export DEVBOX_PORT=443           # SSH TCP port  (default 443)
# export DEVBOX_MOSH_PORT=443      # mosh UDP port (default 443)
# export DEVBOX_SSH_KEY="$HOME/.ssh/id_ed25519"
EOF

echo "Added devbox template to ~/.zshrc.local — fill in DEVBOX_IP / DEVBOX_USERNAME."
