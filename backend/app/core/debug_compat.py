from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Literal, Mapping


class DebugQueryCompatTelemetry:
    """Tracks `POST /event?debug=true` compatibility-route usage in-process."""

    def __init__(self, *, recent_window_size: int = 20) -> None:
        if recent_window_size < 1:
            raise ValueError("EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW must be at least 1.")
        self._lock = Lock()
        self._attempts_total = 0
        self._allowed_total = 0
        self._blocked_total = 0
        self._last_attempt_at: datetime | None = None
        self._last_allowed_at: datetime | None = None
        self._last_blocked_at: datetime | None = None
        self._recent_outcomes: deque[bool] = deque(maxlen=recent_window_size)

    def record_allowed(self) -> None:
        now = datetime.now(timezone.utc)
        with self._lock:
            self._attempts_total += 1
            self._allowed_total += 1
            self._last_attempt_at = now
            self._last_allowed_at = now
            self._recent_outcomes.append(True)

    def record_blocked(self) -> None:
        now = datetime.now(timezone.utc)
        with self._lock:
            self._attempts_total += 1
            self._blocked_total += 1
            self._last_attempt_at = now
            self._last_blocked_at = now
            self._recent_outcomes.append(False)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            recent_attempts = len(self._recent_outcomes)
            recent_allowed_total = sum(1 for value in self._recent_outcomes if value)
            recent_blocked_total = recent_attempts - recent_allowed_total
            return {
                "attempts_total": self._attempts_total,
                "allowed_total": self._allowed_total,
                "blocked_total": self._blocked_total,
                "last_attempt_at": _to_iso_z(self._last_attempt_at),
                "last_allowed_at": _to_iso_z(self._last_allowed_at),
                "last_blocked_at": _to_iso_z(self._last_blocked_at),
                "recent_window_size": int(self._recent_outcomes.maxlen or 0),
                "recent_attempts_total": recent_attempts,
                "recent_allowed_total": recent_allowed_total,
                "recent_blocked_total": recent_blocked_total,
            }


