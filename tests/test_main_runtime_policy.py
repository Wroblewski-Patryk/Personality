import logging
from types import SimpleNamespace

from app.main import _log_runtime_policy_warnings


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
