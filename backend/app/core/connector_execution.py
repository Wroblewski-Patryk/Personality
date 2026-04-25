def clickup_task_create_ready(settings) -> bool:
    api_token = str(getattr(settings, "clickup_api_token", "") or "").strip()
    list_id = str(getattr(settings, "clickup_list_id", "") or "").strip()
    return bool(api_token and list_id)


def google_calendar_read_ready(settings) -> bool:
    access_token = str(getattr(settings, "google_calendar_access_token", "") or "").strip()
    calendar_id = str(getattr(settings, "google_calendar_calendar_id", "") or "").strip()
    timezone_name = str(getattr(settings, "google_calendar_timezone", "") or "").strip()
    return bool(access_token and calendar_id and timezone_name)


def google_drive_list_ready(settings) -> bool:
    access_token = str(getattr(settings, "google_drive_access_token", "") or "").strip()
    folder_id = str(getattr(settings, "google_drive_folder_id", "") or "").strip()
    return bool(access_token and folder_id)


def connector_execution_baseline_snapshot(settings) -> dict[str, object]:
    clickup_ready = clickup_task_create_ready(settings)
    clickup_state = "provider_backed_ready" if clickup_ready else "credentials_missing"
    clickup_hint = (
        "clickup_create_task_live"
        if clickup_ready
        else "configure_clickup_api_token_and_clickup_list_id_for_live_execution"
    )
    google_calendar_ready = google_calendar_read_ready(settings)
    google_calendar_state = (
        "provider_backed_ready" if google_calendar_ready else "credentials_missing"
    )
    google_calendar_hint = (
        "google_calendar_read_availability_live"
        if google_calendar_ready
        else "configure_google_calendar_access_token_and_google_calendar_calendar_id_for_live_read_execution"
    )
    google_drive_ready = google_drive_list_ready(settings)
    google_drive_state = "provider_backed_ready" if google_drive_ready else "credentials_missing"
    google_drive_hint = (
        "google_drive_list_files_live"
        if google_drive_ready
        else "configure_google_drive_access_token_for_live_metadata_read_execution"
    )
    return {
        "execution_owner": "connector_execution_registry",
        "mvp_boundary": "clickup_task_create_list_update_plus_google_calendar_google_drive_duckduckgo_and_generic_http_first_live_paths",
        "task_system": {
            "read_capable_live_paths": ["clickup_list_tasks"],
            "mutation_live_paths": ["clickup_create_task", "clickup_update_task"],
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
            "clickup_update_task": {
                "operation": "update_task",
                "provider": "clickup",
                "execution_mode": "provider_backed_when_configured",
                "ready": clickup_ready,
                "state": clickup_state,
                "hint": (
                    "clickup_update_task_live"
                    if clickup_ready
                    else "configure_clickup_api_token_and_clickup_list_id_for_live_update_execution"
                ),
            },
            "other_operations": "policy_only_until_additional_task_system_provider_paths_exist",
        },
        "calendar": {
            "read_capable_live_paths": ["google_calendar_read_availability"],
            "mutation_live_paths": [],
            "google_calendar_read_availability": {
                "operation": "read_availability",
                "provider": "google_calendar",
                "execution_mode": "provider_backed_when_configured",
                "ready": google_calendar_ready,
                "state": google_calendar_state,
                "hint": google_calendar_hint,
            },
            "other_operations": "policy_only_until_additional_calendar_read_or_mutation_paths_exist",
        },
        "cloud_drive": {
            "read_capable_live_paths": ["google_drive_list_files"],
            "mutation_live_paths": [],
            "google_drive_list_files": {
                "operation": "list_files",
                "provider": "google_drive",
                "execution_mode": "provider_backed_when_configured",
                "ready": google_drive_ready,
                "state": google_drive_state,
                "hint": google_drive_hint,
            },
            "other_operations": "policy_only_until_additional_drive_read_or_mutation_paths_exist",
        },
        "knowledge_search": {
            "read_capable_live_paths": ["duckduckgo_search_web"],
            "mutation_live_paths": [],
            "search_web": {
                "operation": "search_web",
                "provider": "duckduckgo_html",
                "execution_mode": "provider_backed_without_credentials",
                "ready": True,
                "state": "provider_backed_ready",
                "hint": "duckduckgo_html_search_live",
            },
            "suggest_search": {
                "operation": "suggest_search",
                "provider": "duckduckgo_html",
                "execution_mode": "policy_only",
                "ready": True,
                "state": "planning_only_allowed",
                "hint": "search_recommendation_can_be_explained_without_live_provider_execution",
            },
            "other_operations": "policy_only_until_additional_search_provider_paths_are_approved",
        },
        "web_browser": {
            "read_capable_live_paths": ["generic_http_read_page"],
            "mutation_live_paths": [],
            "read_page": {
                "operation": "read_page",
                "provider": "generic_http",
                "execution_mode": "provider_backed_without_credentials",
                "ready": True,
                "state": "provider_backed_ready",
                "hint": "generic_http_read_page_live",
            },
            "suggest_page_review": {
                "operation": "suggest_page_review",
                "provider": "generic_http",
                "execution_mode": "policy_only",
                "ready": True,
                "state": "planning_only_allowed",
                "hint": "page_review_recommendation_can_be_explained_without_live_provider_execution",
            },
            "other_operations": "policy_only_until_additional_browser_provider_paths_are_approved",
        },
    }


