from fastapi import FastAPI
import pytest

import app.main as app_main


class _StrictDebugMismatchSettings:
    app_env = "production"
    log_level = "INFO"
    event_debug_enabled = True
    startup_schema_mode = "migrate"
    production_policy_enforcement = "strict"
    reflection_runtime_mode = "in_process"
    attention_burst_window_ms = 120
    attention_answered_ttl_seconds = 5.0
    attention_stale_turn_seconds = 30.0

    @staticmethod
    def validate_required() -> None:
        return None

    @staticmethod
    def is_event_debug_enabled() -> bool:
        return True


class _StrictSchemaMismatchSettings:
    app_env = "production"
    log_level = "INFO"
    event_debug_enabled = False
    startup_schema_mode = "create_tables"
    production_policy_enforcement = "strict"
    reflection_runtime_mode = "in_process"
    attention_burst_window_ms = 120
    attention_answered_ttl_seconds = 5.0
    attention_stale_turn_seconds = 30.0

    @staticmethod
    def validate_required() -> None:
        return None

    @staticmethod
    def is_event_debug_enabled() -> bool:
        return False


async def test_lifespan_blocks_startup_before_database_init_when_strict_policy_detects_debug_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_initialized = False

    class _DatabaseGuard:
        def __init__(self, *_args, **_kwargs):
            nonlocal database_initialized
            database_initialized = True
            raise AssertionError("Database initialization should not run when strict policy blocks startup.")

    monkeypatch.setattr(app_main, "get_settings", lambda: _StrictDebugMismatchSettings())
    monkeypatch.setattr(app_main, "Database", _DatabaseGuard)

    with pytest.raises(RuntimeError, match="event_debug_enabled=true"):
        async with app_main.lifespan(FastAPI()):
            pass

    assert database_initialized is False


async def test_lifespan_blocks_startup_before_database_init_when_strict_policy_detects_schema_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_initialized = False

    class _DatabaseGuard:
        def __init__(self, *_args, **_kwargs):
            nonlocal database_initialized
            database_initialized = True
            raise AssertionError("Database initialization should not run when strict policy blocks startup.")

    monkeypatch.setattr(app_main, "get_settings", lambda: _StrictSchemaMismatchSettings())
    monkeypatch.setattr(app_main, "Database", _DatabaseGuard)

    with pytest.raises(RuntimeError, match="startup_schema_mode=create_tables"):
        async with app_main.lifespan(FastAPI()):
            pass

    assert database_initialized is False


