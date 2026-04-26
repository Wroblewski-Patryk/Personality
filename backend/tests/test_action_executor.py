from datetime import datetime, timezone

import pytest

from app.core.action import ActionExecutor
from app.core.action_delivery import build_action_delivery_execution_envelope
from app.core.contracts import (
    ActionDelivery,
    ActionDeliveryConnectorIntent,
    ActionDeliveryExecutionEnvelope,
    CancelPlannedWorkItemDomainIntent,
    CalendarSchedulingIntentDomainIntent,
    CompletePlannedWorkItemDomainIntent,
    ConnectedDriveAccessDomainIntent,
    ConnectorCapabilityDiscoveryDomainIntent,
    ConnectorPermissionGateOutput,
    ContextOutput,
    Event,
    EventMeta,
    ExpressionOutput,
    ExternalTaskSyncDomainIntent,
    KnowledgeSearchDomainIntent,
    MaintainRelationDomainIntent,
    MaintainTaskStatusDomainIntent,
    MotivationOutput,
    NoopDomainIntent,
    PerceptionOutput,
    PlanOutput,
    PromoteInferredGoalDomainIntent,
    PromoteInferredTaskDomainIntent,
    ProactiveDeliveryGuardOutput,
    ReschedulePlannedWorkItemDomainIntent,
    RoleOutput,
    UpsertPlannedWorkItemDomainIntent,
    UpdateProactivePreferenceDomainIntent,
    UpdateProactiveStateDomainIntent,
    UpdateCollaborationPreferenceDomainIntent,
    UpdateResponseStyleDomainIntent,
    UpdateTaskStatusDomainIntent,
    UpsertGoalDomainIntent,
    UpsertTaskDomainIntent,
    WebBrowserAccessDomainIntent,
)


class FakeMemoryRepository:
    def __init__(self):
        self.profile_updates: list[dict] = []
        self.goal_updates: list[dict] = []
        self.task_updates: list[dict] = []
        self.active_goals: list[dict] = []
        self.active_tasks: list[dict] = []
        self.active_planned_work: list[dict] = []
        self.task_status_updates: list[dict] = []
        self.planned_work_updates: list[dict] = []
        self.planned_work_status_updates: list[dict] = []
        self.relation_updates: list[dict] = []
        self.conclusion_updates: list[dict] = []
        self.written_episodes: list[dict] = []
        self.semantic_embedding_updates: list[dict] = []

    async def write_episode(self, **kwargs) -> dict:
        self.written_episodes.append(kwargs)
        return {
            "id": 1,
            "event_id": kwargs["event_id"],
            "timestamp": kwargs["event_timestamp"],
            "summary": kwargs["summary"],
            "payload": kwargs["payload"],
            "importance": kwargs["importance"],
        }

    async def upsert_user_profile_language(self, **kwargs) -> dict:
        self.profile_updates.append(kwargs)
        return kwargs

    async def upsert_active_goal(self, **kwargs) -> dict:
        payload = {"id": len(self.goal_updates) + 1, **kwargs}
        self.goal_updates.append(payload)
        self.active_goals.append(payload)
        return payload

    async def get_active_goals(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.active_goals[:limit]

    async def upsert_active_task(self, **kwargs) -> dict:
        payload = {"id": len(self.task_updates) + 1, **kwargs}
        self.task_updates.append(payload)
        self.active_tasks.append(payload)
        return payload

    async def get_active_tasks(self, user_id: str, *, goal_ids: list[int] | None = None, limit: int = 5) -> list[dict]:
        return self.active_tasks[:limit]

    async def get_active_planned_work(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        task_ids: list[int] | None = None,
        limit: int = 8,
    ) -> list[dict]:
        rows = [item for item in self.active_planned_work if item.get("status") in {"pending", "due", "snoozed"}]
        return rows[:limit]

    async def update_task_status(self, *, task_id: int, status: str) -> dict | None:
        for task in self.active_tasks:
            if int(task["id"]) == task_id:
                task["status"] = status
                payload = {"task_id": task_id, "status": status}
                self.task_status_updates.append(payload)
                return task
        return None

    async def upsert_planned_work_item(self, **kwargs) -> dict:
        payload = {"id": len(self.active_planned_work) + 1, "status": "pending", **kwargs}
        self.planned_work_updates.append(payload)
        self.active_planned_work.append(payload)
        return payload

    async def reschedule_planned_work_item(self, *, work_id: int, **kwargs) -> dict | None:
        for item in self.active_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "pending"
                item.update(kwargs)
                payload = {"work_id": work_id, "status": item["status"], **kwargs}
                self.planned_work_status_updates.append(payload)
                return item
        return None

    async def cancel_planned_work_item(self, *, work_id: int) -> dict | None:
        for item in self.active_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "cancelled"
                payload = {"work_id": work_id, "status": item["status"]}
                self.planned_work_status_updates.append(payload)
                return item
        return None

    async def complete_planned_work_item(self, *, work_id: int) -> dict | None:
        for item in self.active_planned_work:
            if int(item["id"]) == work_id:
                item["status"] = "completed"
                payload = {"work_id": work_id, "status": item["status"]}
                self.planned_work_status_updates.append(payload)
                return item
        return None

    async def upsert_relation(self, **kwargs) -> dict:
        payload = {"id": len(self.relation_updates) + 1, **kwargs}
        self.relation_updates.append(payload)
        return payload

    async def upsert_conclusion(self, **kwargs) -> dict:
        self.conclusion_updates.append(kwargs)
        return kwargs

    async def upsert_semantic_embedding(self, **kwargs) -> dict:
        self.semantic_embedding_updates.append(kwargs)
        return {"id": len(self.semantic_embedding_updates), **kwargs}


class FakeTelegramClient:
    def __init__(self, *, error: Exception | None = None):
        self.error = error
        self.calls: list[dict[str, int | str | None]] = []

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        *,
        parse_mode: str | None = None,
    ) -> dict:
        self.calls.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})
        if self.error is not None:
            raise self.error
        return {"ok": True}


class FakeClickUpTaskClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def create_task(self, *, name: str, description: str = "") -> dict:
        self.calls.append({"name": name, "description": description})
        if self.error is not None:
            raise self.error
        return {"id": "clk_123", "name": name}

    async def list_tasks(self, *, limit: int = 10) -> list[dict]:
        self.calls.append({"operation": "list_tasks", "limit": str(limit)})
        if self.error is not None:
            raise self.error
        return [
            {"id": "clk_1", "name": "Release checklist"},
            {"id": "clk_2", "name": "Docs sync"},
        ]

    async def update_task(self, *, task_id: str, status: str) -> dict:
        self.calls.append({"operation": "update_task", "task_id": task_id, "status": status})
        if self.error is not None:
            raise self.error
        return {"id": task_id, "name": "Release checklist", "status": status}


class FakeGoogleCalendarClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def read_availability(self, *, time_hint: str, slot_minutes: int = 60, slot_limit: int = 3) -> dict:
        self.calls.append(
            {
                "time_hint": time_hint,
                "slot_minutes": str(slot_minutes),
                "slot_limit": str(slot_limit),
            }
        )
        if self.error is not None:
            raise self.error
        return {
            "window_start": "2026-04-23T08:00:00+00:00",
            "window_end": "2026-04-23T18:00:00+00:00",
            "time_zone": "UTC",
            "busy_window_count": 2,
            "free_slot_preview": [
                "2026-04-23T09:00:00+00:00 -> 2026-04-23T10:00:00+00:00",
                "2026-04-23T13:00:00+00:00 -> 2026-04-23T14:00:00+00:00",
            ],
        }


class FakeGoogleDriveClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def list_files(self, *, file_hint: str, limit: int = 5) -> list[dict]:
        self.calls.append({"file_hint": file_hint, "limit": str(limit)})
        if self.error is not None:
            raise self.error
        return [
            {
                "id": "drv_1",
                "name": "Release notes",
                "mime_type": "application/vnd.google-apps.document",
                "modified_time": "2026-04-22T07:00:00Z",
            },
            {
                "id": "drv_2",
                "name": "Deployment checklist",
                "mime_type": "text/markdown",
                "modified_time": "2026-04-21T12:00:00Z",
            },
        ]


class FakeDuckDuckGoSearchClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def search_web(self, *, query: str, limit: int = 5) -> list[dict]:
        self.calls.append({"query": query, "limit": str(limit)})
        if self.error is not None:
            raise self.error
        return [
            {
                "title": "Release notes",
                "url": "https://example.com/release-notes",
                "snippet": "Changelog summary",
                "rank": "1",
            },
            {
                "title": "Deployment guide",
                "url": "https://example.com/deploy",
                "snippet": "Deployment details",
                "rank": "2",
            },
        ]


class FakeGenericHttpPageClient:
    def __init__(self, *, ready: bool = True, error: Exception | None = None):
        self.ready = ready
        self.error = error
        self.calls: list[dict[str, str]] = []

    async def read_page(self, *, url: str, excerpt_length: int = 500) -> dict:
        self.calls.append({"url": url, "excerpt_length": str(excerpt_length)})
        if self.error is not None:
            raise self.error
        return {
            "url": url,
            "title": "Release notes",
            "content_type": "text/html",
            "excerpt": "Important changes.",
            "truncated": "false",
        }


def _event(text: str) -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _context() -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=0.1)


def _motivation() -> MotivationOutput:
    return MotivationOutput(
        importance=0.7,
        urgency=0.3,
        valence=0.1,
        arousal=0.4,
        mode="respond",
    )


def _plan(*, domain_intents=None, proactive_delivery_guard: ProactiveDeliveryGuardOutput | None = None) -> PlanOutput:
    return PlanOutput(
        goal="reply",
        steps=["reply"],
        needs_action=False,
        needs_response=True,
        domain_intents=domain_intents if domain_intents is not None else [NoopDomainIntent()],
        proactive_delivery_guard=proactive_delivery_guard,
    )


def _expression() -> ExpressionOutput:
    return ExpressionOutput(message="hello", tone="supportive", channel="api", language="en")


def _delivery(
    *,
    channel: str = "api",
    chat_id: int | str | None = None,
    execution_envelope: ActionDeliveryExecutionEnvelope | None = None,
) -> ActionDelivery:
    return ActionDelivery(
        message="hello",
        tone="supportive",
        channel=channel,
        language="en",
        chat_id=chat_id,
        execution_envelope=execution_envelope or ActionDeliveryExecutionEnvelope(),
    )


def _perception(topic_tags: list[str], language_source: str = "keyword_signal") -> PerceptionOutput:
    return PerceptionOutput(
        event_type="statement",
        topic=topic_tags[0] if topic_tags else "general",
        topic_tags=topic_tags,
        intent="share_information",
        language="en",
        language_source=language_source,
        language_confidence=0.8,
        ambiguity=0.1,
        initial_salience=0.5,
    )


def _role(selected: str = "advisor") -> RoleOutput:
    return RoleOutput(selected=selected, confidence=0.8)


