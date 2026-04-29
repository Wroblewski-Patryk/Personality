from datetime import datetime, timezone

from app.agents.planning import PlanningAgent
from app.core.contracts import (
    CancelPlannedWorkItemDomainIntent,
    CalendarSchedulingIntentDomainIntent,
    CompletePlannedWorkItemDomainIntent,
    ConnectedDriveAccessDomainIntent,
    ConnectorCapabilityDiscoveryDomainIntent,
    ContextOutput,
    Event,
    EventMeta,
    ExternalTaskSyncDomainIntent,
    MaintainRelationDomainIntent,
    MaintainTaskStatusDomainIntent,
    MotivationOutput,
    PromoteInferredGoalDomainIntent,
    PromoteInferredTaskDomainIntent,
    ReschedulePlannedWorkItemDomainIntent,
    RoleOutput,
    SkillCapabilityOutput,
    UpdateCollaborationPreferenceDomainIntent,
    UpdateProactivePreferenceDomainIntent,
    UpdateResponseStyleDomainIntent,
    UpdateTaskStatusDomainIntent,
    UpsertGoalDomainIntent,
    UpsertPlannedWorkItemDomainIntent,
    UpsertTaskDomainIntent,
)


def _event(source: str = "api", text: str = "hello") -> Event:
    return Event(
        event_id="evt-1",
        source=source,
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": text},
        meta=EventMeta(user_id="u-1", trace_id="t-1"),
    )


