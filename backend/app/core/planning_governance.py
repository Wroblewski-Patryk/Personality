from __future__ import annotations


def planning_governance_snapshot() -> dict[str, object]:
    return {
        "policy_owner": "planning_governance",
        "goal_task_creation_posture": "bounded_inferred_growth_from_repeated_execution_blockers_only",
        "goal_task_creation_authority": "typed_intents_and_conscious_action_boundary",
        "proposal_decision_set": ["accept", "merge", "defer", "discard"],
        "proposal_decision_state": "fixed_baseline",
        "proposal_expansion_rule": "new_decisions_require_explicit_contract_and_status_mapping",
    }
