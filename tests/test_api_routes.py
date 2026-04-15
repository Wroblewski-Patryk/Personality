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
    MemoryRecord,
    MotivationOutput,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
    RuntimeResult,
)


class FakeRuntime:
    def __init__(self):
        self.last_event: Event | None = None

    async def run(self, event: Event) -> RuntimeResult:
        self.last_event = event
        timestamp = datetime.now(timezone.utc)
        return RuntimeResult(
            event=event,
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


def _client(secret: str | None = None) -> tuple[TestClient, FakeRuntime, FakeTelegramClient]:
    app = FastAPI()
    app.include_router(router)
    runtime = FakeRuntime()
    telegram_client = FakeTelegramClient()
    app.state.runtime = runtime
    app.state.telegram_client = telegram_client
    app.state.settings = FakeSettings(telegram_webhook_secret=secret)
    return TestClient(app), runtime, telegram_client


def test_health_endpoint_returns_ok() -> None:
    client, _, _ = _client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
