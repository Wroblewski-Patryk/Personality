from pydantic import ValidationError

from app.core.config import Settings


def test_settings_default_to_migration_first_startup_mode() -> None:
    settings = Settings(database_url="postgresql+asyncpg://u:p@localhost:5432/aion")

    assert settings.startup_schema_mode == "migrate"
    assert settings.production_policy_enforcement == "warn"
    assert settings.event_debug_enabled is None
    assert settings.event_debug_token is None
    assert settings.production_debug_token_required is True
    assert settings.event_debug_query_compat_enabled is None
    assert settings.event_debug_query_compat_recent_window == 20
    assert settings.event_debug_query_compat_stale_after_seconds == 86400
    assert settings.semantic_vector_enabled is True
    assert settings.embedding_provider == "deterministic"
    assert settings.embedding_model == "deterministic-v1"
    assert settings.embedding_dimensions == 32
    assert settings.embedding_source_kinds == "episodic,semantic,affective"
    assert settings.get_embedding_source_kinds() == ("episodic", "semantic", "affective")
    assert settings.embedding_refresh_mode == "on_write"
    assert settings.embedding_refresh_interval_seconds == 21600
    assert settings.embedding_provider_ownership_enforcement == "warn"
    assert settings.embedding_model_governance_enforcement == "warn"
    assert settings.embedding_source_rollout_enforcement == "warn"
    assert settings.reflection_runtime_mode == "in_process"
    assert settings.scheduler_enabled is False
    assert settings.reflection_interval == 900
    assert settings.maintenance_interval == 3600
    assert settings.proactive_enabled is False
    assert settings.proactive_interval == 1800
    assert settings.attention_burst_window_ms == 120
    assert settings.attention_answered_ttl_seconds == 5.0
    assert settings.attention_stale_turn_seconds == 30.0
    assert settings.is_event_debug_enabled() is True
    assert settings.is_event_debug_query_compat_enabled() is True


def test_settings_allow_explicit_compatibility_create_tables_mode() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        startup_schema_mode="create_tables",
    )

    assert settings.startup_schema_mode == "create_tables"


def test_settings_reject_unknown_startup_schema_mode() -> None:
    try:
        Settings(
            database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
            startup_schema_mode="legacy",  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        assert "startup_schema_mode" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject unknown startup schema mode.")


def test_settings_allow_disabling_event_debug_payload() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        event_debug_enabled=False,
    )

    assert settings.event_debug_enabled is False
    assert settings.is_event_debug_enabled() is False


def test_settings_default_to_debug_payload_disabled_in_production() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        app_env="production",
    )

    assert settings.event_debug_enabled is None
    assert settings.is_event_debug_enabled() is False
    assert settings.event_debug_query_compat_enabled is None
    assert settings.is_event_debug_query_compat_enabled() is False


def test_settings_default_to_strict_production_policy_enforcement_in_production_when_unset() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        app_env="production",
        event_debug_enabled=False,
    )

    assert settings.resolve_production_policy_enforcement() == "strict"


def test_settings_allow_explicit_warn_production_policy_enforcement_override_in_production() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        app_env="production",
        event_debug_enabled=False,
        production_policy_enforcement="warn",
    )

    assert settings.resolve_production_policy_enforcement() == "warn"


def test_settings_allow_explicit_debug_payload_enablement_in_production() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        app_env="production",
        event_debug_enabled=True,
    )

    assert settings.event_debug_enabled is True
    assert settings.is_event_debug_enabled() is True


def test_settings_allow_optional_event_debug_token() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        event_debug_token="debug-secret",
    )

    assert settings.event_debug_token == "debug-secret"


def test_settings_allow_explicit_debug_query_compat_enablement() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        app_env="production",
        event_debug_query_compat_enabled=True,
    )

    assert settings.event_debug_query_compat_enabled is True
    assert settings.is_event_debug_query_compat_enabled() is True


def test_settings_allow_disabling_production_debug_token_requirement() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        production_debug_token_required=False,
    )

    assert settings.production_debug_token_required is False


def test_settings_allow_explicit_debug_query_compat_recent_window() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        event_debug_query_compat_recent_window=7,
    )

    assert settings.event_debug_query_compat_recent_window == 7


def test_settings_allow_explicit_debug_query_compat_stale_after_seconds() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        event_debug_query_compat_stale_after_seconds=300,
    )

    assert settings.event_debug_query_compat_stale_after_seconds == 300


def test_settings_allow_disabling_semantic_vector_retrieval() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        semantic_vector_enabled=False,
    )

    assert settings.semantic_vector_enabled is False


def test_settings_allow_explicit_embedding_provider_model_and_dimensions() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=1536,
    )

    assert settings.embedding_provider == "openai"
    assert settings.embedding_model == "text-embedding-3-small"
    assert settings.embedding_dimensions == 1536


def test_settings_allow_explicit_embedding_source_kinds() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_source_kinds="episodic,relation",
    )

    assert settings.get_embedding_source_kinds() == ("episodic", "relation")


