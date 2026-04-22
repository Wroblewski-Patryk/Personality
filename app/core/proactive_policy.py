from __future__ import annotations

from typing import Any

from app.core.adaptive_policy import (
    PROACTIVE_ATTENTION_RECENT_OUTBOUND_LIMIT,
    PROACTIVE_ATTENTION_UNANSWERED_LIMIT,
)
from app.proactive.engine import ProactiveDeliveryGuard


PROACTIVE_RUNTIME_POLICY_OWNER = "proactive_runtime_policy"


def proactive_runtime_policy_snapshot(
    *,
    proactive_enabled: bool,
    proactive_interval_seconds: int,
    scheduler_execution_mode: str,
    scheduler_ready: bool,
    scheduler_running: bool,
) -> dict[str, Any]:
    selected_execution_mode = (
        "externalized" if str(scheduler_execution_mode).strip().lower() == "externalized" else "in_process"
    )
    selected_cadence_owner = (
        "external_scheduler" if selected_execution_mode == "externalized" else "in_process_scheduler"
    )
    if not proactive_enabled:
        production_baseline_state = "disabled_by_policy"
        production_baseline_hint = "enable_proactive_runtime_to_allow_scheduler_owned_outreach"
        production_baseline_ready = False
    elif selected_execution_mode == "externalized":
        production_baseline_state = "external_scheduler_target_owner"
        production_baseline_hint = "external_scheduler_must_emit_scheduler_proactive_tick_events"
        production_baseline_ready = bool(scheduler_ready)
    elif scheduler_running:
        production_baseline_state = "in_process_scheduler_live"
        production_baseline_hint = "scheduler_worker_can_emit_bounded_proactive_ticks"
        production_baseline_ready = True
    else:
        production_baseline_state = "in_process_scheduler_not_running"
        production_baseline_hint = "start_scheduler_worker_or_externalize_cadence_owner"
        production_baseline_ready = False

    return {
        "policy_owner": PROACTIVE_RUNTIME_POLICY_OWNER,
        "selected_execution_mode": selected_execution_mode,
        "selected_cadence_owner": selected_cadence_owner,
        "delivery_channel_baseline": "telegram_direct_message",
        "delivery_target_baseline": "recent_telegram_chat_or_numeric_user_id_fallback",
        "candidate_selection_baseline": "opted_in_users_with_active_work_or_time_checkin",
        "anti_spam_contract": {
            "delivery_guard_recent_outbound_limit_default": ProactiveDeliveryGuard.DEFAULT_RECENT_OUTBOUND_LIMIT,
            "delivery_guard_unanswered_limit_default": ProactiveDeliveryGuard.DEFAULT_UNANSWERED_LIMIT,
            "attention_gate_recent_outbound_limit_default": PROACTIVE_ATTENTION_RECENT_OUTBOUND_LIMIT,
            "attention_gate_unanswered_limit_default": PROACTIVE_ATTENTION_UNANSWERED_LIMIT,
            "cadence_cooldown_seconds": max(1800, int(proactive_interval_seconds)),
        },
        "production_baseline_ready": production_baseline_ready,
        "production_baseline_state": production_baseline_state,
        "production_baseline_hint": production_baseline_hint,
    }
