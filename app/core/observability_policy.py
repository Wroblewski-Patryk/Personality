from __future__ import annotations

OBSERVABILITY_EXPORT_POLICY_OWNER = "incident_evidence_export_policy"

REQUIRED_INCIDENT_EVIDENCE_FIELDS = (
    "trace_id",
    "event_id",
    "duration_ms",
    "stage_timings_ms",
)

REQUIRED_POLICY_POSTURE_SURFACES = (
    "runtime_policy",
    "memory_retrieval",
    "scheduler.external_owner_policy",
    "reflection.supervision",
    "connectors.execution_baseline",
)


def observability_export_policy_snapshot(
    *,
    structured_logs_available: bool,
    health_surface_available: bool,
    system_debug_available: bool,
    export_artifact_available: bool,
) -> dict[str, object]:
    local_surfaces: list[str] = []
    if structured_logs_available:
        local_surfaces.append("structured_runtime_logs")
    if health_surface_available:
        local_surfaces.append("health_policy_surfaces")
    if system_debug_available:
        local_surfaces.append("system_debug_runtime_payload")

    if export_artifact_available:
        export_state = "machine_readable_export_available"
        export_hint = "exportable_incident_evidence_ready"
        missing_capabilities: list[str] = []
    else:
        export_state = "local_only_surfaces_pending_export_artifact"
        export_hint = "implement_machine_readable_incident_evidence_export"
        missing_capabilities = [
            "machine_readable_incident_evidence_artifact",
            "machine_readable_release_evidence_attachment",
        ]

    return {
        "policy_owner": OBSERVABILITY_EXPORT_POLICY_OWNER,
        "incident_evidence_contract_version": 1,
        "required_incident_evidence_fields": list(REQUIRED_INCIDENT_EVIDENCE_FIELDS),
        "required_policy_posture_surfaces": list(REQUIRED_POLICY_POSTURE_SURFACES),
        "local_surfaces": local_surfaces,
        "export_artifact_available": export_artifact_available,
        "incident_export_ready": export_artifact_available,
        "incident_export_state": export_state,
        "incident_export_hint": export_hint,
        "missing_export_capabilities": missing_capabilities,
    }