def _scheduler_event(payload: dict) -> Event:
    return Event(
        event_id="evt-scheduler",
        source="scheduler",
        subsource="proactive_tick",
        timestamp=datetime.now(timezone.utc),
        payload=payload,
        meta=EventMeta(user_id="scheduler", trace_id="t-scheduler"),
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
            mode="respond",
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


def test_planning_agent_keeps_supportive_steps_inside_documented_contract() -> None:
    result = PlanningAgent().run(
        event=_event(text="I feel overwhelmed and tired"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.78,
            urgency=0.24,
            valence=-0.45,
            arousal=0.55,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    assert result.goal == "Provide grounded emotional support and one manageable next step."
    assert "acknowledge_emotion" in result.steps
    assert "reduce_pressure" in result.steps


def test_planning_agent_carries_work_partner_skills_and_tool_intents() -> None:
    result = PlanningAgent().run(
        event=_event(text="Be my work partner and search the web for release notes in ClickUp."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.81,
            urgency=0.42,
            valence=0.02,
            arousal=0.39,
            mode="analyze",
        ),
        role=RoleOutput(
            selected="work_partner",
            confidence=0.84,
            selected_skills=[
                SkillCapabilityOutput(
                    skill_id="structured_reasoning",
                    label="Structured reasoning",
                    capability_family="analysis",
                    reason="work_partner_role_selected",
                ),
                SkillCapabilityOutput(
                    skill_id="execution_planning",
                    label="Execution planning",
                    capability_family="execution",
                    reason="work_partner_role_selected",
                ),
                SkillCapabilityOutput(
                    skill_id="connector_boundary_review",
                    label="Connector boundary review",
                    capability_family="connector_boundary",
                    reason="work_partner_role_selected",
                ),
            ],
        ),
    )

    selected_skill_ids = [skill.skill_id for skill in result.selected_skills]
    assert selected_skill_ids == [
        "structured_reasoning",
        "execution_planning",
        "connector_boundary_review",
    ]
    assert any(isinstance(intent, ExternalTaskSyncDomainIntent) for intent in result.domain_intents)
    assert any(intent.intent_type == "knowledge_search_intent" for intent in result.domain_intents)


def test_planning_agent_infers_weather_lookup_without_explicit_search_marker() -> None:
    result = PlanningAgent().run(
        event=_event(text="Jaka jest pogoda w Berlinie dzisiaj?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.71,
            urgency=0.28,
            valence=0.0,
            arousal=0.31,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.72),
    )

    search_intent = next(intent for intent in result.domain_intents if intent.intent_type == "knowledge_search_intent")
    assert search_intent.operation == "search_web"
    assert "pogoda" in search_intent.query_hint.lower()


def test_planning_agent_infers_page_read_for_bare_domain_without_read_page_marker() -> None:
    result = PlanningAgent().run(
        event=_event(text="Co jest na luckysparrow.ch?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.73,
            urgency=0.22,
            valence=0.0,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    browser_intent = next(intent for intent in result.domain_intents if intent.intent_type == "web_browser_access_intent")
    assert browser_intent.operation == "read_page"
    assert browser_intent.page_hint == "https://luckysparrow.ch"


def test_planning_agent_emits_goal_upsert_domain_intent() -> None:
    result = PlanningAgent().run(
        event=_event(text="My goal is to ship the MVP this week."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.75,
            urgency=0.33,
            valence=0.0,
            arousal=0.35,
            mode="analyze",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    assert any(isinstance(intent, UpsertGoalDomainIntent) for intent in result.domain_intents)


def test_planning_agent_emits_goal_and_task_upsert_intents_for_inline_command_phrasing() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you add goal ship the MVP this week and add task fix deployment blocker?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.79,
            urgency=0.37,
            valence=0.0,
            arousal=0.41,
            mode="analyze",
        ),
        role=RoleOutput(selected="advisor", confidence=0.72),
    )

    assert any(isinstance(intent, UpsertGoalDomainIntent) for intent in result.domain_intents)
    assert any(isinstance(intent, UpsertTaskDomainIntent) for intent in result.domain_intents)


def test_planning_agent_emits_task_status_domain_intent() -> None:
    result = PlanningAgent().run(
        event=_event(text="I fixed the deployment blocker."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.74,
            urgency=0.31,
            valence=0.0,
            arousal=0.4,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    assert any(isinstance(intent, UpdateTaskStatusDomainIntent) for intent in result.domain_intents)


def test_planning_agent_infers_task_from_repeated_blocker_evidence() -> None:
    result = PlanningAgent().run(
        event=_event(text="Still blocked again by deployment migration errors in staging."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.82,
            urgency=0.79,
            valence=-0.1,
            arousal=0.62,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.84),
        active_goals=[
            {
                "id": 7,
                "name": "ship the MVP this week",
                "description": "User-declared goal: ship the MVP this week",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
        active_tasks=[],
    )

    inferred_task = next(
        intent for intent in result.domain_intents if isinstance(intent, PromoteInferredTaskDomainIntent)
    )
    assert inferred_task.description.startswith("Inferred task from repeated execution evidence:")
    assert inferred_task.status == "blocked"
    assert not any(isinstance(intent, PromoteInferredGoalDomainIntent) for intent in result.domain_intents)


def test_planning_agent_infers_goal_and_task_when_repeated_evidence_has_no_active_goal() -> None:
    result = PlanningAgent().run(
        event=_event(text="Again I am still blocked by deployment migration failures for the MVP release."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.84,
            urgency=0.76,
            valence=-0.08,
            arousal=0.58,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.82),
        active_goals=[],
        active_tasks=[],
    )

    inferred_goal = next(
        intent for intent in result.domain_intents if isinstance(intent, PromoteInferredGoalDomainIntent)
    )
    inferred_task = next(
        intent for intent in result.domain_intents if isinstance(intent, PromoteInferredTaskDomainIntent)
    )
    assert inferred_goal.description.startswith("Inferred goal from repeated execution evidence:")
    assert inferred_goal.name.startswith("stabilize ")
    assert inferred_task.description.startswith("Inferred task from repeated execution evidence:")
    assert inferred_task.status == "blocked"


def test_planning_agent_blocks_inferred_promotion_on_low_trust_with_borderline_importance() -> None:
    result = PlanningAgent().run(
        event=_event(text="Again I am still blocked by deployment migration failures for the MVP release."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.69,
            urgency=0.71,
            valence=-0.08,
            arousal=0.58,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.82),
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "low_trust",
                "confidence": 0.79,
            }
        ],
        active_goals=[],
        active_tasks=[],
    )

    assert len(result.domain_intents) == 1
    assert result.domain_intents[0].intent_type == "noop"
    assert "reason=trust_gate_low_confidence" in result.inferred_promotion_diagnostics


def test_planning_agent_allows_inferred_promotion_on_high_trust_with_lower_importance() -> None:
    result = PlanningAgent().run(
        event=_event(text="Again I am still blocked by deployment migration failures for the MVP release."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.59,
            urgency=0.7,
            valence=-0.08,
            arousal=0.58,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.82),
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "high_trust",
                "confidence": 0.79,
            }
        ],
        active_goals=[],
        active_tasks=[],
    )

    assert any(isinstance(intent, PromoteInferredGoalDomainIntent) for intent in result.domain_intents)
    assert any(isinstance(intent, PromoteInferredTaskDomainIntent) for intent in result.domain_intents)
    assert "reason=gate_open" in result.inferred_promotion_diagnostics
    assert "result=promote_inferred_task" in result.inferred_promotion_diagnostics
    assert "result=promote_inferred_goal" in result.inferred_promotion_diagnostics


def test_planning_agent_requires_explicit_repeated_signal_under_low_trust_even_with_memory_hint() -> None:
    result = PlanningAgent().run(
        event=_event(text="I am blocked by deployment migration failures for the MVP release."),
        context=ContextOutput(
            summary="Relevant recent memory suggests repeated blockers around deployment migration.",
            related_goals=[],
            related_tags=["deploy"],
            risk_level=0.35,
        ),
        motivation=MotivationOutput(
            importance=0.82,
            urgency=0.78,
            valence=-0.08,
            arousal=0.61,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.82),
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "low_trust",
                "confidence": 0.79,
            }
        ],
        active_goals=[],
        active_tasks=[],
    )

    assert len(result.domain_intents) == 1
    assert result.domain_intents[0].intent_type == "noop"
    assert "reason=missing_repeated_signal" in result.inferred_promotion_diagnostics


def test_planning_agent_allows_memory_hint_repetition_gate_for_medium_trust() -> None:
    result = PlanningAgent().run(
        event=_event(text="I am blocked by deployment migration failures for the MVP release."),
        context=ContextOutput(
            summary="Relevant recent memory suggests repeated blockers around deployment migration.",
            related_goals=[],
            related_tags=["deploy"],
            risk_level=0.35,
        ),
        motivation=MotivationOutput(
            importance=0.64,
            urgency=0.62,
            valence=-0.08,
            arousal=0.55,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.82),
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "medium_trust",
                "confidence": 0.79,
            }
        ],
        active_goals=[],
        active_tasks=[],
    )

    assert any(isinstance(intent, PromoteInferredGoalDomainIntent) for intent in result.domain_intents)
    assert any(isinstance(intent, PromoteInferredTaskDomainIntent) for intent in result.domain_intents)
    assert "reason=gate_open" in result.inferred_promotion_diagnostics


def test_planning_agent_emits_maintenance_task_status_intent_when_repeated_blocker_matches_existing_task() -> None:
    result = PlanningAgent().run(
        event=_event(text="Again I am still blocked by deployment migration failures for the MVP release."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.84,
            urgency=0.76,
            valence=-0.08,
            arousal=0.58,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.82),
        active_goals=[
            {
                "id": 7,
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
                "goal_id": 7,
                "name": "deployment migration failures mvp release",
                "description": "Tracked task from earlier turn",
                "priority": "high",
                "status": "todo",
            }
        ],
    )

    maintenance_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, MaintainTaskStatusDomainIntent)
    )
    assert maintenance_intent.status == "blocked"
    assert maintenance_intent.reason == "inferred_repeated_blocker_evidence"
    assert not any(isinstance(intent, PromoteInferredTaskDomainIntent) for intent in result.domain_intents)


