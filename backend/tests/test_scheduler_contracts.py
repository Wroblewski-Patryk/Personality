from app.core.scheduler_contracts import (
    clamp_scheduler_interval_seconds,
    normalize_scheduler_execution_mode,
    normalize_scheduler_payload,
    normalize_reflection_runtime_mode,
    normalize_scheduler_subsource,
    reflection_deployment_readiness_snapshot,
    reflection_enqueue_dispatch_decision,
    reflection_topology_handoff_posture,
    reflection_scheduler_dispatch_decision,
    scheduler_cadence_dispatch_decision,
    scheduler_cadence_execution_snapshot,
    scheduler_cadence_rules,
)


def test_scheduler_contracts_normalize_unknown_subsource_to_reflection_tick() -> None:
    assert normalize_scheduler_subsource("unknown_tick") == "reflection_tick"


def test_scheduler_contracts_clamp_cadence_interval_to_rules() -> None:
    payload = normalize_scheduler_payload(
        {"text": "proactive check", "cadence_interval_seconds": 5},
        subsource="proactive_tick",
    )

    assert payload["cadence_kind"] == "proactive_tick"
    assert payload["cadence_interval_seconds"] == 1800
    assert payload["runtime_boundary"] == {
        "background_only": False,
        "user_visible_delivery": True,
    }


def test_scheduler_contracts_expose_rule_snapshot_for_runtime_boundaries() -> None:
    rules = scheduler_cadence_rules()

    assert rules["reflection_tick"]["background_only"] is True
    assert rules["maintenance_tick"]["min_interval_seconds"] == 900
    assert rules["proactive_tick"]["user_visible_delivery"] is True


def test_scheduler_contracts_clamp_interval_helper_respects_rule_boundaries() -> None:
    assert clamp_scheduler_interval_seconds(subsource="reflection_tick", interval_seconds=5) == 300
    assert clamp_scheduler_interval_seconds(subsource="maintenance_tick", interval_seconds=500_000) == 172800


def test_scheduler_contracts_normalize_proactive_payload_with_trigger_and_user_context() -> None:
    payload = normalize_scheduler_payload(
        {
            "text": " proactive check ",
            "proactive_trigger": "task_blocked",
            "importance": 0.91,
            "urgency": 0.86,
            "user_context": {
                "quiet_hours": False,
                "focus_mode": True,
                "recent_user_activity": "active",
                "recent_outbound_count": 2,
                "unanswered_proactive_count": 1,
            },
        },
        subsource="proactive_tick",
    )

    assert payload["cadence_kind"] == "proactive_tick"
    assert payload["text"] == "proactive check"
    assert payload["proactive"] == {
        "trigger": "task_blocked",
        "importance": 0.91,
        "urgency": 0.86,
        "user_context": {
            "quiet_hours": False,
            "focus_mode": True,
            "recent_user_activity": "active",
            "recent_outbound_count": 2,
            "unanswered_proactive_count": 1,
        },
    }


def test_scheduler_contracts_preserve_chat_id_for_delivery_targeting() -> None:
    payload = normalize_scheduler_payload(
        {
            "text": "proactive delivery",
            "chat_id": 123456,
        },
        subsource="proactive_tick",
    )

    assert payload["chat_id"] == 123456


def test_scheduler_contracts_normalize_reflection_runtime_mode_with_safe_default() -> None:
    assert normalize_reflection_runtime_mode("deferred") == "deferred"
    assert normalize_reflection_runtime_mode("IN_PROCESS") == "in_process"
    assert normalize_reflection_runtime_mode("legacy_mode") == "in_process"


def test_scheduler_contracts_normalize_scheduler_execution_mode_with_safe_default() -> None:
    assert normalize_scheduler_execution_mode("externalized") == "externalized"
    assert normalize_scheduler_execution_mode("IN_PROCESS") == "in_process"
    assert normalize_scheduler_execution_mode("legacy_mode") == "in_process"


def test_scheduler_contracts_expose_scheduler_cadence_execution_snapshot_for_in_process_mode() -> None:
    snapshot = scheduler_cadence_execution_snapshot(
        execution_mode="in_process",
        scheduler_enabled=True,
        scheduler_running=True,
        proactive_enabled=False,
    )

    assert snapshot == {
        "baseline_execution_mode": "in_process",
        "selected_execution_mode": "in_process",
        "ready": True,
        "blocking_signals": [],
        "maintenance_cadence_owner": "in_process_scheduler",
        "proactive_cadence_owner": "in_process_scheduler",
        "maintenance_tick_dispatch": True,
        "maintenance_tick_reason": "in_process_owner_mode",
        "proactive_tick_dispatch": False,
        "proactive_tick_reason": "proactive_disabled",
        "scheduler_enabled": True,
        "scheduler_running": True,
        "proactive_enabled": False,
    }


