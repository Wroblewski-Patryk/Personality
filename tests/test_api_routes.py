import asyncio
from datetime import datetime, timezone
from threading import Thread
from time import sleep

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router
from app.core.attention import AttentionTurnCoordinator
from app.core.contracts import (
    ActionResult,
    ContextOutput,
    Event,
    EventMeta,
    ExpressionOutput,
    GoalRecordOutput,
    GoalProgressRecordOutput,
    IdentityOutput,
    MemoryRecord,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
    RuntimeResult,
    RuntimeSystemDebugEventView,
    RuntimeSystemDebugMemoryBundle,
    RuntimeSystemDebugOutput,
    RuntimeSystemDebugPlanView,
    TaskRecordOutput,
)


class FakeRuntime:
    def __init__(
        self,
        *,
        reflection_triggered: bool = False,
        run_delay_seconds: float = 0.0,
        action_status: str = "success",
        action_actions: list[str] | None = None,
        action_notes: str | None = None,
    ):
        self.last_event: Event | None = None
        self.events: list[Event] = []
        self.reflection_triggered = reflection_triggered
        self.run_delay_seconds = max(0.0, float(run_delay_seconds))
        self.action_status = action_status
        self.action_actions = list(action_actions) if action_actions is not None else None
        self.action_notes = action_notes

    async def run(self, event: Event) -> RuntimeResult:
        if self.run_delay_seconds > 0:
            await asyncio.sleep(self.run_delay_seconds)
        self.last_event = event
        self.events.append(event)
        timestamp = datetime.now(timezone.utc)
        action_actions = self.action_actions
        if action_actions is None:
            action_actions = ["api_response"] if self.action_status == "success" else ["send_telegram_message"]
        action_notes = self.action_notes
        if action_notes is None:
            action_notes = "Response returned via API." if self.action_status == "success" else "Runtime action failed."
        action_result = ActionResult(
            status=self.action_status,
            actions=action_actions,
            notes=action_notes,
        )
        return RuntimeResult(
            event=event,
            identity=IdentityOutput(
                mission="Help the user move forward with clear, constructive support.",
                values=["clarity", "continuity", "constructiveness"],
                behavioral_style=["direct", "supportive", "analytical"],
                boundaries=["do_not_fake_capabilities"],
                preferred_language="en",
                response_style=None,
                collaboration_preference=None,
                theta_orientation=None,
                summary="Mission: help the user move forward with clear, constructive support. Core style: direct, supportive, analytical. Preferred language context: en.",
            ),
            active_goals=[
                GoalRecordOutput(
                    id=1,
                    name="ship the MVP",
                    description="User-declared goal: ship the MVP",
                    priority="high",
                    status="active",
                    goal_type="tactical",
                )
            ],
            active_tasks=[
                TaskRecordOutput(
                    id=2,
                    goal_id=1,
                    name="fix deployment blocker",
                    description="User-declared task: fix deployment blocker",
                    priority="high",
                    status="blocked",
                )
            ],
            goal_progress_history=[
                GoalProgressRecordOutput(
                    id=1,
                    goal_id=1,
                    score=0.42,
                    execution_state="recovering",
                    progress_trend="improving",
                    source_event_id=event.event_id,
                    created_at=timestamp,
                )
            ],
            perception=PerceptionOutput(
                event_type="statement",
                topic="general",
                topic_tags=["general"],
                intent="share_information",
                language="en",
                language_source="keyword_signal",
                language_confidence=0.8,
                ambiguity=0.1,
                initial_salience=0.5,
            ),
            context=ContextOutput(
                summary="context-summary",
                related_goals=[],
                related_tags=["general"],
                risk_level=0.1,
            ),
            motivation=MotivationOutput(
                importance=0.7,
                urgency=0.4,
                valence=0.1,
                arousal=0.5,
                mode="respond",
            ),
            role=RoleOutput(selected="advisor", confidence=0.6),
            plan=PlanOutput(
                goal="Provide a response.",
                steps=["reply"],
                needs_action=False,
                needs_response=True,
            ),
            action_result=action_result,
            expression=ExpressionOutput(
                message="Test reply",
                tone="supportive",
                channel="api",
                language="en",
            ),
            memory_record=MemoryRecord(
                id=1,
                event_id=event.event_id,
                timestamp=timestamp,
                summary="stored-summary",
                importance=0.7,
            ),
            reflection_triggered=self.reflection_triggered,
            system_debug=RuntimeSystemDebugOutput(
                event=RuntimeSystemDebugEventView(
                    event_id=event.event_id,
                    trace_id=event.meta.trace_id,
                    source=event.source,
                    subsource=event.subsource,
                    timestamp=event.timestamp,
                    user_id=event.meta.user_id,
                    payload=dict(event.payload),
                ),
                perception=PerceptionOutput(
                    event_type="statement",
                    topic="general",
                    topic_tags=["general"],
                    intent="share_information",
                    language="en",
                    language_source="keyword_signal",
                    language_confidence=0.8,
                    ambiguity=0.1,
                    initial_salience=0.5,
                ),
                memory_bundle=RuntimeSystemDebugMemoryBundle(
                    episodic=[{"summary": "stored-summary", "importance": 0.7}],
                    semantic=[{"kind": "response_style", "content": "concise"}],
                    affective=[{"kind": "affective_support_pattern", "content": "supportive"}],
                    relations=[{"relation_type": "collaboration_dynamic", "relation_value": "guided", "confidence": 0.8}],
                    diagnostics={"episodic_lexical_hits": 1, "vector_hits": 0},
                ),
                context=ContextOutput(
                    summary="context-summary",
                    related_goals=[],
                    related_tags=["general"],
                    risk_level=0.1,
                ),
                motivation=MotivationOutput(
                    importance=0.7,
                    urgency=0.4,
                    valence=0.1,
                    arousal=0.5,
                    mode="respond",
                ),
                role=RoleOutput(selected="advisor", confidence=0.6),
                plan=RuntimeSystemDebugPlanView(
                    goal="Provide a response.",
                    steps=["reply"],
                    needs_action=False,
                    needs_response=True,
                    domain_intents=[],
                ),
                expression=ExpressionOutput(
                    message="Test reply",
                    tone="supportive",
                    channel="api",
                    language="en",
                ),
                action_result=action_result,
            ),
            stage_timings_ms={
                "memory_load": 1,
                "task_load": 0,
                "goal_milestone_load": 0,
                "goal_milestone_history_load": 0,
                "goal_progress_load": 0,
                "identity_load": 0,
                "perception": 0,
                "affective_assessment": 0,
                "context": 0,
                "motivation": 0,
                "role": 0,
                "planning": 0,
                "expression": 2,
                "action": 0,
                "memory_persist": 1,
                "reflection_enqueue": 0,
                "state_refresh": 1,
                "total": 12,
            },
            duration_ms=12,
        )


class FakeTelegramClient:
    def __init__(self):
        self.calls: list[dict[str, str | None]] = []

    async def set_webhook(self, webhook_url: str, secret_token: str | None) -> dict:
        self.calls.append({"webhook_url": webhook_url, "secret_token": secret_token})
        return {"ok": True, "result": True}


class FakeSettings:
    def __init__(
        self,
        telegram_webhook_secret: str | None = None,
        *,
        app_env: str = "development",
        event_debug_enabled: bool | None = True,
        event_debug_token: str | None = None,
        production_debug_token_required: bool = True,
        event_debug_query_compat_enabled: bool | None = None,
        event_debug_shared_ingress_mode: str = "compatibility",
        event_debug_query_compat_recent_window: int = 20,
        event_debug_query_compat_stale_after_seconds: int = 86400,
        semantic_vector_enabled: bool = True,
        embedding_provider: str = "deterministic",
        embedding_model: str = "deterministic-v1",
        embedding_dimensions: int = 32,
        embedding_source_kinds: str = "episodic,semantic,affective",
        embedding_refresh_mode: str = "on_write",
        embedding_refresh_interval_seconds: int = 21600,
        embedding_provider_ownership_enforcement: str = "warn",
        embedding_model_governance_enforcement: str = "warn",
        embedding_source_rollout_enforcement: str = "warn",
        startup_schema_mode: str = "migrate",
        production_policy_enforcement: str = "warn",
        reflection_runtime_mode: str = "in_process",
        scheduler_execution_mode: str = "in_process",
        scheduler_enabled: bool = False,
        reflection_interval: int = 900,
        maintenance_interval: int = 3600,
        proactive_enabled: bool = False,
        attention_coordination_mode: str = "in_process",
    ):
        self.telegram_webhook_secret = telegram_webhook_secret
        self.app_env = app_env
        self.event_debug_enabled = event_debug_enabled
        self.event_debug_token = event_debug_token
        self.production_debug_token_required = production_debug_token_required
        self.event_debug_query_compat_enabled = event_debug_query_compat_enabled
        self.event_debug_shared_ingress_mode = event_debug_shared_ingress_mode
        self.event_debug_query_compat_recent_window = event_debug_query_compat_recent_window
        self.event_debug_query_compat_stale_after_seconds = event_debug_query_compat_stale_after_seconds
        self.semantic_vector_enabled = semantic_vector_enabled
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.embedding_source_kinds = embedding_source_kinds
        self.embedding_refresh_mode = embedding_refresh_mode
        self.embedding_refresh_interval_seconds = embedding_refresh_interval_seconds
        self.embedding_provider_ownership_enforcement = embedding_provider_ownership_enforcement
        self.embedding_model_governance_enforcement = embedding_model_governance_enforcement
        self.embedding_source_rollout_enforcement = embedding_source_rollout_enforcement
        self.startup_schema_mode = startup_schema_mode
        self.production_policy_enforcement = production_policy_enforcement
        self.reflection_runtime_mode = reflection_runtime_mode
        self.scheduler_execution_mode = scheduler_execution_mode
        self.scheduler_enabled = scheduler_enabled
        self.reflection_interval = reflection_interval
        self.maintenance_interval = maintenance_interval
        self.proactive_enabled = proactive_enabled
        self.attention_coordination_mode = attention_coordination_mode

    def is_event_debug_enabled(self) -> bool:
        if self.event_debug_enabled is not None:
            return self.event_debug_enabled
        return True

    def is_event_debug_query_compat_enabled(self) -> bool:
        if self.event_debug_query_compat_enabled is not None:
            return self.event_debug_query_compat_enabled
        return self.app_env != "production"


class FakeMemoryRepository:
    def __init__(self, stats: dict[str, int] | None = None):
        self.stats = stats or {
            "total": 4,
            "pending": 1,
            "processing": 1,
            "completed": 1,
            "failed": 1,
            "retryable_failed": 1,
            "exhausted_failed": 0,
            "stuck_processing": 0,
        }

    async def get_reflection_task_stats(
        self,
        *,
        max_attempts: int,
        stuck_after_seconds: int,
        retry_backoff_seconds: tuple[int, ...],
        now=None,
    ) -> dict[str, int]:
        assert max_attempts == 3
        assert stuck_after_seconds == 180
        assert retry_backoff_seconds == (5, 30, 120)
        return self.stats


class FakeReflectionWorker:
    def __init__(self, *, running: bool = True):
        self.running = running

    def snapshot(self) -> dict:
        return {
            "running": self.running,
            "queue_size": 1,
            "queue_capacity": 99,
            "queued_task_count": 1,
            "queued_task_ids": [42],
            "max_attempts": 3,
            "retry_backoff_seconds": [5, 30, 120],
            "stuck_processing_seconds": 180,
        }