def test_planning_agent_does_not_infer_promotion_without_repeated_evidence() -> None:
    result = PlanningAgent().run(
        event=_event(text="I am blocked by deployment migration failures."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.81,
            urgency=0.74,
            valence=-0.05,
            arousal=0.52,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.8),
        active_goals=[],
        active_tasks=[],
    )

    assert len(result.domain_intents) == 1
    assert result.domain_intents[0].intent_type == "noop"
    assert not any(isinstance(intent, PromoteInferredGoalDomainIntent) for intent in result.domain_intents)
    assert not any(isinstance(intent, PromoteInferredTaskDomainIntent) for intent in result.domain_intents)


def test_planning_agent_does_not_infer_promotion_when_repeated_signal_is_weak() -> None:
    result = PlanningAgent().run(
        event=_event(text="Again still blocked by deployment migration failures."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.45,
            urgency=0.42,
            valence=-0.05,
            arousal=0.44,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.77),
        active_goals=[],
        active_tasks=[],
    )

    assert len(result.domain_intents) == 1
    assert result.domain_intents[0].intent_type == "noop"
    assert not any(isinstance(intent, PromoteInferredGoalDomainIntent) for intent in result.domain_intents)
    assert not any(isinstance(intent, PromoteInferredTaskDomainIntent) for intent in result.domain_intents)


def test_planning_agent_avoids_duplicate_inferred_promotions_for_matching_active_state() -> None:
    result = PlanningAgent().run(
        event=_event(text="Again I am still blocked by deployment migration failures for the MVP release."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.84,
            urgency=0.76,
            valence=-0.08,
            arousal=0.58,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.82),
        active_goals=[
            {
                "id": 7,
                "name": "stabilize deployment migration failures mvp release",
                "description": "Inferred goal from repeated execution evidence: stabilize deployment migration failures mvp release",
                "priority": "high",
                "status": "active",
                "goal_type": "tactical",
            }
        ],
        active_tasks=[
            {
                "id": 21,
                "goal_id": 7,
                "name": "deployment migration failures mvp release",
                "description": "Inferred task from repeated execution evidence: deployment migration failures mvp release",
                "priority": "high",
                "status": "blocked",
            }
        ],
    )

    assert len(result.domain_intents) == 1
    assert result.domain_intents[0].intent_type == "noop"
    assert not any(isinstance(intent, PromoteInferredGoalDomainIntent) for intent in result.domain_intents)
    assert not any(isinstance(intent, PromoteInferredTaskDomainIntent) for intent in result.domain_intents)
    assert not any(isinstance(intent, MaintainTaskStatusDomainIntent) for intent in result.domain_intents)


