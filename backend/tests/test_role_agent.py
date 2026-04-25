from datetime import datetime, timezone

from app.agents.role import RoleAgent
from app.core.contracts import AffectiveAssessmentOutput, ContextOutput, Event, EventMeta, PerceptionOutput


def _event(text: str) -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _perception(
    event_type: str,
    topic: str,
    intent: str,
    language: str = "en",
    affective: AffectiveAssessmentOutput | None = None,
) -> PerceptionOutput:
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
        affective=affective or AffectiveAssessmentOutput(),
    )


def _context(risk_level: float = 0.1) -> ContextOutput:
    return ContextOutput(summary="ctx", related_goals=[], related_tags=["general"], risk_level=risk_level)


def test_role_agent_uses_friend_for_affective_support_signal() -> None:
    result = RoleAgent().run(
        event=_event("Status update for today"),
        perception=_perception(
            "statement",
            "general",
            "share_information",
            affective=AffectiveAssessmentOutput(
                affect_label="support_distress",
                intensity=0.72,
                needs_support=True,
                confidence=0.75,
                source="ai_classifier",
                evidence=["stressed", "tired"],
            ),
        ),
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
    assert result.selection_reason == "planning_topic_or_analysis_keyword"
    assert result.skill_policy_owner == "role_skill_boundary_policy"
    assert any(skill.skill_id == "structured_reasoning" for skill in result.selected_skills)
    assert all(skill.policy_owner == "role_skill_boundary_policy" for skill in result.selected_skills)


def test_role_agent_uses_executor_for_direct_action_request() -> None:
    result = RoleAgent().run(
        event=_event("deploy the app to production"),
        perception=_perception("statement", "general", "share_information"),
        context=_context(),
    )

    assert result.selected == "executor"
    assert any(skill.skill_id == "execution_planning" for skill in result.selected_skills)


def test_role_agent_selects_work_partner_for_explicit_work_orchestration_request() -> None:
    result = RoleAgent().run(
        event=_event("Be my work partner and organize the release plan in ClickUp while checking the latest notes."),
        perception=_perception("question", "planning", "request_help"),
        context=_context(),
    )

    selected_skill_ids = [skill.skill_id for skill in result.selected_skills]
    assert result.selected == "work_partner"
    assert result.selection_reason == "work_partner_explicit_orchestration"
    assert "structured_reasoning" in selected_skill_ids
    assert "execution_planning" in selected_skill_ids
    assert "connector_boundary_review" in selected_skill_ids


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
    assert result.selection_reason == "preferred_role_help_tie_break"
    assert any(item.source == "user_preference" and item.applied for item in result.selection_evidence)


def test_role_agent_uses_active_goal_risk_context_for_ambiguous_help_turn() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me think through this blocker?"),
        perception=_perception("question", "general", "request_help"),
        context=ContextOutput(
            summary="ctx",
            related_goals=["ship the MVP this week"],
            related_tags=["goal"],
            risk_level=0.62,
        ),
    )

    assert result.selected == "advisor"
    assert result.selection_reason == "active_goal_risk_review"
    assert any(item.signal == "active_goal_context" and item.applied for item in result.selection_evidence)
    assert any(item.signal == "context_risk" and item.applied for item in result.selection_evidence)


def test_role_agent_raises_analyst_confidence_when_planning_turn_has_active_goal_context() -> None:
    result = RoleAgent().run(
        event=_event("Can you plan the rollout around the current milestone?"),
        perception=_perception("question", "planning", "request_help"),
        context=ContextOutput(
            summary="ctx",
            related_goals=["ship the MVP this week"],
            related_tags=["goal"],
            risk_level=0.34,
        ),
    )

    assert result.selected == "analyst"
    assert result.confidence == 0.85
    assert result.selection_reason == "planning_topic_active_goal_context"
    assert any(item.signal == "active_goal_context" and item.applied for item in result.selection_evidence)


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
        event=_event("Can you help me with this?"),
        perception=_perception(
            "question",
            "general",
            "request_help",
            affective=AffectiveAssessmentOutput(
                affect_label="support_distress",
                intensity=0.64,
                needs_support=True,
                confidence=0.7,
                source="ai_classifier",
                evidence=["overwhelmed"],
            ),
        ),
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


def test_role_agent_uses_relation_collaboration_signal_for_ambiguous_question() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me with this?"),
        perception=_perception("question", "general", "request_help"),
        context=_context(),
        relations=[
            {
                "relation_type": "collaboration_dynamic",
                "relation_value": "guided",
                "confidence": 0.79,
            }
        ],
    )

    assert result.selected == "mentor"


def test_role_agent_ignores_subthreshold_relation_collaboration_signal() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me with this?"),
        perception=_perception("question", "general", "request_help"),
        context=_context(),
        relations=[
            {
                "relation_type": "collaboration_dynamic",
                "relation_value": "hands_on",
                "confidence": 0.69,
            }
        ],
    )

    assert result.selected == "mentor"


def test_role_agent_ignores_subthreshold_theta_bias_for_ambiguous_question() -> None:
    result = RoleAgent().run(
        event=_event("Can you help me with this?"),
        perception=_perception("question", "general", "request_help"),
        context=_context(),
        theta={"support_bias": 0.12, "analysis_bias": 0.57, "execution_bias": 0.31},
    )

    assert result.selected == "mentor"
