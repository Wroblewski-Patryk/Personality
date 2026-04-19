from app.core.events import (
    MAX_EVENT_TEXT_LENGTH,
    build_scheduler_event,
    coalesce_turn_text,
    looks_like_telegram_update,
    normalize_event,
)


def test_normalize_api_event() -> None:
    event = normalize_event({"text": "hello"})

    assert event.source == "api"
    assert event.subsource == "event_endpoint"
    assert event.payload["text"] == "hello"
    assert event.event_id
    assert event.meta.trace_id


def test_normalize_api_event_ignores_internal_source_fields_from_client_payload() -> None:
    event = normalize_event(
        {
            "text": "hello from client",
            "source": "telegram",
            "subsource": "user_message",
            "event_id": "evt-client",
            "meta": {"user_id": "u-1", "trace_id": "trace-client"},
        }
    )

    assert event.source == "api"
    assert event.subsource == "event_endpoint"
    assert event.payload == {"text": "hello from client"}
    assert event.meta.user_id == "u-1"
    assert event.meta.trace_id == "trace-client"


def test_normalize_api_event_uses_payload_text_when_top_level_text_is_missing() -> None:
    event = normalize_event({"payload": {"text": "payload text", "extra": "ignored"}})

    assert event.source == "api"
    assert event.payload == {"text": "payload text"}


def test_normalize_api_event_normalizes_text_and_limits_length() -> None:
    raw_text = "   hello   world \n" + ("x" * (MAX_EVENT_TEXT_LENGTH + 30))
    event = normalize_event({"text": raw_text})

    assert event.payload["text"].startswith("hello world")
    assert len(event.payload["text"]) == MAX_EVENT_TEXT_LENGTH


def test_normalize_api_event_normalizes_meta_field_lengths() -> None:
    event = normalize_event(
        {
            "text": "hello",
            "meta": {
                "user_id": "u" * 80,
                "trace_id": "t" * 90,
            },
        }
    )

    assert len(event.meta.user_id) == 64
    assert len(event.meta.trace_id) == 64


def test_coalesce_turn_text_normalizes_and_skips_empty_parts() -> None:
    merged = coalesce_turn_text(["  hello   there  ", "\n", "  second   line  "])

    assert merged == "hello there\nsecond line"


def test_coalesce_turn_text_applies_max_length_limit() -> None:
    merged = coalesce_turn_text(["x" * MAX_EVENT_TEXT_LENGTH, "y" * 25])

    assert len(merged) == MAX_EVENT_TEXT_LENGTH
    assert merged == "x" * MAX_EVENT_TEXT_LENGTH


def test_normalize_api_event_uses_default_user_id_when_meta_user_id_is_missing() -> None:
    event = normalize_event(
        {"text": "hello"},
        default_user_id="api-user-7",
    )

    assert event.meta.user_id == "api-user-7"


def test_normalize_api_event_prefers_meta_user_id_over_default_user_id() -> None:
    event = normalize_event(
        {
            "text": "hello",
            "meta": {"user_id": "meta-user"},
        },
        default_user_id="header-user",
    )

    assert event.meta.user_id == "meta-user"


def test_normalize_telegram_event() -> None:
    raw = {
        "update_id": 1,
        "message": {
            "text": "ping",
            "chat": {"id": 123},
            "from": {"id": 999},
        },
    }
    event = normalize_event(raw)

    assert event.source == "telegram"
    assert event.subsource == "user_message"
    assert event.payload["chat_id"] == 123
    assert event.payload["text"] == "ping"
    assert event.meta.user_id == "999"


def test_looks_like_telegram_update_requires_message_shape() -> None:
    assert looks_like_telegram_update({"update_id": 1, "message": {"text": "ping"}}) is True
    assert looks_like_telegram_update({"text": "hello"}) is False


def test_build_scheduler_event_normalizes_source_cadence_and_runtime_boundary() -> None:
    event = build_scheduler_event(
        subsource="maintenance_tick",
        payload={
            "text": "  maintenance   pass  ",
            "cadence_interval_seconds": 120,
        },
    )

    assert event.source == "scheduler"
    assert event.subsource == "maintenance_tick"
    assert event.meta.user_id == "scheduler"
    assert event.payload["text"] == "maintenance pass"
    assert event.payload["cadence_kind"] == "maintenance_tick"
    assert event.payload["cadence_interval_seconds"] == 900
    assert event.payload["runtime_boundary"] == {
        "background_only": True,
        "user_visible_delivery": False,
    }


def test_build_scheduler_event_normalizes_proactive_payload_contract() -> None:
    event = build_scheduler_event(
        subsource="proactive_tick",
        payload={
            "text": "check progress",
            "chat_id": 123456,
            "proactive_trigger": "goal_stagnation",
            "importance": 0.81,
            "urgency": 0.67,
            "user_context": {
                "quiet_hours": True,
                "focus_mode": True,
                "recent_user_activity": "idle",
                "recent_outbound_count": 3,
                "unanswered_proactive_count": 2,
            },
        },
    )

    assert event.source == "scheduler"
    assert event.subsource == "proactive_tick"
    assert event.payload["chat_id"] == 123456
    assert event.payload["proactive"] == {
        "trigger": "goal_stagnation",
        "importance": 0.81,
        "urgency": 0.67,
        "user_context": {
            "quiet_hours": True,
            "focus_mode": True,
            "recent_user_activity": "idle",
            "recent_outbound_count": 3,
            "unanswered_proactive_count": 2,
        },
    }
