from __future__ import annotations

from collections.abc import Iterable, Mapping, Set

RELATION_CONFIDENCE_MIN = 0.68
ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN = 0.70
PREFERRED_ROLE_CONFIDENCE_MIN = 0.72
THETA_DOMINANT_BIAS_MIN = 0.58

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
