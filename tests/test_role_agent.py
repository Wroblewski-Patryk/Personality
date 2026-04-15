from datetime import datetime, timezone

from app.agents.role import RoleAgent
from app.core.contracts import ContextOutput, Event, EventMeta, PerceptionOutput


def _event(text: str) -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _perception(event_type: str, topic: str, intent: str) -> PerceptionOutput:
    return PerceptionOutput(
        event_type=event_type,
        topic=topic,
        intent=intent,
        ambiguity=0.1,
        initial_salience=0.5,
    )


def _context(risk_level: float = 0.1) -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=risk_level)


def test_role_agent_uses_friend_for_emotional_language() -> None:
    result = RoleAgent().run(
        event=_event("I feel stressed and tired today"),
        perception=_perception("statement", "general", "share_information"),
        context=_context(),
    )

    assert result.selected == "friend"


def test_role_agent_uses_analyst_for_planning_topics() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me plan the rollout?"),
        perception=_perception("question", "planning", "request_help"),
        context=_context(),
    )

    assert result.selected == "analyst"


def test_role_agent_uses_executor_for_direct_action_request() -> None:
    result = RoleAgent().run(
        event=_event("deploy the app to production"),
        perception=_perception("statement", "general", "share_information"),
        context=_context(),
    )

    assert result.selected == "executor"


def test_role_agent_uses_mentor_for_general_questions() -> None:
    result = RoleAgent().run(
        event=_event("How should I approach this bug?"),
        perception=_perception("question", "general", "request_help"),
        context=_context(),
    )

    assert result.selected == "mentor"


def test_role_agent_handles_polish_executor_request() -> None:
    result = RoleAgent().run(
        event=_event("wdroż poprawkę na produkcję"),
        perception=_perception("statement", "general", "share_information"),
        context=_context(),
    )

    assert result.selected == "executor"
