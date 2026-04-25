from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.core.connector_execution import (
    connector_execution_baseline_snapshot,
    organizer_tool_stack_snapshot,
)
from app.core.web_knowledge_policy import web_knowledge_tooling_snapshot


def _tool_item(
    *,
    tool_id: str,
    label: str,
    category: str,
    kind: str,
    description: str,
    status: str,
    status_reason: str,
    enabled: bool,
    integral: bool,
    provider_ready: bool,
    provider_configured: bool,
    provider_name: str,
    user_toggle_allowed: bool,
    user_preference_supported: bool,
    link_required: bool = False,
    link_state: str = "not_applicable",
    capabilities: list[str] | None = None,
    next_actions: list[str] | None = None,
    source_of_truth: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": tool_id,
        "label": label,
        "category": category,
        "kind": kind,
        "description": description,
        "status": status,
        "status_reason": status_reason,
        "enabled": enabled,
        "integral": integral,
        "provider": {
            "name": provider_name,
            "ready": provider_ready,
            "configured": provider_configured,
        },
        "user_control": {
            "toggle_allowed": user_toggle_allowed,
            "preference_supported": user_preference_supported,
            "requested_enabled": enabled if user_preference_supported else None,
        },
        "link_required": link_required,
        "link_state": link_state,
        "capabilities": list(capabilities or []),
        "next_actions": list(next_actions or []),
        "source_of_truth": list(source_of_truth or []),
    }


def _group(
    *,
    group_id: str,
    title: str,
    description: str,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": group_id,
        "title": title,
        "description": description,
        "item_count": len(items),
        "items": items,
    }


def _provider_configured_from_ready_entry(entry: Mapping[str, Any]) -> bool:
    state = str(entry.get("state", "") or "").strip().lower()
    return bool(entry.get("ready", False)) or state != "credentials_missing"


