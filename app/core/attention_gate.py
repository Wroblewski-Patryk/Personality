from __future__ import annotations

from typing import Any

from app.core.contracts import Event
from app.core.scheduler_contracts import SCHEDULER_PROACTIVE_TICK


def evaluate_proactive_attention_gate(event: Event) -> dict[str, Any] | None:
    if event.source != "scheduler" or event.subsource != SCHEDULER_PROACTIVE_TICK:
        return None

    payload = event.payload if isinstance(event.payload, dict) else {}
    proactive_payload = payload.get("proactive") if isinstance(payload.get("proactive"), dict) else {}
    user_context = proactive_payload.get("user_context") if isinstance(proactive_payload.get("user_context"), dict) else {}

    quiet_hours = bool(user_context.get("quiet_hours", False))
    recent_outbound_count = _safe_int(user_context.get("recent_outbound_count"))
    unanswered_proactive_count = _safe_int(user_context.get("unanswered_proactive_count"))

    if quiet_hours:
        return {
            "allowed": False,
            "reason": "quiet_hours_gate",
            "recent_outbound_count": recent_outbound_count,
            "unanswered_proactive_count": unanswered_proactive_count,
        }
    if recent_outbound_count >= 3:
        return {
            "allowed": False,
            "reason": "attention_outbound_cooldown",
            "recent_outbound_count": recent_outbound_count,
            "unanswered_proactive_count": unanswered_proactive_count,
        }
    if unanswered_proactive_count >= 2:
        return {
            "allowed": False,
            "reason": "attention_unanswered_backlog",
            "recent_outbound_count": recent_outbound_count,
            "unanswered_proactive_count": unanswered_proactive_count,
        }
    return {
        "allowed": True,
        "reason": "attention_gate_pass",
        "recent_outbound_count": recent_outbound_count,
        "unanswered_proactive_count": unanswered_proactive_count,
    }


def _safe_int(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0
