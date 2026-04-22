from collections.abc import Mapping
from typing import Any, Literal

from app.core.affective_policy import affective_assessment_policy_snapshot

def app_environment(settings: Any) -> str:
    return str(getattr(settings, "app_env", "")).strip().lower()


def event_debug_enabled(settings: Any) -> bool:
    debug_toggle = getattr(settings, "is_event_debug_enabled", None)
    if callable(debug_toggle):
        return bool(debug_toggle())
    return bool(getattr(settings, "event_debug_enabled", True))


def event_debug_token_required(settings: Any) -> bool:
    token = str(getattr(settings, "event_debug_token", "") or "").strip()
    return bool(token)


def production_debug_token_required(settings: Any) -> bool:
    return bool(getattr(settings, "production_debug_token_required", True))


def event_debug_query_compat_enabled(settings: Any) -> bool:
    compat_toggle = getattr(settings, "is_event_debug_query_compat_enabled", None)
    if callable(compat_toggle):
        return bool(compat_toggle())
    compat_explicit = getattr(settings, "event_debug_query_compat_enabled", None)
    if compat_explicit is not None:
        return bool(compat_explicit)
    return app_environment(settings) != "production"


def event_debug_query_compat_source(settings: Any) -> Literal["explicit", "environment_default"]:
    if getattr(settings, "event_debug_query_compat_enabled", None) is not None:
        return "explicit"
    return "environment_default"


def event_debug_shared_ingress_mode(settings: Any) -> Literal["compatibility", "break_glass_only"]:
    explicit_mode = getattr(settings, "event_debug_shared_ingress_mode", None)
    if explicit_mode is None:
        mode = "break_glass_only" if app_environment(settings) == "production" else "compatibility"
    else:
        mode = str(explicit_mode or "compatibility").strip().lower()
    if mode == "break_glass_only":
        return "break_glass_only"
    return "compatibility"


def event_debug_shared_ingress_mode_source(settings: Any) -> Literal["explicit", "environment_default"]:
    if getattr(settings, "event_debug_shared_ingress_mode", None) is not None:
        return "explicit"
    return "environment_default"


def event_debug_shared_ingress_posture(
    settings: Any,
) -> Literal["shared_route_compatibility", "shared_route_break_glass_only"]:
    if event_debug_shared_ingress_mode(settings) == "break_glass_only":
        return "shared_route_break_glass_only"
    return "shared_route_compatibility"


def event_debug_token_missing_in_production(settings: Any) -> bool:
    return (
        app_environment(settings) == "production"
        and event_debug_enabled(settings)
        and production_debug_token_required(settings)
        and not event_debug_token_required(settings)
    )


def event_debug_query_compat_enabled_in_production(settings: Any) -> bool:
    return (
        app_environment(settings) == "production"
        and event_debug_enabled(settings)
        and event_debug_query_compat_enabled(settings)
    )


def debug_access_posture(settings: Any) -> Literal[
    "disabled",
    "token_gated",
    "production_token_required_missing",
    "open_no_token",
]:
    if not event_debug_enabled(settings):
        return "disabled"
    if event_debug_token_required(settings):
        return "token_gated"
    if app_environment(settings) == "production" and production_debug_token_required(settings):
        return "production_token_required_missing"
    return "open_no_token"


def debug_token_policy_hint(settings: Any) -> Literal[
    "not_applicable_debug_disabled",
    "token_gated",
    "configure_event_debug_token_or_disable_debug",
    "debug_access_open_without_token",
]:
    posture = debug_access_posture(settings)
    if posture == "disabled":
        return "not_applicable_debug_disabled"
    if posture == "token_gated":
        return "token_gated"
    if posture == "production_token_required_missing":
        return "configure_event_debug_token_or_disable_debug"
    return "debug_access_open_without_token"


def event_debug_source(settings: Any) -> Literal["explicit", "environment_default"]:
    if getattr(settings, "event_debug_enabled", None) is not None:
        return "explicit"
    return "environment_default"


def startup_schema_mode(settings: Any) -> str:
    return str(getattr(settings, "startup_schema_mode", "migrate")).strip().lower()


