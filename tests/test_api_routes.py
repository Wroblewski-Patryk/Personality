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
    def __init__(self, *, reflection_triggered: bool = False):
        self.last_event: Event | None = None
        self.reflection_triggered = reflection_triggered

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
            reflection_triggered=self.reflection_triggered,
            stage_timings_ms={
                "memory_load": 1,
                "task_load": 0,
                "goal_milestone_load": 0,
                "goal_milestone_history_load": 0,
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
    def __init__(
        self,
        telegram_webhook_secret: str | None = None,
        *,
        app_env: str = "development",
        event_debug_enabled: bool | None = True,
        event_debug_token: str | None = None,
        startup_schema_mode: str = "migrate",
        production_policy_enforcement: str = "warn",
    ):
        self.telegram_webhook_secret = telegram_webhook_secret
        self.app_env = app_env
        self.event_debug_enabled = event_debug_enabled
        self.event_debug_token = event_debug_token
        self.startup_schema_mode = startup_schema_mode
        self.production_policy_enforcement = production_policy_enforcement

    def is_event_debug_enabled(self) -> bool:
        if self.event_debug_enabled is not None:
            return self.event_debug_enabled
        return True


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


def _client(
    secret: str | None = None,
    *,
    app_env: str = "development",
    reflection_triggered: bool = False,
    reflection_stats: dict[str, int] | None = None,
    reflection_running: bool = True,
    event_debug_enabled: bool | None = True,
    event_debug_token: str | None = None,
    startup_schema_mode: str = "migrate",
    production_policy_enforcement: str = "warn",
) -> tuple[TestClient, FakeRuntime, FakeTelegramClient]:
    app = FastAPI()
    app.include_router(router)
    runtime = FakeRuntime(reflection_triggered=reflection_triggered)
    telegram_client = FakeTelegramClient()
    memory_repository = FakeMemoryRepository(stats=reflection_stats)
    reflection_worker = FakeReflectionWorker(running=reflection_running)
    app.state.runtime = runtime
    app.state.telegram_client = telegram_client
    app.state.settings = FakeSettings(
        telegram_webhook_secret=secret,
        app_env=app_env,
        event_debug_enabled=event_debug_enabled,
        event_debug_token=event_debug_token,
        startup_schema_mode=startup_schema_mode,
        production_policy_enforcement=production_policy_enforcement,
    )
    app.state.memory_repository = memory_repository
    app.state.reflection_worker = reflection_worker
    return TestClient(app), runtime, telegram_client


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
            "event_debug_source": "explicit",
            "production_policy_enforcement": "warn",
            "recommended_production_policy_enforcement": "warn",
            "production_policy_mismatches": [],
            "production_policy_mismatch_count": 0,
            "strict_startup_blocked": False,
            "strict_rollout_ready": True,
            "strict_rollout_hint": "not_applicable_non_production",
        },
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
        "event_debug_source": "explicit",
        "production_policy_enforcement": "strict",
        "recommended_production_policy_enforcement": "warn",
        "production_policy_mismatches": ["startup_schema_mode=create_tables"],
        "production_policy_mismatch_count": 1,
        "strict_startup_blocked": True,
        "strict_rollout_ready": False,
        "strict_rollout_hint": "resolve_mismatches_before_strict",
    }


def test_health_endpoint_marks_event_debug_source_as_environment_default_when_unset() -> None:
    client, _, _ = _client(event_debug_enabled=None)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["runtime_policy"]["event_debug_enabled"] is True
    assert body["runtime_policy"]["event_debug_token_required"] is False
    assert body["runtime_policy"]["event_debug_source"] == "environment_default"
    assert body["runtime_policy"]["production_policy_enforcement"] == "warn"
    assert body["runtime_policy"]["recommended_production_policy_enforcement"] == "warn"
    assert body["runtime_policy"]["production_policy_mismatches"] == []
    assert body["runtime_policy"]["production_policy_mismatch_count"] == 0
    assert body["runtime_policy"]["strict_startup_blocked"] is False
    assert body["runtime_policy"]["strict_rollout_ready"] is True
    assert body["runtime_policy"]["strict_rollout_hint"] == "not_applicable_non_production"


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
        "startup_schema_mode=create_tables",
    ]
    assert body["runtime_policy"]["production_policy_mismatch_count"] == 2
    assert body["runtime_policy"]["strict_startup_blocked"] is True
    assert body["runtime_policy"]["strict_rollout_ready"] is False
    assert body["runtime_policy"]["recommended_production_policy_enforcement"] == "warn"
    assert body["runtime_policy"]["strict_rollout_hint"] == "resolve_mismatches_before_strict"


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
    assert body["runtime_policy"]["strict_rollout_ready"] is True
    assert body["runtime_policy"]["recommended_production_policy_enforcement"] == "strict"
    assert body["runtime_policy"]["strict_rollout_hint"] == "can_enable_strict"


def test_health_endpoint_marks_reflection_unhealthy_when_worker_not_running() -> None:
    client, _, _ = _client(reflection_running=False)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["reflection"]["healthy"] is False
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
    assert body["reflection"]["worker"]["running"] is True
    assert body["reflection"]["tasks"]["exhausted_failed"] == 1
    assert body["reflection"]["tasks"]["stuck_processing"] == 1


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
    assert runtime.last_event is not None
    assert runtime.last_event.payload["text"] == "show debug runtime"


def test_event_endpoint_rejects_debug_payload_when_debug_token_is_missing() -> None:
    client, runtime, _ = _client(event_debug_enabled=True, event_debug_token="debug-secret")

    response = client.post("/event?debug=true", json={"text": "show debug runtime"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid debug token."
    assert runtime.last_event is None


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
    assert runtime.last_event is not None


def test_event_endpoint_rejects_debug_payload_when_debug_mode_is_disabled() -> None:
    client, runtime, _ = _client(event_debug_enabled=False)

    response = client.post("/event?debug=true", json={"text": "show debug runtime"})

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
    assert "event" in debug_body["debug"]
    assert "stage_timings_ms" in debug_body["debug"]


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