def test_planning_agent_emits_preference_domain_intents_from_explicit_request() -> None:
    result = PlanningAgent().run(
        event=_event(text="Please answer briefly and walk me through this step by step."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.73,
            urgency=0.28,
            valence=0.0,
            arousal=0.35,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    assert any(isinstance(intent, UpdateResponseStyleDomainIntent) for intent in result.domain_intents)
    assert any(isinstance(intent, UpdateCollaborationPreferenceDomainIntent) for intent in result.domain_intents)


def test_planning_agent_emits_reminder_task_and_proactive_preference_from_explicit_request() -> None:
    result = PlanningAgent().run(
        event=_event(text="Remind me to send the release summary tomorrow."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.74,
            urgency=0.34,
            valence=0.0,
            arousal=0.39,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    assert any(isinstance(intent, UpsertTaskDomainIntent) for intent in result.domain_intents)
    assert any(isinstance(intent, UpsertPlannedWorkItemDomainIntent) for intent in result.domain_intents)
    assert any(isinstance(intent, UpdateProactivePreferenceDomainIntent) for intent in result.domain_intents)


def test_planning_agent_emits_recurring_routine_planned_work_from_daily_request() -> None:
    result = PlanningAgent().run(
        event=_event(text="Remind me every day to review my inbox."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.76,
            urgency=0.35,
            valence=0.0,
            arousal=0.38,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    planned_work_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, UpsertPlannedWorkItemDomainIntent)
    )
    assert planned_work_intent.work_kind == "routine"
    assert planned_work_intent.recurrence_mode == "daily"
    assert planned_work_intent.recurrence_rule == ""


def test_planning_agent_emits_custom_recurring_planned_work_rule_from_interval_request() -> None:
    result = PlanningAgent().run(
        event=_event(text="Remind me every 3 days to send the weekly metrics."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.75,
            urgency=0.34,
            valence=0.0,
            arousal=0.36,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    planned_work_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, UpsertPlannedWorkItemDomainIntent)
    )
    assert planned_work_intent.work_kind == "routine"
    assert planned_work_intent.recurrence_mode == "custom"
    assert planned_work_intent.recurrence_rule == "interval_days:3"


def test_planning_agent_emits_planned_work_reschedule_cancel_and_complete_intents() -> None:
    active_planned_work = [
        {
            "id": 11,
            "summary": "send the release summary tomorrow",
            "kind": "reminder",
            "status": "pending",
        }
    ]

    reschedule_result = PlanningAgent().run(
        event=_event(text="Reschedule the release summary reminder to tomorrow."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.72,
            urgency=0.31,
            valence=0.0,
            arousal=0.34,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
        active_planned_work=active_planned_work,
    )
    cancel_result = PlanningAgent().run(
        event=_event(text="Cancel the reminder about the release summary."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.7,
            urgency=0.28,
            valence=0.0,
            arousal=0.31,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
        active_planned_work=active_planned_work,
    )
    complete_result = PlanningAgent().run(
        event=_event(text="I already sent the release summary reminder."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.71,
            urgency=0.27,
            valence=0.0,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
        active_planned_work=active_planned_work,
    )

    assert any(
        isinstance(intent, ReschedulePlannedWorkItemDomainIntent) and intent.work_id == 11
        for intent in reschedule_result.domain_intents
    )
    assert any(
        isinstance(intent, CancelPlannedWorkItemDomainIntent) and intent.work_id == 11
        for intent in cancel_result.domain_intents
    )
    assert any(
        isinstance(intent, CompletePlannedWorkItemDomainIntent) and intent.work_id == 11
        for intent in complete_result.domain_intents
    )


def test_planning_agent_emits_daily_planning_task_from_explicit_request() -> None:
    result = PlanningAgent().run(
        event=_event(text="Help me plan tomorrow."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.72,
            urgency=0.27,
            valence=0.0,
            arousal=0.33,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.7),
    )

    task_intent = next(intent for intent in result.domain_intents if isinstance(intent, UpsertTaskDomainIntent))
    assert task_intent.name == "plan tomorrow"
    assert task_intent.priority == "medium"


def test_planning_agent_emits_noop_domain_intent_when_no_domain_change_detected() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you explain this architecture choice?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.7,
            urgency=0.25,
            valence=0.0,
            arousal=0.3,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
    )

    assert len(result.domain_intents) == 1
    assert result.domain_intents[0].intent_type == "noop"


def test_planning_agent_accepts_single_subconscious_clarifier_and_merges_secondary_nudge() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you help me with this blocker?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.72,
            urgency=0.31,
            valence=0.0,
            arousal=0.34,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        subconscious_proposals=[
            {
                "proposal_id": 101,
                "proposal_type": "ask_user",
                "summary": "Ask the user to clarify blocker scope.",
                "payload": {"question_focus": "blocker scope"},
                "confidence": 0.74,
                "status": "pending",
                "research_policy": "read_only",
                "allowed_tools": ["memory_retrieval"],
            },
            {
                "proposal_id": 102,
                "proposal_type": "nudge_user",
                "summary": "Nudge user toward one concrete unblock step.",
                "payload": {"task_name": "deploy blocker"},
                "confidence": 0.71,
                "status": "pending",
            },
        ],
    )

    assert "ask_subconscious_clarifier" in result.steps
    assert len(result.accepted_proposals) == 1
    assert result.accepted_proposals[0].proposal_id == 101
    assert result.proposal_handoffs[0].proposal_id == 101
    assert result.proposal_handoffs[0].decision == "accept"
    assert result.proposal_handoffs[1].proposal_id == 102
    assert result.proposal_handoffs[1].decision == "merge"


def test_planning_agent_accepts_read_only_research_proposal_when_user_explicitly_requests_research() -> None:
    result = PlanningAgent().run(
        event=_event(text="Please research deployment rollback constraints."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.77,
            urgency=0.29,
            valence=0.0,
            arousal=0.31,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.82),
        subconscious_proposals=[
            {
                "proposal_id": 301,
                "proposal_type": "research_topic",
                "summary": "Research rollback constraints with read-only tools.",
                "payload": {"topic": "deployment rollback"},
                "confidence": 0.7,
                "status": "pending",
                "research_policy": "read_only",
                "allowed_tools": ["memory_retrieval", "knowledge_search"],
            }
        ],
    )

    assert "queue_read_only_research" in result.steps
    assert len(result.accepted_proposals) == 1
    assert result.accepted_proposals[0].proposal_id == 301
    assert result.accepted_proposals[0].research_policy == "read_only"
    assert result.accepted_proposals[0].allowed_tools == ["memory_retrieval", "knowledge_search"]
    assert result.proposal_handoffs[0].decision == "accept"
    assert result.proposal_handoffs[0].reason == "read_only_research_confirmed_by_user_turn"


def test_planning_agent_builds_connector_permission_gates_for_calendar_and_task_connectors() -> None:
    result = PlanningAgent().run(
        event=_event(text="Create calendar meeting tomorrow and create task in ClickUp."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.83,
            urgency=0.76,
            valence=0.05,
            arousal=0.58,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.86),
    )

    calendar_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, CalendarSchedulingIntentDomainIntent)
    )
    task_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, ExternalTaskSyncDomainIntent)
    )

    assert calendar_intent.operation == "create_event"
    assert calendar_intent.mode == "mutate_with_confirmation"
    assert task_intent.operation == "create_task"
    assert task_intent.provider_hint == "clickup"
    assert task_intent.mode == "mutate_with_confirmation"
    assert len(result.connector_permission_gates) == 2
    assert all(gate.requires_opt_in for gate in result.connector_permission_gates)
    assert all(gate.requires_confirmation for gate in result.connector_permission_gates)
    assert all(gate.allowed is False for gate in result.connector_permission_gates)


def test_planning_agent_builds_connected_drive_intent_and_permission_gate() -> None:
    result = PlanningAgent().run(
        event=_event(text="Please upload release notes to Google Drive."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.79,
            urgency=0.54,
            valence=0.02,
            arousal=0.41,
            mode="execute",
        ),
        role=RoleOutput(selected="executor", confidence=0.83),
    )

    drive_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, ConnectedDriveAccessDomainIntent)
    )

    assert drive_intent.operation == "upload_file"
    assert drive_intent.provider_hint == "google_drive"
    assert drive_intent.mode == "mutate_with_confirmation"
    assert len(result.connector_permission_gates) == 1
    gate = result.connector_permission_gates[0]
    assert gate.connector_kind == "cloud_drive"
    assert gate.operation == "upload_file"
    assert gate.requires_opt_in is True
    assert gate.requires_confirmation is True
    assert gate.allowed is False


