from app.core.contracts import (
    CalendarSchedulingIntentDomainIntent,
    ConnectedDriveAccessDomainIntent,
    ConnectorCapabilityDiscoveryDomainIntent,
    ConnectorPermissionGateOutput,
    ContextOutput,
    DomainActionIntent,
    Event,
    ExternalTaskSyncDomainIntent,
    MotivationOutput,
    NoopDomainIntent,
    PlanOutput,
    ProposalHandoffDecisionOutput,
    RoleOutput,
    SubconsciousProposalRecord,
    UpdateCollaborationPreferenceDomainIntent,
    UpdateResponseStyleDomainIntent,
    UpdateTaskStatusDomainIntent,
    ProactiveDecisionOutput,
    UpsertGoalDomainIntent,
    UpsertTaskDomainIntent,
)
from app.proactive.engine import ProactiveDecisionEngine, ProactiveDeliveryGuard
from app.utils.goal_task_signals import detect_goal_signal, detect_task_signal, detect_task_status_signal
from app.utils.preferences import detect_collaboration_preference, detect_response_style_preference
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
        relation_collaboration = self._relation_value(relations=relations or [], relation_type="collaboration_dynamic")
        relation_support = self._relation_value(relations=relations or [], relation_type="support_intensity_preference")
        relation_delivery = self._relation_value(relations=relations or [], relation_type="delivery_reliability")
        goal_milestone_arc_signal = goal_milestone_arc or self._goal_milestone_arc_signal(goal_milestone_history or [])
        goal_history_signal = self._goal_history_signal(goal_progress_history or [])
        proactive_decision = self.proactive_decision_engine.decide(
            event=event,
            context=context,
            user_preferences=user_preferences or {},
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
        )
        if proactive_decision is not None:
            return self._build_proactive_plan(
                event=event,
                motivation=motivation,
                proactive_decision=proactive_decision,
                user_preferences=user_preferences or {},
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
        if relation_delivery == "high_trust" and "favor_concrete_next_step" not in steps:
            prepare_index = steps.index("prepare_response") if "prepare_response" in steps else len(steps)
            steps.insert(prepare_index, "favor_concrete_next_step")

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

        domain_intents = self._build_domain_action_intents(event_text)
        domain_intents.extend(self._build_connector_expansion_intents(accepted_proposals))
        connector_permission_gates = self._build_connector_permission_gates(domain_intents)

        return PlanOutput(
            goal=goal,
            steps=steps,
            needs_action=needs_action,
            needs_response=needs_response,
            domain_intents=domain_intents,
            proposal_handoffs=proposal_handoffs,
            accepted_proposals=accepted_proposals,
            connector_permission_gates=connector_permission_gates,
        )

    def _build_proactive_plan(
        self,
        *,
        event: Event,
        motivation: MotivationOutput,
        proactive_decision: ProactiveDecisionOutput,
        user_preferences: dict,
    ) -> PlanOutput:
        base_steps = ["evaluate_proactive_trigger", "assess_user_context"]
        attention_gate = event.payload.get("attention_gate") if isinstance(event.payload, dict) else {}
        if isinstance(attention_gate, dict) and not bool(attention_gate.get("allowed", True)):
            return PlanOutput(
                goal="Defer proactive outreach until attention-gate conditions are satisfied.",
                steps=[*base_steps, "respect_attention_gate"],
                needs_action=False,
                needs_response=False,
                domain_intents=[NoopDomainIntent()],
                proactive_decision=proactive_decision,
            )
        if not proactive_decision.should_interrupt:
            return PlanOutput(
                goal="Defer proactive outreach until interruption cost becomes acceptable.",
                steps=[*base_steps, "defer_proactive_outreach"],
                needs_action=False,
                needs_response=False,
                domain_intents=[NoopDomainIntent()],
                proactive_decision=proactive_decision,
            )
        delivery_guard = self.proactive_delivery_guard.evaluate(
            event=event,
            user_preferences=user_preferences,
            proactive_decision=proactive_decision,
        )
        if delivery_guard is not None and not delivery_guard.allowed:
            return PlanOutput(
                goal="Defer proactive outreach until delivery guardrails pass.",
                steps=[*base_steps, "respect_proactive_delivery_guardrails"],
                needs_action=False,
                needs_response=False,
                domain_intents=[NoopDomainIntent()],
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
        steps.append("prepare_response")

        needs_response = True
        has_chat_id = isinstance(event.payload.get("chat_id"), (int, str))
        needs_action = needs_response and (
            event.source == "telegram"
            or (event.source == "scheduler" and has_chat_id)
        )
        if needs_action:
            steps.append("send_telegram_message")
        return PlanOutput(
            goal=goal_map.get(output_type, goal_map["suggestion"]),
            steps=steps,
            needs_action=needs_action,
            needs_response=needs_response,
            domain_intents=[NoopDomainIntent()],
            proactive_decision=proactive_decision,
            proactive_delivery_guard=delivery_guard,
        )

    def _build_domain_action_intents(self, event_text: str) -> list[DomainActionIntent]:
        intents: list[DomainActionIntent] = []
        lowered_text = event_text.strip().lower()

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

        calendar_intent = self._calendar_scheduling_intent(lowered_text)
        if calendar_intent is not None:
            intents.append(calendar_intent)

        external_task_intent = self._external_task_sync_intent(lowered_text)
        if external_task_intent is not None:
            intents.append(external_task_intent)

        connected_drive_intent = self._connected_drive_access_intent(lowered_text)
        if connected_drive_intent is not None:
            intents.append(connected_drive_intent)

        if not intents:
            return [NoopDomainIntent()]
        return intents

    def _calendar_scheduling_intent(self, lowered_text: str) -> CalendarSchedulingIntentDomainIntent | None:
        if not any(keyword in lowered_text for keyword in ("calendar", "kalendarz", "meeting", "spotkanie", "schedule")):
            return None
        if any(keyword in lowered_text for keyword in ("create", "utw", "zaplanuj", "book", "reserve")):
            return CalendarSchedulingIntentDomainIntent(
                operation="create_event",
                mode="mutate_with_confirmation",
                title_hint=lowered_text[:120],
                time_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("availability", "free", "woln", "when can", "kiedy")):
            return CalendarSchedulingIntentDomainIntent(
                operation="read_availability",
                mode="read_only",
                title_hint=lowered_text[:120],
                time_hint=lowered_text[:120],
            )
        return CalendarSchedulingIntentDomainIntent(
            operation="suggest_slots",
            mode="suggestion_only",
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
                mode="mutate_with_confirmation",
                task_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("sync", "synchron", "export", "mirror", "link")):
            return ExternalTaskSyncDomainIntent(
                operation="suggest_sync",
                provider_hint=provider,
                mode="suggestion_only",
                task_hint=lowered_text[:120],
            )
        return ExternalTaskSyncDomainIntent(
            operation="list_tasks",
            provider_hint=provider,
            mode="read_only",
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
                mode="mutate_with_confirmation",
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("upload", "add file", "wrzu", "zaladuj")):
            return ConnectedDriveAccessDomainIntent(
                operation="upload_file",
                provider_hint=provider,
                mode="mutate_with_confirmation",
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("update", "edit", "modify", "zmien", "edyt")):
            return ConnectedDriveAccessDomainIntent(
                operation="update_document",
                provider_hint=provider,
                mode="mutate_with_confirmation",
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("search", "find", "szuk", "znajd")):
            return ConnectedDriveAccessDomainIntent(
                operation="search_documents",
                provider_hint=provider,
                mode="read_only",
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("read", "open", "preview", "otw", "pokaz")):
            return ConnectedDriveAccessDomainIntent(
                operation="read_document",
                provider_hint=provider,
                mode="read_only",
                file_hint=lowered_text[:120],
            )
        if any(keyword in lowered_text for keyword in ("organize", "plan", "suggest", "uporzadkuj", "zaproponuj")):
            return ConnectedDriveAccessDomainIntent(
                operation="suggest_file_plan",
                provider_hint=provider,
                mode="suggestion_only",
                file_hint=lowered_text[:120],
            )
        return ConnectedDriveAccessDomainIntent(
            operation="list_files",
            provider_hint=provider,
            mode="read_only",
            file_hint=lowered_text[:120],
        )

    def _build_connector_permission_gates(
        self,
        domain_intents: list[DomainActionIntent],
    ) -> list[ConnectorPermissionGateOutput]:
        gates: list[ConnectorPermissionGateOutput] = []
        for intent in domain_intents:
            if isinstance(intent, CalendarSchedulingIntentDomainIntent):
                mutate = intent.mode == "mutate_with_confirmation"
                gates.append(
                    ConnectorPermissionGateOutput(
                        connector_kind="calendar",
                        provider_hint=intent.provider_hint,
                        operation=intent.operation,
                        mode=intent.mode,
                        requires_opt_in=True,
                        requires_confirmation=mutate,
                        allowed=not mutate,
                        reason=(
                            "explicit_user_confirmation_required"
                            if mutate
                            else "suggestion_or_read_only_allowed"
                        ),
                    )
                )
            if isinstance(intent, ExternalTaskSyncDomainIntent):
                mutate = intent.mode == "mutate_with_confirmation"
                gates.append(
                    ConnectorPermissionGateOutput(
                        connector_kind="task_system",
                        provider_hint=intent.provider_hint,
                        operation=intent.operation,
                        mode=intent.mode,
                        requires_opt_in=True,
                        requires_confirmation=mutate,
                        allowed=not mutate,
                        reason=(
                            "explicit_user_confirmation_required"
                            if mutate
                            else "suggestion_or_read_only_allowed"
                        ),
                    )
                )
            if isinstance(intent, ConnectedDriveAccessDomainIntent):
                mutate = intent.mode == "mutate_with_confirmation"
                gates.append(
                    ConnectorPermissionGateOutput(
                        connector_kind="cloud_drive",
                        provider_hint=intent.provider_hint,
                        operation=intent.operation,
                        mode=intent.mode,
                        requires_opt_in=True,
                        requires_confirmation=mutate,
                        allowed=not mutate,
                        reason=(
                            "explicit_user_confirmation_required"
                            if mutate
                            else "suggestion_or_read_only_allowed"
                        ),
                    )
                )
            if isinstance(intent, ConnectorCapabilityDiscoveryDomainIntent):
                gates.append(
                    ConnectorPermissionGateOutput(
                        connector_kind=intent.connector_kind,
                        provider_hint=intent.provider_hint,
                        operation=f"discover_{intent.requested_capability}",
                        mode=intent.mode,
                        requires_opt_in=False,
                        requires_confirmation=False,
                        allowed=True,
                        reason="proposal_only_no_external_access",
                    )
                )
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

        for raw in subconscious_proposals[:4]:
            proposal_id_raw = raw.get("proposal_id")
            try:
                proposal_id = int(proposal_id_raw)
            except (TypeError, ValueError):
                continue
            proposal = SubconsciousProposalRecord(
                proposal_id=proposal_id,
                proposal_type=str(raw.get("proposal_type", "nudge_user")),
                summary=str(raw.get("summary", "")),
                payload=raw.get("payload") if isinstance(raw.get("payload"), dict) else {},
                confidence=float(raw.get("confidence", 0.0) or 0.0),
                status=str(raw.get("status", "pending")),
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

            handoffs.append(
                ProposalHandoffDecisionOutput(
                    proposal_id=proposal_id,
                    decision=decision,  # type: ignore[arg-type]
                    reason=reason,
                )
            )
        return handoffs, accepted, extra_steps

    def _theta_plan_step(self, theta: dict | None, steps: list[str]) -> str | None:
        if not theta:
            return None

        candidates = {
            "maintain_supportive_stance": float(theta.get("support_bias", 0.0) or 0.0),
            "favor_structured_reasoning": float(theta.get("analysis_bias", 0.0) or 0.0),
            "favor_concrete_next_step": float(theta.get("execution_bias", 0.0) or 0.0),
        }
        step, bias = max(candidates.items(), key=lambda item: item[1])
        if bias < 0.58:
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

    def _relation_value(self, *, relations: list[dict], relation_type: str) -> str | None:
        for relation in relations:
            if str(relation.get("relation_type", "")).strip().lower() != relation_type:
                continue
            confidence = float(relation.get("confidence", 0.0) or 0.0)
            if confidence < 0.68:
                continue
            value = str(relation.get("relation_value", "")).strip().lower()
            if value:
                return value
        return None
