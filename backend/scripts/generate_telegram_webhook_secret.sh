#!/usr/bin/env bash
set -euo pipefail

BYTES="${1:-32}"
ENV_PATH="${2:-.env}"
UPDATE_ENV="${3:-false}"

if [[ "$BYTES" -lt 16 ]]; then
  echo "Bytes must be >= 16 for sufficient entropy."
  exit 1
fi

if command -v openssl >/dev/null 2>&1; then
  SECRET="$(openssl rand -base64 "$BYTES" | tr '+/' '-_' | tr -d '=' | tr -d '\n')"
else
  SECRET="$(python3 - <<'PY'
import base64, secrets
raw = secrets.token_bytes(32)
print(base64.urlsafe_b64encode(raw).decode().rstrip("="))
PY
)"
fi

if [[ "$UPDATE_ENV" == "true" ]]; then
  if [[ ! -f "$ENV_PATH" ]]; then
    echo "Env file not found: $ENV_PATH"
    exit 1
  fi

  if grep -q '^TELEGRAM_WEBHOOK_SECRET=' "$ENV_PATH"; then
    sed -i "s#^TELEGRAM_WEBHOOK_SECRET=.*#TELEGRAM_WEBHOOK_SECRET=${SECRET}#g" "$ENV_PATH"
  else
    printf '\nTELEGRAM_WEBHOOK_SECRET=%s\n' "$SECRET" >> "$ENV_PATH"
  fi

  echo "Updated $ENV_PATH"
fi

echo "TELEGRAM_WEBHOOK_SECRET=$SECRET"

