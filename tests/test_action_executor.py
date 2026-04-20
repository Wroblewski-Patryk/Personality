from datetime import datetime, timezone

from app.core.action import ActionExecutor
from app.core.contracts import (
    ActionDelivery,
    CalendarSchedulingIntentDomainIntent,
    ConnectedDriveAccessDomainIntent,
    ConnectorCapabilityDiscoveryDomainIntent,
    ContextOutput,
    Event,
    EventMeta,
    ExpressionOutput,
    ExternalTaskSyncDomainIntent,
    MotivationOutput,
    NoopDomainIntent,
    PerceptionOutput,
    PlanOutput,
    ProactiveDeliveryGuardOutput,
    RoleOutput,
    UpdateCollaborationPreferenceDomainIntent,
    UpdateResponseStyleDomainIntent,
    UpdateTaskStatusDomainIntent,
    UpsertGoalDomainIntent,
    UpsertTaskDomainIntent,
)


class FakeMemoryRepository:
    def __init__(self):
        self.profile_updates: list[dict] = []
        self.goal_updates: list[dict] = []
        self.task_updates: list[dict] = []
        self.active_goals: list[dict] = []
        self.active_tasks: list[dict] = []
        self.task_status_updates: list[dict] = []
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

    async def get_active_tasks(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.active_tasks[:limit]

    async def update_task_status(self, *, task_id: int, status: str) -> dict | None:
        for task in self.active_tasks:
            if int(task["id"]) == task_id:
                task["status"] = status
                payload = {"task_id": task_id, "status": status}
                self.task_status_updates.append(payload)
                return task
        return None

    async def upsert_semantic_embedding(self, **kwargs) -> dict:
        self.semantic_embedding_updates.append(kwargs)
        return {"id": len(self.semantic_embedding_updates), **kwargs}


class FakeTelegramClient:
    def __init__(self, *, error: Exception | None = None):
        self.error = error
        self.calls: list[dict[str, int | str]] = []

    async def send_message(self, chat_id: int | str, text: str) -> dict:
        self.calls.append({"chat_id": chat_id, "text": text})
        if self.error is not None:
            raise self.error
        return {"ok": True}


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


def _delivery(*, channel: str = "api", chat_id: int | str | None = None) -> ActionDelivery:
    return ActionDelivery(message="hello", tone="supportive", channel=channel, language="en", chat_id=chat_id)


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
    assert telegram_client.calls == [{"chat_id": 123456, "text": "hello"}]


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
    assert telegram_client.calls == [{"chat_id": 123456, "text": "hello"}]


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
        == "provider_not_implemented_fallback_deterministic"
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
    assert record.payload["domain_intents"] == ["connector_capability_discovery_intent"]
