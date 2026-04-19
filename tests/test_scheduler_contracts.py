from app.core.scheduler_contracts import (
    clamp_scheduler_interval_seconds,
    normalize_scheduler_payload,
    normalize_scheduler_subsource,
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
