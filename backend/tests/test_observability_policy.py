from datetime import datetime, timezone

from app.core.observability_policy import (
    build_incident_evidence_bundle_manifest,
    build_runtime_incident_evidence,
    format_incident_bundle_directory_name,
    observability_export_policy_snapshot,
)


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
        bundle_helper_available=True,
    )

    assert snapshot["incident_export_ready"] is True
    assert snapshot["incident_export_state"] == "machine_readable_export_available"
    assert snapshot["incident_export_hint"] == "exportable_incident_evidence_ready"
    assert snapshot["missing_export_capabilities"] == []
    assert snapshot["incident_evidence_bundle_contract_version"] == 1
    assert snapshot["required_bundle_files"] == [
        "manifest.json",
        "incident_evidence.json",
        "health_snapshot.json",
    ]
    assert snapshot["optional_bundle_files"] == ["behavior_validation_report.json"]
    assert snapshot["bundle_entrypoint_path"] == "scripts/export_incident_evidence_bundle.py"
    assert snapshot["bundle_helper_available"] is True


def test_build_runtime_incident_evidence_tracks_stage_timings_and_policy_surface_coverage() -> None:
    evidence = build_runtime_incident_evidence(
        trace_id="trace-123",
        event_id="evt-123",
        source="api",
        duration_ms=42,
        stage_timings_ms={"perception": 4, "action": 8, "total": 42},
        runtime_policy={"event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy"},
        memory_retrieval={"retrieval_lifecycle_policy_owner": "retrieval_lifecycle_policy"},
        learned_state={"policy_owner": "learned_state_inspection_policy"},
        v1_readiness={"policy_owner": "v1_release_readiness_policy"},
        deployment={"deployment_automation_policy_owner": "coolify_repo_deploy_automation"},
        attention={
            "attention_policy_owner": "durable_attention_inbox_policy",
            "coordination_mode": "durable_inbox",
        },
        runtime_topology_attention_switch={
            "policy_owner": "runtime_topology_finalization",
            "selected_mode": "durable_inbox",
        },
        proactive={
            "policy_owner": "proactive_runtime_policy",
            "enabled": True,
            "production_baseline_ready": True,
            "production_baseline_state": "external_scheduler_target_owner",
        },
        scheduler_external_owner_policy={"policy_owner": "external_scheduler_cadence_policy"},
        reflection_supervision={"policy_owner": "deferred_reflection_supervision_policy"},
        connectors_execution_baseline={"policy_owner": "connector_execution_baseline"},
        connectors_organizer_tool_stack={"policy_owner": "production_organizer_tool_stack"},
        connectors_web_knowledge_tools={"policy_owner": "web_knowledge_tooling_policy"},
        telegram_conversation_channel={"policy_owner": "telegram_conversation_reliability_telemetry"},
    )

    assert evidence["kind"] == "runtime_incident_evidence"
    assert evidence["schema_version"] == "1.0.0"
    assert evidence["policy_owner"] == "incident_evidence_export_policy"
    assert evidence["trace_id"] == "trace-123"
    assert evidence["event_id"] == "evt-123"
    assert evidence["duration_ms"] == 42
    assert evidence["stage_timings_ms"] == {"perception": 4, "action": 8, "total": 42}
    assert evidence["policy_surface_coverage"] == {
        "present": [
            "runtime_policy",
            "memory_retrieval",
            "learned_state",
            "v1_readiness",
            "deployment",
            "attention",
            "runtime_topology.attention_switch",
            "proactive",
            "scheduler.external_owner_policy",
            "reflection.supervision",
            "connectors.execution_baseline",
            "connectors.organizer_tool_stack",
            "connectors.web_knowledge_tools",
            "conversation_channels.telegram",
        ],
        "missing": [],
        "complete": True,
    }


def test_build_incident_evidence_bundle_manifest_uses_fixed_file_names_and_retention_posture() -> None:
    manifest = build_incident_evidence_bundle_manifest(
        base_url="http://localhost:8000/",
        capture_mode="incident",
        trace_id="trace-123",
        event_id="evt-123",
        source="api",
        captured_at=datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc),
        attached_behavior_report=True,
    )

    assert manifest["kind"] == "incident_evidence_bundle_manifest"
    assert manifest["schema_version"] == "1.0.0"
    assert manifest["policy_owner"] == "incident_evidence_export_policy"
    assert manifest["capture_mode"] == "incident"
    assert manifest["base_url"] == "http://localhost:8000"
    assert manifest["files"] == {
        "manifest": "manifest.json",
        "incident_evidence": "incident_evidence.json",
        "health_snapshot": "health_snapshot.json",
        "behavior_validation_report": "behavior_validation_report.json",
    }
    assert manifest["retention_baseline"] == {
        "keep_latest_successful_release_bundle": True,
        "keep_latest_failed_release_or_incident_bundle": True,
        "keep_active_incident_bundles_until_closure": True,
    }


def test_format_incident_bundle_directory_name_prefers_trace_id_and_utc_timestamp() -> None:
    directory_name = format_incident_bundle_directory_name(
        captured_at=datetime(2026, 4, 22, 12, 34, 56, tzinfo=timezone.utc),
        trace_id="trace:123/unsafe",
        event_id="evt-123",
    )

    assert directory_name == "20260422T123456Z_trace_123_unsafe"
