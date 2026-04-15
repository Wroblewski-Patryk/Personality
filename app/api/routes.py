from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas import SetWebhookRequest
from app.core.events import normalize_event
from app.core.runtime import RuntimeOrchestrator
from app.integrations.telegram.client import TelegramClient
from app.memory.repository import MemoryRepository
from app.reflection.worker import ReflectionWorker

router = APIRouter()


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


@router.get("/health")
async def health(request: Request) -> dict[str, Any]:
    reflection_worker = _reflection_worker_from_request(request)
    memory_repository = _memory_repository_from_request(request)
    reflection_snapshot = reflection_worker.snapshot()
    reflection_stats = await memory_repository.get_reflection_task_stats(
        max_attempts=int(reflection_snapshot["max_attempts"]),
        stuck_after_seconds=int(reflection_snapshot["stuck_processing_seconds"]),
        retry_backoff_seconds=tuple(int(value) for value in reflection_snapshot["retry_backoff_seconds"]),  # type: ignore[arg-type]
    )
    reflection_healthy = (
        bool(reflection_snapshot["running"])
        and reflection_stats["stuck_processing"] == 0
        and reflection_stats["exhausted_failed"] == 0
    )
    return {
        "status": "ok",
        "reflection": {
            "healthy": reflection_healthy,
            "worker": reflection_snapshot,
            "tasks": reflection_stats,
        },
    }


@router.post("/event")
async def event_endpoint(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    settings = _settings_from_request(request)
    looks_like_telegram = isinstance(payload.get("message"), dict) or "update_id" in payload
    if looks_like_telegram and settings.telegram_webhook_secret:
        received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if received_secret != settings.telegram_webhook_secret:
            raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret token.")

    event = normalize_event(payload)
    runtime = _runtime_from_request(request)
    result = await runtime.run(event)
    return result.model_dump(mode="json")


@router.post("/telegram/set-webhook")
async def set_webhook(body: SetWebhookRequest, request: Request) -> dict[str, Any]:
    telegram_client = _telegram_from_request(request)
    settings = _settings_from_request(request)
    token = body.secret_token or settings.telegram_webhook_secret
    return await telegram_client.set_webhook(webhook_url=body.webhook_url, secret_token=token)