def app_tools_overview_snapshot(
    *,
    settings,
    user_id: str,
    user_preferences: Mapping[str, Any] | None,
    user_profile: Mapping[str, Any] | None,
    telegram_channel: Mapping[str, Any] | None,
) -> dict[str, Any]:
    preferences = dict(user_preferences or {})
    profile = dict(user_profile or {})
    execution_baseline = connector_execution_baseline_snapshot(settings)
    organizer_stack = organizer_tool_stack_snapshot(settings)
    web_knowledge_tools = web_knowledge_tooling_snapshot(
        knowledge_search=execution_baseline["knowledge_search"]["search_web"],
        web_browser=execution_baseline["web_browser"]["read_page"],
    )
    telegram = dict(telegram_channel or {})

    telegram_provider_ready = bool(telegram.get("round_trip_ready", False))
    telegram_provider_configured = bool(telegram.get("bot_token_configured", False))
    telegram_requested_enabled = bool(preferences.get("telegram_enabled", False))
    telegram_linked = bool(str(profile.get("telegram_chat_id", "") or "").strip())
    telegram_link_pending = bool(str(profile.get("telegram_link_code", "") or "").strip())
    telegram_link_state = (
        "linked" if telegram_linked else "pending_confirmation" if telegram_link_pending else "not_linked"
    )
    telegram_status_reason = (
        "telegram_channel_linked_to_authenticated_user"
        if telegram_provider_ready and telegram_linked
        else "telegram_link_code_waiting_for_confirmation"
        if telegram_provider_ready and telegram_link_pending
        else "telegram_user_link_required_before_channel_can_be_used"
        if telegram_provider_ready
        else str(telegram.get("round_trip_hint", "configure_telegram_provider"))
    )
    telegram_next_actions = (
        ["telegram_link_confirmed"]
        if telegram_linked
        else ["send_link_code_to_configured_telegram_bot"]
        if telegram_link_pending
        else ["generate_link_code_and_confirm_from_telegram_chat"]
        if telegram_provider_ready
        else [str(telegram.get("round_trip_hint", "configure_telegram_provider"))]
    )
    clickup_requested_enabled = bool(preferences.get("clickup_enabled", False))
    google_calendar_requested_enabled = bool(preferences.get("google_calendar_enabled", False))
    google_drive_requested_enabled = bool(preferences.get("google_drive_enabled", False))

    clickup_entry = dict(execution_baseline["task_system"]["clickup_list_tasks"])
    google_calendar_entry = dict(execution_baseline["calendar"]["google_calendar_read_availability"])
    google_drive_entry = dict(execution_baseline["cloud_drive"]["google_drive_list_files"])
    search_entry = dict(web_knowledge_tools["knowledge_search"])
    browser_entry = dict(web_knowledge_tools["web_browser"])

    communication_items = [
        _tool_item(
            tool_id="internal_chat",
            label="Internal chat",
            category="communication",
            kind="channel",
            description="Integral first-party communication through the web product shell.",
            status="integral_active",
            status_reason="backend_owned_first_party_ui_channel",
            enabled=True,
            integral=True,
            provider_ready=True,
            provider_configured=True,
            provider_name="first_party_web",
            user_toggle_allowed=False,
            user_preference_supported=False,
            capabilities=["app.chat", "cookie_session", "first_party_auth"],
            source_of_truth=["/app/chat/message", "/app/me"],
        ),
        _tool_item(
            tool_id="telegram",
            label="Telegram",
            category="communication",
            kind="channel",
            description=(
                "External messaging channel backed by the existing Telegram bot, "
                "planned for explicit user linking with first-party auth identities."
            ),
            status=(
                "provider_ready"
                if telegram_provider_ready and telegram_linked
                else "provider_ready_link_required"
                if telegram_provider_ready
                else "provider_configuration_required"
            ),
            status_reason=telegram_status_reason,
            enabled=telegram_provider_ready and telegram_linked and telegram_requested_enabled,
            integral=False,
            provider_ready=telegram_provider_ready,
            provider_configured=telegram_provider_configured,
            provider_name="telegram",
            user_toggle_allowed=True,
            user_preference_supported=True,
            link_required=not telegram_linked,
            link_state=telegram_link_state,
            capabilities=["telegram.delivery", "telegram.ingress"],
            next_actions=telegram_next_actions,
            source_of_truth=["/health.conversation_channels.telegram"],
        ),
    ]
    communication_items[1]["user_control"]["requested_enabled"] = telegram_requested_enabled

    task_management_items = [
        _tool_item(
            tool_id="clickup",
            label="ClickUp",
            category="task_management",
            kind="integration",
            description="Current production task-system integration for listing and updating external tasks.",
            status=(
                "provider_ready" if bool(clickup_entry.get("ready", False)) else "provider_configuration_required"
            ),
            status_reason=str(clickup_entry.get("hint", "configure_clickup_provider")),
            enabled=bool(clickup_entry.get("ready", False)) and clickup_requested_enabled,
            integral=False,
            provider_ready=bool(clickup_entry.get("ready", False)),
            provider_configured=_provider_configured_from_ready_entry(clickup_entry),
            provider_name="clickup",
            user_toggle_allowed=True,
            user_preference_supported=True,
            capabilities=[
                "task_system.clickup_create_task",
                "task_system.clickup_list_tasks",
                "task_system.clickup_update_task",
            ],
            next_actions=[
                str(organizer_stack["activation_snapshot"]["provider_requirements"]["clickup"]["next_action"])
            ],
            source_of_truth=[
                "/health.connectors.execution_baseline.task_system.clickup_list_tasks",
                "/health.connectors.organizer_tool_stack",
            ],
        ),
        _tool_item(
            tool_id="trello",
            label="Trello",
            category="task_management",
            kind="integration",
            description="Planned task-management placeholder for a future bounded provider contract.",
            status="planned_placeholder",
            status_reason="provider_contract_not_implemented_yet",
            enabled=False,
            integral=False,
            provider_ready=False,
            provider_configured=False,
            provider_name="trello",
            user_toggle_allowed=False,
            user_preference_supported=False,
            next_actions=["freeze_trello_contract_before_provider_implementation"],
            source_of_truth=["task_plan_placeholder"],
        ),
        _tool_item(
            tool_id="nest",
            label="Nest app",
            category="task_management",
            kind="integration",
            description="Reserved placeholder for a future first-party custom task app once its backend contract exists.",
            status="planned_placeholder",
            status_reason="custom_provider_contract_not_implemented_yet",
            enabled=False,
            integral=False,
            provider_ready=False,
            provider_configured=False,
            provider_name="custom_nest",
            user_toggle_allowed=False,
            user_preference_supported=False,
            next_actions=["freeze_custom_app_contract_before_runtime_integration"],
            source_of_truth=["task_plan_placeholder"],
        ),
    ]
    task_management_items[0]["user_control"]["requested_enabled"] = clickup_requested_enabled

    knowledge_items = [
        _tool_item(
            tool_id="web_search",
            label="Web search",
            category="knowledge_and_web",
            kind="tool",
            description="Integral public web search capability available to the personality within bounded read-only policy.",
            status="integral_active",
            status_reason=str(search_entry.get("hint", "web_search_ready")),
            enabled=True,
            integral=True,
            provider_ready=bool(search_entry.get("ready", False)),
            provider_configured=True,
            provider_name=str(search_entry.get("provider", "duckduckgo_html")),
            user_toggle_allowed=False,
            user_preference_supported=False,
            capabilities=["knowledge_search.search_web", "knowledge_search.suggest_search"],
            source_of_truth=[
                "/health.connectors.execution_baseline.knowledge_search.search_web",
                "/health.connectors.web_knowledge_tools",
            ],
        ),
        _tool_item(
            tool_id="web_browser",
            label="Web browser",
            category="knowledge_and_web",
            kind="tool",
            description="Integral single-page reading capability used for bounded website review.",
            status="integral_active",
            status_reason=str(browser_entry.get("hint", "web_browser_ready")),
            enabled=True,
            integral=True,
            provider_ready=bool(browser_entry.get("ready", False)),
            provider_configured=True,
            provider_name=str(browser_entry.get("provider", "generic_http")),
            user_toggle_allowed=False,
            user_preference_supported=False,
            capabilities=["web_browser.read_page", "web_browser.suggest_page_review"],
            source_of_truth=[
                "/health.connectors.execution_baseline.web_browser.read_page",
                "/health.connectors.web_knowledge_tools",
            ],
        ),
    ]

    organizer_items = [
        _tool_item(
            tool_id="google_calendar",
            label="Google Calendar",
            category="calendar_and_files",
            kind="integration",
            description="Bounded calendar availability inspection provider.",
            status=(
                "provider_ready"
                if bool(google_calendar_entry.get("ready", False))
                else "provider_configuration_required"
            ),
            status_reason=str(google_calendar_entry.get("hint", "configure_google_calendar_provider")),
            enabled=bool(google_calendar_entry.get("ready", False)) and google_calendar_requested_enabled,
            integral=False,
            provider_ready=bool(google_calendar_entry.get("ready", False)),
            provider_configured=_provider_configured_from_ready_entry(google_calendar_entry),
            provider_name="google_calendar",
            user_toggle_allowed=True,
            user_preference_supported=True,
            capabilities=["calendar.google_calendar_read_availability"],
            next_actions=[
                str(
                    organizer_stack["activation_snapshot"]["provider_requirements"]["google_calendar"][
                        "next_action"
                    ]
                )
            ],
            source_of_truth=[
                "/health.connectors.execution_baseline.calendar.google_calendar_read_availability",
                "/health.connectors.organizer_tool_stack",
            ],
        ),
        _tool_item(
            tool_id="google_drive",
            label="Google Drive",
            category="calendar_and_files",
            kind="integration",
            description="Bounded file-space inspection provider for metadata listing.",
            status=(
                "provider_ready" if bool(google_drive_entry.get("ready", False)) else "provider_configuration_required"
            ),
            status_reason=str(google_drive_entry.get("hint", "configure_google_drive_provider")),
            enabled=bool(google_drive_entry.get("ready", False)) and google_drive_requested_enabled,
            integral=False,
            provider_ready=bool(google_drive_entry.get("ready", False)),
            provider_configured=_provider_configured_from_ready_entry(google_drive_entry),
            provider_name="google_drive",
            user_toggle_allowed=True,
            user_preference_supported=True,
            capabilities=["cloud_drive.google_drive_list_files"],
            next_actions=[
                str(organizer_stack["activation_snapshot"]["provider_requirements"]["google_drive"]["next_action"])
            ],
            source_of_truth=[
                "/health.connectors.execution_baseline.cloud_drive.google_drive_list_files",
                "/health.connectors.organizer_tool_stack",
            ],
        ),
    ]
    organizer_items[0]["user_control"]["requested_enabled"] = google_calendar_requested_enabled
    organizer_items[1]["user_control"]["requested_enabled"] = google_drive_requested_enabled

    groups = [
        _group(
            group_id="communication",
            title="Communication",
            description="Channels the personality can use to communicate with the user.",
            items=communication_items,
        ),
        _group(
            group_id="task_management",
            title="Task Management",
            description="External task systems and planned placeholders for future work management.",
            items=task_management_items,
        ),
        _group(
            group_id="knowledge_and_web",
            title="Knowledge and Web",
            description="Integral public-web capabilities that remain bounded and backend-owned.",
            items=knowledge_items,
        ),
        _group(
            group_id="calendar_and_files",
            title="Calendar and Files",
            description="Organizer-style connectors for bounded availability and file-space inspection.",
            items=organizer_items,
        ),
    ]
    all_items = [item for group in groups for item in group["items"]]

    return {
        "policy_owner": "app_tools_overview_contract",
        "user_id": user_id,
        "group_order": [group["id"] for group in groups],
        "groups": groups,
        "summary": {
            "total_groups": len(groups),
            "total_items": len(all_items),
            "integral_enabled_count": sum(1 for item in all_items if item["integral"] and item["enabled"]),
            "provider_ready_count": sum(1 for item in all_items if bool(item["provider"]["ready"])),
            "provider_blocked_count": sum(1 for item in all_items if not bool(item["provider"]["ready"])),
            "link_required_count": sum(1 for item in all_items if item["link_required"]),
            "planned_placeholder_count": sum(1 for item in all_items if item["status"] == "planned_placeholder"),
        },
    }