@pytest.mark.asyncio()
async def test_persist_episode_captures_tool_grounded_learning_from_read_results() -> None:
    memory = FakeMemoryRepository()
    action = ActionExecutor(
        memory_repository=memory,
        telegram_client=FakeTelegramClient(),
        knowledge_search_client=FakeDuckDuckGoSearchClient(),
        web_browser_client=FakeGenericHttpPageClient(),
    )

    plan = _plan(
        domain_intents=[
            KnowledgeSearchDomainIntent(
                operation="search_web",
                provider_hint="duckduckgo_html",
                mode="read_only",
                query_hint="release notes deployment risks",
            ),
            WebBrowserAccessDomainIntent(
                operation="read_page",
                provider_hint="generic_http",
                mode="read_only",
                page_hint="https://example.com/release-notes",
            ),
        ]
    )
    action_result = await action.execute(plan, _delivery())

    await action.persist_episode(
        _event("Search and read page"),
        _perception(["release"]),
        _context(),
        _motivation(),
        _role(),
        plan,
        action_result,
        _expression(),
    )

    conclusion_kinds = [row["kind"] for row in memory.conclusion_updates]
    assert "tool_grounded_search_knowledge" in conclusion_kinds
    assert "tool_grounded_page_knowledge" in conclusion_kinds
    assert any(
        "release notes deployment risks" in str(row.get("content", ""))
        for row in memory.conclusion_updates
        if row["kind"] == "tool_grounded_search_knowledge"
    )


async def test_execute_uses_api_delivery_contract_for_api_responses() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=telegram_client)

    result = await executor.execute(_plan(), _delivery(channel="api"))

    assert result.status == "success"
    assert result.actions == ["api_response"]
    assert telegram_client.calls == []


async def test_execute_uses_telegram_delivery_contract_for_telegram_responses() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=telegram_client)

    result = await executor.execute(_plan(), _delivery(channel="telegram", chat_id=123456))

    assert result.status == "success"
    assert result.actions == ["send_telegram_message"]
    assert telegram_client.calls == [{"chat_id": 123456, "text": "hello", "parse_mode": None}]


async def test_execute_appends_bounded_web_results_to_delivery_message() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        knowledge_search_client=FakeDuckDuckGoSearchClient(),
        web_browser_client=FakeGenericHttpPageClient(),
    )
    plan = _plan(
        domain_intents=[
            KnowledgeSearchDomainIntent(
                operation="search_web",
                provider_hint="duckduckgo_html",
                mode="read_only",
                query_hint="weather in berlin today",
            ),
            WebBrowserAccessDomainIntent(
                operation="read_page",
                provider_hint="generic_http",
                mode="read_only",
                page_hint="luckysparrow.ch",
            ),
        ]
    )

    result = await executor.execute(plan, _delivery(channel="telegram", chat_id=123456))

    assert result.status == "success"
    assert result.actions == ["duckduckgo_search_web", "generic_http_read_page", "send_telegram_message"]
    delivered_text = str(telegram_client.calls[-1]["text"])
    assert "Web lookup:" in delivered_text
    assert "Page review:" in delivered_text
    assert "https://luckysparrow.ch" in delivered_text


async def test_execute_fails_when_telegram_delivery_contract_has_no_chat_id() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=telegram_client)

    result = await executor.execute(_plan(), _delivery(channel="telegram"))

    assert result.status == "fail"
    assert result.actions == []
    assert "chat_id is missing" in result.notes
    assert telegram_client.calls == []


async def test_execute_handles_telegram_delivery_exception_as_fail_result() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient(error=TimeoutError("upstream timeout"))
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=telegram_client)

    result = await executor.execute(_plan(), _delivery(channel="telegram", chat_id=123456))

    assert result.status == "fail"
    assert result.actions == ["send_telegram_message"]
    assert "TimeoutError" in result.notes
    assert "upstream timeout" in result.notes
    assert telegram_client.calls == [{"chat_id": 123456, "text": "hello", "parse_mode": None}]


