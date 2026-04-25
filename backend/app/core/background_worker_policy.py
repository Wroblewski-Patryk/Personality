from __future__ import annotations

from app.core.scheduler_contracts import (
    normalize_reflection_runtime_mode,
    normalize_scheduler_execution_mode,
)


REFLECTION_EXTERNAL_DRIVER_POLICY_OWNER = "deferred_reflection_external_worker"
REFLECTION_EXTERNAL_DRIVER_ENTRYPOINT = "scripts/run_reflection_queue_once.py"
REFLECTION_EXTERNAL_DRIVER_WRAPPERS = (
    "scripts/run_reflection_queue_once.ps1",
    "scripts/run_reflection_queue_once.sh",
)


def reflection_external_driver_policy_snapshot(
    *,
    reflection_runtime_mode: str | None,
    worker_running: bool,
    scheduler_execution_mode: str | None,
) -> dict[str, object]:
    selected_runtime_mode = normalize_reflection_runtime_mode(reflection_runtime_mode)
    selected_scheduler_execution_mode = normalize_scheduler_execution_mode(
        scheduler_execution_mode
    )

    if selected_runtime_mode != "deferred":
        production_baseline_ready = False
        production_baseline_state = "in_process_compatibility_mode"
        production_baseline_hint = (
            "switch_reflection_runtime_mode_to_deferred_for_external_driver_baseline"
        )
    elif worker_running:
        production_baseline_ready = False
        production_baseline_state = "deferred_local_worker_conflict"
        production_baseline_hint = (
            "stop_app_local_reflection_worker_when_external_driver_owns_queue_drain"
        )
    elif selected_scheduler_execution_mode == "externalized":
        production_baseline_ready = True
        production_baseline_state = "external_driver_baseline_aligned"
        production_baseline_hint = "external_driver_baseline_active"
    else:
        production_baseline_ready = True
        production_baseline_state = "external_driver_ready_scheduler_transitional"
        production_baseline_hint = (
            "external_driver_can_drain_queue_scheduler_owner_remains_transitional"
        )

    return {
        "policy_owner": REFLECTION_EXTERNAL_DRIVER_POLICY_OWNER,
        "baseline_runtime_mode": "deferred",
        "selected_runtime_mode": selected_runtime_mode,
        "selected_scheduler_execution_mode": selected_scheduler_execution_mode,
        "queue_drain_owner_target": "external_driver",
        "entrypoint_kind": "python_script",
        "entrypoint_path": REFLECTION_EXTERNAL_DRIVER_ENTRYPOINT,
        "wrapper_paths": list(REFLECTION_EXTERNAL_DRIVER_WRAPPERS),
        "app_worker_running": bool(worker_running),
        "production_baseline_ready": production_baseline_ready,
        "production_baseline_state": production_baseline_state,
        "production_baseline_hint": production_baseline_hint,
    }
