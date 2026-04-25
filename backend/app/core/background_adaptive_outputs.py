from __future__ import annotations

from typing import Any


GOAL_PROGRESS_SIGNAL_KINDS = {
    "goal_execution_state",
    "goal_progress_score",
    "goal_progress_trend",
    "goal_progress_arc",
    "goal_milestone_transition",
    "goal_milestone_state",
    "goal_milestone_arc",
    "goal_milestone_pressure",
    "goal_milestone_dependency_state",
    "goal_milestone_due_state",
    "goal_milestone_due_window",
    "goal_milestone_risk",
    "goal_completion_criteria",
}


def build_background_adaptive_output_summary(
    *,
    conclusions: list[dict[str, Any]],
    relation_updates: list[dict[str, Any]],
    theta: dict[str, Any] | None,
    subconscious_proposals: list[dict[str, Any]],
    event_id: str,
) -> dict[str, Any]:
    conclusion_kinds = sorted(
        {
            str(item.get("kind", "")).strip()
            for item in conclusions
            if str(item.get("kind", "")).strip()
        }
    )
    relation_types = sorted(
        {
            str(item.get("relation_type", "")).strip()
            for item in relation_updates
            if str(item.get("relation_type", "")).strip()
        }
    )
    proposal_types = sorted(
        {
            str(item.get("proposal_type", "")).strip()
            for item in subconscious_proposals
            if str(item.get("proposal_type", "")).strip()
        }
    )
    progress_signal_kinds = sorted(kind for kind in conclusion_kinds if kind in GOAL_PROGRESS_SIGNAL_KINDS)
    adaptive_output_count = len(conclusion_kinds) + len(relation_types) + len(proposal_types) + (1 if theta else 0)
    return {
        "source": "background_reflection",
        "event_id": event_id,
        "adaptive_output_count": adaptive_output_count,
        "conclusion_kinds": conclusion_kinds,
        "relation_types": relation_types,
        "proposal_types": proposal_types,
        "progress_signal_kinds": progress_signal_kinds,
        "theta_update": {
            "present": theta is not None,
            "dominant_channel": _dominant_theta_channel(theta),
        },
        "foreground_mutation_posture": "background_owned_only",
    }


def summarize_loaded_adaptive_state(
    *,
    user_conclusions: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    theta: dict[str, Any] | None,
) -> dict[str, Any]:
    conclusion_kinds = sorted(
        {
            str(item.get("kind", "")).strip()
            for item in user_conclusions
            if str(item.get("kind", "")).strip()
        }
    )
    relation_types = sorted(
        {
            str(item.get("relation_type", "")).strip()
            for item in relations
            if str(item.get("relation_type", "")).strip()
        }
    )
    progress_signal_kinds = sorted(kind for kind in conclusion_kinds if kind in GOAL_PROGRESS_SIGNAL_KINDS)
    return {
        "loaded_conclusion_kinds": conclusion_kinds,
        "loaded_relation_types": relation_types,
        "loaded_progress_signal_kinds": progress_signal_kinds,
        "theta_loaded": theta is not None,
        "theta_dominant_channel": _dominant_theta_channel(theta),
        "foreground_mutation_posture": "read_only_background_outputs",
    }


def _dominant_theta_channel(theta: dict[str, Any] | None) -> str | None:
    if not theta:
        return None
    candidates = {
        "support": float(theta.get("support_bias", 0.0) or 0.0),
        "analysis": float(theta.get("analysis_bias", 0.0) or 0.0),
        "execution": float(theta.get("execution_bias", 0.0) or 0.0),
    }
    channel, bias = max(candidates.items(), key=lambda item: item[1])
    if bias <= 0.0:
        return None
    return channel