def test_planning_agent_builds_allowed_connector_permission_gates_for_read_and_suggestion_posture() -> None:
    result = PlanningAgent().run(
        event=_event(text="When can we use the calendar next week, list tasks in ClickUp and suggest how to organize files in Google Drive."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.7,
            urgency=0.33,
            valence=0.02,
            arousal=0.36,
            mode="analyze",
        ),
        role=RoleOutput(selected="advisor", confidence=0.82),
    )

    calendar_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, CalendarSchedulingIntentDomainIntent)
    )
    calendar_gate = next(
        gate for gate in result.connector_permission_gates if gate.connector_kind == "calendar"
    )
    task_gate = next(
        gate for gate in result.connector_permission_gates if gate.connector_kind == "task_system"
    )
    drive_gate = next(
        gate for gate in result.connector_permission_gates if gate.connector_kind == "cloud_drive"
    )

    assert calendar_intent.operation == "read_availability"
    assert calendar_intent.provider_hint == "google_calendar"
    assert calendar_gate.operation == "read_availability"
    assert calendar_gate.allowed is True
    assert calendar_gate.requires_confirmation is False
    assert calendar_gate.reason == "suggestion_or_read_only_allowed"

    assert task_gate.operation == "list_tasks"
    assert task_gate.allowed is True
    assert task_gate.requires_confirmation is False
    assert task_gate.reason == "suggestion_or_read_only_allowed"

    assert drive_gate.operation == "suggest_file_plan"
    assert drive_gate.allowed is True
    assert drive_gate.requires_confirmation is False
    assert drive_gate.reason == "suggestion_or_read_only_allowed"


def test_planning_agent_selects_google_drive_for_bounded_list_files_baseline() -> None:
    result = PlanningAgent().run(
        event=_event(text="List files in drive for the release notes folder."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.68,
            urgency=0.31,
            valence=0.02,
            arousal=0.34,
            mode="analyze",
        ),
        role=RoleOutput(selected="advisor", confidence=0.82),
    )

    drive_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, ConnectedDriveAccessDomainIntent)
    )
    drive_gate = next(
        gate for gate in result.connector_permission_gates if gate.connector_kind == "cloud_drive"
    )

    assert drive_intent.operation == "list_files"
    assert drive_intent.provider_hint == "google_drive"
    assert drive_intent.mode == "read_only"
    assert drive_gate.operation == "list_files"
    assert drive_gate.allowed is True
    assert drive_gate.requires_confirmation is False


def test_planning_agent_promotes_connector_expansion_proposal_into_discovery_intent() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can we integrate ClickUp with this assistant for task sync?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.74,
            urgency=0.37,
            valence=0.01,
            arousal=0.33,
            mode="analyze",
        ),
        role=RoleOutput(selected="advisor", confidence=0.79),
        subconscious_proposals=[
            {
                "proposal_id": 901,
                "proposal_type": "suggest_connector_expansion",
                "summary": "Suggest connector expansion for clickup task_system capability 'task_sync'.",
                "payload": {
                    "connector_kind": "task_system",
                    "provider_hint": "clickup",
                    "requested_capability": "task_sync",
                },
                "confidence": 0.78,
                "status": "pending",
                "research_policy": "read_only",
                "allowed_tools": [],
            }
        ],
    )

    assert "propose_connector_capability_expansion" in result.steps
    assert result.proposal_handoffs[0].decision == "accept"
    assert result.proposal_handoffs[0].reason == "connector_capability_gap_detected"
    discovery_intent = next(
        intent for intent in result.domain_intents if isinstance(intent, ConnectorCapabilityDiscoveryDomainIntent)
    )
    assert discovery_intent.connector_kind == "task_system"
    assert discovery_intent.provider_hint == "clickup"
    assert discovery_intent.requested_capability == "task_sync"
    assert discovery_intent.mode == "suggestion_only"
    discovery_gate = next(
        gate
        for gate in result.connector_permission_gates
        if gate.connector_kind == "task_system" and gate.operation == "discover_task_sync"
    )
    assert discovery_gate.allowed is True
    assert discovery_gate.requires_opt_in is False
    assert discovery_gate.requires_confirmation is False
    assert discovery_gate.reason == "proposal_only_no_external_access"


def test_planning_agent_skips_non_retriable_subconscious_proposal_statuses() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you help me with this blocker?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.72,
            urgency=0.31,
            valence=0.0,
            arousal=0.34,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        subconscious_proposals=[
            {
                "proposal_id": 501,
                "proposal_type": "ask_user",
                "summary": "Already accepted proposal should not be re-processed.",
                "payload": {"question_focus": "already accepted"},
                "confidence": 0.77,
                "status": "accepted",
                "research_policy": "read_only",
                "allowed_tools": ["memory_retrieval"],
            },
            {
                "proposal_id": 502,
                "proposal_type": "nudge_user",
                "summary": "Discarded proposal should not be re-processed.",
                "payload": {"task_name": "legacy blocker"},
                "confidence": 0.65,
                "status": "discarded",
            },
            {
                "proposal_id": 503,
                "proposal_type": "ask_user",
                "summary": "Deferred proposal can re-enter conscious turn.",
                "payload": {"question_focus": "current blocker scope"},
                "confidence": 0.71,
                "status": "deferred",
                "research_policy": "read_only",
                "allowed_tools": ["memory_retrieval"],
            },
        ],
    )

    assert len(result.proposal_handoffs) == 1
    assert result.proposal_handoffs[0].proposal_id == 503
    assert result.proposal_handoffs[0].decision == "accept"
    assert len(result.accepted_proposals) == 1
    assert result.accepted_proposals[0].proposal_id == 503
    assert "ask_subconscious_clarifier" in result.steps


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