def production_policy_enforcement(settings: Any) -> Literal["warn", "strict"]:
    enforcement_resolver = getattr(settings, "resolve_production_policy_enforcement", None)
    if callable(enforcement_resolver):
        mode = str(enforcement_resolver()).strip().lower()
    else:
        explicit_mode = getattr(settings, "production_policy_enforcement", None)
        if explicit_mode is None:
            mode = "strict" if app_environment(settings) == "production" else "warn"
        else:
            mode = str(explicit_mode).strip().lower()
    if mode == "strict":
        return "strict"
    return "warn"


def production_policy_mismatches(settings: Any) -> list[str]:
    if app_environment(settings) != "production":
        return []

    violations: list[str] = []
    if event_debug_enabled(settings):
        violations.append("event_debug_enabled=true")
    if event_debug_query_compat_enabled_in_production(settings):
        violations.append("event_debug_query_compat_enabled=true")
    if event_debug_token_missing_in_production(settings):
        violations.append("event_debug_token_missing=true")
    if startup_schema_mode(settings) == "create_tables":
        violations.append("startup_schema_mode=create_tables")
    return violations


def production_policy_mismatch_count(settings: Any) -> int:
    return len(production_policy_mismatches(settings))


def strict_startup_blocked(settings: Any) -> bool:
    return production_policy_enforcement(settings) == "strict" and production_policy_mismatch_count(settings) > 0


def strict_rollout_ready(settings: Any) -> bool:
    return production_policy_mismatch_count(settings) == 0


def recommended_production_policy_enforcement(settings: Any) -> Literal["warn", "strict"]:
    if app_environment(settings) == "production" and strict_rollout_ready(settings):
        return "strict"
    return "warn"


def strict_rollout_hint(settings: Any) -> Literal[
    "not_applicable_non_production",
    "resolve_mismatches_before_strict",
    "can_enable_strict",
]:
    if app_environment(settings) != "production":
        return "not_applicable_non_production"
    if strict_rollout_ready(settings):
        return "can_enable_strict"
    return "resolve_mismatches_before_strict"


def startup_schema_compatibility_posture(
    settings: Any,
) -> Literal["migration_only", "compatibility_create_tables"]:
    if startup_schema_mode(settings) == "create_tables":
        return "compatibility_create_tables"
    return "migration_only"


def startup_schema_compatibility_sunset_ready(settings: Any) -> bool:
    return startup_schema_compatibility_posture(settings) == "migration_only"


def startup_schema_compatibility_sunset_reason(
    settings: Any,
) -> Literal["migration_only_baseline_active", "create_tables_compatibility_active"]:
    if startup_schema_compatibility_sunset_ready(settings):
        return "migration_only_baseline_active"
    return "create_tables_compatibility_active"


def event_debug_shared_ingress_sunset_ready(settings: Any) -> bool:
    if not event_debug_enabled(settings):
        return True
    return event_debug_shared_ingress_mode(settings) == "break_glass_only"


def event_debug_shared_ingress_sunset_reason(
    settings: Any,
) -> Literal[
    "shared_debug_route_disabled_with_debug_payload_off",
    "shared_debug_route_break_glass_only",
    "shared_debug_route_still_in_compatibility_mode",
]:
    if not event_debug_enabled(settings):
        return "shared_debug_route_disabled_with_debug_payload_off"
    if event_debug_shared_ingress_mode(settings) == "break_glass_only":
        return "shared_debug_route_break_glass_only"
    return "shared_debug_route_still_in_compatibility_mode"


def compatibility_sunset_blockers(settings: Any) -> list[str]:
    blockers: list[str] = []
    if not startup_schema_compatibility_sunset_ready(settings):
        blockers.append("startup_schema_compatibility_active")
    if not event_debug_shared_ingress_sunset_ready(settings):
        blockers.append("shared_debug_ingress_compatibility_mode_active")
    return blockers


def compatibility_sunset_ready(settings: Any) -> bool:
    return len(compatibility_sunset_blockers(settings)) == 0


def startup_schema_removal_window() -> str:
    return "after_group_51_release_evidence_green"


def shared_debug_ingress_enforcement_window() -> str:
    return "after_group_51_release_evidence_green"


