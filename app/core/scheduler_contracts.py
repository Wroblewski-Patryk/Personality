from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal


SchedulerSubsource = Literal["reflection_tick", "maintenance_tick", "proactive_tick"]
ReflectionRuntimeMode = Literal["in_process", "deferred"]
SchedulerExecutionMode = Literal["in_process", "externalized"]
SchedulerCadenceDispatchKind = Literal["maintenance_tick", "proactive_tick"]
SCHEDULER_SOURCE = "scheduler"
DEFAULT_SCHEDULER_SUBSOURCE: SchedulerSubsource = "reflection_tick"
DEFAULT_REFLECTION_RUNTIME_MODE: ReflectionRuntimeMode = "in_process"
DEFAULT_SCHEDULER_EXECUTION_MODE: SchedulerExecutionMode = "in_process"
REFLECTION_DEPLOYMENT_BASELINE_MODE: ReflectionRuntimeMode = "in_process"
SCHEDULER_EXECUTION_BASELINE_MODE: SchedulerExecutionMode = "in_process"
SCHEDULER_REFLECTION_TICK: SchedulerSubsource = "reflection_tick"
SCHEDULER_MAINTENANCE_TICK: SchedulerSubsource = "maintenance_tick"
SCHEDULER_PROACTIVE_TICK: SchedulerSubsource = "proactive_tick"
DEFAULT_PROACTIVE_TRIGGER = "time_checkin"
ALLOWED_PROACTIVE_TRIGGERS = {
    "time_checkin",
    "goal_stagnation",
    "goal_deadline",
    "task_blocked",
    "task_overdue",
    "memory_pattern",
    "relation_nudge",
    "external_alert",
}

SCHEDULER_CADENCE_RULES: dict[str, dict[str, int | bool]] = {
    "reflection_tick": {
        "min_interval_seconds": 300,
        "max_interval_seconds": 86_400,
        "background_only": True,
        "user_visible_delivery": False,
    },
    "maintenance_tick": {
        "min_interval_seconds": 900,
        "max_interval_seconds": 172_800,
        "background_only": True,
        "user_visible_delivery": False,
    },
    "proactive_tick": {
        "min_interval_seconds": 1_800,
        "max_interval_seconds": 86_400,
        "background_only": False,
        "user_visible_delivery": True,
    },
}


def normalize_scheduler_subsource(value: str | None) -> SchedulerSubsource:
    normalized = str(value or "").strip().lower()
    if normalized in SCHEDULER_CADENCE_RULES:
        return normalized  # type: ignore[return-value]
    return DEFAULT_SCHEDULER_SUBSOURCE


def normalize_reflection_runtime_mode(value: str | None) -> ReflectionRuntimeMode:
    normalized = str(value or "").strip().lower()
    if normalized == "deferred":
        return "deferred"
    return DEFAULT_REFLECTION_RUNTIME_MODE


def normalize_scheduler_execution_mode(value: str | None) -> SchedulerExecutionMode:
    normalized = str(value or "").strip().lower()
    if normalized == "externalized":
        return "externalized"
    return DEFAULT_SCHEDULER_EXECUTION_MODE


def scheduler_cadence_execution_snapshot(
    *,
    execution_mode: str | None,
    scheduler_enabled: bool,
    scheduler_running: bool,
    proactive_enabled: bool,
) -> dict[str, Any]:
    selected_mode = normalize_scheduler_execution_mode(execution_mode)
    cadence_owner = "external_scheduler" if selected_mode == "externalized" else "in_process_scheduler"
    maintenance_dispatch, maintenance_reason = scheduler_cadence_dispatch_decision(
        execution_mode=selected_mode,
        cadence_kind=SCHEDULER_MAINTENANCE_TICK,
        proactive_enabled=proactive_enabled,
    )
    proactive_dispatch, proactive_reason = scheduler_cadence_dispatch_decision(
        execution_mode=selected_mode,
        cadence_kind=SCHEDULER_PROACTIVE_TICK,
        proactive_enabled=proactive_enabled,
    )
    blocking_signals: list[str] = []

    if selected_mode == "in_process":
        if scheduler_enabled and not scheduler_running:
            blocking_signals.append("in_process_scheduler_not_running")
    elif scheduler_running:
        blocking_signals.append("externalized_scheduler_worker_running")

    return {
        "baseline_execution_mode": SCHEDULER_EXECUTION_BASELINE_MODE,
        "selected_execution_mode": selected_mode,
        "ready": len(blocking_signals) == 0,
        "blocking_signals": blocking_signals,
        "maintenance_cadence_owner": cadence_owner,
        "proactive_cadence_owner": cadence_owner,
        "maintenance_tick_dispatch": maintenance_dispatch,
        "maintenance_tick_reason": maintenance_reason,
        "proactive_tick_dispatch": proactive_dispatch,
        "proactive_tick_reason": proactive_reason,
        "scheduler_enabled": scheduler_enabled,
        "scheduler_running": scheduler_running,
        "proactive_enabled": proactive_enabled,
    }


