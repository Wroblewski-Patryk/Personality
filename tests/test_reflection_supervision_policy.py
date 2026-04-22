from app.core.reflection_supervision_policy import (
    reflection_supervision_policy_snapshot,
)


def test_reflection_supervision_policy_marks_aligned_deferred_external_baseline_ready() -> None:
    snapshot = reflection_supervision_policy_snapshot(
        reflection_runtime_mode="deferred",
        scheduler_execution_mode="externalized",
        worker_running=False,
        task_stats={
            "pending": 0,
            "processing": 0,
            "retryable_failed": 0,
            "stuck_processing": 0,
            "exhausted_failed": 0,
        },
    )

    assert snapshot == {
        "policy_owner": "deferred_reflection_supervision_policy",
        "target_runtime_mode": "deferred",
        "target_queue_drain_owner": "external_driver",
        "target_scheduler_execution_mode": "externalized",
        "retry_owner": "durable_queue",
        "recovery_entrypoint_path": "scripts/run_reflection_queue_once.py",
        "selected_runtime_mode": "deferred",
        "selected_scheduler_execution_mode": "externalized",
        "app_worker_running": False,
        "queue_health_state": "steady_state_clear",
        "pending_count": 0,
        "processing_count": 0,
        "retryable_failed_count": 0,
        "stuck_processing_count": 0,
        "exhausted_failed_count": 0,
        "blocking_signals": [],
        "recovery_actions": [],
        "production_supervision_ready": True,
        "production_supervision_state": "deferred_supervision_aligned",
        "production_supervision_hint": "external_supervision_ready",
    }


def test_reflection_supervision_policy_marks_recovery_required_when_worker_or_failures_conflict() -> None:
    snapshot = reflection_supervision_policy_snapshot(
        reflection_runtime_mode="deferred",
        scheduler_execution_mode="in_process",
        worker_running=True,
        task_stats={
            "pending": 2,
            "processing": 1,
            "retryable_failed": 1,
            "stuck_processing": 1,
            "exhausted_failed": 2,
        },
    )

    assert snapshot["queue_health_state"] == "recovery_required"
    assert snapshot["production_supervision_ready"] is False
    assert snapshot["production_supervision_state"] == "supervision_gaps_present"
    assert "app_local_worker_still_running" in snapshot["blocking_signals"]
    assert "external_scheduler_owner_not_selected" in snapshot["blocking_signals"]
    assert "stuck_processing_present" in snapshot["blocking_signals"]
    assert "exhausted_failures_present" in snapshot["blocking_signals"]
    assert "stop_app_local_reflection_worker" in snapshot["recovery_actions"]
    assert "externalize_reflection_queue_drain_owner" in snapshot["recovery_actions"]
    assert "drain_or_requeue_stuck_processing_tasks" in snapshot["recovery_actions"]
    assert "inspect_and_recover_exhausted_failed_tasks" in snapshot["recovery_actions"]


def test_reflection_supervision_policy_keeps_active_backlog_ready_when_baseline_is_aligned() -> None:
    snapshot = reflection_supervision_policy_snapshot(
        reflection_runtime_mode="deferred",
        scheduler_execution_mode="externalized",
        worker_running=False,
        task_stats={
            "pending": 3,
            "processing": 1,
            "retryable_failed": 1,
            "stuck_processing": 0,
            "exhausted_failed": 0,
        },
    )

    assert snapshot["queue_health_state"] == "active_backlog_under_supervision"
    assert snapshot["blocking_signals"] == []
    assert snapshot["production_supervision_ready"] is True
    assert snapshot["production_supervision_state"] == "deferred_supervision_active_backlog"
    assert (
        snapshot["production_supervision_hint"]
        == "external_supervision_active_with_recoverable_backlog"
    )
