#!/usr/bin/env bash
# Install the self-contained Rex Mac app from Superlogical's preview channel.
set -euo pipefail

if [[ "$(uname -s)" != Darwin ]]; then
  echo "Rex.app is for macOS; run this installer on your Mac." >&2
  exit 1
fi

app_dir="${HOME}/Applications"
if [[ -d /Applications/Rex.app || -d "${app_dir}/Rex.app" ]]; then
  echo "Rex.app is already installed."
  exit 0
fi

mkdir -p "$app_dir"
install_tmp="$(mktemp -d "${app_dir}/.rex-install.XXXXXX")"
mounted=false
cleanup() {
  if [[ "$mounted" == true ]] && ! hdiutil detach "$install_tmp/mount" >/dev/null; then
    echo "Could not detach $install_tmp/mount; leaving the temporary files in place." >&2
    return
  fi
  rm -rf "$install_tmp"
}
trap cleanup EXIT

curl -fL --proto '=https' --tlsv1.2 \
  https://blob.superlogical.com/download/rex-app/preview/latest.dmg \
  -o "$install_tmp/Rex.dmg"
mkdir "$install_tmp/mount"
hdiutil attach -readonly -nobrowse -mountpoint "$install_tmp/mount" \
  "$install_tmp/Rex.dmg" >/dev/null
mounted=true
ditto "$install_tmp/mount/Rex.app" "$install_tmp/Rex.app"
mv "$install_tmp/Rex.app" "${app_dir}/Rex.app"
echo "Installed ${app_dir}/Rex.app. Open Rex, then run devbox or devbox-ssh."
