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
        self.conclusion_updates: list[dict] = []
        self.user_preferences: dict = {}
        self.user_conclusions: list[dict] = []
        self.user_theta: dict | None = None

    async def get_recent_for_user(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.recent_memory[:limit]

    async def get_user_profile(self, user_id: str) -> dict | None:
        return self.user_profile

    async def get_user_runtime_preferences(self, user_id: str) -> dict:
        return self.user_preferences

    async def get_user_conclusions(self, user_id: str, limit: int = 3) -> list[dict]:
        return self.user_conclusions[:limit]

    async def get_user_theta(self, user_id: str) -> dict | None:
        return self.user_theta

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

    async def upsert_conclusion(self, **kwargs) -> dict:
        self.conclusion_updates.append(kwargs)
        return kwargs

    async def upsert_theta(self, **kwargs) -> dict:
        self.user_theta = kwargs
        return kwargs


class FakeTelegramClient:
    async def send_message(self, chat_id: int | str, text: str) -> dict:
        return {"ok": True}


class FakeOpenAIClient:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
    ) -> str | None:
        self.calls.append(
            {
                "user_text": user_text,
                "context_summary": context_summary,
                "role_name": role_name,
                "response_language": response_language,
                "response_style": response_style or "",
                "plan_goal": plan_goal,
                "motivation_mode": motivation_mode,
                "response_tone": response_tone,
                "collaboration_preference": collaboration_preference or "",
            }
        )
        return "Mocked OpenAI reply"


class FakeReflectionWorker:
    def __init__(self, enqueue_result: bool = True):
        self.enqueue_result = enqueue_result
        self.calls: list[dict[str, str]] = []

    async def enqueue(self, user_id: str, event_id: str) -> bool:
        self.calls.append({"user_id": user_id, "event_id": event_id})
        return self.enqueue_result


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
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
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
    assert result.reflection_triggered is True
    assert reflection.calls == [{"user_id": "u-1", "event_id": "evt-1"}]
    assert memory.profile_updates == []
    assert openai.calls[0]["response_style"] == ""
    assert openai.calls[0]["response_tone"] == "supportive"
    assert openai.calls[0]["collaboration_preference"] == ""


async def test_runtime_pipeline_uses_user_profile_language_for_ambiguous_turn_without_recent_memory() -> None:
    memory = FakeMemoryRepository(
        recent_memory=[],
        user_profile={"preferred_language": "pl", "language_confidence": 0.92, "language_source": "explicit_request"},
    )
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
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
    assert result.reflection_triggered is True
    assert memory.profile_updates == []
    assert openai.calls[0]["response_style"] == ""
    assert openai.calls[0]["response_tone"] == "supportive"
    assert openai.calls[0]["collaboration_preference"] == ""


async def test_runtime_pipeline_applies_structured_response_preference_from_conclusion_memory() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {"response_style": "structured", "response_style_source": "explicit_request"}
    memory.user_conclusions = [
        {"kind": "response_style", "content": "structured", "confidence": 0.95, "source": "explicit_request"}
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-3",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "How should we deploy this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-3"),
    )

    result = await runtime.run(event)

    assert result.expression.message == "Mocked OpenAI reply"
    assert openai.calls[0]["response_style"] == "structured"
    assert "Stable user preferences: prefers structured responses." in result.context.summary
    assert "format_response_as_bullets" in result.plan.steps
    assert result.reflection_triggered is True
    assert openai.calls[0]["response_tone"] == "analytical"
    assert openai.calls[0]["collaboration_preference"] == ""


async def test_runtime_pipeline_applies_concise_response_preference_to_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {"response_style": "concise", "response_style_source": "explicit_request"}
    memory.user_conclusions = [
        {"kind": "response_style", "content": "concise", "confidence": 0.95, "source": "explicit_request"}
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-4",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you review the current deployment issue?"},
        meta=EventMeta(user_id="u-1", trace_id="t-4"),
    )

    result = await runtime.run(event)

    assert result.expression.message == "Mocked OpenAI reply"
    assert openai.calls[0]["response_style"] == "concise"
    assert "keep_response_concise" in result.plan.steps
    assert result.reflection_triggered is True
    assert openai.calls[0]["response_tone"] == "analytical"
    assert openai.calls[0]["collaboration_preference"] == ""


