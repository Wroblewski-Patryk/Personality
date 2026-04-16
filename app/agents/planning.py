from app.core.contracts import ContextOutput, Event, MotivationOutput, PlanOutput, RoleOutput


class PlanningAgent:
    def run(
        self,
        event: Event,
        context: ContextOutput,
        motivation: MotivationOutput,
        role: RoleOutput,
        user_preferences: dict | None = None,
        theta: dict | None = None,
        active_goals: list[dict] | None = None,
        active_tasks: list[dict] | None = None,
        active_goal_milestones: list[dict] | None = None,
        goal_milestone_history: list[dict] | None = None,
        goal_progress_history: list[dict] | None = None,
    ) -> PlanOutput:
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
        goal_milestone_arc_signal = goal_milestone_arc or self._goal_milestone_arc_signal(goal_milestone_history or [])
        goal_history_signal = self._goal_history_signal(goal_progress_history or [])

        if motivation.mode == "clarify":
            goal = "Ask for the missing information needed to help."
            steps.extend(["request_missing_input", "prepare_response"])
        elif motivation.mode == "support" or role.selected == "friend":
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

        return PlanOutput(
            goal=goal,
            steps=steps,
            needs_action=needs_action,
            needs_response=needs_response,
        )

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
        tokens = self._text_tokens(str(event.payload.get("text", "")))
        ranked = sorted(
            active_goals,
            key=lambda goal: (
                len(tokens.intersection(self._text_tokens(str(goal.get("name", "")) + " " + str(goal.get("description", ""))))),
                self._priority_rank(str(goal.get("priority", ""))),
            ),
            reverse=True,
        )
        if not ranked:
            return None
        top = ranked[0]
        overlap = len(tokens.intersection(self._text_tokens(str(top.get("name", "")) + " " + str(top.get("description", "")))))
        if overlap <= 0 and tokens:
            return None
        return top

    def _select_relevant_task(self, event: Event, active_tasks: list[dict], relevant_goal_id: int | None) -> dict | None:
        tokens = self._text_tokens(str(event.payload.get("text", "")))
        ranked = sorted(
            active_tasks,
            key=lambda task: (
                1 if relevant_goal_id is not None and task.get("goal_id") == relevant_goal_id else 0,
                len(tokens.intersection(self._text_tokens(str(task.get("name", "")) + " " + str(task.get("description", ""))))),
                self._task_status_rank(str(task.get("status", ""))),
                self._priority_rank(str(task.get("priority", ""))),
            ),
            reverse=True,
        )
        if not ranked:
            return None
        top = ranked[0]
        overlap = len(tokens.intersection(self._text_tokens(str(top.get("name", "")) + " " + str(top.get("description", "")))))
        if overlap <= 0 and relevant_goal_id is None and tokens:
            return None
        return top

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
        canonical = "".join(char if char.isalnum() or char.isspace() else " " for char in value.strip().lower())
        return {token for token in canonical.split() if len(token) >= 3}

    def _priority_rank(self, priority: str) -> int:
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }.get(priority, 0)

    def _task_status_rank(self, status: str) -> int:
        return {
            "todo": 1,
            "in_progress": 2,
            "blocked": 3,
        }.get(status, 0)

    def _goal_history_signal(self, goal_progress_history: list[dict]) -> str:
        if len(goal_progress_history) < 2:
            return ""

        ordered = list(reversed(goal_progress_history))
        scores: list[float] = []
        for item in ordered:
            try:
                scores.append(float(item.get("score", 0.0)))
            except (TypeError, ValueError):
                continue

        if len(scores) < 2:
            return ""

        delta = round(scores[-1] - scores[0], 2)
        span = round(max(scores) - min(scores), 2)
        if delta <= -0.2:
            return "regression"
        if delta >= 0.2:
            return "lift"
        if span >= 0.3:
            return "volatile"
        return ""

    def _goal_milestone_arc_signal(self, goal_milestone_history: list[dict]) -> str:
        if len(goal_milestone_history) < 2:
            return ""

        ordered = list(reversed(goal_milestone_history))
        states: list[tuple[str, str]] = []
        for item in ordered:
            pair = (
                str(item.get("phase", "")).strip().lower(),
                str(item.get("risk_level", "")).strip().lower(),
            )
            if not pair[0] and not pair[1]:
                continue
            if not states or states[-1] != pair:
                states.append(pair)

        if len(states) < 2:
            return ""

        previous_phase, previous_risk = states[-2]
        current_phase, current_risk = states[-1]
        had_completion_before = any(phase == "completion_window" for phase, _ in states[:-1])
        had_recovery_before = any(phase == "recovery_phase" for phase, _ in states[:-1])
        phase_changes = sum(
            1
            for index in range(1, len(states))
            if states[index][0] and states[index - 1][0] and states[index][0] != states[index - 1][0]
        )
        distinct_phases = {phase for phase, _ in states if phase}

        if current_phase == "completion_window" and had_completion_before and had_recovery_before and previous_phase != "completion_window":
            return "reentered_completion_window"
        if current_phase == "recovery_phase" and had_completion_before:
            return "recovery_backslide"
        if len(distinct_phases) >= 3 and phase_changes >= 3:
            return "milestone_whiplash"
        if current_phase == "completion_window" and previous_phase == "completion_window":
            return "steady_closure"
        if current_phase == "completion_window" and (
            previous_phase != "completion_window"
            or (previous_risk in {"watch", "stabilizing", "on_track"} and current_risk == "ready_to_close")
        ):
            return "closure_momentum"
        return ""
