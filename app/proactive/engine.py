from __future__ import annotations

from app.core.contracts import (
    ContextOutput,
    Event,
    ProactiveDecisionOutput,
    ProactiveDeliveryGuardOutput,
    ProactiveOutputType,
)
from app.core.scheduler_contracts import SCHEDULER_PROACTIVE_TICK


class ProactiveDecisionEngine:
    OUTPUT_TRIGGER_MAP: dict[str, ProactiveOutputType] = {
        "time_checkin": "reminder",
        "goal_stagnation": "reminder",
        "goal_deadline": "warning",
        "task_blocked": "warning",
        "task_overdue": "warning",
        "memory_pattern": "insight",
        "relation_nudge": "encouragement",
        "external_alert": "warning",
    }

    def decide(
        self,
        *,
        event: Event,
        context: ContextOutput,
        user_preferences: dict | None = None,
        active_goals: list[dict] | None = None,
        active_tasks: list[dict] | None = None,
    ) -> ProactiveDecisionOutput | None:
        if event.source != "scheduler" or event.subsource != SCHEDULER_PROACTIVE_TICK:
            return None

        payload = event.payload if isinstance(event.payload, dict) else {}
        proactive = payload.get("proactive")
        proactive_payload = proactive if isinstance(proactive, dict) else {}
        trigger = str(proactive_payload.get("trigger", "time_checkin") or "time_checkin").strip().lower()
        output_type = self.OUTPUT_TRIGGER_MAP.get(trigger, "suggestion")

        importance = self._clamp_unit(
            proactive_payload.get("importance", 0.55 + min(max(context.risk_level, 0.0), 0.2))
        )
        urgency = self._clamp_unit(
            proactive_payload.get("urgency", 0.55 if output_type == "warning" else 0.45)
        )
        relevance = self._relevance(
            trigger=trigger,
            context=context,
            user_preferences=user_preferences or {},
            active_goals=active_goals or [],
            active_tasks=active_tasks or [],
        )
        user_context = proactive_payload.get("user_context") if isinstance(proactive_payload.get("user_context"), dict) else {}
        interruption_cost = self._interruption_cost(user_context=user_context)

        decision_score = round((importance * 0.45 + urgency * 0.35 + relevance * 0.2) - interruption_cost, 2)
        threshold = 0.2 if output_type == "warning" else 0.28
        if bool(user_context.get("quiet_hours", False)):
            threshold += 0.07
        should_interrupt = decision_score >= threshold

        mode = "soft"
        if output_type == "warning" and urgency >= 0.8 and should_interrupt:
            mode = "strong"
        elif urgency >= 0.6 or output_type in {"reminder", "insight"}:
            mode = "medium"

        reason = f"{trigger}_selected"
        if not should_interrupt:
            reason = "interruption_cost_too_high"

        return ProactiveDecisionOutput(
            trigger=trigger,
            output_type=output_type,
            mode=mode,
            importance=importance,
            urgency=urgency,
            relevance=relevance,
            interruption_cost=interruption_cost,
            decision_score=decision_score,
            should_interrupt=should_interrupt,
            reason=reason,
        )

    def _relevance(
        self,
        *,
        trigger: str,
        context: ContextOutput,
        user_preferences: dict,
        active_goals: list[dict],
        active_tasks: list[dict],
    ) -> float:
        relevance = 0.4 + min(max(context.risk_level, 0.0), 0.2)
        has_goal = bool(active_goals)
        has_blocked_task = any(str(task.get("status", "")).strip().lower() == "blocked" for task in active_tasks)
        if trigger in {"goal_stagnation", "goal_deadline"} and has_goal:
            relevance += 0.2
        if trigger in {"task_blocked", "task_overdue"} and has_blocked_task:
            relevance += 0.24
        if trigger == "relation_nudge":
            collaboration_preference = str(user_preferences.get("collaboration_preference", "")).strip().lower()
            if collaboration_preference in {"guided", "hands_on"}:
                relevance += 0.14
        if trigger == "memory_pattern":
            affective_pattern = str(user_preferences.get("affective_support_pattern", "")).strip().lower()
            if affective_pattern:
                relevance += 0.12
        return self._clamp_unit(relevance)

    def _interruption_cost(self, *, user_context: dict) -> float:
        interruption_cost = 0.18
        if bool(user_context.get("quiet_hours", False)):
            interruption_cost += 0.42
        if bool(user_context.get("focus_mode", False)):
            interruption_cost += 0.28
        recent_user_activity = str(user_context.get("recent_user_activity", "unknown") or "unknown").strip().lower()
        if recent_user_activity == "active":
            interruption_cost -= 0.12
        elif recent_user_activity == "idle":
            interruption_cost += 0.08
        elif recent_user_activity == "away":
            interruption_cost += 0.12
        recent_outbound_count = self._safe_int(user_context.get("recent_outbound_count"))
        unanswered_proactive_count = self._safe_int(user_context.get("unanswered_proactive_count"))
        if recent_outbound_count >= 2:
            interruption_cost += 0.12
        if unanswered_proactive_count >= 1:
            interruption_cost += 0.16
        return self._clamp_unit(interruption_cost)

    def _safe_int(self, value: object) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0

    def _clamp_unit(self, value: object) -> float:
        try:
            candidate = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, round(candidate, 2)))


