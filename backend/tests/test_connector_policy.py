from datetime import datetime, timezone

from app.agents.planning import PlanningAgent
from app.core.connector_read_policy import connector_read_baseline_snapshot
from app.core.connector_policy import (
    build_connector_permission_gate,
    connector_guardrail_snapshot,
    resolve_connector_capability_discovery_policy,
    resolve_connector_operation_policy,
)
from app.core.contracts import (
    CalendarSchedulingIntentDomainIntent,
    ConnectedDriveAccessDomainIntent,
    ContextOutput,
    Event,
    EventMeta,
    ExternalTaskSyncDomainIntent,
    KnowledgeSearchDomainIntent,
    WebBrowserAccessDomainIntent,
    MotivationOutput,
    RoleOutput,
)


def _event(text: str) -> Event:
    return Event(
        event_id="evt-policy-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-policy", trace_id="t-policy"),
    )


def _context() -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=0.1)


def test_connector_operation_policy_defines_internal_vs_external_baseline() -> None:
    calendar_create = resolve_connector_operation_policy("calendar", "create_event")
    task_link = resolve_connector_operation_policy("task_system", "link_internal_task")
    drive_read = resolve_connector_operation_policy("cloud_drive", "read_document")
    search_read = resolve_connector_operation_policy("knowledge_search", "search_web")
    browser_read = resolve_connector_operation_policy("web_browser", "read_page")

    assert calendar_create.mode == "mutate_with_confirmation"
    assert calendar_create.requires_confirmation is True
    assert calendar_create.allowed_without_external_access is False

    assert task_link.mode == "suggestion_only"
    assert task_link.requires_confirmation is False
    assert task_link.allowed_without_external_access is True

    assert drive_read.mode == "read_only"
    assert drive_read.requires_confirmation is False
    assert drive_read.allowed_without_external_access is True

    assert search_read.mode == "read_only"
    assert search_read.requires_opt_in is False
    assert search_read.allowed_without_external_access is True

    assert browser_read.mode == "read_only"
    assert browser_read.requires_opt_in is False
    assert browser_read.allowed_without_external_access is True


def test_connector_capability_discovery_policy_stays_suggestion_only() -> None:
    policy = resolve_connector_capability_discovery_policy("task_system", "task_sync")

    assert policy.operation == "discover_task_sync"
    assert policy.mode == "suggestion_only"
    assert policy.requires_opt_in is False
    assert policy.allowed_without_external_access is True
    assert policy.policy_reason == "proposal_only_no_external_access"


def test_build_connector_permission_gate_uses_shared_policy_outputs() -> None:
    gate = build_connector_permission_gate(
        ExternalTaskSyncDomainIntent(
            operation="list_tasks",
            provider_hint="clickup",
            mode="read_only",
            task_hint="sprint board",
        )
    )

    assert gate.connector_kind == "task_system"
    assert gate.operation == "list_tasks"
    assert gate.mode == "read_only"
    assert gate.allowed is True
    assert gate.requires_confirmation is False
    assert gate.reason == "suggestion_or_read_only_allowed"

    search_gate = build_connector_permission_gate(
        KnowledgeSearchDomainIntent(
            operation="search_web",
            provider_hint="generic",
            mode="read_only",
            query_hint="release notes",
        )
    )
    browser_gate = build_connector_permission_gate(
        WebBrowserAccessDomainIntent(
            operation="read_page",
            provider_hint="generic",
            mode="read_only",
            page_hint="https://example.com/release-notes",
        )
    )

    assert search_gate.connector_kind == "knowledge_search"
    assert search_gate.operation == "search_web"
    assert search_gate.allowed is True
    assert search_gate.requires_opt_in is False
    assert browser_gate.connector_kind == "web_browser"
    assert browser_gate.operation == "read_page"
    assert browser_gate.allowed is True
    assert browser_gate.requires_opt_in is False


def test_connector_read_baseline_selects_clickup_task_list_as_next_live_read_path() -> None:
    snapshot = connector_read_baseline_snapshot()

    assert snapshot["policy_owner"] == "connector_read_execution_baseline"
    selected = snapshot["selected_live_read_path"]
    assert selected["connector_kind"] == "cloud_drive"
    assert selected["provider"] == "google_drive"
    assert selected["operation"] == "list_files"
    assert selected["execution_mode"] == "provider_backed_next"
    assert (
        snapshot["deferred_families"]["calendar"]
        == "current_live_read_path_already_implemented_through_google_calendar_read_availability"
    )


