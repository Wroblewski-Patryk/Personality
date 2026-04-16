#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <base_url> [text] [user_id] [debug]" >&2
  exit 1
fi

BASE_URL="${1%/}"
TEXT="${2:-AION manual smoke test}"
USER_ID="${3:-manual-smoke}"
DEBUG_FLAG="${4:-false}"

BASE_URL="$BASE_URL" \
TEXT="$TEXT" \
USER_ID="$USER_ID" \
DEBUG_FLAG="$DEBUG_FLAG" \
python3 - <<'PY'
import json
import os
import urllib.parse
import urllib.request
import uuid

base_url = os.environ["BASE_URL"].rstrip("/")
text = os.environ["TEXT"]
user_id = os.environ["USER_ID"]
debug_flag = os.environ["DEBUG_FLAG"].strip().lower() in {"1", "true", "yes", "debug"}
trace_id = str(uuid.uuid4())

health_request = urllib.request.Request(f"{base_url}/health", method="GET")
with urllib.request.urlopen(health_request, timeout=30) as response:
    health = json.loads(response.read().decode("utf-8"))

if health.get("status") != "ok":
    raise SystemExit(f"Health check failed: unexpected status {health.get('status')!r}")

payload = {
    "source": "api",
    "subsource": "manual_smoke",
    "text": text,
    "meta": {
        "user_id": user_id,
        "trace_id": trace_id,
    },
}

event_url = f"{base_url}/event"
if debug_flag:
    event_url = f"{event_url}?{urllib.parse.urlencode({'debug': 'true'})}"

body = json.dumps(payload).encode("utf-8")
request = urllib.request.Request(
    event_url,
    data=body,
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)

with urllib.request.urlopen(request, timeout=60) as response:
    result = json.loads(response.read().decode("utf-8"))

if not result.get("event_id"):
    raise SystemExit("Smoke request failed: response is missing event_id")
if not result.get("reply", {}).get("message"):
    raise SystemExit("Smoke request failed: response is missing reply.message")
if not result.get("runtime", {}).get("role"):
    raise SystemExit("Smoke request failed: response is missing runtime.role")
if debug_flag and "debug" not in result:
    raise SystemExit("Smoke request failed: debug=true was requested but debug payload is missing")

summary = {
    "base_url": base_url,
    "health_status": health.get("status"),
    "reflection_healthy": health.get("reflection", {}).get("healthy"),
    "event_id": result.get("event_id"),
    "trace_id": result.get("trace_id"),
    "reply_message": result.get("reply", {}).get("message"),
    "reply_language": result.get("reply", {}).get("language"),
    "runtime_role": result.get("runtime", {}).get("role"),
    "runtime_action": result.get("runtime", {}).get("action_status"),
    "reflection_triggered": result.get("runtime", {}).get("reflection_triggered"),
    "debug_included": "debug" in result,
}

print(json.dumps(summary, ensure_ascii=False))
PY