def release_readiness_violations(runtime_policy: Mapping[str, Any]) -> list[str]:
    if runtime_policy.get("strict_rollout_hint") == "not_applicable_non_production":
        return []

    violations: list[str] = []

    mismatches = runtime_policy.get("production_policy_mismatches")
    if not isinstance(mismatches, list):
        violations.append("runtime_policy.production_policy_mismatches_missing")
    elif mismatches:
        violations.append("runtime_policy.production_policy_mismatches_non_empty")

    if "strict_startup_blocked" not in runtime_policy:
        violations.append("runtime_policy.strict_startup_blocked_missing")
    elif runtime_policy.get("strict_startup_blocked") is True:
        violations.append("runtime_policy.strict_startup_blocked=true")

    if "event_debug_query_compat_enabled" not in runtime_policy:
        violations.append("runtime_policy.event_debug_query_compat_enabled_missing")
    elif runtime_policy.get("event_debug_query_compat_enabled") is True:
        violations.append("runtime_policy.event_debug_query_compat_enabled=true")

    return violations


def release_readiness_snapshot(runtime_policy: Mapping[str, Any]) -> dict[str, Any]:
    violations = release_readiness_violations(runtime_policy)
    return {
        "ready": len(violations) == 0,
        "violations": violations,
    }


def runtime_policy_snapshot(settings: Any) -> dict[str, Any]:
    mismatches = production_policy_mismatches(settings)
    enforcement = production_policy_enforcement(settings)
    mismatch_count = len(mismatches)
    recommended_enforcement = recommended_production_policy_enforcement(settings)
    rollout_hint = strict_rollout_hint(settings)
    shared_ingress_mode = event_debug_shared_ingress_mode(settings)
    schema_sunset_posture = startup_schema_compatibility_posture(settings)
    schema_sunset_ready = startup_schema_compatibility_sunset_ready(settings)
    schema_sunset_reason = startup_schema_compatibility_sunset_reason(settings)
    shared_ingress_sunset_ready = event_debug_shared_ingress_sunset_ready(settings)
    shared_ingress_sunset_reason = event_debug_shared_ingress_sunset_reason(settings)
    sunset_blockers = compatibility_sunset_blockers(settings)
    affective_policy = affective_assessment_policy_snapshot(settings)
    return {
        **affective_policy,
        "startup_schema_mode": startup_schema_mode(settings),
        "startup_schema_compatibility_posture": schema_sunset_posture,
        "startup_schema_compatibility_sunset_ready": schema_sunset_ready,
        "startup_schema_compatibility_sunset_reason": schema_sunset_reason,
        "event_debug_enabled": event_debug_enabled(settings),
        "event_debug_token_required": event_debug_token_required(settings),
        "production_debug_token_required": production_debug_token_required(settings),
        "event_debug_query_compat_enabled": event_debug_query_compat_enabled(settings),
        "event_debug_query_compat_source": event_debug_query_compat_source(settings),
        "event_debug_ingress_owner": "internal_route_primary_shared_route_compat",
        "event_debug_internal_ingress_path": "/internal/event/debug",
        "event_debug_shared_ingress_path": "/event/debug",
        "event_debug_shared_ingress_mode": shared_ingress_mode,
        "event_debug_shared_ingress_mode_source": event_debug_shared_ingress_mode_source(settings),
        "event_debug_shared_ingress_break_glass_required": shared_ingress_mode == "break_glass_only",
        "event_debug_shared_ingress_posture": event_debug_shared_ingress_posture(settings),
        "event_debug_shared_ingress_sunset_ready": shared_ingress_sunset_ready,
        "event_debug_shared_ingress_sunset_reason": shared_ingress_sunset_reason,
        "event_debug_shared_ingress_enforcement_window": shared_debug_ingress_enforcement_window(),
        "debug_access_posture": debug_access_posture(settings),
        "debug_token_policy_hint": debug_token_policy_hint(settings),
        "event_debug_source": event_debug_source(settings),
        "production_policy_enforcement": enforcement,
        "recommended_production_policy_enforcement": recommended_enforcement,
        "production_policy_mismatches": mismatches,
        "production_policy_mismatch_count": mismatch_count,
        "strict_startup_blocked": enforcement == "strict" and mismatch_count > 0,
        "strict_rollout_ready": mismatch_count == 0,
        "strict_rollout_hint": rollout_hint,
        "startup_schema_removal_window": startup_schema_removal_window(),
        "compatibility_sunset_ready": len(sunset_blockers) == 0,
        "compatibility_sunset_blockers": sunset_blockers,
    }
