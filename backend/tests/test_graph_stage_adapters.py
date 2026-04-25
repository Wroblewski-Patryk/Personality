from datetime import datetime, timezone

import pytest

from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.contracts import (
    ActionDelivery,
    CalendarSchedulingIntentDomainIntent,
    ConnectorPermissionGateOutput,
    ContextOutput,
    Event,
    EventMeta,
    IdentityOutput,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
)
from app.core.graph_adapters import GraphStageAdapters
from app.core.graph_state import GraphMemoryState, build_graph_state_seed
from app.expression.generator import ExpressionAgent
from app.identity.service import IdentityService
from app.motivation.engine import MotivationEngine


class _FakeOpenAIClient:
    async def generate_reply(
        self,
        user_text: str,
        context_summary: str,
        foreground_awareness_summary: str,
        role_name: str,
        response_language: str,
        response_style: str | None,
        plan_goal: str,
        motivation_mode: str,
        response_tone: str,
        collaboration_preference: str | None,
        identity_summary: str = "",
        current_turn_timestamp: str = "",
    ) -> str | None:
        return f"Mocked graph reply for: {user_text}"

    async def classify_affective_state(self, *, user_text: str, response_language: str) -> dict | None:
        return None


class _NoopMemoryRepository:
    pass


class _FakeTelegramClient:
    async def send_message(self, chat_id: int | str, text: str) -> dict:
        return {"ok": True}


def _event() -> Event:
    return Event(
        event_id="evt-graph-adapter-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "Can you help me with graph migration next steps?"},
        meta=EventMeta(user_id="u-1", trace_id="t-graph-adapter-1"),
    )


@pytest.mark.asyncio
async def test_graph_stage_adapters_run_existing_modules_with_graph_state() -> None:
    adapters = GraphStageAdapters(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=_FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=_NoopMemoryRepository(),
            telegram_client=_FakeTelegramClient(),
        ),
    )
    identity = IdentityService().build(user_profile=None, user_preferences={}, user_theta=None)
    state = build_graph_state_seed(_event()).model_copy(
        update={
            "memory": GraphMemoryState(
                episodic=[
                    {
                        "id": 7,
                        "event_id": "evt-prev",
                        "summary": (
                            "event=previous graph task; memory_kind=semantic; "
                            "memory_topics=graph,migration; response_language=en; action=success"
                        ),
                        "importance": 0.67,
                        "event_timestamp": datetime.now(timezone.utc),
                    }
                ],
                operational={
                    "user_profile": None,
                    "user_preferences": {},
                    "user_theta": None,
                },
            ),
            "identity": identity,
            "active_goals": [],
            "active_tasks": [],
            "active_goal_milestones": [],
            "goal_milestone_history": [],
            "goal_progress_history": [],
        }
    )

    state = adapters.run_perception(state)
    state = await adapters.run_affective_assessment(state)
    state = adapters.run_context(state)
    state = adapters.run_motivation(state)
    state = adapters.run_role(state)
    state = adapters.run_planning(state)
    state = await adapters.run_expression(state)
    assert state.action_delivery is not None
    assert state.action_delivery.channel == "api"
    state = await adapters.run_action(state)

    assert state.perception is not None
    assert state.context is not None
    assert state.motivation is not None
    assert state.role is not None
    assert state.plan is not None
    assert state.expression is not None
    assert state.action_delivery is not None
    assert state.action_delivery.channel == "api"
    assert state.action_result is not None
    assert state.action_result.status == "success"


@pytest.mark.asyncio
async def test_graph_stage_adapters_action_consumes_explicit_delivery_handoff() -> None:
    adapters = GraphStageAdapters(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=_FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=_NoopMemoryRepository(),
            telegram_client=_FakeTelegramClient(),
        ),
    )
    state = build_graph_state_seed(_event()).model_copy(
        update={
            "plan": PlanOutput(
                goal="reply",
                steps=["prepare_response"],
                needs_action=True,
                needs_response=True,
            ),
            "action_delivery": ActionDelivery(
                message="handoff message",
                tone="supportive",
                channel="api",
                language="en",
                chat_id=None,
            ),
        }
    )
    state = state.model_copy(update={"expression": None})
    state = await adapters.run_action(state)

    assert state.action_delivery is not None
    assert state.action_result is not None
    assert state.action_result.status == "success"


