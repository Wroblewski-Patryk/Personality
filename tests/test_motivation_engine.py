from datetime import datetime, timezone

import pytest

from app.core.contracts import AffectiveAssessmentOutput, ContextOutput, Event, EventMeta, PerceptionOutput
from app.motivation.engine import MotivationEngine
from tests.empathy_fixtures import EMPATHY_SUPPORT_SCENARIOS


def _event(text: str) -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _scheduler_event(payload: dict | None = None) -> Event:
    return Event(
        event_id="evt-scheduler",
        source="scheduler",
        subsource="proactive_tick",
        timestamp=datetime.now(timezone.utc),
        payload=payload or {
            "text": "scheduler proactive tick",
            "proactive": {
                "trigger": "time_checkin",
                "importance": 0.55,
                "urgency": 0.45,
                "user_context": {},
            },
        },
        meta=EventMeta(user_id="scheduler", trace_id="t-scheduler"),
    )


def _context(risk_level: float = 0.1) -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=risk_level)


def _perception(
    event_type: str = "statement",
    topic: str = "general",
    intent: str = "share_information",
    affective: AffectiveAssessmentOutput | None = None,
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
        affective=affective or AffectiveAssessmentOutput(),
    )


def test_motivation_engine_requests_clarification_without_text() -> None:
    result = MotivationEngine().run(event=_event(""), context=_context(), perception=_perception())

    assert result.mode == "clarify"
    assert result.importance == 0.3


def test_motivation_engine_uses_affective_contract_for_documented_respond_mode() -> None:
    result = MotivationEngine().run(
        event=_event("Status update for today"),
        context=_context(),
        perception=_perception(
            affective=AffectiveAssessmentOutput(
                affect_label="support_distress",
                intensity=0.72,
                needs_support=True,
                confidence=0.76,
                source="ai_classifier",
                evidence=["stressed", "overwhelmed"],
            )
        ),
    )

    assert result.mode == "respond"
    assert result.valence < 0


def test_motivation_engine_describes_affective_distress_without_undocumented_support_mode() -> None:
    result = MotivationEngine().run(
        event=_event("Quick check-in"),
        context=_context(),
        perception=_perception(
            affective=AffectiveAssessmentOutput(
                affect_label="support_distress",
                intensity=0.8,
                needs_support=True,
                confidence=0.75,
                source="ai_classifier",
                evidence=["anxious", "lonely"],
            )
        ),
    )

    assert result.mode == "respond"
    assert result.valence <= -0.45
    assert result.arousal >= 0.5


def test_motivation_engine_uses_reflected_affective_support_preferences() -> None:
    baseline = MotivationEngine().run(
        event=_event("Can you help me think this through?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
    )
    reflected = MotivationEngine().run(
        event=_event("Can you help me think this through?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={
            "affective_support_pattern": "recurring_distress",
            "affective_support_sensitivity": "high",
        },
    )

    assert reflected.mode == "analyze"
    assert reflected.importance > baseline.importance
    assert reflected.urgency > baseline.urgency
    assert reflected.valence <= baseline.valence


@pytest.mark.parametrize("scenario", EMPATHY_SUPPORT_SCENARIOS, ids=lambda scenario: scenario.key)
def test_motivation_engine_keeps_empathy_quality_for_heavy_ambiguous_and_mixed_turns(scenario) -> None:
    result = MotivationEngine().run(
        event=_event(scenario.text),
        context=_context(),
        perception=_perception(affective=scenario.affective()),
    )

    assert result.mode == "respond"
    assert result.urgency >= scenario.expected_min_urgency
    assert result.valence <= scenario.expected_max_valence
    assert result.arousal >= scenario.expected_min_arousal


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


def test_motivation_engine_raises_completion_pressure_for_goal_milestone_transition() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_milestone_transition": "entered_completion_window"},
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
    assert result.importance >= 0.79
    assert result.urgency >= 0.3


def test_motivation_engine_keeps_goal_pressure_from_milestone_state_without_transition() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_milestone_state": "completion_window"},
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
    assert result.importance >= 0.8
    assert result.urgency >= 0.25


def test_motivation_engine_adds_pressure_for_milestone_risk() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_milestone_risk": "at_risk"},
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
    assert result.importance >= 0.81
    assert result.urgency >= 0.28


def test_motivation_engine_adds_pressure_for_goal_completion_criteria() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={
            "goal_milestone_risk": "ready_to_close",
            "goal_completion_criteria": "finish_remaining_active_work",
        },
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
    assert result.importance >= 0.83
    assert result.urgency >= 0.33


def test_motivation_engine_adds_pressure_for_goal_milestone_history_signal() -> None:
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
        goal_milestone_history=[
            {"goal_id": 1, "phase": "completion_window", "risk_level": "ready_to_close"},
            {"goal_id": 1, "phase": "recovery_phase", "risk_level": "stabilizing"},
        ],
    )

    assert result.mode == "analyze"
    assert result.importance >= 0.8
    assert result.urgency >= 0.27


