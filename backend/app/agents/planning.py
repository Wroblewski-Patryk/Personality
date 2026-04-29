import re
from datetime import timedelta

from app.core.adaptive_policy import dominant_theta_channel, relation_value
from app.core.contracts import (
    CancelPlannedWorkItemDomainIntent,
    CalendarSchedulingIntentDomainIntent,
    CompletePlannedWorkItemDomainIntent,
    ConnectedDriveAccessDomainIntent,
    ConnectorCapabilityDiscoveryDomainIntent,
    ConnectorPermissionGateOutput,
    ContextOutput,
    DomainActionIntent,
    Event,
    ExternalTaskSyncDomainIntent,
    MaintainTaskStatusDomainIntent,
    MotivationOutput,
    NoopDomainIntent,
    PlanOutput,
    PromoteInferredGoalDomainIntent,
    PromoteInferredTaskDomainIntent,
    ProactiveDecisionOutput,
    ProposalHandoffDecisionOutput,
    ReschedulePlannedWorkItemDomainIntent,
    RoleOutput,
    SubconsciousProposalRecord,
    KnowledgeSearchDomainIntent,
    MaintainRelationDomainIntent,
    UpsertPlannedWorkItemDomainIntent,
    WebBrowserAccessDomainIntent,
    UpdateProactiveStateDomainIntent,
    UpdateProactivePreferenceDomainIntent,
    UpdateCollaborationPreferenceDomainIntent,
    UpdateResponseStyleDomainIntent,
    UpdateTaskStatusDomainIntent,
    UpsertGoalDomainIntent,
    UpsertTaskDomainIntent,
)
from app.communication.boundary import extract_communication_boundary_signals
from app.core.connector_policy import (
    build_connector_permission_gate,
    resolve_connector_capability_discovery_policy,
    resolve_connector_operation_policy,
)
from app.proactive.engine import ProactiveDecisionEngine, ProactiveDeliveryGuard
from app.utils.goal_task_signals import detect_goal_signal, detect_task_signal, detect_task_status_signal
from app.utils.language import normalize_for_matching
from app.utils.preferences import (
    detect_collaboration_preference,
    detect_proactive_preference,
    detect_response_style_preference,
)
from app.utils.goal_task_selection import (
    priority_rank as shared_priority_rank,
    select_relevant_goal as shared_select_relevant_goal,
    select_relevant_task as shared_select_relevant_task,
    task_status_rank as shared_task_status_rank,
    text_tokens as shared_text_tokens,
)
from app.utils.progress_signals import (
    goal_history_signal as shared_goal_history_signal,
    goal_milestone_arc_signal as shared_goal_milestone_arc_signal,
)


