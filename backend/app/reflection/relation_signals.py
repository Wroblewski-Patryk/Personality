from __future__ import annotations

from collections.abc import Callable, Sequence

from app.communication.boundary import (
    BOUNDARY_RELATION_TYPES,
    extract_communication_boundary_signals,
)


def derive_relation_updates(
    recent_memory: Sequence[dict],
    *,
    extract_memory_fields: Callable[[dict], dict[str, str]],
) -> list[dict]:
    if not recent_memory:
        return []

    action_success_count = 0
    support_turn_count = 0
    collaboration_updates: list[str] = []
    boundary_updates: list[dict] = []

    for memory_item in recent_memory:
        fields = extract_memory_fields(memory_item)
        action = str(fields.get("action", "")).strip().lower()
        if action == "success":
            action_success_count += 1

        collaboration = str(fields.get("collaboration_update", "")).strip().lower()
        if collaboration in {"guided", "hands_on"}:
            collaboration_updates.append(collaboration)

        affect_needs_support = str(fields.get("affect_needs_support", "")).strip().lower()
        if affect_needs_support in {"1", "true", "yes"}:
            support_turn_count += 1

        relation_update = str(fields.get("relation_update", "")).strip().lower()
        relation_type, relation_value = _parse_relation_update(relation_update)
        if relation_type in BOUNDARY_RELATION_TYPES and relation_value:
            boundary_updates.append(
                {
                    "relation_type": relation_type,
                    "relation_value": relation_value,
                    "confidence": 0.82,
                    "source": "background_reflection",
                    "evidence_count": 1,
                    "decay_rate": 0.02,
                }
            )

        event_text = str(fields.get("event", "")).strip()
        for signal in extract_communication_boundary_signals(event_text):
            boundary_updates.append(
                {
                    "relation_type": signal.relation_type,
                    "relation_value": signal.relation_value,
                    "confidence": min(0.94, signal.confidence),
                    "source": "background_reflection",
                    "evidence_count": 1,
                    "decay_rate": 0.02,
                }
            )

    sample_size = len(recent_memory)
    relation_updates: list[dict] = []

    if sample_size >= 3:
        success_ratio = float(action_success_count) / float(sample_size)
        if success_ratio >= 0.75:
            relation_updates.append(
                {
                    "relation_type": "delivery_reliability",
                    "relation_value": "high_trust",
                    "confidence": 0.74,
                    "source": "background_reflection",
                    "evidence_count": action_success_count,
                    "decay_rate": 0.02,
                }
            )
        elif success_ratio >= 0.5:
            relation_updates.append(
                {
                    "relation_type": "delivery_reliability",
                    "relation_value": "medium_trust",
                    "confidence": 0.69,
                    "source": "background_reflection",
                    "evidence_count": action_success_count,
                    "decay_rate": 0.03,
                }
            )
        else:
            relation_updates.append(
                {
                    "relation_type": "delivery_reliability",
                    "relation_value": "low_trust",
                    "confidence": 0.62,
                    "source": "background_reflection",
                    "evidence_count": max(1, sample_size - action_success_count),
                    "decay_rate": 0.05,
                }
            )

    if collaboration_updates:
        relation_updates.append(
            {
                "relation_type": "collaboration_dynamic",
                "relation_value": collaboration_updates[0],
                "confidence": 0.78,
                "source": "background_reflection",
                "evidence_count": len(collaboration_updates),
                "decay_rate": 0.04,
            }
        )

    if support_turn_count >= 2:
        relation_updates.append(
            {
                "relation_type": "support_intensity_preference",
                "relation_value": "high_support",
                "confidence": 0.76,
                "source": "background_reflection",
                "evidence_count": support_turn_count,
                "decay_rate": 0.03,
            }
        )
    elif support_turn_count == 1 and sample_size >= 4:
        relation_updates.append(
            {
                "relation_type": "support_intensity_preference",
                "relation_value": "balanced_support",
                "confidence": 0.68,
                "source": "background_reflection",
                "evidence_count": support_turn_count,
                "decay_rate": 0.05,
            }
        )

    relation_updates.extend(boundary_updates)

    deduped: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for relation in relation_updates:
        key = (str(relation["relation_type"]), str(relation["relation_value"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(relation)
    return deduped


def _parse_relation_update(value: str) -> tuple[str, str]:
    if not value:
        return "", ""
    parts = value.split(":")
    if len(parts) < 2:
        return "", ""
    return parts[0].strip().lower(), parts[1].strip().lower()