def test_motivation_engine_adds_pressure_for_goal_milestone_arc() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_milestone_arc": "reentered_completion_window"},
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
    assert result.importance >= 0.8
    assert result.urgency >= 0.27


def test_motivation_engine_adds_pressure_for_goal_milestone_pressure() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_milestone_pressure": "lingering_completion"},
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
    assert result.importance >= 0.82
    assert result.urgency >= 0.29


def test_motivation_engine_adds_pressure_for_goal_milestone_dependency_state() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_milestone_dependency_state": "blocked_dependency"},
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
    assert result.importance >= 0.81
    assert result.urgency >= 0.28


def test_motivation_engine_adds_pressure_for_goal_milestone_due_state() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_milestone_due_state": "closure_due_now"},
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
    assert result.importance >= 0.82
    assert result.urgency >= 0.3


def test_motivation_engine_adds_pressure_for_goal_milestone_due_window() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_milestone_due_window": "overdue_due_window"},
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
    assert result.importance >= 0.81
    assert result.urgency >= 0.29


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


def test_motivation_engine_adds_pressure_for_unstable_goal_progress_arc() -> None:
    result = MotivationEngine().run(
        event=_event("What should I do next for the MVP?"),
        context=_context(),
        perception=_perception(event_type="question", intent="request_help"),
        user_preferences={"goal_progress_arc": "unstable_progress"},
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
    assert result.importance >= 0.76
    assert result.urgency >= 0.24


def test_motivation_engine_defer_proactive_when_interruption_cost_is_high() -> None:
    result = MotivationEngine().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "proactive": {
                    "trigger": "goal_stagnation",
                    "importance": 0.82,
                    "urgency": 0.7,
                    "user_context": {
                        "quiet_hours": True,
                        "focus_mode": True,
                        "recent_user_activity": "away",
                        "recent_outbound_count": 3,
                        "unanswered_proactive_count": 2,
                    },
                },
            }
        ),
        context=_context(),
        perception=_perception(),
        active_goals=[{"id": 1, "name": "ship the MVP this week", "status": "active"}],
    )

    assert result.mode == "ignore"
    assert result.importance >= 0.8
    assert result.urgency >= 0.6


def test_motivation_engine_selects_execute_mode_for_high_signal_proactive_warning() -> None:
    result = MotivationEngine().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "proactive": {
                    "trigger": "task_blocked",
                    "importance": 0.86,
                    "urgency": 0.88,
                    "user_context": {
                        "quiet_hours": False,
                        "focus_mode": False,
                        "recent_user_activity": "active",
                        "recent_outbound_count": 0,
                        "unanswered_proactive_count": 0,
                    },
                },
            }
        ),
        context=_context(),
        perception=_perception(),
        active_tasks=[{"id": 11, "name": "fix deploy blocker", "status": "blocked"}],
    )

    assert result.mode == "execute"
    assert result.importance >= 0.86
    assert result.urgency >= 0.88
