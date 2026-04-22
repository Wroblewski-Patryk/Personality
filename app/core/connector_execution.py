def clickup_task_create_ready(settings) -> bool:
    api_token = str(getattr(settings, "clickup_api_token", "") or "").strip()
    list_id = str(getattr(settings, "clickup_list_id", "") or "").strip()
    return bool(api_token and list_id)


def connector_execution_baseline_snapshot(settings) -> dict[str, object]:
    clickup_ready = clickup_task_create_ready(settings)
    clickup_state = "provider_backed_ready" if clickup_ready else "credentials_missing"
    clickup_hint = (
        "clickup_create_task_live"
        if clickup_ready
        else "configure_clickup_api_token_and_clickup_list_id_for_live_execution"
    )
    return {
        "execution_owner": "connector_execution_registry",
        "mvp_boundary": "clickup_task_create_and_list_first_live_paths",
        "task_system": {
            "read_capable_live_paths": ["clickup_list_tasks"],
            "mutation_live_paths": ["clickup_create_task"],
            "clickup_create_task": {
                "operation": "create_task",
                "provider": "clickup",
                "execution_mode": "provider_backed_when_configured",
                "ready": clickup_ready,
                "state": clickup_state,
                "hint": clickup_hint,
            },
            "clickup_list_tasks": {
                "operation": "list_tasks",
                "provider": "clickup",
                "execution_mode": "provider_backed_when_configured",
                "ready": clickup_ready,
                "state": clickup_state,
                "hint": (
                    "clickup_list_tasks_live"
                    if clickup_ready
                    else "configure_clickup_api_token_and_clickup_list_id_for_live_read_execution"
                ),
            },
            "other_operations": "policy_only_until_pre_action_read_and_additional_provider_paths_exist",
        },
        "calendar": {
            "execution_mode": "policy_only",
            "hint": "calendar_execution_remains_permission_gated_without_provider_adapter",
        },
        "cloud_drive": {
            "execution_mode": "policy_only",
            "hint": "drive_execution_remains_permission_gated_without_provider_adapter",
        },
    }