def test_planning_agent_ignores_subthreshold_theta_for_generic_turn() -> None:
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
            "support_bias": 0.15,
            "analysis_bias": 0.57,
            "execution_bias": 0.28,
        },
    )

    assert result.steps == [
        "interpret_event",
        "review_context",
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


def test_planning_agent_uses_relation_signals_for_collaboration_and_support_steps() -> None:
    result = PlanningAgent().run(
        event=_event(text="help me with this"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.52,
            urgency=0.2,
            valence=0.05,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.6),
        relations=[
            {
                "relation_type": "collaboration_dynamic",
                "relation_value": "guided",
                "confidence": 0.79,
            },
            {
                "relation_type": "support_intensity_preference",
                "relation_value": "high_support",
                "confidence": 0.76,
            },
        ],
    )

    assert result.goal == "Guide the user through the next step in a calm, step by step way."
    assert "favor_guided_walkthrough" in result.steps
    assert "maintain_supportive_stance" in result.steps


def test_planning_agent_ignores_subthreshold_relation_signals_for_collaboration_and_support_steps() -> None:
    result = PlanningAgent().run(
        event=_event(text="help me with this"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.52,
            urgency=0.2,
            valence=0.05,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.6),
        relations=[
            {
                "relation_type": "collaboration_dynamic",
                "relation_value": "guided",
                "confidence": 0.67,
            },
            {
                "relation_type": "support_intensity_preference",
                "relation_value": "high_support",
                "confidence": 0.67,
            },
            {
                "relation_type": "delivery_reliability",
                "relation_value": "high_trust",
                "confidence": 0.67,
            },
        ],
    )

    assert result.goal == "Provide a clear and useful response to the user event."
    assert result.steps == [
        "interpret_event",
        "review_context",
        "prepare_response",
    ]


def test_planning_agent_calibrates_planning_confidence_from_delivery_reliability() -> None:
    high_trust = PlanningAgent().run(
        event=_event(text="help me with this"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.52,
            urgency=0.2,
            valence=0.05,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.6),
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "high_trust",
                "confidence": 0.79,
            }
        ],
    )
    low_trust = PlanningAgent().run(
        event=_event(text="help me with this"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.52,
            urgency=0.2,
            valence=0.05,
            arousal=0.3,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.6),
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "low_trust",
                "confidence": 0.79,
            }
        ],
    )

    assert "plan_with_confident_next_step" in high_trust.steps
    assert "favor_concrete_next_step" in high_trust.steps
    assert "plan_with_cautious_validation" in low_trust.steps
    assert "quick verification check" in low_trust.goal.lower()


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


def test_planning_agent_targets_matching_goal_when_multiple_goals_are_active() -> None:
    result = PlanningAgent().run(
        event=_event(text="Can you help me close tax filing and finish invoices?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.82,
            urgency=0.38,
            valence=0.05,
            arousal=0.42,
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
            },
            {
                "id": 22,
                "name": "close tax filing",
                "description": "User-declared goal: close tax filing",
                "priority": "medium",
                "status": "active",
                "goal_type": "operational",
            },
        ],
        active_tasks=[
            {
                "id": 31,
                "goal_id": 11,
                "name": "fix deployment blocker",
                "description": "User-declared task: fix deployment blocker",
                "priority": "high",
                "status": "blocked",
            },
            {
                "id": 32,
                "goal_id": 22,
                "name": "prepare tax documents",
                "description": "User-declared task: prepare tax documents",
                "priority": "high",
                "status": "in_progress",
            },
        ],
    )

    assert "close tax filing" in result.goal
    assert "ship the MVP this week" not in result.goal
    assert "align_with_active_goal" in result.steps
    assert "advance_active_task" in result.steps


def test_planning_agent_aligns_with_active_milestone() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
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
        active_goal_milestones=[
            {
                "id": 41,
                "goal_id": 11,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
            }
        ],
    )

    assert "Drive goal to closure" in result.goal
    assert "align_with_active_milestone" in result.steps


def test_planning_agent_uses_active_milestone_risk_and_completion_criteria() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.89,
            urgency=0.45,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={
            "goal_milestone_risk": "ready_to_close",
            "goal_completion_criteria": "finish_remaining_active_work",
        },
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
        active_goal_milestones=[
            {
                "id": 41,
                "goal_id": 11,
                "name": "Drive goal to closure",
                "phase": "completion_window",
                "status": "active",
                "risk_level": "ready_to_close",
                "completion_criteria": "finish_remaining_active_work",
            }
        ],
    )

    assert "ready_to_close" in result.goal
    assert "finish remaining active work" in result.goal
    assert "validate_milestone_closure" in result.steps
    assert "finish_remaining_active_work" in result.steps


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


def test_planning_agent_adds_reduce_milestone_risk_step() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.84,
            urgency=0.38,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_milestone_risk": "at_risk"},
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
    assert "reduce_milestone_risk" in result.steps


def test_planning_agent_adds_confirm_goal_completion_step() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.85,
            urgency=0.4,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_completion_criteria": "confirm_goal_completion"},
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
    assert "confirm_goal_completion" in result.steps


def test_planning_agent_adds_milestone_arc_step_for_closure_momentum() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.86,
            urgency=0.4,
            valence=0.05,
            arousal=0.45,
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
        goal_milestone_history=[
            {"goal_id": 11, "phase": "completion_window", "risk_level": "ready_to_close"},
            {"goal_id": 11, "phase": "recovery_phase", "risk_level": "stabilizing"},
        ],
    )

    assert "align_with_active_goal" in result.steps
    assert "protect_milestone_closure_arc" in result.steps


def test_planning_agent_adds_milestone_arc_step_for_reentered_completion_window() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.89,
            urgency=0.43,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_milestone_arc": "reentered_completion_window"},
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
    assert "stabilize_reentered_completion_window" in result.steps


def test_planning_agent_adds_milestone_pressure_step_for_lingering_completion() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.91,
            urgency=0.46,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_milestone_pressure": "lingering_completion"},
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
    assert "force_goal_closure_decision" in result.steps


def test_planning_agent_adds_milestone_dependency_step_for_blocked_dependency() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.91,
            urgency=0.46,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_milestone_dependency_state": "blocked_dependency"},
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
    assert "resolve_blocking_dependency" in result.steps


def test_planning_agent_adds_milestone_due_step_for_dependency_due_next() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.92,
            urgency=0.49,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_milestone_due_state": "dependency_due_next"},
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
    assert "finish_due_dependency" in result.steps


def test_planning_agent_adds_milestone_due_window_step_for_overdue_window() -> None:
    result = PlanningAgent().run(
        event=_event(text="What should I do next for the MVP?"),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.94,
            urgency=0.51,
            valence=0.05,
            arousal=0.45,
            mode="analyze",
        ),
        role=RoleOutput(selected="analyst", confidence=0.8),
        user_preferences={"goal_milestone_due_window": "overdue_due_window"},
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
    assert "recover_overdue_window" in result.steps


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