def debug_query_compat_sunset_snapshot(
    *,
    compat_enabled: bool,
    telemetry_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    attempts_total = int(telemetry_snapshot.get("attempts_total", 0) or 0)
    allowed_total = int(telemetry_snapshot.get("allowed_total", 0) or 0)
    blocked_total = int(telemetry_snapshot.get("blocked_total", 0) or 0)
    allow_rate = 0.0
    block_rate = 0.0
    if attempts_total > 0:
        allow_rate = allowed_total / attempts_total
        block_rate = blocked_total / attempts_total
    recommendation = _debug_query_compat_recommendation(
        compat_enabled=compat_enabled,
        attempts_total=attempts_total,
    )
    return {
        "event_debug_query_compat_allow_rate": round(allow_rate, 3),
        "event_debug_query_compat_block_rate": round(block_rate, 3),
        "event_debug_query_compat_recommendation": recommendation,
        "event_debug_query_compat_sunset_ready": _debug_query_compat_sunset_ready(
            recommendation=recommendation
        ),
        "event_debug_query_compat_sunset_reason": _debug_query_compat_sunset_reason(
            recommendation=recommendation
        ),
    }


def debug_query_compat_recent_snapshot(
    *,
    compat_enabled: bool,
    telemetry_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    recent_attempts = int(telemetry_snapshot.get("recent_attempts_total", 0) or 0)
    recent_allowed_total = int(telemetry_snapshot.get("recent_allowed_total", 0) or 0)
    recent_blocked_total = int(telemetry_snapshot.get("recent_blocked_total", 0) or 0)
    recent_allow_rate = 0.0
    recent_block_rate = 0.0
    if recent_attempts > 0:
        recent_allow_rate = recent_allowed_total / recent_attempts
        recent_block_rate = recent_blocked_total / recent_attempts
    return {
        "event_debug_query_compat_recent_attempts_total": recent_attempts,
        "event_debug_query_compat_recent_allow_rate": round(recent_allow_rate, 3),
        "event_debug_query_compat_recent_block_rate": round(recent_block_rate, 3),
        "event_debug_query_compat_recent_state": _debug_query_compat_recent_state(
            compat_enabled=compat_enabled,
            recent_block_rate=recent_block_rate,
            recent_attempts=recent_attempts,
        ),
    }


def debug_query_compat_freshness_snapshot(
    *,
    telemetry_snapshot: Mapping[str, Any],
    stale_after_seconds: int,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    if stale_after_seconds < 1:
        raise ValueError("EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS must be at least 1.")
    last_attempt_at = _from_iso_z(telemetry_snapshot.get("last_attempt_at"))
    if last_attempt_at is None:
        return {
            "event_debug_query_compat_stale_after_seconds": stale_after_seconds,
            "event_debug_query_compat_last_attempt_age_seconds": None,
            "event_debug_query_compat_last_attempt_state": "no_attempts_recorded",
        }
    now_value = now_utc if now_utc is not None else datetime.now(timezone.utc)
    if now_value.tzinfo is None:
        now_value = now_value.replace(tzinfo=timezone.utc)
    age_seconds = max(0, int((now_value.astimezone(timezone.utc) - last_attempt_at).total_seconds()))
    return {
        "event_debug_query_compat_stale_after_seconds": stale_after_seconds,
        "event_debug_query_compat_last_attempt_age_seconds": age_seconds,
        "event_debug_query_compat_last_attempt_state": "stale" if age_seconds >= stale_after_seconds else "fresh",
    }


def debug_query_compat_activity_snapshot(
    *,
    compat_enabled: bool,
    telemetry_snapshot: Mapping[str, Any],
    stale_after_seconds: int,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    attempts_total = int(telemetry_snapshot.get("attempts_total", 0) or 0)
    freshness_snapshot = debug_query_compat_freshness_snapshot(
        telemetry_snapshot=telemetry_snapshot,
        stale_after_seconds=stale_after_seconds,
        now_utc=now_utc,
    )
    activity_state = _debug_query_compat_activity_state(
        compat_enabled=compat_enabled,
        attempts_total=attempts_total,
        last_attempt_state=str(
            freshness_snapshot.get("event_debug_query_compat_last_attempt_state", "no_attempts_recorded")
        ),
    )
    return {
        "event_debug_query_compat_activity_state": activity_state,
        "event_debug_query_compat_activity_hint": _debug_query_compat_activity_hint(
            activity_state=activity_state
        ),
    }


def _debug_query_compat_recommendation(
    *,
    compat_enabled: bool,
    attempts_total: int,
) -> Literal[
    "compat_disabled",
    "no_compat_traffic_detected_disable_when_possible",
    "migrate_clients_before_disabling_compat",
]:
    if not compat_enabled:
        return "compat_disabled"
    if attempts_total == 0:
        return "no_compat_traffic_detected_disable_when_possible"
    return "migrate_clients_before_disabling_compat"


def _debug_query_compat_recent_state(
    *,
    compat_enabled: bool,
    recent_block_rate: float,
    recent_attempts: int,
) -> Literal[
    "compat_disabled",
    "no_recent_attempts",
    "mostly_blocked",
    "mixed",
    "mostly_allowed",
]:
    if not compat_enabled:
        return "compat_disabled"
    if recent_attempts <= 0:
        return "no_recent_attempts"
    if recent_block_rate >= 0.75:
        return "mostly_blocked"
    if recent_block_rate >= 0.25:
        return "mixed"
    return "mostly_allowed"


def _debug_query_compat_sunset_ready(
    *,
    recommendation: Literal[
        "compat_disabled",
        "no_compat_traffic_detected_disable_when_possible",
        "migrate_clients_before_disabling_compat",
    ],
) -> bool:
    return recommendation in {
        "compat_disabled",
        "no_compat_traffic_detected_disable_when_possible",
    }


def _debug_query_compat_sunset_reason(
    *,
    recommendation: Literal[
        "compat_disabled",
        "no_compat_traffic_detected_disable_when_possible",
        "migrate_clients_before_disabling_compat",
    ],
) -> Literal[
    "compat_disabled",
    "no_compat_attempts_detected",
    "compat_attempts_detected_migration_needed",
]:
    if recommendation == "compat_disabled":
        return "compat_disabled"
    if recommendation == "no_compat_traffic_detected_disable_when_possible":
        return "no_compat_attempts_detected"
    return "compat_attempts_detected_migration_needed"


def _debug_query_compat_activity_state(
    *,
    compat_enabled: bool,
    attempts_total: int,
    last_attempt_state: str,
) -> Literal[
    "compat_disabled",
    "no_attempts_observed",
    "stale_historical_attempts",
    "recent_attempts_observed",
]:
    if not compat_enabled:
        return "compat_disabled"
    if attempts_total <= 0:
        return "no_attempts_observed"
    if last_attempt_state == "stale":
        return "stale_historical_attempts"
    return "recent_attempts_observed"


def _debug_query_compat_activity_hint(
    *,
    activity_state: Literal[
        "compat_disabled",
        "no_attempts_observed",
        "stale_historical_attempts",
        "recent_attempts_observed",
    ],
) -> Literal[
    "compat_disabled_no_action",
    "can_disable_when_ready",
    "verify_stale_clients_before_disable",
    "keep_compat_until_recent_clients_migrate",
]:
    if activity_state == "compat_disabled":
        return "compat_disabled_no_action"
    if activity_state == "no_attempts_observed":
        return "can_disable_when_ready"
    if activity_state == "stale_historical_attempts":
        return "verify_stale_clients_before_disable"
    return "keep_compat_until_recent_clients_migrate"


def _to_iso_z(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _from_iso_z(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    normalized = raw.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