@pytest.mark.asyncio
async def test_graph_stage_adapters_expression_builds_connector_safe_delivery_envelope() -> None:
    adapters = GraphStageAdapters(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=_FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=_NoopMemoryRepository(),
            telegram_client=_FakeTelegramClient(),
        ),
    )
    state = build_graph_state_seed(_event()).model_copy(
        update={
            "identity": IdentityOutput(
                mission="Help the user move forward.",
                values=["clarity"],
                behavioral_style=["direct", "supportive"],
                boundaries=["no hidden side effects"],
                summary="Direct and supportive help.",
            ),
            "perception": PerceptionOutput(
                event_type="request",
                topic="calendar",
                topic_tags=["calendar", "planning"],
                intent="request_help",
                language="en",
                language_source="default",
                language_confidence=0.8,
                ambiguity=0.1,
                initial_salience=0.6,
            ),
            "context": ContextOutput(
                summary="User asked for schedule help.",
                related_goals=[],
                related_tags=["calendar"],
                risk_level=0.1,
            ),
            "motivation": MotivationOutput(
                importance=0.7,
                urgency=0.3,
                valence=0.1,
                arousal=0.4,
                mode="respond",
            ),
            "role": RoleOutput(selected="advisor", confidence=0.8),
            "plan": PlanOutput(
                goal="help with scheduling",
                steps=["prepare_response"],
                needs_action=True,
                needs_response=True,
                domain_intents=[
                    CalendarSchedulingIntentDomainIntent(
                        operation="create_event",
                        provider_hint="google_calendar",
                        mode="mutate_with_confirmation",
                        title_hint="team sync",
                        time_hint="tomorrow 10:00",
                    )
                ],
                connector_permission_gates=[
                    ConnectorPermissionGateOutput(
                        connector_kind="calendar",
                        provider_hint="google_calendar",
                        operation="create_event",
                        mode="mutate_with_confirmation",
                        requires_opt_in=True,
                        requires_confirmation=True,
                        allowed=False,
                        reason="explicit_user_confirmation_required",
                    )
                ],
            ),
        }
    )

    state = await adapters.run_expression(state)

    assert state.action_delivery is not None
    assert state.action_delivery.execution_envelope.connector_safe is True
    assert len(state.action_delivery.execution_envelope.connector_intents) == 1
    assert len(state.action_delivery.execution_envelope.connector_permission_gates) == 1
    assert state.action_delivery.execution_envelope.connector_intents[0].operation == "create_event"


def test_graph_stage_adapters_validate_required_state_fields() -> None:
    adapters = GraphStageAdapters(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=_FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=_NoopMemoryRepository(),
            telegram_client=_FakeTelegramClient(),
        ),
    )
    state = build_graph_state_seed(_event())

    with pytest.raises(ValueError, match="missing graph state fields: identity, perception"):
        adapters.run_context(state)


@pytest.mark.asyncio
async def test_graph_stage_adapters_action_requires_explicit_delivery_handoff() -> None:
    adapters = GraphStageAdapters(
        perception_agent=PerceptionAgent(),
        context_agent=ContextAgent(),
        motivation_engine=MotivationEngine(),
        role_agent=RoleAgent(),
        planning_agent=PlanningAgent(),
        expression_agent=ExpressionAgent(openai_client=_FakeOpenAIClient()),
        action_executor=ActionExecutor(
            memory_repository=_NoopMemoryRepository(),
            telegram_client=_FakeTelegramClient(),
        ),
    )
    state = build_graph_state_seed(_event()).model_copy(
        update={
            "plan": PlanOutput(
                goal="noop",
                steps=[],
                needs_action=True,
                needs_response=True,
            )
        }
    )

    with pytest.raises(ValueError, match="missing graph state fields: action_delivery"):
        await adapters.run_action(state)
