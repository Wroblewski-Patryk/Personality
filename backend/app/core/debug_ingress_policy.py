from __future__ import annotations


DEBUG_INTERNAL_ADMIN_INGRESS_PATH = "/internal/event/debug"
DEBUG_SHARED_COMPAT_INGRESS_PATH = "/event/debug"
DEBUG_QUERY_COMPAT_INGRESS_PATH = "/event?debug=true"
DEBUG_RETIREMENT_CUTOVER_POSTURE = (
    "dedicated_internal_admin_route_primary_shared_routes_break_glass_then_remove"
)
DEBUG_RETIREMENT_GATE_CHECKLIST = [
    "normal_operator_debug_uses_dedicated_internal_admin_route",
    "shared_event_debug_route_is_break_glass_only_or_disabled",
    "query_debug_compatibility_route_disabled",
    "release_smoke_green_for_dedicated_admin_debug_path",
    "rollback_notes_cover_shared_debug_break_glass_reenablement",
]


def debug_ingress_policy_snapshot() -> dict[str, object]:
    return {
        "policy_owner": "dedicated_admin_debug_ingress_policy",
        "target_admin_ingress_kind": "dedicated_internal_admin_route",
        "target_admin_ingress_path": DEBUG_INTERNAL_ADMIN_INGRESS_PATH,
        "shared_compat_ingress_path": DEBUG_SHARED_COMPAT_INGRESS_PATH,
        "query_compat_ingress_path": DEBUG_QUERY_COMPAT_INGRESS_PATH,
        "shared_compat_retirement_target": "break_glass_only_then_remove_from_normal_operator_flows",
        "shared_compat_retirement_cutover_posture": DEBUG_RETIREMENT_CUTOVER_POSTURE,
        "shared_compat_retirement_gate_checklist": list(DEBUG_RETIREMENT_GATE_CHECKLIST),
        "shared_compat_retirement_blockers": [
            "shared_clients_still_depend_on_compat_route",
            "release_smoke_not_green_for_dedicated_admin_path",
            "rollback_notes_missing_for_break_glass_posture",
        ],
        "shared_compatibility_posture": "rollback_safe_compatibility_only",
        "operator_default": "use_dedicated_admin_ingress",
        "break_glass_header": "X-AION-Debug-Break-Glass",
    }


def debug_ingress_retirement_blockers(
    *,
    debug_enabled: bool,
    shared_ingress_mode: str,
    query_compat_enabled: bool,
) -> list[str]:
    if not debug_enabled:
        return []

    blockers: list[str] = []
    if str(shared_ingress_mode) == "compatibility":
        blockers.append("shared_debug_route_still_primary")
    if bool(query_compat_enabled):
        blockers.append("query_debug_compatibility_still_enabled")
    return blockers


def debug_ingress_admin_posture_state(
    *,
    debug_enabled: bool,
    shared_ingress_mode: str,
    query_compat_enabled: bool,
) -> str:
    if not debug_enabled:
        return "debug_disabled_admin_route_primary_by_default"
    blockers = debug_ingress_retirement_blockers(
        debug_enabled=debug_enabled,
        shared_ingress_mode=shared_ingress_mode,
        query_compat_enabled=query_compat_enabled,
    )
    if blockers:
        return "transitional_shared_compatibility_active"
    return "dedicated_admin_route_primary"


def debug_ingress_retirement_gate_state(
    *,
    debug_enabled: bool,
    shared_ingress_mode: str,
    query_compat_enabled: bool,
) -> str:
    blockers = debug_ingress_retirement_blockers(
        debug_enabled=debug_enabled,
        shared_ingress_mode=shared_ingress_mode,
        query_compat_enabled=query_compat_enabled,
    )
    if not debug_enabled:
        return "shared_debug_disabled_retirement_gate_satisfied"
    if blockers:
        return "shared_debug_compatibility_retirement_blocked"
    return "shared_debug_break_glass_retirement_gate_ready"
