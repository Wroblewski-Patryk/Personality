from datetime import datetime, timezone

from app.core.contracts import ContextOutput, Event, EventMeta, PerceptionOutput
from app.motivation.engine import MotivationEngine


def _event(text: str) -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _context(risk_level: float = 0.1) -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=risk_level)


def _perception(
    event_type: str = "statement",
    topic: str = "general",
    intent: str = "share_information",
) -> PerceptionOutput:
    return PerceptionOutput(
        event_type=event_type,
        topic=topic,
        topic_tags=[topic],
        intent=intent,
        language="en",
        language_source="default",
        language_confidence=0.35,
        ambiguity=0.1,
        initial_salience=0.5,
    )


def test_motivation_engine_requests_clarification_without_text() -> None:
    result = MotivationEngine().run(event=_event(""), context=_context(), perception=_perception())

    assert result.mode == "clarify"
    assert result.importance == 0.3


def test_motivation_engine_uses_support_mode_for_emotional_text() -> None:
    result = MotivationEngine().run(
        event=_event("I feel stressed and overwhelmed"),
        context=_context(),
        perception=_perception(),
    )

    assert result.mode == "support"
    assert result.valence < 0


def test_motivation_engine_uses_execute_mode_for_urgent_action_requests() -> None:
    result = MotivationEngine().run(
        event=_event("deploy the production fix now"),
        context=_context(risk_level=0.2),
        perception=_perception(),
    )

    assert result.mode == "execute"
    assert result.urgency >= 0.75
    assert result.importance >= 0.65


def test_motivation_engine_uses_analyze_mode_for_questions() -> None:
    result = MotivationEngine().run(
        event=_event("Can you explain why this rollout failed?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.6


def test_motivation_engine_handles_polish_urgent_request() -> None:
    result = MotivationEngine().run(
        event=_event("wdroz to na produkcje teraz"),
        context=_context(),
        perception=_perception(),
    )

    assert result.mode == "execute"
    assert result.urgency >= 0.75


def test_motivation_engine_uses_theta_bias_for_ambiguous_brief_turn() -> None:
    result = MotivationEngine().run(
        event=_event("help me"),
        context=_context(),
        perception=_perception(),
        theta={
            "support_bias": 0.11,
            "analysis_bias": 0.68,
            "execution_bias": 0.21,
        },
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.5


def test_motivation_engine_keeps_explicit_execution_signal_over_theta_support_bias() -> None:
    result = MotivationEngine().run(
        event=_event("deploy the fix now"),
        context=_context(),
        perception=_perception(),
        theta={
            "support_bias": 0.77,
            "analysis_bias": 0.12,
            "execution_bias": 0.11,
        },
    )

    assert result.mode == "execute"


def test_motivation_engine_uses_guided_collaboration_preference_for_ambiguous_turn() -> None:
    result = MotivationEngine().run(
        event=_event("help me"),
        context=_context(),
        perception=_perception(),
        user_preferences={"collaboration_preference": "guided"},
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.5


def test_motivation_engine_uses_hands_on_collaboration_preference_before_theta() -> None:
    result = MotivationEngine().run(
        event=_event("help me"),
        context=_context(),
        perception=_perception(),
        user_preferences={"collaboration_preference": "hands_on"},
        theta={
            "support_bias": 0.15,
            "analysis_bias": 0.75,
            "execution_bias": 0.1,
        },
    )

    assert result.mode == "execute"


def test_motivation_engine_keeps_explicit_analysis_signal_over_collaboration_preference() -> None:
    result = MotivationEngine().run(
        event=_event("Can you explain why this rollout failed?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"collaboration_preference": "hands_on"},
    )

    assert result.mode == "analyze"


def test_motivation_engine_boosts_priority_for_related_goal_and_blocked_task() -> None:
    result = MotivationEngine().run(
        event=_event("Can you help me fix the deployment blocker for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
        active_tasks=[
            {
                "id": 2,
                "goal_id": 1,
                "name": "fix deployment blocker",
                "description": "User-declared task: fix deployment blocker",
                "priority": "high",
                "status": "blocked",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.78
    assert result.urgency >= 0.35


def test_motivation_engine_boosts_goal_pressure_from_reflected_blocked_execution_state() -> None:
    result = MotivationEngine().run(
        event=_event("Can you help me move the MVP forward?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_execution_state": "blocked"},
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.75
    assert result.urgency >= 0.28


def test_motivation_engine_recognizes_progressing_goal_execution_state_without_blocking() -> None:
    result = MotivationEngine().run(
        event=_event("Can you help me move the MVP forward?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_execution_state": "progressing"},
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.72
    assert result.urgency == 0.2


def test_motivation_engine_adds_urgency_for_stagnating_goal_execution_state() -> None:
    result = MotivationEngine().run(
        event=_event("Can you help me move the MVP forward?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_execution_state": "stagnating"},
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.73
    assert result.urgency >= 0.25


def test_motivation_engine_recognizes_recovering_goal_execution_state() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_execution_state": "recovering"},
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.74
    assert result.urgency >= 0.24


def test_motivation_engine_recognizes_advancing_goal_execution_state() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_execution_state": "advancing"},
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.73
    assert result.urgency >= 0.23


def test_motivation_engine_boosts_for_early_goal_progress_score() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_progress_score": 0.22},
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.74
    assert result.urgency >= 0.23


def test_motivation_engine_boosts_for_high_goal_progress_score() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_progress_score": 0.84},
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.73
    assert result.urgency >= 0.24


def test_motivation_engine_adds_pressure_for_slipping_goal_progress_trend() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_progress_trend": "slipping"},
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.75
    assert result.urgency >= 0.25


def test_motivation_engine_adds_pressure_for_goal_history_regression() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        active_goals=[
            {
                "id": 1,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
        goal_progress_history=[
            {"goal_id": 1, "score": 0.34},
            {"goal_id": 1, "score": 0.61},
            {"goal_id": 1, "score": 0.82},
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.76
    assert result.urgency >= 0.24