def test_settings_allow_explicit_embedding_refresh_mode_and_interval() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_refresh_mode="manual",
        embedding_refresh_interval_seconds=7200,
    )

    assert settings.embedding_refresh_mode == "manual"
    assert settings.embedding_refresh_interval_seconds == 7200


def test_settings_allow_strict_embedding_provider_ownership_enforcement_mode() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_provider_ownership_enforcement="strict",
    )

    assert settings.embedding_provider_ownership_enforcement == "strict"


def test_settings_allow_strict_embedding_model_governance_enforcement_mode() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_model_governance_enforcement="strict",
    )

    assert settings.embedding_model_governance_enforcement == "strict"


def test_settings_allow_strict_embedding_source_rollout_enforcement_mode() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_source_rollout_enforcement="strict",
    )

    assert settings.embedding_source_rollout_enforcement == "strict"


def test_settings_allow_strict_production_policy_enforcement_mode() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        production_policy_enforcement="strict",
    )

    assert settings.production_policy_enforcement == "strict"


def test_settings_allow_deferred_reflection_runtime_mode() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        reflection_runtime_mode="deferred",
    )

    assert settings.reflection_runtime_mode == "deferred"


def test_settings_reject_unknown_production_policy_enforcement_mode() -> None:
    try:
        Settings(
            database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
            production_policy_enforcement="legacy",  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        assert "production_policy_enforcement" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject unknown production policy enforcement mode.")


def test_settings_reject_unknown_reflection_runtime_mode() -> None:
    try:
        Settings(
            database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
            reflection_runtime_mode="legacy",  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        assert "reflection_runtime_mode" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject unknown reflection runtime mode.")


def test_settings_reject_unknown_embedding_provider_ownership_enforcement_mode() -> None:
    try:
        Settings(
            database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
            embedding_provider_ownership_enforcement="legacy",  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        assert "embedding_provider_ownership_enforcement" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError(
            "Expected Settings validation to reject unknown embedding provider ownership enforcement mode."
        )


def test_settings_reject_unknown_embedding_model_governance_enforcement_mode() -> None:
    try:
        Settings(
            database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
            embedding_model_governance_enforcement="legacy",  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        assert "embedding_model_governance_enforcement" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError(
            "Expected Settings validation to reject unknown embedding model governance enforcement mode."
        )


def test_settings_reject_unknown_embedding_source_rollout_enforcement_mode() -> None:
    try:
        Settings(
            database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
            embedding_source_rollout_enforcement="legacy",  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        assert "embedding_source_rollout_enforcement" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError(
            "Expected Settings validation to reject unknown embedding source rollout enforcement mode."
        )


def test_settings_reject_too_low_reflection_interval() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        reflection_interval=120,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "REFLECTION_INTERVAL" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject too-low reflection interval.")


def test_settings_reject_too_low_maintenance_interval() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        maintenance_interval=300,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "MAINTENANCE_INTERVAL" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject too-low maintenance interval.")


def test_settings_reject_too_low_proactive_interval() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        proactive_interval=300,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "PROACTIVE_INTERVAL" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject too-low proactive interval.")


def test_settings_reject_negative_attention_burst_window_ms() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        attention_burst_window_ms=-1,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "ATTENTION_BURST_WINDOW_MS" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject negative attention burst window.")


def test_settings_reject_too_low_attention_answered_ttl_seconds() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        attention_answered_ttl_seconds=0.1,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "ATTENTION_ANSWERED_TTL_SECONDS" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject too-low attention answered ttl.")


def test_settings_reject_attention_stale_turn_seconds_lower_than_answered_ttl() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        attention_answered_ttl_seconds=3.0,
        attention_stale_turn_seconds=2.0,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "ATTENTION_STALE_TURN_SECONDS" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError(
            "Expected Settings validation to reject attention stale-turn threshold lower than answered ttl."
        )


def test_settings_reject_too_low_event_debug_query_compat_recent_window() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        event_debug_query_compat_recent_window=0,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError(
            "Expected Settings validation to reject too-low debug query compat recent window."
        )


def test_settings_reject_too_low_event_debug_query_compat_stale_after_seconds() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        event_debug_query_compat_stale_after_seconds=0,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError(
            "Expected Settings validation to reject too-low debug query compat stale threshold."
        )


def test_settings_reject_too_low_embedding_dimensions() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_dimensions=0,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "EMBEDDING_DIMENSIONS" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject too-low embedding dimensions.")


def test_settings_reject_empty_embedding_model() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_model="   ",
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "EMBEDDING_MODEL" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject empty embedding model.")


def test_settings_reject_unknown_embedding_source_kind() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_source_kinds="episodic,unknown_kind",
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "EMBEDDING_SOURCE_KINDS" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject unknown embedding source kind.")


def test_settings_reject_too_low_embedding_refresh_interval_seconds() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        embedding_refresh_interval_seconds=59,
    )

    try:
        settings.validate_required()
    except ValueError as exc:
        assert "EMBEDDING_REFRESH_INTERVAL_SECONDS" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected Settings validation to reject too-low embedding refresh interval.")
