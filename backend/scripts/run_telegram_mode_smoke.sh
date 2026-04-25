#!/usr/bin/env bash
set -euo pipefail

BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
EXPECTED_WEBHOOK_URL="${EXPECTED_WEBHOOK_URL:-}"
RESTORE_WEBHOOK_URL="${RESTORE_WEBHOOK_URL:-}"
SECRET_TOKEN="${TELEGRAM_WEBHOOK_SECRET:-}"
LISTEN_TIMEOUT_SECONDS="${LISTEN_TIMEOUT_SECONDS:-2}"
LISTEN_LIMIT="${LISTEN_LIMIT:-5}"
REQUIRED_CHAT_ID="${REQUIRED_CHAT_ID:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bot-token)
      BOT_TOKEN="${2:-}"
      shift 2
      ;;
    --expected-webhook-url)
      EXPECTED_WEBHOOK_URL="${2:-}"
      shift 2
      ;;
    --restore-webhook-url)
      RESTORE_WEBHOOK_URL="${2:-}"
      shift 2
      ;;
    --secret-token)
      SECRET_TOKEN="${2:-}"
      shift 2
      ;;
    --listen-timeout-seconds)
      LISTEN_TIMEOUT_SECONDS="${2:-}"
      shift 2
      ;;
    --listen-limit)
      LISTEN_LIMIT="${2:-}"
      shift 2
      ;;
    --required-chat-id)
      REQUIRED_CHAT_ID="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$BOT_TOKEN" ]]; then
  echo "Missing bot token. Use --bot-token or TELEGRAM_BOT_TOKEN." >&2
  exit 1
fi

TELEGRAM_API_BASE="https://api.telegram.org/bot${BOT_TOKEN}"

telegram_api_call() {
  local method="$1"
  local payload="$2"
  curl -sS -X POST "${TELEGRAM_API_BASE}/${method}" \
    -H "Content-Type: application/json" \
    -d "${payload}"
}

WEBHOOK_INFO="$(telegram_api_call "getWebhookInfo" "{}")"
CURRENT_WEBHOOK_URL="$(printf '%s' "$WEBHOOK_INFO" | sed -n 's/.*"url":"\([^"]*\)".*/\1/p')"
PENDING_UPDATE_COUNT="$(printf '%s' "$WEBHOOK_INFO" | sed -n 's/.*"pending_update_count":\([0-9]\+\).*/\1/p')"
if [[ -z "$PENDING_UPDATE_COUNT" ]]; then
  PENDING_UPDATE_COUNT="0"
fi

if [[ -n "$EXPECTED_WEBHOOK_URL" ]] && [[ "$CURRENT_WEBHOOK_URL" != "$EXPECTED_WEBHOOK_URL" ]]; then
  echo "Warning: webhook URL mismatch. current='${CURRENT_WEBHOOK_URL}', expected='${EXPECTED_WEBHOOK_URL}'." >&2
fi

if [[ -z "$RESTORE_WEBHOOK_URL" ]]; then
  RESTORE_WEBHOOK_URL="$CURRENT_WEBHOOK_URL"
fi

if [[ -z "$RESTORE_WEBHOOK_URL" ]]; then
  echo "Cannot restore webhook automatically: provide --restore-webhook-url." >&2
  exit 1
fi

DELETE_WEBHOOK_RESULT="$(telegram_api_call "deleteWebhook" '{"drop_pending_updates":false}')"
UPDATES_RESULT="$(telegram_api_call "getUpdates" "{\"timeout\":${LISTEN_TIMEOUT_SECONDS},\"limit\":${LISTEN_LIMIT}}")"
DISCOVERED_CHAT_IDS="$(printf '%s' "$UPDATES_RESULT" | sed -n 's/.*"chat":{"id":\(-\?[0-9]\+\).*/\1/p' | sort -u | tr '\n' ',' | sed 's/,$//')"

if [[ -n "$REQUIRED_CHAT_ID" ]]; then
  if [[ ",${DISCOVERED_CHAT_IDS}," != *",${REQUIRED_CHAT_ID},"* ]]; then
    echo "Required chat_id '${REQUIRED_CHAT_ID}' not found in getUpdates probe." >&2
    exit 1
  fi
elif [[ -z "$DISCOVERED_CHAT_IDS" ]]; then
  echo "Warning: no chat_id detected in getUpdates probe. Verify bot-start handshake." >&2
fi

if [[ -n "$SECRET_TOKEN" ]]; then
  RESTORE_PAYLOAD="$(printf '{"url":"%s","secret_token":"%s"}' "$RESTORE_WEBHOOK_URL" "$SECRET_TOKEN")"
else
  RESTORE_PAYLOAD="$(printf '{"url":"%s"}' "$RESTORE_WEBHOOK_URL")"
fi
RESTORE_RESULT="$(telegram_api_call "setWebhook" "$RESTORE_PAYLOAD")"

printf '%s\n' "{"
printf '  "webhook_mode": {"current_url": "%s", "pending_update_count": %s},\n' "$CURRENT_WEBHOOK_URL" "$PENDING_UPDATE_COUNT"
printf '  "listen_probe": {"discovered_chat_ids": "%s"},\n' "$DISCOVERED_CHAT_IDS"
printf '  "responses": {\n'
printf '    "getWebhookInfo": %s,\n' "$WEBHOOK_INFO"
printf '    "deleteWebhook": %s,\n' "$DELETE_WEBHOOK_RESULT"
printf '    "getUpdates": %s,\n' "$UPDATES_RESULT"
printf '    "setWebhook": %s\n' "$RESTORE_RESULT"
printf '  },\n'
printf '  "preconditions": {\n'
printf '    "bot_started_by_user": "required",\n'
printf '    "chat_id_available": "required_for_delivery_validation"\n'
printf '  }\n'
printf '}\n'
