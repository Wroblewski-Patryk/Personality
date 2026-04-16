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
        goal_milestone_transition = str((user_preferences or {}).get("goal_milestone_transition", "")).strip().lower()
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

    def _apply_active_goal(self, goal: str, relevant_goal: dict) -> str:
        goal_name = str(relevant_goal.get("name", "")).strip()
        if not goal_name:
            return goal
        return f"{goal} Keep the response aligned with the active goal '{goal_name}'."

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
