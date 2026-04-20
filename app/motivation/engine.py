from app.core.adaptive_policy import dominant_theta_channel, should_apply_motivation_adaptive_tie_break
from app.core.contracts import ContextOutput, Event, MotivationOutput, PerceptionOutput
from app.proactive.engine import ProactiveDecisionEngine
from app.utils.goal_task_selection import (
    has_related_blocked_task as shared_has_related_blocked_task,
    priority_rank as shared_priority_rank,
    related_goal_priority as shared_related_goal_priority,
    text_tokens as shared_text_tokens,
)
from app.utils.language import normalize_for_matching
from app.utils.progress_signals import (
    goal_history_signal as shared_goal_history_signal,
    goal_milestone_arc_signal as shared_goal_milestone_arc_signal,
)


class MotivationEngine:
    def __init__(self, proactive_decision_engine: ProactiveDecisionEngine | None = None):
        self.proactive_decision_engine = proactive_decision_engine or ProactiveDecisionEngine()

    def run(
        self,
        event: Event,
        context: ContextOutput,
        perception: PerceptionOutput,
        user_preferences: dict | None = None,
        theta: dict | None = None,
        active_goals: list[dict] | None = None,
        active_tasks: list[dict] | None = None,
        goal_milestone_history: list[dict] | None = None,
        goal_progress_history: list[dict] | None = None,
    ) -> MotivationOutput:
        text = str(event.payload.get("text", "")).strip()
        lowered = normalize_for_matching(text)
        affective = perception.affective
        affective_label = str(affective.affect_label).strip().lower()
        affective_intensity = max(0.0, min(1.0, float(affective.intensity or 0.0)))
        affective_needs_support = bool(affective.needs_support)
        proactive_decision = self.proactive_decision_engine.decide(
            event=event,
            context=context,
            user_preferences=user_preferences or {},
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
        )
        if proactive_decision is not None:
            return self._motivation_from_proactive_decision(proactive_decision)

        if not text:
            return MotivationOutput(
                importance=0.3,
                urgency=0.1,
                valence=0.0,
                arousal=0.1,
                mode="clarify",
            )

        urgent_keywords = {
            "urgent",
            "asap",
            "immediately",
            "now",
            "blocked",
            "broken",
            "production",
            "failing",
            "deadline",
            "pilne",
            "natychmiast",
            "teraz",
            "blokuje",
            "awaria",
            "produkcja",
            "termin",
        }
        analysis_keywords = {
            "analyze",
            "analysis",
            "review",
            "compare",
            "debug",
            "explain",
            "plan",
            "analiza",
            "przeanalizuj",
            "porownaj",
            "wyjasnij",
            "sprawdz",
            "zaplanuj",
        }
        execution_keywords = {
            "build",
            "create",
            "write",
            "fix",
            "implement",
            "add",
            "setup",
            "deploy",
            "zbuduj",
            "stworz",
            "napisz",
            "napraw",
            "wdroz",
            "dodaj",
            "skonfiguruj",
            "ustaw",
            "zrob",
        }

        has_question = text.endswith("?")
        has_urgent_signal = any(keyword in lowered for keyword in urgent_keywords) or "!" in text or affective_label == "urgent_pressure"
        has_emotional_signal = affective_needs_support or affective_label == "support_distress"
        has_analysis_signal = has_question or any(keyword in lowered for keyword in analysis_keywords)
        has_execution_signal = any(lowered.startswith(keyword) for keyword in execution_keywords)
        has_positive_signal = affective_label == "positive_engagement"
        is_brief_turn = len(lowered.split()) <= 4
        collaboration_preference = str((user_preferences or {}).get("collaboration_preference", "")).strip().lower()
        affective_support_pattern = str((user_preferences or {}).get("affective_support_pattern", "")).strip().lower()
        affective_support_sensitivity = str(
            (user_preferences or {}).get("affective_support_sensitivity", "")
        ).strip().lower()
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
        milestone_arc_signal = goal_milestone_arc or self._goal_milestone_arc_signal(goal_milestone_history or [])
        goal_history_signal = self._goal_history_signal(goal_progress_history or [])
        related_goal_priority = self._related_goal_priority(text=text, goals=active_goals or [])
        blocked_task_match = self._has_related_blocked_task(text=text, tasks=active_tasks or [])

        importance = 0.45
        importance += 0.15 if has_question else 0.0
        importance += 0.2 if has_urgent_signal else 0.0
        importance += min(context.risk_level, 0.2)
        importance += (
            0.06
            if affective_support_pattern == "recurring_distress"
            else 0.03
            if affective_support_pattern == "confidence_recovery"
            else 0.0
        )
        importance += (
            0.04
            if affective_support_sensitivity == "high"
            else 0.02
            if affective_support_sensitivity == "moderate"
            else 0.0
        )
        importance += {"medium": 0.05, "high": 0.1, "critical": 0.18}.get(related_goal_priority, 0.0)
        importance += 0.08 if blocked_task_match else 0.0
        importance += (
            0.06
            if goal_execution_state == "blocked"
            else 0.05
            if goal_execution_state == "recovering"
            else 0.04
            if goal_execution_state == "advancing"
            else 0.04
            if goal_execution_state == "stagnating"
            else 0.03
            if goal_execution_state == "progressing"
            else 0.0
        )
        importance += 0.04 if 0 < goal_progress_score < 0.35 else 0.03 if goal_progress_score >= 0.75 else 0.0
        importance += (
            0.05
            if goal_progress_trend == "slipping"
            else 0.03
            if goal_progress_trend == "improving"
            else 0.01
            if goal_progress_trend == "steady"
            else 0.0
        )
        importance += (
            0.05
            if goal_progress_arc == "falling_behind"
            else 0.04
            if goal_progress_arc == "unstable_progress"
            else 0.03
            if goal_progress_arc in {"recovery_gaining_traction", "breakthrough_momentum"}
            else 0.01
            if goal_progress_arc == "holding_pattern"
            else 0.0
        )
        importance += (
            0.05
            if goal_milestone_state == "completion_window"
            else 0.04
            if goal_milestone_state == "recovery_phase"
            else 0.03
            if goal_milestone_state == "execution_phase"
            else 0.02
            if goal_milestone_state == "early_stage"
            else 0.0
        )
        importance += (
            0.05
            if goal_milestone_transition == "slipped_from_completion_window"
            else 0.04
            if goal_milestone_transition == "entered_completion_window"
            else 0.04
            if goal_milestone_transition == "dropped_back_to_early_stage"
            else 0.03
            if goal_milestone_transition == "entered_execution_phase"
            else 0.0
        )
        importance += (
            0.06
            if goal_milestone_risk == "at_risk"
            else 0.04
            if goal_milestone_risk == "ready_to_close"
            else 0.03
            if goal_milestone_risk in {"watch", "stabilizing"}
            else 0.01
            if goal_milestone_risk == "on_track"
            else 0.0
        )
        importance += (
            0.05
            if goal_completion_criteria in {"resolve_remaining_blocker", "finish_remaining_active_work"}
            else 0.04
            if goal_completion_criteria == "confirm_goal_completion"
            else 0.03
            if goal_completion_criteria in {"stabilize_remaining_work", "unblock_next_task"}
            else 0.02
            if goal_completion_criteria in {"define_first_execution_step", "advance_next_task"}
            else 0.0
        )
        importance += (
            0.07
            if goal_milestone_pressure == "lingering_completion"
            else 0.06
            if goal_milestone_pressure == "dragging_recovery"
            else 0.05
            if goal_milestone_pressure == "stale_execution"
            else 0.04
            if goal_milestone_pressure in {"building_closure_pressure", "lingering_setup"}
            else 0.0
        )
        importance += (
            0.06
            if goal_milestone_dependency_state == "blocked_dependency"
            else 0.04
            if goal_milestone_dependency_state == "multi_step_dependency"
            else 0.03
            if goal_milestone_dependency_state == "single_step_dependency"
            else 0.04
            if goal_milestone_dependency_state == "clear_to_close"
            else 0.0
        )
        importance += (
            0.07
            if goal_milestone_due_state == "closure_due_now"
            else 0.06
            if goal_milestone_due_state == "dependency_due_next"
            else 0.05
            if goal_milestone_due_state in {"recovery_due_attention", "execution_due_attention"}
            else 0.04
            if goal_milestone_due_state == "setup_due_start"
            else 0.0
        )
        importance += (
            0.04
            if goal_milestone_due_window == "fresh_due_window"
            else 0.03
            if goal_milestone_due_window == "active_due_window"
            else 0.07
            if goal_milestone_due_window == "overdue_due_window"
            else 0.06
            if goal_milestone_due_window == "reopened_due_window"
            else 0.0
        )
        importance += (
            0.06
            if milestone_arc_signal == "recovery_backslide"
            else 0.05
            if milestone_arc_signal in {"closure_momentum", "reentered_completion_window"}
            else 0.04
            if milestone_arc_signal == "milestone_whiplash"
            else 0.03
            if milestone_arc_signal == "steady_closure"
            else 0.0
        )
        importance += 0.04 if goal_history_signal == "regression" else 0.02 if goal_history_signal == "lift" else 0.0

        urgency = 0.2
        urgency += 0.45 if has_urgent_signal else 0.0
        urgency += 0.1 if has_execution_signal else 0.0
        urgency += (
            0.05
            if affective_support_pattern == "recurring_distress"
            else 0.02
            if affective_support_pattern == "confidence_recovery"
            else 0.0
        )
        urgency += (
            0.04
            if affective_support_sensitivity == "high"
            else 0.02
            if affective_support_sensitivity == "moderate"
            else 0.0
        )
        urgency += 0.15 if blocked_task_match else 0.0
        urgency += (
            0.08
            if goal_execution_state == "blocked"
            else 0.04
            if goal_execution_state == "recovering"
            else 0.03
            if goal_execution_state == "advancing"
            else 0.05
            if goal_execution_state == "stagnating"
            else 0.0
        )
        urgency += 0.03 if 0 < goal_progress_score < 0.35 else 0.04 if goal_progress_score >= 0.75 else 0.0
        urgency += 0.05 if goal_progress_trend == "slipping" else 0.02 if goal_progress_trend == "improving" else 0.0
        urgency += (
            0.05
            if goal_progress_arc == "falling_behind"
            else 0.04
            if goal_progress_arc == "unstable_progress"
            else 0.02
            if goal_progress_arc == "breakthrough_momentum"
            else 0.01
            if goal_progress_arc in {"recovery_gaining_traction", "holding_pattern"}
            else 0.0
        )
        urgency += (
            0.05
            if goal_milestone_state == "completion_window"
            else 0.03
            if goal_milestone_state == "recovery_phase"
            else 0.03
            if goal_milestone_state == "execution_phase"
            else 0.02
            if goal_milestone_state == "early_stage"
            else 0.0
        )
        urgency += (
            0.08
            if goal_milestone_transition == "slipped_from_completion_window"
            else 0.1
            if goal_milestone_transition == "entered_completion_window"
            else 0.05
            if goal_milestone_transition == "dropped_back_to_early_stage"
            else 0.03
            if goal_milestone_transition == "entered_execution_phase"
            else 0.0
        )
        urgency += (
            0.08
            if goal_milestone_risk == "at_risk"
            else 0.07
            if goal_milestone_risk == "ready_to_close"
            else 0.04
            if goal_milestone_risk in {"watch", "stabilizing"}
            else 0.02
            if goal_milestone_risk == "on_track"
            else 0.0
        )
        urgency += (
            0.08
            if goal_completion_criteria == "resolve_remaining_blocker"
            else 0.07
            if goal_completion_criteria == "finish_remaining_active_work"
            else 0.06
            if goal_completion_criteria == "confirm_goal_completion"
            else 0.05
            if goal_completion_criteria in {"stabilize_remaining_work", "unblock_next_task"}
            else 0.03
            if goal_completion_criteria in {"define_first_execution_step", "advance_next_task"}
            else 0.0
        )
        urgency += (
            0.09
            if goal_milestone_pressure == "lingering_completion"
            else 0.07
            if goal_milestone_pressure == "dragging_recovery"
            else 0.06
            if goal_milestone_pressure == "stale_execution"
            else 0.05
            if goal_milestone_pressure in {"building_closure_pressure", "lingering_setup"}
            else 0.0
        )
        urgency += (
            0.08
            if goal_milestone_dependency_state == "blocked_dependency"
            else 0.05
            if goal_milestone_dependency_state == "multi_step_dependency"
            else 0.04
            if goal_milestone_dependency_state == "single_step_dependency"
            else 0.06
            if goal_milestone_dependency_state == "clear_to_close"
            else 0.0
        )
        urgency += (
            0.1
            if goal_milestone_due_state == "closure_due_now"
            else 0.08
            if goal_milestone_due_state == "dependency_due_next"
            else 0.07
            if goal_milestone_due_state in {"recovery_due_attention", "execution_due_attention"}
            else 0.05
            if goal_milestone_due_state == "setup_due_start"
            else 0.0
        )
        urgency += (
            0.05
            if goal_milestone_due_window == "fresh_due_window"
            else 0.04
            if goal_milestone_due_window == "active_due_window"
            else 0.09
            if goal_milestone_due_window == "overdue_due_window"
            else 0.08
            if goal_milestone_due_window == "reopened_due_window"
            else 0.0
        )
        urgency += (
            0.08
            if milestone_arc_signal == "recovery_backslide"
            else 0.07
            if milestone_arc_signal in {"closure_momentum", "reentered_completion_window"}
            else 0.05
            if milestone_arc_signal == "milestone_whiplash"
            else 0.04
            if milestone_arc_signal == "steady_closure"
            else 0.0
        )
        urgency += 0.04 if goal_history_signal == "regression" else 0.01 if goal_history_signal == "lift" else 0.0

        if has_emotional_signal:
            valence = max(-1.0, -0.25 - (0.45 * affective_intensity))
        elif has_positive_signal:
            valence = min(1.0, 0.15 + (0.45 * affective_intensity))
        elif has_urgent_signal:
            valence = -0.1
        elif affective_support_pattern == "recurring_distress":
            valence = -0.08
        else:
            valence = 0.05

        arousal = 0.3
        arousal += 0.35 if has_urgent_signal else 0.0
        arousal += (0.1 + (0.2 * affective_intensity)) if has_emotional_signal else 0.0
        arousal += 0.1 if has_question else 0.0

        adaptive_tie_break_allowed = should_apply_motivation_adaptive_tie_break(
            intent=perception.intent,
            topic=perception.topic,
            is_brief_turn=is_brief_turn,
            has_positive_signal=has_positive_signal,
            has_emotional_signal=has_emotional_signal,
            has_execution_signal=has_execution_signal,
            has_analysis_signal=has_analysis_signal,
        )
        theta_mode = self._theta_mode(theta) if adaptive_tie_break_allowed else None
        collaboration_mode = (
            self._collaboration_mode(collaboration_preference)
            if adaptive_tie_break_allowed
            else None
        )

        if has_emotional_signal:
            mode = "respond"
        elif has_execution_signal:
            mode = "execute"
        elif has_analysis_signal:
            mode = "analyze"
        elif collaboration_mode:
            mode = collaboration_mode
            importance += 0.05
            if collaboration_mode == "execute":
                urgency += 0.08
                arousal += 0.05
        elif theta_mode:
            mode = theta_mode
            importance += 0.05
            if theta_mode == "execute":
                urgency += 0.08
                arousal += 0.05
            elif theta_mode == "respond":
                valence = min(valence, -0.05)
        else:
            mode = "respond"

        return MotivationOutput(
            importance=self._clamp(importance),
            urgency=self._clamp(urgency),
            valence=max(-1.0, min(1.0, valence)),
            arousal=self._clamp(arousal),
            mode=mode,
        )

    def _related_goal_priority(self, text: str, goals: list[dict]) -> str | None:
        return shared_related_goal_priority(text=text, goals=goals, tokenize=self._text_tokens)

    def _has_related_blocked_task(self, text: str, tasks: list[dict]) -> bool:
        return shared_has_related_blocked_task(text=text, tasks=tasks, tokenize=self._text_tokens)

    def _text_tokens(self, value: str) -> set[str]:
        return shared_text_tokens(value, normalize=True)

    def _priority_rank(self, priority: str) -> int:
        return shared_priority_rank(priority)

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, round(value, 2)))

    def _theta_mode(self, theta: dict | None) -> str | None:
        channel = dominant_theta_channel(theta)
        if channel is None:
            return None
        mode_by_channel = {
            "support": "respond",
            "analysis": "analyze",
            "execution": "execute",
        }
        return mode_by_channel.get(channel)

    def _collaboration_mode(self, collaboration_preference: str) -> str | None:
        if collaboration_preference == "hands_on":
            return "execute"
        if collaboration_preference == "guided":
            return "analyze"
        return None

    def _goal_history_signal(self, goal_progress_history: list[dict]) -> str:
        return shared_goal_history_signal(goal_progress_history)

    def _goal_milestone_arc_signal(self, goal_milestone_history: list[dict]) -> str:
        return shared_goal_milestone_arc_signal(goal_milestone_history)

    def _motivation_from_proactive_decision(self, proactive_decision) -> MotivationOutput:
        if not proactive_decision.should_interrupt:
            return MotivationOutput(
                importance=self._clamp(proactive_decision.importance),
                urgency=self._clamp(proactive_decision.urgency),
                valence=0.0,
                arousal=0.1,
                mode="ignore",
            )

        mode_by_output = {
            "suggestion": "respond",
            "reminder": "respond",
            "question": "clarify",
            "warning": "execute",
            "encouragement": "respond",
            "insight": "analyze",
        }
        output_type = str(proactive_decision.output_type)
        mode = mode_by_output.get(output_type, "respond")
        valence = 0.05
        if output_type == "warning":
            valence = -0.15
        elif output_type == "encouragement":
            valence = 0.2

        arousal = self._clamp(0.2 + (0.7 * float(proactive_decision.urgency)))
        return MotivationOutput(
            importance=self._clamp(max(float(proactive_decision.importance), float(proactive_decision.relevance))),
            urgency=self._clamp(float(proactive_decision.urgency)),
            valence=max(-1.0, min(1.0, valence)),
            arousal=arousal,
            mode=mode,
        )
