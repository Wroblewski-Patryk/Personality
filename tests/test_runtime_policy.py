from types import SimpleNamespace

from app.core.config import Settings
from app.core.runtime_policy import (
    compatibility_sunset_blockers,
    compatibility_sunset_ready,
    event_debug_shared_ingress_sunset_reason,
    event_debug_shared_ingress_sunset_ready,
    production_policy_mismatch_count,
    recommended_production_policy_enforcement,
    release_readiness_snapshot,
    release_readiness_violations,
    runtime_policy_snapshot,
    startup_schema_compatibility_posture,
    startup_schema_compatibility_sunset_reason,
    startup_schema_compatibility_sunset_ready,
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
        "affective_assessment_enabled": True,
        "affective_assessment_source": "environment_default",
        "affective_classifier_available": False,
        "affective_assessment_posture": "fallback_only_classifier_unavailable",
        "affective_assessment_hint": "configure_openai_api_key_or_disable_ai_affective_assessment",
        "affective_assessment_owner": "affective_assessment_rollout_policy",
        "startup_schema_mode": "migrate",
        "startup_schema_compatibility_posture": "migration_only",
        "startup_schema_compatibility_sunset_ready": True,
        "startup_schema_compatibility_sunset_reason": "migration_only_baseline_active",
        "event_debug_enabled": True,
        "event_debug_token_required": False,
        "production_debug_token_required": True,
        "event_debug_query_compat_enabled": True,
        "event_debug_query_compat_source": "environment_default",
        "event_debug_ingress_owner": "internal_route_primary_shared_route_compat",
        "event_debug_internal_ingress_path": "/internal/event/debug",
        "event_debug_shared_ingress_path": "/event/debug",
        "event_debug_shared_ingress_mode": "compatibility",
        "event_debug_shared_ingress_mode_source": "environment_default",
        "event_debug_shared_ingress_break_glass_required": False,
        "event_debug_shared_ingress_posture": "shared_route_compatibility",
        "event_debug_shared_ingress_sunset_ready": False,
        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_still_in_compatibility_mode",
        "event_debug_shared_ingress_enforcement_window": "after_group_51_release_evidence_green",
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
        "startup_schema_removal_window": "after_group_51_release_evidence_green",
        "compatibility_sunset_ready": False,
        "compatibility_sunset_blockers": ["shared_debug_ingress_compatibility_mode_active"],
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
    assert snapshot["event_debug_ingress_owner"] == "internal_route_primary_shared_route_compat"
    assert snapshot["event_debug_internal_ingress_path"] == "/internal/event/debug"
    assert snapshot["event_debug_shared_ingress_path"] == "/event/debug"
    assert snapshot["event_debug_shared_ingress_mode"] == "break_glass_only"
    assert snapshot["event_debug_shared_ingress_mode_source"] == "environment_default"
    assert snapshot["event_debug_shared_ingress_break_glass_required"] is True
    assert snapshot["event_debug_shared_ingress_posture"] == "shared_route_break_glass_only"
    assert snapshot["event_debug_shared_ingress_sunset_ready"] is True
    assert snapshot["event_debug_shared_ingress_sunset_reason"] == "shared_debug_route_break_glass_only"
    assert snapshot["event_debug_shared_ingress_enforcement_window"] == "after_group_51_release_evidence_green"
    assert snapshot["debug_access_posture"] == "token_gated"
    assert snapshot["debug_token_policy_hint"] == "token_gated"
    assert snapshot["affective_assessment_enabled"] is False
    assert snapshot["affective_assessment_source"] == "environment_default"
    assert snapshot["affective_classifier_available"] is False
    assert snapshot["affective_assessment_posture"] == "fallback_only_policy_disabled"
    assert snapshot["recommended_production_policy_enforcement"] == "warn"
    assert snapshot["strict_rollout_hint"] == "resolve_mismatches_before_strict"
    assert snapshot["production_policy_enforcement"] == "strict"
    assert snapshot["startup_schema_compatibility_posture"] == "compatibility_create_tables"
    assert snapshot["startup_schema_compatibility_sunset_ready"] is False
    assert snapshot["startup_schema_compatibility_sunset_reason"] == "create_tables_compatibility_active"
    assert snapshot["compatibility_sunset_ready"] is False
    assert snapshot["compatibility_sunset_blockers"] == [
        "startup_schema_compatibility_active",
    ]


def test_runtime_policy_snapshot_defaults_to_strict_enforcement_for_production_settings_when_unset() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        app_env="production",
        event_debug_enabled=False,
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["production_policy_enforcement"] == "strict"
    assert snapshot["production_policy_mismatches"] == []
    assert snapshot["strict_startup_blocked"] is False
    assert snapshot["strict_rollout_ready"] is True


def test_runtime_policy_snapshot_respects_explicit_warn_override_for_production_settings() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost:5432/aion",
        app_env="production",
        event_debug_enabled=False,
        production_policy_enforcement="warn",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["production_policy_enforcement"] == "warn"
    assert snapshot["production_policy_mismatches"] == []
    assert snapshot["strict_startup_blocked"] is False
    assert snapshot["strict_rollout_ready"] is True


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
    assert snapshot["event_debug_ingress_owner"] == "internal_route_primary_shared_route_compat"
    assert snapshot["event_debug_internal_ingress_path"] == "/internal/event/debug"
    assert snapshot["event_debug_shared_ingress_path"] == "/event/debug"
    assert snapshot["event_debug_shared_ingress_mode"] == "break_glass_only"
    assert snapshot["event_debug_shared_ingress_mode_source"] == "environment_default"
    assert snapshot["event_debug_shared_ingress_break_glass_required"] is True
    assert snapshot["event_debug_shared_ingress_posture"] == "shared_route_break_glass_only"
    assert snapshot["event_debug_shared_ingress_sunset_ready"] is True
    assert (
        snapshot["event_debug_shared_ingress_sunset_reason"]
        == "shared_debug_route_disabled_with_debug_payload_off"
    )
    assert snapshot["event_debug_shared_ingress_enforcement_window"] == "after_group_51_release_evidence_green"
    assert snapshot["debug_access_posture"] == "disabled"
    assert snapshot["debug_token_policy_hint"] == "not_applicable_debug_disabled"
    assert snapshot["affective_assessment_enabled"] is False
    assert snapshot["affective_assessment_source"] == "environment_default"
    assert snapshot["affective_classifier_available"] is False
    assert snapshot["affective_assessment_posture"] == "fallback_only_policy_disabled"
    assert snapshot["production_policy_mismatches"] == []
    assert snapshot["production_policy_mismatch_count"] == 0
    assert snapshot["strict_startup_blocked"] is False
    assert snapshot["strict_rollout_ready"] is True
    assert snapshot["recommended_production_policy_enforcement"] == "strict"
    assert snapshot["strict_rollout_hint"] == "can_enable_strict"
    assert snapshot["event_debug_token_required"] is False
    assert snapshot["startup_schema_compatibility_posture"] == "migration_only"
    assert snapshot["startup_schema_compatibility_sunset_ready"] is True
    assert snapshot["startup_schema_compatibility_sunset_reason"] == "migration_only_baseline_active"
    assert snapshot["startup_schema_removal_window"] == "after_group_51_release_evidence_green"
    assert snapshot["compatibility_sunset_ready"] is True
    assert snapshot["compatibility_sunset_blockers"] == []


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


def test_runtime_policy_snapshot_marks_break_glass_shared_ingress_posture() -> None:
    settings = SimpleNamespace(
        app_env="development",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        production_debug_token_required=False,
        event_debug_shared_ingress_mode="break_glass_only",
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    snapshot = runtime_policy_snapshot(settings)

    assert snapshot["event_debug_shared_ingress_mode"] == "break_glass_only"
    assert snapshot["event_debug_shared_ingress_break_glass_required"] is True
    assert snapshot["event_debug_shared_ingress_posture"] == "shared_route_break_glass_only"
    assert snapshot["event_debug_shared_ingress_sunset_ready"] is True
    assert snapshot["event_debug_shared_ingress_sunset_reason"] == "shared_debug_route_break_glass_only"
    assert snapshot["compatibility_sunset_ready"] is True
    assert snapshot["compatibility_sunset_blockers"] == []


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


def test_release_readiness_snapshot_is_ready_when_release_gates_pass() -> None:
    runtime_policy = {
        "production_policy_mismatches": [],
        "strict_startup_blocked": False,
        "event_debug_query_compat_enabled": False,
    }

    readiness = release_readiness_snapshot(runtime_policy)

    assert readiness == {
        "ready": True,
        "violations": [],
    }


def test_release_readiness_snapshot_is_not_ready_when_release_gates_fail() -> None:
    runtime_policy = {
        "production_policy_mismatches": ["event_debug_enabled=true"],
        "strict_startup_blocked": True,
        "event_debug_query_compat_enabled": True,
    }

    readiness = release_readiness_snapshot(runtime_policy)

    assert readiness["ready"] is False
    assert readiness["violations"] == [
        "runtime_policy.production_policy_mismatches_non_empty",
        "runtime_policy.strict_startup_blocked=true",
        "runtime_policy.event_debug_query_compat_enabled=true",
    ]


def test_release_readiness_violations_include_missing_required_gate_fields() -> None:
    runtime_policy = {}

    violations = release_readiness_violations(runtime_policy)

    assert violations == [
        "runtime_policy.production_policy_mismatches_missing",
        "runtime_policy.strict_startup_blocked_missing",
        "runtime_policy.event_debug_query_compat_enabled_missing",
    ]


def test_release_readiness_violations_are_not_applicable_outside_production() -> None:
    runtime_policy = {
        "strict_rollout_hint": "not_applicable_non_production",
        "production_policy_mismatches": [],
        "strict_startup_blocked": False,
        "event_debug_query_compat_enabled": True,
    }

    assert release_readiness_violations(runtime_policy) == []


def test_compatibility_sunset_helpers_mark_create_tables_and_shared_compat_as_not_ready() -> None:
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        production_debug_token_required=True,
        event_debug_shared_ingress_mode="compatibility",
        startup_schema_mode="create_tables",
        production_policy_enforcement="warn",
    )

    assert startup_schema_compatibility_posture(settings) == "compatibility_create_tables"
    assert startup_schema_compatibility_sunset_ready(settings) is False
    assert startup_schema_compatibility_sunset_reason(settings) == "create_tables_compatibility_active"
    assert event_debug_shared_ingress_sunset_ready(settings) is False
    assert (
        event_debug_shared_ingress_sunset_reason(settings)
        == "shared_debug_route_still_in_compatibility_mode"
    )
    assert compatibility_sunset_blockers(settings) == [
        "startup_schema_compatibility_active",
        "shared_debug_ingress_compatibility_mode_active",
    ]
    assert compatibility_sunset_ready(settings) is False


def test_compatibility_sunset_helpers_mark_migration_only_and_break_glass_as_ready() -> None:
    settings = SimpleNamespace(
        app_env="production",
        event_debug_enabled=True,
        event_debug_token="debug-secret",
        production_debug_token_required=True,
        event_debug_shared_ingress_mode="break_glass_only",
        startup_schema_mode="migrate",
        production_policy_enforcement="warn",
    )

    assert startup_schema_compatibility_posture(settings) == "migration_only"
    assert startup_schema_compatibility_sunset_ready(settings) is True
    assert startup_schema_compatibility_sunset_reason(settings) == "migration_only_baseline_active"
    assert event_debug_shared_ingress_sunset_ready(settings) is True
    assert event_debug_shared_ingress_sunset_reason(settings) == "shared_debug_route_break_glass_only"
    assert compatibility_sunset_blockers(settings) == []
    assert compatibility_sunset_ready(settings) is True
