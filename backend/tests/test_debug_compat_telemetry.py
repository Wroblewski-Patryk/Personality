from datetime import datetime, timezone

from app.core.debug_compat import (
    DebugQueryCompatTelemetry,
    debug_query_compat_activity_snapshot,
    debug_query_compat_freshness_snapshot,
    debug_query_compat_recent_snapshot,
    debug_query_compat_sunset_snapshot,
)


def test_debug_query_compat_telemetry_defaults_to_empty_snapshot() -> None:
    telemetry = DebugQueryCompatTelemetry()

    snapshot = telemetry.snapshot()

    assert snapshot == {
        "attempts_total": 0,
        "allowed_total": 0,
        "blocked_total": 0,
        "last_attempt_at": None,
        "last_allowed_at": None,
        "last_blocked_at": None,
        "recent_window_size": 20,
        "recent_attempts_total": 0,
        "recent_allowed_total": 0,
        "recent_blocked_total": 0,
    }


def test_debug_query_compat_telemetry_tracks_allowed_and_blocked_attempts() -> None:
    telemetry = DebugQueryCompatTelemetry()

    telemetry.record_allowed()
    telemetry.record_blocked()

    snapshot = telemetry.snapshot()

    assert snapshot["attempts_total"] == 2
    assert snapshot["allowed_total"] == 1
    assert snapshot["blocked_total"] == 1
    assert snapshot["last_attempt_at"] is not None
    assert snapshot["last_allowed_at"] is not None
    assert snapshot["last_blocked_at"] is not None
    assert snapshot["recent_window_size"] == 20
    assert snapshot["recent_attempts_total"] == 2
    assert snapshot["recent_allowed_total"] == 1
    assert snapshot["recent_blocked_total"] == 1


def test_debug_query_compat_telemetry_uses_configured_recent_window_size() -> None:
    telemetry = DebugQueryCompatTelemetry(recent_window_size=3)

    telemetry.record_allowed()
    telemetry.record_blocked()
    telemetry.record_allowed()
    telemetry.record_allowed()

    snapshot = telemetry.snapshot()

    assert snapshot["attempts_total"] == 4
    assert snapshot["recent_window_size"] == 3
    assert snapshot["recent_attempts_total"] == 3
    assert snapshot["recent_allowed_total"] == 2
    assert snapshot["recent_blocked_total"] == 1


def test_debug_query_compat_telemetry_rejects_non_positive_recent_window_size() -> None:
    try:
        DebugQueryCompatTelemetry(recent_window_size=0)
    except ValueError as exc:
        assert "EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError(
            "Expected DebugQueryCompatTelemetry to reject too-low recent window size."
        )


def test_debug_query_compat_sunset_snapshot_defaults_to_zero_rates() -> None:
    snapshot = debug_query_compat_sunset_snapshot(
        compat_enabled=True,
        telemetry_snapshot={
            "attempts_total": 0,
            "allowed_total": 0,
            "blocked_total": 0,
        },
    )

    assert snapshot == {
        "event_debug_query_compat_allow_rate": 0.0,
        "event_debug_query_compat_block_rate": 0.0,
        "event_debug_query_compat_recommendation": "no_compat_traffic_detected_disable_when_possible",
        "event_debug_query_compat_sunset_ready": True,
        "event_debug_query_compat_sunset_reason": "no_compat_attempts_detected",
    }


def test_debug_query_compat_sunset_snapshot_marks_migration_when_traffic_exists() -> None:
    snapshot = debug_query_compat_sunset_snapshot(
        compat_enabled=True,
        telemetry_snapshot={
            "attempts_total": 4,
            "allowed_total": 3,
            "blocked_total": 1,
        },
    )

    assert snapshot == {
        "event_debug_query_compat_allow_rate": 0.75,
        "event_debug_query_compat_block_rate": 0.25,
        "event_debug_query_compat_recommendation": "migrate_clients_before_disabling_compat",
        "event_debug_query_compat_sunset_ready": False,
        "event_debug_query_compat_sunset_reason": "compat_attempts_detected_migration_needed",
    }