class FakeSchedulerWorker:
    def __init__(
        self,
        *,
        enabled: bool = False,
        running: bool = False,
        execution_mode: str = "in_process",
        configured_enabled: bool | None = None,
        proactive_enabled: bool = False,
        reflection_runtime_mode: str = "in_process",
        reflection_interval_seconds: int = 900,
        maintenance_interval_seconds: int = 3600,
    ):
        self.enabled = enabled
        self.running = running
        self.execution_mode = execution_mode
        self.configured_enabled = enabled if configured_enabled is None else configured_enabled
        self.proactive_enabled = proactive_enabled
        self.reflection_runtime_mode = reflection_runtime_mode
        self.reflection_interval_seconds = reflection_interval_seconds
        self.maintenance_interval_seconds = maintenance_interval_seconds

    def snapshot(self) -> dict:
        cadence_execution = {
            "baseline_execution_mode": "in_process",
            "selected_execution_mode": self.execution_mode,
            "ready": not (
                (self.execution_mode == "in_process" and self.enabled and not self.running)
                or (self.execution_mode == "externalized" and self.running)
            ),
            "blocking_signals": (
                ["in_process_scheduler_not_running"]
                if self.execution_mode == "in_process" and self.enabled and not self.running
                else (
                    ["externalized_scheduler_worker_running"]
                    if self.execution_mode == "externalized" and self.running
                    else []
                )
            ),
            "maintenance_cadence_owner": (
                "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler"
            ),
            "proactive_cadence_owner": (
                "external_scheduler" if self.execution_mode == "externalized" else "in_process_scheduler"
            ),
            "maintenance_tick_dispatch": self.execution_mode == "in_process",
            "maintenance_tick_reason": (
                "in_process_owner_mode" if self.execution_mode == "in_process" else "externalized_owner_mode"
            ),
            "proactive_tick_dispatch": self.execution_mode == "in_process" and self.proactive_enabled,
            "proactive_tick_reason": (
                "in_process_owner_mode"
                if self.execution_mode == "in_process" and self.proactive_enabled
                else (
                    "proactive_disabled"
                    if self.execution_mode == "in_process"
                    else "externalized_owner_mode"
                )
            ),
            "scheduler_enabled": self.enabled,
            "scheduler_running": self.running,
            "proactive_enabled": self.proactive_enabled,
        }
        return {
            "execution_mode": self.execution_mode,
            "configured_enabled": self.configured_enabled,
            "enabled": self.enabled,
            "running": self.running,
            "proactive_enabled": self.proactive_enabled,
            "maintenance_cadence_owner": cadence_execution["maintenance_cadence_owner"],
            "proactive_cadence_owner": cadence_execution["proactive_cadence_owner"],
            "cadence_execution": cadence_execution,
            "reflection_runtime_mode": self.reflection_runtime_mode,
            "reflection_interval_seconds": self.reflection_interval_seconds,
            "maintenance_interval_seconds": self.maintenance_interval_seconds,
            "reflection_batch_limit": 10,
            "next_reflection_due_at": None,
            "next_maintenance_due_at": None,
            "last_reflection_tick_at": None,
            "last_maintenance_tick_at": None,
            "last_reflection_summary": {},
            "last_maintenance_summary": {},
        }


def _client(
    secret: str | None = None,
    *,
    app_env: str = "development",
    reflection_triggered: bool = False,
    run_delay_seconds: float = 0.0,
    runtime_action_status: str = "success",
    runtime_action_actions: list[str] | None = None,
    runtime_action_notes: str | None = None,
    reflection_stats: dict[str, int] | None = None,
    reflection_running: bool = True,
    event_debug_enabled: bool | None = True,
    event_debug_token: str | None = None,
    production_debug_token_required: bool = True,
    event_debug_query_compat_enabled: bool | None = None,
    event_debug_shared_ingress_mode: str = "compatibility",
    event_debug_query_compat_recent_window: int = 20,
    event_debug_query_compat_stale_after_seconds: int = 86400,
    semantic_vector_enabled: bool = True,
    embedding_provider: str = "deterministic",
    embedding_model: str = "deterministic-v1",
    embedding_dimensions: int = 32,
    embedding_source_kinds: str = "episodic,semantic,affective",
    embedding_refresh_mode: str = "on_write",
    embedding_refresh_interval_seconds: int = 21600,
    embedding_provider_ownership_enforcement: str = "warn",
    embedding_model_governance_enforcement: str = "warn",
    embedding_source_rollout_enforcement: str = "warn",
    startup_schema_mode: str = "migrate",
    production_policy_enforcement: str = "warn",
    reflection_runtime_mode: str = "in_process",
    scheduler_execution_mode: str = "in_process",
    scheduler_enabled: bool = False,
    scheduler_running: bool = False,
    reflection_interval: int = 900,
    maintenance_interval: int = 3600,
    proactive_enabled: bool = False,
    attention_burst_window_ms: int = 120,
    attention_coordination_mode: str = "in_process",
) -> tuple[TestClient, FakeRuntime, FakeTelegramClient]:
    app = FastAPI()
    app.include_router(router)
    runtime = FakeRuntime(
        reflection_triggered=reflection_triggered,
        run_delay_seconds=run_delay_seconds,
        action_status=runtime_action_status,
        action_actions=runtime_action_actions,
        action_notes=runtime_action_notes,
    )
    telegram_client = FakeTelegramClient()
    memory_repository = FakeMemoryRepository(stats=reflection_stats)
    reflection_worker = FakeReflectionWorker(running=reflection_running)
    scheduler_worker = FakeSchedulerWorker(
        enabled=scheduler_enabled,
        running=scheduler_running,
        execution_mode=scheduler_execution_mode,
        configured_enabled=scheduler_enabled,
        proactive_enabled=proactive_enabled,
        reflection_runtime_mode=reflection_runtime_mode,
        reflection_interval_seconds=reflection_interval,
        maintenance_interval_seconds=maintenance_interval,
    )
    app.state.runtime = runtime
    app.state.telegram_client = telegram_client
    app.state.settings = FakeSettings(
        telegram_webhook_secret=secret,
        app_env=app_env,
        event_debug_enabled=event_debug_enabled,
        event_debug_token=event_debug_token,
        production_debug_token_required=production_debug_token_required,
        event_debug_query_compat_enabled=event_debug_query_compat_enabled,
        event_debug_shared_ingress_mode=event_debug_shared_ingress_mode,
        event_debug_query_compat_recent_window=event_debug_query_compat_recent_window,
        event_debug_query_compat_stale_after_seconds=event_debug_query_compat_stale_after_seconds,
        semantic_vector_enabled=semantic_vector_enabled,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        embedding_dimensions=embedding_dimensions,
        embedding_source_kinds=embedding_source_kinds,
        embedding_refresh_mode=embedding_refresh_mode,
        embedding_refresh_interval_seconds=embedding_refresh_interval_seconds,
        embedding_provider_ownership_enforcement=embedding_provider_ownership_enforcement,
        embedding_model_governance_enforcement=embedding_model_governance_enforcement,
        embedding_source_rollout_enforcement=embedding_source_rollout_enforcement,
        startup_schema_mode=startup_schema_mode,
        production_policy_enforcement=production_policy_enforcement,
        reflection_runtime_mode=reflection_runtime_mode,
        scheduler_execution_mode=scheduler_execution_mode,
        scheduler_enabled=scheduler_enabled,
        reflection_interval=reflection_interval,
        maintenance_interval=maintenance_interval,
        proactive_enabled=proactive_enabled,
        attention_coordination_mode=attention_coordination_mode,
    )
    app.state.memory_repository = memory_repository
    app.state.reflection_worker = reflection_worker
    app.state.scheduler_worker = scheduler_worker
    app.state.attention_turn_coordinator = AttentionTurnCoordinator(
        burst_window_ms=attention_burst_window_ms,
        answered_ttl_seconds=0.5,
        stale_turn_seconds=3.0,
        coordination_mode=attention_coordination_mode,
    )
    return TestClient(app), runtime, telegram_client


def _telegram_update(update_id: int, text: str, *, chat_id: int = 123, user_id: int = 999) -> dict:
    return {
        "update_id": update_id,
        "message": {
            "text": text,
            "chat": {"id": chat_id},
            "from": {"id": user_id},
        },
    }


