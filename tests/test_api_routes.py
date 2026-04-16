from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router
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
    TaskRecordOutput,
)


class FakeRuntime:
    def __init__(self):
        self.last_event: Event | None = None

    async def run(self, event: Event) -> RuntimeResult:
        self.last_event = event
        timestamp = datetime.now(timezone.utc)
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
            action_result=ActionResult(
                status="success",
                actions=["api_response"],
                notes="Response returned via API.",
            ),
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
            reflection_triggered=False,
            stage_timings_ms={
                "memory_load": 1,
                "task_load": 0,
                "goal_progress_load": 0,
                "identity_load": 0,
                "perception": 0,
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
    def __init__(self, telegram_webhook_secret: str | None = None):
        self.telegram_webhook_secret = telegram_webhook_secret


class FakeMemoryRepository:
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
        return {
            "total": 4,
            "pending": 1,
            "processing": 1,
            "completed": 1,
            "failed": 1,
            "retryable_failed": 1,
            "exhausted_failed": 0,
            "stuck_processing": 0,
        }


class FakeReflectionWorker:
    def snapshot(self) -> dict:
        return {
            "running": True,
            "queue_size": 1,
            "queue_capacity": 99,
            "queued_task_count": 1,
            "queued_task_ids": [42],
            "max_attempts": 3,
            "retry_backoff_seconds": [5, 30, 120],
            "stuck_processing_seconds": 180,
        }


def _client(secret: str | None = None) -> tuple[TestClient, FakeRuntime, FakeTelegramClient]:
    app = FastAPI()
    app.include_router(router)
    runtime = FakeRuntime()
    telegram_client = FakeTelegramClient()
    memory_repository = FakeMemoryRepository()
    reflection_worker = FakeReflectionWorker()
    app.state.runtime = runtime
    app.state.telegram_client = telegram_client
    app.state.settings = FakeSettings(telegram_webhook_secret=secret)
    app.state.memory_repository = memory_repository
    app.state.reflection_worker = reflection_worker
    return TestClient(app), runtime, telegram_client


def test_health_endpoint_returns_ok() -> None:
    client, _, _ = _client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "reflection": {
            "healthy": True,
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


def test_event_endpoint_returns_runtime_result_and_normalizes_event() -> None:
    client, runtime, _ = _client()

    response = client.post("/event", json={"text": "hello from api"})

    assert response.status_code == 200
    body = response.json()
    assert body["expression"]["message"] == "Test reply"
    assert body["expression"]["language"] == "en"
    assert body["perception"]["language"] == "en"
    assert body["perception"]["language_source"] == "keyword_signal"
    assert body["reflection_triggered"] is False
    assert body["identity"]["mission"] == "Help the user move forward with clear, constructive support."
    assert body["active_goals"][0]["name"] == "ship the MVP"
    assert body["active_tasks"][0]["status"] == "blocked"
    assert body["goal_progress_history"][0]["score"] == 0.42
    assert body["stage_timings_ms"]["memory_load"] == 1
    assert body["stage_timings_ms"]["total"] == 12
    assert body["event"]["source"] == "api"
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "hello from api"
    assert runtime.last_event.meta.trace_id


def test_event_endpoint_rejects_telegram_payload_with_wrong_secret() -> None:
    client, runtime, _ = _client(secret="expected-secret")

    response = client.post(
        "/event",
        json={
            "update_id": 1,
            "message": {
                "text": "ping",
                "chat": {"id": 123},
                "from": {"id": 999},
            },
        },
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
