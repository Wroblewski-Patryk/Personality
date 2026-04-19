from __future__ import annotations

from typing import Any, Literal


SchedulerSubsource = Literal["reflection_tick", "maintenance_tick", "proactive_tick"]
SCHEDULER_SOURCE = "scheduler"
DEFAULT_SCHEDULER_SUBSOURCE: SchedulerSubsource = "reflection_tick"
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


def scheduler_cadence_rules() -> dict[str, dict[str, int | bool]]:
    return {key: dict(value) for key, value in SCHEDULER_CADENCE_RULES.items()}


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
