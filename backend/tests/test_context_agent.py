from datetime import datetime, timezone

from app.agents.context import ContextAgent
from app.core.contracts import AffectiveAssessmentOutput, Event, EventMeta, IdentityOutput, PerceptionOutput


def _event(text: str = "hello") -> Event:
    return Event(
        event_id="evt-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _perception() -> PerceptionOutput:
    return PerceptionOutput(
        event_type="statement",
        topic="general",
        topic_tags=["general"],
        intent="share_information",
        language="en",
        language_source="keyword_signal",
        language_confidence=0.8,
        ambiguity=0.1,
        initial_salience=0.5,
    )


def _identity() -> IdentityOutput:
    return IdentityOutput(
        mission="Help the user move forward with clear, constructive support.",
        values=["clarity", "continuity", "constructiveness"],
        behavioral_style=["direct", "supportive", "analytical"],
        boundaries=["do_not_fake_capabilities"],
        preferred_language="en",
        response_style=None,
        collaboration_preference=None,
        theta_orientation=None,
        summary="Mission: help the user move forward with clear, constructive support. Core style: direct, supportive, analytical.",
    )


def test_context_summary_stays_simple_without_recent_memory() -> None:
    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=[])

    assert "User said: 'hello' with detected intent 'share_information'." in result.summary
    assert "Foreground awareness: Current turn timestamp:" in result.summary
    assert result.related_tags == ["general", "language:en"]


def test_context_summary_includes_stable_user_preferences_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "response_style",
                "content": "concise",
                "confidence": 0.95,
                "source": "explicit_request",
            }
        ],
    )

    assert "Stable user preferences: prefers concise responses." in result.summary


def test_context_summary_includes_affective_support_pattern_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "affective_support_pattern",
                "content": "recurring_distress",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: recent turns show recurring stress signals and benefit from supportive pacing." in result.summary


def test_context_summary_includes_relation_cues_when_confident_relations_exist() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        relations=[
            {
                "relation_type": "collaboration_dynamic",
                "relation_value": "guided",
                "confidence": 0.78,
            },
            {
                "relation_type": "delivery_reliability",
                "relation_value": "high_trust",
                "confidence": 0.74,
            },
        ],
    )

    assert "Relation cues: current collaboration flow is guided and step-oriented" in result.summary
    assert "interaction trust is high when concrete delivery is proposed" in result.summary


def test_context_summary_can_include_identity_stance() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        identity=_identity(),
    )

    assert "Identity stance: direct, supportive, analytical." in result.summary


def test_context_summary_includes_foreground_awareness_name_memory_and_tools() -> None:
    result = ContextAgent().run(
        event=_event("jak sie nazywam"),
        perception=_perception(),
        recent_memory=[{"summary": "earlier recall", "payload": {"event": "hello"}}],
        identity=_identity().model_copy(update={"display_name": "Patryk"}),
    )

    assert result.known_user_name == "Patryk"
    assert result.memory_continuity_available is True
    assert "search_web" in result.available_tool_hints
    assert "read_page" in result.available_tool_hints
    assert "Known user name: Patryk." in result.foreground_awareness_summary


