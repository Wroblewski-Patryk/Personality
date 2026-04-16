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


def _perception(event_type: str, topic: str, intent: str, language: str = "en") -> PerceptionOutput:
    return PerceptionOutput(
        event_type=event_type,
        topic=topic,
        topic_tags=[topic],
        intent=intent,
        language=language,
        language_source="keyword_signal",
        language_confidence=0.8,
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
        event=_event("wdroz poprawke na produkcje"),
        perception=_perception("statement", "general", "share_information", language="pl"),
        context=_context(),
    )

    assert result.selected == "executor"


def test_role_agent_uses_preferred_role_as_tie_breaker_for_ambiguous_question() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me with this?"),
        perception=_perception("question", "general", "request_help"),
        context=_context(),
        user_preferences={"preferred_role": "analyst", "preferred_role_confidence": 0.76},
    )

    assert result.selected == "analyst"


def test_role_agent_does_not_override_explicit_executor_signal_with_preference() -> None:
    result = RoleAgent().run(
        event=_event("deploy the app to production"),
        perception=_perception("statement", "general", "share_information"),
        context=_context(),
        user_preferences={"preferred_role": "mentor", "preferred_role_confidence": 0.9},
    )

    assert result.selected == "executor"


def test_role_agent_uses_theta_bias_when_no_preferred_role_exists() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me with this?"),
        perception=_perception("question", "general", "request_help"),
        context=_context(),
        theta={"support_bias": 0.12, "analysis_bias": 0.68, "execution_bias": 0.2},
    )

    assert result.selected == "analyst"


def test_role_agent_keeps_explicit_emotional_signal_over_theta_bias() -> None:
    result = RoleAgent().run(
        event=_event("I feel stressed and need help"),
        perception=_perception("statement", "general", "share_information"),
        context=_context(),
        theta={"support_bias": 0.1, "analysis_bias": 0.75, "execution_bias": 0.15},
    )

    assert result.selected == "friend"


def test_role_agent_uses_guided_collaboration_preference_for_ambiguous_question() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me with this?"),
        perception=_perception("question", "general", "request_help"),
        context=_context(),
        user_preferences={"collaboration_preference": "guided"},
    )

    assert result.selected == "mentor"


def test_role_agent_uses_hands_on_collaboration_preference_before_theta() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me with this?"),
        perception=_perception("question", "general", "request_help"),
        context=_context(),
        user_preferences={"collaboration_preference": "hands_on"},
        theta={"support_bias": 0.1, "analysis_bias": 0.78, "execution_bias": 0.12},
    )

    assert result.selected == "executor"