def test_debug_query_compat_sunset_snapshot_marks_migration_when_only_blocked_attempts_exist() -> None:
    snapshot = debug_query_compat_sunset_snapshot(
        compat_enabled=True,
        telemetry_snapshot={
            "attempts_total": 2,
            "allowed_total": 0,
            "blocked_total": 2,
        },
    )

    assert snapshot == {
        "event_debug_query_compat_allow_rate": 0.0,
        "event_debug_query_compat_block_rate": 1.0,
        "event_debug_query_compat_recommendation": "migrate_clients_before_disabling_compat",
        "event_debug_query_compat_sunset_ready": False,
        "event_debug_query_compat_sunset_reason": "compat_attempts_detected_migration_needed",
    }


def test_debug_query_compat_sunset_snapshot_marks_disabled_state_when_compat_is_off() -> None:
    snapshot = debug_query_compat_sunset_snapshot(
        compat_enabled=False,
        telemetry_snapshot={
            "attempts_total": 2,
            "allowed_total": 0,
            "blocked_total": 2,
        },
    )

    assert snapshot == {
        "event_debug_query_compat_allow_rate": 0.0,
        "event_debug_query_compat_block_rate": 1.0,
        "event_debug_query_compat_recommendation": "compat_disabled",
        "event_debug_query_compat_sunset_ready": True,
        "event_debug_query_compat_sunset_reason": "compat_disabled",
    }


def test_debug_query_compat_recent_snapshot_defaults_when_no_attempts_exist() -> None:
    snapshot = debug_query_compat_recent_snapshot(
        compat_enabled=True,
        telemetry_snapshot={
            "recent_attempts_total": 0,
            "recent_allowed_total": 0,
            "recent_blocked_total": 0,
        },
    )

    assert snapshot == {
        "event_debug_query_compat_recent_attempts_total": 0,
        "event_debug_query_compat_recent_allow_rate": 0.0,
        "event_debug_query_compat_recent_block_rate": 0.0,
        "event_debug_query_compat_recent_state": "no_recent_attempts",
    }


def test_debug_query_compat_recent_snapshot_marks_mixed_state_for_balanced_outcomes() -> None:
    snapshot = debug_query_compat_recent_snapshot(
        compat_enabled=True,
        telemetry_snapshot={
            "recent_attempts_total": 4,
            "recent_allowed_total": 2,
            "recent_blocked_total": 2,
        },
    )

    assert snapshot == {
        "event_debug_query_compat_recent_attempts_total": 4,
        "event_debug_query_compat_recent_allow_rate": 0.5,
        "event_debug_query_compat_recent_block_rate": 0.5,
        "event_debug_query_compat_recent_state": "mixed",
    }


def test_debug_query_compat_recent_snapshot_marks_disabled_state_when_compat_is_off() -> None:
    snapshot = debug_query_compat_recent_snapshot(
        compat_enabled=False,
        telemetry_snapshot={
            "recent_attempts_total": 3,
            "recent_allowed_total": 0,
            "recent_blocked_total": 3,
        },
    )

    assert snapshot == {
        "event_debug_query_compat_recent_attempts_total": 3,
        "event_debug_query_compat_recent_allow_rate": 0.0,
        "event_debug_query_compat_recent_block_rate": 1.0,
        "event_debug_query_compat_recent_state": "compat_disabled",
    }


