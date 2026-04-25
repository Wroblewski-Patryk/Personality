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
    organizer_daily_use_state = str(
        organizer_tool_stack.get("daily_use_state", "daily_use_state_unknown") or "daily_use_state_unknown"
    )
    website_reading_workflow = web_knowledge_tools.get("website_reading_workflow", {})
    website_reading_state = str(
        website_reading_workflow.get("workflow_state", "website_reading_state_unknown")
        or "website_reading_state_unknown"
    )
    tool_grounded_learning = learned_state.get("tool_grounded_learning", {})
    tool_grounded_learning_state = (
        "tool_grounded_learning_surface_ready"
        if (
            tool_grounded_learning.get("policy_owner") == "tool_grounded_learning_policy"
            and tool_grounded_learning.get("capture_owner") == "action_owned_external_read_summaries_only"
            and tool_grounded_learning.get("persistence_owner") == "memory_conclusion_write_after_action"
            and tool_grounded_learning.get("execution_bypass_allowed") is False
            and tool_grounded_learning.get("self_modifying_skill_learning_allowed") is False
        )
        else "tool_grounded_learning_surface_invalid"
    )
    deployment_state = (
        "deploy_parity_surface_ready"
        if (
            deployment.get("deployment_automation_policy_owner") == "coolify_repo_deploy_automation"
            and str(deployment.get("runtime_trigger_mode", "") or "")
            in {"source_automation", "webhook_manual_fallback", "ui_manual_fallback"}
            and str(deployment.get("runtime_build_revision_state", "") or "") == "runtime_build_revision_declared"
        )
        else "deploy_parity_surface_invalid"
    )
    planned_work_state = "foreground_due_delivery_and_recurring_reevaluation_ready"
    return {
        "policy_owner": V1_READINESS_POLICY_OWNER,
        "product_stage": "v1_no_ui_life_assistant",
        "acceptance_bundle_owner": "health_plus_incident_evidence_plus_behavior_validation",
        "final_acceptance_bundle_owner": "no_ui_v1_daily_use_acceptance_bundle",
        "final_acceptance_target": "all_final_gates_green_in_live_production",
        "conversation_surface": "/health.conversation_channels.telegram",
        "conversation_round_trip_state": telegram_state,
        "conversation_gate_state": (
            "conversation_surface_ready"
            if telegram_state in {"provider_backed_ready", "missing_bot_token"}
            else "conversation_surface_invalid"
        ),
        "learned_state_surface": "/health.learned_state",
        "learned_state_internal_path": learned_state_path,
        "learned_state_gate_state": (
            "inspection_surface_ready" if learned_state_path == "/internal/state/inspect" else "inspection_surface_invalid"
        ),
        "approved_tool_slices": list(V1_APPROVED_TOOL_SLICES),
        "approved_tooling_state": "bounded_provider_slices_live",
        "organizer_daily_use_state": organizer_daily_use_state,
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
        "final_acceptance_gate_states": {
            "conversation_reliability": (
                "conversation_surface_ready"
                if telegram_state in {"provider_backed_ready", "missing_bot_token"}
                else "conversation_surface_invalid"
            ),
            "learned_state_inspection": (
                "inspection_surface_ready"
                if learned_state_path == "/internal/state/inspect"
                else "inspection_surface_invalid"
            ),
            "website_reading": website_reading_state,
            "tool_grounded_learning": tool_grounded_learning_state,
            "time_aware_planned_work": planned_work_state,
            "organizer_daily_use": organizer_daily_use_state,
            "deploy_parity": deployment_state,
        },
        "final_acceptance_surfaces": {
            "conversation_reliability": "/health.conversation_channels.telegram",
            "learned_state_inspection": "/health.learned_state",
            "website_reading": "/health.connectors.web_knowledge_tools.website_reading_workflow",
            "tool_grounded_learning": "/health.learned_state.tool_grounded_learning",
            "time_aware_planned_work": "/health.v1_readiness",
            "organizer_daily_use": "/health.connectors.organizer_tool_stack",
            "deploy_parity": "/health.deployment",
        },
        "required_behavior_scenarios": list(V1_REQUIRED_BEHAVIOR_SCENARIOS),
        "work_partner_role_state": work_partner_state,
        "work_partner_boundary": str(
            role_skill_policy.get("work_partner_role_boundary", "same_personality_role_not_separate_persona") or ""
        ),
    }