async def test_execute_runs_provider_backed_clickup_task_creation_before_delivery() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    clickup_client = FakeClickUpTaskClient()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        clickup_task_client=clickup_client,
    )

    plan = _plan(
        domain_intents=[
            ExternalTaskSyncDomainIntent(
                operation="create_task",
                provider_hint="clickup",
                mode="mutate_with_confirmation",
                task_hint="Create launch checklist in ClickUp",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="api",
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "success"
    assert result.actions == ["clickup_create_task", "api_response"]
    assert "ClickUp task created (clk_123)" in result.notes
    assert clickup_client.calls == [
        {
            "name": "Create launch checklist in ClickUp",
            "description": "Created by AION connector execution from intent: Create launch checklist in ClickUp",
        }
    ]


async def test_execute_fails_when_provider_backed_clickup_execution_errors() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    clickup_client = FakeClickUpTaskClient(error=RuntimeError("clickup unavailable"))
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        clickup_task_client=clickup_client,
    )

    plan = _plan(
        domain_intents=[
            ExternalTaskSyncDomainIntent(
                operation="create_task",
                provider_hint="clickup",
                mode="mutate_with_confirmation",
                task_hint="Create launch checklist in ClickUp",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="telegram",
            chat_id=123456,
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "fail"
    assert result.actions == ["clickup_create_task"]
    assert "clickup unavailable" in result.notes
    assert telegram_client.calls == []


async def test_execute_runs_provider_backed_clickup_task_read_before_delivery() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    clickup_client = FakeClickUpTaskClient()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        clickup_task_client=clickup_client,
    )

    plan = _plan(
        domain_intents=[
            ExternalTaskSyncDomainIntent(
                operation="list_tasks",
                provider_hint="clickup",
                mode="read_only",
                task_hint="current sprint",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="api",
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "success"
    assert result.actions == ["clickup_list_tasks", "api_response"]
    assert "ClickUp task read returned: Release checklist, Docs sync." in result.notes
    assert clickup_client.calls == [{"operation": "list_tasks", "limit": "5"}]


async def test_execute_runs_provider_backed_clickup_task_update_before_delivery() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    clickup_client = FakeClickUpTaskClient()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        clickup_task_client=clickup_client,
    )

    plan = _plan(
        domain_intents=[
            ExternalTaskSyncDomainIntent(
                operation="update_task",
                provider_hint="clickup",
                mode="mutate_with_confirmation",
                task_hint="release checklist",
                status_hint="done",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="api",
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "success"
    assert result.actions == ["clickup_update_task", "api_response"]
    assert "ClickUp task updated (clk_1)" in result.notes
    assert clickup_client.calls == [
        {"operation": "list_tasks", "limit": "10"},
        {"operation": "update_task", "task_id": "clk_1", "status": "complete"},
    ]


async def test_execute_runs_provider_backed_google_calendar_read_before_delivery() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    calendar_client = FakeGoogleCalendarClient()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        google_calendar_client=calendar_client,
    )

    plan = _plan(
        domain_intents=[
            CalendarSchedulingIntentDomainIntent(
                operation="read_availability",
                provider_hint="google_calendar",
                mode="read_only",
                title_hint="team sync",
                time_hint="tomorrow morning",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="api",
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "success"
    assert result.actions == ["google_calendar_read_availability", "api_response"]
    assert "Google Calendar availability read" in result.notes
    assert "Top free slots:" in result.notes
    assert calendar_client.calls == [
        {
            "time_hint": "tomorrow morning",
            "slot_minutes": "60",
            "slot_limit": "3",
        }
    ]


async def test_execute_fails_when_provider_backed_google_calendar_read_errors() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    calendar_client = FakeGoogleCalendarClient(error=RuntimeError("calendar unavailable"))
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        google_calendar_client=calendar_client,
    )

    plan = _plan(
        domain_intents=[
            CalendarSchedulingIntentDomainIntent(
                operation="read_availability",
                provider_hint="google_calendar",
                mode="read_only",
                title_hint="team sync",
                time_hint="next week",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="telegram",
            chat_id=123456,
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "fail"
    assert result.actions == ["google_calendar_read_availability"]
    assert "calendar unavailable" in result.notes
    assert telegram_client.calls == []


async def test_execute_runs_provider_backed_google_drive_metadata_read_before_delivery() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    drive_client = FakeGoogleDriveClient()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        google_drive_client=drive_client,
    )

    plan = _plan(
        domain_intents=[
            ConnectedDriveAccessDomainIntent(
                operation="list_files",
                provider_hint="google_drive",
                mode="read_only",
                file_hint="release notes",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="api",
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "success"
    assert result.actions == ["google_drive_list_files", "api_response"]
    assert "Google Drive metadata read returned:" in result.notes
    assert "Release notes [application/vnd.google-apps.document] (drv_1)" in result.notes
    assert drive_client.calls == [{"file_hint": "release notes", "limit": "5"}]


async def test_execute_runs_provider_backed_web_search_before_delivery() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    search_client = FakeDuckDuckGoSearchClient()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        knowledge_search_client=search_client,
    )

    plan = _plan(
        domain_intents=[
            KnowledgeSearchDomainIntent(
                operation="search_web",
                provider_hint="duckduckgo_html",
                mode="read_only",
                query_hint="latest release notes",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="api",
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "success"
    assert result.actions == ["duckduckgo_search_web", "api_response"]
    assert "Web search returned: Release notes (https://example.com/release-notes)" in result.notes
    assert search_client.calls == [{"query": "latest release notes", "limit": "5"}]


async def test_execute_runs_provider_backed_browser_page_read_before_delivery() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    browser_client = FakeGenericHttpPageClient()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        web_browser_client=browser_client,
    )

    plan = _plan(
        domain_intents=[
            WebBrowserAccessDomainIntent(
                operation="read_page",
                provider_hint="generic_http",
                mode="read_only",
                page_hint="Read page https://example.com/release-notes now.",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="api",
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "success"
    assert result.actions == ["generic_http_read_page", "api_response"]
    assert "Browser page read returned: Release notes [text/html] https://example.com/release-notes." in result.notes
    assert browser_client.calls == [{"url": "https://example.com/release-notes", "excerpt_length": "500"}]


async def test_execute_fails_when_provider_backed_google_drive_metadata_read_errors() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    drive_client = FakeGoogleDriveClient(error=RuntimeError("drive unavailable"))
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=telegram_client,
        google_drive_client=drive_client,
    )

    plan = _plan(
        domain_intents=[
            ConnectedDriveAccessDomainIntent(
                operation="list_files",
                provider_hint="google_drive",
                mode="read_only",
                file_hint="release notes",
            )
        ]
    )

    result = await executor.execute(
        plan,
        _delivery(
            channel="telegram",
            chat_id=123456,
            execution_envelope=build_action_delivery_execution_envelope(plan),
        ),
    )

    assert result.status == "fail"
    assert result.actions == ["google_drive_list_files"]
    assert "drive unavailable" in result.notes
    assert telegram_client.calls == []


async def test_execute_blocks_connector_intent_when_mode_violates_shared_policy() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=telegram_client)

    result = await executor.execute(
        _plan(
            domain_intents=[
                ExternalTaskSyncDomainIntent(
                    operation="list_tasks",
                    provider_hint="clickup",
                    mode="mutate_with_confirmation",
                    task_hint="sprint board",
                )
            ]
        ),
        _delivery(channel="telegram", chat_id=123456),
    )

    assert result.status == "fail"
    assert result.actions == []
    assert "Connector policy guardrail blocked inconsistent intent posture" in result.notes
    assert "external_task_sync_intent:list_tasks" in result.notes
    assert telegram_client.calls == []


async def test_execute_blocks_web_knowledge_intent_when_mode_violates_shared_policy() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=telegram_client)

    result = await executor.execute(
        _plan(
            domain_intents=[
                KnowledgeSearchDomainIntent(
                    operation="search_web",
                    provider_hint="generic",
                    mode="mutate_with_confirmation",
                    query_hint="latest release notes",
                ),
                WebBrowserAccessDomainIntent(
                    operation="read_page",
                    provider_hint="generic",
                    mode="mutate_with_confirmation",
                    page_hint="https://example.com/changelog",
                ),
            ]
        ),
        _delivery(channel="telegram", chat_id=123456),
    )

    assert result.status == "fail"
    assert result.actions == []
    assert "Connector policy guardrail blocked inconsistent intent posture" in result.notes
    assert "knowledge_search_intent:search_web" in result.notes
    assert "web_browser_access_intent:read_page" in result.notes
    assert telegram_client.calls == []


async def test_execute_fails_when_action_delivery_envelope_drifts_from_plan() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=telegram_client)

    result = await executor.execute(
        _plan(
            domain_intents=[
                CalendarSchedulingIntentDomainIntent(
                    operation="create_event",
                    provider_hint="google_calendar",
                    mode="mutate_with_confirmation",
                    title_hint="team sync",
                    time_hint="tomorrow 10:00",
                )
            ]
        ),
        _delivery(
            channel="telegram",
            chat_id=123456,
            execution_envelope=ActionDeliveryExecutionEnvelope(
                connector_safe=True,
                connector_intents=[
                    ActionDeliveryConnectorIntent(
                        connector_kind="calendar",
                        provider_hint="google_calendar",
                        operation="suggest_slots",
                        mode="suggestion_only",
                        allowed=True,
                        requires_confirmation=False,
                        reason="suggestion_or_read_only_allowed",
                    )
                ],
                connector_permission_gates=[
                    ConnectorPermissionGateOutput(
                        connector_kind="calendar",
                        provider_hint="google_calendar",
                        operation="suggest_slots",
                        mode="suggestion_only",
                        requires_opt_in=True,
                        requires_confirmation=False,
                        allowed=True,
                        reason="suggestion_or_read_only_allowed",
                    )
                ],
            ),
        ),
    )

    assert result.status == "fail"
    assert result.actions == []
    assert "Action delivery envelope drift detected" in result.notes
    assert telegram_client.calls == []


async def test_execute_defers_when_proactive_delivery_guard_disallows_outreach() -> None:
    memory_repository = FakeMemoryRepository()
    telegram_client = FakeTelegramClient()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=telegram_client)

    result = await executor.execute(
        _plan(
            proactive_delivery_guard=ProactiveDeliveryGuardOutput(
                allowed=False,
                reason="opt_in_required",
            )
        ),
        _delivery(channel="telegram", chat_id=123456),
    )

    assert result.status == "noop"
    assert result.actions == []
    assert "opt_in_required" in result.notes
    assert telegram_client.calls == []


async def test_persist_episode_marks_specific_request_as_semantic_memory() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    record = await executor.persist_episode(
        event=_event("deploy the fix to production now"),
        perception=_perception(["general", "deploy", "production"]),
        context=_context(),
        motivation=_motivation(),
        role=_role("executor"),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert "User said 'deploy the fix to production now'." in record.summary
    assert record.payload["memory_kind"] == "semantic"
    assert record.payload["memory_topics"] == ["general", "deploy", "production", "fix"]
    assert record.payload["affect_label"] == "neutral"
    assert record.payload["affect_needs_support"] is False
    assert record.payload["affect_source"] == "deterministic_placeholder"
    assert record.payload["preference_update"] == ""
    assert record.payload["motivation"] == "respond"
    assert record.payload["role"] == "executor"
    assert record.payload["plan_steps"] == ["reply"]
    assert memory_repository.written_episodes[0]["payload"] == record.payload
    assert memory_repository.profile_updates == [
        {
            "user_id": "u-1",
            "language_code": "en",
            "confidence": 0.8,
            "source": "keyword_signal",
        }
    ]


async def test_persist_episode_marks_short_follow_up_as_continuity_memory() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    record = await executor.persist_episode(
        event=_event("ok"),
        perception=_perception(["general"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert "User said 'ok'." in record.summary
    assert record.payload["memory_kind"] == "continuity"
    assert record.payload["memory_topics"] == ["general"]
    assert record.payload["affect_label"] == "neutral"
    assert record.payload["affect_needs_support"] is False
    assert record.payload["preference_update"] == ""
    assert record.payload["motivation"] == "respond"
    assert record.payload["role"] == "advisor"
    assert record.payload["plan_steps"] == ["reply"]
    assert memory_repository.profile_updates == [
        {
            "user_id": "u-1",
            "language_code": "en",
            "confidence": 0.8,
            "source": "keyword_signal",
        }
    ]


async def test_persist_episode_upserts_semantic_embedding_when_vector_retrieval_is_enabled() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    await executor.persist_episode(
        event=_event("deploy the fix"),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert len(memory_repository.semantic_embedding_updates) == 1
    update = memory_repository.semantic_embedding_updates[0]
    assert isinstance(update["embedding"], list)
    assert len(update["embedding"]) == 32
    assert update["embedding_model"] == "deterministic-v1"
    assert update["embedding_dimensions"] == 32
    assert update["metadata"]["embedding_status"] == "materialized_on_write"
    assert update["metadata"]["embedding_refresh_mode"] == "on_write"
    assert update["metadata"]["embedding_provider_requested"] == "deterministic"
    assert update["metadata"]["embedding_provider_effective"] == "deterministic"
    assert update["metadata"]["embedding_provider_hint"] == "deterministic_baseline"


async def test_persist_episode_skips_semantic_embedding_when_vector_retrieval_is_disabled() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=FakeTelegramClient(),
        semantic_vector_enabled=False,
    )

    await executor.persist_episode(
        event=_event("deploy the fix"),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert memory_repository.semantic_embedding_updates == []


async def test_persist_episode_falls_back_to_deterministic_embedding_when_non_deterministic_provider_is_requested() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=FakeTelegramClient(),
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=16,
    )

    await executor.persist_episode(
        event=_event("deploy the fix"),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert len(memory_repository.semantic_embedding_updates) == 1
    update = memory_repository.semantic_embedding_updates[0]
    assert isinstance(update["embedding"], list)
    assert len(update["embedding"]) == 16
    assert update["embedding_model"] == "deterministic-v1"
    assert update["embedding_dimensions"] == 16
    assert update["metadata"]["embedding_status"] == "materialized_on_write"
    assert update["metadata"]["embedding_refresh_mode"] == "on_write"
    assert update["metadata"]["embedding_provider_requested"] == "openai"
    assert update["metadata"]["embedding_provider_effective"] == "deterministic"
    assert (
        update["metadata"]["embedding_provider_hint"]
        == "openai_api_key_missing_fallback_deterministic"
    )
    assert update["metadata"]["embedding_model_requested"] == "text-embedding-3-small"
    assert update["metadata"]["embedding_model_effective"] == "deterministic-v1"


async def test_persist_episode_marks_episodic_embedding_pending_when_manual_refresh_mode_is_enabled() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=FakeTelegramClient(),
        embedding_refresh_mode="manual",
    )

    await executor.persist_episode(
        event=_event("deploy the fix"),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert len(memory_repository.semantic_embedding_updates) == 1
    update = memory_repository.semantic_embedding_updates[0]
    assert update["embedding"] is None
    assert update["metadata"]["embedding_status"] == "pending_manual_refresh"
    assert update["metadata"]["embedding_refresh_mode"] == "manual"


async def test_persist_episode_skips_episodic_embedding_when_source_kind_is_not_enabled() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(
        memory_repository=memory_repository,
        telegram_client=FakeTelegramClient(),
        semantic_vector_enabled=True,
        embedding_source_kinds=("semantic", "affective"),
    )

    await executor.persist_episode(
        event=_event("deploy the fix"),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert memory_repository.semantic_embedding_updates == []


async def test_persist_episode_skips_profile_update_for_derived_language_signal() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    await executor.persist_episode(
        event=_event("ok"),
        perception=_perception(["general"], language_source="user_profile"),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert memory_repository.profile_updates == []


async def test_persist_episode_marks_explicit_response_style_preference_for_reflection() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(domain_intents=[UpdateResponseStyleDomainIntent(style="concise")])
    record = await executor.persist_episode(
        event=_event("Please answer briefly from now on."),
        perception=_perception(["general"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["preference_update"] == "response_style:concise"


async def test_persist_episode_marks_explicit_collaboration_preference_for_reflection() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(domain_intents=[UpdateCollaborationPreferenceDomainIntent(preference="guided")])
    record = await executor.persist_episode(
        event=_event("Can you walk me through this step by step?"),
        perception=_perception(["general"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["collaboration_update"] == "guided"


async def test_persist_episode_upserts_goal_from_domain_intent() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            UpsertGoalDomainIntent(
                name="ship the MVP this week",
                description="User-declared goal: ship the MVP this week",
                priority="high",
                goal_type="operational",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("My goal is to ship the MVP this week."),
        perception=_perception(["general", "mvp"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["goal_update"] == "ship the MVP this week"
    assert memory_repository.goal_updates[0]["name"] == "ship the MVP this week"
    assert memory_repository.goal_updates[0]["priority"] == "high"


async def test_persist_episode_upserts_task_from_domain_intent_and_links_matching_goal() -> None:
    memory_repository = FakeMemoryRepository()
    memory_repository.active_goals = [
        {
            "id": 7,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            UpsertTaskDomainIntent(
                name="ship the MVP deployment blocker",
                description="User-declared task: ship the MVP deployment blocker",
                priority="high",
                status="blocked",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("I need to ship the MVP deployment blocker."),
        perception=_perception(["general", "mvp", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["task_update"] == "ship the MVP deployment blocker"
    assert memory_repository.task_updates[0]["name"] == "ship the MVP deployment blocker"
    assert memory_repository.task_updates[0]["goal_id"] == 7
    assert memory_repository.task_updates[0]["status"] == "blocked"


async def test_persist_episode_updates_matching_task_status_from_domain_intent() -> None:
    memory_repository = FakeMemoryRepository()
    memory_repository.active_tasks = [
        {
            "id": 5,
            "user_id": "u-1",
            "goal_id": None,
            "name": "fix deployment blocker",
            "description": "User-declared task: fix deployment blocker",
            "priority": "high",
            "status": "blocked",
        }
    ]
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            UpdateTaskStatusDomainIntent(
                status="done",
                task_hint="deployment blocker",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("I fixed the deployment blocker."),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["task_status_update"] == "fix deployment blocker:done"
    assert memory_repository.task_status_updates == [{"task_id": 5, "status": "done"}]


async def test_persist_episode_upserts_and_updates_planned_work_from_domain_intents() -> None:
    memory_repository = FakeMemoryRepository()
    memory_repository.active_goals = [
        {
            "id": 7,
            "user_id": "u-1",
            "name": "ship the MVP this week",
            "description": "User-declared goal: ship the MVP this week",
            "priority": "high",
            "status": "active",
            "goal_type": "operational",
        }
    ]
    memory_repository.active_tasks = [
        {
            "id": 5,
            "user_id": "u-1",
            "goal_id": 7,
            "name": "send the release summary tomorrow",
            "description": "User-declared task: send the release summary tomorrow",
            "priority": "medium",
            "status": "todo",
        }
    ]
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    upsert_plan = _plan(
        domain_intents=[
            UpsertPlannedWorkItemDomainIntent(
                work_kind="reminder",
                summary="send the release summary tomorrow",
                preferred_at=datetime(2026, 4, 25, 9, 0, tzinfo=timezone.utc),
                channel_hint="telegram",
                provenance="explicit_user_request",
            )
        ]
    )
    upsert_record = await executor.persist_episode(
        event=_event("Remind me to send the release summary tomorrow."),
        perception=_perception(["general", "release"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=upsert_plan,
        action_result=await executor.execute(upsert_plan, _delivery()),
        expression=_expression(),
    )

    status_plan = _plan(
        domain_intents=[
            ReschedulePlannedWorkItemDomainIntent(
                work_id=1,
                preferred_at=datetime(2026, 4, 26, 8, 30, tzinfo=timezone.utc),
            ),
            CancelPlannedWorkItemDomainIntent(work_id=1),
            CompletePlannedWorkItemDomainIntent(work_id=1),
        ]
    )
    status_record = await executor.persist_episode(
        event=_event("Please reschedule, then cancel, then mark the release summary reminder done."),
        perception=_perception(["general", "release"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=status_plan,
        action_result=await executor.execute(status_plan, _delivery()),
        expression=_expression(),
    )

    assert upsert_record.payload["planned_work_update"] == "reminder:send the release summary tomorrow:pending"
    assert memory_repository.planned_work_updates[0]["goal_id"] == 7
    assert memory_repository.planned_work_updates[0]["task_id"] == 5
    assert status_record.payload["planned_work_status_update"] == "send the release summary tomorrow:completed:completed"
    assert memory_repository.planned_work_status_updates[0]["work_id"] == 1
    assert memory_repository.planned_work_status_updates[-1]["status"] == "completed"


async def test_persist_episode_promotes_inferred_goal_from_typed_domain_intent() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            PromoteInferredGoalDomainIntent(
                name="stabilize deployment migration failures",
                description="Inferred goal from repeated execution evidence: stabilize deployment migration failures",
                priority="high",
                goal_type="tactical",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("Again still blocked by deployment migration failures."),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["goal_update"] == "stabilize deployment migration failures"
    assert memory_repository.goal_updates[0]["description"].startswith("Inferred goal from repeated execution evidence:")


async def test_persist_episode_promotes_inferred_task_from_typed_domain_intent() -> None:
    memory_repository = FakeMemoryRepository()
    memory_repository.active_goals = [
        {
            "id": 7,
            "user_id": "u-1",
            "name": "stabilize deployment migration failures",
            "description": "Inferred goal from repeated execution evidence: stabilize deployment migration failures",
            "priority": "high",
            "status": "active",
            "goal_type": "tactical",
        }
    ]
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            PromoteInferredTaskDomainIntent(
                name="deployment migration failures staging",
                description="Inferred task from repeated execution evidence: deployment migration failures staging",
                priority="high",
                status="blocked",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("Again still blocked by deployment migration failures in staging."),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["task_update"] == "deployment migration failures staging"
    assert memory_repository.task_updates[0]["description"].startswith("Inferred task from repeated execution evidence:")
    assert memory_repository.task_updates[0]["goal_id"] == 7


async def test_persist_episode_maintains_task_status_from_typed_maintenance_intent() -> None:
    memory_repository = FakeMemoryRepository()
    memory_repository.active_tasks = [
        {
            "id": 5,
            "user_id": "u-1",
            "goal_id": None,
            "name": "deployment migration failures staging",
            "description": "Inferred task from repeated execution evidence: deployment migration failures staging",
            "priority": "high",
            "status": "todo",
        }
    ]
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            MaintainTaskStatusDomainIntent(
                status="blocked",
                task_hint="deployment migration failures",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("Again still blocked by deployment migration failures in staging."),
        perception=_perception(["general", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["task_status_update"] == "deployment migration failures staging:blocked"
    assert memory_repository.task_status_updates == [{"task_id": 5, "status": "blocked"}]


async def test_persist_episode_does_not_infer_domain_updates_without_domain_intents() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(domain_intents=[NoopDomainIntent()])
    record = await executor.persist_episode(
        event=_event("My goal is to ship the MVP this week."),
        perception=_perception(["general", "mvp"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["goal_update"] == ""
    assert record.payload["task_update"] == ""
    assert record.payload["task_status_update"] == ""
    assert memory_repository.goal_updates == []
    assert memory_repository.task_updates == []
    assert memory_repository.task_status_updates == []


async def test_persist_episode_tracks_calendar_and_external_task_connector_intents() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            CalendarSchedulingIntentDomainIntent(
                operation="create_event",
                provider_hint="google_calendar",
                mode="mutate_with_confirmation",
                title_hint="team sync",
                time_hint="tomorrow 10:00",
            ),
            ExternalTaskSyncDomainIntent(
                operation="create_task",
                provider_hint="clickup",
                mode="mutate_with_confirmation",
                task_hint="deploy rollback checklist",
            ),
        ]
    )
    record = await executor.persist_episode(
        event=_event("Please schedule it on calendar and create task in ClickUp."),
        perception=_perception(["general", "calendar", "task_sync"]),
        context=_context(),
        motivation=_motivation(),
        role=_role("executor"),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["calendar_connector_update"] == "create_event:mutate_with_confirmation:google_calendar"
    assert record.payload["task_connector_update"] == "create_task:mutate_with_confirmation:clickup"
    assert (
        record.payload["calendar_connector_guardrail"]
        == "external_mutation_requires_confirmation:blocked_until_confirmation"
    )
    assert (
        record.payload["task_connector_guardrail"]
        == "external_mutation_requires_confirmation:blocked_until_confirmation"
    )
    assert record.payload["domain_intents"] == [
        "calendar_scheduling_intent",
        "external_task_sync_intent",
    ]


async def test_persist_episode_tracks_connected_drive_connector_intent() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            ConnectedDriveAccessDomainIntent(
                operation="upload_file",
                provider_hint="google_drive",
                mode="mutate_with_confirmation",
                file_hint="release-notes.md",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("Upload release notes to Google Drive."),
        perception=_perception(["general", "drive"]),
        context=_context(),
        motivation=_motivation(),
        role=_role("executor"),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["drive_connector_update"] == "upload_file:mutate_with_confirmation:google_drive"
    assert (
        record.payload["drive_connector_guardrail"]
        == "external_mutation_requires_confirmation:blocked_until_confirmation"
    )
    assert record.payload["domain_intents"] == ["connected_drive_access_intent"]


async def test_persist_episode_tracks_connector_capability_discovery_intent() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            ConnectorCapabilityDiscoveryDomainIntent(
                connector_kind="task_system",
                provider_hint="clickup",
                requested_capability="task_sync",
                evidence="repeated_unmet_need",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("Can we connect ClickUp for task sync?"),
        perception=_perception(["general", "connectors"]),
        context=_context(),
        motivation=_motivation(),
        role=_role("analyst"),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["connector_expansion_update"] == "task_system:clickup:task_sync"
    assert (
        record.payload["connector_expansion_guardrail"]
        == "proposal_only_no_external_access:allowed_without_external_access"
    )
    assert record.payload["domain_intents"] == ["connector_capability_discovery_intent"]


async def test_persist_episode_maintains_relation_from_typed_domain_intent() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            MaintainRelationDomainIntent(
                relation_type="delivery_reliability",
                relation_value="high_trust",
                confidence=0.86,
                source="planning_intent",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("You can be more direct with me now."),
        perception=_perception(["general", "trust"]),
        context=_context(),
        motivation=_motivation(),
        role=_role("advisor"),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["relation_update"] == "delivery_reliability:high_trust:global:global"
    assert memory_repository.relation_updates == [
        {
            "id": 1,
            "user_id": "u-1",
            "relation_type": "delivery_reliability",
            "relation_value": "high_trust",
            "confidence": 0.86,
            "source": "planning_intent",
            "supporting_event_id": "evt-1",
            "scope_type": "global",
            "scope_key": "global",
            "evidence_count": 1,
            "decay_rate": 0.02,
        }
    ]


async def test_persist_episode_updates_proactive_state_from_typed_domain_intent() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            UpdateProactiveStateDomainIntent(
                state="delivery_ready",
                trigger="task_blocked",
                reason="delivery_ready",
                output_type="warning",
                mode="strong",
            )
        ]
    )
    record = await executor.persist_episode(
        event=Event(
            event_id="evt-1",
            source="scheduler",
            subsource="proactive_tick",
            timestamp=datetime.now(timezone.utc),
            payload={"text": "scheduler proactive tick", "chat_id": 123456},
            meta=EventMeta(user_id="u-1", trace_id="t-1"),
        ),
        perception=_perception(["general", "proactive"]),
        context=_context(),
        motivation=_motivation(),
        role=_role("advisor"),
        plan=plan,
        action_result=await executor.execute(plan, _delivery(channel="telegram", chat_id=123456)),
        expression=ExpressionOutput(message="hello", tone="supportive", channel="telegram", language="en"),
    )

    assert record.payload["proactive_state_update"] == "delivery_ready:task_blocked:delivery_ready"
    assert record.payload["event_visibility"] == "internal"
    assert record.payload["assistant_visibility"] == "transcript"
    assert record.payload["action_actions"] == ["send_telegram_message"]
    assert memory_repository.conclusion_updates == [
        {
            "user_id": "u-1",
            "kind": "proactive_outreach_state",
            "content": "delivery_ready",
            "confidence": 0.9,
            "source": "proactive_planning",
            "supporting_event_id": "evt-1",
        },
        {
            "user_id": "u-1",
            "kind": "proactive_outreach_trigger",
            "content": "task_blocked",
            "confidence": 0.9,
            "source": "proactive_planning",
            "supporting_event_id": "evt-1",
        },
    ]


async def test_persist_episode_marks_api_user_turn_as_transcript_visible() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    record = await executor.persist_episode(
        event=_event("hello there"),
        perception=_perception(["general"]),
        context=_context(),
        motivation=_motivation(),
        role=_role("advisor"),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _delivery()),
        expression=_expression(),
    )

    assert record.payload["event_visibility"] == "transcript"
    assert record.payload["assistant_visibility"] == "transcript"


async def test_persist_episode_updates_proactive_preference_from_typed_domain_intent() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    plan = _plan(
        domain_intents=[
            UpdateProactivePreferenceDomainIntent(
                opt_in=True,
                source="explicit_request",
            )
        ]
    )
    record = await executor.persist_episode(
        event=_event("Remind me to send the release summary tomorrow."),
        perception=_perception(["general", "planning"]),
        context=_context(),
        motivation=_motivation(),
        role=_role("advisor"),
        plan=plan,
        action_result=await executor.execute(plan, _delivery()),
        expression=_expression(),
    )

    assert record.payload["proactive_preference_update"] == "proactive_opt_in:true"
    assert memory_repository.conclusion_updates == [
        {
            "user_id": "u-1",
            "kind": "proactive_opt_in",
            "content": "true",
            "confidence": 0.95,
            "source": "explicit_request",
            "supporting_event_id": "evt-1",
        }
    ]