def test_scheduler_contracts_scheduler_cadence_execution_snapshot_marks_externalized_running_mismatch() -> None:
    snapshot = scheduler_cadence_execution_snapshot(
        execution_mode="externalized",
        scheduler_enabled=False,
        scheduler_running=True,
        proactive_enabled=True,
    )

    assert snapshot["selected_execution_mode"] == "externalized"
    assert snapshot["ready"] is False
    assert snapshot["maintenance_cadence_owner"] == "external_scheduler"
    assert snapshot["proactive_cadence_owner"] == "external_scheduler"
    assert snapshot["maintenance_tick_dispatch"] is False
    assert snapshot["maintenance_tick_reason"] == "externalized_owner_mode"
    assert snapshot["proactive_tick_dispatch"] is False
    assert snapshot["proactive_tick_reason"] == "externalized_owner_mode"
    assert "externalized_scheduler_worker_running" in snapshot["blocking_signals"]


def test_scheduler_contracts_scheduler_cadence_dispatch_decision_respects_owner_mode_and_proactive_gate() -> None:
    dispatch, reason = scheduler_cadence_dispatch_decision(
        execution_mode="in_process",
        cadence_kind="maintenance_tick",
        proactive_enabled=False,
    )
    assert dispatch is True
    assert reason == "in_process_owner_mode"

    dispatch, reason = scheduler_cadence_dispatch_decision(
        execution_mode="in_process",
        cadence_kind="proactive_tick",
        proactive_enabled=False,
    )
    assert dispatch is False
    assert reason == "proactive_disabled"

    dispatch, reason = scheduler_cadence_dispatch_decision(
        execution_mode="externalized",
        cadence_kind="maintenance_tick",
        proactive_enabled=True,
    )
    assert dispatch is False
    assert reason == "externalized_owner_mode"


def test_scheduler_contracts_expose_shared_reflection_dispatch_boundary_rules() -> None:
    enqueue_dispatch, enqueue_reason = reflection_enqueue_dispatch_decision(
        runtime_mode="deferred",
        worker_running=True,
    )
    assert enqueue_dispatch is False
    assert enqueue_reason == "deferred_runtime"

    scheduler_dispatch, scheduler_reason = reflection_scheduler_dispatch_decision(
        runtime_mode="deferred",
        worker_running=False,
    )
    assert scheduler_dispatch is True
    assert scheduler_reason == "deferred_runtime"

    enqueue_dispatch, enqueue_reason = reflection_enqueue_dispatch_decision(
        runtime_mode="in_process",
        worker_running=True,
    )
    assert enqueue_dispatch is True
    assert enqueue_reason == "in_process_worker_running"

    scheduler_dispatch, scheduler_reason = reflection_scheduler_dispatch_decision(
        runtime_mode="in_process",
        worker_running=True,
    )
    assert scheduler_dispatch is False
    assert scheduler_reason == "in_process_worker_running"


def test_scheduler_contracts_expose_reflection_handoff_posture_for_external_driver_mode() -> None:
    posture = reflection_topology_handoff_posture(
        runtime_mode="deferred",
        worker_running=False,
    )

    assert posture == {
        "runtime_mode": "deferred",
        "enqueue_owner": "runtime_followup",
        "queue_backend": "durable_postgres_queue",
        "queue_drain_owner": "external_driver",
        "retry_owner": "durable_queue",
        "external_driver_expected": True,
        "worker_running": False,
        "runtime_enqueue_dispatch": False,
        "runtime_enqueue_reason": "deferred_runtime",
        "scheduler_tick_dispatch": True,
        "scheduler_tick_reason": "deferred_runtime",
    }


def test_scheduler_contracts_reflection_deployment_readiness_is_ready_for_healthy_in_process_mode() -> None:
    topology = reflection_topology_handoff_posture(
        runtime_mode="in_process",
        worker_running=True,
    )

    readiness = reflection_deployment_readiness_snapshot(
        runtime_mode="in_process",
        topology=topology,
        worker_running=True,
        task_stats={"stuck_processing": 0, "exhausted_failed": 0},
    )

    assert readiness == {
        "baseline_runtime_mode": "in_process",
        "selected_runtime_mode": "in_process",
        "ready": True,
        "blocking_signals": [],
    }


def test_scheduler_contracts_reflection_deployment_readiness_marks_deferred_mode_mismatch_when_worker_runs_locally() -> None:
    topology = reflection_topology_handoff_posture(
        runtime_mode="deferred",
        worker_running=True,
    )

    readiness = reflection_deployment_readiness_snapshot(
        runtime_mode="deferred",
        topology=topology,
        worker_running=True,
        task_stats={"stuck_processing": 0, "exhausted_failed": 0},
    )

    assert readiness["baseline_runtime_mode"] == "in_process"
    assert readiness["selected_runtime_mode"] == "deferred"
    assert readiness["ready"] is False
    assert "deferred_in_process_worker_running" in readiness["blocking_signals"]


def test_scheduler_contracts_reflection_deployment_readiness_marks_task_health_blockers() -> None:
    topology = reflection_topology_handoff_posture(
        runtime_mode="in_process",
        worker_running=True,
    )

    readiness = reflection_deployment_readiness_snapshot(
        runtime_mode="in_process",
        topology=topology,
        worker_running=True,
        task_stats={"stuck_processing": 2, "exhausted_failed": 1},
    )

    assert readiness["ready"] is False
    assert "reflection_stuck_processing_detected" in readiness["blocking_signals"]
    assert "reflection_exhausted_failures_detected" in readiness["blocking_signals"]
