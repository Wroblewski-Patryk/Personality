from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.core.scheduler_contracts import (
    normalize_reflection_runtime_mode,
    normalize_scheduler_execution_mode,
)


REFLECTION_SUPERVISION_POLICY_OWNER = "deferred_reflection_supervision_policy"
REFLECTION_SUPERVISION_RECOVERY_ENTRYPOINT = "scripts/run_reflection_queue_once.py"


def _safe_non_negative_int(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def reflection_supervision_policy_snapshot(
    *,
    reflection_runtime_mode: str | None,
    scheduler_execution_mode: str | None,
    worker_running: bool,
    task_stats: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    selected_runtime_mode = normalize_reflection_runtime_mode(reflection_runtime_mode)
    selected_scheduler_execution_mode = normalize_scheduler_execution_mode(
        scheduler_execution_mode
    )
    stats = dict(task_stats or {})
    pending = _safe_non_negative_int(stats.get("pending"))
    processing = _safe_non_negative_int(stats.get("processing"))
    retryable_failed = _safe_non_negative_int(stats.get("retryable_failed"))
    exhausted_failed = _safe_non_negative_int(stats.get("exhausted_failed"))
    stuck_processing = _safe_non_negative_int(stats.get("stuck_processing"))

    recovery_actions: list[str] = []
    blocking_signals: list[str] = []

    if selected_runtime_mode != "deferred":
        blocking_signals.append("deferred_runtime_mode_not_selected")
        recovery_actions.append("switch_reflection_runtime_mode_to_deferred")
    if worker_running:
        blocking_signals.append("app_local_worker_still_running")
        recovery_actions.append("stop_app_local_reflection_worker")
    if selected_scheduler_execution_mode != "externalized":
        blocking_signals.append("external_scheduler_owner_not_selected")
        recovery_actions.append("externalize_reflection_queue_drain_owner")
    if stuck_processing > 0:
        blocking_signals.append("stuck_processing_present")
        recovery_actions.append("drain_or_requeue_stuck_processing_tasks")
    if exhausted_failed > 0:
        blocking_signals.append("exhausted_failures_present")
        recovery_actions.append("inspect_and_recover_exhausted_failed_tasks")

    if stuck_processing > 0 or exhausted_failed > 0:
        queue_health_state = "recovery_required"
    elif retryable_failed > 0 or pending > 0 or processing > 0:
        queue_health_state = "active_backlog_under_supervision"
    else:
        queue_health_state = "steady_state_clear"

    if blocking_signals:
        production_supervision_ready = False
        production_supervision_state = "supervision_gaps_present"
        production_supervision_hint = "resolve_blocking_signals_before_production_deferred_supervision"
    elif queue_health_state == "active_backlog_under_supervision":
        production_supervision_ready = True
        production_supervision_state = "deferred_supervision_active_backlog"
        production_supervision_hint = "external_supervision_active_with_recoverable_backlog"
    else:
        production_supervision_ready = True
        production_supervision_state = "deferred_supervision_aligned"
        production_supervision_hint = "external_supervision_ready"

    return {
        "policy_owner": REFLECTION_SUPERVISION_POLICY_OWNER,
        "target_runtime_mode": "deferred",
        "target_queue_drain_owner": "external_driver",
        "target_scheduler_execution_mode": "externalized",
        "retry_owner": "durable_queue",
        "recovery_entrypoint_path": REFLECTION_SUPERVISION_RECOVERY_ENTRYPOINT,
        "selected_runtime_mode": selected_runtime_mode,
        "selected_scheduler_execution_mode": selected_scheduler_execution_mode,
        "app_worker_running": bool(worker_running),
        "queue_health_state": queue_health_state,
        "pending_count": pending,
        "processing_count": processing,
        "retryable_failed_count": retryable_failed,
        "stuck_processing_count": stuck_processing,
        "exhausted_failed_count": exhausted_failed,
        "blocking_signals": blocking_signals,
        "recovery_actions": recovery_actions,
        "production_supervision_ready": production_supervision_ready,
        "production_supervision_state": production_supervision_state,
        "production_supervision_hint": production_supervision_hint,
    }
