from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.api.schemas import EventQueueResponse, EventResponse, EventReplyResponse, EventRuntimeResponse, SetWebhookRequest
from app.core.attention import (
    AttentionTurnCoordinator,
    attention_coordination_readiness_snapshot,
    attention_timing_policy_snapshot,
)
from app.core.api_readiness_policy import api_readiness_policy_snapshot
from app.core.debug_compat import (
    DebugQueryCompatTelemetry,
    debug_query_compat_activity_snapshot,
    debug_query_compat_freshness_snapshot,
    debug_query_compat_recent_snapshot,
    debug_query_compat_sunset_snapshot,
)
from app.core.events import looks_like_telegram_update, normalize_event
from app.core.background_adaptive_outputs import summarize_loaded_adaptive_state
from app.core.identity_policy import identity_policy_snapshot
from app.core.learned_state_policy import learned_state_policy_snapshot
from app.core.adaptive_governance import adaptive_identity_governance_snapshot
from app.core.affective_diagnostics import affective_input_policy_snapshot
from app.core.affective_policy import affective_assessment_policy_snapshot
from app.core.background_worker_policy import (
    reflection_external_driver_policy_snapshot,
)
from app.core.reflection_supervision_policy import (
    reflection_supervision_policy_snapshot,
)
from app.core.connector_policy import (
    connector_authorization_matrix_snapshot,
    connector_capability_proposal_snapshot,
)
from app.core.connector_execution import (
    connector_execution_baseline_snapshot,
    organizer_tool_stack_snapshot,
)
from app.core.deployment_policy import deployment_policy_snapshot
from app.core.external_scheduler_policy import external_scheduler_policy_snapshot
from app.core.observability_policy import observability_export_policy_snapshot
from app.core.observability_policy import build_runtime_incident_evidence
from app.core.planning_governance import planning_governance_snapshot
from app.core.proactive_policy import proactive_runtime_policy_snapshot
from app.core.role_skill_policy import role_skill_policy_snapshot
from app.core.skill_registry import skill_registry_snapshot
from app.core.v1_readiness_policy import v1_readiness_policy_snapshot
from app.core.web_knowledge_policy import web_knowledge_tooling_snapshot
from app.core.runtime_policy import (
    app_environment,
    event_debug_enabled,
    event_debug_query_compat_enabled,
    event_debug_shared_ingress_mode,
    event_debug_shared_ingress_posture,
    event_debug_token_required,
    production_debug_token_required,
    release_readiness_snapshot,
    runtime_policy_snapshot,
)
from app.core.runtime import RuntimeOrchestrator
from app.core.retrieval_policy import retrieval_depth_policy_snapshot
from app.core.scheduler_contracts import (
    normalize_scheduler_execution_mode,
    reflection_deployment_readiness_snapshot,
    reflection_topology_handoff_posture,
    scheduler_cadence_execution_snapshot,
)
from app.core.topology_policy import runtime_topology_policy_snapshot
from app.integrations.telegram.client import TelegramClient
from app.integrations.telegram.telemetry import TelegramChannelTelemetry
from app.memory.embeddings import embedding_strategy_snapshot, normalize_embedding_source_kinds
from app.memory.repository import MemoryRepository
from app.reflection.worker import ReflectionWorker
from app.utils.language import language_continuity_policy_snapshot
from app.workers.scheduler import SchedulerWorker

router = APIRouter()
DEBUG_INTERNAL_INGRESS_PATH = "/internal/event/debug"
DEBUG_COMPAT_HINT_HEADER = "X-AION-Debug-Compat"
DEBUG_COMPAT_HINT_VALUE = "query_debug_route_is_compatibility_use_internal_event_debug"
DEBUG_COMPAT_LINK_VALUE = f"<{DEBUG_INTERNAL_INGRESS_PATH}>; rel=\"alternate\""
DEBUG_COMPAT_DEPRECATED_HEADER = "X-AION-Debug-Compat-Deprecated"
DEBUG_COMPAT_DEPRECATED_VALUE = "true"
DEBUG_SHARED_COMPAT_HINT_HEADER = "X-AION-Debug-Shared-Compat"
DEBUG_SHARED_COMPAT_HINT_VALUE = "shared_debug_route_is_compatibility_use_internal_event_debug"
DEBUG_SHARED_COMPAT_DEPRECATED_HEADER = "X-AION-Debug-Shared-Compat-Deprecated"
DEBUG_SHARED_COMPAT_DEPRECATED_VALUE = "true"
DEBUG_SHARED_MODE_HEADER = "X-AION-Debug-Shared-Mode"
DEBUG_SHARED_POSTURE_HEADER = "X-AION-Debug-Shared-Posture"
DEBUG_SHARED_BREAK_GLASS_HEADER = "X-AION-Debug-Break-Glass"
DEBUG_SHARED_BREAK_GLASS_USED_HEADER = "X-AION-Debug-Shared-Break-Glass-Used"


def _runtime_from_request(request: Request) -> RuntimeOrchestrator:
    return request.app.state.runtime  # type: ignore[return-value]


def _telegram_from_request(request: Request) -> TelegramClient:
    return request.app.state.telegram_client  # type: ignore[return-value]


def _settings_from_request(request: Request):
    return request.app.state.settings


def _telegram_telemetry_from_request(request: Request) -> TelegramChannelTelemetry:
    telemetry = getattr(request.app.state, "telegram_channel_telemetry", None)
    if isinstance(telemetry, TelegramChannelTelemetry):
        return telemetry
    telemetry = TelegramChannelTelemetry()
    request.app.state.telegram_channel_telemetry = telemetry
    return telemetry


