from __future__ import annotations


def connector_read_baseline_snapshot() -> dict[str, object]:
    return {
        "policy_owner": "connector_read_execution_baseline",
        "selected_live_read_path": {
            "connector_kind": "cloud_drive",
            "provider": "google_drive",
            "operation": "list_files",
            "execution_mode": "provider_backed_next",
            "why_selected": "extends_connector_execution_into_metadata_only_drive_listing_without_exposing_document_contents_or_write_semantics",
        },
        "deferred_families": {
            "task_system": "current_live_read_path_already_implemented_through_clickup_list_tasks",
            "calendar": "current_live_read_path_already_implemented_through_google_calendar_read_availability",
        },
        "current_live_mutation_path": {
            "connector_kind": "task_system",
            "provider": "clickup",
            "operation": "create_task",
        },
    }