def test_debug_query_compat_freshness_snapshot_defaults_when_no_attempts_exist() -> None:
    snapshot = debug_query_compat_freshness_snapshot(
        telemetry_snapshot={"last_attempt_at": None},
        stale_after_seconds=600,
        now_utc=datetime(2026, 4, 19, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert snapshot == {
        "event_debug_query_compat_stale_after_seconds": 600,
        "event_debug_query_compat_last_attempt_age_seconds": None,
        "event_debug_query_compat_last_attempt_state": "no_attempts_recorded",
    }


def test_debug_query_compat_freshness_snapshot_marks_fresh_state_when_last_attempt_is_recent() -> None:
    snapshot = debug_query_compat_freshness_snapshot(
        telemetry_snapshot={"last_attempt_at": "2026-04-19T09:55:00Z"},
        stale_after_seconds=600,
        now_utc=datetime(2026, 4, 19, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert snapshot == {
        "event_debug_query_compat_stale_after_seconds": 600,
        "event_debug_query_compat_last_attempt_age_seconds": 300,
        "event_debug_query_compat_last_attempt_state": "fresh",
    }


def test_debug_query_compat_freshness_snapshot_marks_stale_state_when_last_attempt_age_crosses_threshold() -> None:
    snapshot = debug_query_compat_freshness_snapshot(
        telemetry_snapshot={"last_attempt_at": "2026-04-19T09:49:59Z"},
        stale_after_seconds=600,
        now_utc=datetime(2026, 4, 19, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert snapshot == {
        "event_debug_query_compat_stale_after_seconds": 600,
        "event_debug_query_compat_last_attempt_age_seconds": 601,
        "event_debug_query_compat_last_attempt_state": "stale",
    }


def test_debug_query_compat_freshness_snapshot_rejects_non_positive_stale_threshold() -> None:
    try:
        debug_query_compat_freshness_snapshot(
            telemetry_snapshot={"last_attempt_at": "2026-04-19T09:55:00Z"},
            stale_after_seconds=0,
        )
    except ValueError as exc:
        assert "EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError(
            "Expected debug_query_compat_freshness_snapshot to reject too-low stale threshold."
        )


def test_debug_query_compat_activity_snapshot_marks_compat_disabled_state_when_route_is_off() -> None:
    snapshot = debug_query_compat_activity_snapshot(
        compat_enabled=False,
        telemetry_snapshot={"attempts_total": 5, "last_attempt_at": "2026-04-19T09:55:00Z"},
        stale_after_seconds=600,
        now_utc=datetime(2026, 4, 19, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert snapshot == {
        "event_debug_query_compat_activity_state": "compat_disabled",
        "event_debug_query_compat_activity_hint": "compat_disabled_no_action",
    }


def test_debug_query_compat_activity_snapshot_marks_no_attempts_state() -> None:
    snapshot = debug_query_compat_activity_snapshot(
        compat_enabled=True,
        telemetry_snapshot={"attempts_total": 0, "last_attempt_at": None},
        stale_after_seconds=600,
        now_utc=datetime(2026, 4, 19, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert snapshot == {
        "event_debug_query_compat_activity_state": "no_attempts_observed",
        "event_debug_query_compat_activity_hint": "can_disable_when_ready",
    }


def test_debug_query_compat_activity_snapshot_marks_stale_historical_state_when_last_attempt_is_stale() -> None:
    snapshot = debug_query_compat_activity_snapshot(
        compat_enabled=True,
        telemetry_snapshot={"attempts_total": 3, "last_attempt_at": "2026-04-19T09:49:59Z"},
        stale_after_seconds=600,
        now_utc=datetime(2026, 4, 19, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert snapshot == {
        "event_debug_query_compat_activity_state": "stale_historical_attempts",
        "event_debug_query_compat_activity_hint": "verify_stale_clients_before_disable",
    }


def test_debug_query_compat_activity_snapshot_marks_recent_attempts_state_when_last_attempt_is_fresh() -> None:
    snapshot = debug_query_compat_activity_snapshot(
        compat_enabled=True,
        telemetry_snapshot={"attempts_total": 3, "last_attempt_at": "2026-04-19T09:55:00Z"},
        stale_after_seconds=600,
        now_utc=datetime(2026, 4, 19, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert snapshot == {
        "event_debug_query_compat_activity_state": "recent_attempts_observed",
        "event_debug_query_compat_activity_hint": "keep_compat_until_recent_clients_migrate",
    }