def test_health_endpoint_returns_ok() -> None:
    client, _, _ = _client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "runtime_policy": {
            "startup_schema_mode": "migrate",
            "event_debug_enabled": True,
            "event_debug_token_required": False,
            "production_debug_token_required": True,
            "event_debug_query_compat_enabled": True,
            "event_debug_query_compat_source": "environment_default",
            "event_debug_ingress_owner": "internal_route_primary_shared_route_compat",
            "event_debug_internal_ingress_path": "/internal/event/debug",
            "event_debug_shared_ingress_path": "/event/debug",
            "event_debug_shared_ingress_mode": "compatibility",
            "event_debug_shared_ingress_break_glass_required": False,
            "event_debug_shared_ingress_posture": "transitional_compatibility",
            "debug_access_posture": "open_no_token",
            "debug_token_policy_hint": "debug_access_open_without_token",
            "event_debug_source": "explicit",
            "production_policy_enforcement": "warn",
            "recommended_production_policy_enforcement": "warn",
            "production_policy_mismatches": [],
            "production_policy_mismatch_count": 0,
            "strict_startup_blocked": False,
            "strict_rollout_ready": True,
            "strict_rollout_hint": "not_applicable_non_production",
            "event_debug_query_compat_allow_rate": 0.0,
            "event_debug_query_compat_block_rate": 0.0,
            "event_debug_query_compat_recommendation": "no_compat_traffic_detected_disable_when_possible",
            "event_debug_query_compat_sunset_ready": True,
            "event_debug_query_compat_sunset_reason": "no_compat_attempts_detected",
            "event_debug_query_compat_recent_attempts_total": 0,
            "event_debug_query_compat_recent_allow_rate": 0.0,
            "event_debug_query_compat_recent_block_rate": 0.0,
            "event_debug_query_compat_recent_state": "no_recent_attempts",
            "event_debug_query_compat_stale_after_seconds": 86400,
            "event_debug_query_compat_last_attempt_age_seconds": None,
            "event_debug_query_compat_last_attempt_state": "no_attempts_recorded",
            "event_debug_query_compat_activity_state": "no_attempts_observed",
            "event_debug_query_compat_activity_hint": "can_disable_when_ready",
            "event_debug_query_compat_telemetry": {
                "attempts_total": 0,
                "allowed_total": 0,
                "blocked_total": 0,
                "last_attempt_at": None,
                "last_allowed_at": None,
                "last_blocked_at": None,
                "recent_window_size": 20,
                "recent_attempts_total": 0,
                "recent_allowed_total": 0,
                "recent_blocked_total": 0,
            },
        },
        "release_readiness": {
            "ready": True,
            "violations": [],
        },
        "memory_retrieval": {
            "semantic_vector_enabled": True,
            "semantic_retrieval_mode": "hybrid_vector_lexical",
            "semantic_embedding_provider_ready": True,
            "semantic_embedding_posture": "ready",
            "semantic_embedding_provider_requested": "deterministic",
            "semantic_embedding_provider_effective": "deterministic",
            "semantic_embedding_provider_hint": "deterministic_baseline",
            "semantic_embedding_provider_ownership_state": "deterministic_baseline_owner",
            "semantic_embedding_provider_ownership_hint": "deterministic_provider_owns_embedding_execution",
            "semantic_embedding_provider_ownership_enforcement": "warn",
            "semantic_embedding_provider_ownership_enforcement_state": "not_applicable_no_fallback",
            "semantic_embedding_provider_ownership_enforcement_hint": "no_provider_ownership_violation",
            "semantic_embedding_owner_strategy_state": "deterministic_on_write_owner",
            "semantic_embedding_owner_strategy_hint": "deterministic_baseline_owner_active",
            "semantic_embedding_owner_strategy_recommendation": "deterministic_on_write_baseline_is_active",
            "semantic_embedding_model_requested": "deterministic-v1",
            "semantic_embedding_model_effective": "deterministic-v1",
            "semantic_embedding_model_governance_state": "model_contract_aligned",
            "semantic_embedding_model_governance_hint": "embedding_model_contract_aligned_with_provider",
            "semantic_embedding_model_governance_enforcement": "warn",
            "semantic_embedding_model_governance_enforcement_state": "not_applicable_aligned",
            "semantic_embedding_model_governance_enforcement_hint": "no_model_governance_violation",
            "semantic_embedding_strict_rollout_violations": [],
            "semantic_embedding_strict_rollout_violation_count": 0,
            "semantic_embedding_strict_rollout_ready": True,
            "semantic_embedding_strict_rollout_state": "ready",
            "semantic_embedding_strict_rollout_hint": "can_enable_strict_provider_and_model_enforcement",
            "semantic_embedding_strict_rollout_recommendation": "enable_strict_provider_and_model_enforcement",
            "semantic_embedding_recommended_provider_ownership_enforcement": "strict",
            "semantic_embedding_recommended_model_governance_enforcement": "strict",
            "semantic_embedding_provider_ownership_enforcement_alignment": "below_recommendation",
            "semantic_embedding_model_governance_enforcement_alignment": "below_recommendation",
            "semantic_embedding_enforcement_alignment_state": "below_recommendation",
            "semantic_embedding_enforcement_alignment_hint": "consider_enabling_strict_for_provider_and_model",
            "semantic_embedding_dimensions": 32,
            "semantic_embedding_warning_state": "no_warning",
            "semantic_embedding_warning_hint": "embedding_strategy_ready",
            "semantic_embedding_source_kinds": ["episodic", "semantic", "affective"],
            "semantic_embedding_source_coverage_state": "full_for_current_retrieval_path",
            "semantic_embedding_source_coverage_hint": "semantic_and_affective_sources_enabled",
            "semantic_embedding_source_rollout_state": "semantic_affective_baseline",
            "semantic_embedding_source_rollout_hint": "high_signal_sources_active",
            "semantic_embedding_source_rollout_recommendation": "add_relation_source_after_baseline_stabilizes",
            "semantic_embedding_source_rollout_order": ["semantic", "affective", "relation"],
            "semantic_embedding_source_rollout_enabled_sources": ["semantic", "affective"],
            "semantic_embedding_source_rollout_missing_sources": ["relation"],
            "semantic_embedding_source_rollout_next_source_kind": "relation",
            "semantic_embedding_source_rollout_completion_state": "baseline_complete_relation_pending",
            "semantic_embedding_source_rollout_phase_index": 2,
            "semantic_embedding_source_rollout_phase_total": 3,
            "semantic_embedding_source_rollout_progress_percent": 67,
            "semantic_embedding_source_rollout_enforcement": "warn",
            "semantic_embedding_source_rollout_enforcement_state": "warning_only",
            "semantic_embedding_source_rollout_enforcement_hint": "pending_source_rollout_allowed_in_warn_mode",
            "semantic_embedding_recommended_source_rollout_enforcement": "warn",
            "semantic_embedding_source_rollout_enforcement_alignment": "aligned",
            "semantic_embedding_source_rollout_enforcement_alignment_state": "aligned_with_recommendation",
            "semantic_embedding_source_rollout_enforcement_alignment_hint": "source_rollout_enforcement_matches_recommendation",
            "semantic_embedding_refresh_mode": "on_write",
            "semantic_embedding_refresh_interval_seconds": 21600,
            "semantic_embedding_refresh_state": "on_write_refresh_active",
            "semantic_embedding_refresh_hint": "refresh_on_write_enabled",
            "semantic_embedding_refresh_cadence_state": "on_write_continuous",
            "semantic_embedding_refresh_cadence_hint": "on_write_refresh_has_no_manual_gap",
            "semantic_embedding_recommended_refresh_mode": "on_write",
            "semantic_embedding_refresh_alignment_state": "aligned",
            "semantic_embedding_refresh_alignment_hint": "refresh_mode_matches_active_rollout_recommendation",
        },
        "scheduler": {
            "healthy": True,
            "execution_mode": "in_process",
            "configured_enabled": False,
            "enabled": False,
            "running": False,
            "proactive_enabled": False,
            "maintenance_cadence_owner": "in_process_scheduler",
            "proactive_cadence_owner": "in_process_scheduler",
            "cadence_execution": {
                "baseline_execution_mode": "in_process",
                "selected_execution_mode": "in_process",
                "ready": True,
                "blocking_signals": [],
                "maintenance_cadence_owner": "in_process_scheduler",
                "proactive_cadence_owner": "in_process_scheduler",
                "maintenance_tick_dispatch": True,
                "maintenance_tick_reason": "in_process_owner_mode",
                "proactive_tick_dispatch": False,
                "proactive_tick_reason": "proactive_disabled",
                "scheduler_enabled": False,
                "scheduler_running": False,
                "proactive_enabled": False,
            },
            "reflection_runtime_mode": "in_process",
            "reflection_interval_seconds": 900,
            "maintenance_interval_seconds": 3600,
            "reflection_batch_limit": 10,
            "next_reflection_due_at": None,
            "next_maintenance_due_at": None,
            "last_reflection_tick_at": None,
            "last_maintenance_tick_at": None,
            "last_reflection_summary": {},
            "last_maintenance_summary": {},
        },
        "attention": {
            "healthy": True,
            "coordination_mode": "in_process",
            "turn_state_owner": "in_process_coordinator",
            "durable_inbox_expected": False,
            "deployment_readiness": {
                "baseline_coordination_mode": "in_process",
                "selected_coordination_mode": "in_process",
                "ready": True,
                "blocking_signals": [],
                "turn_state_owner": "in_process_coordinator",
                "durable_inbox_expected": False,
            },
            "burst_window_ms": 120,
            "answered_ttl_seconds": 0.5,
            "stale_turn_seconds": 3.0,
            "pending": 0,
            "claimed": 0,
            "answered": 0,
        },
        "reflection": {
            "healthy": True,
            "runtime_mode": "in_process",
            "deployment_readiness": {
                "baseline_runtime_mode": "in_process",
                "selected_runtime_mode": "in_process",
                "ready": True,
                "blocking_signals": [],
            },
            "topology": {
                "runtime_mode": "in_process",
                "enqueue_owner": "runtime_followup",
                "queue_backend": "durable_postgres_queue",
                "queue_drain_owner": "in_process_worker",
                "retry_owner": "durable_queue",
                "external_driver_expected": False,
                "worker_running": True,
                "runtime_enqueue_dispatch": True,
                "runtime_enqueue_reason": "in_process_worker_running",
                "scheduler_tick_dispatch": False,
                "scheduler_tick_reason": "in_process_worker_running",
                "max_attempts": 3,
                "retry_backoff_seconds": [5, 30, 120],
                "stuck_processing_seconds": 180,
            },
            "worker": {
                "running": True,
                "queue_size": 1,
                "queue_capacity": 99,
                "queued_task_count": 1,
                "queued_task_ids": [42],
                "max_attempts": 3,
                "retry_backoff_seconds": [5, 30, 120],
                "stuck_processing_seconds": 180,
            },
            "tasks": {
                "total": 4,
                "pending": 1,
                "processing": 1,
                "completed": 1,
                "failed": 1,
                "retryable_failed": 1,
                "exhausted_failed": 0,
                "stuck_processing": 0,
            },
        },
    }


