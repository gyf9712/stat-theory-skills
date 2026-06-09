#!/usr/bin/env bash
# Install stat-theory-skills into ~/.claude/skills/
# Usage: bash install.sh [--force]

set -euo pipefail

SKILL_DIR="${HOME}/.claude/skills"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
FORCE="${1:-}"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "ERROR: source skills/ directory not found at ${SOURCE_DIR}"
  exit 1
fi

mkdir -p "${SKILL_DIR}"

echo "Installing stat-theory-skills → ${SKILL_DIR}"
echo ""

for skill_path in "${SOURCE_DIR}"/*/; do
  skill_name="$(basename "${skill_path}")"
  target="${SKILL_DIR}/${skill_name}"

  if [[ -d "${target}" && "${FORCE}" != "--force" ]]; then
    echo "  [SKIP] ${skill_name} (already exists — use --force to overwrite)"
    continue
  fi

  rm -rf "${target}"
  cp -r "${skill_path}" "${target}"
  echo "  [OK]   ${skill_name}"
done

# Install shared reference files (proof-strategy etc.) into stat-shared-references/.
# Files are copied individually so we do not clobber stat-shared-references/
# content owned by stat-writing-skills.
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_SRC="${REPO_DIR}/stat-shared-references"
SHARED_DST="${SKILL_DIR}/stat-shared-references"

if [[ -d "${SHARED_SRC}" ]]; then
  mkdir -p "${SHARED_DST}"
  echo ""
  echo "Installing shared references → ${SHARED_DST}"
  for f in "${SHARED_SRC}"/*.md; do
    [[ -e "${f}" ]] || continue
    fname="$(basename "${f}")"
    target="${SHARED_DST}/${fname}"
    if [[ -e "${target}" && "${FORCE}" != "--force" ]]; then
      echo "  [SKIP] ${fname} (already exists — use --force to overwrite)"
      continue
    fi
    cp "${f}" "${target}"
    echo "  [OK]   ${fname}"
  done

  # Install the scripts/ subdirectory (proof_index.py etc.) wholesale.
  if [[ -d "${SHARED_SRC}/scripts" ]]; then
    mkdir -p "${SHARED_DST}/scripts"
    for s in "${SHARED_SRC}/scripts"/*.py; do
      [[ -e "${s}" ]] || continue
      cp "${s}" "${SHARED_DST}/scripts/"
      echo "  [OK]   scripts/$(basename "${s}")"
    done
  fi
fi

echo ""
echo "Done. Available skills:"
echo "  /proofcheck      — verify mathematical proofs"
echo "  /proof-repair    — literature-backed repair plans"
echo "  /theory-sharpen  — strengthen theoretical results"
echo "  /proof-writer    — write rigorous corrected proofs"
echo ""
echo "⚠️  IMPORTANT: These skills require Claude Opus for proper mathematical reasoning."
echo "   Before invoking any skill, run in Claude Code:"
echo "     /model opus"
echo ""
echo "   Or set Opus as default in ~/.claude/settings.json:"
echo '     { "model": "opus", "effortLevel": "high" }'
echo ""
echo "Optional: enable Codex MCP cross-review (independent second opinion):"
echo "  claude mcp add codex -s user -- codex mcp-server"
