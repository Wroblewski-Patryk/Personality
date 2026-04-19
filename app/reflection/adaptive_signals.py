from collections.abc import Callable, Sequence

from app.utils.preferences import detect_collaboration_preference


def has_outcome_evidence(fields: dict[str, str]) -> bool:
    if fields.get("action", "").strip().lower() != "success":
        return False
    return any(
        fields.get(key, "").strip()
        for key in (
            "goal_update",
            "task_update",
            "task_status_update",
            "preference_update",
            "collaboration_update",
        )
    )


def derive_preferred_role(
    *,
    role_counts: dict[str, int],
    total: int,
    outcome_evidence_count: int,
) -> dict | None:
    if total < 4 or not role_counts:
        return None
    if outcome_evidence_count < 2:
        return None

    preferred_role, count = max(role_counts.items(), key=lambda item: item[1])
    if count < 3:
        return None
    if count / total < 0.6:
        return None

    return {
        "kind": "preferred_role",
        "content": preferred_role,
        "confidence": 0.76,
        "source": "background_reflection",
    }


def derive_theta(
    recent_memory: Sequence[dict],
    *,
    extract_memory_fields: Callable[[dict], dict[str, str]],
) -> dict | None:
    if len(recent_memory) < 3:
        return None

    role_map = {
        "friend": "support_bias",
        "analyst": "analysis_bias",
        "executor": "execution_bias",
    }
    totals = {
        "support_bias": 0,
        "analysis_bias": 0,
        "execution_bias": 0,
    }
    counted = 0

    for memory_item in recent_memory:
        fields = extract_memory_fields(memory_item)
        if not has_outcome_evidence(fields):
            continue
        role = fields.get("role", "").strip().lower()
        key = role_map.get(role)
        if key is None:
            continue
        totals[key] += 1
        counted += 1

    if counted < 3:
        return None

    return {
        "support_bias": round(totals["support_bias"] / counted, 2),
        "analysis_bias": round(totals["analysis_bias"] / counted, 2),
        "execution_bias": round(totals["execution_bias"] / counted, 2),
    }


def derive_collaboration_preference(
    recent_memory: Sequence[dict],
    *,
    extract_memory_fields: Callable[[dict], dict[str, str]],
) -> dict | None:
    if len(recent_memory) < 4:
        return None

    guided_count = 0
    hands_on_count = 0
    sample_size = 0

    for memory_item in recent_memory:
        fields = extract_memory_fields(memory_item)
        if not has_outcome_evidence(fields):
            continue

        collaboration_update = fields.get("collaboration_update", "").strip().lower()
        event_text = fields.get("event", "").strip()
        explicit_event_preference = detect_collaboration_preference(event_text)

        signal = ""
        if collaboration_update in {"guided", "hands_on"}:
            signal = collaboration_update
        elif explicit_event_preference is not None:
            signal = explicit_event_preference.preference

        if signal not in {"guided", "hands_on"}:
            continue

        sample_size += 1
        if signal == "guided":
            guided_count += 1
        else:
            hands_on_count += 1

    if sample_size < 3:
        return None

    if hands_on_count >= 2 and hands_on_count / sample_size >= 0.67:
        return {
            "kind": "collaboration_preference",
            "content": "hands_on",
            "confidence": 0.73,
            "source": "background_reflection",
        }

    if guided_count >= 2 and guided_count / sample_size >= 0.67:
        return {
            "kind": "collaboration_preference",
            "content": "guided",
            "confidence": 0.73,
            "source": "background_reflection",
        }

    return None
