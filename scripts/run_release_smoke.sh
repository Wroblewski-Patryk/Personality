#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <base_url> [text] [user_id] [debug] [deployment_evidence_path] [deployment_evidence_max_age_minutes]" >&2
  exit 1
fi

BASE_URL="${1%/}"
TEXT="${2:-AION manual smoke test}"
USER_ID="${3:-manual-smoke}"
DEBUG_FLAG="${4:-false}"
DEPLOYMENT_EVIDENCE_PATH="${5:-}"
DEPLOYMENT_EVIDENCE_MAX_AGE_MINUTES="${6:-60}"

BASE_URL="$BASE_URL" \
TEXT="$TEXT" \
USER_ID="$USER_ID" \
DEBUG_FLAG="$DEBUG_FLAG" \
DEPLOYMENT_EVIDENCE_PATH="$DEPLOYMENT_EVIDENCE_PATH" \
DEPLOYMENT_EVIDENCE_MAX_AGE_MINUTES="$DEPLOYMENT_EVIDENCE_MAX_AGE_MINUTES" \
python3 - <<'PY'
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request
import uuid

base_url = os.environ["BASE_URL"].rstrip("/")
text = os.environ["TEXT"]
user_id = os.environ["USER_ID"]
debug_flag = os.environ["DEBUG_FLAG"].strip().lower() in {"1", "true", "yes", "debug"}
deployment_evidence_path = os.environ.get("DEPLOYMENT_EVIDENCE_PATH", "").strip()
try:
    deployment_evidence_max_age_minutes = int(os.environ.get("DEPLOYMENT_EVIDENCE_MAX_AGE_MINUTES", "60"))
except ValueError:
    raise SystemExit("Deployment evidence verification failed: invalid max age minutes value.")
trace_id = str(uuid.uuid4())

deployment_evidence_checked = False
deployment_evidence_age_minutes = None
deployment_evidence_status_code = None

if deployment_evidence_path:
    evidence_file = Path(deployment_evidence_path)
    if not evidence_file.exists():
        raise SystemExit(f"Deployment evidence verification failed: file not found {deployment_evidence_path!r}")

    try:
        evidence = json.loads(evidence_file.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, json.JSONDecodeError):
        raise SystemExit(f"Deployment evidence verification failed: invalid JSON in {deployment_evidence_path!r}")

    if not isinstance(evidence, dict) or evidence.get("kind") != "coolify_deploy_webhook_evidence":
        raise SystemExit("Deployment evidence verification failed: unexpected evidence kind.")

    response = evidence.get("response")
    if not isinstance(response, dict):
        raise SystemExit("Deployment evidence verification failed: response block is missing.")

    response_ok = bool(response.get("ok"))
    try:
        deployment_evidence_status_code = int(response.get("status_code", 0))
    except (TypeError, ValueError):
        deployment_evidence_status_code = 0
    if not response_ok or deployment_evidence_status_code < 200 or deployment_evidence_status_code >= 300:
        raise SystemExit("Deployment evidence verification failed: webhook response is not successful.")

    generated_at_raw = str(evidence.get("generated_at") or "").strip()
    if not generated_at_raw:
        raise SystemExit("Deployment evidence verification failed: generated_at is missing.")
    generated_at = generated_at_raw.replace("Z", "+00:00")
    try:
        generated_at_dt = datetime.fromisoformat(generated_at).astimezone(timezone.utc)
    except ValueError:
        raise SystemExit("Deployment evidence verification failed: generated_at is invalid.")
    deployment_evidence_age_minutes = round(
        (datetime.now(timezone.utc) - generated_at_dt).total_seconds() / 60.0,
        2,
    )
    if deployment_evidence_age_minutes > deployment_evidence_max_age_minutes:
        raise SystemExit(
            "Deployment evidence verification failed: evidence age "
            f"{deployment_evidence_age_minutes} min exceeds {deployment_evidence_max_age_minutes} min."
        )
    deployment_evidence_checked = True

health_request = urllib.request.Request(f"{base_url}/health", method="GET")
with urllib.request.urlopen(health_request, timeout=30) as response:
    health = json.loads(response.read().decode("utf-8"))

if health.get("status") != "ok":
    raise SystemExit(f"Health check failed: unexpected status {health.get('status')!r}")

runtime_policy = health.get("runtime_policy")
if not isinstance(runtime_policy, dict):
    raise SystemExit("Health check failed: response is missing runtime_policy")

expected_internal_debug_ingress_path = "/internal/event/debug"
expected_shared_debug_ingress_path = "/event/debug"

internal_debug_ingress_path = str(runtime_policy.get("event_debug_internal_ingress_path", "")).strip()
if internal_debug_ingress_path != expected_internal_debug_ingress_path:
    raise SystemExit(
        "Health check failed: unexpected event_debug_internal_ingress_path "
        f"{internal_debug_ingress_path!r}"
    )

shared_debug_ingress_path = str(runtime_policy.get("event_debug_shared_ingress_path", "")).strip()
if shared_debug_ingress_path != expected_shared_debug_ingress_path:
    raise SystemExit(
        "Health check failed: unexpected event_debug_shared_ingress_path "
        f"{shared_debug_ingress_path!r}"
    )

shared_debug_ingress_mode = str(runtime_policy.get("event_debug_shared_ingress_mode", "")).strip()
if shared_debug_ingress_mode not in {"compatibility", "break_glass_only"}:
    raise SystemExit(
        "Health check failed: unexpected event_debug_shared_ingress_mode "
        f"{shared_debug_ingress_mode!r}"
    )

