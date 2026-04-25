from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.contracts import Event, EventMeta
from app.core.scheduler_contracts import (
    SCHEDULER_SOURCE,
    normalize_scheduler_payload,
    normalize_scheduler_subsource,
)

MAX_EVENT_TEXT_LENGTH = 4000
MAX_META_ID_LENGTH = 64
ANONYMOUS_USER_ID = "anonymous"
SCHEDULER_USER_ID = "scheduler"


def looks_like_telegram_update(raw: dict[str, Any]) -> bool:
    message = raw.get("message")
    if not isinstance(message, dict):
        return False
    return any(key in message for key in {"chat", "from", "text"}) or "update_id" in raw


def normalize_event(
    raw: dict[str, Any],
    *,
    default_user_id: str | None = None,
    default_trace_id: str | None = None,
) -> Event:
    if looks_like_telegram_update(raw):
        message = raw["message"]
        chat = message.get("chat", {})
        user = message.get("from", {})
        payload = {
            "text": _normalize_text(message.get("text", "")),
            "chat_id": chat.get("id"),
            "update_id": raw.get("update_id"),
        }
        return Event(
            event_id=str(uuid4()),
            source="telegram",
            subsource="user_message",
            timestamp=datetime.now(timezone.utc),
            payload=payload,
            meta=EventMeta(
                user_id=_normalize_user_id(default_user_id or user.get("id")),
                trace_id=str(uuid4()),
            ),
        )

    payload = raw.get("payload", {})
    if not isinstance(payload, dict):
        payload = {}

    text_source = raw.get("text") if "text" in raw else payload.get("text", "")
    normalized_text = _normalize_text(text_source)
    payload = {"text": normalized_text}

    meta = raw.get("meta", {})
    if not isinstance(meta, dict):
        meta = {}

    return Event(
        event_id=str(uuid4()),
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload=payload,
        meta=EventMeta(
                user_id=_normalize_user_id(meta.get("user_id") or default_user_id),
                trace_id=_normalize_trace_id(meta.get("trace_id") or default_trace_id),
        ),
    )


def build_scheduler_event(
    *,
    subsource: str | None = None,
    payload: dict[str, Any] | None = None,
    user_id: str | None = None,
    trace_id: str | None = None,
) -> Event:
    normalized_subsource = normalize_scheduler_subsource(subsource)
    normalized_payload = normalize_scheduler_payload(payload, subsource=normalized_subsource)
    return Event(
        event_id=str(uuid4()),
        source=SCHEDULER_SOURCE,
        subsource=normalized_subsource,
        timestamp=datetime.now(timezone.utc),
        payload=normalized_payload,
        meta=EventMeta(
            user_id=_normalize_user_id(user_id or SCHEDULER_USER_ID),
            trace_id=_normalize_trace_id(trace_id),
        ),
    )


def _normalize_text(value: object) -> str:
    text = str(value) if value is not None else ""
    normalized = " ".join(text.split())
    return normalized[:MAX_EVENT_TEXT_LENGTH]


def coalesce_turn_text(parts: list[str], *, separator: str = "\n") -> str:
    normalized_parts: list[str] = []
    for part in parts:
        normalized = _normalize_text(part)
        if normalized:
            normalized_parts.append(normalized)
    if not normalized_parts:
        return ""
    merged = separator.join(normalized_parts)
    return merged[:MAX_EVENT_TEXT_LENGTH]


def _normalize_user_id(value: object) -> str:
    candidate = str(value or "").strip()
    if not candidate:
        return ANONYMOUS_USER_ID
    return candidate[:MAX_META_ID_LENGTH]


def _normalize_trace_id(value: object) -> str:
    candidate = str(value or "").strip()
    if not candidate:
        return str(uuid4())
    return candidate[:MAX_META_ID_LENGTH]