def test_connector_guardrail_snapshot_distinguishes_blocked_vs_allowed_posture() -> None:
    blocked = connector_guardrail_snapshot(
        CalendarSchedulingIntentDomainIntent(
            operation="create_event",
            provider_hint="google_calendar",
            mode="mutate_with_confirmation",
            title_hint="team sync",
            time_hint="tomorrow 10:00",
        )
    )
    allowed = connector_guardrail_snapshot(
        ConnectedDriveAccessDomainIntent(
            operation="read_document",
            provider_hint="google_drive",
            mode="read_only",
            file_hint="runbook",
        )
    )

    assert blocked == "external_mutation_requires_confirmation:blocked_until_confirmation"
    assert allowed == "read_only_operator_preview:allowed_without_external_access"


def test_planning_agent_uses_shared_connector_policy_for_non_mutating_intents() -> None:
    planner = PlanningAgent()
    motivation = MotivationOutput(
        importance=0.72,
        urgency=0.34,
        valence=0.0,
        arousal=0.38,
        mode="analyze",
    )
    role = RoleOutput(selected="advisor", confidence=0.8)

    calendar_result = planner.run(
        event=_event("When can we use the calendar for a meeting next week?"),
        context=_context(),
        motivation=motivation,
        role=role,
    )
    calendar_intent = next(
        intent
        for intent in calendar_result.domain_intents
        if isinstance(intent, CalendarSchedulingIntentDomainIntent)
    )
    assert calendar_intent.operation == "read_availability"
    assert calendar_intent.provider_hint == "google_calendar"
    assert calendar_intent.mode == resolve_connector_operation_policy(
        "calendar",
        "read_availability",
    ).mode

    task_result = planner.run(
        event=_event("List tasks in ClickUp for this sprint."),
        context=_context(),
        motivation=motivation,
        role=role,
    )
    task_intent = next(
        intent
        for intent in task_result.domain_intents
        if isinstance(intent, ExternalTaskSyncDomainIntent)
    )
    assert task_intent.operation == "list_tasks"
    assert task_intent.mode == resolve_connector_operation_policy(
        "task_system",
        "list_tasks",
    ).mode

    drive_result = planner.run(
        event=_event("Suggest how to organize files in Google Drive."),
        context=_context(),
        motivation=motivation,
        role=role,
    )
    drive_intent = next(
        intent
        for intent in drive_result.domain_intents
        if isinstance(intent, ConnectedDriveAccessDomainIntent)
    )
    assert drive_intent.operation == "suggest_file_plan"
    assert drive_intent.mode == resolve_connector_operation_policy(
        "cloud_drive",
        "suggest_file_plan",
    ).mode

    search_result = planner.run(
        event=_event("Please search the web for the latest release notes."),
        context=_context(),
        motivation=motivation,
        role=role,
    )
    search_intent = next(
        intent
        for intent in search_result.domain_intents
        if isinstance(intent, KnowledgeSearchDomainIntent)
    )
    assert search_intent.operation == "search_web"
    assert search_intent.provider_hint == "duckduckgo_html"
    assert search_intent.mode == resolve_connector_operation_policy(
        "knowledge_search",
        "search_web",
    ).mode

    browser_result = planner.run(
        event=_event("Read page https://example.com/changelog in the browser."),
        context=_context(),
        motivation=motivation,
        role=role,
    )
    browser_intent = next(
        intent
        for intent in browser_result.domain_intents
        if isinstance(intent, WebBrowserAccessDomainIntent)
    )
    assert browser_intent.operation == "read_page"
    assert browser_intent.provider_hint == "generic_http"
    assert browser_intent.mode == resolve_connector_operation_policy(
        "web_browser",
        "read_page",
    ).mode

    update_result = planner.run(
        event=_event("Mark the Release checklist task as done in ClickUp."),
        context=_context(),
        motivation=motivation,
        role=role,
    )
    update_intent = next(
        intent
        for intent in update_result.domain_intents
        if isinstance(intent, ExternalTaskSyncDomainIntent)
    )
    assert update_intent.operation == "update_task"
    assert update_intent.provider_hint == "clickup"
    assert update_intent.status_hint == "done"