def _memory_repository_from_request(request: Request) -> MemoryRepository:
    return request.app.state.memory_repository  # type: ignore[return-value]


def _reflection_worker_from_request(request: Request) -> ReflectionWorker:
    return request.app.state.reflection_worker  # type: ignore[return-value]


def _scheduler_worker_from_request(request: Request) -> SchedulerWorker | None:
    return getattr(request.app.state, "scheduler_worker", None)


def _attention_coordinator_from_request(request: Request) -> AttentionTurnCoordinator:
    coordinator = getattr(request.app.state, "attention_turn_coordinator", None)
    if isinstance(coordinator, AttentionTurnCoordinator):
        return coordinator
    settings = _settings_from_request(request)
    coordinator = AttentionTurnCoordinator(
        burst_window_ms=int(getattr(settings, "attention_burst_window_ms", 120)),
        answered_ttl_seconds=float(getattr(settings, "attention_answered_ttl_seconds", 5.0)),
        stale_turn_seconds=float(getattr(settings, "attention_stale_turn_seconds", 30.0)),
        coordination_mode=str(getattr(settings, "attention_coordination_mode", "in_process")),
        memory_repository=_memory_repository_from_request(request),
    )
    request.app.state.attention_turn_coordinator = coordinator
    return coordinator


async def _attention_snapshot_from_request(request: Request) -> dict[str, Any]:
    coordinator = _attention_coordinator_from_request(request)
    snapshot = await coordinator.snapshot()
    burst_window_ms = int(round(coordinator.burst_window_seconds * 1000))
    answered_ttl_seconds = float(coordinator.answered_ttl_seconds)
    stale_turn_seconds = float(coordinator.stale_turn_seconds)
    readiness = attention_coordination_readiness_snapshot(
        coordination_mode=coordinator.coordination_mode,
        pending=int(snapshot.get("pending", 0)),
        claimed=int(snapshot.get("claimed", 0)),
        store_available=bool(
            snapshot.get("contract_store_mode") == "repository_backed"
            or coordinator.coordination_mode != "durable_inbox"
        ),
        stale_cleanup_candidates=int(snapshot.get("stale_cleanup_candidates", 0)),
        answered_cleanup_candidates=int(snapshot.get("answered_cleanup_candidates", 0)),
    )
    timing_policy = attention_timing_policy_snapshot(
        burst_window_ms=burst_window_ms,
        answered_ttl_seconds=answered_ttl_seconds,
        stale_turn_seconds=stale_turn_seconds,
    )
    return {
        "attention_policy_owner": "durable_attention_inbox_policy",
        "healthy": bool(readiness["ready"]),
        "coordination_mode": str(readiness["selected_coordination_mode"]),
        "turn_state_owner": str(readiness["turn_state_owner"]),
        "durable_inbox_expected": bool(readiness["durable_inbox_expected"]),
        "persistence_owner": str(readiness["persistence_owner"]),
        "parity_state": str(readiness["parity_state"]),
        "deployment_readiness": readiness,
        "timing_policy": timing_policy,
        "burst_window_ms": burst_window_ms,
        "answered_ttl_seconds": answered_ttl_seconds,
        "stale_turn_seconds": stale_turn_seconds,
        **snapshot,
    }


async def _scheduler_cadence_evidence_from_request(request: Request) -> dict[str, dict[str, Any]]:
    memory_repository = _memory_repository_from_request(request)
    loader = getattr(memory_repository, "get_scheduler_cadence_evidence", None)
    if not callable(loader):
        return {}

    maintenance = await loader(cadence_kind="maintenance")
    proactive = await loader(cadence_kind="proactive")
    snapshot: dict[str, dict[str, Any]] = {}
    if isinstance(maintenance, dict):
        snapshot["maintenance"] = maintenance
    if isinstance(proactive, dict):
        snapshot["proactive"] = proactive
    return snapshot


def _memory_retrieval_snapshot_from_settings(settings) -> dict[str, Any]:
    snapshot = embedding_strategy_snapshot(
        semantic_vector_enabled=bool(getattr(settings, "semantic_vector_enabled", True)),
        provider=str(getattr(settings, "embedding_provider", "deterministic")),
        model=str(getattr(settings, "embedding_model", "deterministic-v1")),
        dimensions=max(1, int(getattr(settings, "embedding_dimensions", 32))),
        source_kinds=normalize_embedding_source_kinds(
            str(getattr(settings, "embedding_source_kinds", "episodic,semantic,affective"))
        ),
        refresh_mode=str(getattr(settings, "embedding_refresh_mode", "on_write")),
        refresh_interval_seconds=int(getattr(settings, "embedding_refresh_interval_seconds", 21600)),
        provider_ownership_enforcement=str(
            getattr(settings, "embedding_provider_ownership_enforcement", "warn")
        ),
        model_governance_enforcement=str(
            getattr(settings, "embedding_model_governance_enforcement", "warn")
        ),
        source_rollout_enforcement=str(
            getattr(settings, "embedding_source_rollout_enforcement", "warn")
        ),
        openai_api_key=str(getattr(settings, "openai_api_key", "") or ""),
    )
    snapshot["retrieval_depth_policy"] = retrieval_depth_policy_snapshot(
        episodic_limit=RuntimeOrchestrator.MEMORY_LOAD_LIMIT,
        conclusion_limit=8,
        semantic_vector_enabled=bool(getattr(settings, "semantic_vector_enabled", True)),
    )
    return snapshot