def test_context_summary_includes_relevant_active_goals_and_tasks() -> None:
    result = ContextAgent().run(
        event=_event("can you help me fix the deployment blocker for the mvp"),
        perception=_perception(),
        recent_memory=[],
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

    assert "Active goals: ship the MVP this week." in result.summary
    assert "Active tasks: fix deployment blocker (blocked)." in result.summary
    assert result.related_goals == ["ship the MVP this week"]


def test_context_prefers_affective_relevant_memory_order_when_support_is_needed() -> None:
    perception = _perception().model_copy(
        update={
            "affective": AffectiveAssessmentOutput(
                affect_label="support_distress",
                intensity=0.8,
                needs_support=True,
                confidence=0.79,
                source="ai_classifier",
                evidence=["overwhelmed"],
            )
        }
    )
    result = ContextAgent().run(
        event=_event("I am overwhelmed about deployment"),
        perception=perception,
        recent_memory=[
            {
                "summary": "older neutral deployment memory",
                "importance": 0.91,
                "payload": {
                    "payload_version": 1,
                    "event": "deployment checklist review",
                    "memory_kind": "semantic",
                    "memory_topics": ["deployment", "checklist"],
                    "response_language": "en",
                    "affect_label": "neutral",
                    "affect_needs_support": False,
                    "action": "success",
                    "expression": "Let's review the checklist.",
                },
            },
            {
                "summary": "older supportive deployment memory",
                "importance": 0.7,
                "payload": {
                    "payload_version": 1,
                    "event": "overwhelmed during deployment",
                    "memory_kind": "semantic",
                    "memory_topics": ["deployment", "overwhelmed"],
                    "response_language": "en",
                    "affect_label": "support_distress",
                    "affect_needs_support": True,
                    "action": "success",
                    "expression": "You are not alone; let's do one step at a time.",
                },
            },
        ],
    )

    assert "Relevant recent memory:" in result.summary
    assert result.summary.index("overwhelmed during deployment") < result.summary.index("deployment checklist review")


def test_context_summary_includes_active_goal_milestones() -> None:
    result = ContextAgent().run(
        event=_event("can you help me finish the mvp"),
        perception=_perception(),
        recent_memory=[],
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
        active_goal_milestones=[
            {
                "id": 3,
                "goal_id": 1,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
            }
        ],
    )

    assert "Active milestones: Drive goal to closure (completion_window)." in result.summary


def test_context_summary_formats_active_goal_milestone_with_risk_and_criteria() -> None:
    result = ContextAgent().run(
        event=_event("can you help me finish the mvp"),
        perception=_perception(),
        recent_memory=[],
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
        active_goal_milestones=[
            {
                "id": 3,
                "goal_id": 1,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
                "risk_level": "ready_to_close",
                "completion_criteria": "finish_remaining_active_work",
            }
        ],
    )

    assert (
        "Active milestones: Drive goal to closure (completion_window, ready_to_close, finish remaining active work)."
        in result.summary
    )


def test_context_summary_formats_active_goal_milestone_with_arc() -> None:
    result = ContextAgent().run(
        event=_event("can you help me finish the mvp"),
        perception=_perception(),
        recent_memory=[],
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
        active_goal_milestones=[
            {
                "id": 3,
                "goal_id": 1,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
                "arc": "reentered_completion_window",
                "risk_level": "ready_to_close",
            }
        ],
    )

    assert (
        "Active milestones: Drive goal to closure (completion_window, re-entered completion window, ready_to_close)."
        in result.summary
    )


def test_context_summary_formats_active_goal_milestone_with_pressure() -> None:
    result = ContextAgent().run(
        event=_event("can you help me finish the mvp"),
        perception=_perception(),
        recent_memory=[],
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
        active_goal_milestones=[
            {
                "id": 3,
                "goal_id": 1,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
                "pressure_level": "lingering_completion",
                "risk_level": "ready_to_close",
            }
        ],
    )

    assert (
        "Active milestones: Drive goal to closure (completion_window, lingering completion, ready_to_close)."
        in result.summary
    )


def test_context_summary_formats_active_goal_milestone_with_dependency_state() -> None:
    result = ContextAgent().run(
        event=_event("can you help me finish the mvp"),
        perception=_perception(),
        recent_memory=[],
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
        active_goal_milestones=[
            {
                "id": 3,
                "goal_id": 1,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
                "dependency_state": "multi_step_dependency",
                "risk_level": "ready_to_close",
            }
        ],
    )

    assert (
        "Active milestones: Drive goal to closure (completion_window, multi-step dependency chain, ready_to_close)."
        in result.summary
    )


def test_context_summary_formats_active_goal_milestone_with_due_state() -> None:
    result = ContextAgent().run(
        event=_event("can you help me finish the mvp"),
        perception=_perception(),
        recent_memory=[],
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
        active_goal_milestones=[
            {
                "id": 3,
                "goal_id": 1,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
                "due_state": "dependency_due_next",
                "risk_level": "ready_to_close",
            }
        ],
    )

    assert (
        "Active milestones: Drive goal to closure (completion_window, next dependency is due now, ready_to_close)."
        in result.summary
    )


def test_context_summary_formats_active_goal_milestone_with_due_window() -> None:
    result = ContextAgent().run(
        event=_event("can you help me finish the mvp"),
        perception=_perception(),
        recent_memory=[],
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
        active_goal_milestones=[
            {
                "id": 3,
                "goal_id": 1,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
                "due_window": "overdue_due_window",
                "risk_level": "ready_to_close",
            }
        ],
    )

    assert (
        "Active milestones: Drive goal to closure (completion_window, overdue due window, ready_to_close)."
        in result.summary
    )


def test_context_summary_includes_collaboration_preference_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "collaboration_preference",
                "content": "guided",
                "confidence": 0.91,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: prefers guided step by step help." in result.summary


def test_context_summary_includes_goal_execution_state_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_execution_state",
                "content": "blocked",
                "confidence": 0.82,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: current goal progress is blocked by an active task." in result.summary


def test_context_summary_includes_stagnating_goal_execution_state_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_execution_state",
                "content": "stagnating",
                "confidence": 0.72,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: current goal seems to be stagnating without recent execution." in result.summary


def test_context_summary_includes_recovering_goal_execution_state_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_execution_state",
                "content": "recovering",
                "confidence": 0.77,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: current goal is recovering after a recent unblock or completion." in result.summary


def test_context_summary_includes_advancing_goal_execution_state_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_execution_state",
                "content": "advancing",
                "confidence": 0.75,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: current goal work is actively advancing." in result.summary


def test_context_summary_includes_goal_progress_score_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_progress_score",
                "content": "0.82",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: goal completion is entering the final stretch." in result.summary


def test_context_summary_includes_goal_progress_trend_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_progress_trend",
                "content": "slipping",
                "confidence": 0.75,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: goal progress trend is slipping." in result.summary


def test_context_summary_includes_goal_progress_arc_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_progress_arc",
                "content": "recovery_gaining_traction",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: goal recovery is gaining traction." in result.summary


def test_context_summary_includes_goal_milestone_transition_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we close this out"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_milestone_transition",
                "content": "entered_completion_window",
                "confidence": 0.77,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: goal has entered the completion window." in result.summary


def test_context_summary_includes_goal_milestone_state_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_milestone_state",
                "content": "execution_phase",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: current goal is in an active execution phase." in result.summary


def test_context_summary_includes_goal_milestone_arc_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we close this out"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_milestone_arc",
                "content": "reentered_completion_window",
                "confidence": 0.79,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: active milestone has re-entered the completion window after recovery." in result.summary


def test_context_summary_includes_goal_milestone_pressure_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we close this out"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_milestone_pressure",
                "content": "lingering_completion",
                "confidence": 0.8,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: active milestone has lingered in the completion window for too long." in result.summary


def test_context_summary_includes_goal_milestone_dependency_state_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we close this out"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_milestone_dependency_state",
                "content": "multi_step_dependency",
                "confidence": 0.76,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: active milestone still depends on multiple remaining work items." in result.summary


def test_context_summary_includes_goal_milestone_due_state_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we close this out"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_milestone_due_state",
                "content": "dependency_due_next",
                "confidence": 0.79,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: active milestone is due to resolve its next dependency." in result.summary


def test_context_summary_includes_goal_milestone_due_window_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we close this out"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_milestone_due_window",
                "content": "overdue_due_window",
                "confidence": 0.82,
                "source": "background_reflection",
            }
        ],
    )

    assert "Stable user preferences: active milestone due window has become overdue." in result.summary


