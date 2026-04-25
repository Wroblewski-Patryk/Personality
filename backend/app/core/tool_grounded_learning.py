from __future__ import annotations

from typing import Any


TOOL_GROUNDED_LEARNING_POLICY_OWNER = "tool_grounded_learning_policy"

TOOL_GROUNDED_CONCLUSION_KINDS: dict[tuple[str, str], str] = {
    ("knowledge_search", "search_web"): "tool_grounded_search_knowledge",
    ("web_browser", "read_page"): "tool_grounded_page_knowledge",
    ("task_system", "list_tasks"): "tool_grounded_task_snapshot",
    ("calendar", "read_availability"): "tool_grounded_calendar_snapshot",
    ("cloud_drive", "list_files"): "tool_grounded_drive_snapshot",
}


def tool_grounded_conclusion_kind(*, source_family: str, source_operation: str) -> str:
    return TOOL_GROUNDED_CONCLUSION_KINDS[(str(source_family).strip().lower(), str(source_operation).strip().lower())]


def is_tool_grounded_conclusion_kind(kind: str) -> bool:
    normalized = str(kind or "").strip().lower()
    return normalized in TOOL_GROUNDED_CONCLUSION_KINDS.values()


def tool_grounded_learning_policy_snapshot() -> dict[str, Any]:
    return {
        "policy_owner": TOOL_GROUNDED_LEARNING_POLICY_OWNER,
        "capture_owner": "action_owned_external_read_summaries_only",
        "persistence_owner": "memory_conclusion_write_after_action",
        "allowed_source_families": [
            "knowledge_search",
            "web_browser",
            "task_system",
            "calendar",
            "cloud_drive",
        ],
        "allowed_read_operations": [
            "knowledge_search.search_web",
            "web_browser.read_page",
            "task_system.list_tasks",
            "calendar.read_availability",
            "cloud_drive.list_files",
        ],
        "capture_posture": "bounded_read_summary_only",
        "raw_payload_storage_allowed": False,
        "memory_layer": "semantic",
        "execution_bypass_allowed": False,
        "self_modifying_skill_learning_allowed": False,
        "reflection_follow_on_allowed": True,
    }