async def _incident_evidence_from_request(
    *,
    request: Request,
    result,
) -> dict[str, Any]:
    settings = _settings_from_request(request)
    reflection_worker = _reflection_worker_from_request(request)
    scheduler_worker = _scheduler_worker_from_request(request)
    memory_repository = _memory_repository_from_request(request)
    runtime_policy = runtime_policy_snapshot(settings)
    memory_retrieval = _memory_retrieval_snapshot_from_settings(settings)
    attention_snapshot = await _attention_snapshot_from_request(request)
    scheduler_execution_mode = normalize_scheduler_execution_mode(
        str(getattr(settings, "scheduler_execution_mode", "in_process") or "in_process")
    )
    scheduler_snapshot = scheduler_worker.snapshot() if scheduler_worker is not None else {}
    cadence_evidence = await _scheduler_cadence_evidence_from_request(request)
    maintenance_evidence = cadence_evidence.get("maintenance", {})
    proactive_evidence = cadence_evidence.get("proactive", {})
    scheduler_external_owner_policy = external_scheduler_policy_snapshot(
        scheduler_execution_mode=str(
            scheduler_snapshot.get("execution_mode", scheduler_execution_mode)
        ),
        scheduler_running=bool(scheduler_snapshot.get("running", False)),
        maintenance_last_run_at=maintenance_evidence.get("last_run_at")
        or scheduler_snapshot.get("last_maintenance_tick_at"),
        maintenance_last_summary=maintenance_evidence.get("summary")
        or scheduler_snapshot.get("last_maintenance_summary", {}),
        maintenance_interval_seconds=int(scheduler_snapshot.get("maintenance_interval_seconds", 3600)),
        proactive_enabled=bool(scheduler_snapshot.get("proactive_enabled", False)),
        proactive_last_run_at=proactive_evidence.get("last_run_at")
        or scheduler_snapshot.get("last_proactive_tick_at"),
        proactive_last_summary=proactive_evidence.get("summary")
        or scheduler_snapshot.get("last_proactive_summary", {}),
        proactive_interval_seconds=int(scheduler_snapshot.get("proactive_interval_seconds", 1800)),
    )
    reflection_snapshot = reflection_worker.snapshot()
    reflection_stats = await memory_repository.get_reflection_task_stats(
        max_attempts=int(reflection_snapshot["max_attempts"]),
        stuck_after_seconds=int(reflection_snapshot["stuck_processing_seconds"]),
        retry_backoff_seconds=tuple(int(value) for value in reflection_snapshot["retry_backoff_seconds"]),  # type: ignore[arg-type]
    )
    reflection_supervision = reflection_supervision_policy_snapshot(
        reflection_runtime_mode=str(getattr(settings, "reflection_runtime_mode", "in_process") or "in_process"),
        scheduler_execution_mode=str(
            scheduler_snapshot.get("execution_mode", scheduler_execution_mode)
        ),
        worker_running=bool(reflection_snapshot["running"]),
        task_stats=reflection_stats,
    )
    reflection_topology = reflection_topology_handoff_posture(
        runtime_mode=str(getattr(settings, "reflection_runtime_mode", "in_process") or "in_process"),
        worker_running=bool(reflection_snapshot["running"]),
    )
    reflection_readiness = reflection_deployment_readiness_snapshot(
        runtime_mode=str(getattr(settings, "reflection_runtime_mode", "in_process") or "in_process"),
        topology=reflection_topology,
        worker_running=bool(reflection_snapshot["running"]),
        task_stats=reflection_stats,
    )
    runtime_topology = runtime_topology_policy_snapshot(
        reflection_runtime_mode=str(getattr(settings, "reflection_runtime_mode", "in_process") or "in_process"),
        reflection_readiness=reflection_readiness,
        attention_snapshot=attention_snapshot,
    )
    connectors_execution_baseline = connector_execution_baseline_snapshot(settings)
    telegram_conversation_channel = _telegram_telemetry_from_request(request).snapshot(
        bot_token_configured=bool(getattr(settings, "telegram_bot_token", "")),
        webhook_secret_configured=bool(getattr(settings, "telegram_webhook_secret", "")),
    )
    learned_state = learned_state_policy_snapshot()
    role_skill_policy = role_skill_policy_snapshot()
    return build_runtime_incident_evidence(
        trace_id=result.event.meta.trace_id,
        event_id=result.event.event_id,
        source=result.event.source,
        duration_ms=result.duration_ms,
        stage_timings_ms=result.stage_timings_ms,
        runtime_policy=runtime_policy,
        memory_retrieval=memory_retrieval,
        learned_state=learned_state,
        v1_readiness=v1_readiness_policy_snapshot(
            telegram_conversation_channel=telegram_conversation_channel,
            learned_state=learned_state,
            role_skill_policy=role_skill_policy,
        ),
        attention=attention_snapshot,
        runtime_topology_attention_switch=dict(runtime_topology.get("attention_switch", {})),
        proactive=proactive_runtime_policy_snapshot(
            proactive_enabled=bool(getattr(settings, "proactive_enabled", False)),
            proactive_interval_seconds=int(getattr(settings, "proactive_interval", 1800)),
            scheduler_execution_mode=str(
                scheduler_snapshot.get("execution_mode", scheduler_execution_mode)
            ),
            scheduler_ready=bool(
                scheduler_external_owner_policy.get("production_baseline_ready", False)
            ),
            scheduler_running=bool(scheduler_snapshot.get("running", False)),
        ),
        scheduler_external_owner_policy=scheduler_external_owner_policy,
        reflection_supervision=reflection_supervision,
        connectors_execution_baseline=connectors_execution_baseline,
        telegram_conversation_channel=telegram_conversation_channel,
    )