def test_health_endpoint_allows_deferred_reflection_mode_without_running_worker() -> None:
    client, _, _ = _client(
        reflection_running=False,
        reflection_runtime_mode="deferred",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["reflection"]["runtime_mode"] == "deferred"
    assert body["reflection"]["deployment_readiness"] == {
        "baseline_runtime_mode": "in_process",
        "selected_runtime_mode": "deferred",
        "ready": True,
        "blocking_signals": [],
    }
    assert body["reflection"]["topology"]["queue_drain_owner"] == "external_driver"
    assert body["reflection"]["topology"]["external_driver_expected"] is True
    assert body["reflection"]["topology"]["runtime_enqueue_dispatch"] is False
    assert body["reflection"]["topology"]["scheduler_tick_dispatch"] is True
    assert body["reflection"]["worker"]["running"] is False
    assert body["reflection"]["healthy"] is True


def test_health_endpoint_exposes_in_process_handoff_posture_when_worker_is_stopped() -> None:
    client, _, _ = _client(
        reflection_running=False,
        reflection_runtime_mode="in_process",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["reflection"]["runtime_mode"] == "in_process"
    assert body["reflection"]["deployment_readiness"]["ready"] is False
    assert "in_process_worker_not_running" in body["reflection"]["deployment_readiness"]["blocking_signals"]
    assert body["reflection"]["topology"]["queue_drain_owner"] == "in_process_worker"
    assert body["reflection"]["topology"]["external_driver_expected"] is False
    assert body["reflection"]["topology"]["runtime_enqueue_dispatch"] is False
    assert body["reflection"]["topology"]["runtime_enqueue_reason"] == "in_process_worker_not_running"
    assert body["reflection"]["topology"]["scheduler_tick_dispatch"] is True
    assert body["reflection"]["topology"]["scheduler_tick_reason"] == "in_process_worker_not_running"
    assert body["reflection"]["worker"]["running"] is False
    assert body["reflection"]["healthy"] is False


def test_health_endpoint_exposes_lexical_only_memory_retrieval_mode_when_semantic_vectors_are_disabled() -> None:
    client, _, _ = _client(semantic_vector_enabled=False)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"] == {
        "semantic_vector_enabled": False,
        "semantic_retrieval_mode": "lexical_only",
        "semantic_embedding_provider_ready": True,
        "semantic_embedding_posture": "ready",
        "semantic_embedding_provider_requested": "deterministic",
        "semantic_embedding_provider_effective": "deterministic",
        "semantic_embedding_provider_hint": "deterministic_baseline",
        "semantic_embedding_provider_ownership_state": "vectors_disabled",
        "semantic_embedding_provider_ownership_hint": "not_applicable_vectors_disabled",
        "semantic_embedding_provider_ownership_enforcement": "warn",
        "semantic_embedding_provider_ownership_enforcement_state": "not_applicable_vectors_disabled",
        "semantic_embedding_provider_ownership_enforcement_hint": "not_applicable_vectors_disabled",
        "semantic_embedding_owner_strategy_state": "vectors_disabled",
        "semantic_embedding_owner_strategy_hint": "enable_vectors_before_owner_strategy_rollout",
        "semantic_embedding_owner_strategy_recommendation": "defer_owner_strategy_selection_until_vectors_enabled",
        "semantic_embedding_model_requested": "deterministic-v1",
        "semantic_embedding_model_effective": "deterministic-v1",
        "semantic_embedding_model_governance_state": "vectors_disabled",
        "semantic_embedding_model_governance_hint": "not_applicable_vectors_disabled",
        "semantic_embedding_model_governance_enforcement": "warn",
        "semantic_embedding_model_governance_enforcement_state": "not_applicable_vectors_disabled",
        "semantic_embedding_model_governance_enforcement_hint": "not_applicable_vectors_disabled",
        "semantic_embedding_strict_rollout_violations": [],
        "semantic_embedding_strict_rollout_violation_count": 0,
        "semantic_embedding_strict_rollout_ready": False,
        "semantic_embedding_strict_rollout_state": "not_applicable_vectors_disabled",
        "semantic_embedding_strict_rollout_hint": "enable_vectors_before_strict_enforcement_rollout",
        "semantic_embedding_strict_rollout_recommendation": "defer_strict_enforcement_until_vectors_enabled",
        "semantic_embedding_recommended_provider_ownership_enforcement": "warn",
        "semantic_embedding_recommended_model_governance_enforcement": "warn",
        "semantic_embedding_provider_ownership_enforcement_alignment": "not_applicable_vectors_disabled",
        "semantic_embedding_model_governance_enforcement_alignment": "not_applicable_vectors_disabled",
        "semantic_embedding_enforcement_alignment_state": "not_applicable_vectors_disabled",
        "semantic_embedding_enforcement_alignment_hint": "enable_vectors_before_enforcement_alignment",
        "semantic_embedding_dimensions": 32,
        "semantic_embedding_warning_state": "vectors_disabled",
        "semantic_embedding_warning_hint": "enable_semantic_vectors_to_activate_embedding_strategy",
        "semantic_embedding_source_kinds": ["episodic", "semantic", "affective"],
        "semantic_embedding_source_coverage_state": "vectors_disabled",
        "semantic_embedding_source_coverage_hint": "not_applicable_vectors_disabled",
        "semantic_embedding_source_rollout_state": "vectors_disabled",
        "semantic_embedding_source_rollout_hint": "enable_vectors_before_source_rollout",
        "semantic_embedding_source_rollout_recommendation": "defer_source_rollout_until_vectors_enabled",
        "semantic_embedding_source_rollout_order": ["semantic", "affective", "relation"],
        "semantic_embedding_source_rollout_enabled_sources": ["semantic", "affective"],
        "semantic_embedding_source_rollout_missing_sources": ["relation"],
        "semantic_embedding_source_rollout_next_source_kind": "none",
        "semantic_embedding_source_rollout_completion_state": "vectors_disabled",
        "semantic_embedding_source_rollout_phase_index": 2,
        "semantic_embedding_source_rollout_phase_total": 3,
        "semantic_embedding_source_rollout_progress_percent": 67,
        "semantic_embedding_source_rollout_enforcement": "warn",
        "semantic_embedding_source_rollout_enforcement_state": "not_applicable_vectors_disabled",
        "semantic_embedding_source_rollout_enforcement_hint": "not_applicable_vectors_disabled",
        "semantic_embedding_recommended_source_rollout_enforcement": "warn",
        "semantic_embedding_source_rollout_enforcement_alignment": "not_applicable_vectors_disabled",
        "semantic_embedding_source_rollout_enforcement_alignment_state": "not_applicable_vectors_disabled",
        "semantic_embedding_source_rollout_enforcement_alignment_hint": "enable_vectors_before_source_rollout_enforcement_alignment",
        "semantic_embedding_refresh_mode": "on_write",
        "semantic_embedding_refresh_interval_seconds": 21600,
        "semantic_embedding_refresh_state": "vectors_disabled",
        "semantic_embedding_refresh_hint": "not_applicable_vectors_disabled",
        "semantic_embedding_refresh_cadence_state": "vectors_disabled",
        "semantic_embedding_refresh_cadence_hint": "not_applicable_vectors_disabled",
        "semantic_embedding_recommended_refresh_mode": "on_write",
        "semantic_embedding_refresh_alignment_state": "not_applicable_vectors_disabled",
        "semantic_embedding_refresh_alignment_hint": "enable_vectors_before_refresh_alignment",
    }


def test_health_endpoint_exposes_embedding_provider_fallback_posture_when_non_deterministic_provider_is_requested() -> None:
    client, _, _ = _client(
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=1536,
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"] == {
        "semantic_vector_enabled": True,
        "semantic_retrieval_mode": "hybrid_vector_lexical",
        "semantic_embedding_provider_ready": False,
        "semantic_embedding_posture": "fallback_deterministic",
        "semantic_embedding_provider_requested": "openai",
        "semantic_embedding_provider_effective": "deterministic",
        "semantic_embedding_provider_hint": "provider_not_implemented_fallback_deterministic",
        "semantic_embedding_provider_ownership_state": "provider_fallback_active",
        "semantic_embedding_provider_ownership_hint": "requested_provider_not_effective_owner",
        "semantic_embedding_provider_ownership_enforcement": "warn",
        "semantic_embedding_provider_ownership_enforcement_state": "warning_only",
        "semantic_embedding_provider_ownership_enforcement_hint": "fallback_allowed_in_warn_mode",
        "semantic_embedding_owner_strategy_state": "fallback_owner_active",
        "semantic_embedding_owner_strategy_hint": "requested_provider_not_effective_owner",
        "semantic_embedding_owner_strategy_recommendation": "keep_deterministic_owner_until_provider_execution_is_available",
        "semantic_embedding_model_requested": "text-embedding-3-small",
        "semantic_embedding_model_effective": "deterministic-v1",
        "semantic_embedding_model_governance_state": "provider_fallback_effective_model",
        "semantic_embedding_model_governance_hint": "effective_model_controlled_by_fallback_provider",
        "semantic_embedding_model_governance_enforcement": "warn",
        "semantic_embedding_model_governance_enforcement_state": "not_applicable_aligned",
        "semantic_embedding_model_governance_enforcement_hint": "no_model_governance_violation",
        "semantic_embedding_strict_rollout_violations": ["provider_ownership_fallback_active"],
        "semantic_embedding_strict_rollout_violation_count": 1,
        "semantic_embedding_strict_rollout_ready": False,
        "semantic_embedding_strict_rollout_state": "not_ready_provider_ownership",
        "semantic_embedding_strict_rollout_hint": "resolve_provider_ownership_before_strict",
        "semantic_embedding_strict_rollout_recommendation": "keep_provider_ownership_warn_until_provider_owner_is_effective",
        "semantic_embedding_recommended_provider_ownership_enforcement": "warn",
        "semantic_embedding_recommended_model_governance_enforcement": "strict",
        "semantic_embedding_provider_ownership_enforcement_alignment": "aligned",
        "semantic_embedding_model_governance_enforcement_alignment": "below_recommendation",
        "semantic_embedding_enforcement_alignment_state": "below_recommendation",
        "semantic_embedding_enforcement_alignment_hint": "consider_enabling_model_governance_strict",
        "semantic_embedding_dimensions": 1536,
        "semantic_embedding_warning_state": "provider_fallback_active",
        "semantic_embedding_warning_hint": "provider_not_implemented_using_deterministic_fallback",
        "semantic_embedding_source_kinds": ["episodic", "semantic", "affective"],
        "semantic_embedding_source_coverage_state": "full_for_current_retrieval_path",
        "semantic_embedding_source_coverage_hint": "semantic_and_affective_sources_enabled",
        "semantic_embedding_source_rollout_state": "semantic_affective_baseline",
        "semantic_embedding_source_rollout_hint": "high_signal_sources_active",
        "semantic_embedding_source_rollout_recommendation": "add_relation_source_after_baseline_stabilizes",
        "semantic_embedding_source_rollout_order": ["semantic", "affective", "relation"],
        "semantic_embedding_source_rollout_enabled_sources": ["semantic", "affective"],
        "semantic_embedding_source_rollout_missing_sources": ["relation"],
        "semantic_embedding_source_rollout_next_source_kind": "relation",
        "semantic_embedding_source_rollout_completion_state": "baseline_complete_relation_pending",
        "semantic_embedding_source_rollout_phase_index": 2,
        "semantic_embedding_source_rollout_phase_total": 3,
        "semantic_embedding_source_rollout_progress_percent": 67,
        "semantic_embedding_source_rollout_enforcement": "warn",
        "semantic_embedding_source_rollout_enforcement_state": "warning_only",
        "semantic_embedding_source_rollout_enforcement_hint": "pending_source_rollout_allowed_in_warn_mode",
        "semantic_embedding_recommended_source_rollout_enforcement": "warn",
        "semantic_embedding_source_rollout_enforcement_alignment": "aligned",
        "semantic_embedding_source_rollout_enforcement_alignment_state": "aligned_with_recommendation",
        "semantic_embedding_source_rollout_enforcement_alignment_hint": "source_rollout_enforcement_matches_recommendation",
        "semantic_embedding_refresh_mode": "on_write",
        "semantic_embedding_refresh_interval_seconds": 21600,
        "semantic_embedding_refresh_state": "on_write_refresh_active",
        "semantic_embedding_refresh_hint": "refresh_on_write_enabled",
        "semantic_embedding_refresh_cadence_state": "on_write_continuous",
        "semantic_embedding_refresh_cadence_hint": "on_write_refresh_has_no_manual_gap",
        "semantic_embedding_recommended_refresh_mode": "on_write",
        "semantic_embedding_refresh_alignment_state": "aligned",
        "semantic_embedding_refresh_alignment_hint": "refresh_mode_matches_active_rollout_recommendation",
    }


def test_health_endpoint_exposes_configured_embedding_source_kinds() -> None:
    client, _, _ = _client(embedding_source_kinds="episodic,relation")

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"]["semantic_embedding_source_kinds"] == ["episodic", "relation"]
    assert body["memory_retrieval"]["semantic_embedding_source_coverage_state"] == "missing_for_current_retrieval_path"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_coverage_hint"]
        == "enable_semantic_or_affective_source_for_vector_hits"
    )
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_state"] == "foundational_sources_only"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_recommendation"]
        == "enable_semantic_then_affective_sources"
    )
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enabled_sources"] == ["relation"]
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_missing_sources"] == ["semantic", "affective"]
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_next_source_kind"] == "semantic"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_completion_state"]
        == "baseline_blocked_semantic_missing"
    )
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_progress_percent"] == 33
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement"] == "warn"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_state"] == "warning_only"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_hint"]
        == "pending_source_rollout_allowed_in_warn_mode"
    )
    assert body["memory_retrieval"]["semantic_embedding_recommended_source_rollout_enforcement"] == "warn"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment"] == "aligned"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment_state"]
        == "aligned_with_recommendation"
    )
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment_hint"]
        == "source_rollout_enforcement_matches_recommendation"
    )


def test_health_endpoint_marks_source_rollout_fully_enabled_when_relation_is_included() -> None:
    client, _, _ = _client(embedding_source_kinds="episodic,semantic,affective,relation")

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_state"] == "all_vector_sources_enabled"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_hint"]
        == "semantic_affective_relation_sources_enabled"
    )
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_recommendation"]
        == "maintain_current_source_rollout"
    )
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enabled_sources"]
        == ["semantic", "affective", "relation"]
    )
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_missing_sources"] == []
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_next_source_kind"] == "none"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_completion_state"] == "fully_enabled"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_progress_percent"] == 100
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_state"]
        == "not_applicable_rollout_complete"
    )
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_hint"] == "source_rollout_is_complete"
    assert body["memory_retrieval"]["semantic_embedding_recommended_source_rollout_enforcement"] == "strict"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment"] == "below_recommendation"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment_state"]
        == "below_recommendation"
    )
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment_hint"]
        == "consider_enabling_source_rollout_strict_when_rollout_is_complete"
    )
    assert body["memory_retrieval"]["semantic_embedding_recommended_refresh_mode"] == "manual"
    assert (
        body["memory_retrieval"]["semantic_embedding_refresh_alignment_state"]
        == "on_write_before_recommended_manual"
    )
    assert (
        body["memory_retrieval"]["semantic_embedding_refresh_alignment_hint"]
        == "consider_switching_to_manual_for_mature_rollout"
    )


