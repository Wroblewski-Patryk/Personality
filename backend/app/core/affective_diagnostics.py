from __future__ import annotations

from typing import Any


def affective_input_policy_snapshot() -> dict[str, str]:
    return {
        "policy_owner": "perception_affective_input",
        "input_kind": "heuristic_turn_signal",
        "input_source_baseline": "deterministic_placeholder",
        "final_assessment_owner": "affective_assessment_rollout_policy",
        "fallback_resolution_posture": "reuse_input_when_assessment_unavailable",
    }


def extract_affective_fallback_reason(affective: Any) -> str:
    if str(getattr(affective, "source", "")).strip().lower() != "fallback":
        return ""
    for evidence in list(getattr(affective, "evidence", []) or []):
        item = str(evidence).strip()
        if item.startswith("fallback_reason:"):
            return item.split(":", 1)[1][:64]
    return ""


def affective_resolution_snapshot(
    *,
    affective_input: Any,
    affective_final: Any,
) -> dict[str, Any]:
    fallback_reason = extract_affective_fallback_reason(affective_final)
    input_source = str(getattr(affective_input, "source", "")).strip().lower() or "unknown"
    final_source = str(getattr(affective_final, "source", "")).strip().lower() or "unknown"
    input_label = str(getattr(affective_input, "affect_label", "")).strip().lower() or "neutral"
    final_label = str(getattr(affective_final, "affect_label", "")).strip().lower() or "neutral"
    input_reused = (
        final_source == "fallback"
        and input_source == "deterministic_placeholder"
        and input_label == final_label
    )
    return {
        "input_source": input_source,
        "input_label": input_label,
        "input_needs_support": bool(getattr(affective_input, "needs_support", False)),
        "final_source": final_source,
        "final_label": final_label,
        "final_needs_support": bool(getattr(affective_final, "needs_support", False)),
        "input_reused_as_final": input_reused,
        "fallback_reason": fallback_reason or "not_applicable",
        "resolution_owner_chain": "perception_affective_input_to_affective_assessment",
    }
