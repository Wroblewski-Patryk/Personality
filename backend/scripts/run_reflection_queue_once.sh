#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

limit="${1:-10}"
shift || true

cd "$REPO_ROOT"
python "${SCRIPT_DIR}/run_reflection_queue_once.py" --limit "$limit" "$@"
