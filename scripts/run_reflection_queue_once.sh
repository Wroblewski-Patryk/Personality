#!/usr/bin/env bash
set -euo pipefail

limit="${1:-10}"
shift || true

python ./scripts/run_reflection_queue_once.py --limit "$limit" "$@"
