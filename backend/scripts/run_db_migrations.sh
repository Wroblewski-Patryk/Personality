#!/usr/bin/env bash
set -euo pipefail

revision="${1:-head}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "$REPO_ROOT"
python -m alembic -c "${REPO_ROOT}/backend/alembic.ini" upgrade "$revision"