def reflection_enqueue_dispatch_decision(*, runtime_mode: str | None, worker_running: bool) -> tuple[bool, str]:
    normalized_mode = normalize_reflection_runtime_mode(runtime_mode)
    if normalized_mode == "deferred":
        return False, "deferred_runtime"
    if worker_running:
        return True, "in_process_worker_running"
    return False, "in_process_worker_not_running"


def reflection_scheduler_dispatch_decision(*, runtime_mode: str | None, worker_running: bool) -> tuple[bool, str]:
    normalized_mode = normalize_reflection_runtime_mode(runtime_mode)
    if normalized_mode == "deferred":
        return True, "deferred_runtime"
    if worker_running:
        return False, "in_process_worker_running"
    return True, "in_process_worker_not_running"


def reflection_topology_handoff_posture(*, runtime_mode: str | None, worker_running: bool) -> dict[str, Any]:
    normalized_mode = normalize_reflection_runtime_mode(runtime_mode)
    enqueue_dispatch, enqueue_reason = reflection_enqueue_dispatch_decision(
        runtime_mode=normalized_mode,
        worker_running=worker_running,
    )
    scheduler_dispatch, scheduler_reason = reflection_scheduler_dispatch_decision(
        runtime_mode=normalized_mode,
        worker_running=worker_running,
    )
    queue_drain_owner = "external_driver" if normalized_mode == "deferred" else "in_process_worker"
    return {
        "runtime_mode": normalized_mode,
        "enqueue_owner": "runtime_followup",
        "queue_backend": "durable_postgres_queue",
        "queue_drain_owner": queue_drain_owner,
        "retry_owner": "durable_queue",
        "external_driver_expected": normalized_mode == "deferred",
        "worker_running": worker_running,
        "runtime_enqueue_dispatch": enqueue_dispatch,
        "runtime_enqueue_reason": enqueue_reason,
        "scheduler_tick_dispatch": scheduler_dispatch,
        "scheduler_tick_reason": scheduler_reason,
    }