def test_health_endpoint_exposes_embedding_model_governance_posture_for_deterministic_custom_model() -> None:
    client, _, _ = _client(
        embedding_provider="deterministic",
        embedding_model="deterministic-v2",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"]["semantic_embedding_model_governance_state"] == "deterministic_custom_model_name"
    assert (
        body["memory_retrieval"]["semantic_embedding_model_governance_hint"]
        == "deterministic_provider_uses_fixed_embedding_behavior"
    )
    assert body["memory_retrieval"]["semantic_embedding_model_governance_enforcement"] == "warn"
    assert body["memory_retrieval"]["semantic_embedding_model_governance_enforcement_state"] == "warning_only"


def test_health_endpoint_exposes_provider_ownership_enforcement_blocked_posture_in_strict_mode() -> None:
    client, _, _ = _client(
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_provider_ownership_enforcement="strict",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"]["semantic_embedding_provider_ownership_enforcement"] == "strict"
    assert body["memory_retrieval"]["semantic_embedding_provider_ownership_enforcement_state"] == "blocked"
    assert (
        body["memory_retrieval"]["semantic_embedding_provider_ownership_enforcement_hint"]
        == "switch_to_effective_provider_owner_before_startup"
    )
    assert body["memory_retrieval"]["semantic_embedding_enforcement_alignment_state"] == "mixed_relative_to_recommendation"
    assert (
        body["memory_retrieval"]["semantic_embedding_enforcement_alignment_hint"]
        == "normalize_enforcement_levels_to_recommendation"
    )


def test_health_endpoint_exposes_model_governance_enforcement_blocked_posture_in_strict_mode() -> None:
    client, _, _ = _client(
        embedding_provider="deterministic",
        embedding_model="deterministic-v2",
        embedding_model_governance_enforcement="strict",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"]["semantic_embedding_model_governance_enforcement"] == "strict"
    assert body["memory_retrieval"]["semantic_embedding_model_governance_enforcement_state"] == "blocked"
    assert (
        body["memory_retrieval"]["semantic_embedding_model_governance_enforcement_hint"]
        == "use_deterministic_v1_or_switch_to_effective_provider_model"
    )
    assert body["memory_retrieval"]["semantic_embedding_enforcement_alignment_state"] == "mixed_relative_to_recommendation"
    assert (
        body["memory_retrieval"]["semantic_embedding_enforcement_alignment_hint"]
        == "normalize_enforcement_levels_to_recommendation"
    )


def test_health_endpoint_exposes_source_rollout_enforcement_blocked_posture_in_strict_mode() -> None:
    client, _, _ = _client(
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_source_rollout_enforcement="strict",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement"] == "strict"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_state"] == "blocked"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_hint"]
        == "enable_pending_source_kinds_before_startup"
    )
    assert body["memory_retrieval"]["semantic_embedding_recommended_source_rollout_enforcement"] == "warn"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment"] == "above_recommendation"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment_state"]
        == "above_recommendation"
    )
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment_hint"]
        == "source_rollout_strict_enabled_ahead_of_recommendation"
    )
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_next_source_kind"] == "relation"


def test_health_endpoint_exposes_source_rollout_enforcement_aligned_posture_when_rollout_is_complete_and_strict_is_enabled() -> None:
    client, _, _ = _client(
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective,relation",
        embedding_source_rollout_enforcement="strict",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_next_source_kind"] == "none"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement"] == "strict"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_state"]
        == "not_applicable_rollout_complete"
    )
    assert body["memory_retrieval"]["semantic_embedding_recommended_source_rollout_enforcement"] == "strict"
    assert body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment"] == "aligned"
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment_state"]
        == "aligned_with_recommendation"
    )
    assert (
        body["memory_retrieval"]["semantic_embedding_source_rollout_enforcement_alignment_hint"]
        == "source_rollout_enforcement_matches_recommendation"
    )


