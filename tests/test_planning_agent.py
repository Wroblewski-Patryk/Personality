from datetime import datetime, timezone

from app.agents.planning import PlanningAgent
from app.core.contracts import ContextOutput, Event, EventMeta, MotivationOutput, RoleOutput


def _event(source: str = "api", text: str = "hello") -> Event:
    return Event(
        event_id="evt-1",
        source=source,
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _context() -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=0.1)


def test_planning_agent_builds_support_plan() -> None:
    result = PlanningAgent().run(
        event=_event(text="I feel stressed"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.8,
            urgency=0.4,
            valence=-0.3,
            arousal=0.6,
            mode="support",
        ),
        role=RoleOutput(selected="friend", confidence=0.8),
    )

    assert result.goal == "Provide grounded emotional support and one manageable next step."
    assert result.steps == [
        "interpret_event",
        "review_context",
        "acknowledge_emotion",
        "reduce_pressure",
        "prepare_response",
    ]
    assert result.needs_response is True
    assert result.needs_action is False


def test_planning_agent_adds_concise_step_from_semantic_preference() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you help me plan this?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.7,
            urgency=0.3,
            valence=0.0,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"response_style": "concise"},
    )

    assert result.steps == [
        "interpret_event",
        "review_context",
        "break_down_problem",
        "highlight_next_step",
        "keep_response_concise",
        "prepare_response",
    ]


def test_planning_agent_adds_structured_step_from_semantic_preference() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you help me plan this?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.7,
            urgency=0.3,
            valence=0.0,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"response_style": "structured"},
    )

    assert result.steps == [
        "interpret_event",
        "review_context",
        "break_down_problem",
        "highlight_next_step",
        "format_response_as_bullets",
        "prepare_response",
    ]


def test_planning_agent_adds_telegram_delivery_step_when_needed() -> None:
    result = PlanningAgent().run(
        event=_event(source="telegram", text="deploy the fix"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.8,
            urgency=0.8,
            valence=-0.1,
            arousal=0.8,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.8),
    )

    assert result.goal == "Move the requested task toward execution with the smallest concrete next step."
    assert result.steps[-1] == "send_telegram_message"
    assert result.needs_action is True


def test_planning_agent_adds_theta_reasoning_step_for_generic_turn() -> None:
    result = PlanningAgent().run(
        event=_event(text="help me"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.5,
            urgency=0.2,
            valence=0.05,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.6),
        theta={
            "support_bias": 0.14,
            "analysis_bias": 0.71,
            "execution_bias": 0.15,
        },
    )

    assert result.steps == [
        "interpret_event",
        "review_context",
        "favor_structured_reasoning",
        "prepare_response",
    ]


def test_planning_agent_uses_guided_collaboration_preference_for_generic_turn() -> None:
    result = PlanningAgent().run(
        event=_event(text="help me with this"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.5,
            urgency=0.2,
            valence=0.05,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.6),
        user_preferences={"collaboration_preference": "guided"},
    )

    assert result.goal == "Guide the user through the next step in a calm, step by step way."
    assert result.steps == [
        "interpret_event",
        "review_context",
        "favor_guided_walkthrough",
        "prepare_response",
    ]


def test_planning_agent_uses_hands_on_collaboration_preference_for_generic_turn() -> None:
    result = PlanningAgent().run(
        event=_event(text="help me with this"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.5,
            urgency=0.2,
            valence=0.05,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.6),
        user_preferences={"collaboration_preference": "hands_on"},
    )

    assert result.goal == "Provide a clear response that ends with a concrete next step."
    assert result.steps == [
        "interpret_event",
        "review_context",
        "favor_concrete_next_step",
        "prepare_response",
    ]


def test_planning_agent_aligns_with_active_goal_and_blocked_task() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you help me fix the deployment blocker for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.8,
            urgency=0.35,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        active_goals=[
            {
                "id": 11,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
        active_tasks=[
            {
                "id": 21,
                "goal_id": 11,
                "name": "fix deployment blocker",
                "description": "User-declared task: fix deployment blocker",
                "priority": "high",
                "status": "blocked",
            }
        ],
    )

    assert "ship the MVP this week" in result.goal
    assert "align_with_active_goal" in result.steps
    assert "unblock_active_task" in result.steps
