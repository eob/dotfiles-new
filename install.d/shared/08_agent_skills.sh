#!/bin/bash
# Copy agent skills to Claude Code, Google Antigravity, OpenAI Codex, and OpenCode.
# Uses directory copying rather than symlinking to allow maintaining private skills
# locally in agent skill directories without exposing them to this public repository.
set -euo pipefail

DOTFILES_DIR="${HOME}/.dotfiles"
SKILLS_DIR="${DOTFILES_DIR}/skills"

[[ -d "${SKILLS_DIR}" ]] || exit 0

TARGET_DIRS=(
  "${HOME}/.claude/skills"
  "${HOME}/.gemini/config/skills"
  "${HOME}/.codex/skills"
  "${HOME}/.config/opencode/skills"
)

# Ensure target directories exist
for target in "${TARGET_DIRS[@]}"; do
  mkdir -p "${target}"
done

# Copy each shared skill into the target directories
for skill in "${SKILLS_DIR}"/*; do
  [[ -d "${skill}" ]] || continue
  skill_name="$(basename "${skill}")"

  for target in "${TARGET_DIRS[@]}"; do
    dest="${target}/${skill_name}"

    # Remove existing symlink or old copy of this specific skill
    if [[ -L "${dest}" || -d "${dest}" ]]; then
      rm -rf "${dest}"
    fi

    cp -r "${skill}" "${dest}"
    echo "Copied skill ${skill_name} to ${target}/"
  done
done
