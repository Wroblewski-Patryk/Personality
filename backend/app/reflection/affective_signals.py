from collections.abc import Callable, Sequence


def derive_affective_conclusions(
    recent_memory: Sequence[dict],
    *,
    extract_memory_fields: Callable[[dict], dict[str, str]],
) -> list[dict]:
    if len(recent_memory) < 3:
        return []

    sample_size = 0
    support_hits = 0
    distress_hits = 0
    positive_hits = 0

    for memory_item in recent_memory:
        fields = extract_memory_fields(memory_item)
        action = fields.get("action", "").strip().lower()
        if action and action != "success":
            continue

        affect_label = fields.get("affect_label", "").strip().lower()
        needs_support = fields.get("affect_needs_support", "").strip().lower() in {"1", "true", "yes"}
        if not affect_label and not fields.get("affect_needs_support", "").strip():
            continue

        sample_size += 1
        if needs_support or affect_label == "support_distress":
            support_hits += 1
        if affect_label == "support_distress":
            distress_hits += 1
        if affect_label == "positive_engagement":
            positive_hits += 1

    if sample_size < 3:
        return []

    support_ratio = support_hits / sample_size
    positive_ratio = positive_hits / sample_size
    conclusions: list[dict] = []

    if distress_hits >= 2 and support_ratio >= 0.5:
        conclusions.append(
            {
                "kind": "affective_support_pattern",
                "content": "recurring_distress",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        )
    elif positive_hits >= 2 and positive_ratio >= 0.5 and distress_hits <= 1:
        conclusions.append(
            {
                "kind": "affective_support_pattern",
                "content": "confidence_recovery",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        )

    if support_ratio >= 0.6:
        conclusions.append(
            {
                "kind": "affective_support_sensitivity",
                "content": "high",
                "confidence": 0.78,
                "source": "background_reflection",
            }
        )
    elif support_ratio >= 0.35:
        conclusions.append(
            {
                "kind": "affective_support_sensitivity",
                "content": "moderate",
                "confidence": 0.72,
                "source": "background_reflection",
            }
        )

    return conclusions