def test_context_summary_includes_goal_milestone_risk_and_completion_criteria_from_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we close this out"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "goal_milestone_risk",
                "content": "ready_to_close",
                "confidence": 0.79,
                "source": "background_reflection",
            },
            {
                "kind": "goal_completion_criteria",
                "content": "finish_remaining_active_work",
                "confidence": 0.8,
                "source": "background_reflection",
            },
        ],
    )

    assert "Stable user preferences: active milestone looks ready to close | goal completion depends on finishing the remaining active work." in result.summary


def test_context_summary_includes_recent_goal_progress_history() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed for the MVP"),
        perception=_perception(),
        recent_memory=[],
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
            {
                "id": 3,
                "goal_id": 11,
                "score": 0.72,
                "execution_state": "advancing",
                "progress_trend": "improving",
                "source_event_id": "evt-new",
                "created_at": datetime.now(timezone.utc),
            },
            {
                "id": 2,
                "goal_id": 11,
                "score": 0.49,
                "execution_state": "recovering",
                "progress_trend": "improving",
                "source_event_id": "evt-mid",
                "created_at": datetime.now(timezone.utc),
            },
            {
                "id": 1,
                "goal_id": 11,
                "score": 0.26,
                "execution_state": "blocked",
                "progress_trend": "slipping",
                "source_event_id": "evt-old",
                "created_at": datetime.now(timezone.utc),
            },
        ],
    )

    assert "Recent goal history shows lift from 0.26 to 0.72." in result.summary


