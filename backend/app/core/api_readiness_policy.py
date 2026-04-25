from __future__ import annotations


API_READINESS_POLICY_OWNER = "v2_backend_api_readiness_policy"


def api_readiness_policy_snapshot() -> dict[str, object]:
    return {
        "policy_owner": API_READINESS_POLICY_OWNER,
        "product_stage": "v2_backend_surface_seed",
        "readiness_state": "stable_backend_surfaces_available",
        "health_surfaces": {
            "capability_catalog": "/health.capability_catalog",
            "learned_state": "/health.learned_state",
            "role_skill": "/health.role_skill",
            "connectors": "/health.connectors",
            "v1_readiness": "/health.v1_readiness",
        },
        "internal_inspection_path": "/internal/state/inspect",
        "internal_inspection_sections": [
            "capability_catalog",
            "identity_state",
            "learned_knowledge",
            "role_skill_state",
            "planning_state",
        ],
        "capability_catalog_sections": [
            "role_posture",
            "skill_catalog_posture",
            "tool_and_connector_posture",
            "learned_state_linkage",
        ],
        "planning_state_sections": [
            "active_goals",
            "active_tasks",
            "active_goal_milestones",
            "pending_proposals",
        ],
        "current_turn_debug_surface_path": "/internal/event/debug",
        "current_turn_role_surface": "system_debug.role",
        "current_turn_selected_skills_surface": "system_debug.adaptive_state.selected_skills",
        "current_turn_plan_surface": "system_debug.plan",
        "connector_posture_surface": "/health.connectors",
    }
