from __future__ import annotations

from typing import Any

from app.core.adaptive_policy import proactive_attention_limits
from app.core.contracts import Event
from app.core.scheduler_contracts import SCHEDULER_PROACTIVE_TICK


def evaluate_proactive_attention_gate(
    event: Event,
    *,
    relations: list[dict] | None = None,
    theta: dict | None = None,
) -> dict[str, Any] | None:
    if event.source != "scheduler" or event.subsource != SCHEDULER_PROACTIVE_TICK:
        return None

    payload = event.payload if isinstance(event.payload, dict) else {}
    proactive_payload = payload.get("proactive") if isinstance(payload.get("proactive"), dict) else {}
    user_context = proactive_payload.get("user_context") if isinstance(proactive_payload.get("user_context"), dict) else {}
    adaptive_limits = proactive_attention_limits(relations=relations or [], theta=theta)

    quiet_hours = bool(user_context.get("quiet_hours", False))
    recent_outbound_count = _safe_int(user_context.get("recent_outbound_count"))
    unanswered_proactive_count = _safe_int(user_context.get("unanswered_proactive_count"))
    recent_outbound_limit = int(adaptive_limits["recent_outbound_limit"])
    unanswered_proactive_limit = int(adaptive_limits["unanswered_proactive_limit"])

    base_gate = {
        "recent_outbound_count": recent_outbound_count,
        "unanswered_proactive_count": unanswered_proactive_count,
        "recent_outbound_limit": recent_outbound_limit,
        "unanswered_proactive_limit": unanswered_proactive_limit,
        "relation_delivery_reliability": adaptive_limits["relation_delivery_reliability"],
        "relation_support_intensity": adaptive_limits["relation_support_intensity"],
        "theta_channel": adaptive_limits["theta_channel"],
    }

    if quiet_hours:
        return {
            "allowed": False,
            "reason": "quiet_hours_gate",
            **base_gate,
        }
    if recent_outbound_count >= recent_outbound_limit:
        return {
            "allowed": False,
            "reason": "attention_outbound_cooldown",
            **base_gate,
        }
    if unanswered_proactive_count >= unanswered_proactive_limit:
        return {
            "allowed": False,
            "reason": "attention_unanswered_backlog",
            **base_gate,
        }
    return {
        "allowed": True,
        "reason": "attention_gate_pass",
        **base_gate,
    }


def _safe_int(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0