def _safe_non_negative_int(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def reflection_deployment_readiness_snapshot(
    *,
    runtime_mode: str | None,
    topology: Mapping[str, Any],
    worker_running: bool,
    task_stats: Mapping[str, Any],
) -> dict[str, Any]:
    selected_mode = normalize_reflection_runtime_mode(runtime_mode)
    blocking_signals: list[str] = []

    if selected_mode == "in_process":
        if not worker_running:
            blocking_signals.append("in_process_worker_not_running")
        if topology.get("queue_drain_owner") != "in_process_worker":
            blocking_signals.append("in_process_queue_drain_owner_mismatch")
        if bool(topology.get("external_driver_expected")):
            blocking_signals.append("in_process_external_driver_flag_mismatch")
        if bool(topology.get("scheduler_tick_dispatch")):
            blocking_signals.append("in_process_scheduler_dispatch_flag_mismatch")
    else:
        if worker_running:
            blocking_signals.append("deferred_in_process_worker_running")
        if topology.get("queue_drain_owner") != "external_driver":
            blocking_signals.append("deferred_queue_drain_owner_mismatch")
        if not bool(topology.get("external_driver_expected")):
            blocking_signals.append("deferred_external_driver_expectation_missing")
        if not bool(topology.get("scheduler_tick_dispatch")):
            blocking_signals.append("deferred_scheduler_dispatch_flag_mismatch")

    stuck_processing = _safe_non_negative_int(task_stats.get("stuck_processing"))
    exhausted_failed = _safe_non_negative_int(task_stats.get("exhausted_failed"))

    if stuck_processing > 0:
        blocking_signals.append("reflection_stuck_processing_detected")
    if exhausted_failed > 0:
        blocking_signals.append("reflection_exhausted_failures_detected")

    return {
        "baseline_runtime_mode": REFLECTION_DEPLOYMENT_BASELINE_MODE,
        "selected_runtime_mode": selected_mode,
        "ready": len(blocking_signals) == 0,
        "blocking_signals": blocking_signals,
    }


def scheduler_cadence_rules() -> dict[str, dict[str, int | bool]]:
    return {key: dict(value) for key, value in SCHEDULER_CADENCE_RULES.items()}


def scheduler_cadence_dispatch_decision(
    *,
    execution_mode: str | None,
    cadence_kind: str | None,
    proactive_enabled: bool,
) -> tuple[bool, str]:
    selected_mode = normalize_scheduler_execution_mode(execution_mode)
    normalized_kind = normalize_scheduler_subsource(cadence_kind)
    if normalized_kind not in {SCHEDULER_MAINTENANCE_TICK, SCHEDULER_PROACTIVE_TICK}:
        return False, "unsupported_cadence_kind"
    if selected_mode == "externalized":
        return False, "externalized_owner_mode"
    if normalized_kind == SCHEDULER_PROACTIVE_TICK and not proactive_enabled:
        return False, "proactive_disabled"
    return True, "in_process_owner_mode"


def normalize_proactive_trigger(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in ALLOWED_PROACTIVE_TRIGGERS:
        return normalized
    return DEFAULT_PROACTIVE_TRIGGER


def clamp_scheduler_interval_seconds(*, subsource: str | None, interval_seconds: int) -> int:
    normalized_subsource = normalize_scheduler_subsource(subsource)
    rules = SCHEDULER_CADENCE_RULES[normalized_subsource]
    minimum = int(rules["min_interval_seconds"])
    maximum = int(rules["max_interval_seconds"])
    return max(minimum, min(maximum, int(interval_seconds)))


def _clamp_unit_float(value: object, *, default: float) -> float:
    try:
        return max(0.0, min(1.0, round(float(value), 2)))
    except (TypeError, ValueError):
        return max(0.0, min(1.0, round(default, 2)))


def _normalize_proactive_user_context(value: object) -> dict[str, object]:
    raw = value if isinstance(value, dict) else {}

    def as_bool(raw_value: object) -> bool:
        if isinstance(raw_value, bool):
            return raw_value
        if isinstance(raw_value, str):
            return raw_value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(raw_value)

    def as_int(raw_value: object, *, default: int = 0, minimum: int = 0) -> int:
        try:
            return max(minimum, int(raw_value))
        except (TypeError, ValueError):
            return max(minimum, int(default))

    activity = str(raw.get("recent_user_activity", "unknown") or "unknown").strip().lower()
    if activity not in {"active", "idle", "away", "unknown"}:
        activity = "unknown"
    return {
        "quiet_hours": as_bool(raw.get("quiet_hours", False)),
        "focus_mode": as_bool(raw.get("focus_mode", False)),
        "recent_user_activity": activity,
        "recent_outbound_count": as_int(raw.get("recent_outbound_count", 0)),
        "unanswered_proactive_count": as_int(raw.get("unanswered_proactive_count", 0)),
    }


def normalize_scheduler_payload(payload: dict[str, Any] | None, *, subsource: str | None) -> dict[str, Any]:
    raw_payload = payload if isinstance(payload, dict) else {}
    normalized_subsource = normalize_scheduler_subsource(subsource)
    rules = SCHEDULER_CADENCE_RULES[normalized_subsource]
    interval = int(raw_payload.get("cadence_interval_seconds", rules["min_interval_seconds"]) or rules["min_interval_seconds"])
    interval = clamp_scheduler_interval_seconds(subsource=normalized_subsource, interval_seconds=interval)
    text = " ".join(str(raw_payload.get("text", f"scheduler:{normalized_subsource}")).split())
    normalized_payload: dict[str, Any] = {
        "text": text,
        "cadence_kind": normalized_subsource,
        "cadence_interval_seconds": interval,
        "runtime_boundary": {
            "background_only": bool(rules["background_only"]),
            "user_visible_delivery": bool(rules["user_visible_delivery"]),
        },
    }
    raw_chat_id = raw_payload.get("chat_id")
    if isinstance(raw_chat_id, str):
        chat_id = raw_chat_id.strip()
        if chat_id:
            normalized_payload["chat_id"] = chat_id
    elif isinstance(raw_chat_id, int):
        normalized_payload["chat_id"] = raw_chat_id
    planned_work_due = raw_payload.get("planned_work_due")
    if isinstance(planned_work_due, Mapping):
        normalized_payload["planned_work_due"] = dict(planned_work_due)
    if normalized_subsource == SCHEDULER_PROACTIVE_TICK:
        proactive_trigger = normalize_proactive_trigger(
            str(raw_payload.get("proactive_trigger") or raw_payload.get("trigger") or "")
        )
        normalized_payload["proactive"] = {
            "trigger": proactive_trigger,
            "importance": _clamp_unit_float(raw_payload.get("importance"), default=0.55),
            "urgency": _clamp_unit_float(raw_payload.get("urgency"), default=0.5),
            "user_context": _normalize_proactive_user_context(raw_payload.get("user_context")),
        }
    return normalized_payload