def test_planning_agent_builds_proactive_warning_plan_when_interrupt_is_allowed() -> None:
    result = PlanningAgent().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "chat_id": 123456,
                "proactive": {
                    "trigger": "task_blocked",
                    "importance": 0.88,
                    "urgency": 0.9,
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
        motivation=MotivationOutput(
            importance=0.9,
            urgency=0.9,
            valence=-0.1,
            arousal=0.8,
            mode="execute",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        user_preferences={"proactive_opt_in": True},
        active_tasks=[{"id": 21, "name": "fix deploy blocker", "status": "blocked"}],
    )

    assert result.proactive_decision is not None
    assert result.proactive_decision.output_type == "warning"
    assert result.proactive_decision.should_interrupt is True
    assert result.goal == "Deliver a proactive warning with one clear immediate next step."
    assert "compose_proactive_warning" in result.steps
    assert "prioritize_immediate_attention" in result.steps
    assert "send_telegram_message" in result.steps
    assert result.needs_response is True


def test_planning_agent_persists_communication_boundary_directives_as_relations() -> None:
    result = PlanningAgent().run(
        event=_event(text="Nie pisz do mnie co pol godziny i nie musisz sie witac co wiadomosc."),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.7,
            urgency=0.2,
            valence=0.0,
            arousal=0.2,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
    )

    relation_intents = [
        intent for intent in result.domain_intents if isinstance(intent, MaintainRelationDomainIntent)
    ]
    assert {
        (intent.relation_type, intent.relation_value)
        for intent in relation_intents
    } >= {
        ("contact_cadence_preference", "low_frequency"),
        ("interaction_ritual_preference", "avoid_repeated_greeting"),
    }


def test_planning_agent_defers_proactive_outreach_when_contact_cadence_is_on_demand() -> None:
    result = PlanningAgent().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "chat_id": 123456,
                "proactive": {
                    "trigger": "task_blocked",
                    "importance": 0.9,
                    "urgency": 0.9,
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
        motivation=MotivationOutput(
            importance=0.9,
            urgency=0.9,
            valence=0.0,
            arousal=0.4,
            mode="execute",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        user_preferences={"proactive_opt_in": True},
        relations=[
            {
                "relation_type": "contact_cadence_preference",
                "relation_value": "on_demand",
                "confidence": 0.96,
            }
        ],
        active_tasks=[{"id": 21, "name": "fix deploy blocker", "status": "blocked"}],
    )

    assert result.proactive_decision is not None
    assert result.proactive_decision.should_interrupt is False
    assert result.proactive_decision.reason == "contact_cadence_on_demand"
    assert result.needs_response is False
    assert result.needs_action is False
    assert result.domain_intents[0].intent_type == "update_proactive_state"
    assert result.domain_intents[0].state == "interruption_deferred"
    assert result.domain_intents[0].trigger == "task_blocked"


def test_planning_agent_calibrates_proactive_outreach_tone_for_low_trust_relation() -> None:
    result = PlanningAgent().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "chat_id": 123456,
                "proactive": {
                    "trigger": "task_blocked",
                    "importance": 0.92,
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
        motivation=MotivationOutput(
            importance=0.9,
            urgency=0.9,
            valence=-0.1,
            arousal=0.8,
            mode="execute",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        user_preferences={"proactive_opt_in": True},
        relations=[
            {
                "relation_type": "delivery_reliability",
                "relation_value": "low_trust",
                "confidence": 0.8,
            }
        ],
        active_tasks=[{"id": 21, "name": "fix deploy blocker", "status": "blocked"}],
    )

    assert result.proactive_decision is not None
    assert result.proactive_decision.output_type == "reminder"
    assert result.proactive_decision.should_interrupt is True
    assert "use_low_pressure_outreach_tone" in result.steps
    assert "low-pressure and verification-oriented" in result.goal.lower()


def test_planning_agent_defers_proactive_outreach_when_interruption_cost_is_high() -> None:
    result = PlanningAgent().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "proactive": {
                    "trigger": "goal_stagnation",
                    "importance": 0.82,
                    "urgency": 0.72,
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
        motivation=MotivationOutput(
            importance=0.8,
            urgency=0.6,
            valence=0.0,
            arousal=0.2,
            mode="ignore",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        active_goals=[{"id": 11, "name": "ship the MVP this week", "status": "active"}],
    )

    assert result.proactive_decision is not None
    assert result.proactive_decision.should_interrupt is False
    assert result.goal == "Defer proactive outreach until interruption cost becomes acceptable."
    assert "defer_proactive_outreach" in result.steps
    assert result.needs_response is False
    assert result.needs_action is False
    assert result.domain_intents[0].intent_type == "update_proactive_state"
    assert result.domain_intents[0].state == "interruption_deferred"


def test_planning_agent_keeps_plain_time_checkin_silent_without_active_work_or_strong_relation_signal() -> None:
    result = PlanningAgent().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "chat_id": 123456,
                "proactive": {
                    "trigger": "time_checkin",
                    "user_context": {
                        "quiet_hours": False,
                        "focus_mode": False,
                        "recent_user_activity": "away",
                        "recent_outbound_count": 0,
                        "unanswered_proactive_count": 0,
                    },
                },
            }
        ),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.3,
            urgency=0.2,
            valence=0.0,
            arousal=0.1,
            mode="ignore",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        user_preferences={"proactive_opt_in": True},
    )

    assert result.proactive_decision is not None
    assert result.proactive_decision.trigger == "time_checkin"
    assert result.proactive_decision.should_interrupt is False
    assert result.goal == "Defer proactive outreach until interruption cost becomes acceptable."
    assert result.needs_response is False
    assert result.needs_action is False
    assert result.domain_intents[0].state == "interruption_deferred"


def test_planning_agent_defers_proactive_outreach_when_opt_in_is_missing() -> None:
    result = PlanningAgent().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "chat_id": 123456,
                "proactive": {
                    "trigger": "task_blocked",
                    "importance": 0.9,
                    "urgency": 0.85,
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
        motivation=MotivationOutput(
            importance=0.86,
            urgency=0.82,
            valence=0.0,
            arousal=0.4,
            mode="execute",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        active_tasks=[{"id": 11, "name": "fix deploy blocker", "status": "blocked"}],
    )

    assert result.proactive_decision is not None
    assert result.proactive_decision.should_interrupt is True
    assert result.proactive_delivery_guard is not None
    assert result.proactive_delivery_guard.allowed is False
    assert result.proactive_delivery_guard.reason == "opt_in_required"
    assert result.goal == "Defer proactive outreach until delivery guardrails pass."
    assert "respect_proactive_delivery_guardrails" in result.steps
    assert result.needs_response is False
    assert result.needs_action is False
    assert result.domain_intents[0].intent_type == "update_proactive_state"
    assert result.domain_intents[0].state == "delivery_guard_blocked"


def test_planning_agent_respects_attention_gate_before_other_proactive_delivery_logic() -> None:
    result = PlanningAgent().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick",
                "proactive": {
                    "trigger": "task_blocked",
                    "importance": 0.9,
                    "urgency": 0.87,
                    "user_context": {
                        "quiet_hours": False,
                        "focus_mode": False,
                        "recent_user_activity": "active",
                        "recent_outbound_count": 0,
                        "unanswered_proactive_count": 0,
                    },
                },
                "attention_gate": {
                    "allowed": False,
                    "reason": "attention_outbound_cooldown",
                    "recent_outbound_count": 4,
                    "unanswered_proactive_count": 1,
                },
            }
        ),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.86,
            urgency=0.82,
            valence=0.0,
            arousal=0.4,
            mode="execute",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        user_preferences={"proactive_opt_in": True},
        active_tasks=[{"id": 11, "name": "fix deploy blocker", "status": "blocked"}],
    )

    assert result.proactive_decision is not None
    assert result.goal == "Defer proactive outreach until attention-gate conditions are satisfied."
    assert result.steps == ["evaluate_proactive_trigger", "assess_user_context", "respect_attention_gate"]
    assert result.needs_response is False
    assert result.needs_action is False
    assert result.domain_intents[0].intent_type == "update_proactive_state"
    assert result.domain_intents[0].state == "attention_gate_blocked"