def test_health_endpoint_exposes_embedding_refresh_posture() -> None:
    client, _, _ = _client(
        embedding_refresh_mode="manual",
        embedding_refresh_interval_seconds=7200,
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["memory_retrieval"]["semantic_embedding_refresh_mode"] == "manual"
    assert body["memory_retrieval"]["semantic_embedding_refresh_interval_seconds"] == 7200
    assert body["memory_retrieval"]["semantic_embedding_refresh_state"] == "manual_refresh_required"
    assert (
        body["memory_retrieval"]["semantic_embedding_refresh_hint"]
        == "ensure_manual_refresh_process_is_defined"
    )
    assert body["memory_retrieval"]["semantic_embedding_refresh_cadence_state"] == "manual_moderate_frequency"
    assert (
        body["memory_retrieval"]["semantic_embedding_refresh_cadence_hint"]
        == "manual_refresh_runs_within_daily_window"
    )
    assert body["memory_retrieval"]["semantic_embedding_recommended_refresh_mode"] == "on_write"
    assert body["memory_retrieval"]["semantic_embedding_refresh_alignment_state"] == "manual_override"
    assert (
        body["memory_retrieval"]["semantic_embedding_refresh_alignment_hint"]
        == "ensure_manual_mode_has_operational_coverage"
    )
    assert body["memory_retrieval"]["semantic_embedding_owner_strategy_state"] == "deterministic_manual_owner"
    assert (
        body["memory_retrieval"]["semantic_embedding_owner_strategy_hint"]
        == "manual_refresh_required_for_deterministic_owner"
    )


def test_health_endpoint_marks_scheduler_unhealthy_when_enabled_but_not_running() -> None:
    client, _, _ = _client(
        scheduler_enabled=True,
        scheduler_running=False,
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["scheduler"]["enabled"] is True
    assert body["scheduler"]["running"] is False
    assert body["scheduler"]["healthy"] is False
    assert body["scheduler"]["cadence_execution"]["ready"] is False
    assert "in_process_scheduler_not_running" in body["scheduler"]["cadence_execution"]["blocking_signals"]


def test_health_endpoint_exposes_externalized_scheduler_execution_mode_posture() -> None:
    client, _, _ = _client(
        scheduler_enabled=True,
        scheduler_running=False,
        scheduler_execution_mode="externalized",
        proactive_enabled=True,
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["scheduler"]["execution_mode"] == "externalized"
    assert body["scheduler"]["enabled"] is True
    assert body["scheduler"]["running"] is False
    assert body["scheduler"]["proactive_enabled"] is True
    assert body["scheduler"]["maintenance_cadence_owner"] == "external_scheduler"
    assert body["scheduler"]["proactive_cadence_owner"] == "external_scheduler"
    assert body["scheduler"]["cadence_execution"]["selected_execution_mode"] == "externalized"
    assert body["scheduler"]["cadence_execution"]["maintenance_cadence_owner"] == "external_scheduler"
    assert body["scheduler"]["cadence_execution"]["proactive_cadence_owner"] == "external_scheduler"
    assert body["scheduler"]["cadence_execution"]["maintenance_tick_dispatch"] is False
    assert body["scheduler"]["cadence_execution"]["maintenance_tick_reason"] == "externalized_owner_mode"
    assert body["scheduler"]["cadence_execution"]["proactive_tick_dispatch"] is False
    assert body["scheduler"]["cadence_execution"]["proactive_tick_reason"] == "externalized_owner_mode"
    assert body["scheduler"]["healthy"] is True


def test_health_endpoint_exposes_attention_snapshot() -> None:
    client, _, _ = _client(attention_burst_window_ms=240)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["attention"] == {
        "healthy": True,
        "coordination_mode": "in_process",
        "turn_state_owner": "in_process_coordinator",
        "durable_inbox_expected": False,
        "deployment_readiness": {
            "baseline_coordination_mode": "in_process",
            "selected_coordination_mode": "in_process",
            "ready": True,
            "blocking_signals": [],
            "turn_state_owner": "in_process_coordinator",
            "durable_inbox_expected": False,
        },
        "burst_window_ms": 240,
        "answered_ttl_seconds": 0.5,
        "stale_turn_seconds": 3.0,
        "pending": 0,
        "claimed": 0,
        "answered": 0,
    }


def test_health_endpoint_exposes_durable_attention_owner_mode_posture() -> None:
    client, _, _ = _client(
        attention_coordination_mode="durable_inbox",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["attention"]["coordination_mode"] == "durable_inbox"
    assert body["attention"]["turn_state_owner"] == "durable_attention_inbox"
    assert body["attention"]["durable_inbox_expected"] is True
    assert body["attention"]["healthy"] is False
    assert body["attention"]["deployment_readiness"]["selected_coordination_mode"] == "durable_inbox"
    assert body["attention"]["deployment_readiness"]["ready"] is False
    assert "durable_inbox_owner_mode_not_implemented" in body["attention"]["deployment_readiness"]["blocking_signals"]


def test_health_endpoint_exposes_runtime_policy_flags() -> None:
    client, _, _ = _client(
        app_env="production",
        event_debug_enabled=False,
        startup_schema_mode="create_tables",
        production_policy_enforcement="strict",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["runtime_policy"] == {
        "startup_schema_mode": "create_tables",
        "event_debug_enabled": False,
        "event_debug_token_required": False,
        "production_debug_token_required": True,
        "event_debug_query_compat_enabled": False,
        "event_debug_query_compat_source": "environment_default",
        "event_debug_ingress_owner": "internal_route_primary_shared_route_compat",
        "event_debug_internal_ingress_path": "/internal/event/debug",
        "event_debug_shared_ingress_path": "/event/debug",
        "event_debug_shared_ingress_mode": "compatibility",
        "event_debug_shared_ingress_break_glass_required": False,
        "event_debug_shared_ingress_posture": "transitional_compatibility",
        "debug_access_posture": "disabled",
        "debug_token_policy_hint": "not_applicable_debug_disabled",
        "event_debug_source": "explicit",
        "production_policy_enforcement": "strict",
        "recommended_production_policy_enforcement": "warn",
        "production_policy_mismatches": ["startup_schema_mode=create_tables"],
        "production_policy_mismatch_count": 1,
        "strict_startup_blocked": True,
        "strict_rollout_ready": False,
        "strict_rollout_hint": "resolve_mismatches_before_strict",
        "event_debug_query_compat_allow_rate": 0.0,
        "event_debug_query_compat_block_rate": 0.0,
        "event_debug_query_compat_recommendation": "compat_disabled",
        "event_debug_query_compat_sunset_ready": True,
        "event_debug_query_compat_sunset_reason": "compat_disabled",
        "event_debug_query_compat_recent_attempts_total": 0,
        "event_debug_query_compat_recent_allow_rate": 0.0,
        "event_debug_query_compat_recent_block_rate": 0.0,
        "event_debug_query_compat_recent_state": "compat_disabled",
        "event_debug_query_compat_stale_after_seconds": 86400,
        "event_debug_query_compat_last_attempt_age_seconds": None,
        "event_debug_query_compat_last_attempt_state": "no_attempts_recorded",
        "event_debug_query_compat_activity_state": "compat_disabled",
        "event_debug_query_compat_activity_hint": "compat_disabled_no_action",
        "event_debug_query_compat_telemetry": {
            "attempts_total": 0,
            "allowed_total": 0,
            "blocked_total": 0,
            "last_attempt_at": None,
            "last_allowed_at": None,
            "last_blocked_at": None,
            "recent_window_size": 20,
            "recent_attempts_total": 0,
            "recent_allowed_total": 0,
            "recent_blocked_total": 0,
        },
    }


def test_health_endpoint_marks_break_glass_shared_ingress_posture_when_configured() -> None:
    client, _, _ = _client(
        event_debug_enabled=True,
        event_debug_shared_ingress_mode="break_glass_only",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["event_debug_shared_ingress_mode"] == "break_glass_only"
    assert body["runtime_policy"]["event_debug_shared_ingress_break_glass_required"] is True
    assert body["runtime_policy"]["event_debug_shared_ingress_posture"] == "transitional_break_glass_only"
    assert body["runtime_policy"]["event_debug_internal_ingress_path"] == "/internal/event/debug"
    assert body["runtime_policy"]["event_debug_shared_ingress_path"] == "/event/debug"


def test_health_endpoint_marks_event_debug_source_as_environment_default_when_unset() -> None:
    client, _, _ = _client(event_debug_enabled=None)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["event_debug_enabled"] is True
    assert body["runtime_policy"]["event_debug_token_required"] is False
    assert body["runtime_policy"]["production_debug_token_required"] is True
    assert body["runtime_policy"]["event_debug_query_compat_enabled"] is True
    assert body["runtime_policy"]["event_debug_query_compat_source"] == "environment_default"
    assert body["runtime_policy"]["debug_access_posture"] == "open_no_token"
    assert body["runtime_policy"]["debug_token_policy_hint"] == "debug_access_open_without_token"
    assert body["runtime_policy"]["event_debug_source"] == "environment_default"
    assert body["runtime_policy"]["production_policy_enforcement"] == "warn"
    assert body["runtime_policy"]["recommended_production_policy_enforcement"] == "warn"
    assert body["runtime_policy"]["production_policy_mismatches"] == []
    assert body["runtime_policy"]["production_policy_mismatch_count"] == 0
    assert body["runtime_policy"]["strict_startup_blocked"] is False
    assert body["runtime_policy"]["strict_rollout_ready"] is True
    assert body["runtime_policy"]["strict_rollout_hint"] == "not_applicable_non_production"
    assert body["release_readiness"]["ready"] is True
    assert body["release_readiness"]["violations"] == []
    assert body["runtime_policy"]["event_debug_query_compat_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_block_rate"] == 0.0
    assert (
        body["runtime_policy"]["event_debug_query_compat_recommendation"]
        == "no_compat_traffic_detected_disable_when_possible"
    )
    assert body["runtime_policy"]["event_debug_query_compat_sunset_ready"] is True
    assert body["runtime_policy"]["event_debug_query_compat_sunset_reason"] == "no_compat_attempts_detected"
    assert body["runtime_policy"]["event_debug_query_compat_recent_attempts_total"] == 0
    assert body["runtime_policy"]["event_debug_query_compat_recent_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_block_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_state"] == "no_recent_attempts"
    assert body["runtime_policy"]["event_debug_query_compat_stale_after_seconds"] == 86400
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"] is None
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "no_attempts_recorded"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "no_attempts_observed"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "can_disable_when_ready"


def test_health_endpoint_exposes_all_production_policy_mismatches_when_present() -> None:
    client, _, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="strict",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["production_policy_mismatches"] == [
        "event_debug_enabled=true",
        "event_debug_token_missing=true",
        "startup_schema_mode=create_tables",
    ]
    assert body["runtime_policy"]["production_policy_mismatch_count"] == 3
    assert body["runtime_policy"]["strict_startup_blocked"] is True
    assert body["runtime_policy"]["strict_rollout_ready"] is False
    assert body["release_readiness"]["ready"] is False
    assert body["release_readiness"]["violations"] == [
        "runtime_policy.production_policy_mismatches_non_empty",
        "runtime_policy.strict_startup_blocked=true",
    ]
    assert body["runtime_policy"]["production_debug_token_required"] is True
    assert body["runtime_policy"]["event_debug_query_compat_enabled"] is False
    assert body["runtime_policy"]["event_debug_query_compat_source"] == "environment_default"
    assert body["runtime_policy"]["debug_access_posture"] == "production_token_required_missing"
    assert body["runtime_policy"]["debug_token_policy_hint"] == "configure_event_debug_token_or_disable_debug"
    assert body["runtime_policy"]["recommended_production_policy_enforcement"] == "warn"
    assert body["runtime_policy"]["strict_rollout_hint"] == "resolve_mismatches_before_strict"
    assert body["runtime_policy"]["event_debug_query_compat_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_block_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recommendation"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_sunset_ready"] is True
    assert body["runtime_policy"]["event_debug_query_compat_sunset_reason"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_recent_attempts_total"] == 0
    assert body["runtime_policy"]["event_debug_query_compat_recent_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_block_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_state"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_stale_after_seconds"] == 86400
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"] is None
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "no_attempts_recorded"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "compat_disabled_no_action"


def test_health_endpoint_shows_strict_rollout_hint_when_production_is_ready() -> None:
    client, _, _ = _client(
        app_env="production",
        event_debug_enabled=False,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["production_policy_mismatches"] == []
    assert body["runtime_policy"]["event_debug_token_required"] is False
    assert body["runtime_policy"]["production_debug_token_required"] is True
    assert body["runtime_policy"]["event_debug_query_compat_enabled"] is False
    assert body["runtime_policy"]["event_debug_query_compat_source"] == "environment_default"
    assert body["runtime_policy"]["debug_access_posture"] == "disabled"
    assert body["runtime_policy"]["debug_token_policy_hint"] == "not_applicable_debug_disabled"
    assert body["runtime_policy"]["strict_rollout_ready"] is True
    assert body["runtime_policy"]["recommended_production_policy_enforcement"] == "strict"
    assert body["runtime_policy"]["strict_rollout_hint"] == "can_enable_strict"
    assert body["runtime_policy"]["event_debug_query_compat_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_block_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recommendation"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_sunset_ready"] is True
    assert body["runtime_policy"]["event_debug_query_compat_sunset_reason"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_recent_attempts_total"] == 0
    assert body["runtime_policy"]["event_debug_query_compat_recent_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_block_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_state"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_stale_after_seconds"] == 86400
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"] is None
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "no_attempts_recorded"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "compat_disabled_no_action"


def test_health_endpoint_defaults_to_strict_policy_enforcement_in_production_when_unset() -> None:
    client, _, _ = _client(
        app_env="production",
        event_debug_enabled=False,
        startup_schema_mode="migrate",
        production_policy_enforcement=None,  # type: ignore[arg-type]
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["production_policy_enforcement"] == "strict"
    assert body["runtime_policy"]["production_policy_mismatches"] == []
    assert body["runtime_policy"]["strict_startup_blocked"] is False
    assert body["runtime_policy"]["strict_rollout_ready"] is True


def test_health_endpoint_marks_query_compat_as_explicit_production_mismatch_when_enabled() -> None:
    client, _, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        event_debug_query_compat_enabled=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["event_debug_query_compat_enabled"] is True
    assert body["runtime_policy"]["event_debug_query_compat_source"] == "explicit"
    assert body["runtime_policy"]["production_policy_mismatches"] == [
        "event_debug_enabled=true",
        "event_debug_query_compat_enabled=true",
    ]
    assert body["runtime_policy"]["production_policy_mismatch_count"] == 2
    assert body["runtime_policy"]["strict_rollout_ready"] is False
    assert body["release_readiness"]["ready"] is False
    assert body["release_readiness"]["violations"] == [
        "runtime_policy.production_policy_mismatches_non_empty",
        "runtime_policy.event_debug_query_compat_enabled=true",
    ]
    assert body["runtime_policy"]["event_debug_query_compat_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_block_rate"] == 0.0
    assert (
        body["runtime_policy"]["event_debug_query_compat_recommendation"]
        == "no_compat_traffic_detected_disable_when_possible"
    )
    assert body["runtime_policy"]["event_debug_query_compat_sunset_ready"] is True
    assert body["runtime_policy"]["event_debug_query_compat_sunset_reason"] == "no_compat_attempts_detected"
    assert body["runtime_policy"]["event_debug_query_compat_recent_attempts_total"] == 0
    assert body["runtime_policy"]["event_debug_query_compat_recent_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_block_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_state"] == "no_recent_attempts"
    assert body["runtime_policy"]["event_debug_query_compat_stale_after_seconds"] == 86400
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"] is None
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "no_attempts_recorded"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "no_attempts_observed"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "can_disable_when_ready"


def test_health_endpoint_marks_debug_access_posture_as_token_gated_when_token_is_configured() -> None:
    client, _, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["event_debug_enabled"] is True
    assert body["runtime_policy"]["event_debug_token_required"] is True
    assert body["runtime_policy"]["debug_access_posture"] == "token_gated"
    assert body["runtime_policy"]["debug_token_policy_hint"] == "token_gated"


def test_health_endpoint_marks_debug_access_posture_as_open_when_production_token_requirement_is_disabled() -> None:
    client, _, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=False,
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["event_debug_enabled"] is True
    assert body["runtime_policy"]["event_debug_token_required"] is False
    assert body["runtime_policy"]["production_debug_token_required"] is False
    assert body["runtime_policy"]["debug_access_posture"] == "open_no_token"
    assert body["runtime_policy"]["debug_token_policy_hint"] == "debug_access_open_without_token"


def test_health_endpoint_marks_reflection_unhealthy_when_worker_not_running() -> None:
    client, _, _ = _client(reflection_running=False)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["reflection"]["healthy"] is False
    assert body["reflection"]["deployment_readiness"]["ready"] is False
    assert "in_process_worker_not_running" in body["reflection"]["deployment_readiness"]["blocking_signals"]
    assert body["reflection"]["worker"]["running"] is False
    assert body["reflection"]["tasks"]["exhausted_failed"] == 0
    assert body["reflection"]["tasks"]["stuck_processing"] == 0


def test_health_endpoint_marks_reflection_unhealthy_when_queue_is_stuck() -> None:
    client, _, _ = _client(
        reflection_stats={
            "total": 5,
            "pending": 0,
            "processing": 1,
            "completed": 3,
            "failed": 1,
            "retryable_failed": 0,
            "exhausted_failed": 1,
            "stuck_processing": 1,
        }
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["reflection"]["healthy"] is False
    assert body["reflection"]["deployment_readiness"]["ready"] is False
    assert "reflection_stuck_processing_detected" in body["reflection"]["deployment_readiness"]["blocking_signals"]
    assert "reflection_exhausted_failures_detected" in body["reflection"]["deployment_readiness"]["blocking_signals"]
    assert body["reflection"]["worker"]["running"] is True
    assert body["reflection"]["tasks"]["exhausted_failed"] == 1
    assert body["reflection"]["tasks"]["stuck_processing"] == 1


def test_health_endpoint_marks_deferred_mode_not_ready_when_in_process_worker_is_running() -> None:
    client, _, _ = _client(
        reflection_running=True,
        reflection_runtime_mode="deferred",
    )

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["reflection"]["runtime_mode"] == "deferred"
    assert body["reflection"]["deployment_readiness"]["ready"] is False
    assert "deferred_in_process_worker_running" in body["reflection"]["deployment_readiness"]["blocking_signals"]


def test_event_endpoint_returns_public_response_and_normalizes_event() -> None:
    client, runtime, _ = _client()

    response = client.post("/event", json={"text": "hello from api"})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "event_id": runtime.last_event.event_id if runtime.last_event is not None else body["event_id"],
        "trace_id": runtime.last_event.meta.trace_id if runtime.last_event is not None else body["trace_id"],
        "source": "api",
        "reply": {
            "message": "Test reply",
            "language": "en",
            "tone": "supportive",
            "channel": "api",
        },
        "runtime": {
            "role": "advisor",
            "motivation_mode": "respond",
            "action_status": "success",
            "reflection_triggered": False,
        },
    }
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "hello from api"
    assert runtime.last_event.meta.trace_id
    assert "debug" not in body


def test_event_endpoint_enforces_api_boundary_for_source_and_payload_shape() -> None:
    client, runtime, _ = _client()

    response = client.post(
        "/event",
        json={
            "text": "  hello   from \n api  ",
            "source": "telegram",
            "subsource": "user_message",
            "payload": {"text": "payload text", "hidden": "value"},
            "meta": {"user_id": "", "trace_id": ""},
        },
    )

    assert response.status_code == 200
    assert runtime.last_event is not None
    assert runtime.last_event.source == "api"
    assert runtime.last_event.subsource == "event_endpoint"
    assert runtime.last_event.payload == {"text": "hello from api"}
    assert runtime.last_event.meta.user_id == "anonymous"
    assert runtime.last_event.meta.trace_id


def test_event_endpoint_uses_x_aion_user_id_header_when_meta_user_id_is_missing() -> None:
    client, runtime, _ = _client()

    response = client.post(
        "/event",
        json={"text": "hello from api"},
        headers={"X-AION-User-Id": "header-user"},
    )

    assert response.status_code == 200
    assert runtime.last_event is not None
    assert runtime.last_event.meta.user_id == "header-user"


def test_event_endpoint_prefers_meta_user_id_over_x_aion_user_id_header() -> None:
    client, runtime, _ = _client()

    response = client.post(
        "/event",
        json={"text": "hello from api", "meta": {"user_id": "meta-user"}},
        headers={"X-AION-User-Id": "header-user"},
    )

    assert response.status_code == 200
    assert runtime.last_event is not None
    assert runtime.last_event.meta.user_id == "meta-user"


def test_event_endpoint_user_id_fallback_does_not_stick_between_requests() -> None:
    client, runtime, _ = _client()

    first = client.post(
        "/event",
        json={"text": "hello from api"},
        headers={"X-AION-User-Id": "header-user"},
    )
    second = client.post(
        "/event",
        json={"text": "hello from api"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert len(runtime.events) == 2
    assert runtime.events[0].meta.user_id == "header-user"
    assert runtime.events[1].meta.user_id == "anonymous"


def test_event_endpoint_can_return_full_runtime_debug_payload_when_requested() -> None:
    client, runtime, _ = _client(reflection_triggered=True)

    response = client.post("/event?debug=true", json={"text": "show debug runtime"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"]["message"] == "Test reply"
    assert body["runtime"]["reflection_triggered"] is True
    assert body["debug"]["affective"]["affect_label"] == "neutral"
    assert body["debug"]["expression"]["message"] == "Test reply"
    assert body["debug"]["perception"]["language"] == "en"
    assert body["debug"]["perception"]["affective"]["source"] == "deterministic_placeholder"
    assert body["debug"]["identity"]["mission"] == "Help the user move forward with clear, constructive support."
    assert body["debug"]["active_goals"][0]["name"] == "ship the MVP"
    assert body["debug"]["active_tasks"][0]["status"] == "blocked"
    assert body["debug"]["goal_progress_history"][0]["score"] == 0.42
    assert body["debug"]["stage_timings_ms"]["memory_load"] == 1
    assert body["debug"]["stage_timings_ms"]["total"] == 12
    assert body["debug"]["event"]["source"] == "api"
    assert response.headers["x-aion-debug-compat"] == "query_debug_route_is_compatibility_use_internal_event_debug"
    assert response.headers["link"] == "</internal/event/debug>; rel=\"alternate\""
    assert response.headers["x-aion-debug-compat-deprecated"] == "true"
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "show debug runtime"


def test_event_debug_endpoint_returns_full_runtime_debug_payload_when_enabled() -> None:
    client, runtime, _ = _client(reflection_triggered=True)

    response = client.post("/event/debug", json={"text": "show explicit debug runtime"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"]["message"] == "Test reply"
    assert body["runtime"]["reflection_triggered"] is True
    assert body["debug"]["expression"]["message"] == "Test reply"
    assert body["debug"]["event"]["source"] == "api"
    assert "x-aion-debug-compat" not in response.headers
    assert (
        response.headers["x-aion-debug-shared-compat"]
        == "shared_debug_route_is_compatibility_use_internal_event_debug"
    )
    assert response.headers["link"] == "</internal/event/debug>; rel=\"alternate\""
    assert response.headers["x-aion-debug-shared-compat-deprecated"] == "true"
    assert response.headers["x-aion-debug-shared-mode"] == "compatibility"
    assert response.headers["x-aion-debug-shared-posture"] == "transitional_compatibility"
    assert "x-aion-debug-shared-break-glass-used" not in response.headers
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "show explicit debug runtime"


def test_internal_event_debug_endpoint_returns_primary_debug_payload_without_shared_compat_headers() -> None:
    client, runtime, _ = _client(reflection_triggered=True)

    response = client.post("/internal/event/debug", json={"text": "show internal debug runtime"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"]["message"] == "Test reply"
    assert body["runtime"]["reflection_triggered"] is True
    assert body["debug"]["event"]["source"] == "api"
    assert "x-aion-debug-compat" not in response.headers
    assert "x-aion-debug-shared-compat" not in response.headers
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "show internal debug runtime"


def test_internal_event_debug_endpoint_returns_fail_action_result_without_500() -> None:
    client, runtime, _ = _client(
        runtime_action_status="fail",
        runtime_action_actions=["send_telegram_message"],
        runtime_action_notes="Telegram delivery exception: TimeoutError: upstream timeout",
    )

    response = client.post("/internal/event/debug", json=_telegram_update(9001, "trigger telegram failure"))

    assert response.status_code == 200
    body = response.json()
    assert body["runtime"]["action_status"] == "fail"
    assert body["debug"]["action_result"]["status"] == "fail"
    assert body["debug"]["action_result"]["actions"] == ["send_telegram_message"]
    assert "TimeoutError" in body["debug"]["action_result"]["notes"]
    assert runtime.last_event is not None


def test_event_debug_endpoint_rejects_shared_ingress_when_break_glass_override_is_required() -> None:
    client, runtime, _ = _client(
        event_debug_enabled=True,
        event_debug_shared_ingress_mode="break_glass_only",
    )

    response = client.post("/event/debug", json={"text": "shared debug without override"})

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Shared debug ingress is in break-glass-only mode. "
        "Set X-AION-Debug-Break-Glass: true or use POST /internal/event/debug."
    )
    assert runtime.last_event is None


def test_event_debug_endpoint_allows_shared_ingress_with_break_glass_override_header() -> None:
    client, runtime, _ = _client(
        event_debug_enabled=True,
        event_debug_shared_ingress_mode="break_glass_only",
    )

    response = client.post(
        "/event/debug",
        json={"text": "shared debug with break glass"},
        headers={"X-AION-Debug-Break-Glass": "true"},
    )

    assert response.status_code == 200
    assert (
        response.headers["x-aion-debug-shared-compat"]
        == "shared_debug_route_is_compatibility_use_internal_event_debug"
    )
    assert response.headers["x-aion-debug-shared-compat-deprecated"] == "true"
    assert response.headers["link"] == "</internal/event/debug>; rel=\"alternate\""
    assert response.headers["x-aion-debug-shared-mode"] == "break_glass_only"
    assert response.headers["x-aion-debug-shared-posture"] == "transitional_break_glass_only"
    assert response.headers["x-aion-debug-shared-break-glass-used"] == "true"
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "shared debug with break glass"


def test_internal_event_debug_endpoint_ignores_shared_break_glass_posture() -> None:
    client, runtime, _ = _client(
        event_debug_enabled=True,
        event_debug_shared_ingress_mode="break_glass_only",
    )

    response = client.post("/internal/event/debug", json={"text": "internal debug no override"})

    assert response.status_code == 200
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "internal debug no override"


def test_event_endpoint_rejects_debug_payload_when_debug_token_is_missing() -> None:
    client, runtime, _ = _client(event_debug_enabled=True, event_debug_token="debug-secret")

    response = client.post("/event?debug=true", json={"text": "show debug runtime"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid debug token."
    assert runtime.last_event is None


def test_event_debug_endpoint_rejects_debug_payload_when_debug_token_is_missing() -> None:
    client, runtime, _ = _client(event_debug_enabled=True, event_debug_token="debug-secret")

    response = client.post("/event/debug", json={"text": "show debug runtime"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid debug token."
    assert runtime.last_event is None


def test_event_endpoint_rejects_debug_payload_in_production_when_token_is_not_configured() -> None:
    client, runtime, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        event_debug_query_compat_enabled=True,
    )

    response = client.post("/event?debug=true", json={"text": "show debug runtime"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Debug token is required in production."
    assert runtime.last_event is None


def test_event_debug_endpoint_rejects_debug_payload_in_production_when_token_is_not_configured() -> None:
    client, runtime, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
    )

    response = client.post("/event/debug", json={"text": "show debug runtime"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Debug token is required in production."
    assert runtime.last_event is None


def test_event_endpoint_allows_debug_payload_in_production_when_token_requirement_is_disabled() -> None:
    client, runtime, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=False,
        event_debug_query_compat_enabled=True,
    )

    response = client.post("/event?debug=true", json={"text": "show debug runtime"})

    assert response.status_code == 200
    body = response.json()
    assert "debug" in body
    assert body["debug"]["expression"]["message"] == "Test reply"
    assert runtime.last_event is not None


def test_event_endpoint_rejects_debug_query_compat_route_in_production_when_disabled_by_default() -> None:
    client, runtime, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
    )

    response = client.post("/event?debug=true", json={"text": "show debug runtime"})

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Debug query compatibility route is disabled for this environment. Use POST /internal/event/debug."
    )
    assert runtime.last_event is None

    body = client.get("/health").json()
    assert body["runtime_policy"]["event_debug_query_compat_telemetry"]["attempts_total"] == 1
    assert body["runtime_policy"]["event_debug_query_compat_telemetry"]["allowed_total"] == 0
    assert body["runtime_policy"]["event_debug_query_compat_telemetry"]["blocked_total"] == 1
    assert body["runtime_policy"]["event_debug_query_compat_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_block_rate"] == 1.0
    assert body["runtime_policy"]["event_debug_query_compat_recommendation"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_sunset_ready"] is True
    assert body["runtime_policy"]["event_debug_query_compat_sunset_reason"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_recent_attempts_total"] == 1
    assert body["runtime_policy"]["event_debug_query_compat_recent_allow_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_block_rate"] == 1.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_state"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_stale_after_seconds"] == 86400
    assert isinstance(body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"], int)
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"] >= 0
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "fresh"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "compat_disabled"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "compat_disabled_no_action"


def test_event_endpoint_allows_debug_payload_when_debug_token_matches() -> None:
    client, runtime, _ = _client(event_debug_enabled=True, event_debug_token="debug-secret")

    response = client.post(
        "/event?debug=true",
        json={"text": "show debug runtime"},
        headers={"X-AION-Debug-Token": "debug-secret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "debug" in body
    assert body["debug"]["expression"]["message"] == "Test reply"
    assert response.headers["x-aion-debug-compat"] == "query_debug_route_is_compatibility_use_internal_event_debug"
    assert response.headers["x-aion-debug-compat-deprecated"] == "true"
    assert runtime.last_event is not None


def test_event_endpoint_allows_debug_payload_in_production_when_query_compat_is_explicitly_enabled() -> None:
    client, runtime, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        event_debug_query_compat_enabled=True,
    )

    response = client.post(
        "/event?debug=true",
        json={"text": "show debug runtime"},
        headers={"X-AION-Debug-Token": "debug-secret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "debug" in body
    assert body["debug"]["expression"]["message"] == "Test reply"
    assert response.headers["x-aion-debug-compat"] == "query_debug_route_is_compatibility_use_internal_event_debug"
    assert response.headers["x-aion-debug-compat-deprecated"] == "true"
    assert runtime.last_event is not None


def test_health_endpoint_exposes_query_compat_telemetry_after_allowed_and_blocked_attempts() -> None:
    client, _, _ = _client(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        event_debug_query_compat_enabled=True,
    )

    allowed = client.post(
        "/event?debug=true",
        json={"text": "debug allowed"},
        headers={"X-AION-Debug-Token": "debug-secret"},
    )
    assert allowed.status_code == 200

    blocked = client.post(
        "/event?debug=true",
        json={"text": "debug blocked"},
    )
    assert blocked.status_code == 403

    body = client.get("/health").json()
    telemetry = body["runtime_policy"]["event_debug_query_compat_telemetry"]
    assert telemetry["attempts_total"] == 2
    assert telemetry["allowed_total"] == 1
    assert telemetry["blocked_total"] == 1
    assert telemetry["last_attempt_at"] is not None
    assert telemetry["last_allowed_at"] is not None
    assert telemetry["last_blocked_at"] is not None
    assert telemetry["recent_window_size"] == 20
    assert telemetry["recent_attempts_total"] == 2
    assert telemetry["recent_allowed_total"] == 1
    assert telemetry["recent_blocked_total"] == 1
    assert body["runtime_policy"]["event_debug_query_compat_allow_rate"] == 0.5
    assert body["runtime_policy"]["event_debug_query_compat_block_rate"] == 0.5
    assert (
        body["runtime_policy"]["event_debug_query_compat_recommendation"]
        == "migrate_clients_before_disabling_compat"
    )
    assert body["runtime_policy"]["event_debug_query_compat_sunset_ready"] is False
    assert (
        body["runtime_policy"]["event_debug_query_compat_sunset_reason"]
        == "compat_attempts_detected_migration_needed"
    )
    assert body["runtime_policy"]["event_debug_query_compat_recent_attempts_total"] == 2
    assert body["runtime_policy"]["event_debug_query_compat_recent_allow_rate"] == 0.5
    assert body["runtime_policy"]["event_debug_query_compat_recent_block_rate"] == 0.5
    assert body["runtime_policy"]["event_debug_query_compat_recent_state"] == "mixed"
    assert body["runtime_policy"]["event_debug_query_compat_stale_after_seconds"] == 86400
    assert isinstance(body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"], int)
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"] >= 0
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "fresh"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "recent_attempts_observed"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "keep_compat_until_recent_clients_migrate"


def test_health_endpoint_respects_configured_query_compat_recent_window_size() -> None:
    client, _, _ = _client(
        event_debug_query_compat_recent_window=3,
    )

    for _ in range(4):
        response = client.post("/event?debug=true", json={"text": "debug rolling window"})
        assert response.status_code == 200

    body = client.get("/health").json()
    telemetry = body["runtime_policy"]["event_debug_query_compat_telemetry"]
    assert telemetry["recent_window_size"] == 3
    assert telemetry["recent_attempts_total"] == 3
    assert telemetry["recent_allowed_total"] == 3
    assert telemetry["recent_blocked_total"] == 0
    assert body["runtime_policy"]["event_debug_query_compat_recent_attempts_total"] == 3
    assert body["runtime_policy"]["event_debug_query_compat_recent_allow_rate"] == 1.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_block_rate"] == 0.0
    assert body["runtime_policy"]["event_debug_query_compat_recent_state"] == "mostly_allowed"
    assert body["runtime_policy"]["event_debug_query_compat_stale_after_seconds"] == 86400
    assert isinstance(body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"], int)
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"] >= 0
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "fresh"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "recent_attempts_observed"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "keep_compat_until_recent_clients_migrate"


def test_health_endpoint_respects_configured_query_compat_stale_threshold() -> None:
    client, _, _ = _client(
        event_debug_query_compat_stale_after_seconds=30,
    )

    body = client.get("/health").json()
    assert body["runtime_policy"]["event_debug_query_compat_stale_after_seconds"] == 30
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_age_seconds"] is None
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "no_attempts_recorded"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "no_attempts_observed"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "can_disable_when_ready"


def test_health_endpoint_marks_query_compat_activity_as_stale_when_last_attempt_is_older_than_threshold() -> None:
    client, _, _ = _client(
        event_debug_query_compat_stale_after_seconds=1,
    )

    response = client.post("/event?debug=true", json={"text": "debug stale posture"})
    assert response.status_code == 200
    sleep(1.1)

    body = client.get("/health").json()
    assert body["runtime_policy"]["event_debug_query_compat_last_attempt_state"] == "stale"
    assert body["runtime_policy"]["event_debug_query_compat_activity_state"] == "stale_historical_attempts"
    assert body["runtime_policy"]["event_debug_query_compat_activity_hint"] == "verify_stale_clients_before_disable"


def test_event_debug_endpoint_allows_debug_payload_when_debug_token_matches() -> None:
    client, runtime, _ = _client(event_debug_enabled=True, event_debug_token="debug-secret")

    response = client.post(
        "/event/debug",
        json={"text": "show debug runtime"},
        headers={"X-AION-Debug-Token": "debug-secret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "debug" in body
    assert body["debug"]["expression"]["message"] == "Test reply"
    assert (
        response.headers["x-aion-debug-shared-compat"]
        == "shared_debug_route_is_compatibility_use_internal_event_debug"
    )
    assert response.headers["x-aion-debug-shared-compat-deprecated"] == "true"
    assert response.headers["x-aion-debug-shared-mode"] == "compatibility"
    assert response.headers["x-aion-debug-shared-posture"] == "transitional_compatibility"
    assert "x-aion-debug-shared-break-glass-used" not in response.headers
    assert runtime.last_event is not None


def test_event_endpoint_rejects_debug_payload_when_debug_mode_is_disabled() -> None:
    client, runtime, _ = _client(event_debug_enabled=False)

    response = client.post("/event?debug=true", json={"text": "show debug runtime"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Debug payload is disabled for this environment."
    assert runtime.last_event is None


def test_event_debug_endpoint_rejects_debug_payload_when_debug_mode_is_disabled() -> None:
    client, runtime, _ = _client(event_debug_enabled=False)

    response = client.post("/event/debug", json={"text": "show debug runtime"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Debug payload is disabled for this environment."
    assert runtime.last_event is None


def test_event_endpoint_contract_smoke_pins_public_shape_and_debug_gate() -> None:
    client, _, _ = _client()

    response = client.post("/event", json={"text": "contract smoke"})

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"event_id", "trace_id", "source", "reply", "runtime"}
    assert set(body["reply"].keys()) == {"message", "language", "tone", "channel"}
    assert set(body["runtime"].keys()) == {"role", "motivation_mode", "action_status", "reflection_triggered"}
    assert "debug" not in body

    debug_response = client.post("/event?debug=true", json={"text": "contract smoke debug"})

    assert debug_response.status_code == 200
    debug_body = debug_response.json()
    assert "debug" in debug_body
    assert "system_debug" in debug_body
    assert "event" in debug_body["debug"]
    assert "stage_timings_ms" in debug_body["debug"]
    assert debug_response.headers["x-aion-debug-compat"] == "query_debug_route_is_compatibility_use_internal_event_debug"


def test_event_debug_endpoint_exposes_system_debug_behavior_contract() -> None:
    client, _, _ = _client()

    debug_response = client.post("/internal/event/debug", json={"text": "system debug contract"})

    assert debug_response.status_code == 200
    body = debug_response.json()
    assert "system_debug" in body
    system_debug = body["system_debug"]
    assert system_debug["mode"] == "system_debug"
    assert system_debug["event"]["event_id"] == body["event_id"]
    assert system_debug["event"]["trace_id"] == body["trace_id"]
    assert set(system_debug["memory_bundle"].keys()) == {"episodic", "semantic", "affective", "relations", "diagnostics"}
    assert set(system_debug["plan"].keys()) == {"goal", "steps", "needs_action", "needs_response", "domain_intents"}
    assert system_debug["action_result"]["status"] == "success"
    assert "x-aion-debug-shared-compat" not in debug_response.headers


def test_event_endpoint_debug_payload_pins_foreground_boundary_stage_order() -> None:
    client, _, _ = _client()

    debug_response = client.post("/event?debug=true", json={"text": "foreground boundary parity"})

    assert debug_response.status_code == 200
    debug_body = debug_response.json()
    stage_timings = debug_body["debug"]["stage_timings_ms"]
    stage_order = list(stage_timings.keys())

    assert stage_order.index("memory_load") < stage_order.index("perception")
    assert stage_order.index("task_load") < stage_order.index("perception")
    assert stage_order.index("goal_milestone_load") < stage_order.index("perception")
    assert stage_order.index("identity_load") < stage_order.index("perception")
    assert stage_order.index("perception") < stage_order.index("affective_assessment")
    assert stage_order.index("affective_assessment") < stage_order.index("context")
    assert stage_order.index("expression") < stage_order.index("action")
    assert stage_order.index("action") < stage_order.index("memory_persist")
    assert stage_order.index("memory_persist") < stage_order.index("reflection_enqueue")
    assert stage_order.index("reflection_enqueue") < stage_order.index("state_refresh")
    assert stage_order[-1] == "total"


def test_event_endpoint_exposes_reflection_trigger_when_runtime_queues_reflection() -> None:
    client, runtime, _ = _client(reflection_triggered=True)

    response = client.post("/event", json={"text": "trigger reflection"})

    assert response.status_code == 200
    body = response.json()
    assert body["runtime"]["reflection_triggered"] is True
    assert body["runtime"]["action_status"] == "success"
    assert body["runtime"]["motivation_mode"] == "respond"
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "trigger reflection"


def test_event_endpoint_coalesces_rapid_telegram_messages_into_single_runtime_turn() -> None:
    client, runtime, _ = _client(attention_burst_window_ms=160)
    first_response: dict[str, object] = {}

    def _first_call() -> None:
        first_response["value"] = client.post("/event", json=_telegram_update(1001, "first burst message"))

    thread = Thread(target=_first_call)
    thread.start()
    sleep(0.05)
    second = client.post("/event", json=_telegram_update(1002, " second   burst    message "))
    thread.join(timeout=2.0)

    assert "value" in first_response
    first = first_response["value"]
    assert isinstance(first, type(second))
    assert first.status_code == 200
    assert second.status_code == 200

    second_body = second.json()
    assert second_body["queue"] == {
        "queued": True,
        "reason": "coalesced_into_pending_turn",
        "turn_id": second_body["queue"]["turn_id"],
        "source_count": 2,
    }

    assert len(runtime.events) == 1
    assembled = runtime.events[0]
    assert assembled.payload["text"] == "first burst message\nsecond burst message"
    assert assembled.payload["turn_status"] == "claimed"
    assert assembled.payload["turn_source_count"] == 2
    assert len(assembled.payload["coalesced_event_ids"]) == 2


def test_event_endpoint_ignores_duplicate_telegram_update_during_pending_turn() -> None:
    client, runtime, _ = _client(attention_burst_window_ms=160)
    first_response: dict[str, object] = {}

    def _first_call() -> None:
        first_response["value"] = client.post("/event", json=_telegram_update(2001, "first payload"))

    thread = Thread(target=_first_call)
    thread.start()
    sleep(0.05)
    duplicate = client.post("/event", json=_telegram_update(2001, "duplicate payload"))
    thread.join(timeout=2.0)

    assert "value" in first_response
    assert duplicate.status_code == 200
    duplicate_body = duplicate.json()
    assert duplicate_body["queue"] == {
        "queued": True,
        "reason": "duplicate_update",
        "turn_id": duplicate_body["queue"]["turn_id"],
        "source_count": 1,
    }
    assert len(runtime.events) == 1
    assert runtime.events[0].payload["text"] == "first payload"


def test_event_endpoint_blocks_second_runtime_run_when_turn_is_already_claimed() -> None:
    client, runtime, _ = _client(
        attention_burst_window_ms=40,
        run_delay_seconds=0.25,
    )
    first_response: dict[str, object] = {}

    def _first_call() -> None:
        first_response["value"] = client.post("/event", json=_telegram_update(3001, "first message"))

    thread = Thread(target=_first_call)
    thread.start()
    sleep(0.12)
    claimed = client.post("/event", json=_telegram_update(3002, "second message while claimed"))
    thread.join(timeout=3.0)

    assert "value" in first_response
    assert claimed.status_code == 200
    claimed_body = claimed.json()
    assert claimed_body["queue"] == {
        "queued": True,
        "reason": "turn_already_claimed",
        "turn_id": claimed_body["queue"]["turn_id"],
        "source_count": 1,
    }
    assert len(runtime.events) == 1
    assert runtime.events[0].payload["text"] == "first message"

    next_turn = client.post("/event", json=_telegram_update(3003, "next turn after answer"))
    assert next_turn.status_code == 200
    assert len(runtime.events) == 2
    assert runtime.events[1].payload["text"] == "next turn after answer"


def test_event_endpoint_rejects_telegram_payload_with_wrong_secret() -> None:
    client, runtime, _ = _client(secret="expected-secret")

    response = client.post(
        "/event",
        json=_telegram_update(1, "ping"),
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid Telegram webhook secret token."
    assert runtime.last_event is None


def test_set_webhook_uses_request_secret_or_settings_default() -> None:
    client, _, telegram_client = _client(secret="fallback-secret")

    response = client.post(
        "/telegram/set-webhook",
        json={"webhook_url": "https://personality.luckysparrow.ch/event"},
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True, "result": True}
    assert telegram_client.calls == [
        {
            "webhook_url": "https://personality.luckysparrow.ch/event",
            "secret_token": "fallback-secret",
        }
    ]