def test_context_summary_includes_recent_goal_milestone_history() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed for the MVP"),
        perception=_perception(),
        recent_memory=[],
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
        goal_milestone_history=[
            {
                "id": 2,
                "goal_id": 11,
                "milestone_name": "Drive goal to closure",
                "phase": "completion_window",
                "risk_level": "ready_to_close",
                "completion_criteria": "finish_remaining_active_work",
                "source_event_id": "evt-new",
                "created_at": datetime.now(timezone.utc),
            },
            {
                "id": 1,
                "goal_id": 11,
                "milestone_name": "Stabilize goal recovery",
                "phase": "recovery_phase",
                "risk_level": "stabilizing",
                "completion_criteria": "stabilize_remaining_work",
                "source_event_id": "evt-old",
                "created_at": datetime.now(timezone.utc),
            },
        ],
    )

    assert "Recent milestone history moved from recovery phase to completion window." in result.summary


def test_context_ignores_low_confidence_conclusions() -> None:
    result = ContextAgent().run(
        event=_event("how should we proceed"),
        perception=_perception(),
        recent_memory=[],
        conclusions=[
            {
                "kind": "response_style",
                "content": "concise",
                "confidence": 0.5,
                "source": "weak_signal",
            }
        ],
    )

    assert "Stable user preferences:" not in result.summary


def test_context_related_tags_are_deduplicated_preserving_order() -> None:
    perception = PerceptionOutput(
        event_type="statement",
        topic="planning",
        topic_tags=["planning", "production", "planning"],
        intent="share_information",
        language="en",
        language_source="keyword_signal",
        language_confidence=0.8,
        ambiguity=0.1,
        initial_salience=0.5,
    )

    result = ContextAgent().run(event=_event("plan the production rollout"), perception=perception, recent_memory=[])

    assert result.related_tags == ["planning", "production", "language:en"]


