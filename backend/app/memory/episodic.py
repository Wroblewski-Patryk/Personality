from collections.abc import Mapping, Sequence
from typing import Any


def extract_episode_fields(memory_item: Mapping[str, Any] | None) -> dict[str, str]:
    if not isinstance(memory_item, Mapping):
        return {}

    payload = memory_item.get("payload")
    if isinstance(payload, Mapping):
        return {
            "event": _as_text(payload.get("event")),
            "memory_kind": _as_text(payload.get("memory_kind")),
            "memory_topics": ",".join(_as_text_list(payload.get("memory_topics"))),
            "response_language": _as_text(payload.get("response_language") or payload.get("language")),
            "affect_label": _as_text(payload.get("affect_label")),
            "affect_intensity": _as_text(payload.get("affect_intensity")),
            "affect_needs_support": _as_text(payload.get("affect_needs_support")),
            "affect_source": _as_text(payload.get("affect_source")),
            "affect_evidence": ",".join(_as_text_list(payload.get("affect_evidence"))),
            "preference_update": _as_text(payload.get("preference_update")),
            "collaboration_update": _as_text(payload.get("collaboration_update")),
            "proactive_preference_update": _as_text(payload.get("proactive_preference_update")),
            "proactive_state_update": _as_text(payload.get("proactive_state_update")),
            "relation_update": _as_text(payload.get("relation_update")),
            "goal_update": _as_text(payload.get("goal_update")),
            "task_update": _as_text(payload.get("task_update")),
            "task_status_update": _as_text(payload.get("task_status_update")),
            "planned_work_update": _as_text(payload.get("planned_work_update")),
            "planned_work_status_update": _as_text(payload.get("planned_work_status_update")),
            "calendar_connector_update": _as_text(payload.get("calendar_connector_update")),
            "task_connector_update": _as_text(payload.get("task_connector_update")),
            "drive_connector_update": _as_text(payload.get("drive_connector_update")),
            "connector_expansion_update": _as_text(payload.get("connector_expansion_update")),
            "context": _as_text(payload.get("context")),
            "motivation": _as_text(payload.get("motivation")),
            "role": _as_text(payload.get("role")),
            "plan_goal": _as_text(payload.get("plan_goal")),
            "plan_steps": ",".join(_as_text_list(payload.get("plan_steps"))),
            "action": _as_text(payload.get("action")),
            "expression": _as_text(payload.get("expression")),
        }

    fields: dict[str, str] = {}
    raw_summary = _as_text(memory_item.get("summary"))
    for part in " ".join(raw_summary.split()).split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        fields[key.strip()] = value.strip()
    return fields


def build_episode_summary(payload: Mapping[str, Any], *, max_length: int = 1000) -> str:
    event_text = _clip_text(_as_text(payload.get("event")), max_length=120)
    expression_text = _clip_text(_as_text(payload.get("expression")), max_length=180)
    memory_kind = _as_text(payload.get("memory_kind"))
    memory_topics = _as_text_list(payload.get("memory_topics"))
    affect_label = _as_text(payload.get("affect_label"))
    affect_needs_support = _as_text(payload.get("affect_needs_support"))
    motivation = _as_text(payload.get("motivation"))
    role = _as_text(payload.get("role"))
    action = _as_text(payload.get("action"))

    parts: list[str] = []
    if event_text:
        parts.append(f"User said '{event_text}'.")
    if expression_text:
        parts.append(f"AION replied '{expression_text}'.")

    details: list[str] = []
    if memory_kind:
        details.append(f"memory={memory_kind}")
    if memory_topics:
        details.append(f"topics={', '.join(memory_topics)}")
    if affect_label:
        details.append(f"affect={affect_label}")
    if affect_needs_support:
        details.append(f"support={affect_needs_support}")
    if motivation:
        details.append(f"motivation={motivation}")
    if role:
        details.append(f"role={role}")
    if action:
        details.append(f"action={action}")
    if details:
        parts.append("Episode details: " + "; ".join(details) + ".")

    summary = " ".join(part.strip() for part in parts if part.strip()).strip()
    if len(summary) <= max_length:
        return summary
    return _clip_text(summary, max_length=max_length)


def _clip_text(value: str, *, max_length: int) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
        return normalized

    clipped = normalized[: max_length - 3].rstrip()
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    return clipped.rstrip(" ,;:-") + "..."


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        candidates = value.split(",")
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        candidates = list(value)
    else:
        candidates = []

    normalized: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        text = _as_text(item)
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized
