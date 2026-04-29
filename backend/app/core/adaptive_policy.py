from __future__ import annotations

from collections.abc import Iterable, Mapping, Set

from app.communication.boundary import (
    CONTACT_CADENCE_RELATION,
    CONTACT_LOW_FREQUENCY,
    CONTACT_ON_DEMAND,
    CONTACT_SCHEDULED_ONLY,
    INTERRUPTION_LOW,
    INTERRUPTION_TOLERANCE_RELATION,
    INTERACTION_RITUAL_RELATION,
)

RELATION_CONFIDENCE_MIN = 0.68
ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN = 0.70
PREFERRED_ROLE_CONFIDENCE_MIN = 0.72
THETA_DOMINANT_BIAS_MIN = 0.58
PROACTIVE_ATTENTION_RECENT_OUTBOUND_LIMIT = 3
PROACTIVE_ATTENTION_UNANSWERED_LIMIT = 2

_THETA_BIAS_BY_CHANNEL = {
    "support": "support_bias",
    "analysis": "analysis_bias",
    "execution": "execution_bias",
}


def relation_value(
    *,
    relations: Iterable[Mapping[str, object]],
    relation_type: str,
    min_confidence: float = RELATION_CONFIDENCE_MIN,
) -> str | None:
    for relation in relations:
        candidate_type = str(relation.get("relation_type", "")).strip().lower()
        if candidate_type != relation_type:
            continue
        confidence = float(relation.get("confidence", 0.0) or 0.0)
        if confidence < min_confidence:
            continue
        value = str(relation.get("relation_value", "")).strip().lower()
        if value:
            return value
    return None


def preferred_role_allowed(
    *,
    preferred_role: str,
    preferred_role_confidence: float,
    allowed_roles: Set[str],
) -> bool:
    candidate = str(preferred_role or "").strip().lower()
    if candidate not in allowed_roles:
        return False
    return float(preferred_role_confidence or 0.0) >= PREFERRED_ROLE_CONFIDENCE_MIN


def dominant_theta_channel(theta: Mapping[str, object] | None) -> str | None:
    if not theta:
        return None

    candidates = {
        channel: float(theta.get(key, 0.0) or 0.0)
        for channel, key in _THETA_BIAS_BY_CHANNEL.items()
    }
    channel, bias = max(candidates.items(), key=lambda item: item[1])
    if bias < THETA_DOMINANT_BIAS_MIN:
        return None
    return channel


def is_role_adaptive_tie_break_turn(*, event_type: str, intent: str, topic: str) -> bool:
    return event_type == "question" or intent == "request_help" or topic == "general"


def is_motivation_adaptive_tie_break_turn(
    *,
    intent: str,
    topic: str,
    is_brief_turn: bool,
    has_positive_signal: bool,
) -> bool:
    return intent == "request_help" or (topic == "general" and is_brief_turn and not has_positive_signal)


def should_apply_motivation_adaptive_tie_break(
    *,
    intent: str,
    topic: str,
    is_brief_turn: bool,
    has_positive_signal: bool,
    has_emotional_signal: bool,
    has_execution_signal: bool,
    has_analysis_signal: bool,
) -> bool:
    if has_emotional_signal or has_execution_signal or has_analysis_signal:
        return False
    return is_motivation_adaptive_tie_break_turn(
        intent=intent,
        topic=topic,
        is_brief_turn=is_brief_turn,
        has_positive_signal=has_positive_signal,
    )


def proactive_signal_context(
    *,
    relations: Iterable[Mapping[str, object]],
    theta: Mapping[str, object] | None,
) -> dict[str, str | None]:
    return {
        "relation_collaboration": relation_value(
            relations=relations,
            relation_type="collaboration_dynamic",
        ),
        "relation_support_intensity": relation_value(
            relations=relations,
            relation_type="support_intensity_preference",
        ),
        "relation_delivery_reliability": relation_value(
            relations=relations,
            relation_type="delivery_reliability",
        ),
        "relation_contact_cadence": relation_value(
            relations=relations,
            relation_type=CONTACT_CADENCE_RELATION,
        ),
        "relation_interruption_tolerance": relation_value(
            relations=relations,
            relation_type=INTERRUPTION_TOLERANCE_RELATION,
        ),
        "relation_interaction_ritual": relation_value(
            relations=relations,
            relation_type=INTERACTION_RITUAL_RELATION,
        ),
        "theta_channel": dominant_theta_channel(theta),
    }


