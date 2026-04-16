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


def test_planning_agent_adds_recover_goal_progress_step_from_reflected_blocked_state() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you help me move the MVP forward?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.76,
            urgency=0.28,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_execution_state": "blocked"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "recover_goal_progress" in result.steps


def test_planning_agent_adds_completion_window_step_from_goal_milestone_transition() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.84,
            urgency=0.36,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_milestone_transition": "entered_completion_window"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "close_goal_completion_window" in result.steps


def test_planning_agent_adds_goal_closure_step_from_milestone_state() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.82,
            urgency=0.3,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_milestone_state": "completion_window"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "drive_goal_to_closure" in result.steps


def test_planning_agent_adds_preserve_goal_momentum_step_from_reflected_progress_state() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.73,
            urgency=0.2,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_execution_state": "progressing"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "preserve_goal_momentum" in result.steps


def test_planning_agent_adds_restart_goal_progress_step_from_stagnating_state() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.74,
            urgency=0.26,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_execution_state": "stagnating"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "restart_goal_progress" in result.steps


def test_planning_agent_adds_stabilize_goal_recovery_step_from_recovering_state() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.75,
            urgency=0.24,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_execution_state": "recovering"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "stabilize_goal_recovery" in result.steps


def test_planning_agent_adds_continue_goal_execution_step_from_advancing_state() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.74,
            urgency=0.23,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_execution_state": "advancing"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "continue_goal_execution" in result.steps


def test_planning_agent_adds_increase_goal_progress_step_for_early_progress_score() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.74,
            urgency=0.23,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_progress_score": 0.22},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "increase_goal_progress" in result.steps


def test_planning_agent_adds_push_goal_to_completion_step_for_high_progress_score() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.73,
            urgency=0.24,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_progress_score": 0.84},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "push_goal_to_completion" in result.steps


def test_planning_agent_adds_correct_goal_drift_step_for_slipping_progress_trend() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.78,
            urgency=0.27,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_progress_trend": "slipping"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "correct_goal_drift" in result.steps


def test_planning_agent_adds_protect_goal_trajectory_step_for_lift_history() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.76,
            urgency=0.24,
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
        goal_progress_history=[
            {"goal_id": 11, "score": 0.72},
            {"goal_id": 11, "score": 0.49},
            {"goal_id": 11, "score": 0.26},
        ],
    )

    assert "align_with_active_goal" in result.steps
    assert "protect_goal_trajectory" in result.steps


def test_planning_agent_adds_consolidate_goal_recovery_step_for_progress_arc() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.79,
            urgency=0.25,
            valence=0.05,
            arousal=0.4,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_progress_arc": "recovery_gaining_traction"},
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
    )

    assert "align_with_active_goal" in result.steps
    assert "consolidate_goal_recovery" in result.steps
