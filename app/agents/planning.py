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
    ) -> PlanOutput:
        goal = "Provide a clear and useful response to the user event."
        steps = ["interpret_event", "review_context"]
        response_style = str((user_preferences or {}).get("response_style", "")).strip().lower()
        collaboration_preference = str((user_preferences or {}).get("collaboration_preference", "")).strip().lower()
        goal_execution_state = str((user_preferences or {}).get("goal_execution_state", "")).strip().lower()

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
        if goal_execution_state == "progressing":
            if "advance_active_task" in steps or "preserve_goal_momentum" in steps:
                return None
            return "preserve_goal_momentum"
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
