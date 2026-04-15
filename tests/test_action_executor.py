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
    assert "role=executor" in record.summary
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
    assert "role=advisor" in record.summary
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
