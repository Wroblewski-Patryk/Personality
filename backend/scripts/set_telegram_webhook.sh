#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <webhook_url> [api_base] [secret_token]"
  exit 1
fi

WEBHOOK_URL="$1"
API_BASE="${2:-http://localhost:8000}"
SECRET_TOKEN="${3:-}"

if [[ -n "$SECRET_TOKEN" ]]; then
  BODY=$(printf '{"webhook_url":"%s","secret_token":"%s"}' "$WEBHOOK_URL" "$SECRET_TOKEN")
else
  BODY=$(printf '{"webhook_url":"%s"}' "$WEBHOOK_URL")
fi

curl -sS -X POST "${API_BASE}/telegram/set-webhook" \
  -H "Content-Type: application/json" \
  -d "${BODY}"

echo