def _debug_query_compat_telemetry_from_request(request: Request) -> DebugQueryCompatTelemetry:
    telemetry = getattr(request.app.state, "debug_query_compat_telemetry", None)
    if isinstance(telemetry, DebugQueryCompatTelemetry):
        return telemetry
    settings = getattr(request.app.state, "settings", None)
    recent_window_size = int(getattr(settings, "event_debug_query_compat_recent_window", 20))
    telemetry = DebugQueryCompatTelemetry(recent_window_size=recent_window_size)
    request.app.state.debug_query_compat_telemetry = telemetry
    return telemetry


def _enforce_debug_access(*, request: Request, settings) -> None:
    if not event_debug_enabled(settings):
        raise HTTPException(status_code=403, detail="Debug payload is disabled for this environment.")
    if event_debug_token_required(settings):
        received_debug_token = request.headers.get("X-AION-Debug-Token")
        expected_debug_token = str(getattr(settings, "event_debug_token", "") or "")
        if received_debug_token != expected_debug_token:
            raise HTTPException(status_code=403, detail="Invalid debug token.")
        return
    if app_environment(settings) == "production" and production_debug_token_required(settings):
        raise HTTPException(status_code=403, detail="Debug token is required in production.")


async def _build_learned_state_snapshot(*, request: Request, user_id: str) -> dict[str, Any]:
    memory_repository = _memory_repository_from_request(request)
    profile = await memory_repository.get_user_profile(user_id=user_id)
    preferences = await memory_repository.get_user_runtime_preferences(user_id=user_id)
    conclusions = await memory_repository.get_user_conclusions(user_id=user_id, limit=24)
    relations = await memory_repository.get_user_relations(user_id=user_id, limit=12)
    active_goals = await memory_repository.get_active_goals(user_id=user_id, limit=8)
    goal_ids = [int(goal["id"]) for goal in active_goals if goal.get("id") is not None]
    active_tasks = await memory_repository.get_active_tasks(user_id=user_id, goal_ids=goal_ids, limit=12)
    active_goal_milestones = await memory_repository.get_active_goal_milestones(
        user_id=user_id,
        goal_ids=goal_ids,
        limit=8,
    )
    pending_proposals = await memory_repository.get_pending_subconscious_proposals(
        user_id=user_id,
        limit=8,
    )
    theta_loader = getattr(memory_repository, "get_user_theta", None)
    theta = await theta_loader(user_id=user_id) if callable(theta_loader) else None
    adaptive_outputs = summarize_loaded_adaptive_state(
        user_conclusions=conclusions,
        relations=relations,
        theta=theta if isinstance(theta, dict) else None,
    )

    preference_kinds = {
        "response_style",
        "collaboration_preference",
        "preferred_role",
        "proactive_opt_in",
    }
    affective_kinds = {
        "affective_support_pattern",
        "affective_support_sensitivity",
    }
    learned_preferences = {
        key: value
        for key, value in {
            "preferred_language": (profile or {}).get("preferred_language") if isinstance(profile, dict) else None,
            "response_style": preferences.get("response_style"),
            "collaboration_preference": preferences.get("collaboration_preference"),
            "preferred_role": preferences.get("preferred_role"),
            "proactive_opt_in": preferences.get("proactive_opt_in"),
        }.items()
        if value not in {None, ""}
    }
    semantic_conclusions = [
        row
        for row in conclusions
        if str(row.get("kind", "")).strip().lower() not in preference_kinds.union(affective_kinds)
    ]
    affective_conclusions = [
        row for row in conclusions if str(row.get("kind", "")).strip().lower() in affective_kinds
    ]
    relation_types = sorted(
        {
            str(row.get("relation_type", "")).strip().lower()
            for row in relations
            if str(row.get("relation_type", "")).strip()
        }
    )
    semantic_conclusion_kinds = sorted(
        {
            str(row.get("kind", "")).strip().lower()
            for row in semantic_conclusions
            if str(row.get("kind", "")).strip()
        }
    )
    affective_conclusion_kinds = sorted(
        {
            str(row.get("kind", "")).strip().lower()
            for row in affective_conclusions
            if str(row.get("kind", "")).strip()
        }
    )
    skill_registry = skill_registry_snapshot()
    role_skill_policy = role_skill_policy_snapshot()
    planning_continuity_summary = {
        "active_goal_count": len(active_goals),
        "active_task_count": len(active_tasks),
        "blocked_task_count": sum(1 for row in active_tasks if str(row.get("status", "")).strip().lower() == "blocked"),
        "active_milestone_count": len(active_goal_milestones),
        "pending_proposal_count": len(pending_proposals),
        "primary_goal_names": [
            str(row.get("name", "")).strip()
            for row in active_goals[:3]
            if str(row.get("name", "")).strip()
        ],
        "primary_task_names": [
            str(row.get("name", "")).strip()
            for row in active_tasks[:5]
            if str(row.get("name", "")).strip()
        ],
    }
    learned_knowledge_summary = {
        "semantic_conclusion_count": len(semantic_conclusions),
        "semantic_conclusion_kinds": semantic_conclusion_kinds,
        "affective_conclusion_count": len(affective_conclusions),
        "affective_conclusion_kinds": affective_conclusion_kinds,
        "relation_count": len(relations),
        "relation_types": relation_types,
        "adaptive_output_keys": sorted(str(key) for key in adaptive_outputs.keys()),
        "theta_present": bool(theta),
    }
    preference_summary = {
        "learned_preference_count": len(learned_preferences),
        "learned_preference_keys": sorted(str(key) for key in learned_preferences.keys()),
        "preferred_language_present": "preferred_language" in learned_preferences,
        "preferred_role_present": "preferred_role" in learned_preferences,
        "proactive_opt_in_present": "proactive_opt_in" in learned_preferences,
    }
    selection_visibility_summary = {
        "current_turn_selected_role_available_via": "system_debug.role",
        "current_turn_selected_skills_available_via": "system_debug.adaptive_state.selected_skills",
        "catalog_skill_count": int(skill_registry.get("catalog_count", 0)),
        "catalog_skill_ids": [
            str(item.get("skill_id", "")).strip()
            for item in skill_registry.get("catalog", [])
            if isinstance(item, dict) and str(item.get("skill_id", "")).strip()
        ],
        "metadata_only_skill_boundary": True,
        "work_partner_role_available": bool(role_skill_policy.get("work_partner_role_available", False)),
    }

    return {
        **learned_state_policy_snapshot(),
        "api_readiness": api_readiness_policy_snapshot(),
        "user_id": user_id,
        "identity_state": {
            "identity_policy": identity_policy_snapshot(),
            "profile": dict(profile or {}) if isinstance(profile, dict) else {},
            "learned_preferences": learned_preferences,
            "preference_summary": preference_summary,
        },
        "learned_knowledge": {
            "semantic_conclusions": semantic_conclusions,
            "affective_conclusions": affective_conclusions,
            "relations": relations,
            "adaptive_outputs": adaptive_outputs,
            "theta": dict(theta) if isinstance(theta, dict) else {},
            "knowledge_summary": learned_knowledge_summary,
            "reflection_growth_summary": {
                "adaptive_output_keys": learned_knowledge_summary["adaptive_output_keys"],
                "reflection_backed_semantic_growth": bool(semantic_conclusions),
                "reflection_backed_affective_growth": bool(affective_conclusions),
                "relation_signal_types": relation_types,
            },
        },
        "role_skill_state": {
            "role_skill_policy": role_skill_policy,
            "skill_registry": skill_registry,
            "selection_visibility_summary": selection_visibility_summary,
        },
        "planning_state": {
            "active_goals": active_goals,
            "active_tasks": active_tasks,
            "active_goal_milestones": active_goal_milestones,
            "pending_proposals": pending_proposals,
            "continuity_summary": planning_continuity_summary,
        },
    }


