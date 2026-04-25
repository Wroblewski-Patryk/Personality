from __future__ import annotations

from typing import Any


TOPOLOGY_SWITCH_RELEASE_WINDOW = "after_group_50_evidence_green"
REFLECTION_SWITCH_CRITERIA = (
    "reflection_deployment_readiness.ready",
    "external_driver_dispatch_path_verified",
    "release_smoke_includes_reflection_mode_checks",
)
ATTENTION_SWITCH_CRITERIA = (
    "attention.deployment_readiness.ready",
    "attention.contract_store_mode_repository_backed",
    "release_smoke_includes_attention_owner_checks",
)


def runtime_topology_policy_snapshot(
    *,
    reflection_runtime_mode: str,
    reflection_readiness: dict[str, Any],
    attention_snapshot: dict[str, Any],
) -> dict[str, Any]:
    reflection_ready = bool(reflection_readiness.get("ready", False))
    attention_ready = bool(attention_snapshot.get("deployment_readiness", {}).get("ready", False))
    return {
        "policy_owner": "runtime_topology_finalization",
        "release_window": TOPOLOGY_SWITCH_RELEASE_WINDOW,
        "reflection_switch": {
            "baseline_mode": "in_process",
            "target_mode": "deferred",
            "selected_mode": str(reflection_runtime_mode),
            "production_default_change_ready": reflection_ready,
            "criteria": list(REFLECTION_SWITCH_CRITERIA),
            "rollback_posture": "return_to_in_process_until_external_driver_slo_is_stable",
        },
        "attention_switch": {
            "policy_owner": "runtime_topology_finalization",
            "baseline_mode": "in_process",
            "target_mode": "durable_inbox",
            "selected_mode": str(attention_snapshot.get("coordination_mode", "in_process")),
            "production_default_change_ready": attention_ready,
            "criteria": list(ATTENTION_SWITCH_CRITERIA),
            "rollback_posture": "return_to_in_process_until_durable_inbox_cleanup_and_claim_semantics_are_stable",
        },
        "graph_boundary": {
            "pre_graph_owner": "runtime_shell",
            "graph_stage_owner": "foreground_graph_runner",
            "post_graph_owner": "runtime_followups",
            "long_term_baseline": "current_pre_post_graph_split_is_canonical",
            "future_node_expansion": "bounded_optional_non_stage_nodes_only_when_complexity_decreases",
        },
        "proposal_decision_policy": {
            "decision_set": ["accept", "merge", "defer", "discard"],
            "decision_set_state": "fixed_baseline",
            "expansion_rule": "new_decisions_require_explicit_contract_and_status_mapping",
        },
    }
