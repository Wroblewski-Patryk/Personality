from datetime import datetime, timezone

from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.contracts import Event, EventMeta
from app.core.runtime import RuntimeOrchestrator
from app.expression.generator import ExpressionAgent
from app.motivation.engine import MotivationEngine


class FakeMemoryRepository:
    def __init__(self, recent_memory: list[dict] | None = None, user_profile: dict | None = None):
        self.recent_memory = recent_memory or []
        self.user_profile = user_profile
        self.profile_updates: list[dict] = []

    async def get_recent_for_user(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.recent_memory[:limit]

    async def get_user_profile(self, user_id: str) -> dict | None:
        return self.user_profile

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


class FakeOpenAIClient:
    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        role_name: str,
        response_language: str,
        plan_goal: str,
        motivation_mode: str,
    ) -> str | None:
        return "Mocked OpenAI reply"


async def test_runtime_pipeline_api_source() -> None:
    memory = FakeMemoryRepository(
        recent_memory=[
            {
                "id": 7,
                "event_id": "evt-prev",
                "summary": (
                    "event=previous hello; memory_kind=continuity; memory_topics=previous,hello; response_language=en; context=old context; "
                    "plan_goal=reply; action=success; expression=Earlier reply"
                ),
                "importance": 0.6,
                "event_timestamp": datetime.now(timezone.utc),
            }
        ]
    )
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
    )

    event = Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello"},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )

    result = await runtime.run(event)

    assert result.action_result.status == "success"
    assert "previous hello" in result.context.summary
    assert "Earlier reply" in result.context.summary
    assert result.perception.language == "en"
    assert result.perception.language_source == "recent_memory"
    assert "general" in result.perception.topic_tags
    assert result.role.selected == "advisor"
    assert result.motivation.mode == "respond"
    assert result.plan.steps == ["interpret_event", "review_context", "prepare_response"]
    assert result.expression.message == "Mocked OpenAI reply"
    assert result.expression.language == "en"
    assert result.memory_record is not None
    assert "memory_kind=continuity" in result.memory_record.summary
    assert "memory_topics=general,hello" in result.memory_record.summary
    assert "response_language=en" in result.memory_record.summary
    assert result.reflection_triggered is False
    assert memory.profile_updates == []


async def test_runtime_pipeline_uses_user_profile_language_for_ambiguous_turn_without_recent_memory() -> None:
    memory = FakeMemoryRepository(
        recent_memory=[],
        user_profile={"preferred_language": "pl", "language_confidence": 0.92, "language_source": "explicit_request"},
    )
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=FakeOpenAIClient()),
        action_executor=action,
        memory_repository=memory,
    )

    event = Event(
        event_id="evt-2",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "ok"},
        meta=EventMeta(user_id="u-1", trace_id="t-2"),
    )

    result = await runtime.run(event)

    assert result.perception.language == "pl"
    assert result.perception.language_source == "user_profile"
    assert result.expression.language == "pl"
    assert result.context.related_tags == ["general", "language:pl"]
    assert memory.profile_updates == []