def organizer_tool_stack_snapshot(settings) -> dict[str, object]:
    execution_baseline = connector_execution_baseline_snapshot(settings)
    task_system = dict(execution_baseline["task_system"])
    calendar = dict(execution_baseline["calendar"])
    cloud_drive = dict(execution_baseline["cloud_drive"])

    clickup_create = dict(task_system["clickup_create_task"])
    clickup_list = dict(task_system["clickup_list_tasks"])
    clickup_update = dict(task_system["clickup_update_task"])
    calendar_read = dict(calendar["google_calendar_read_availability"])
    drive_list = dict(cloud_drive["google_drive_list_files"])

    approved_operations = [
        "task_system.clickup_create_task",
        "task_system.clickup_list_tasks",
        "task_system.clickup_update_task",
        "calendar.google_calendar_read_availability",
        "cloud_drive.google_drive_list_files",
    ]
    readiness_entries = {
        "task_system.clickup_create_task": clickup_create,
        "task_system.clickup_list_tasks": clickup_list,
        "task_system.clickup_update_task": clickup_update,
        "calendar.google_calendar_read_availability": calendar_read,
        "cloud_drive.google_drive_list_files": drive_list,
    }
    ready_operations = [
        operation_id for operation_id in approved_operations if bool(readiness_entries[operation_id].get("ready", False))
    ]
    credential_gap_operations = [
        operation_id for operation_id in approved_operations if not bool(readiness_entries[operation_id].get("ready", False))
    ]
    activation_requirements = {
        "clickup": {
            "provider": "clickup",
            "required_settings": [
                "CLICKUP_API_TOKEN",
                "CLICKUP_LIST_ID",
            ],
            "optional_settings": [],
            "activation_scope": [
                "task_system.clickup_create_task",
                "task_system.clickup_list_tasks",
                "task_system.clickup_update_task",
            ],
            "ready": bool(clickup_create.get("ready", False)),
            "missing_settings": [
                name
                for name, value in (
                    ("CLICKUP_API_TOKEN", str(getattr(settings, "clickup_api_token", "") or "").strip()),
                    ("CLICKUP_LIST_ID", str(getattr(settings, "clickup_list_id", "") or "").strip()),
                )
                if not value
            ],
            "user_opt_in_required": True,
            "confirmation_required_operations": [
                "task_system.clickup_create_task",
                "task_system.clickup_update_task",
            ],
            "next_action": (
                "ready_for_clickup_operator_acceptance"
                if bool(clickup_create.get("ready", False))
                else "configure_clickup_api_token_and_clickup_list_id"
            ),
        },
        "google_calendar": {
            "provider": "google_calendar",
            "required_settings": [
                "GOOGLE_CALENDAR_ACCESS_TOKEN",
                "GOOGLE_CALENDAR_CALENDAR_ID",
                "GOOGLE_CALENDAR_TIMEZONE",
            ],
            "optional_settings": [],
            "activation_scope": [
                "calendar.google_calendar_read_availability",
            ],
            "ready": bool(calendar_read.get("ready", False)),
            "missing_settings": [
                name
                for name, value in (
                    (
                        "GOOGLE_CALENDAR_ACCESS_TOKEN",
                        str(getattr(settings, "google_calendar_access_token", "") or "").strip(),
                    ),
                    (
                        "GOOGLE_CALENDAR_CALENDAR_ID",
                        str(getattr(settings, "google_calendar_calendar_id", "") or "").strip(),
                    ),
                    (
                        "GOOGLE_CALENDAR_TIMEZONE",
                        str(getattr(settings, "google_calendar_timezone", "") or "").strip(),
                    ),
                )
                if not value
            ],
            "user_opt_in_required": True,
            "confirmation_required_operations": [],
            "next_action": (
                "ready_for_google_calendar_operator_acceptance"
                if bool(calendar_read.get("ready", False))
                else "configure_google_calendar_access_token_calendar_id_and_timezone"
            ),
        },
        "google_drive": {
            "provider": "google_drive",
            "required_settings": [
                "GOOGLE_DRIVE_ACCESS_TOKEN",
                "GOOGLE_DRIVE_FOLDER_ID",
            ],
            "optional_settings": [],
            "activation_scope": [
                "cloud_drive.google_drive_list_files",
            ],
            "ready": bool(drive_list.get("ready", False)),
            "missing_settings": [
                name
                for name, value in (
                    (
                        "GOOGLE_DRIVE_ACCESS_TOKEN",
                        str(getattr(settings, "google_drive_access_token", "") or "").strip(),
                    ),
                    (
                        "GOOGLE_DRIVE_FOLDER_ID",
                        str(getattr(settings, "google_drive_folder_id", "") or "").strip(),
                    ),
                )
                if not value
            ],
            "user_opt_in_required": True,
            "confirmation_required_operations": [],
            "next_action": (
                "ready_for_google_drive_operator_acceptance"
                if bool(drive_list.get("ready", False))
                else "configure_google_drive_access_token_and_folder_id"
            ),
        },
    }
    activation_ready_provider_count = sum(
        1 for provider_entry in activation_requirements.values() if bool(provider_entry["ready"])
    )
    activation_next_actions = [
        provider_entry["next_action"]
        for provider_entry in activation_requirements.values()
        if not bool(provider_entry["ready"])
    ]
    daily_use_workflows = {
        "clickup_task_review_and_mutation": {
            "provider": "clickup",
            "workflow_kind": "task_review_and_mutation",
            "approved_operations": [
                "task_system.clickup_list_tasks",
                "task_system.clickup_create_task",
                "task_system.clickup_update_task",
            ],
            "daily_use_ready": bool(clickup_create.get("ready", False)),
            "daily_use_state": (
                "ready_for_daily_use_with_opt_in_and_confirmed_mutations"
                if bool(clickup_create.get("ready", False))
                else "blocked_missing_provider_credentials"
            ),
            "user_opt_in_required": True,
            "mutation_confirmation_required": True,
            "planning_boundary": "internal_tasks_and_goals_remain_primary",
            "next_action": (
                "ready_for_clickup_daily_use"
                if bool(clickup_create.get("ready", False))
                else "configure_clickup_api_token_and_clickup_list_id"
            ),
        },
        "google_calendar_availability_inspection": {
            "provider": "google_calendar",
            "workflow_kind": "availability_inspection",
            "approved_operations": [
                "calendar.google_calendar_read_availability",
            ],
            "daily_use_ready": bool(calendar_read.get("ready", False)),
            "daily_use_state": (
                "ready_for_daily_use_with_opt_in"
                if bool(calendar_read.get("ready", False))
                else "blocked_missing_provider_credentials"
            ),
            "user_opt_in_required": True,
            "mutation_confirmation_required": False,
            "planning_boundary": "availability_evidence_only_no_calendar_management",
            "next_action": (
                "ready_for_google_calendar_daily_use"
                if bool(calendar_read.get("ready", False))
                else "configure_google_calendar_access_token_calendar_id_and_timezone"
            ),
        },
        "google_drive_file_space_inspection": {
            "provider": "google_drive",
            "workflow_kind": "file_space_inspection",
            "approved_operations": [
                "cloud_drive.google_drive_list_files",
            ],
            "daily_use_ready": bool(drive_list.get("ready", False)),
            "daily_use_state": (
                "ready_for_daily_use_with_opt_in"
                if bool(drive_list.get("ready", False))
                else "blocked_missing_provider_credentials"
            ),
            "user_opt_in_required": True,
            "mutation_confirmation_required": False,
            "planning_boundary": "metadata_only_file_evidence_no_document_body_ingestion",
            "next_action": (
                "ready_for_google_drive_daily_use"
                if bool(drive_list.get("ready", False))
                else "configure_google_drive_access_token_and_folder_id"
            ),
        },
    }
    ready_daily_use_workflows = [
        workflow_id
        for workflow_id, workflow in daily_use_workflows.items()
        if bool(workflow.get("daily_use_ready", False))
    ]
    blocked_daily_use_workflows = [
        workflow_id
        for workflow_id, workflow in daily_use_workflows.items()
        if not bool(workflow.get("daily_use_ready", False))
    ]
    return {
        "policy_owner": "production_organizer_tool_stack",
        "stack_name": "clickup_calendar_drive_first_stack",
        "product_scope": "no_ui_life_assistant_and_work_partner_organization_support",
        "approved_connector_kinds": ["task_system", "calendar", "cloud_drive"],
        "approved_operations": approved_operations,
        "read_only_operations": [
            "task_system.clickup_list_tasks",
            "calendar.google_calendar_read_availability",
            "cloud_drive.google_drive_list_files",
        ],
        "confirmation_required_operations": [
            "task_system.clickup_create_task",
            "task_system.clickup_update_task",
        ],
        "user_opt_in_required_operations": list(readiness_entries.keys()),
        "mutation_boundary": "clickup_mutations_confirmation_required_calendar_and_drive_mutations_out_of_scope",
        "read_boundary": "bounded_reads_only_for_calendar_availability_and_drive_metadata",
        "provider_ready_operation_count": len(ready_operations),
        "provider_total_operation_count": len(readiness_entries),
        "ready_operations": ready_operations,
        "credential_gap_operations": credential_gap_operations,
        "readiness_state": (
            "provider_stack_ready" if not credential_gap_operations else "provider_credentials_missing"
        ),
        "readiness_hint": (
            "organizer_tool_stack_ready_for_operator_acceptance"
            if not credential_gap_operations
            else "configure_clickup_google_calendar_and_google_drive_credentials_for_full_stack_readiness"
        ),
        "daily_use_workflows": daily_use_workflows,
        "daily_use_ready_workflow_count": len(ready_daily_use_workflows),
        "daily_use_total_workflow_count": len(daily_use_workflows),
        "daily_use_ready_workflows": ready_daily_use_workflows,
        "daily_use_blocked_workflows": blocked_daily_use_workflows,
        "daily_use_state": (
            "all_daily_use_workflows_ready"
            if not blocked_daily_use_workflows
            else "daily_use_workflows_blocked_by_provider_activation"
        ),
        "daily_use_hint": (
            "organizer_workflows_ready_for_daily_use"
            if not blocked_daily_use_workflows
            else "finish_provider_activation_before_treating_organizer_stack_as_daily_use_ready"
        ),
        "activation_snapshot": {
            "policy_owner": "production_organizer_tool_activation",
            "provider_activation_total": len(activation_requirements),
            "provider_activation_ready": activation_ready_provider_count,
            "provider_activation_state": (
                "all_providers_ready_for_operator_acceptance"
                if activation_ready_provider_count == len(activation_requirements)
                else "provider_activation_incomplete"
            ),
            "user_opt_in_required": True,
            "mutation_confirmation_required": True,
            "provider_requirements": activation_requirements,
            "next_actions": activation_next_actions,
        },
        "provider_readiness": readiness_entries,
    }
