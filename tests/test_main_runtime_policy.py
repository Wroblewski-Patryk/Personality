import logging
from types import SimpleNamespace

from app.main import _log_embedding_strategy_warnings, _log_runtime_policy_warnings


def test_startup_logs_warning_when_production_runs_with_debug_payload_enabled(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("runtime_policy_warning" in message for message in messages)
    assert any("disable_debug_payload_in_production" in message for message in messages)
    assert any("configure_event_debug_token_when_debug_enabled" in message for message in messages)
    assert any("source=explicit" in message for message in messages)


def test_startup_logs_warning_when_production_enables_query_compat_debug_route(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        production_debug_token_required=True,
        event_debug_query_compat_enabled=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("disable_event_debug_query_compat_in_production" in message for message in messages)
    assert not any("retire_shared_debug_ingress_from_normal_production_use" in message for message in messages)


def test_startup_skips_warning_when_debug_payload_is_disabled(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=False,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("runtime_policy_warning" in message for message in messages)


def test_startup_skips_debug_warning_when_production_uses_environment_default_disable(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)

    class _Settings:
        app_env = "production"
        event_debug_enabled = None
        event_debug_token = None
        production_debug_token_required = True
        startup_schema_mode = "migrate"
        production_policy_enforcement = "warn"

        @staticmethod
        def is_event_debug_enabled() -> bool:
            return False

    _log_runtime_policy_warnings(settings=_Settings(), logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("disable_debug_payload_in_production" in message for message in messages)


def test_startup_logs_warning_when_production_runs_with_schema_compatibility_mode(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=False,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("runtime_policy_warning" in message for message in messages)
    assert any("use_migration_first_startup_in_production" in message for message in messages)


def test_startup_skips_schema_compatibility_warning_outside_production(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="development",
        event_debug_enabled=False,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("use_migration_first_startup_in_production" in message for message in messages)


def test_startup_blocks_when_strict_enforcement_and_debug_payload_enabled_in_production(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="strict",
    )

    try:
        _log_runtime_policy_warnings(settings=settings, logger=logger)
    except RuntimeError as exc:
        assert "event_debug_enabled=true" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected strict production policy enforcement to block startup.")

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("runtime_policy_block" in message for message in messages)
    assert any("violations=event_debug_enabled=true" in message for message in messages)


def test_startup_blocks_when_strict_enforcement_and_schema_compatibility_mode_in_production(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=False,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="strict",
    )

    try:
        _log_runtime_policy_warnings(settings=settings, logger=logger)
    except RuntimeError as exc:
        assert "startup_schema_mode=create_tables" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected strict production policy enforcement to block startup.")

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("runtime_policy_block" in message for message in messages)
    assert any("violations=startup_schema_mode=create_tables" in message for message in messages)


def test_startup_blocks_when_strict_enforcement_and_multiple_mismatches_in_production(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="strict",
    )

    try:
        _log_runtime_policy_warnings(settings=settings, logger=logger)
    except RuntimeError as exc:
        assert "event_debug_enabled=true" in str(exc)
        assert "event_debug_token_missing=true" in str(exc)
        assert "startup_schema_mode=create_tables" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected strict production policy enforcement to block startup.")

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("violations=event_debug_enabled=true,event_debug_token_missing=true,startup_schema_mode=create_tables" in message for message in messages)


def test_startup_blocks_when_strict_enforcement_and_query_compat_is_enabled_in_production(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        event_debug_query_compat_enabled=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="strict",
    )

    try:
        _log_runtime_policy_warnings(settings=settings, logger=logger)
    except RuntimeError as exc:
        assert "event_debug_enabled=true" in str(exc)
        assert "event_debug_query_compat_enabled=true" in str(exc)
        assert "event_debug_token_missing=true" in str(exc)
        assert "startup_schema_mode=create_tables" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected strict production policy enforcement to block startup.")

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any(
        "violations=event_debug_enabled=true,event_debug_query_compat_enabled=true,event_debug_token_missing=true,startup_schema_mode=create_tables"
        in message
        for message in messages
    )


def test_startup_warn_mode_does_not_block_when_multiple_mismatches_exist(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("runtime_policy_warning" in message for message in messages)
    assert any("disable_debug_payload_in_production" in message for message in messages)
    assert any("use_migration_first_startup_in_production" in message for message in messages)
    assert not any("runtime_policy_block" in message for message in messages)
    assert not any("runtime_policy_hint" in message for message in messages)


def test_startup_logs_strict_rollout_hint_when_production_warn_mode_is_ready(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=False,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("runtime_policy_hint" in message for message in messages)
    assert any("recommended_enforcement=strict" in message for message in messages)
    assert any("hint=can_enable_strict" in message for message in messages)
    assert any("runtime_policy_compatibility_sunset_hint" in message for message in messages)
    assert any("startup_schema_compatibility_sunset_ready=True" in message for message in messages)
    assert any("event_debug_shared_ingress_sunset_ready=True" in message for message in messages)
    assert any("compatibility_sunset_ready=True" in message for message in messages)


def test_startup_blocks_with_production_default_strict_policy_when_enforcement_is_unset(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement=None,
    )

    try:
        _log_runtime_policy_warnings(settings=settings, logger=logger)
    except RuntimeError as exc:
        assert "event_debug_enabled=true" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected production default strict policy enforcement to block startup.")


def test_startup_skips_debug_token_warning_when_debug_token_is_configured(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("disable_debug_payload_in_production" in message for message in messages)
    assert not any("configure_event_debug_token_when_debug_enabled" in message for message in messages)


def test_startup_skips_debug_token_warning_when_production_token_requirement_is_disabled(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=False,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    _log_runtime_policy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("disable_debug_payload_in_production" in message for message in messages)
    assert not any("configure_event_debug_token_when_debug_enabled" in message for message in messages)
    assert any(
        "enable_production_debug_token_requirement_or_configure_event_debug_token" in message
        for message in messages
    )


def test_startup_logs_embedding_strategy_warning_when_provider_falls_back_to_deterministic(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_strategy_warning" in message for message in messages)
    assert any("requested_provider=openai" in message for message in messages)
    assert any("effective_provider=deterministic" in message for message in messages)
    assert any("ownership_state=provider_fallback_active" in message for message in messages)
    assert any("ownership_enforcement=warn" in message for message in messages)
    assert any("ownership_enforcement_state=warning_only" in message for message in messages)
    assert any("owner_strategy_state=fallback_owner_active" in message for message in messages)
    assert not any("embedding_model_governance_warning" in message for message in messages)
    assert not any("embedding_strategy_block" in message for message in messages)


def test_startup_blocks_embedding_provider_fallback_when_ownership_enforcement_is_strict(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_provider_ownership_enforcement="strict",
    )

    try:
        _log_embedding_strategy_warnings(settings=settings, logger=logger)
    except RuntimeError as exc:
        assert "Embedding provider ownership strict-mode violation" in str(exc)
        assert "requested_provider=openai" in str(exc)
        assert "effective_provider=deterministic" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected strict provider ownership enforcement to block startup.")

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_strategy_warning" in message for message in messages)
    assert any("ownership_enforcement=strict" in message for message in messages)
    assert any("ownership_enforcement_state=blocked" in message for message in messages)
    assert any("embedding_strategy_block" in message for message in messages)


def test_startup_skips_embedding_strategy_warning_when_requested_provider_is_effective(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("embedding_strategy_warning" in message for message in messages)


def test_startup_skips_embedding_strategy_warning_when_openai_provider_is_configured(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        openai_api_key="test-openai-key",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("embedding_strategy_warning" in message for message in messages)
    assert not any("embedding_strategy_block" in message for message in messages)


def test_startup_logs_embedding_model_governance_warning_when_deterministic_custom_model_is_requested(
    caplog,
) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v2",
        embedding_source_kinds="episodic,semantic,affective",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_model_governance_warning" in message for message in messages)
    assert any("requested_model=deterministic-v2" in message for message in messages)
    assert any("governance_state=deterministic_custom_model_name" in message for message in messages)
    assert any("governance_enforcement=warn" in message for message in messages)
    assert any("governance_enforcement_state=warning_only" in message for message in messages)
    assert not any("embedding_model_governance_block" in message for message in messages)


def test_startup_blocks_deterministic_custom_model_when_governance_enforcement_is_strict(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v2",
        embedding_model_governance_enforcement="strict",
        embedding_source_kinds="episodic,semantic,affective",
    )

    try:
        _log_embedding_strategy_warnings(settings=settings, logger=logger)
    except RuntimeError as exc:
        assert "Embedding model governance strict-mode violation" in str(exc)
        assert "requested_model=deterministic-v2" in str(exc)
        assert "effective_model=deterministic-v2" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected strict model governance enforcement to block startup.")

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_model_governance_warning" in message for message in messages)
    assert any("governance_enforcement=strict" in message for message in messages)
    assert any("governance_enforcement_state=blocked" in message for message in messages)
    assert any("embedding_model_governance_block" in message for message in messages)


def test_startup_skips_embedding_model_governance_warning_for_deterministic_baseline_model(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("embedding_model_governance_warning" in message for message in messages)


def test_startup_skips_embedding_strategy_warning_when_vectors_are_disabled(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=False,
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("embedding_strategy_warning" in message for message in messages)
    assert not any("embedding_source_coverage_warning" in message for message in messages)


def test_startup_logs_embedding_source_coverage_warning_when_semantic_and_affective_sources_are_missing(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,relation",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_source_coverage_warning" in message for message in messages)
    assert any("coverage_state=missing_for_current_retrieval_path" in message for message in messages)
    assert any("rollout_state=foundational_sources_only" in message for message in messages)


def test_startup_skips_embedding_source_coverage_warning_when_semantic_and_affective_sources_are_enabled(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("embedding_source_coverage_warning" in message for message in messages)


def test_startup_logs_embedding_source_rollout_hint_when_next_source_is_pending(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_source_rollout_hint" in message for message in messages)
    assert any("rollout_next_source_kind=relation" in message for message in messages)
    assert any("rollout_completion_state=baseline_complete_relation_pending" in message for message in messages)
    assert any("rollout_progress_percent=67" in message for message in messages)


def test_startup_skips_embedding_source_rollout_hint_when_all_sources_are_enabled(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective,relation",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("embedding_source_rollout_hint" in message for message in messages)


def test_startup_logs_embedding_source_rollout_warning_when_rollout_enforcement_is_warn(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_source_rollout_enforcement="warn",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_source_rollout_warning" in message for message in messages)
    assert any("source_rollout_enforcement=warn" in message for message in messages)
    assert any("source_rollout_enforcement_state=warning_only" in message for message in messages)
    assert any("recommended_source_rollout_enforcement=warn" in message for message in messages)
    assert any("source_rollout_enforcement_alignment=aligned" in message for message in messages)
    assert any("source_rollout_enforcement_alignment_state=aligned_with_recommendation" in message for message in messages)
    assert any("rollout_next_source_kind=relation" in message for message in messages)
    assert not any("embedding_source_rollout_block" in message for message in messages)


def test_startup_blocks_embedding_source_rollout_when_enforcement_is_strict(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_source_rollout_enforcement="strict",
    )

    try:
        _log_embedding_strategy_warnings(settings=settings, logger=logger)
    except RuntimeError as exc:
        assert "Embedding source rollout strict-mode violation" in str(exc)
        assert "rollout_completion_state=baseline_complete_relation_pending" in str(exc)
        assert "next_source_kind=relation" in str(exc)
    else:  # pragma: no cover - defensive fallback
        raise AssertionError("Expected strict source rollout enforcement to block startup.")

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_source_rollout_block" in message for message in messages)
    assert any("source_rollout_enforcement=strict" in message for message in messages)
    assert any("source_rollout_enforcement_state=blocked" in message for message in messages)
    assert any("recommended_source_rollout_enforcement=warn" in message for message in messages)
    assert any("source_rollout_enforcement_alignment=above_recommendation" in message for message in messages)
    assert any("source_rollout_enforcement_alignment_state=above_recommendation" in message for message in messages)


def test_startup_logs_embedding_source_rollout_enforcement_hint_when_alignment_is_aligned(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_source_rollout_enforcement="warn",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_source_rollout_enforcement_hint" in message for message in messages)
    assert any("source_rollout_enforcement=warn" in message for message in messages)
    assert any("recommended_source_rollout_enforcement=warn" in message for message in messages)
    assert any("source_rollout_enforcement_alignment=aligned" in message for message in messages)
    assert any("source_rollout_enforcement_alignment_state=aligned_with_recommendation" in message for message in messages)


def test_startup_logs_embedding_source_rollout_enforcement_hint_when_alignment_is_below_recommendation(
    caplog,
) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective,relation",
        embedding_source_rollout_enforcement="warn",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_source_rollout_enforcement_hint" in message for message in messages)
    assert any("source_rollout_enforcement=warn" in message for message in messages)
    assert any("recommended_source_rollout_enforcement=strict" in message for message in messages)
    assert any("source_rollout_enforcement_alignment=below_recommendation" in message for message in messages)
    assert any("source_rollout_enforcement_alignment_state=below_recommendation" in message for message in messages)


def test_startup_logs_embedding_refresh_warning_when_manual_refresh_mode_is_enabled(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_refresh_mode="manual",
        embedding_refresh_interval_seconds=7200,
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_refresh_warning" in message for message in messages)
    assert any("refresh_mode=manual" in message for message in messages)
    assert any("refresh_interval_seconds=7200" in message for message in messages)
    assert any("refresh_state=manual_refresh_required" in message for message in messages)
    assert any("hint=ensure_manual_refresh_process_is_defined" in message for message in messages)
    assert any("refresh_cadence_state=manual_moderate_frequency" in message for message in messages)
    assert any("refresh_cadence_hint=manual_refresh_runs_within_daily_window" in message for message in messages)


def test_startup_skips_embedding_refresh_warning_when_on_write_refresh_mode_is_enabled(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("WARNING", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_refresh_mode="on_write",
        embedding_refresh_interval_seconds=21600,
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert not any("embedding_refresh_warning" in message for message in messages)


def test_startup_logs_embedding_refresh_hint_when_manual_mode_overrides_active_rollout_recommendation(
    caplog,
) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_refresh_mode="manual",
        embedding_refresh_interval_seconds=7200,
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_refresh_hint" in message for message in messages)
    assert any("refresh_mode=manual" in message for message in messages)
    assert any("recommended_refresh_mode=on_write" in message for message in messages)
    assert any("refresh_alignment_state=manual_override" in message for message in messages)
    assert any("refresh_cadence_state=manual_moderate_frequency" in message for message in messages)


def test_startup_logs_embedding_refresh_hint_when_on_write_precedes_manual_recommendation_for_mature_rollout(
    caplog,
) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective,relation",
        embedding_refresh_mode="on_write",
        embedding_refresh_interval_seconds=21600,
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_refresh_hint" in message for message in messages)
    assert any("refresh_mode=on_write" in message for message in messages)
    assert any("recommended_refresh_mode=manual" in message for message in messages)
    assert any("refresh_alignment_state=on_write_before_recommended_manual" in message for message in messages)


def test_startup_logs_embedding_strategy_hint_when_strict_rollout_is_ready_but_enforcement_is_warn(
    caplog,
) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_provider_ownership_enforcement="warn",
        embedding_model_governance_enforcement="warn",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_strategy_hint" in message for message in messages)
    assert any("enforcement_alignment_state=below_recommendation" in message for message in messages)
    assert any("strict_rollout_ready=True" in message for message in messages)
    assert any("recommended_provider_ownership_enforcement=strict" in message for message in messages)
    assert any("recommended_model_governance_enforcement=strict" in message for message in messages)


def test_startup_logs_embedding_strategy_hint_when_enforcement_alignment_is_aligned(caplog) -> None:
    logger_name = "aion.app"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    settings = SimpleNamespace(
        semantic_vector_enabled=True,
        embedding_provider="deterministic",
        embedding_model="deterministic-v1",
        embedding_source_kinds="episodic,semantic,affective",
        embedding_provider_ownership_enforcement="strict",
        embedding_model_governance_enforcement="strict",
    )

    _log_embedding_strategy_warnings(settings=settings, logger=logger)

    messages = [record.getMessage() for record in caplog.records if record.name == logger_name]
    assert any("embedding_strategy_hint" in message for message in messages)
    assert any("enforcement_alignment_state=aligned_with_recommendation" in message for message in messages)
    assert any("strict_rollout_state=ready" in message for message in messages)
    assert any(
        "strict_rollout_recommendation=enable_strict_provider_and_model_enforcement"
        in message
        for message in messages
    )
