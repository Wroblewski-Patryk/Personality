from __future__ import annotations

from typing import Any

from app.core.connector_policy import connector_authorization_matrix_snapshot
from app.core.role_selection_policy import role_preset_catalog_snapshot


CAPABILITY_CATALOG_POLICY_OWNER = "backend_capability_catalog_policy"


def capability_catalog_snapshot(
    *,
    api_readiness: dict[str, Any],
    learned_state: dict[str, Any],
    role_skill_policy: dict[str, Any],
    skill_registry: dict[str, Any],
    connectors: dict[str, Any],
    selection_visibility_summary: dict[str, Any] | None = None,
    authorization_subject: str | None = None,
) -> dict[str, Any]:
    organizer_tool_stack = (
        dict(connectors.get("organizer_tool_stack", {}))
        if isinstance(connectors.get("organizer_tool_stack"), dict)
        else {}
    )
    organizer_activation_snapshot = (
        dict(organizer_tool_stack.get("activation_snapshot", {}))
        if isinstance(organizer_tool_stack.get("activation_snapshot"), dict)
        else {}
    )
    web_knowledge_tools = (
        dict(connectors.get("web_knowledge_tools", {}))
        if isinstance(connectors.get("web_knowledge_tools"), dict)
        else {}
    )
    execution_baseline = (
        dict(connectors.get("execution_baseline", {}))
        if isinstance(connectors.get("execution_baseline"), dict)
        else {}
    )
    selection_summary = dict(selection_visibility_summary or {})
    role_catalog = role_preset_catalog_snapshot(
        current_role_name=str(role_skill_policy.get("current_role_name", "") or "")
    )
    authorization_matrix = connector_authorization_matrix_snapshot()
    described_skill_records = [
        dict(item)
        for item in skill_registry.get("catalog", [])
        if isinstance(item, dict)
    ]
    described_skill_ids = [
        str(item.get("skill_id", "")).strip()
        for item in described_skill_records
        if str(item.get("skill_id", "")).strip()
    ]
    authorization_entries = []
    raw_authorization_matrix = authorization_matrix.get("authorization_matrix", {})
    if isinstance(raw_authorization_matrix, dict):
        for connector_kind, entries in raw_authorization_matrix.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                operation = str(entry.get("operation", "")).strip()
                if not operation:
                    continue
                authorization_entries.append(
                    {
                        "connector_kind": str(connector_kind),
                        "qualified_operation": f"{connector_kind}.{operation}",
                        **entry,
                    }
                )
    authorized_without_opt_in_operations = [
        entry["qualified_operation"]
        for entry in authorization_entries
        if bool(entry.get("allowed_without_external_access"))
        and not bool(entry.get("requires_opt_in"))
        and not bool(entry.get("requires_confirmation"))
    ]
    authorized_with_opt_in_operations = [
        entry["qualified_operation"]
        for entry in authorization_entries
        if bool(entry.get("requires_opt_in")) and not bool(entry.get("requires_confirmation"))
    ]
    authorized_with_confirmation_operations = [
        entry["qualified_operation"]
        for entry in authorization_entries
        if bool(entry.get("requires_confirmation"))
    ]

    approved_connector_kinds = organizer_tool_stack.get("approved_connector_kinds", [])
    approved_operations = organizer_tool_stack.get("approved_operations", [])
    ready_operations = organizer_tool_stack.get("ready_operations", [])
    credential_gap_operations = organizer_tool_stack.get("credential_gap_operations", [])
    work_partner_tool_families = role_skill_policy.get("work_partner_tool_families", [])

    return {
        "policy_owner": CAPABILITY_CATALOG_POLICY_OWNER,
        "catalog_posture": "aggregated_backend_truth_surface",
        "aggregation_boundary": "composed_from_existing_health_and_internal_inspection_surfaces",
        "execution_authority": "unchanged_action_boundary",
        "authorization_authority": "unchanged_connector_permission_gates",
        "capability_record_truth_model": {
            "description_boundary": "durable_role_and_skill_metadata_plus_tool_authorization_records",
            "selection_boundary": "runtime_turn_selection_and_selected_skill_metadata",
            "authorization_boundary": "connector_permission_gates_plus_provider_readiness",
        },
        "future_ui_posture": "consume_catalog_without_reconstructing_backend_truth_client_side",
        "source_surfaces": {
            "api_readiness": "/health.api_readiness",
            "learned_state": "/health.learned_state",
            "role_skill": "/health.role_skill",
            "connectors": "/health.connectors",
            "internal_inspection": str(api_readiness.get("internal_inspection_path", "/internal/state/inspect")),
            "current_turn_role": str(api_readiness.get("current_turn_role_surface", "system_debug.role")),
            "current_turn_selected_skills": str(
                api_readiness.get(
                    "current_turn_selected_skills_surface",
                    "system_debug.adaptive_state.selected_skills",
                )
            ),
            "current_turn_plan": str(api_readiness.get("current_turn_plan_surface", "system_debug.plan")),
        },
        "role_posture": {
            "role_selection_owner": role_skill_policy.get("role_selection_owner"),
            "current_role_name": role_skill_policy.get("current_role_name", ""),
            "work_partner_role_available": role_skill_policy.get("work_partner_role_available"),
            "work_partner_role_state": role_skill_policy.get("work_partner_role_state"),
            "work_partner_scope": role_skill_policy.get("work_partner_scope"),
            "work_partner_mutation_boundary": role_skill_policy.get("work_partner_mutation_boundary"),
            "described_role_presets": role_catalog.get("catalog", []),
            "described_role_names": role_catalog.get("selectable_role_names", []),
            "selectable_role_names": role_catalog.get("selectable_role_names", []),
            "preferred_role_eligible_names": role_catalog.get("preferred_role_eligible_names", []),
        },
        "skill_catalog_posture": {
            "skill_selection_owner": role_skill_policy.get("skill_selection_owner"),
            "skill_execution_boundary": role_skill_policy.get("skill_execution_boundary"),
            "action_skill_execution_allowed": role_skill_policy.get("action_skill_execution_allowed"),
            "selection_visibility_summary": selection_summary,
            "catalog_count": skill_registry.get("catalog_count", 0),
            "catalog": described_skill_records,
            "described_skill_ids": described_skill_ids,
            "runtime_selection_surface": selection_summary.get(
                "current_turn_selected_skills_available_via",
                "system_debug.adaptive_state.selected_skills",
            ),
            "learning_posture": skill_registry.get("learning_posture"),
            "learning_hint": skill_registry.get("learning_hint"),
        },
        "tool_and_connector_posture": {
            "authorization_record_owner": authorization_matrix.get("policy_owner"),
            "authorization_subject": (
                str(authorization_subject).strip()
                if str(authorization_subject or "").strip()
                else "global_runtime_policy_posture"
            ),
            "authorization_record_state": (
                "user_scope_policy_and_provider_posture"
                if str(authorization_subject or "").strip()
                else "global_policy_and_provider_posture"
            ),
            "approved_tool_families": sorted(
                {
                    str(item).strip()
                    for item in list(work_partner_tool_families) + list(approved_connector_kinds)
                    if str(item).strip()
                }
            ),
            "selectable_tool_families": sorted(
                {
                    str(item).strip()
                    for item in list(work_partner_tool_families)
                    if str(item).strip()
                }
            ),
            "approved_operations": list(approved_operations),
            "authorized_without_opt_in_operations": authorized_without_opt_in_operations,
            "authorized_with_opt_in_operations": authorized_with_opt_in_operations,
            "authorized_with_confirmation_operations": authorized_with_confirmation_operations,
            "ready_operations": list(ready_operations),
            "credential_gap_operations": list(credential_gap_operations),
            "organizer_stack_state": organizer_tool_stack.get("readiness_state"),
            "organizer_stack_hint": organizer_tool_stack.get("readiness_hint"),
            "organizer_activation_state": organizer_activation_snapshot.get("provider_activation_state"),
            "organizer_activation_next_actions": organizer_activation_snapshot.get("next_actions", []),
            "confirmation_required_operations": organizer_tool_stack.get("confirmation_required_operations", []),
            "user_opt_in_required_operations": organizer_tool_stack.get("user_opt_in_required_operations", []),
            "web_knowledge_tools": web_knowledge_tools,
            "execution_baseline_owner": execution_baseline.get("execution_owner"),
            "execution_baseline_boundary": execution_baseline.get("mvp_boundary"),
        },
        "learned_state_linkage": {
            "learned_state_policy_owner": learned_state.get("policy_owner"),
            "tool_grounded_learning_policy_owner": (
                learned_state.get("tool_grounded_learning", {}) or {}
            ).get("policy_owner"),
            "skill_learning_posture": learned_state.get("skill_learning_posture"),
            "internal_inspection_path": learned_state.get("internal_inspection_path"),
        },
    }