def proactive_relevance_adjustment(
    *,
    trigger: str,
    relations: Iterable[Mapping[str, object]],
    theta: Mapping[str, object] | None,
) -> float:
    context = proactive_signal_context(relations=relations, theta=theta)
    adjustment = 0.0

    if context["relation_delivery_reliability"] == "high_trust":
        adjustment += 0.06
    elif context["relation_delivery_reliability"] == "medium_trust":
        adjustment += 0.03
    elif context["relation_delivery_reliability"] == "low_trust":
        if trigger in {"time_checkin", "relation_nudge", "memory_pattern"}:
            adjustment -= 0.06
        else:
            adjustment -= 0.04

    if context["relation_support_intensity"] == "high_support" and trigger in {"time_checkin", "relation_nudge"}:
        adjustment += 0.05

    if context["relation_contact_cadence"] in {CONTACT_ON_DEMAND, CONTACT_SCHEDULED_ONLY}:
        if trigger in {"time_checkin", "goal_stagnation", "memory_pattern", "relation_nudge"}:
            adjustment -= 0.12
    elif context["relation_contact_cadence"] == CONTACT_LOW_FREQUENCY and trigger in {"time_checkin", "memory_pattern"}:
        adjustment -= 0.08

    if context["relation_collaboration"] == "hands_on" and trigger in {
        "task_blocked",
        "task_overdue",
        "goal_deadline",
        "goal_stagnation",
    }:
        adjustment += 0.04
    elif context["relation_collaboration"] == "guided" and trigger in {
        "time_checkin",
        "memory_pattern",
        "relation_nudge",
    }:
        adjustment += 0.03

    theta_channel = context["theta_channel"]
    if theta_channel == "execution" and trigger in {"task_blocked", "task_overdue", "goal_deadline"}:
        adjustment += 0.03
    elif theta_channel == "analysis" and trigger in {"goal_stagnation", "memory_pattern"}:
        adjustment += 0.02
    elif theta_channel == "support" and trigger in {"time_checkin", "relation_nudge"}:
        adjustment += 0.02

    return max(-0.15, min(0.15, round(adjustment, 2)))


def proactive_interruption_adjustment(
    *,
    relations: Iterable[Mapping[str, object]],
    theta: Mapping[str, object] | None,
) -> float:
    context = proactive_signal_context(relations=relations, theta=theta)
    adjustment = 0.0
    delivery_reliability = context["relation_delivery_reliability"]

    if delivery_reliability == "high_trust":
        adjustment -= 0.08
    elif delivery_reliability == "medium_trust":
        adjustment -= 0.03
    elif delivery_reliability == "low_trust":
        adjustment += 0.14

    if context["relation_support_intensity"] == "high_support":
        adjustment += 0.04

    if context["relation_contact_cadence"] in {CONTACT_ON_DEMAND, CONTACT_SCHEDULED_ONLY}:
        adjustment += 0.22
    elif context["relation_contact_cadence"] == CONTACT_LOW_FREQUENCY:
        adjustment += 0.12

    if context["relation_interruption_tolerance"] == INTERRUPTION_LOW:
        adjustment += 0.1

    if context["theta_channel"] == "support":
        adjustment += 0.03

    return max(-0.15, min(0.25, round(adjustment, 2)))


def proactive_attention_limits(
    *,
    relations: Iterable[Mapping[str, object]],
    theta: Mapping[str, object] | None,
) -> dict[str, int | str | None]:
    context = proactive_signal_context(relations=relations, theta=theta)
    recent_outbound_limit = PROACTIVE_ATTENTION_RECENT_OUTBOUND_LIMIT
    unanswered_limit = PROACTIVE_ATTENTION_UNANSWERED_LIMIT

    if context["relation_delivery_reliability"] == "low_trust":
        recent_outbound_limit = min(recent_outbound_limit, 1)
        unanswered_limit = min(unanswered_limit, 1)
    elif context["relation_delivery_reliability"] == "medium_trust":
        recent_outbound_limit = min(recent_outbound_limit, 2)

    if context["relation_support_intensity"] == "high_support" or context["theta_channel"] == "support":
        unanswered_limit = min(unanswered_limit, 1)

    if context["relation_contact_cadence"] in {CONTACT_ON_DEMAND, CONTACT_SCHEDULED_ONLY, CONTACT_LOW_FREQUENCY}:
        recent_outbound_limit = min(recent_outbound_limit, 1)
        unanswered_limit = min(unanswered_limit, 1)

    return {
        "recent_outbound_limit": recent_outbound_limit,
        "unanswered_proactive_limit": unanswered_limit,
        "relation_delivery_reliability": context["relation_delivery_reliability"],
        "relation_support_intensity": context["relation_support_intensity"],
        "relation_contact_cadence": context["relation_contact_cadence"],
        "relation_interruption_tolerance": context["relation_interruption_tolerance"],
        "relation_interaction_ritual": context["relation_interaction_ritual"],
        "theta_channel": context["theta_channel"],
    }
