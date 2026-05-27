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

echo ""
echo "Done. Available skills:"
echo "  /proofcheck      — verify mathematical proofs"
echo "  /proof-repair    — literature-backed repair plans"
echo "  /theory-sharpen  — strengthen theoretical results"
echo "  /proof-writer    — write rigorous corrected proofs"
echo ""
echo "Optional: enable Codex MCP cross-review:"
echo "  claude mcp add codex -s user -- codex mcp-server"
