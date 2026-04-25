#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "$REPO_ROOT"
"${REPO_ROOT}/.venv/Scripts/python.exe" "${SCRIPT_DIR}/run_maintenance_tick_once.py" "$@"