def test_context_summary_includes_recent_memory_signal() -> None:
    event = _event("deployment help")
    recent_memory = [
        {
            "id": 1,
            "event_id": "evt-prev",
            "summary": (
                "event=deployment help request; memory_kind=semantic; memory_topics=deployment,help; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=We deployed it successfully"
            ),
            "importance": 0.8,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "Relevant recent memory:" in result.summary
    assert "deployment help request" in result.summary
    assert "We deployed it successfully" in result.summary


def test_clip_text_prefers_completed_sentence_when_it_fits() -> None:
    result = ContextAgent()._clip_text(
        "First complete sentence. Second sentence that should not fit cleanly.",
        30,
    )

    assert result == "First complete sentence."


def test_clip_text_falls_back_to_word_boundary_with_ellipsis() -> None:
    result = ContextAgent()._clip_text(
        "one two three four five six seven",
        18,
    )

    assert result == "one two three..."


def test_context_summary_clips_long_memory_cleanly() -> None:
    event = _event("production verification")
    recent_memory = [
        {
            "id": 2,
            "event_id": "evt-prev-2",
            "summary": (
                "event=asked for a very detailed production verification walkthrough with extra deployment notes; "
                "memory_kind=semantic; memory_topics=production,verification,deployment; "
                "response_language=en; "
                "context=old context; plan_goal=reply; action=success; "
                "expression=This response is intentionally long so the context summary has to cut it cleanly "
                "without stopping in the middle of a word or sentence fragment during runtime"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "asked for a very detailed production..." in result.summary
    assert "cut it cleanly without..." in result.summary


def test_context_prefers_same_language_memory_over_mismatched_recent_entries() -> None:
    perception = PerceptionOutput(
        event_type="statement",
        topic="general",
        topic_tags=["general"],
        intent="share_information",
        language="pl",
        language_source="keyword_signal",
        language_confidence=0.9,
        ambiguity=0.1,
        initial_salience=0.5,
    )
    recent_memory = [
        {
            "id": 10,
            "event_id": "evt-en",
            "summary": (
                "event=deploy the fix; memory_kind=semantic; memory_topics=deploy,fix; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=Let's deploy it carefully"
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 11,
            "event_id": "evt-pl",
            "summary": (
                "event=wdroz poprawke; memory_kind=semantic; memory_topics=wdroz,poprawke; response_language=pl; context=stary kontekst; "
                "plan_goal=reply; action=success; expression=Jasne, lecimy z tym"
            ),
            "importance": 0.6,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=_event(), perception=perception, recent_memory=recent_memory)

    assert "wdroz poprawke" in result.summary
    assert "Jasne, lecimy z tym" in result.summary
    assert "deploy the fix" not in result.summary


def test_context_falls_back_to_unknown_language_memory_when_no_match_exists() -> None:
    event = _event("ok")
    recent_memory = [
        {
            "id": 12,
            "event_id": "evt-unknown",
            "summary": (
                "event=asked about rollout; memory_kind=continuity; context=old context; "
                "plan_goal=reply; action=success; expression=We can keep going"
            ),
            "importance": 0.8,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "asked about rollout" in result.summary
    assert "We can keep going" in result.summary


def test_context_deduplicates_same_memory_summary() -> None:
    repeated_summary = (
        "event=deploy the fix now; memory_kind=semantic; memory_topics=deploy,fix; response_language=en; context=old context; "
        "plan_goal=reply; action=success; expression=Please provide the deployment details"
    )
    recent_memory = [
        {
            "id": 13,
            "event_id": "evt-en-1",
            "summary": repeated_summary,
            "importance": 0.9,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 14,
            "event_id": "evt-en-2",
            "summary": repeated_summary,
            "importance": 0.8,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 15,
            "event_id": "evt-en-3",
            "summary": (
                "event=deploy checklist; response_language=en; context=other context; "
                "memory_kind=semantic; memory_topics=deploy,checklist; "
                "plan_goal=reply; action=success; expression=Let's verify the rollout checklist"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=recent_memory)

    assert result.summary.count("deploy the fix now") == 1
    assert "deploy checklist" in result.summary


def test_context_deduplicates_near_duplicate_event_memory() -> None:
    recent_memory = [
        {
            "id": 16,
            "event_id": "evt-en-4",
            "summary": (
                "event=deploy the fix now; response_language=en; context=old context; "
                "memory_kind=semantic; memory_topics=deploy,fix; "
                "plan_goal=reply; action=success; expression=Please provide the necessary deployment details to proceed."
            ),
            "importance": 0.9,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 17,
            "event_id": "evt-en-5",
            "summary": (
                "event=deploy the fix now!; response_language=en; context=updated context; "
                "memory_kind=semantic; memory_topics=deploy,fix; "
                "plan_goal=reply; action=success; expression=To proceed with deploying the fix, please provide the necessary deployment details."
            ),
            "importance": 0.85,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 18,
            "event_id": "evt-en-6",
            "summary": (
                "event=deploy checklist; response_language=en; context=other context; "
                "memory_kind=semantic; memory_topics=deploy,checklist; "
                "plan_goal=reply; action=success; expression=Let's verify the rollout checklist"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=_event(), perception=_perception(), recent_memory=recent_memory)

    assert result.summary.count("deploy the fix now") == 1
    assert "deploy checklist" in result.summary


def test_context_prefers_more_topically_relevant_memory_over_higher_importance() -> None:
    event = Event(
        event_id="evt-2",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "deploy the fix to production now"},
        meta=EventMeta(user_id="u-1", trace_id="t-2"),
    )
    recent_memory = [
        {
            "id": 19,
            "event_id": "evt-en-7",
            "summary": (
                "event=write blog post draft; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=Let's outline the article first"
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 20,
            "event_id": "evt-en-8",
            "summary": (
                "event=deploy the fix to production; response_language=en; context=deploy context; "
                "plan_goal=reply; action=success; expression=Let's verify the production deploy steps"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "deploy the fix to production" in result.summary
    assert "Let's verify the production deploy steps" in result.summary
    assert "write blog post draft" not in result.summary


def test_context_uses_importance_when_relevance_is_tied() -> None:
    event = Event(
        event_id="evt-3",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "status update please"},
        meta=EventMeta(user_id="u-1", trace_id="t-3"),
    )
    recent_memory = [
        {
            "id": 21,
            "event_id": "evt-en-9",
            "summary": (
                "event=deployment status update; response_language=en; context=old context; "
                "plan_goal=reply; action=success; expression=Production looks stable"
            ),
            "importance": 0.55,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 22,
            "event_id": "evt-en-10",
            "summary": (
                "event=deployment status update; response_language=en; context=newer context; "
                "plan_goal=reply; action=success; expression=Production is healthy and all services are up"
            ),
            "importance": 0.9,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "Production is healthy and all services are up" in result.summary


def test_context_skips_irrelevant_memory_for_specific_request() -> None:
    event = Event(
        event_id="evt-4",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "status update please"},
        meta=EventMeta(user_id="u-1", trace_id="t-4"),
    )
    recent_memory = [
        {
            "id": 23,
            "event_id": "evt-en-11",
            "summary": (
                "event=deploy the fix now; memory_kind=semantic; memory_topics=deploy,fix,details; response_language=en; context=deploy context; "
                "plan_goal=reply; action=success; expression=Please provide the necessary deployment details to proceed."
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert result.summary.startswith("User said: 'status update please' with detected intent 'share_information'.")
    assert "Relevant recent memory:" not in result.summary
    assert "Foreground awareness: Current turn timestamp:" in result.summary


def test_context_keeps_memory_for_ambiguous_short_follow_up() -> None:
    event = Event(
        event_id="evt-5",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "ok"},
        meta=EventMeta(user_id="u-1", trace_id="t-5"),
    )
    recent_memory = [
        {
            "id": 24,
            "event_id": "evt-en-12",
            "summary": (
                "event=deploy the fix now; memory_kind=continuity; memory_topics=deploy,fix; response_language=en; context=deploy context; "
                "plan_goal=reply; action=success; expression=Please provide the necessary deployment details to proceed."
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "Relevant recent memory:" in result.summary


def test_context_uses_perception_topic_tags_for_memory_matching() -> None:
    event = Event(
        event_id="evt-8",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "please help"},
        meta=EventMeta(user_id="u-1", trace_id="t-8"),
    )
    perception = PerceptionOutput(
        event_type="question",
        topic="planning",
        topic_tags=["planning", "deploy", "production"],
        intent="request_help",
        language="en",
        language_source="keyword_signal",
        language_confidence=0.8,
        ambiguity=0.1,
        initial_salience=0.8,
    )
    recent_memory = [
        {
            "id": 29,
            "event_id": "evt-en-17",
            "summary": (
                "event=release planning; memory_kind=semantic; memory_topics=planning,deploy,production; "
                "response_language=en; context=semantic context; plan_goal=reply; action=success; "
                "expression=Let's walk through the rollout plan"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=perception, recent_memory=recent_memory)

    assert "release planning" in result.summary


def test_context_prefers_semantic_memory_for_specific_request_over_continuity() -> None:
    event = Event(
        event_id="evt-6",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "deploy the fix to production now"},
        meta=EventMeta(user_id="u-1", trace_id="t-6"),
    )
    recent_memory = [
        {
            "id": 25,
            "event_id": "evt-en-13",
            "summary": (
                "event=ok; memory_kind=continuity; memory_topics=; response_language=en; context=continuity context; "
                "plan_goal=reply; action=success; expression=Please provide the necessary deployment details to proceed."
            ),
            "importance": 0.95,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 26,
            "event_id": "evt-en-14",
            "summary": (
                "event=deploy the fix to production; memory_kind=semantic; memory_topics=deploy,fix,production; "
                "response_language=en; context=semantic context; plan_goal=reply; action=success; "
                "expression=Let's verify the production deploy steps"
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "Let's verify the production deploy steps" in result.summary
    assert "Please provide the necessary deployment details to proceed." not in result.summary


def test_context_prefers_continuity_memory_for_short_follow_up() -> None:
    event = Event(
        event_id="evt-7",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "ok"},
        meta=EventMeta(user_id="u-1", trace_id="t-7"),
    )
    recent_memory = [
        {
            "id": 27,
            "event_id": "evt-en-15",
            "summary": (
                "event=deploy the fix to production; memory_kind=semantic; memory_topics=deploy,fix,production; "
                "response_language=en; context=semantic context; plan_goal=reply; action=success; "
                "expression=Let's verify the production deploy steps"
            ),
            "importance": 0.9,
            "event_timestamp": datetime.now(timezone.utc),
        },
        {
            "id": 28,
            "event_id": "evt-en-16",
            "summary": (
                "event=ok; memory_kind=continuity; memory_topics=; response_language=en; context=continuity context; "
                "plan_goal=reply; action=success; expression=Please provide the necessary deployment details to proceed."
            ),
            "importance": 0.7,
            "event_timestamp": datetime.now(timezone.utc),
        },
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "Please provide the necessary deployment details to proceed." in result.summary
    assert "Let's verify the production deploy steps" not in result.summary


def test_context_reads_structured_memory_payload_before_legacy_summary() -> None:
    event = Event(
        event_id="evt-structured-memory",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "deploy the fix to production now"},
        meta=EventMeta(user_id="u-1", trace_id="t-structured-memory"),
    )
    recent_memory = [
        {
            "id": 31,
            "event_id": "evt-structured-prev",
            "summary": "Readable summary only.",
            "payload": {
                "payload_version": 1,
                "event": "deploy the fix to production",
                "memory_kind": "semantic",
                "memory_topics": ["deploy", "fix", "production"],
                "response_language": "en",
                "context": "semantic context",
                "plan_goal": "reply",
                "action": "success",
                "expression": "Let's verify the production deploy steps",
            },
            "importance": 0.72,
            "event_timestamp": datetime.now(timezone.utc),
        }
    ]

    result = ContextAgent().run(event=event, perception=_perception(), recent_memory=recent_memory)

    assert "Let's verify the production deploy steps" in result.summary