class PlanningAgent:
    def __init__(
        self,
        proactive_decision_engine: ProactiveDecisionEngine | None = None,
        proactive_delivery_guard: ProactiveDeliveryGuard | None = None,
    ):
        self.proactive_decision_engine = proactive_decision_engine or ProactiveDecisionEngine()
        self.proactive_delivery_guard = proactive_delivery_guard or ProactiveDeliveryGuard()

    def run(
        self,
        event: Event,
        context: ContextOutput,
        motivation: MotivationOutput,
        role: RoleOutput,
        user_preferences: dict | None = None,
        relations: list[dict] | None = None,
        theta: dict | None = None,
        active_goals: list[dict] | None = None,
        active_tasks: list[dict] | None = None,
        active_planned_work: list[dict] | None = None,
        active_goal_milestones: list[dict] | None = None,
        goal_milestone_history: list[dict] | None = None,
        goal_progress_history: list[dict] | None = None,
        subconscious_proposals: list[dict] | None = None,
    ) -> PlanOutput:
        event_text = str(event.payload.get("text", ""))
        goal = "Provide a clear and useful response to the user event."
        steps = ["interpret_event", "review_context"]
        response_style = str((user_preferences or {}).get("response_style", "")).strip().lower()
        collaboration_preference = str((user_preferences or {}).get("collaboration_preference", "")).strip().lower()
        goal_execution_state = str((user_preferences or {}).get("goal_execution_state", "")).strip().lower()
        goal_progress_score = float((user_preferences or {}).get("goal_progress_score", 0.0) or 0.0)
        goal_progress_trend = str((user_preferences or {}).get("goal_progress_trend", "")).strip().lower()
        goal_progress_arc = str((user_preferences or {}).get("goal_progress_arc", "")).strip().lower()
        goal_milestone_state = str((user_preferences or {}).get("goal_milestone_state", "")).strip().lower()
        goal_milestone_arc = str((user_preferences or {}).get("goal_milestone_arc", "")).strip().lower()
        goal_milestone_pressure = str((user_preferences or {}).get("goal_milestone_pressure", "")).strip().lower()
        goal_milestone_dependency_state = str((user_preferences or {}).get("goal_milestone_dependency_state", "")).strip().lower()
        goal_milestone_due_state = str((user_preferences or {}).get("goal_milestone_due_state", "")).strip().lower()
        goal_milestone_due_window = str((user_preferences or {}).get("goal_milestone_due_window", "")).strip().lower()
        goal_milestone_transition = str((user_preferences or {}).get("goal_milestone_transition", "")).strip().lower()
        goal_milestone_risk = str((user_preferences or {}).get("goal_milestone_risk", "")).strip().lower()
        goal_completion_criteria = str((user_preferences or {}).get("goal_completion_criteria", "")).strip().lower()
        relation_collaboration = relation_value(relations=relations or [], relation_type="collaboration_dynamic")
        relation_support = relation_value(relations=relations or [], relation_type="support_intensity_preference")
        relation_delivery = relation_value(relations=relations or [], relation_type="delivery_reliability")
        goal_milestone_arc_signal = goal_milestone_arc or self._goal_milestone_arc_signal(goal_milestone_history or [])
        goal_history_signal = self._goal_history_signal(goal_progress_history or [])
        proactive_decision = self.proactive_decision_engine.decide(
            event=event,
            context=context,
            user_preferences=user_preferences or {},
            relations=relations or [],
            theta=theta,
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
        )
        if proactive_decision is not None:
            return self._build_proactive_plan(
                event=event,
                motivation=motivation,
                proactive_decision=proactive_decision,
                user_preferences=user_preferences or {},
                relations=relations or [],
            )

        if motivation.mode == "clarify":
            goal = "Ask for the missing information needed to help."
            steps.extend(["request_missing_input", "prepare_response"])
        elif role.selected == "friend" or motivation.valence <= -0.3:
            goal = "Provide grounded emotional support and one manageable next step."
            steps.extend(["acknowledge_emotion", "reduce_pressure", "prepare_response"])
        elif motivation.mode == "execute" or role.selected == "executor":
            goal = "Move the requested task toward execution with the smallest concrete next step."
            steps.extend(["identify_requested_change", "propose_execution_step", "prepare_response"])
        elif motivation.mode == "analyze" or role.selected == "analyst":
            goal = "Explain the situation clearly and suggest a structured next step."
            steps.extend(["break_down_problem", "highlight_next_step", "prepare_response"])
        elif role.selected == "mentor":
            goal = "Guide the user toward a confident next step."
            steps.extend(["offer_guidance", "prepare_response"])
        else:
            steps.append("prepare_response")

        needs_response = motivation.mode != "ignore"
        needs_action = event.source == "telegram" and needs_response
        if needs_action:
            steps.append("send_telegram_message")

        if response_style == "concise" and "keep_response_concise" not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, "keep_response_concise")
        elif response_style == "structured" and "format_response_as_bullets" not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, "format_response_as_bullets")

        goal = self._apply_collaboration_preference_goal(
            goal=goal,
            collaboration_preference=collaboration_preference,
            motivation=motivation,
            role=role,
        )
        collaboration_step = self._collaboration_plan_step(
            collaboration_preference=collaboration_preference,
            steps=steps,
        )
        if collaboration_step is not None and collaboration_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, collaboration_step)
        relation_collaboration_step = self._collaboration_plan_step(
            collaboration_preference=relation_collaboration or "",
            steps=steps,
        )
        if relation_collaboration_step is not None and relation_collaboration_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, relation_collaboration_step)
            if not collaboration_preference:
                goal = self._apply_collaboration_preference_goal(
                    goal=goal,
                    collaboration_preference=relation_collaboration or "",
                    motivation=motivation,
                    role=role,
                )
        if relation_support == "high_support" and "maintain_supportive_stance" not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, "maintain_supportive_stance")
        trust_confidence_step = self._delivery_reliability_confidence_step(
            relation_delivery=relation_delivery,
            steps=steps,
        )
        if trust_confidence_step is not None and trust_confidence_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, trust_confidence_step)
        if relation_delivery == "high_trust" and "favor_concrete_next_step" not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, "favor_concrete_next_step")
        goal = self._apply_delivery_reliability_goal(
            goal=goal,
            relation_delivery=relation_delivery or "",
            motivation=motivation,
            role=role,
        )

        theta_step = self._theta_plan_step(theta=theta, steps=steps)
        if theta_step is not None and theta_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, theta_step)

        relevant_goal = self._select_relevant_goal(event=event, active_goals=active_goals or [])
        if relevant_goal is not None:
            goal = self._apply_active_goal(goal=goal, relevant_goal=relevant_goal)
            if "align_with_active_goal" not in steps:
                prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
                steps.insert(prepare_index, "align_with_active_goal")
        relevant_milestone = self._select_relevant_milestone(
            active_goal_milestones=active_goal_milestones or [],
            relevant_goal_id=int(relevant_goal["id"]) if relevant_goal and relevant_goal.get("id") is not None else None,
        )
        if relevant_milestone is not None:
            goal = self._apply_active_milestone(goal=goal, relevant_milestone=relevant_milestone)
            goal = self._apply_active_milestone_signals(goal=goal, relevant_milestone=relevant_milestone)
            if "align_with_active_milestone" not in steps:
                prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
                steps.insert(prepare_index, "align_with_active_milestone")

        relevant_task = self._select_relevant_task(
            event=event,
            active_tasks=active_tasks or [],
            relevant_goal_id=int(relevant_goal["id"]) if relevant_goal and relevant_goal.get("id") is not None else None,
        )
        task_step = self._task_plan_step(relevant_task)
        if task_step is not None and task_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, task_step)

        goal_state_step = self._goal_execution_step(goal_execution_state=goal_execution_state, steps=steps)
        if goal_state_step is not None and goal_state_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_state_step)

        goal_progress_step = self._goal_progress_step(goal_progress_score=goal_progress_score, steps=steps)
        if goal_progress_step is not None and goal_progress_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_progress_step)

        goal_progress_trend_step = self._goal_progress_trend_step(
            goal_progress_trend=goal_progress_trend,
            steps=steps,
        )
        if goal_progress_trend_step is not None and goal_progress_trend_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_progress_trend_step)

        goal_history_step = self._goal_history_step(goal_history_signal=goal_history_signal, steps=steps)
        if goal_history_step is not None and goal_history_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_history_step)

        goal_progress_arc_step = self._goal_progress_arc_step(goal_progress_arc=goal_progress_arc, steps=steps)
        if goal_progress_arc_step is not None and goal_progress_arc_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_progress_arc_step)

        goal_milestone_state_step = self._goal_milestone_state_step(
            goal_milestone_state=goal_milestone_state,
            steps=steps,
        )
        if goal_milestone_state_step is not None and goal_milestone_state_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_milestone_state_step)

        goal_milestone_transition_step = self._goal_milestone_transition_step(
            goal_milestone_transition=goal_milestone_transition,
            steps=steps,
        )
        if goal_milestone_transition_step is not None and goal_milestone_transition_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_milestone_transition_step)

        goal_milestone_risk_step = self._goal_milestone_risk_step(
            goal_milestone_risk=goal_milestone_risk,
            steps=steps,
        )
        if goal_milestone_risk_step is not None and goal_milestone_risk_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_milestone_risk_step)

        goal_milestone_pressure_step = self._goal_milestone_pressure_step(
            goal_milestone_pressure=goal_milestone_pressure,
            steps=steps,
        )
        if goal_milestone_pressure_step is not None and goal_milestone_pressure_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_milestone_pressure_step)

        goal_milestone_dependency_step = self._goal_milestone_dependency_step(
            goal_milestone_dependency_state=goal_milestone_dependency_state,
            steps=steps,
        )
        if goal_milestone_dependency_step is not None and goal_milestone_dependency_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_milestone_dependency_step)

        goal_milestone_due_step = self._goal_milestone_due_step(
            goal_milestone_due_state=goal_milestone_due_state,
            steps=steps,
        )
        if goal_milestone_due_step is not None and goal_milestone_due_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_milestone_due_step)

        goal_milestone_due_window_step = self._goal_milestone_due_window_step(
            goal_milestone_due_window=goal_milestone_due_window,
            steps=steps,
        )
        if goal_milestone_due_window_step is not None and goal_milestone_due_window_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_milestone_due_window_step)

        goal_completion_criteria_step = self._goal_completion_criteria_step(
            goal_completion_criteria=goal_completion_criteria,
            steps=steps,
        )
        if goal_completion_criteria_step is not None and goal_completion_criteria_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_completion_criteria_step)

        goal_milestone_arc_step = self._goal_milestone_arc_step(
            goal_milestone_arc_signal=goal_milestone_arc_signal,
            steps=steps,
        )
        if goal_milestone_arc_step is not None and goal_milestone_arc_step not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, goal_milestone_arc_step)
        proposal_handoffs, accepted_proposals, proposal_steps = self._evaluate_subconscious_proposals(
            event=event,
            motivation=motivation,
            subconscious_proposals=subconscious_proposals or [],
        )
        for step in proposal_steps:
            if step in steps:
                continue
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, step)
        accepted_due_planned_work = self._accepted_due_planned_work_proposal(accepted_proposals)
        if accepted_due_planned_work is not None:
            goal = "Deliver the due planned-work follow-up with one clear immediate next step."
            steps = ["interpret_event", "review_context", "integrate_subconscious_nudge", "prepare_response"]
            delivery_channel = str(accepted_due_planned_work.payload.get("delivery_channel", "none")).strip().lower()
            needs_response = True
            needs_action = delivery_channel == "telegram" and isinstance(event.payload.get("chat_id"), (int, str))
            if needs_action:
                steps.append("send_telegram_message")

        domain_intents, inferred_promotion_diagnostics = self._build_domain_action_intents(
            event=event,
            event_text=event_text,
            context_summary=context.summary,
            motivation=motivation,
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
            active_planned_work=active_planned_work or [],
            relation_delivery=relation_delivery,
        )
        domain_intents.extend(self._build_connector_expansion_intents(accepted_proposals))
        connector_permission_gates = self._build_connector_permission_gates(domain_intents)

        return PlanOutput(
            goal=goal,
            steps=steps,
            needs_action=needs_action,
            needs_response=needs_response,
            domain_intents=domain_intents,
            inferred_promotion_diagnostics=inferred_promotion_diagnostics,
            proposal_handoffs=proposal_handoffs,
            accepted_proposals=accepted_proposals,
            connector_permission_gates=connector_permission_gates,
            selected_skills=list(role.selected_skills),
        )

    def _build_proactive_plan(
        self,
        *,
        event: Event,
        motivation: MotivationOutput,
        proactive_decision: ProactiveDecisionOutput,
        user_preferences: dict,
        relations: list[dict],
    ) -> PlanOutput:
        base_steps = ["evaluate_proactive_trigger", "assess_user_context"]
        attention_gate = event.payload.get("attention_gate") if isinstance(event.payload, dict) else {}
        relation_delivery = relation_value(relations=relations, relation_type="delivery_reliability")
        if isinstance(attention_gate, dict) and not bool(attention_gate.get("allowed", True)):
            return PlanOutput(
                goal="Defer proactive outreach until attention-gate conditions are satisfied.",
                steps=[*base_steps, "respect_attention_gate"],
                needs_action=False,
                needs_response=False,
                domain_intents=[
                    self._proactive_state_intent(
                        proactive_decision=proactive_decision,
                        state="attention_gate_blocked",
                        reason=str(attention_gate.get("reason", "attention_gate_blocked") or "attention_gate_blocked"),
                    )
                ],
                proactive_decision=proactive_decision,
            )
        if not proactive_decision.should_interrupt:
            return PlanOutput(
                goal="Defer proactive outreach until interruption cost becomes acceptable.",
                steps=[*base_steps, "defer_proactive_outreach"],
                needs_action=False,
                needs_response=False,
                domain_intents=[
                    self._proactive_state_intent(
                        proactive_decision=proactive_decision,
                        state="interruption_deferred",
                        reason=str(proactive_decision.reason or "interruption_cost_too_high"),
                    )
                ],
                proactive_decision=proactive_decision,
            )
        delivery_guard = self.proactive_delivery_guard.evaluate(
            event=event,
            user_preferences=user_preferences,
            relations=relations,
            proactive_decision=proactive_decision,
        )
        if delivery_guard is not None and not delivery_guard.allowed:
            return PlanOutput(
                goal="Defer proactive outreach until delivery guardrails pass.",
                steps=[*base_steps, "respect_proactive_delivery_guardrails"],
                needs_action=False,
                needs_response=False,
                domain_intents=[
                    self._proactive_state_intent(
                        proactive_decision=proactive_decision,
                        state="delivery_guard_blocked",
                        reason=str(delivery_guard.reason or "delivery_guard_blocked"),
                    )
                ],
                proactive_decision=proactive_decision,
                proactive_delivery_guard=delivery_guard,
            )

        output_step_map = {
            "suggestion": "compose_proactive_suggestion",
            "reminder": "compose_proactive_reminder",
            "question": "compose_proactive_question",
            "warning": "compose_proactive_warning",
            "encouragement": "compose_proactive_encouragement",
            "insight": "compose_proactive_insight",
        }
        goal_map = {
            "suggestion": "Deliver a proactive suggestion that helps the user move the current work forward.",
            "reminder": "Deliver a proactive reminder linked to active commitments.",
            "question": "Deliver a proactive clarification question before progress stalls.",
            "warning": "Deliver a proactive warning with one clear immediate next step.",
            "encouragement": "Deliver proactive encouragement tied to user momentum.",
            "insight": "Deliver a proactive insight grounded in recurring patterns.",
        }
        output_type = str(proactive_decision.output_type)
        steps = [*base_steps, output_step_map.get(output_type, "compose_proactive_suggestion")]
        if proactive_decision.mode == "strong":
            steps.append("mark_high_priority_proactive")
        if motivation.mode == "execute":
            steps.append("prioritize_immediate_attention")
        trust_tone_step = self._proactive_trust_tone_step(relation_delivery=relation_delivery or "")
        if trust_tone_step is not None and trust_tone_step not in steps:
            steps.append(trust_tone_step)
        steps.append("prepare_response")

        needs_response = True
        has_chat_id = isinstance(event.payload.get("chat_id"), (int, str))
        needs_action = needs_response and (
            event.source == "telegram"
            or (event.source == "scheduler" and has_chat_id)
        )
        if needs_action:
            steps.append("send_telegram_message")
        goal = self._apply_proactive_delivery_reliability_goal(
            goal=goal_map.get(output_type, goal_map["suggestion"]),
            relation_delivery=relation_delivery or "",
        )
        return PlanOutput(
            goal=goal,
            steps=steps,
            needs_action=needs_action,
            needs_response=needs_response,
            domain_intents=[
                self._proactive_state_intent(
                    proactive_decision=proactive_decision,
                    state="delivery_ready",
                    reason="delivery_ready",
                )
            ],
            proactive_decision=proactive_decision,
            proactive_delivery_guard=delivery_guard,
        )

    def _proactive_state_intent(
        self,
        *,
        proactive_decision: ProactiveDecisionOutput,
        state: str,
        reason: str,
    ) -> UpdateProactiveStateDomainIntent:
        return UpdateProactiveStateDomainIntent(
            state=state,
            trigger=str(proactive_decision.trigger or "time_checkin"),
            reason=reason,
            output_type=proactive_decision.output_type,
            mode=proactive_decision.mode,
        )

    def _build_domain_action_intents(
        self,
        *,
        event: Event,
        event_text: str,
        context_summary: str,
        motivation: MotivationOutput,
        active_goals: list[dict],
        active_tasks: list[dict],
        active_planned_work: list[dict],
        relation_delivery: str | None,
    ) -> tuple[list[DomainActionIntent], list[str]]:
        intents: list[DomainActionIntent] = []
        inferred_promotion_diagnostics: list[str] = []
        lowered_text = normalize_for_matching(event_text.strip())

        goal_signal = detect_goal_signal(event_text)
        if goal_signal is not None:
            intents.append(
                UpsertGoalDomainIntent(
                    name=goal_signal.name,
                    description=goal_signal.description,
                    priority=goal_signal.priority,
                    goal_type=goal_signal.goal_type,
                )
            )

        task_signal = detect_task_signal(event_text)
        if task_signal is not None:
            intents.append(
                UpsertTaskDomainIntent(
                    name=task_signal.name,
                    description=task_signal.description,
                    priority=task_signal.priority,
                    status=task_signal.status,
                )
            )
        intents.extend(
            self._planned_work_intents(
                event=event,
                event_text=event_text,
                active_planned_work=active_planned_work,
            )
        )

        task_status_signal = detect_task_status_signal(event_text)
        if task_status_signal is not None:
            intents.append(
                UpdateTaskStatusDomainIntent(
                    status=task_status_signal.status,
                    task_hint=task_status_signal.task_hint,
                )
            )

        style_preference = detect_response_style_preference(event_text)
        if style_preference is not None:
            intents.append(
                UpdateResponseStyleDomainIntent(
                    style=style_preference.style,
                    source=style_preference.source,
                )
            )

        collaboration_preference = detect_collaboration_preference(event_text)
        if collaboration_preference is not None:
            intents.append(
                UpdateCollaborationPreferenceDomainIntent(
                    preference=collaboration_preference.preference,
                    source=collaboration_preference.source,
                )
            )

        proactive_preference = detect_proactive_preference(event_text)
        if proactive_preference is not None:
            intents.append(
                UpdateProactivePreferenceDomainIntent(
                    opt_in=proactive_preference.opt_in,
                    source=proactive_preference.source,
                )
            )

        boundary_relation_keys: set[tuple[str, str]] = set()
        for signal in extract_communication_boundary_signals(event_text):
            key = (signal.relation_type, signal.relation_value)
            if key in boundary_relation_keys:
                continue
            boundary_relation_keys.add(key)
            intents.append(
                MaintainRelationDomainIntent(
                    relation_type=signal.relation_type,
                    relation_value=signal.relation_value,
                    confidence=signal.confidence,
                    source=signal.source,
                    evidence_count=1,
                    decay_rate=0.02,
                )
            )

        calendar_intent = self._calendar_scheduling_intent(lowered_text)
        if calendar_intent is not None:
            intents.append(calendar_intent)

        external_task_intent = self._external_task_sync_intent(lowered_text)
        if external_task_intent is not None:
            intents.append(external_task_intent)

        connected_drive_intent = self._connected_drive_access_intent(lowered_text)
        if connected_drive_intent is not None:
            intents.append(connected_drive_intent)

        knowledge_search_intent = self._knowledge_search_intent(event_text=event_text, normalized_text=lowered_text)
        if knowledge_search_intent is not None:
            intents.append(knowledge_search_intent)

        web_browser_intent = self._web_browser_access_intent(event_text=event_text, normalized_text=lowered_text)
        if web_browser_intent is not None:
            intents.append(web_browser_intent)

        inferred_intents, inferred_promotion_diagnostics = self._build_inferred_goal_task_intents(
            event_text=event_text,
            context_summary=context_summary,
            motivation=motivation,
            active_goals=active_goals,
            active_tasks=active_tasks,
            existing_intents=intents,
            relation_delivery=relation_delivery,
        )
        intents.extend(inferred_intents)

        if not intents:
            return [NoopDomainIntent()], inferred_promotion_diagnostics
        return intents, inferred_promotion_diagnostics

    def _planned_work_intents(
        self,
        *,
        event: Event,
        event_text: str,
        active_planned_work: list[dict],
    ) -> list[DomainActionIntent]:
        normalized = normalize_for_matching(event_text)
        if not normalized:
            return []

        intents: list[DomainActionIntent] = []
        matched_work = self._match_planned_work_candidate(event_text=event_text, active_planned_work=active_planned_work)
        preferred_at = self._planned_work_preferred_at(event=event, normalized_text=normalized)

        if matched_work is not None and self._looks_like_cancel_planned_work(normalized):
            intents.append(
                CancelPlannedWorkItemDomainIntent(
                    work_id=int(matched_work["id"]),
                    reason="explicit_user_cancellation",
                )
            )
            return intents

        if matched_work is not None and self._looks_like_complete_planned_work(normalized):
            intents.append(
                CompletePlannedWorkItemDomainIntent(
                    work_id=int(matched_work["id"]),
                    reason="explicit_user_completion",
                )
            )
            return intents

        if matched_work is not None and self._looks_like_reschedule_planned_work(normalized) and preferred_at is not None:
            intents.append(
                ReschedulePlannedWorkItemDomainIntent(
                    work_id=int(matched_work["id"]),
                    not_before=preferred_at,
                    preferred_at=preferred_at,
                    reason="explicit_user_reschedule",
                )
            )
            return intents

        if self._looks_like_planned_work_request(normalized):
            planned_kind = self._planned_work_kind(normalized)
            summary = self._planned_work_summary(event_text=event_text)
            if summary:
                intents.append(
                    UpsertPlannedWorkItemDomainIntent(
                        work_kind=planned_kind,
                        summary=summary,
                        not_before=preferred_at,
                        preferred_at=preferred_at,
                        recurrence_mode=self._planned_work_recurrence_mode(normalized),
                        recurrence_rule=self._planned_work_recurrence_rule(normalized),
                        channel_hint=self._planned_work_channel_hint(event),
                        provenance="explicit_user_request",
                    )
                )
        return intents

    def _looks_like_planned_work_request(self, normalized_text: str) -> bool:
        if re.search(r"\bremind me every\s+\d+\s+days?\b", normalized_text) or re.search(
            r"\bprzypominaj mi co\s+\d+\s+dni\b",
            normalized_text,
        ):
            return True
        return any(
            phrase in normalized_text
            for phrase in (
                "remind me to ",
                "remind me about ",
                "remind me every day",
                "remind me every week",
                "please remind me to ",
                "please remind me about ",
                "przypomnij mi zeby ",
                "przypomnij mi aby ",
                "przypomnij mi o ",
                "przypominaj mi codziennie",
                "przypominaj mi co tydzien",
                "przypominaj mi co tydzień",
                "help me plan today",
                "help me plan tomorrow",
                "plan tomorrow",
                "plan my day",
                "weekly planning",
                "help me plan this week",
                "zaplanuj moj dzien",
                "pomoz mi zaplanowac dzis",
                "pomoz mi zaplanowac jutro",
                "zaplanuj jutro",
                "plan tygodnia",
                "pomoz mi zaplanowac ten tydzien",
            )
        )

    def _looks_like_cancel_planned_work(self, normalized_text: str) -> bool:
        return any(
            phrase in normalized_text
            for phrase in (
                "cancel the reminder",
                "cancel reminder",
                "stop reminding me about ",
                "dont remind me about ",
                "don't remind me about ",
                "anuluj przypomnienie",
                "nie przypominaj mi o ",
                "usun przypomnienie",
            )
        )

    def _looks_like_complete_planned_work(self, normalized_text: str) -> bool:
        return any(
            phrase in normalized_text
            for phrase in (
                "i already did ",
                "i already sent ",
                "done with ",
                "completed ",
                "juz zrobilem ",
                "juz zrobilam ",
                "juz wyslalem ",
                "juz wyslalam ",
                "to juz zrobione",
            )
        )

    def _looks_like_reschedule_planned_work(self, normalized_text: str) -> bool:
        return any(
            phrase in normalized_text
            for phrase in (
                "reschedule",
                "move the reminder",
                "move reminder",
                "instead tomorrow",
                "instead next week",
                "reschedule reminder",
                "przeloz przypomnienie",
                "przesun przypomnienie",
            )
        )

    def _planned_work_kind(self, normalized_text: str) -> str:
        if any(
            token in normalized_text
            for token in (
                "every day",
                "daily",
                "every week",
                "weekly",
                "codziennie",
                "co tydzien",
                "co tydzień",
            )
        ):
            return "routine"
        if any(token in normalized_text for token in ("plan today", "plan tomorrow", "weekly planning", "zaplanuj", "plan my day")):
            return "check_in"
        return "reminder"

    def _planned_work_summary(self, event_text: str) -> str:
        task_signal = detect_task_signal(event_text)
        if task_signal is not None:
            return task_signal.name
        return " ".join(str(event_text).split())[:160]

    def _planned_work_preferred_at(self, *, event: Event, normalized_text: str):
        base = event.timestamp
        if "tomorrow" in normalized_text or "jutro" in normalized_text:
            return base + timedelta(days=1)
        if "next week" in normalized_text:
            return base + timedelta(days=7)
        if "today" in normalized_text or "dzis" in normalized_text:
            return base
        if "this week" in normalized_text or "ten tydzien" in normalized_text:
            return base + timedelta(days=3)
        return None

    def _planned_work_recurrence_mode(self, normalized_text: str) -> str:
        if re.search(r"\bevery\s+\d+\s+days?\b", normalized_text) or re.search(r"\bco\s+\d+\s+dni\b", normalized_text):
            return "custom"
        if any(
            token in normalized_text
            for token in ("every day", "daily", "codziennie", "kazdego dnia", "każdego dnia")
        ):
            return "daily"
        if any(
            token in normalized_text
            for token in ("every week", "weekly", "co tydzien", "co tydzień")
        ):
            return "weekly"
        return "none"

    def _planned_work_recurrence_rule(self, normalized_text: str) -> str:
        english_match = re.search(r"\bevery\s+(\d+)\s+days?\b", normalized_text)
        if english_match is not None:
            return f"interval_days:{int(english_match.group(1))}"
        polish_match = re.search(r"\bco\s+(\d+)\s+dni\b", normalized_text)
        if polish_match is not None:
            return f"interval_days:{int(polish_match.group(1))}"
        return ""

    def _planned_work_channel_hint(self, event: Event) -> str:
        if event.source == "telegram":
            return "telegram"
        if event.source == "api":
            return "api"
        return "none"

    def _match_planned_work_candidate(self, *, event_text: str, active_planned_work: list[dict]) -> dict | None:
        hint_tokens = self._text_tokens(event_text)
        best_item: dict | None = None
        best_score = 0
        for item in active_planned_work:
            item_id = item.get("id")
            if item_id is None:
                continue
            item_tokens = self._text_tokens(str(item.get("summary", "")))
            overlap = len(hint_tokens.intersection(item_tokens))
            if overlap > best_score:
                best_score = overlap
                best_item = item
        return best_item if best_score > 0 else None

    def _build_inferred_goal_task_intents(
        self,
        *,
        event_text: str,
        context_summary: str,
        motivation: MotivationOutput,
        active_goals: list[dict],
        active_tasks: list[dict],
        existing_intents: list[DomainActionIntent],
        relation_delivery: str | None,
    ) -> tuple[list[DomainActionIntent], list[str]]:
        gate_reason = self._inferred_promotion_gate_reason(
            event_text=event_text,
            context_summary=context_summary,
            motivation=motivation,
            relation_delivery=relation_delivery,
        )
        diagnostics = [f"reason={gate_reason}"]
        if gate_reason != "gate_open":
            return [], diagnostics

        has_goal_intent = any(isinstance(intent, UpsertGoalDomainIntent) for intent in existing_intents)
        has_task_intent = any(isinstance(intent, UpsertTaskDomainIntent) for intent in existing_intents)
        has_task_status_intent = any(
            isinstance(intent, (UpdateTaskStatusDomainIntent, MaintainTaskStatusDomainIntent))
            for intent in existing_intents
        )
        inferred_intents: list[DomainActionIntent] = []
        normalized = normalize_for_matching(event_text)
        inferred_task_name = self._infer_task_name_from_repeated_evidence(event_text)
        inferred_task_status = self._inferred_task_status(normalized)
        matching_task = (
            self._find_matching_task_candidate(inferred_task_name, active_tasks)
            if inferred_task_name is not None
            else None
        )

        if (
            not has_task_intent
            and inferred_task_name is not None
            and matching_task is None
        ):
            inferred_intents.append(
                PromoteInferredTaskDomainIntent(
                    name=inferred_task_name,
                    description=f"Inferred task from repeated execution evidence: {inferred_task_name[:220]}",
                    priority=self._inferred_priority(normalized, motivation),
                    status=inferred_task_status,
                )
            )
        elif (
            not has_task_status_intent
            and inferred_task_name is not None
            and matching_task is not None
            and inferred_task_status == "blocked"
            and str(matching_task.get("status", "")).strip().lower() not in {"blocked", "done", "cancelled"}
        ):
            inferred_intents.append(
                MaintainTaskStatusDomainIntent(
                    status="blocked",
                    task_hint=inferred_task_name,
                    reason="inferred_repeated_blocker_evidence",
                )
            )

        if has_goal_intent:
            diagnostics.append("result=goal_intent_already_present")
            return inferred_intents, diagnostics

        inferred_goal_name = self._infer_goal_name_from_repeated_evidence(
            event_text=event_text,
            inferred_task_name=inferred_task_name,
        )
        if inferred_goal_name is None:
            diagnostics.append("result=no_goal_candidate")
            return inferred_intents, diagnostics
        if self._is_duplicate_goal_candidate(inferred_goal_name, active_goals):
            diagnostics.append("result=duplicate_goal_candidate")
            return inferred_intents, diagnostics

        if active_goals:
            diagnostics.append("result=active_goal_already_present")
            return inferred_intents, diagnostics

        inferred_intents.append(
            PromoteInferredGoalDomainIntent(
                name=inferred_goal_name,
                description=f"Inferred goal from repeated execution evidence: {inferred_goal_name[:220]}",
                priority=self._inferred_priority(normalized, motivation),
                goal_type=self._inferred_goal_type(normalized),
            )
        )
        if any(isinstance(intent, PromoteInferredTaskDomainIntent) for intent in inferred_intents):
            diagnostics.append("result=promote_inferred_task")
        if any(isinstance(intent, MaintainTaskStatusDomainIntent) for intent in inferred_intents):
            diagnostics.append("result=maintain_task_status")
        if any(isinstance(intent, PromoteInferredGoalDomainIntent) for intent in inferred_intents):
            diagnostics.append("result=promote_inferred_goal")
        return inferred_intents, diagnostics

    def _can_infer_goal_task_promotion(
        self,
        *,
        event_text: str,
        context_summary: str,
        motivation: MotivationOutput,
        relation_delivery: str | None,
    ) -> bool:
        return (
            self._inferred_promotion_gate_reason(
                event_text=event_text,
                context_summary=context_summary,
                motivation=motivation,
                relation_delivery=relation_delivery,
            )
            == "gate_open"
        )

    def _inferred_promotion_gate_reason(
        self,
        *,
        event_text: str,
        context_summary: str,
        motivation: MotivationOutput,
        relation_delivery: str | None,
    ) -> str:
        if motivation.mode not in {"respond", "analyze", "execute"}:
            return "mode_not_supported"
        if motivation.importance < self._inferred_promotion_importance_min(relation_delivery or ""):
            return "trust_gate_low_confidence"

        normalized_event = normalize_for_matching(event_text)
        normalized_context = normalize_for_matching(context_summary)
        if not normalized_event:
            return "empty_event_text"

        issue_markers = (
            "blocked",
            "blocker",
            "stuck",
            "failing",
            "failed",
            "error",
            "issue",
            "problem",
            "cannot",
            "cant",
            "nie moge",
            "nie mog",
            "blokuje",
            "awaria",
            "blad",
            "problem",
        )
        repeated_markers = (
            "again",
            "still",
            "repeated",
            "keeps",
            "keep failing",
            "nadal",
            "znow",
            "wciaz",
            "ponownie",
            "kolejny raz",
            "powraca",
            "repro",
        )

        has_issue = any(marker in normalized_event for marker in issue_markers)
        if not has_issue:
            return "missing_issue_marker"
        has_repeated = any(marker in normalized_event for marker in repeated_markers)
        if (
            not has_repeated
            and (
                relation_delivery == "low_trust"
                or "relevant recent memory" not in normalized_context
            )
        ):
            return "missing_repeated_signal"
        return "gate_open"

    def _inferred_promotion_importance_min(self, relation_delivery: str) -> float:
        if relation_delivery == "low_trust":
            return 0.74
        if relation_delivery == "high_trust":
            return 0.58
        return 0.62

    def _infer_task_name_from_repeated_evidence(self, event_text: str) -> str | None:
        normalized = normalize_for_matching(event_text)
        if not normalized:
            return None

        raw = str(event_text).strip()
        extraction_markers = (
            "blocked by ",
            "blocked on ",
            "stuck on ",
            "stuck with ",
            "failing on ",
            "fails on ",
            "nie moge przez ",
            "blokuje mnie ",
        )
        lowered_raw = raw.lower()
        extracted = ""
        for marker in extraction_markers:
            marker_index = lowered_raw.find(marker)
            if marker_index == -1:
                continue
            extracted = raw[marker_index + len(marker):].strip()
            break

        token_source = normalize_for_matching(extracted) if extracted else normalized
        removable_tokens = {
            "again",
            "still",
            "blocked",
            "blocker",
            "stuck",
            "failing",
            "failed",
            "issue",
            "problem",
            "error",
            "errors",
            "nadal",
            "znow",
            "wciaz",
            "ponownie",
            "kolejny",
            "powraca",
            "please",
            "prosze",
            "help",
            "pomoz",
        }
        tokens = [
            token
            for token in token_source.split()
            if len(token) >= 3 and token not in removable_tokens
        ]
        if len(tokens) < 2:
            return None
        candidate = " ".join(tokens[:8]).strip(" .,:;!-")
        if len(candidate) < 8:
            return None
        return candidate[:160]

    def _infer_goal_name_from_repeated_evidence(self, *, event_text: str, inferred_task_name: str | None) -> str | None:
        normalized = normalize_for_matching(event_text)
        if not normalized:
            return None
        if inferred_task_name:
            return f"stabilize {inferred_task_name[:120]}"

        focus_tokens = [
            token
            for token in normalized.split()
            if len(token) >= 4
            and token
            not in {
                "again",
                "still",
                "blocked",
                "blocker",
                "stuck",
                "failing",
                "error",
                "problem",
                "issue",
                "nadal",
                "znow",
                "wciaz",
                "ponownie",
            }
        ]
        if len(focus_tokens) < 2:
            return None
        return f"stabilize {' '.join(focus_tokens[:5])}"[:160]

    def _is_duplicate_goal_candidate(self, candidate_name: str, active_goals: list[dict]) -> bool:
        candidate_tokens = self._text_tokens(candidate_name)
        if not candidate_tokens:
            return True
        for goal in active_goals:
            goal_name = str(goal.get("name", "")).strip()
            goal_description = str(goal.get("description", "")).strip()
            existing_tokens = self._text_tokens(f"{goal_name} {goal_description}")
            if not existing_tokens:
                continue
            if self._token_overlap_ratio(candidate_tokens, existing_tokens) >= 0.6:
                return True
        return False

    def _is_duplicate_task_candidate(self, candidate_name: str, active_tasks: list[dict]) -> bool:
        return self._find_matching_task_candidate(candidate_name, active_tasks) is not None

    def _find_matching_task_candidate(self, candidate_name: str, active_tasks: list[dict]) -> dict | None:
        candidate_tokens = self._text_tokens(candidate_name)
        if not candidate_tokens:
            return None
        for task in active_tasks:
            task_name = str(task.get("name", "")).strip()
            task_description = str(task.get("description", "")).strip()
            existing_tokens = self._text_tokens(f"{task_name} {task_description}")
            if not existing_tokens:
                continue
            if self._token_overlap_ratio(candidate_tokens, existing_tokens) >= 0.6:
                return task
        return None

    def _token_overlap_ratio(self, left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        overlap = len(left.intersection(right))
        baseline = max(1, min(len(left), len(right)))
        return float(overlap) / float(baseline)

    def _inferred_priority(self, normalized_text: str, motivation: MotivationOutput) -> str:
        if any(
            marker in normalized_text
            for marker in ("urgent", "critical", "production", "pilne", "prod", "awaria")
        ):
            return "high"
        if motivation.urgency >= 0.7 or motivation.importance >= 0.78:
            return "high"
        return "medium"

    def _inferred_task_status(self, normalized_text: str) -> str:
        if any(marker in normalized_text for marker in ("blocked", "blocker", "stuck", "failing", "blokuje", "awaria")):
            return "blocked"
        return "todo"

    def _inferred_goal_type(self, normalized_text: str) -> str:
        if any(marker in normalized_text for marker in ("today", "tomorrow", "this week", "dzis", "jutro", "w tym tygodniu")):
            return "operational"
        return "tactical"

    def _calendar_scheduling_intent(self, lowered_text: str) -> CalendarSchedulingIntentDomainIntent | None:
        if not any(keyword in lowered_text for keyword in ("calendar", "kalendarz", "meeting", "spotkanie", "schedule")):
            return None
        if any(keyword in lowered_text for keyword in ("create", "utw", "zaplanuj", "book", "reserve")):
            return CalendarSchedulingIntentDomainIntent(
                operation="create_event",
                mode=resolve_connector_operation_policy("calendar", "create_event").mode,
                title_hint=lowered_text[:120],
                time_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("availability", "free", "woln", "when can", "kiedy")):
            return CalendarSchedulingIntentDomainIntent(
                operation="read_availability",
                provider_hint="google_calendar",
                mode=resolve_connector_operation_policy("calendar", "read_availability").mode,
                title_hint=lowered_text[:120],
                time_hint=lowered_text[:120],
            )
        return CalendarSchedulingIntentDomainIntent(
            operation="suggest_slots",
            mode=resolve_connector_operation_policy("calendar", "suggest_slots").mode,
            title_hint=lowered_text[:120],
            time_hint=lowered_text[:120],
        )

    def _external_task_sync_intent(self, lowered_text: str) -> ExternalTaskSyncDomainIntent | None:
        provider = None
        for candidate in ("clickup", "trello", "asana", "jira"):
            if candidate in lowered_text:
                provider = candidate
                break
        if provider is None:
            return None

        if any(keyword in lowered_text for keyword in ("create", "utw", "add card", "create card", "create task")):
            return ExternalTaskSyncDomainIntent(
                operation="create_task",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("task_system", "create_task").mode,
                task_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("update", "mark", "done", "complete", "zamknij", "oznacz")):
            status_hint = "done" if any(keyword in lowered_text for keyword in ("done", "complete", "zamknij", "oznacz")) else "in_progress"
            return ExternalTaskSyncDomainIntent(
                operation="update_task",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("task_system", "update_task").mode,
                task_hint=lowered_text[:120],
                status_hint=status_hint,
            )
        if any(keyword in lowered_text for keyword in ("sync", "synchron", "export", "mirror", "link")):
            return ExternalTaskSyncDomainIntent(
                operation="suggest_sync",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("task_system", "suggest_sync").mode,
                task_hint=lowered_text[:120],
            )
        return ExternalTaskSyncDomainIntent(
            operation="list_tasks",
            provider_hint=provider,
            mode=resolve_connector_operation_policy("task_system", "list_tasks").mode,
            task_hint=lowered_text[:120],
        )

    def _connected_drive_access_intent(self, lowered_text: str) -> ConnectedDriveAccessDomainIntent | None:
        provider = "generic"
        for candidate, label in (
            ("google drive", "google_drive"),
            ("gdrive", "google_drive"),
            ("onedrive", "onedrive"),
            ("dropbox", "dropbox"),
            ("box", "box"),
        ):
            if candidate in lowered_text:
                provider = label
                break

        drive_keywords = (
            "drive",
            "document",
            "doc",
            "file",
            "folder",
            "plik",
            "dokument",
            "katalog",
        )
        if provider == "generic" and not any(keyword in lowered_text for keyword in drive_keywords):
            return None

        if any(keyword in lowered_text for keyword in ("delete", "remove", "usun", "skasuj")):
            return ConnectedDriveAccessDomainIntent(
                operation="delete_file",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("cloud_drive", "delete_file").mode,
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("upload", "add file", "wrzu", "zaladuj")):
            return ConnectedDriveAccessDomainIntent(
                operation="upload_file",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("cloud_drive", "upload_file").mode,
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("update", "edit", "modify", "zmien", "edyt")):
            return ConnectedDriveAccessDomainIntent(
                operation="update_document",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("cloud_drive", "update_document").mode,
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("search", "find", "szuk", "znajd")):
            return ConnectedDriveAccessDomainIntent(
                operation="search_documents",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("cloud_drive", "search_documents").mode,
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("read", "open", "preview", "otw", "pokaz")):
            return ConnectedDriveAccessDomainIntent(
                operation="read_document",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("cloud_drive", "read_document").mode,
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("organize", "plan", "suggest", "uporzadkuj", "zaproponuj")):
            return ConnectedDriveAccessDomainIntent(
                operation="suggest_file_plan",
                provider_hint=provider,
                mode=resolve_connector_operation_policy("cloud_drive", "suggest_file_plan").mode,
                file_hint=lowered_text[:120],
            )
        selected_provider = "google_drive" if provider == "generic" else provider
        return ConnectedDriveAccessDomainIntent(
            operation="list_files",
            provider_hint=selected_provider,
            mode=resolve_connector_operation_policy("cloud_drive", "list_files").mode,
            file_hint=lowered_text[:120],
        )

    def _knowledge_search_intent(self, *, event_text: str, normalized_text: str) -> KnowledgeSearchDomainIntent | None:
        search_markers = (
            "search the web",
            "search online",
            "look up",
            "find online",
            "google it",
            "google for",
            "internet search",
            "wyszukaj",
            "poszukaj",
            "szukaj w internecie",
            "sprawdz w internecie",
        )
        weather_markers = (
            "weather",
            "forecast",
            "pogoda",
            "prognoza pogody",
        )
        current_fact_markers = (
            "latest",
            "news",
            "najnowsze",
            "aktualne",
            "dzisiaj",
            "today",
        )
        should_search = any(marker in normalized_text for marker in search_markers)
        if not should_search:
            if any(marker in normalized_text for marker in weather_markers):
                should_search = True
            elif any(marker in normalized_text for marker in current_fact_markers) and "http" not in normalized_text:
                should_search = True
        if not should_search:
            return None
        if any(keyword in normalized_text for keyword in ("should i search", "czy warto szukac", "suggest search")):
            return KnowledgeSearchDomainIntent(
                operation="suggest_search",
                provider_hint="duckduckgo_html",
                mode=resolve_connector_operation_policy("knowledge_search", "suggest_search").mode,
                query_hint=event_text[:160],
            )
        return KnowledgeSearchDomainIntent(
            operation="search_web",
            provider_hint="duckduckgo_html",
            mode=resolve_connector_operation_policy("knowledge_search", "search_web").mode,
            query_hint=event_text[:160],
        )

    def _web_browser_access_intent(self, *, event_text: str, normalized_text: str) -> WebBrowserAccessDomainIntent | None:
        browser_markers = (
            "open page",
            "read page",
            "browse",
            "browser",
            "website",
            "web page",
            "url",
            "otworz strone",
            "przeczytaj strone",
            "odwiedz strone",
            "przegladaj strone",
        )
        explicit_target = self._extract_bounded_website_target(event_text)
        if not any(marker in normalized_text for marker in browser_markers) and explicit_target is None:
            return None
        if any(keyword in normalized_text for keyword in ("should we browse", "suggest page", "review page later")):
            return WebBrowserAccessDomainIntent(
                operation="suggest_page_review",
                provider_hint="generic_http",
                mode=resolve_connector_operation_policy("web_browser", "suggest_page_review").mode,
                page_hint=explicit_target or event_text[:160],
            )
        return WebBrowserAccessDomainIntent(
            operation="read_page",
            provider_hint="generic_http",
            mode=resolve_connector_operation_policy("web_browser", "read_page").mode,
            page_hint=explicit_target or event_text[:160],
        )

    def _extract_bounded_website_target(self, text: str) -> str | None:
        raw = str(text or "").strip()
        if not raw:
            return None
        url_match = re.search(r"(https?://[^\s]+)", raw, re.IGNORECASE)
        if url_match is not None:
            return url_match.group(1).strip("()[]<>,.;'\"")[:500]
        domain_match = re.search(r"\b((?:[a-z0-9-]+\.)+[a-z]{2,})(?:/[^\s]*)?\b", raw, re.IGNORECASE)
        if domain_match is None:
            return None
        domain = domain_match.group(1).strip("()[]<>,.;'\"")
        if "." not in domain:
            return None
        return f"https://{domain}"[:500]

    def _build_connector_permission_gates(
        self,
        domain_intents: list[DomainActionIntent],
    ) -> list[ConnectorPermissionGateOutput]:
        gates: list[ConnectorPermissionGateOutput] = []
        for intent in domain_intents:
            if isinstance(intent, CalendarSchedulingIntentDomainIntent):
                gates.append(build_connector_permission_gate(intent))
            if isinstance(intent, ExternalTaskSyncDomainIntent):
                gates.append(build_connector_permission_gate(intent))
            if isinstance(intent, ConnectedDriveAccessDomainIntent):
                gates.append(build_connector_permission_gate(intent))
            if isinstance(intent, ConnectorCapabilityDiscoveryDomainIntent):
                gates.append(build_connector_permission_gate(intent))
            if isinstance(intent, KnowledgeSearchDomainIntent):
                gates.append(build_connector_permission_gate(intent))
            if isinstance(intent, WebBrowserAccessDomainIntent):
                gates.append(build_connector_permission_gate(intent))
        return gates

    def _build_connector_expansion_intents(
        self,
        accepted_proposals: list[SubconsciousProposalRecord],
    ) -> list[ConnectorCapabilityDiscoveryDomainIntent]:
        intents: list[ConnectorCapabilityDiscoveryDomainIntent] = []
        seen: set[tuple[str, str, str]] = set()
        for proposal in accepted_proposals:
            if proposal.proposal_type != "suggest_connector_expansion":
                continue
            payload = proposal.payload if isinstance(proposal.payload, dict) else {}
            connector_kind = str(payload.get("connector_kind", "task_system")).strip().lower()
            if connector_kind not in {"calendar", "task_system", "cloud_drive"}:
                connector_kind = "task_system"
            provider_hint = str(payload.get("provider_hint", "generic")).strip().lower() or "generic"
            requested_capability = (
                str(payload.get("requested_capability", "connector_access")).strip().lower() or "connector_access"
            )
            key = (connector_kind, provider_hint, requested_capability)
            if key in seen:
                continue
            seen.add(key)
            intents.append(
                ConnectorCapabilityDiscoveryDomainIntent(
                    connector_kind=connector_kind,  # type: ignore[arg-type]
                    provider_hint=provider_hint,
                    requested_capability=requested_capability,
                    evidence="subconscious_repeated_unmet_need",
                    mode=resolve_connector_capability_discovery_policy(
                        connector_kind,  # type: ignore[arg-type]
                        requested_capability,
                    ).mode,
                )
            )
        return intents

    def _evaluate_subconscious_proposals(
        self,
        *,
        event: Event,
        motivation: MotivationOutput,
        subconscious_proposals: list[dict],
    ) -> tuple[list[ProposalHandoffDecisionOutput], list[SubconsciousProposalRecord], list[str]]:
        if not subconscious_proposals:
            return [], [], []

        handoffs: list[ProposalHandoffDecisionOutput] = []
        accepted: list[SubconsciousProposalRecord] = []
        extra_steps: list[str] = []
        normalized_text = str(event.payload.get("text", "")).strip().lower()
        retriable_statuses = {"pending", "deferred"}

        for raw in subconscious_proposals[:4]:
            proposal_id_raw = raw.get("proposal_id")
            try:
                proposal_id = int(proposal_id_raw)
            except (TypeError, ValueError):
                continue
            proposal_status = str(raw.get("status", "pending")).strip().lower()
            if proposal_status not in retriable_statuses:
                continue
            proposal = SubconsciousProposalRecord(
                proposal_id=proposal_id,
                proposal_type=str(raw.get("proposal_type", "nudge_user")),
                summary=str(raw.get("summary", "")),
                payload=raw.get("payload") if isinstance(raw.get("payload"), dict) else {},
                confidence=float(raw.get("confidence", 0.0) or 0.0),
                status=proposal_status,
                source_event_id=str(raw.get("source_event_id", "") or "") or None,
                research_policy=str(raw.get("research_policy", "read_only")),
                allowed_tools=[
                    str(item)
                    for item in raw.get("allowed_tools", [])
                    if isinstance(item, str)
                ],
            )

            decision = "defer"
            reason = "requires_conscious_confirmation"
            payload = proposal.payload if isinstance(proposal.payload, dict) else {}
            planned_work_due_handoff = str(payload.get("handoff_kind", "")).strip().lower() == "planned_work_due"
            if event.source in {"api", "telegram"} and motivation.mode != "ignore":
                if proposal.proposal_type in {"ask_user", "nudge_user"} and not accepted:
                    decision = "accept"
                    reason = "conscious_turn_selected_single_proposal"
                    accepted.append(proposal)
                    if proposal.proposal_type == "ask_user":
                        extra_steps.append("ask_subconscious_clarifier")
                    else:
                        extra_steps.append("integrate_subconscious_nudge")
                elif proposal.proposal_type == "research_topic" and (
                    "research" in normalized_text or "sprawd" in normalized_text
                ):
                    decision = "accept"
                    reason = "read_only_research_confirmed_by_user_turn"
                    accepted.append(proposal)
                    extra_steps.append("queue_read_only_research")
                elif proposal.proposal_type in {"ask_user", "nudge_user"} and accepted:
                    decision = "merge"
                    reason = "merged_into_primary_conscious_proposal"
                elif proposal.proposal_type == "suggest_connector_expansion":
                    expansion_cues = (
                        "integrat",
                        "connect",
                        "connector",
                        "sync",
                        "plugin",
                        "extension",
                        "capability",
                    )
                    if any(cue in normalized_text for cue in expansion_cues) or not accepted:
                        decision = "accept"
                        reason = "connector_capability_gap_detected"
                        accepted.append(proposal)
                        extra_steps.append("propose_connector_capability_expansion")
            elif event.source == "scheduler" and planned_work_due_handoff and not accepted:
                decision = "accept"
                reason = "scheduled_due_planned_work_handoff"
                accepted.append(proposal)
                extra_steps.append("integrate_subconscious_nudge")

            handoffs.append(
                ProposalHandoffDecisionOutput(
                    proposal_id=proposal_id,
                    decision=decision,  # type: ignore[arg-type]
                    reason=reason,
                )
            )
        return handoffs, accepted, extra_steps

    def _accepted_due_planned_work_proposal(
        self,
        accepted_proposals: list[SubconsciousProposalRecord],
    ) -> SubconsciousProposalRecord | None:
        for proposal in accepted_proposals:
            payload = proposal.payload if isinstance(proposal.payload, dict) else {}
            if str(payload.get("handoff_kind", "")).strip().lower() == "planned_work_due":
                return proposal
        return None

    def _theta_plan_step(self, theta: dict | None, steps: list[str]) -> str | None:
        channel = dominant_theta_channel(theta)
        if channel is None:
            return None
        step_by_channel = {
            "support": "maintain_supportive_stance",
            "analysis": "favor_structured_reasoning",
            "execution": "favor_concrete_next_step",
        }
        step = step_by_channel.get(channel)
        if step is None:
            return None

        if step == "maintain_supportive_stance" and (
            "acknowledge_emotion" in steps or "reduce_pressure" in steps
        ):
            return None
        if step == "favor_structured_reasoning" and "break_down_problem" in steps:
            return None
        if step == "favor_concrete_next_step" and "propose_execution_step" in steps:
            return None
        return step

    def _collaboration_plan_step(self, collaboration_preference: str, steps: list[str]) -> str | None:
        if collaboration_preference == "hands_on":
            if "propose_execution_step" in steps or "favor_concrete_next_step" in steps:
                return None
            return "favor_concrete_next_step"
        if collaboration_preference == "guided":
            if (
                "offer_guidance" in steps
                or "break_down_problem" in steps
                or "favor_guided_walkthrough" in steps
            ):
                return None
            return "favor_guided_walkthrough"
        return None

    def _apply_collaboration_preference_goal(
        self,
        goal: str,
        collaboration_preference: str,
        motivation: MotivationOutput,
        role: RoleOutput,
    ) -> str:
        if collaboration_preference == "hands_on":
            if motivation.mode == "execute" or role.selected == "executor":
                return "Move the requested task toward execution with the smallest concrete next step."
            return "Provide a clear response that ends with a concrete next step."
        if collaboration_preference == "guided":
            if motivation.mode == "analyze" or role.selected in {"analyst", "mentor"}:
                return "Explain the situation clearly with a guided step by step path."
            return "Guide the user through the next step in a calm, step by step way."
        return goal

    def _delivery_reliability_confidence_step(self, relation_delivery: str, steps: list[str]) -> str | None:
        if relation_delivery == "high_trust":
            if "plan_with_confident_next_step" in steps:
                return None
            return "plan_with_confident_next_step"
        if relation_delivery == "low_trust":
            if "plan_with_cautious_validation" in steps:
                return None
            return "plan_with_cautious_validation"
        return None

    def _apply_delivery_reliability_goal(
        self,
        *,
        goal: str,
        relation_delivery: str,
        motivation: MotivationOutput,
        role: RoleOutput,
    ) -> str:
        if relation_delivery == "high_trust":
            if motivation.mode == "execute" or role.selected == "executor":
                return "Move the requested task toward execution with confidence and the smallest concrete next step."
            return f"{goal} Keep planning confidence high and finish with one concrete next step."
        if relation_delivery == "low_trust":
            return f"{goal} Keep confidence calibrated: make assumptions explicit and include one quick verification check."
        return goal

    def _proactive_trust_tone_step(self, *, relation_delivery: str) -> str | None:
        if relation_delivery == "high_trust":
            return "use_confident_outreach_tone"
        if relation_delivery == "low_trust":
            return "use_low_pressure_outreach_tone"
        return None

    def _apply_proactive_delivery_reliability_goal(self, *, goal: str, relation_delivery: str) -> str:
        if relation_delivery == "high_trust":
            return f"{goal} Keep the outreach confident and action-oriented."
        if relation_delivery == "low_trust":
            return f"{goal} Keep the outreach low-pressure and verification-oriented."
        return goal

    def _select_relevant_goal(self, event: Event, active_goals: list[dict]) -> dict | None:
        return shared_select_relevant_goal(
            event_text=str(event.payload.get("text", "")),
            active_goals=active_goals,
            tokenize=self._text_tokens,
        )

    def _select_relevant_task(self, event: Event, active_tasks: list[dict], relevant_goal_id: int | None) -> dict | None:
        return shared_select_relevant_task(
            event_text=str(event.payload.get("text", "")),
            active_tasks=active_tasks,
            tokenize=self._text_tokens,
            relevant_goal_id=relevant_goal_id,
        )

    def _task_plan_step(self, task: dict | None) -> str | None:
        if not task:
            return None
        if str(task.get("status", "")).strip().lower() == "blocked":
            return "unblock_active_task"
        return "advance_active_task"

    def _select_relevant_milestone(self, active_goal_milestones: list[dict], relevant_goal_id: int | None) -> dict | None:
        if not active_goal_milestones:
            return None
        if relevant_goal_id is not None:
            linked = [item for item in active_goal_milestones if item.get("goal_id") == relevant_goal_id]
            if linked:
                return linked[0]
        return active_goal_milestones[0]

    def _goal_execution_step(self, goal_execution_state: str, steps: list[str]) -> str | None:
        if goal_execution_state == "blocked":
            if "unblock_active_task" in steps or "recover_goal_progress" in steps:
                return None
            return "recover_goal_progress"
        if goal_execution_state == "recovering":
            if (
                "unblock_active_task" in steps
                or "recover_goal_progress" in steps
                or "stabilize_goal_recovery" in steps
            ):
                return None
            return "stabilize_goal_recovery"
        if goal_execution_state == "advancing":
            if "advance_active_task" in steps or "continue_goal_execution" in steps:
                return None
            return "continue_goal_execution"
        if goal_execution_state == "stagnating":
            if (
                "unblock_active_task" in steps
                or "recover_goal_progress" in steps
                or "restart_goal_progress" in steps
            ):
                return None
            return "restart_goal_progress"
        if goal_execution_state == "progressing":
            if "advance_active_task" in steps or "preserve_goal_momentum" in steps:
                return None
            return "preserve_goal_momentum"
        return None

    def _goal_progress_step(self, goal_progress_score: float, steps: list[str]) -> str | None:
        if goal_progress_score <= 0.0:
            return None
        if goal_progress_score < 0.35:
            if "increase_goal_progress" in steps or "restart_goal_progress" in steps:
                return None
            return "increase_goal_progress"
        if goal_progress_score >= 0.75:
            if "push_goal_to_completion" in steps or "continue_goal_execution" in steps:
                return None
            return "push_goal_to_completion"
        return None

    def _goal_progress_trend_step(self, goal_progress_trend: str, steps: list[str]) -> str | None:
        if goal_progress_trend == "slipping":
            if (
                "correct_goal_drift" in steps
                or "recover_goal_progress" in steps
                or "restart_goal_progress" in steps
            ):
                return None
            return "correct_goal_drift"
        if goal_progress_trend == "improving":
            if (
                "reinforce_goal_progress" in steps
                or "continue_goal_execution" in steps
                or "push_goal_to_completion" in steps
            ):
                return None
            return "reinforce_goal_progress"
        if goal_progress_trend == "steady":
            if "maintain_goal_consistency" in steps or "preserve_goal_momentum" in steps:
                return None
            return "maintain_goal_consistency"
        return None

    def _goal_history_step(self, goal_history_signal: str, steps: list[str]) -> str | None:
        if goal_history_signal == "regression":
            if (
                "rebuild_goal_trajectory" in steps
                or "correct_goal_drift" in steps
                or "restart_goal_progress" in steps
                or "recover_goal_progress" in steps
            ):
                return None
            return "rebuild_goal_trajectory"
        if goal_history_signal == "lift":
            if (
                "protect_goal_trajectory" in steps
                or "reinforce_goal_progress" in steps
                or "push_goal_to_completion" in steps
            ):
                return None
            return "protect_goal_trajectory"
        if goal_history_signal == "volatile":
            if "stabilize_goal_trajectory" in steps or "stabilize_goal_recovery" in steps:
                return None
            return "stabilize_goal_trajectory"
        return None

    def _goal_progress_arc_step(self, goal_progress_arc: str, steps: list[str]) -> str | None:
        if goal_progress_arc == "recovery_gaining_traction":
            if "consolidate_goal_recovery" in steps or "stabilize_goal_recovery" in steps:
                return None
            return "consolidate_goal_recovery"
        if goal_progress_arc == "breakthrough_momentum":
            if "capitalize_on_goal_breakthrough" in steps or "push_goal_to_completion" in steps:
                return None
            return "capitalize_on_goal_breakthrough"
        if goal_progress_arc == "unstable_progress":
            if "stabilize_goal_progress_arc" in steps or "stabilize_goal_trajectory" in steps:
                return None
            return "stabilize_goal_progress_arc"
        if goal_progress_arc == "falling_behind":
            if "rescue_goal_progress_arc" in steps or "correct_goal_drift" in steps or "rebuild_goal_trajectory" in steps:
                return None
            return "rescue_goal_progress_arc"
        if goal_progress_arc == "holding_pattern":
            if "sustain_goal_holding_pattern" in steps or "maintain_goal_consistency" in steps:
                return None
            return "sustain_goal_holding_pattern"
        return None

    def _goal_milestone_transition_step(self, goal_milestone_transition: str, steps: list[str]) -> str | None:
        if goal_milestone_transition == "entered_execution_phase":
            if "convert_goal_into_execution" in steps or "continue_goal_execution" in steps:
                return None
            return "convert_goal_into_execution"
        if goal_milestone_transition == "entered_completion_window":
            if "close_goal_completion_window" in steps or "push_goal_to_completion" in steps:
                return None
            return "close_goal_completion_window"
        if goal_milestone_transition == "slipped_from_completion_window":
            if "restore_completion_window" in steps or "rescue_goal_progress_arc" in steps:
                return None
            return "restore_completion_window"
        if goal_milestone_transition == "dropped_back_to_early_stage":
            if "rebuild_goal_foundation" in steps or "restart_goal_progress" in steps:
                return None
            return "rebuild_goal_foundation"
        return None

    def _goal_milestone_state_step(self, goal_milestone_state: str, steps: list[str]) -> str | None:
        if goal_milestone_state == "early_stage":
            if "establish_goal_foundation" in steps or "increase_goal_progress" in steps or "rebuild_goal_foundation" in steps:
                return None
            return "establish_goal_foundation"
        if goal_milestone_state == "execution_phase":
            if "sustain_goal_execution_phase" in steps or "continue_goal_execution" in steps or "advance_active_task" in steps:
                return None
            return "sustain_goal_execution_phase"
        if goal_milestone_state == "recovery_phase":
            if "stabilize_goal_recovery_phase" in steps or "stabilize_goal_recovery" in steps or "consolidate_goal_recovery" in steps:
                return None
            return "stabilize_goal_recovery_phase"
        if goal_milestone_state == "completion_window":
            if "drive_goal_to_closure" in steps or "close_goal_completion_window" in steps or "push_goal_to_completion" in steps:
                return None
            return "drive_goal_to_closure"
        return None

    def _goal_milestone_risk_step(self, goal_milestone_risk: str, steps: list[str]) -> str | None:
        if goal_milestone_risk == "at_risk":
            if "reduce_milestone_risk" in steps or "recover_goal_progress" in steps or "correct_goal_drift" in steps:
                return None
            return "reduce_milestone_risk"
        if goal_milestone_risk == "watch":
            if "monitor_milestone_risk" in steps or "stabilize_goal_progress_arc" in steps:
                return None
            return "monitor_milestone_risk"
        if goal_milestone_risk == "ready_to_close":
            if "validate_milestone_closure" in steps or "drive_goal_to_closure" in steps or "close_goal_completion_window" in steps:
                return None
            return "validate_milestone_closure"
        if goal_milestone_risk == "stabilizing":
            if "stabilize_milestone_recovery" in steps or "stabilize_goal_recovery" in steps or "consolidate_goal_recovery" in steps:
                return None
            return "stabilize_milestone_recovery"
        return None

    def _goal_milestone_pressure_step(self, goal_milestone_pressure: str, steps: list[str]) -> str | None:
        if goal_milestone_pressure == "building_closure_pressure":
            if "tighten_completion_window" in steps or "push_goal_to_completion" in steps:
                return None
            return "tighten_completion_window"
        if goal_milestone_pressure == "lingering_completion":
            if "force_goal_closure_decision" in steps or "confirm_goal_completion" in steps:
                return None
            return "force_goal_closure_decision"
        if goal_milestone_pressure == "dragging_recovery":
            if "break_recovery_drag" in steps or "stabilize_goal_recovery" in steps:
                return None
            return "break_recovery_drag"
        if goal_milestone_pressure == "stale_execution":
            if "unstick_execution_phase" in steps or "continue_goal_execution" in steps:
                return None
            return "unstick_execution_phase"
        if goal_milestone_pressure == "lingering_setup":
            if "force_first_execution_step" in steps or "define_first_execution_step" in steps:
                return None
            return "force_first_execution_step"
        return None

    def _goal_milestone_dependency_step(self, goal_milestone_dependency_state: str, steps: list[str]) -> str | None:
        if goal_milestone_dependency_state == "blocked_dependency":
            if (
                "resolve_blocking_dependency" in steps
                or "resolve_remaining_blocker" in steps
                or "unblock_active_task" in steps
            ):
                return None
            return "resolve_blocking_dependency"
        if goal_milestone_dependency_state == "multi_step_dependency":
            if (
                "sequence_remaining_dependencies" in steps
                or "finish_remaining_active_work" in steps
            ):
                return None
            return "sequence_remaining_dependencies"
        if goal_milestone_dependency_state == "single_step_dependency":
            if (
                "finish_last_dependency" in steps
                or "finish_remaining_active_work" in steps
                or "advance_active_task" in steps
            ):
                return None
            return "finish_last_dependency"
        if goal_milestone_dependency_state == "clear_to_close":
            if (
                "confirm_dependency_clearance" in steps
                or "confirm_goal_completion" in steps
                or "validate_milestone_closure" in steps
            ):
                return None
            return "confirm_dependency_clearance"
        return None

    def _goal_milestone_due_step(self, goal_milestone_due_state: str, steps: list[str]) -> str | None:
        if goal_milestone_due_state == "closure_due_now":
            if (
                "make_due_closure_call" in steps
                or "confirm_goal_completion" in steps
                or "validate_milestone_closure" in steps
            ):
                return None
            return "make_due_closure_call"
        if goal_milestone_due_state == "dependency_due_next":
            if (
                "finish_due_dependency" in steps
                or "sequence_remaining_dependencies" in steps
                or "finish_last_dependency" in steps
            ):
                return None
            return "finish_due_dependency"
        if goal_milestone_due_state == "recovery_due_attention":
            if (
                "restore_due_recovery" in steps
                or "stabilize_goal_recovery" in steps
                or "break_recovery_drag" in steps
            ):
                return None
            return "restore_due_recovery"
        if goal_milestone_due_state == "execution_due_attention":
            if (
                "push_due_execution" in steps
                or "continue_goal_execution" in steps
                or "unstick_execution_phase" in steps
            ):
                return None
            return "push_due_execution"
        if goal_milestone_due_state == "setup_due_start":
            if (
                "start_due_execution" in steps
                or "define_first_execution_step" in steps
                or "force_first_execution_step" in steps
            ):
                return None
            return "start_due_execution"
        return None

    def _goal_milestone_due_window_step(self, goal_milestone_due_window: str, steps: list[str]) -> str | None:
        if goal_milestone_due_window == "fresh_due_window":
            if "work_within_due_window" in steps or "make_due_closure_call" in steps:
                return None
            return "work_within_due_window"
        if goal_milestone_due_window == "active_due_window":
            if "keep_due_window_moving" in steps or "finish_due_dependency" in steps:
                return None
            return "keep_due_window_moving"
        if goal_milestone_due_window == "overdue_due_window":
            if "recover_overdue_window" in steps or "force_goal_closure_decision" in steps:
                return None
            return "recover_overdue_window"
        if goal_milestone_due_window == "reopened_due_window":
            if "stabilize_reopened_due_window" in steps or "stabilize_reentered_completion_window" in steps:
                return None
            return "stabilize_reopened_due_window"
        return None

    def _goal_completion_criteria_step(self, goal_completion_criteria: str, steps: list[str]) -> str | None:
        if goal_completion_criteria == "resolve_remaining_blocker":
            if "resolve_remaining_blocker" in steps or "unblock_active_task" in steps or "reduce_milestone_risk" in steps:
                return None
            return "resolve_remaining_blocker"
        if goal_completion_criteria == "finish_remaining_active_work":
            if "finish_remaining_active_work" in steps or "advance_active_task" in steps or "continue_goal_execution" in steps:
                return None
            return "finish_remaining_active_work"
        if goal_completion_criteria == "confirm_goal_completion":
            if "confirm_goal_completion" in steps or "validate_milestone_closure" in steps or "drive_goal_to_closure" in steps:
                return None
            return "confirm_goal_completion"
        if goal_completion_criteria == "stabilize_remaining_work":
            if "stabilize_remaining_work" in steps or "stabilize_goal_recovery" in steps or "consolidate_goal_recovery" in steps:
                return None
            return "stabilize_remaining_work"
        if goal_completion_criteria == "unblock_next_task":
            if "unblock_next_task" in steps or "resolve_remaining_blocker" in steps or "recover_goal_progress" in steps:
                return None
            return "unblock_next_task"
        if goal_completion_criteria == "define_first_execution_step":
            if "define_first_execution_step" in steps or "establish_goal_foundation" in steps or "increase_goal_progress" in steps:
                return None
            return "define_first_execution_step"
        if goal_completion_criteria == "advance_next_task":
            if "advance_next_task" in steps or "advance_active_task" in steps or "continue_goal_execution" in steps:
                return None
            return "advance_next_task"
        return None

    def _goal_milestone_arc_step(self, goal_milestone_arc_signal: str, steps: list[str]) -> str | None:
        if goal_milestone_arc_signal == "closure_momentum":
            if (
                "protect_milestone_closure_arc" in steps
                or "drive_goal_to_closure" in steps
            ):
                return None
            return "protect_milestone_closure_arc"
        if goal_milestone_arc_signal == "reentered_completion_window":
            if (
                "stabilize_reentered_completion_window" in steps
                or "drive_goal_to_closure" in steps
            ):
                return None
            return "stabilize_reentered_completion_window"
        if goal_milestone_arc_signal == "recovery_backslide":
            if (
                "arrest_milestone_backslide" in steps
                or "reduce_milestone_risk" in steps
                or "stabilize_goal_recovery" in steps
            ):
                return None
            return "arrest_milestone_backslide"
        if goal_milestone_arc_signal == "milestone_whiplash":
            if "dampen_milestone_whiplash" in steps or "monitor_milestone_risk" in steps:
                return None
            return "dampen_milestone_whiplash"
        if goal_milestone_arc_signal == "steady_closure":
            if "hold_milestone_closure_line" in steps:
                return None
            return "hold_milestone_closure_line"
        return None

    def _apply_active_goal(self, goal: str, relevant_goal: dict) -> str:
        goal_name = str(relevant_goal.get("name", "")).strip()
        if not goal_name:
            return goal
        return f"{goal} Keep the response aligned with the active goal '{goal_name}'."

    def _apply_active_milestone(self, goal: str, relevant_milestone: dict) -> str:
        milestone_name = str(relevant_milestone.get("name", "")).strip()
        if not milestone_name:
            return goal
        return f"{goal} Keep the response aligned with the active milestone '{milestone_name}'."

    def _apply_active_milestone_signals(self, goal: str, relevant_milestone: dict) -> str:
        dependency_state = str(relevant_milestone.get("dependency_state", "")).strip().lower()
        due_state = str(relevant_milestone.get("due_state", "")).strip().lower()
        due_window = str(relevant_milestone.get("due_window", "")).strip().lower()
        risk_level = str(relevant_milestone.get("risk_level", "")).strip().lower()
        completion_criteria = str(relevant_milestone.get("completion_criteria", "")).strip().lower()
        hints: list[str] = []
        if dependency_state:
            hints.append(
                "Treat the milestone dependency state as "
                f"'{dependency_state.replace('_', ' ')}'."
            )
        if due_state:
            hints.append(
                "Treat the milestone due state as "
                f"'{due_state.replace('_', ' ')}'."
            )
        if due_window:
            hints.append(
                "Treat the milestone due window as "
                f"'{due_window.replace('_', ' ')}'."
            )
        if risk_level:
            hints.append(f"Treat the milestone risk as '{risk_level}'.")
        if completion_criteria:
            hints.append(
                "Use the milestone completion criterion "
                f"'{completion_criteria.replace('_', ' ')}' as the operational finish line."
            )
        if not hints:
            return goal
        return f"{goal} {' '.join(hints)}"

    def _text_tokens(self, value: str) -> set[str]:
        return shared_text_tokens(value, normalize=False)

    def _priority_rank(self, priority: str) -> int:
        return shared_priority_rank(priority)

    def _task_status_rank(self, status: str) -> int:
        return shared_task_status_rank(status)

    def _goal_history_signal(self, goal_progress_history: list[dict]) -> str:
        return shared_goal_history_signal(goal_progress_history)

    def _goal_milestone_arc_signal(self, goal_milestone_history: list[dict]) -> str:
        return shared_goal_milestone_arc_signal(goal_milestone_history)
