from __future__ import annotations

from typing import Any, Mapping


V1_READINESS_POLICY_OWNER = "v1_release_readiness_policy"
V1_REQUIRED_BEHAVIOR_SCENARIOS = (
    "T13.1",
    "T14.1",
    "T14.2",
    "T14.3",
    "T15.1",
    "T15.2",
    "T16.1",
    "T16.2",
    "T16.3",
    "T17.1",
    "T17.2",
    "T18.1",
    "T18.2",
    "T19.1",
    "T19.2",
)
V1_APPROVED_TOOL_SLICES = (
    "knowledge_search.search_web",
    "web_browser.read_page",
    "task_system.clickup_list_tasks",
    "task_system.clickup_update_task",
    "calendar.google_calendar_read_availability",
    "cloud_drive.google_drive_list_files",
)


def _conversation_gate_state(telegram_conversation_channel: Mapping[str, Any]) -> str:
    round_trip_ready = bool(telegram_conversation_channel.get("round_trip_ready", False))
    round_trip_state = str(telegram_conversation_channel.get("round_trip_state", "") or "")
    if round_trip_ready and round_trip_state == "provider_backed_ready":
        return "conversation_surface_ready"
    if round_trip_state == "missing_bot_token":
        return "conversation_surface_provider_missing"
    return "conversation_surface_invalid"


def _learned_state_gate_state(learned_state: Mapping[str, Any]) -> str:
    learned_state_path = str(learned_state.get("internal_inspection_path", "") or "")
    if learned_state_path == "/internal/state/inspect":
        return "inspection_surface_ready"
    return "inspection_surface_invalid"


def _tool_grounded_learning_state(learned_state: Mapping[str, Any]) -> str:
    tool_grounded_learning = learned_state.get("tool_grounded_learning", {})
    if (
        tool_grounded_learning.get("policy_owner") == "tool_grounded_learning_policy"
        and tool_grounded_learning.get("capture_owner") == "action_owned_external_read_summaries_only"
        and tool_grounded_learning.get("persistence_owner") == "memory_conclusion_write_after_action"
        and tool_grounded_learning.get("execution_bypass_allowed") is False
        and tool_grounded_learning.get("self_modifying_skill_learning_allowed") is False
    ):
        return "tool_grounded_learning_surface_ready"
    return "tool_grounded_learning_surface_invalid"


def _deployment_gate_state(deployment: Mapping[str, Any]) -> str:
    automation_owner = str(deployment.get("deployment_automation_policy_owner", "") or "")
    trigger_mode = str(deployment.get("runtime_trigger_mode", "") or "")
    trigger_class = str(deployment.get("runtime_trigger_class", "") or "")
    provenance_state = str(deployment.get("runtime_provenance_state", "") or "")
    build_revision_state = str(deployment.get("runtime_build_revision_state", "") or "")
    if automation_owner != "coolify_repo_deploy_automation" or build_revision_state != "runtime_build_revision_declared":
        return "deploy_parity_surface_invalid"
    if trigger_class == "primary_automation" and provenance_state == "primary_runtime_provenance_declared":
        return "deploy_parity_surface_ready"
    if trigger_mode in {"webhook_manual_fallback", "ui_manual_fallback"} and provenance_state == "fallback_runtime_provenance_declared":
        return "deploy_parity_surface_manual_fallback"
    return "deploy_parity_surface_invalid"