async def _handle_event_request(
    *,
    payload: dict[str, Any],
    request: Request,
    include_debug: bool,
) -> dict[str, Any]:
    settings = _settings_from_request(request)
    looks_like_telegram = looks_like_telegram_update(payload)
    telegram_update_id = payload.get("update_id") if looks_like_telegram else None
    telegram_chat_id = None
    if looks_like_telegram:
        telegram_chat_id = ((payload.get("message") or {}).get("chat") or {}).get("id")
        _telegram_telemetry_from_request(request).record_ingress_attempt(
            update_id=telegram_update_id,
            chat_id=telegram_chat_id,
        )
    if looks_like_telegram and settings.telegram_webhook_secret:
        received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if received_secret != settings.telegram_webhook_secret:
            _telegram_telemetry_from_request(request).record_ingress_rejection(
                reason="invalid_webhook_secret",
                update_id=telegram_update_id,
                chat_id=telegram_chat_id,
            )
            raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret token.")
    if include_debug:
        _enforce_debug_access(request=request, settings=settings)

    event = normalize_event(
        payload,
        default_user_id=request.headers.get("X-AION-User-Id"),
    )
    attention_coordinator = _attention_coordinator_from_request(request)
    turn_decision = await attention_coordinator.prepare_event(event)
    if not turn_decision.should_process:
        queue_reason = turn_decision.queue_reason or "queued"
        if looks_like_telegram:
            _telegram_telemetry_from_request(request).record_ingress_queued(
                reason=queue_reason,
                update_id=telegram_update_id,
                chat_id=telegram_chat_id,
                source_count=turn_decision.source_count,
            )
        queued_response = EventResponse(
            event_id=turn_decision.event.event_id,
            trace_id=turn_decision.event.meta.trace_id,
            source=turn_decision.event.source,
            queue=EventQueueResponse(
                queued=True,
                reason=queue_reason,
                turn_id=turn_decision.turn_id,
                source_count=turn_decision.source_count,
            ),
        )
        return queued_response.model_dump(mode="json", exclude_none=True)

    runtime_event = turn_decision.event
    runtime = _runtime_from_request(request)
    try:
        try:
            result = await runtime.run(runtime_event)
        except Exception as exc:
            if looks_like_telegram:
                _telegram_telemetry_from_request(request).record_ingress_runtime_failure(
                    reason=f"runtime_exception:{type(exc).__name__}",
                    update_id=telegram_update_id,
                    chat_id=telegram_chat_id,
                )
            raise
    finally:
        await attention_coordinator.finalize_event(runtime_event)

    if looks_like_telegram:
        _telegram_telemetry_from_request(request).record_ingress_processed(
            update_id=telegram_update_id,
            chat_id=telegram_chat_id,
            action_status=result.action_result.status,
            reflection_triggered=result.reflection_triggered,
        )

    incident_evidence = None
    if include_debug:
        incident_evidence = await _incident_evidence_from_request(
            request=request,
            result=result,
        )

    response = EventResponse(
        event_id=result.event.event_id,
        trace_id=result.event.meta.trace_id,
        source=result.event.source,
        reply=EventReplyResponse(
            message=result.expression.message,
            language=result.expression.language,
            tone=result.expression.tone,
            channel=result.expression.channel,
        ),
        runtime=EventRuntimeResponse(
            role=result.role.selected,
            motivation_mode=result.motivation.mode,
            action_status=result.action_result.status,
            reflection_triggered=result.reflection_triggered,
        ),
        debug=result if include_debug else None,
        system_debug=result.system_debug if include_debug else None,
        incident_evidence=incident_evidence,
    )
    return response.model_dump(mode="json", exclude_none=True)