async def test_runtime_pipeline_uses_preferred_role_from_semantic_memory_for_ambiguous_question() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "preferred_role": "analyst",
        "preferred_role_confidence": 0.76,
    }
    memory.user_conclusions = [
        {"kind": "preferred_role", "content": "analyst", "confidence": 0.76, "source": "background_reflection"}
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-5",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-5"),
    )

    result = await runtime.run(event)

    assert result.role.selected == "analyst"
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_theta_bias_when_no_preferred_role_exists() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_theta = {
        "support_bias": 0.12,
        "analysis_bias": 0.67,
        "execution_bias": 0.21,
    }
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-6",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-6"),
    )

    result = await runtime.run(event)

    assert result.role.selected == "analyst"
    assert result.reflection_triggered is True


async def test_runtime_pipeline_uses_theta_bias_for_motivation_and_planning_on_brief_turn() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_theta = {
        "support_bias": 0.14,
        "analysis_bias": 0.71,
        "execution_bias": 0.15,
    }
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-7",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "help me"},
        meta=EventMeta(user_id="u-1", trace_id="t-7"),
    )

    result = await runtime.run(event)

    assert result.motivation.mode == "analyze"
    assert result.role.selected == "analyst"
    assert "break_down_problem" in result.plan.steps or "favor_structured_reasoning" in result.plan.steps
    assert result.reflection_triggered is True
    assert result.expression.tone == "analytical"
    assert openai.calls[0]["response_tone"] == "analytical"


async def test_runtime_pipeline_uses_collaboration_preference_in_context_and_plan() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "collaboration_preference": "hands_on",
        "collaboration_preference_confidence": 0.73,
    }
    memory.user_conclusions = [
        {
            "kind": "collaboration_preference",
            "content": "hands_on",
            "confidence": 0.73,
            "source": "background_reflection",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-8",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-8"),
    )

    result = await runtime.run(event)

    assert "Stable user preferences: prefers concrete execution help." in result.context.summary
    assert result.plan.goal == "Move the requested task toward execution with the smallest concrete next step."
    assert "propose_execution_step" in result.plan.steps
    assert result.reflection_triggered is True
    assert result.expression.tone == "action-oriented"
    assert openai.calls[0]["collaboration_preference"] == "hands_on"
    assert openai.calls[0]["response_tone"] == "action-oriented"


async def test_runtime_pipeline_uses_guided_collaboration_preference_for_role_and_motivation() -> None:
    memory = FakeMemoryRepository(recent_memory=[])
    memory.user_preferences = {
        "collaboration_preference": "guided",
        "collaboration_preference_confidence": 0.73,
    }
    memory.user_conclusions = [
        {
            "kind": "collaboration_preference",
            "content": "guided",
            "confidence": 0.73,
            "source": "background_reflection",
        }
    ]
    action = ActionExecutor(memory_repository=memory, telegram_client=FakeTelegramClient())
    openai = FakeOpenAIClient()
    reflection = FakeReflectionWorker()
    runtime = RuntimeOrchestrator(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=openai),
        action_executor=action,
        memory_repository=memory,
        reflection_worker=reflection,
    )

    event = Event(
        event_id="evt-9",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with this?"},
        meta=EventMeta(user_id="u-1", trace_id="t-9"),
    )

    result = await runtime.run(event)

    assert result.motivation.mode == "analyze"
    assert result.role.selected == "mentor"
    assert result.plan.goal == "Explain the situation clearly with a guided step by step path."
    assert "break_down_problem" in result.plan.steps
    assert result.expression.tone == "guiding"
    assert openai.calls[0]["collaboration_preference"] == "guided"
    assert openai.calls[0]["response_tone"] == "guiding"
