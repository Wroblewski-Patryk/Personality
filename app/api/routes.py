from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.api.schemas import EventQueueResponse, EventResponse, EventReplyResponse, EventRuntimeResponse, SetWebhookRequest
from app.core.attention import (
    AttentionTurnCoordinator,
    attention_coordination_readiness_snapshot,
    attention_timing_policy_snapshot,
)
from app.core.debug_compat import (
    DebugQueryCompatTelemetry,
    debug_query_compat_activity_snapshot,
    debug_query_compat_freshness_snapshot,
    debug_query_compat_recent_snapshot,
    debug_query_compat_sunset_snapshot,
)
from app.core.events import looks_like_telegram_update, normalize_event
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
from app.integrations.telegram.client import TelegramClient
from app.memory.embeddings import embedding_strategy_snapshot, normalize_embedding_source_kinds
from app.memory.repository import MemoryRepository
from app.reflection.worker import ReflectionWorker
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
    )
    snapshot["retrieval_depth_policy"] = retrieval_depth_policy_snapshot(
        episodic_limit=RuntimeOrchestrator.MEMORY_LOAD_LIMIT,
        conclusion_limit=8,
        semantic_vector_enabled=bool(getattr(settings, "semantic_vector_enabled", True)),
    )
    return snapshot


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


async def _handle_event_request(
    *,
    payload: dict[str, Any],
    request: Request,
    include_debug: bool,
) -> dict[str, Any]:
    settings = _settings_from_request(request)
    looks_like_telegram = looks_like_telegram_update(payload)
    if looks_like_telegram and settings.telegram_webhook_secret:
        received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if received_secret != settings.telegram_webhook_secret:
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
        result = await runtime.run(runtime_event)
    finally:
        await attention_coordinator.finalize_event(runtime_event)

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
        "maintenance_cadence_owner": scheduler_execution["maintenance_cadence_owner"],
        "proactive_cadence_owner": scheduler_execution["proactive_cadence_owner"],
        "cadence_execution": scheduler_execution,
    }
    scheduler_healthy = bool(scheduler_execution["ready"])
    attention_snapshot = await _attention_snapshot_from_request(request)
    memory_retrieval_snapshot = _memory_retrieval_snapshot_from_settings(settings)
    release_readiness = release_readiness_snapshot(runtime_policy)
    return {
        "status": "ok",
        "runtime_policy": runtime_policy,
        "release_readiness": release_readiness,
        "memory_retrieval": memory_retrieval_snapshot,
        "scheduler": {
            "healthy": scheduler_healthy,
            **scheduler_snapshot,
        },
        "attention": attention_snapshot,
        "reflection": {
            "healthy": reflection_healthy,
            "runtime_mode": reflection_runtime_mode,
            "deployment_readiness": reflection_deployment_readiness,
            "topology": reflection_topology,
            "worker": reflection_snapshot,
            "adaptive_outputs": dict(reflection_snapshot.get("adaptive_output_summary", {})),
            "tasks": reflection_stats,
        },
    }


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