shared_break_glass_required = bool(runtime_policy.get("event_debug_shared_ingress_break_glass_required"))
expected_shared_break_glass_required = shared_debug_ingress_mode == "break_glass_only"
if shared_break_glass_required != expected_shared_break_glass_required:
    raise SystemExit("Health check failed: inconsistent shared ingress break-glass requirement")

shared_ingress_posture = str(runtime_policy.get("event_debug_shared_ingress_posture", "")).strip()
expected_shared_ingress_posture = (
    "shared_route_break_glass_only"
    if expected_shared_break_glass_required
    else "shared_route_compatibility"
)
if shared_ingress_posture != expected_shared_ingress_posture:
    raise SystemExit(
        "Health check failed: inconsistent shared ingress posture "
        f"{shared_ingress_posture!r}"
    )

release_readiness = health.get("release_readiness")
if isinstance(release_readiness, dict) and "ready" in release_readiness:
    release_ready = bool(release_readiness.get("ready"))
    release_violations = [
        str(item)
        for item in release_readiness.get("violations", [])
        if isinstance(item, str) and item.strip()
    ]
else:
    release_violations = []
    if runtime_policy.get("production_policy_mismatches"):
        release_violations.append("runtime_policy.production_policy_mismatches_non_empty")
    if bool(runtime_policy.get("strict_startup_blocked")):
        release_violations.append("runtime_policy.strict_startup_blocked=true")
    if bool(runtime_policy.get("event_debug_query_compat_enabled")):
        release_violations.append("runtime_policy.event_debug_query_compat_enabled=true")
    release_ready = len(release_violations) == 0

if not release_ready:
    details = ",".join(release_violations) if release_violations else "unspecified"
    raise SystemExit(f"Release readiness check failed: {details}")

reflection = health.get("reflection")
if not isinstance(reflection, dict):
    raise SystemExit("Health check failed: response is missing reflection")

deployment_readiness = reflection.get("deployment_readiness")
if isinstance(deployment_readiness, dict) and "ready" in deployment_readiness:
    reflection_deployment_ready = bool(deployment_readiness.get("ready"))
    reflection_deployment_violations = [
        str(item)
        for item in deployment_readiness.get("blocking_signals", [])
        if isinstance(item, str) and item.strip()
    ]
else:
    runtime_mode = str(reflection.get("runtime_mode", "in_process")).strip().lower() or "in_process"
    worker = reflection.get("worker")
    worker_running = bool(worker.get("running")) if isinstance(worker, dict) else False
    topology = reflection.get("topology") if isinstance(reflection.get("topology"), dict) else {}
    tasks = reflection.get("tasks") if isinstance(reflection.get("tasks"), dict) else {}

    fallback_signals: list[str] = []
    if runtime_mode == "deferred":
        if worker_running:
            fallback_signals.append("deferred_in_process_worker_running")
        if topology.get("queue_drain_owner") != "external_driver":
            fallback_signals.append("deferred_queue_drain_owner_mismatch")
        if not bool(topology.get("external_driver_expected")):
            fallback_signals.append("deferred_external_driver_expectation_missing")
        if not bool(topology.get("scheduler_tick_dispatch")):
            fallback_signals.append("deferred_scheduler_dispatch_flag_mismatch")
    else:
        if not worker_running:
            fallback_signals.append("in_process_worker_not_running")
        if topology.get("queue_drain_owner") != "in_process_worker":
            fallback_signals.append("in_process_queue_drain_owner_mismatch")
        if bool(topology.get("external_driver_expected")):
            fallback_signals.append("in_process_external_driver_flag_mismatch")
        if bool(topology.get("scheduler_tick_dispatch")):
            fallback_signals.append("in_process_scheduler_dispatch_flag_mismatch")

    try:
        stuck_processing = max(0, int(tasks.get("stuck_processing", 0)))
    except (TypeError, ValueError):
        stuck_processing = 0
    try:
        exhausted_failed = max(0, int(tasks.get("exhausted_failed", 0)))
    except (TypeError, ValueError):
        exhausted_failed = 0
    if stuck_processing > 0:
        fallback_signals.append("reflection_stuck_processing_detected")
    if exhausted_failed > 0:
        fallback_signals.append("reflection_exhausted_failures_detected")

    reflection_deployment_violations = fallback_signals
    reflection_deployment_ready = len(reflection_deployment_violations) == 0

if not reflection_deployment_ready:
    details = ",".join(reflection_deployment_violations) if reflection_deployment_violations else "unspecified"
    raise SystemExit(f"Reflection deployment readiness check failed: {details}")

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
    "release_ready": release_ready,
    "release_violations": release_violations,
    "reflection_deployment_ready": reflection_deployment_ready,
    "reflection_deployment_violations": reflection_deployment_violations,
    "debug_internal_ingress_path": internal_debug_ingress_path,
    "debug_shared_ingress_path": shared_debug_ingress_path,
    "debug_shared_ingress_mode": shared_debug_ingress_mode,
    "debug_shared_break_glass_required": shared_break_glass_required,
    "debug_shared_ingress_posture": shared_ingress_posture,
    "debug_included": "debug" in result,
    "deployment_evidence_checked": deployment_evidence_checked,
    "deployment_evidence_path": deployment_evidence_path,
    "deployment_evidence_age_minutes": deployment_evidence_age_minutes,
    "deployment_evidence_status_code": deployment_evidence_status_code,
}

print(json.dumps(summary, ensure_ascii=False))
PY