async def test_lifespan_wires_memory_repository_into_attention_coordinator_for_durable_inbox(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_kwargs: dict[str, object] = {}

    class _Settings:
        app_env = "development"
        log_level = "INFO"
        openai_api_key = None
        openai_model = "gpt-4o-mini"
        affective_assessment_enabled = None
        database_url = "sqlite+aiosqlite://"
        telegram_bot_token = "telegram-token"
        startup_schema_mode = "migrate"
        production_policy_enforcement = "warn"
        reflection_runtime_mode = "in_process"
        attention_burst_window_ms = 120
        attention_answered_ttl_seconds = 5.0
        attention_stale_turn_seconds = 30.0
        attention_coordination_mode = "durable_inbox"
        scheduler_enabled = False
        scheduler_execution_mode = "in_process"
        reflection_interval = 900
        maintenance_interval = 3600
        proactive_enabled = False
        proactive_interval = 1800
        event_debug_query_compat_recent_window = 20
        app_port = 8000
        semantic_vector_enabled = False
        embedding_provider = "deterministic"
        embedding_model = "deterministic-v1"
        embedding_dimensions = 32
        embedding_refresh_mode = "on_write"
        embedding_refresh_interval_seconds = 21600
        embedding_provider_ownership_enforcement = "warn"
        embedding_model_governance_enforcement = "warn"
        embedding_source_rollout_enforcement = "warn"

        @staticmethod
        def validate_required() -> None:
            return None

        @staticmethod
        def is_affective_assessment_enabled() -> bool:
            return False

        @staticmethod
        def get_embedding_source_kinds() -> tuple[str, ...]:
            return ("episodic", "semantic", "affective")

    class _FakeDatabase:
        def __init__(self, *_args, **_kwargs):
            self.engine = object()
            self.session_factory = object()

        async def dispose(self) -> None:
            return None

    class _FakeMemoryRepository:
        def __init__(self, *_args, **_kwargs):
            pass

        async def get_reflection_task_stats(self, **_kwargs) -> dict[str, int]:
            return {
                "pending": 0,
                "processing": 0,
                "retryable_failed": 0,
                "stuck_processing": 0,
                "exhausted_failed": 0,
            }

    class _FakeTelegramClient:
        def __init__(self, *_args, **_kwargs):
            pass

        async def close(self) -> None:
            return None

    class _FakeReflectionWorker:
        def __init__(self, *_args, **_kwargs):
            self._running = False

        async def start(self) -> None:
            self._running = True

        async def stop(self) -> None:
            self._running = False

        def is_running(self) -> bool:
            return self._running

        def snapshot(self) -> dict[str, object]:
            return {
                "running": self._running,
                "max_attempts": 3,
                "stuck_processing_seconds": 180,
                "retry_backoff_seconds": [5, 30, 120],
                "adaptive_output_summary": {},
            }

    class _FakeSchedulerWorker:
        def __init__(self, *_args, **kwargs):
            self.enabled = bool(kwargs.get("enabled", False))
            self.runtime = None

        async def start(self) -> None:
            return None

        async def stop(self) -> None:
            return None

        def set_runtime(self, runtime) -> None:
            self.runtime = runtime

    class _FakeAttentionCoordinator:
        def __init__(self, **kwargs):
            captured_kwargs.update(kwargs)
            self.memory_repository = kwargs.get("memory_repository")

    class _Dummy:
        def __init__(self, *_args, **_kwargs):
            pass

    monkeypatch.setattr(app_main, "get_settings", lambda: _Settings())
    monkeypatch.setattr(app_main, "setup_logging", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(app_main, "Database", _FakeDatabase)
    monkeypatch.setattr(app_main, "OpenAIEmbeddingClient", _Dummy)
    monkeypatch.setattr(app_main, "MemoryRepository", _FakeMemoryRepository)
    monkeypatch.setattr(app_main, "TelegramClient", _FakeTelegramClient)
    monkeypatch.setattr(app_main, "OpenAIClient", _Dummy)
    monkeypatch.setattr(app_main, "ActionExecutor", _Dummy)
    monkeypatch.setattr(app_main, "ClickUpTaskClient", _Dummy)
    monkeypatch.setattr(app_main, "GoogleCalendarAvailabilityClient", _Dummy)
    monkeypatch.setattr(app_main, "GoogleDriveMetadataClient", _Dummy)
    monkeypatch.setattr(app_main, "DuckDuckGoSearchClient", _Dummy)
    monkeypatch.setattr(app_main, "GenericHttpPageClient", _Dummy)
    monkeypatch.setattr(app_main, "ReflectionWorker", _FakeReflectionWorker)
    monkeypatch.setattr(app_main, "SchedulerWorker", _FakeSchedulerWorker)
    monkeypatch.setattr(app_main, "RuntimeOrchestrator", _Dummy)
    monkeypatch.setattr(app_main, "PerceptionAgent", _Dummy)
    monkeypatch.setattr(app_main, "ContextAgent", _Dummy)
    monkeypatch.setattr(app_main, "MotivationEngine", _Dummy)
    monkeypatch.setattr(app_main, "RoleAgent", _Dummy)
    monkeypatch.setattr(app_main, "PlanningAgent", _Dummy)
    monkeypatch.setattr(app_main, "ExpressionAgent", _Dummy)
    monkeypatch.setattr(app_main, "AffectiveAssessor", _Dummy)
    monkeypatch.setattr(app_main, "AttentionTurnCoordinator", _FakeAttentionCoordinator)

    app = FastAPI()
    async with app_main.lifespan(app):
        assert app.state.memory_repository is captured_kwargs["memory_repository"]
        assert captured_kwargs["coordination_mode"] == "durable_inbox"


class _PostgresVectorDependencyMissingSettings:
    app_env = "production"
    log_level = "INFO"
    event_debug_enabled = False
    startup_schema_mode = "migrate"
    production_policy_enforcement = "warn"
    database_url = "postgresql+asyncpg://db.example.local:5432/aion"
    reflection_runtime_mode = "in_process"
    attention_burst_window_ms = 120
    attention_answered_ttl_seconds = 5.0
    attention_stale_turn_seconds = 30.0
    semantic_vector_enabled = True
    embedding_provider = "deterministic"
    embedding_model = "deterministic-v1"
    embedding_dimensions = 32
    embedding_refresh_mode = "on_write"
    embedding_refresh_interval_seconds = 21600
    embedding_provider_ownership_enforcement = "warn"
    embedding_model_governance_enforcement = "warn"
    embedding_source_rollout_enforcement = "warn"

    @staticmethod
    def validate_required() -> None:
        return None

    @staticmethod
    def get_embedding_source_kinds() -> tuple[str, ...]:
        return ("episodic", "semantic", "affective")


async def test_lifespan_blocks_startup_before_database_init_when_pgvector_binding_is_missing_for_postgres_vectors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_initialized = False

    class _DatabaseGuard:
        def __init__(self, *_args, **_kwargs):
            nonlocal database_initialized
            database_initialized = True
            raise AssertionError("Database initialization should not run when pgvector binding is missing.")

    monkeypatch.setattr(app_main, "get_settings", lambda: _PostgresVectorDependencyMissingSettings())
    monkeypatch.setattr(app_main, "pgvector_python_binding_available", lambda: False)
    monkeypatch.setattr(app_main, "Database", _DatabaseGuard)

    with pytest.raises(RuntimeError, match="Python 'pgvector' package"):
        async with app_main.lifespan(FastAPI()):
            pass

    assert database_initialized is False