async def _handle_internal_debug_ingress(
    *,
    payload: dict[str, Any],
    request: Request,
) -> dict[str, Any]:
    return await _handle_event_request(
        payload=payload,
        request=request,
        include_debug=True,
    )


def _mark_query_debug_compat_headers(response: Response) -> None:
    response.headers[DEBUG_COMPAT_HINT_HEADER] = DEBUG_COMPAT_HINT_VALUE
    response.headers["Link"] = DEBUG_COMPAT_LINK_VALUE
    response.headers[DEBUG_COMPAT_DEPRECATED_HEADER] = DEBUG_COMPAT_DEPRECATED_VALUE


def _is_break_glass_override_request(request: Request) -> bool:
    value = str(request.headers.get(DEBUG_SHARED_BREAK_GLASS_HEADER, "") or "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _enforce_shared_debug_ingress_policy(*, request: Request, settings) -> bool:
    shared_mode = event_debug_shared_ingress_mode(settings)
    if shared_mode != "break_glass_only":
        return False
    if _is_break_glass_override_request(request):
        return True
    raise HTTPException(
        status_code=403,
        detail=(
            "Shared debug ingress is in break-glass-only mode. "
            f"Set {DEBUG_SHARED_BREAK_GLASS_HEADER}: true or use POST {DEBUG_INTERNAL_INGRESS_PATH}."
        ),
    )


def _mark_shared_debug_compat_headers(*, response: Response, settings, break_glass_used: bool) -> None:
    response.headers[DEBUG_SHARED_COMPAT_HINT_HEADER] = DEBUG_SHARED_COMPAT_HINT_VALUE
    response.headers["Link"] = DEBUG_COMPAT_LINK_VALUE
    response.headers[DEBUG_SHARED_COMPAT_DEPRECATED_HEADER] = DEBUG_SHARED_COMPAT_DEPRECATED_VALUE
    response.headers[DEBUG_SHARED_MODE_HEADER] = event_debug_shared_ingress_mode(settings)
    response.headers[DEBUG_SHARED_POSTURE_HEADER] = event_debug_shared_ingress_posture(settings)
    if break_glass_used:
        response.headers[DEBUG_SHARED_BREAK_GLASS_USED_HEADER] = "true"


@router.get("/health")
async def health(request: Request) -> dict[str, Any]:
    settings = _settings_from_request(request)
    reflection_worker = _reflection_worker_from_request(request)
    scheduler_worker = _scheduler_worker_from_request(request)
    reflection_runtime_mode = str(getattr(settings, "reflection_runtime_mode", "in_process") or "in_process")
    memory_repository = _memory_repository_from_request(request)
    runtime_policy = runtime_policy_snapshot(settings)
    compat_telemetry_snapshot = _debug_query_compat_telemetry_from_request(request).snapshot()
    stale_after_seconds = int(getattr(settings, "event_debug_query_compat_stale_after_seconds", 86400))
    runtime_policy["event_debug_query_compat_telemetry"] = compat_telemetry_snapshot
    runtime_policy.update(
        debug_query_compat_sunset_snapshot(
            compat_enabled=bool(runtime_policy["event_debug_query_compat_enabled"]),
            telemetry_snapshot=compat_telemetry_snapshot,
        )
    )
    runtime_policy.update(
        debug_query_compat_recent_snapshot(
            compat_enabled=bool(runtime_policy["event_debug_query_compat_enabled"]),
            telemetry_snapshot=compat_telemetry_snapshot,
        )
    )
    runtime_policy.update(
        debug_query_compat_freshness_snapshot(
            telemetry_snapshot=compat_telemetry_snapshot,
            stale_after_seconds=stale_after_seconds,
        )
    )
    runtime_policy.update(
        debug_query_compat_activity_snapshot(
            compat_enabled=bool(runtime_policy["event_debug_query_compat_enabled"]),
            telemetry_snapshot=compat_telemetry_snapshot,
            stale_after_seconds=stale_after_seconds,
        )
    )
    reflection_snapshot = reflection_worker.snapshot()
    reflection_topology = reflection_topology_handoff_posture(
        runtime_mode=reflection_runtime_mode,
        worker_running=bool(reflection_snapshot["running"]),
    )
    reflection_topology["max_attempts"] = int(reflection_snapshot["max_attempts"])
    reflection_topology["retry_backoff_seconds"] = list(reflection_snapshot["retry_backoff_seconds"])  # type: ignore[arg-type]
    reflection_topology["stuck_processing_seconds"] = int(reflection_snapshot["stuck_processing_seconds"])
    reflection_stats = await memory_repository.get_reflection_task_stats(
        max_attempts=int(reflection_snapshot["max_attempts"]),
        stuck_after_seconds=int(reflection_snapshot["stuck_processing_seconds"]),
        retry_backoff_seconds=tuple(int(value) for value in reflection_snapshot["retry_backoff_seconds"]),  # type: ignore[arg-type]
    )
    reflection_deployment_readiness = reflection_deployment_readiness_snapshot(
        runtime_mode=reflection_runtime_mode,
        topology=reflection_topology,
        worker_running=bool(reflection_snapshot["running"]),
        task_stats=reflection_stats,
    )
    if reflection_runtime_mode == "in_process":
        reflection_healthy = (
            bool(reflection_snapshot["running"])
            and reflection_stats["stuck_processing"] == 0
            and reflection_stats["exhausted_failed"] == 0
        )
    else:
        reflection_healthy = (
            reflection_stats["stuck_processing"] == 0
            and reflection_stats["exhausted_failed"] == 0
        )
    scheduler_execution_mode = normalize_scheduler_execution_mode(
        str(getattr(settings, "scheduler_execution_mode", "in_process") or "in_process")
    )
    proactive_enabled = bool(getattr(settings, "proactive_enabled", False))
    scheduler_snapshot = scheduler_worker.snapshot() if scheduler_worker is not None else {}
    cadence_evidence = await _scheduler_cadence_evidence_from_request(request)
    maintenance_evidence = cadence_evidence.get("maintenance", {})
    proactive_evidence = cadence_evidence.get("proactive", {})
    scheduler_running = bool(scheduler_snapshot.get("running", False))
    scheduler_enabled = bool(scheduler_snapshot.get("enabled", False))
    scheduler_execution = scheduler_cadence_execution_snapshot(
        execution_mode=str(scheduler_snapshot.get("execution_mode", scheduler_execution_mode)),
        scheduler_enabled=scheduler_enabled,
        scheduler_running=scheduler_running,
        proactive_enabled=bool(scheduler_snapshot.get("proactive_enabled", proactive_enabled)),
    )
    scheduler_snapshot = {
        **scheduler_snapshot,
        "execution_mode": scheduler_execution["selected_execution_mode"],
        "configured_enabled": bool(scheduler_snapshot.get("configured_enabled", scheduler_enabled)),
        "enabled": scheduler_enabled,
        "running": scheduler_running,
        "proactive_enabled": bool(scheduler_snapshot.get("proactive_enabled", proactive_enabled)),
        "last_maintenance_tick_at": maintenance_evidence.get("last_run_at")
        or scheduler_snapshot.get("last_maintenance_tick_at"),
        "last_proactive_tick_at": proactive_evidence.get("last_run_at")
        or scheduler_snapshot.get("last_proactive_tick_at"),
        "last_maintenance_summary": maintenance_evidence.get("summary")
        or scheduler_snapshot.get("last_maintenance_summary", {}),
        "last_proactive_summary": proactive_evidence.get("summary")
        or scheduler_snapshot.get("last_proactive_summary", {}),
        "maintenance_cadence_owner": scheduler_execution["maintenance_cadence_owner"],
        "proactive_cadence_owner": scheduler_execution["proactive_cadence_owner"],
        "cadence_execution": scheduler_execution,
        "external_owner_policy": external_scheduler_policy_snapshot(
            scheduler_execution_mode=str(
                scheduler_snapshot.get("execution_mode", scheduler_execution_mode)
            ),
            scheduler_running=scheduler_running,
            maintenance_last_run_at=maintenance_evidence.get("last_run_at")
            or scheduler_snapshot.get("last_maintenance_tick_at"),
            maintenance_last_summary=maintenance_evidence.get("summary")
            or scheduler_snapshot.get("last_maintenance_summary", {}),
            maintenance_interval_seconds=int(scheduler_snapshot.get("maintenance_interval_seconds", 3600)),
            proactive_enabled=bool(scheduler_snapshot.get("proactive_enabled", proactive_enabled)),
            proactive_last_run_at=proactive_evidence.get("last_run_at")
            or scheduler_snapshot.get("last_proactive_tick_at"),
            proactive_last_summary=proactive_evidence.get("summary")
            or scheduler_snapshot.get("last_proactive_summary", {}),
            proactive_interval_seconds=int(scheduler_snapshot.get("proactive_interval_seconds", 1800)),
        ),
    }
    scheduler_healthy = bool(scheduler_execution["ready"])
    attention_snapshot = await _attention_snapshot_from_request(request)
    memory_retrieval_snapshot = _memory_retrieval_snapshot_from_settings(settings)
    release_readiness = release_readiness_snapshot(runtime_policy)
    proactive_policy = proactive_runtime_policy_snapshot(
        proactive_enabled=proactive_enabled,
        proactive_interval_seconds=int(getattr(settings, "proactive_interval", 1800)),
        scheduler_execution_mode=str(scheduler_snapshot.get("execution_mode", scheduler_execution_mode)),
        scheduler_ready=bool(scheduler_execution["ready"]),
        scheduler_running=scheduler_running,
    )
    role_skill_policy = role_skill_policy_snapshot()
    reflection_external_driver_policy = reflection_external_driver_policy_snapshot(
        reflection_runtime_mode=reflection_runtime_mode,
        worker_running=bool(reflection_snapshot["running"]),
        scheduler_execution_mode=str(
            scheduler_snapshot.get("execution_mode", scheduler_execution_mode)
        ),
    )
    reflection_supervision = reflection_supervision_policy_snapshot(
        reflection_runtime_mode=reflection_runtime_mode,
        scheduler_execution_mode=str(
            scheduler_snapshot.get("execution_mode", scheduler_execution_mode)
        ),
        worker_running=bool(reflection_snapshot["running"]),
        task_stats=reflection_stats,
    )
    topology_policy = runtime_topology_policy_snapshot(
        reflection_runtime_mode=reflection_runtime_mode,
        reflection_readiness=reflection_deployment_readiness,
        attention_snapshot=attention_snapshot,
    )
    observability = observability_export_policy_snapshot(
        structured_logs_available=True,
        health_surface_available=True,
        system_debug_available=True,
        export_artifact_available=True,
        bundle_helper_available=True,
    )
    telegram_channel = _telegram_telemetry_from_request(request).snapshot(
        bot_token_configured=bool(getattr(settings, "telegram_bot_token", "")),
        webhook_secret_configured=bool(getattr(settings, "telegram_webhook_secret", "")),
    )
    learned_state = learned_state_policy_snapshot()
    v1_readiness = v1_readiness_policy_snapshot(
        telegram_conversation_channel=telegram_channel,
        learned_state=learned_state,
        role_skill_policy=role_skill_policy,
    )
    return {
        "status": "ok",
        "runtime_policy": runtime_policy,
        "release_readiness": release_readiness,
        "v1_readiness": v1_readiness,
        "api_readiness": api_readiness_policy_snapshot(),
        "runtime_topology": topology_policy,
        "observability": observability,
        "identity": {
            **identity_policy_snapshot(),
            "language_continuity": language_continuity_policy_snapshot(),
            "adaptive_governance": adaptive_identity_governance_snapshot(),
        },
        "affective": {
            **affective_input_policy_snapshot(),
            "assessment_policy": affective_assessment_policy_snapshot(settings),
        },
        "memory_retrieval": memory_retrieval_snapshot,
        "planning_governance": planning_governance_snapshot(),
        "learned_state": learned_state,
        "connectors": {
            **connector_authorization_matrix_snapshot(),
            "capability_proposal": connector_capability_proposal_snapshot(),
            "execution_baseline": connector_execution_baseline_snapshot(settings),
            "organizer_tool_stack": organizer_tool_stack_snapshot(settings),
            "web_knowledge_tools": web_knowledge_tooling_snapshot(),
        },
        "deployment": deployment_policy_snapshot(),
        "conversation_channels": {
            "telegram": telegram_channel,
        },
        "scheduler": {
            "healthy": scheduler_healthy,
            **scheduler_snapshot,
        },
        "proactive": {
            **proactive_policy,
            "enabled": proactive_enabled,
            "scheduler_tick_summary": dict(scheduler_snapshot.get("last_proactive_summary", {})),
            "last_tick_at": scheduler_snapshot.get("last_proactive_tick_at"),
        },
        "role_skill": role_skill_policy,
        "attention": attention_snapshot,
        "reflection": {
            "healthy": reflection_healthy,
            "runtime_mode": reflection_runtime_mode,
            "deployment_readiness": reflection_deployment_readiness,
            "topology": reflection_topology,
            "external_driver_policy": reflection_external_driver_policy,
            "supervision": reflection_supervision,
            "worker": reflection_snapshot,
            "adaptive_outputs": dict(reflection_snapshot.get("adaptive_output_summary", {})),
            "tasks": reflection_stats,
        },
    }


@router.get("/internal/state/inspect")
async def internal_state_inspection_endpoint(
    request: Request,
    user_id: str = Query(..., min_length=1),
) -> dict[str, Any]:
    settings = _settings_from_request(request)
    _enforce_debug_access(request=request, settings=settings)
    return await _build_learned_state_snapshot(request=request, user_id=user_id.strip())


@router.post("/event", response_model=EventResponse, response_model_exclude_none=True)
async def event_endpoint(
    payload: dict[str, Any],
    request: Request,
    response: Response,
    debug: bool = Query(default=False),
) -> dict[str, Any]:
    settings = _settings_from_request(request)
    compat_telemetry = _debug_query_compat_telemetry_from_request(request)
    if debug and not event_debug_query_compat_enabled(settings):
        compat_telemetry.record_blocked()
        raise HTTPException(
            status_code=403,
            detail=(
                "Debug query compatibility route is disabled for this environment. "
                f"Use POST {DEBUG_INTERNAL_INGRESS_PATH}."
            ),
        )
    if debug:
        try:
            body = await _handle_internal_debug_ingress(
                payload=payload,
                request=request,
            )
        except HTTPException:
            compat_telemetry.record_blocked()
            raise
        compat_telemetry.record_allowed()
    else:
        body = await _handle_event_request(
            payload=payload,
            request=request,
            include_debug=False,
        )
    if debug:
        _mark_query_debug_compat_headers(response)
    return body


@router.post("/event/debug", response_model=EventResponse, response_model_exclude_none=True)
async def event_debug_endpoint(
    payload: dict[str, Any],
    request: Request,
    response: Response,
) -> dict[str, Any]:
    settings = _settings_from_request(request)
    break_glass_used = _enforce_shared_debug_ingress_policy(request=request, settings=settings)
    body = await _handle_internal_debug_ingress(
        payload=payload,
        request=request,
    )
    _mark_shared_debug_compat_headers(
        response=response,
        settings=settings,
        break_glass_used=break_glass_used,
    )
    return body


@router.post(DEBUG_INTERNAL_INGRESS_PATH, response_model=EventResponse, response_model_exclude_none=True)
async def internal_event_debug_endpoint(
    payload: dict[str, Any],
    request: Request,
) -> dict[str, Any]:
    return await _handle_internal_debug_ingress(
        payload=payload,
        request=request,
    )


@router.post("/telegram/set-webhook")
async def set_webhook(body: SetWebhookRequest, request: Request) -> dict[str, Any]:
    telegram_client = _telegram_from_request(request)
    settings = _settings_from_request(request)
    token = body.secret_token or settings.telegram_webhook_secret
    return await telegram_client.set_webhook(webhook_url=body.webhook_url, secret_token=token)