class ProactiveDeliveryGuard:
    DEFAULT_RECENT_OUTBOUND_LIMIT = 2
    DEFAULT_UNANSWERED_LIMIT = 1

    def evaluate(
        self,
        *,
        event: Event,
        user_preferences: dict | None = None,
        proactive_decision: ProactiveDecisionOutput | None = None,
    ) -> ProactiveDeliveryGuardOutput | None:
        if event.source != "scheduler" or event.subsource != SCHEDULER_PROACTIVE_TICK:
            return None
        if proactive_decision is None:
            return None

        payload = event.payload if isinstance(event.payload, dict) else {}
        proactive_payload = payload.get("proactive") if isinstance(payload.get("proactive"), dict) else {}
        user_context = proactive_payload.get("user_context") if isinstance(proactive_payload.get("user_context"), dict) else {}
        preferences = user_preferences or {}

        chat_id = payload.get("chat_id")
        if not isinstance(chat_id, (int, str)):
            return ProactiveDeliveryGuardOutput(
                allowed=False,
                reason="missing_delivery_target",
            )

        opt_in = self._as_bool(preferences.get("proactive_opt_in"))
        if not opt_in:
            return ProactiveDeliveryGuardOutput(
                allowed=False,
                reason="opt_in_required",
            )

        recent_outbound_limit = self._safe_int(
            preferences.get("proactive_recent_outbound_limit"),
            default=self.DEFAULT_RECENT_OUTBOUND_LIMIT,
            minimum=1,
        )
        unanswered_limit = self._safe_int(
            preferences.get("proactive_unanswered_limit"),
            default=self.DEFAULT_UNANSWERED_LIMIT,
            minimum=1,
        )
        recent_outbound_count = self._safe_int(user_context.get("recent_outbound_count"))
        unanswered_proactive_count = self._safe_int(user_context.get("unanswered_proactive_count"))

        if recent_outbound_count >= recent_outbound_limit:
            return ProactiveDeliveryGuardOutput(
                allowed=False,
                reason="recent_outbound_limit",
                recent_outbound_count=recent_outbound_count,
                recent_outbound_limit=recent_outbound_limit,
                unanswered_proactive_count=unanswered_proactive_count,
                unanswered_proactive_limit=unanswered_limit,
            )
        if unanswered_proactive_count >= unanswered_limit:
            return ProactiveDeliveryGuardOutput(
                allowed=False,
                reason="unanswered_proactive_limit",
                recent_outbound_count=recent_outbound_count,
                recent_outbound_limit=recent_outbound_limit,
                unanswered_proactive_count=unanswered_proactive_count,
                unanswered_proactive_limit=unanswered_limit,
            )
        return ProactiveDeliveryGuardOutput(
            allowed=True,
            reason="delivery_allowed",
            recent_outbound_count=recent_outbound_count,
            recent_outbound_limit=recent_outbound_limit,
            unanswered_proactive_count=unanswered_proactive_count,
            unanswered_proactive_limit=unanswered_limit,
        )

    def _safe_int(self, value: object, *, default: int = 0, minimum: int = 0) -> int:
        try:
            return max(minimum, int(value))
        except (TypeError, ValueError):
            return max(minimum, int(default))

    def _as_bool(self, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)
