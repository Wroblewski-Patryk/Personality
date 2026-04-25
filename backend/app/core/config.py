from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.memory.embeddings import normalize_embedding_source_kinds


class Settings(BaseSettings):
    app_build_revision: str = "unknown"
    deployment_trigger_mode: Literal[
        "source_automation",
        "webhook_manual_fallback",
        "ui_manual_fallback",
    ] = "source_automation"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    telegram_bot_token: str | None = None
    telegram_webhook_secret: str | None = None
    database_url: str | None = None
    clickup_api_token: str | None = None
    clickup_list_id: str | None = None
    google_calendar_access_token: str | None = None
    google_calendar_calendar_id: str | None = None
    google_calendar_timezone: str = "UTC"
    google_drive_access_token: str | None = None
    google_drive_folder_id: str | None = None
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "INFO"
    affective_assessment_enabled: bool | None = None
    event_debug_enabled: bool | None = None
    event_debug_token: str | None = None
    production_debug_token_required: bool = True
    event_debug_query_compat_enabled: bool | None = None
    event_debug_shared_ingress_mode: Literal["compatibility", "break_glass_only"] = "break_glass_only"
    event_debug_query_compat_recent_window: int = 20
    event_debug_query_compat_stale_after_seconds: int = 86400
    semantic_vector_enabled: bool = True
    embedding_provider: Literal["deterministic", "local_hybrid", "openai"] = "deterministic"
    embedding_model: str = "deterministic-v1"
    embedding_dimensions: int = 32
    embedding_source_kinds: str = "episodic,semantic,affective"
    embedding_refresh_mode: Literal["on_write", "manual"] = "on_write"
    embedding_refresh_interval_seconds: int = 21600
    embedding_provider_ownership_enforcement: Literal["warn", "strict"] = "warn"
    embedding_model_governance_enforcement: Literal["warn", "strict"] = "warn"
    embedding_source_rollout_enforcement: Literal["warn", "strict"] = "warn"
    startup_schema_mode: Literal["migrate", "create_tables"] = "migrate"
    production_policy_enforcement: Literal["warn", "strict"] = "warn"
    reflection_runtime_mode: Literal["in_process", "deferred"] = "in_process"
    scheduler_execution_mode: Literal["in_process", "externalized"] = "in_process"
    scheduler_enabled: bool = False
    reflection_interval: int = 900
    maintenance_interval: int = 3600
    proactive_enabled: bool = False
    proactive_interval: int = 1800
    attention_coordination_mode: Literal["in_process", "durable_inbox"] = "in_process"
    attention_burst_window_ms: int = 120
    attention_answered_ttl_seconds: float = 5.0
    attention_stale_turn_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def validate_required(self) -> None:
        environment = self.app_env.lower()
        if environment in {"testing", "test"}:
            return

        missing: list[str] = []
        if not self.database_url:
            missing.append("DATABASE_URL")
        if environment == "production":
            if not self.openai_api_key:
                missing.append("OPENAI_API_KEY")
            if not self.telegram_bot_token:
                missing.append("TELEGRAM_BOT_TOKEN")
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Missing required environment variables: {joined}")

        if self.reflection_interval < 300:
            raise ValueError("REFLECTION_INTERVAL must be at least 300 seconds.")
        if self.maintenance_interval < 900:
            raise ValueError("MAINTENANCE_INTERVAL must be at least 900 seconds.")
        if self.proactive_interval < 1800:
            raise ValueError("PROACTIVE_INTERVAL must be at least 1800 seconds.")
        if self.attention_burst_window_ms < 0:
            raise ValueError("ATTENTION_BURST_WINDOW_MS must be greater than or equal to 0.")
        if self.attention_answered_ttl_seconds < 0.5:
            raise ValueError("ATTENTION_ANSWERED_TTL_SECONDS must be at least 0.5 seconds.")
        if self.attention_stale_turn_seconds < self.attention_answered_ttl_seconds:
            raise ValueError(
                "ATTENTION_STALE_TURN_SECONDS must be greater than or equal to ATTENTION_ANSWERED_TTL_SECONDS."
            )
        if self.event_debug_query_compat_recent_window < 1:
            raise ValueError("EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW must be at least 1.")
        if self.event_debug_query_compat_stale_after_seconds < 1:
            raise ValueError("EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS must be at least 1.")
        if self.embedding_dimensions < 1:
            raise ValueError("EMBEDDING_DIMENSIONS must be at least 1.")
        if not str(self.embedding_model).strip():
            raise ValueError("EMBEDDING_MODEL must be a non-empty string.")
        normalize_embedding_source_kinds(self.embedding_source_kinds)
        if self.embedding_refresh_interval_seconds < 60:
            raise ValueError("EMBEDDING_REFRESH_INTERVAL_SECONDS must be at least 60.")

    def is_event_debug_enabled(self) -> bool:
        if self.event_debug_enabled is not None:
            return self.event_debug_enabled
        return self.app_env.lower() != "production"

    def is_affective_assessment_enabled(self) -> bool:
        if self.affective_assessment_enabled is not None:
            return self.affective_assessment_enabled
        return self.app_env.lower() != "production"

    def is_event_debug_query_compat_enabled(self) -> bool:
        if self.event_debug_query_compat_enabled is not None:
            return self.event_debug_query_compat_enabled
        return False

    def resolve_production_policy_enforcement(self) -> Literal["warn", "strict"]:
        mode = str(self.production_policy_enforcement).strip().lower()
        if "production_policy_enforcement" not in self.model_fields_set:
            return "strict" if self.app_env.lower() == "production" else "warn"
        if mode == "strict":
            return "strict"
        return "warn"

    def get_embedding_source_kinds(self) -> tuple[str, ...]:
        return normalize_embedding_source_kinds(self.embedding_source_kinds)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