def test_planning_agent_keeps_proactive_path_separate_from_proposal_handoff_and_connector_intents() -> None:
    result = PlanningAgent().run(
        event=_scheduler_event(
            {
                "text": "scheduler proactive tick please connect clickup and calendar",
                "chat_id": 123456,
                "proactive": {
                    "trigger": "task_blocked",
                    "importance": 0.88,
                    "urgency": 0.9,
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
        motivation=MotivationOutput(
            importance=0.9,
            urgency=0.9,
            valence=-0.1,
            arousal=0.8,
            mode="execute",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        user_preferences={"proactive_opt_in": True},
        active_tasks=[{"id": 21, "name": "fix deploy blocker", "status": "blocked"}],
        subconscious_proposals=[
            {
                "proposal_id": 901,
                "proposal_type": "ask_user",
                "summary": "Clarify blocker details.",
                "payload": {"question_focus": "blocker"},
                "confidence": 0.74,
                "status": "pending",
            },
            {
                "proposal_id": 902,
                "proposal_type": "suggest_connector_expansion",
                "summary": "Suggest clickup task sync connector expansion.",
                "payload": {
                    "connector_kind": "task_system",
                    "provider_hint": "clickup",
                    "requested_capability": "task_sync",
                },
                "confidence": 0.78,
                "status": "pending",
            },
        ],
    )

    assert result.proactive_decision is not None
    assert result.needs_response is True
    assert result.needs_action is True
    assert result.domain_intents[0].intent_type == "update_proactive_state"
    assert result.domain_intents[0].state == "delivery_ready"
    assert result.proposal_handoffs == []
    assert result.accepted_proposals == []
    assert result.connector_permission_gates == []


def test_planning_agent_accepts_scheduler_due_planned_work_handoff_for_foreground_delivery() -> None:
    result = PlanningAgent().run(
        event=Event(
            event_id="evt-scheduler-due-1",
            source="scheduler",
            subsource="maintenance_tick",
            timestamp=datetime.now(timezone.utc),
            payload={
                "text": "planned work due: send the release summary",
                "chat_id": 123456,
                "planned_work_due": {
                    "work_id": 9,
                    "summary": "send the release summary",
                    "work_kind": "reminder",
                    "delivery_channel": "telegram",
                    "source_event_id": "evt-reminder-1",
                },
            },
            meta=EventMeta(user_id="123456", trace_id="t-scheduler-due-1"),
        ),
        context=_context(),
        motivation=MotivationOutput(
            importance=0.78,
            urgency=0.66,
            valence=0.0,
            arousal=0.48,
            mode="execute",
        ),
        role=RoleOutput(selected="advisor", confidence=0.8),
        subconscious_proposals=[
            {
                "proposal_id": 611,
                "proposal_type": "nudge_user",
                "summary": "planned_work_due:9:send the release summary",
                "payload": {
                    "handoff_kind": "planned_work_due",
                    "work_id": 9,
                    "work_kind": "reminder",
                    "summary": "send the release summary",
                    "delivery_channel": "telegram",
                    "source_event_id": "evt-reminder-1",
                },
                "confidence": 0.82,
                "status": "pending",
            }
        ],
    )

    assert result.goal == "Deliver the due planned-work follow-up with one clear immediate next step."
    assert result.steps == [
        "interpret_event",
        "review_context",
        "integrate_subconscious_nudge",
        "prepare_response",
        "send_telegram_message",
    ]
    assert result.needs_response is True
    assert result.needs_action is True
    assert len(result.accepted_proposals) == 1
    assert result.accepted_proposals[0].proposal_id == 611
    assert result.proposal_handoffs[0].decision == "accept"
    assert result.proposal_handoffs[0].reason == "scheduled_due_planned_work_handoff"
