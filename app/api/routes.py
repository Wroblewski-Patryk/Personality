from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.api.schemas import EventQueueResponse, EventResponse, EventReplyResponse, EventRuntimeResponse, SetWebhookRequest
from app.core.attention import AttentionTurnCoordinator
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
    event_debug_token_required,
    production_debug_token_required,
    runtime_policy_snapshot,
)
from app.core.runtime import RuntimeOrchestrator
from app.integrations.telegram.client import TelegramClient
from app.memory.repository import MemoryRepository
from app.reflection.worker import ReflectionWorker
from app.workers.scheduler import SchedulerWorker

router = APIRouter()
DEBUG_COMPAT_HINT_HEADER = "X-AION-Debug-Compat"
DEBUG_COMPAT_HINT_VALUE = "query_debug_route_is_compatibility_use_post_event_debug"
DEBUG_COMPAT_LINK_VALUE = '</event/debug>; rel="alternate"'
DEBUG_COMPAT_DEPRECATED_HEADER = "X-AION-Debug-Compat-Deprecated"
DEBUG_COMPAT_DEPRECATED_VALUE = "true"


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
    coordinator = AttentionTurnCoordinator()
    request.app.state.attention_turn_coordinator = coordinator
    return coordinator


def _attention_snapshot_from_request(request: Request) -> dict[str, Any]:
    coordinator = _attention_coordinator_from_request(request)
    snapshot = coordinator.snapshot()
    return {
        "burst_window_ms": int(round(coordinator.burst_window_seconds * 1000)),
        "answered_ttl_seconds": coordinator.answered_ttl_seconds,
        "stale_turn_seconds": coordinator.stale_turn_seconds,
        **snapshot,
    }


def _memory_retrieval_snapshot_from_settings(settings) -> dict[str, Any]:
    semantic_vector_enabled = bool(getattr(settings, "semantic_vector_enabled", True))
    return {
        "semantic_vector_enabled": semantic_vector_enabled,
        "semantic_retrieval_mode": "hybrid_vector_lexical" if semantic_vector_enabled else "lexical_only",
    }


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
    )
    return response.model_dump(mode="json", exclude_none=True)


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
    reflection_stats = await memory_repository.get_reflection_task_stats(
        max_attempts=int(reflection_snapshot["max_attempts"]),
        stuck_after_seconds=int(reflection_snapshot["stuck_processing_seconds"]),
        retry_backoff_seconds=tuple(int(value) for value in reflection_snapshot["retry_backoff_seconds"]),  # type: ignore[arg-type]
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
    scheduler_snapshot = scheduler_worker.snapshot() if scheduler_worker is not None else {"enabled": False, "running": False}
    scheduler_healthy = bool(
        not scheduler_snapshot.get("enabled") or scheduler_snapshot.get("running")
    )
    attention_snapshot = _attention_snapshot_from_request(request)
    memory_retrieval_snapshot = _memory_retrieval_snapshot_from_settings(settings)
    return {
        "status": "ok",
        "runtime_policy": runtime_policy,
        "memory_retrieval": memory_retrieval_snapshot,
        "scheduler": {
            "healthy": scheduler_healthy,
            **scheduler_snapshot,
        },
        "attention": attention_snapshot,
        "reflection": {
            "healthy": reflection_healthy,
            "runtime_mode": reflection_runtime_mode,
            "worker": reflection_snapshot,
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
            detail="Debug query compatibility route is disabled for this environment. Use POST /event/debug.",
        )
    if debug:
        try:
            body = await _handle_event_request(
                payload=payload,
                request=request,
                include_debug=True,
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
        response.headers[DEBUG_COMPAT_HINT_HEADER] = DEBUG_COMPAT_HINT_VALUE
        response.headers["Link"] = DEBUG_COMPAT_LINK_VALUE
        response.headers[DEBUG_COMPAT_DEPRECATED_HEADER] = DEBUG_COMPAT_DEPRECATED_VALUE
    return body


@router.post("/event/debug", response_model=EventResponse, response_model_exclude_none=True)
async def event_debug_endpoint(
    payload: dict[str, Any],
    request: Request,
) -> dict[str, Any]:
    return await _handle_event_request(
        payload=payload,
        request=request,
        include_debug=True,
    )


@router.post("/telegram/set-webhook")
async def set_webhook(body: SetWebhookRequest, request: Request) -> dict[str, Any]:
    telegram_client = _telegram_from_request(request)
    settings = _settings_from_request(request)
    token = body.secret_token or settings.telegram_webhook_secret
    return await telegram_client.set_webhook(webhook_url=body.webhook_url, secret_token=token)
