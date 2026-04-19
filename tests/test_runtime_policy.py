from types import SimpleNamespace

from app.core.runtime_policy import (
    production_policy_mismatch_count,
    recommended_production_policy_enforcement,
    runtime_policy_snapshot,
    strict_rollout_hint,
    strict_rollout_ready,
    strict_startup_blocked,
)


def test_runtime_policy_snapshot_defaults_to_no_production_mismatches_outside_production() -> None:
    settings = SimpleNamespace(
        app_env="development",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot == {
        "startup_schema_mode": "migrate",
        "event_debug_enabled": True,
        "event_debug_token_required": False,
        "production_debug_token_required": True,
        "event_debug_query_compat_enabled": True,
        "event_debug_query_compat_source": "environment_default",
        "debug_access_posture": "open_no_token",
        "debug_token_policy_hint": "debug_access_open_without_token",
        "event_debug_source": "explicit",
        "production_policy_enforcement": "warn",
        "recommended_production_policy_enforcement": "warn",
        "production_policy_mismatches": [],
        "production_policy_mismatch_count": 0,
        "strict_startup_blocked": False,
        "strict_rollout_ready": True,
        "strict_rollout_hint": "not_applicable_non_production",
    }


def test_runtime_policy_snapshot_includes_all_production_mismatches() -> None:
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        production_debug_token_required=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="strict",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["production_policy_mismatches"] == [
        "event_debug_enabled=true",
        "startup_schema_mode=create_tables",
    ]
    assert snapshot["production_policy_mismatch_count"] == 2
    assert snapshot["strict_startup_blocked"] is True
    assert snapshot["strict_rollout_ready"] is False
    assert snapshot["event_debug_token_required"] is True
    assert snapshot["event_debug_query_compat_enabled"] is False
    assert snapshot["event_debug_query_compat_source"] == "environment_default"
    assert snapshot["debug_access_posture"] == "token_gated"
    assert snapshot["debug_token_policy_hint"] == "token_gated"
    assert snapshot["recommended_production_policy_enforcement"] == "warn"
    assert snapshot["strict_rollout_hint"] == "resolve_mismatches_before_strict"
    assert snapshot["production_policy_enforcement"] == "strict"


def test_runtime_policy_snapshot_marks_event_debug_source_as_environment_default_when_unset() -> None:
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

    snapshot = runtime_policy_snapshot(_Settings())

    assert snapshot["event_debug_enabled"] is False
    assert snapshot["event_debug_source"] == "environment_default"
    assert snapshot["production_debug_token_required"] is True
    assert snapshot["event_debug_query_compat_enabled"] is False
    assert snapshot["event_debug_query_compat_source"] == "environment_default"
    assert snapshot["debug_access_posture"] == "disabled"
    assert snapshot["debug_token_policy_hint"] == "not_applicable_debug_disabled"
    assert snapshot["production_policy_mismatches"] == []
    assert snapshot["production_policy_mismatch_count"] == 0
    assert snapshot["strict_startup_blocked"] is False
    assert snapshot["strict_rollout_ready"] is True
    assert snapshot["recommended_production_policy_enforcement"] == "strict"
    assert snapshot["strict_rollout_hint"] == "can_enable_strict"
    assert snapshot["event_debug_token_required"] is False


def test_strict_startup_blocked_is_false_when_warn_mode_has_mismatches() -> None:
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="warn",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["production_policy_mismatches"] == [
        "event_debug_enabled=true",
        "event_debug_token_missing=true",
        "startup_schema_mode=create_tables",
    ]
    assert production_policy_mismatch_count(settings) == 3
    assert strict_startup_blocked(settings) is False
    assert strict_rollout_ready(settings) is False
    assert strict_rollout_hint(settings) == "resolve_mismatches_before_strict"
    assert recommended_production_policy_enforcement(settings) == "warn"


def test_recommended_enforcement_is_strict_for_production_when_no_mismatches() -> None:
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=False,
        event_debug_token="debug-secret",
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    assert strict_rollout_ready(settings) is True
    assert strict_rollout_hint(settings) == "can_enable_strict"
    assert recommended_production_policy_enforcement(settings) == "strict"


def test_runtime_policy_snapshot_marks_debug_token_required_when_token_is_set() -> None:
    settings = SimpleNamespace(
        app_env="development",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        production_debug_token_required=False,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["event_debug_token_required"] is True
    assert snapshot["production_debug_token_required"] is False
    assert snapshot["event_debug_query_compat_enabled"] is True
    assert snapshot["event_debug_query_compat_source"] == "environment_default"
    assert snapshot["debug_access_posture"] == "token_gated"
    assert snapshot["debug_token_policy_hint"] == "token_gated"


def test_runtime_policy_snapshot_marks_production_token_required_missing_when_debug_enabled_without_token() -> None:
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["event_debug_enabled"] is True
    assert snapshot["event_debug_token_required"] is False
    assert snapshot["production_debug_token_required"] is True
    assert snapshot["event_debug_query_compat_enabled"] is False
    assert snapshot["event_debug_query_compat_source"] == "environment_default"
    assert snapshot["debug_access_posture"] == "production_token_required_missing"
    assert snapshot["debug_token_policy_hint"] == "configure_event_debug_token_or_disable_debug"
    assert snapshot["production_policy_mismatches"] == [
        "event_debug_enabled=true",
        "event_debug_token_missing=true",
    ]
    assert snapshot["production_policy_mismatch_count"] == 2
    assert snapshot["strict_rollout_ready"] is False


def test_runtime_policy_snapshot_marks_query_compat_as_explicit_mismatch_when_enabled_in_production() -> None:
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        production_debug_token_required=True,
        event_debug_query_compat_enabled=True,
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["event_debug_query_compat_enabled"] is True
    assert snapshot["event_debug_query_compat_source"] == "explicit"
    assert snapshot["production_policy_mismatches"] == [
        "event_debug_enabled=true",
        "event_debug_query_compat_enabled=true",
    ]
    assert snapshot["production_policy_mismatch_count"] == 2


def test_runtime_policy_snapshot_includes_query_compat_and_token_missing_when_both_apply() -> None:
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token=None,
        production_debug_token_required=True,
        event_debug_query_compat_enabled=True,
        startup_schema_mode="create_tables",
        production_policy_enforcement="warn",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["production_policy_mismatches"] == [
        "event_debug_enabled=true",
        "event_debug_query_compat_enabled=true",
        "event_debug_token_missing=true",
        "startup_schema_mode=create_tables",
    ]
    assert snapshot["production_policy_mismatch_count"] == 4
