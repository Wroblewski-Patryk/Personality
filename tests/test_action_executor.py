from datetime import datetime, timezone

from app.core.action import ActionExecutor
from app.core.contracts import (
    ContextOutput,
    Event,
    EventMeta,
    ExpressionOutput,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
)


class FakeMemoryRepository:
    def __init__(self):
        self.profile_updates: list[dict] = []
        self.goal_updates: list[dict] = []
        self.task_updates: list[dict] = []
        self.active_goals: list[dict] = []

    async def write_episode(self, **kwargs) -> dict:
        return {
            "id": 1,
            "event_id": kwargs["event_id"],
            "timestamp": kwargs["event_timestamp"],
            "summary": kwargs["summary"],
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
        return payload


class FakeTelegramClient:
    async def send_message(self, chat_id: int | str, text: str) -> dict:
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


def _plan() -> PlanOutput:
    return PlanOutput(goal="reply", steps=["reply"], needs_action=False, needs_response=True)


def _expression() -> ExpressionOutput:
    return ExpressionOutput(message="hello", tone="supportive", channel="api", language="en")


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
        action_result=await executor.execute(_plan(), _event("deploy the fix to production now"), _expression()),
        expression=_expression(),
    )

    assert "memory_kind=semantic" in record.summary
    assert "memory_topics=general,deploy,production,fix" in record.summary
    assert "preference_update=" in record.summary
    assert "motivation=respond" in record.summary
    assert "role=executor" in record.summary
    assert "plan_steps=reply" in record.summary
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
        action_result=await executor.execute(_plan(), _event("ok"), _expression()),
        expression=_expression(),
    )

    assert "memory_kind=continuity" in record.summary
    assert "memory_topics=general" in record.summary
    assert "preference_update=" in record.summary
    assert "motivation=respond" in record.summary
    assert "role=advisor" in record.summary
    assert "plan_steps=reply" in record.summary
    assert memory_repository.profile_updates == [
        {
            "user_id": "u-1",
            "language_code": "en",
            "confidence": 0.8,
            "source": "keyword_signal",
        }
    ]


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
        action_result=await executor.execute(_plan(), _event("ok"), _expression()),
        expression=_expression(),
    )

    assert memory_repository.profile_updates == []


async def test_persist_episode_marks_explicit_response_style_preference_for_reflection() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    record = await executor.persist_episode(
        event=_event("Please answer briefly from now on."),
        perception=_perception(["general"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _event("Please answer briefly from now on."), _expression()),
        expression=_expression(),
    )

    assert "preference_update=response_style:concise" in record.summary


async def test_persist_episode_marks_explicit_collaboration_preference_for_reflection() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    record = await executor.persist_episode(
        event=_event("Can you walk me through this step by step?"),
        perception=_perception(["general"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _event("Can you walk me through this step by step?"), _expression()),
        expression=_expression(),
    )

    assert "collaboration_update=guided" in record.summary


async def test_persist_episode_upserts_explicit_goal_signal() -> None:
    memory_repository = FakeMemoryRepository()
    executor = ActionExecutor(memory_repository=memory_repository, telegram_client=FakeTelegramClient())

    record = await executor.persist_episode(
        event=_event("My goal is to ship the MVP this week."),
        perception=_perception(["general", "mvp"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _event("My goal is to ship the MVP this week."), _expression()),
        expression=_expression(),
    )

    assert "goal_update=ship the MVP this week" in record.summary
    assert memory_repository.goal_updates[0]["name"] == "ship the MVP this week"
    assert memory_repository.goal_updates[0]["priority"] == "high"


async def test_persist_episode_upserts_task_signal_and_links_matching_goal() -> None:
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

    record = await executor.persist_episode(
        event=_event("I need to ship the MVP deployment blocker."),
        perception=_perception(["general", "mvp", "deploy"]),
        context=_context(),
        motivation=_motivation(),
        role=_role(),
        plan=_plan(),
        action_result=await executor.execute(_plan(), _event("I need to ship the MVP deployment blocker."), _expression()),
        expression=_expression(),
    )

    assert "task_update=ship the MVP deployment blocker" in record.summary
    assert memory_repository.task_updates[0]["name"] == "ship the MVP deployment blocker"
    assert memory_repository.task_updates[0]["goal_id"] == 7
    assert memory_repository.task_updates[0]["status"] == "blocked"