def v1_readiness_policy_snapshot(
    *,
    telegram_conversation_channel: Mapping[str, Any],
    learned_state: Mapping[str, Any],
    role_skill_policy: Mapping[str, Any],
    organizer_tool_stack: Mapping[str, Any],
    web_knowledge_tools: Mapping[str, Any],
    deployment: Mapping[str, Any],
) -> dict[str, object]:
    telegram_state = str(telegram_conversation_channel.get("round_trip_state", "") or "")
    learned_state_path = str(learned_state.get("internal_inspection_path", "") or "")
    work_partner_state = str(role_skill_policy.get("work_partner_role_state", "available") or "available")
    conversation_gate_state = _conversation_gate_state(telegram_conversation_channel)
    learned_state_gate_state = _learned_state_gate_state(learned_state)
    organizer_daily_use_state = str(
        organizer_tool_stack.get("daily_use_state", "daily_use_state_unknown") or "daily_use_state_unknown"
    )
    website_reading_workflow = web_knowledge_tools.get("website_reading_workflow", {})
    website_reading_state = str(
        website_reading_workflow.get("workflow_state", "website_reading_state_unknown")
        or "website_reading_state_unknown"
    )
    tool_grounded_learning_state = _tool_grounded_learning_state(learned_state)
    deployment_state = _deployment_gate_state(deployment)
    planned_work_state = "foreground_due_delivery_and_recurring_reevaluation_ready"
    final_acceptance_gate_states = {
        "conversation_reliability": conversation_gate_state,
        "learned_state_inspection": learned_state_gate_state,
        "website_reading": website_reading_state,
        "tool_grounded_learning": tool_grounded_learning_state,
        "time_aware_planned_work": planned_work_state,
        "deploy_parity": deployment_state,
    }
    final_acceptance_state = (
        "core_v1_bundle_ready"
        if all(
            state in {
                "conversation_surface_ready",
                "inspection_surface_ready",
                "ready_for_direct_and_search_first_review",
                "tool_grounded_learning_surface_ready",
                "foreground_due_delivery_and_recurring_reevaluation_ready",
                "deploy_parity_surface_ready",
            }
            for state in final_acceptance_gate_states.values()
        )
        else "core_v1_bundle_incomplete"
    )
    return {
        "policy_owner": V1_READINESS_POLICY_OWNER,
        "product_stage": "v1_no_ui_life_assistant",
        "acceptance_bundle_owner": "health_plus_incident_evidence_plus_behavior_validation",
        "final_acceptance_bundle_owner": "no_ui_v1_daily_use_acceptance_bundle",
        "final_acceptance_target": "all_final_gates_green_in_live_production",
        "conversation_surface": "/health.conversation_channels.telegram",
        "conversation_round_trip_state": telegram_state,
        "conversation_gate_state": conversation_gate_state,
        "learned_state_surface": "/health.learned_state",
        "learned_state_internal_path": learned_state_path,
        "learned_state_gate_state": learned_state_gate_state,
        "approved_tool_slices": list(V1_APPROVED_TOOL_SLICES),
        "approved_tooling_state": (
            "core_bounded_tooling_ready"
            if website_reading_state == "ready_for_direct_and_search_first_review"
            and tool_grounded_learning_state == "tool_grounded_learning_surface_ready"
            and work_partner_state == "available"
            else "core_bounded_tooling_incomplete"
        ),
        "organizer_daily_use_state": organizer_daily_use_state,
        "organizer_daily_use_classification": "extension_readiness_non_blocking_for_core_v1",
        "organizer_daily_use_ready_workflow_count": int(
            organizer_tool_stack.get("daily_use_ready_workflow_count", 0) or 0
        ),
        "organizer_daily_use_total_workflow_count": int(
            organizer_tool_stack.get("daily_use_total_workflow_count", 0) or 0
        ),
        "organizer_daily_use_ready_workflows": list(
            organizer_tool_stack.get("daily_use_ready_workflows", []) or []
        ),
        "organizer_daily_use_blocked_workflows": list(
            organizer_tool_stack.get("daily_use_blocked_workflows", []) or []
        ),
        "organizer_daily_use_hint": str(
            organizer_tool_stack.get("daily_use_hint", "organizer_daily_use_hint_unknown")
            or "organizer_daily_use_hint_unknown"
        ),
        "organizer_daily_use_next_actions": list(
            organizer_tool_stack.get("credential_gap_operations", []) or []
        ),
        "website_reading_workflow_state": website_reading_state,
        "tool_grounded_learning_state": tool_grounded_learning_state,
        "time_aware_planned_work_policy_owner": "internal_time_aware_planned_work_policy",
        "time_aware_planned_work_delivery_path": "attention_to_planning_to_expression_to_action",
        "time_aware_planned_work_recurrence_owner": "scheduler_reevaluation_with_foreground_handoff",
        "time_aware_planned_work_gate_state": planned_work_state,
        "deploy_parity_state": deployment_state,
        "final_acceptance_gate_states": final_acceptance_gate_states,
        "final_acceptance_state": final_acceptance_state,
        "final_acceptance_surfaces": {
            "conversation_reliability": "/health.conversation_channels.telegram",
            "learned_state_inspection": "/health.learned_state",
            "website_reading": "/health.connectors.web_knowledge_tools.website_reading_workflow",
            "tool_grounded_learning": "/health.learned_state.tool_grounded_learning",
            "time_aware_planned_work": "/health.v1_readiness",
            "deploy_parity": "/health.deployment",
        },
        "extension_gate_states": {
            "organizer_daily_use": organizer_daily_use_state,
        },
        "extension_gate_surfaces": {
            "organizer_daily_use": "/health.connectors.organizer_tool_stack",
        },
        "required_behavior_scenarios": list(V1_REQUIRED_BEHAVIOR_SCENARIOS),
        "work_partner_role_state": work_partner_state,
        "work_partner_boundary": str(
            role_skill_policy.get("work_partner_role_boundary", "same_personality_role_not_separate_persona") or ""
        ),
    }
