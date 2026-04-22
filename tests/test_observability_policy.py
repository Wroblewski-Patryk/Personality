from app.core.observability_policy import observability_export_policy_snapshot


def test_observability_export_policy_marks_local_only_posture_until_artifact_exists() -> None:
    snapshot = observability_export_policy_snapshot(
        structured_logs_available=True,
        health_surface_available=True,
        system_debug_available=True,
        export_artifact_available=False,
    )

    assert snapshot["policy_owner"] == "incident_evidence_export_policy"
    assert snapshot["incident_evidence_contract_version"] == 1
    assert snapshot["local_surfaces"] == [
        "structured_runtime_logs",
        "health_policy_surfaces",
        "system_debug_runtime_payload",
    ]
    assert snapshot["incident_export_ready"] is False
    assert snapshot["incident_export_state"] == "local_only_surfaces_pending_export_artifact"
    assert snapshot["incident_export_hint"] == "implement_machine_readable_incident_evidence_export"
    assert snapshot["missing_export_capabilities"] == [
        "machine_readable_incident_evidence_artifact",
        "machine_readable_release_evidence_attachment",
    ]


def test_observability_export_policy_marks_ready_when_machine_readable_export_exists() -> None:
    snapshot = observability_export_policy_snapshot(
        structured_logs_available=True,
        health_surface_available=True,
        system_debug_available=True,
        export_artifact_available=True,
    )

    assert snapshot["incident_export_ready"] is True
    assert snapshot["incident_export_state"] == "machine_readable_export_available"
    assert snapshot["incident_export_hint"] == "exportable_incident_evidence_ready"
    assert snapshot["missing_export_capabilities"] == []
