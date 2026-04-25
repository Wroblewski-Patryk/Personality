from __future__ import annotations

import importlib.util
import sys
from argparse import Namespace
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_behavior_validation.py"
SPEC = importlib.util.spec_from_file_location("run_behavior_validation_script", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _summary(*, total: int, passed: int, failed: int, errors: int, skipped: int, exit_code: int) -> dict[str, int]:
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "exit_code": exit_code,
    }


VALID_RETRIEVAL_INCIDENT_POSTURE = {
    "retrieval_lifecycle_policy_owner": "retrieval_lifecycle_policy",
    "semantic_embedding_provider_requested": "openai",
    "semantic_embedding_provider_effective": "openai",
    "semantic_embedding_model_requested": "text-embedding-3-small",
    "semantic_embedding_model_effective": "text-embedding-3-small",
    "semantic_embedding_execution_class": "provider_owned_openai_api",
    "semantic_embedding_production_baseline_state": "aligned_openai_provider_owned",
    "retrieval_lifecycle_provider_drift_state": "aligned_target_provider",
    "retrieval_lifecycle_alignment_state": "aligned_with_defined_lifecycle_baseline",
    "retrieval_lifecycle_pending_gaps": [],
}
VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS = [
    "T13.1",
    "T14.1",
    "T14.2",
    "T14.3",
    "T15.1",
    "T15.2",
    "T16.1",
    "T16.2",
    "T16.3",
    "T17.1",
    "T17.2",
    "T18.1",
    "T18.2",
]
VALID_V1_APPROVED_TOOL_SLICES = [
    "knowledge_search.search_web",
    "web_browser.read_page",
    "task_system.clickup_list_tasks",
    "task_system.clickup_update_task",
    "calendar.google_calendar_read_availability",
    "cloud_drive.google_drive_list_files",
]
VALID_TOOL_GROUNDED_LEARNING_POLICY = {
    "policy_owner": "tool_grounded_learning_policy",
    "capture_owner": "action_owned_external_read_summaries_only",
    "persistence_owner": "memory_conclusion_write_after_action",
    "allowed_read_operations": [
        "knowledge_search.search_web",
        "web_browser.read_page",
        "task_system.list_tasks",
        "calendar.read_availability",
        "cloud_drive.list_files",
    ],
    "execution_bypass_allowed": False,
    "self_modifying_skill_learning_allowed": False,
}


def test_ci_gate_fails_when_no_tests_collected_and_tests_are_required() -> None:
    status, violations, context = MODULE._evaluate_gate(
        gate_mode="ci",
        summary=_summary(total=0, passed=0, failed=0, errors=0, skipped=0, exit_code=0),
        ci_require_tests=True,
    )

    assert status == "fail"
    assert violations == [MODULE.GATE_REASON_NO_BEHAVIOR_TESTS_COLLECTED]
    assert context == {
        "summary_total": 0,
        "summary_failed": 0,
        "summary_errors": 0,
        "pytest_exit_code": 0,
    }


def test_ci_gate_allows_empty_collection_when_requirement_is_disabled() -> None:
    status, violations, context = MODULE._evaluate_gate(
        gate_mode="ci",
        summary=_summary(total=0, passed=0, failed=0, errors=0, skipped=0, exit_code=0),
        ci_require_tests=False,
    )

    assert status == "pass"
    assert violations == []
    assert context["summary_total"] == 0


def test_ci_gate_uses_normalized_reason_codes_for_failed_and_error_paths() -> None:
    status, violations, context = MODULE._evaluate_gate(
        gate_mode="ci",
        summary=_summary(total=4, passed=1, failed=2, errors=1, skipped=0, exit_code=1),
        ci_require_tests=True,
    )

    assert status == "fail"
    assert violations == [
        MODULE.GATE_REASON_FAILED_CASES_DETECTED,
        MODULE.GATE_REASON_ERROR_CASES_DETECTED,
        MODULE.GATE_REASON_PYTEST_EXIT_CODE_NON_ZERO,
    ]
    assert context == {
        "summary_total": 4,
        "summary_failed": 2,
        "summary_errors": 1,
        "pytest_exit_code": 1,
    }


def test_operator_gate_tracks_pytest_exit_only() -> None:
    status, violations, context = MODULE._evaluate_gate(
        gate_mode="operator",
        summary=_summary(total=0, passed=0, failed=0, errors=0, skipped=0, exit_code=1),
        ci_require_tests=True,
    )

    assert status == "fail"
    assert violations == [MODULE.GATE_REASON_PYTEST_EXIT_CODE_NON_ZERO]
    assert context["pytest_exit_code"] == 1


def test_main_includes_gate_payload_and_returns_ci_failure_on_gate_violation(
    monkeypatch,
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "behavior-report.json"

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=True,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["artifact_schema_version"] == MODULE.ARTIFACT_SCHEMA_VERSION
    assert payload["gate_reason_taxonomy_version"] == MODULE.GATE_REASON_TAXONOMY_VERSION
    assert payload["summary"]["exit_code"] == 0
    assert payload["gate"]["mode"] == "ci"
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["reason_taxonomy_version"] == MODULE.GATE_REASON_TAXONOMY_VERSION
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_NO_BEHAVIOR_TESTS_COLLECTED]
    assert payload["gate"]["violation_context"]["summary_total"] == 0
    assert payload["gate"]["violation_context"]["pytest_exit_code"] == 0
    assert payload["gate"]["ci_require_tests"] is True


def test_main_includes_gate_payload_and_keeps_operator_mode_exit_code(
    monkeypatch,
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "behavior-report.json"

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            print_artifact_json=False,
            gate_mode="operator",
            ci_require_tests=True,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["artifact_schema_version"] == MODULE.ARTIFACT_SCHEMA_VERSION
    assert payload["gate"]["mode"] == "operator"
    assert payload["gate"]["status"] == "pass"
    assert payload["gate"]["violations"] == []
    assert payload["gate"]["violation_context"]["pytest_exit_code"] == 0
    assert payload["gate"]["ci_require_tests"] is True


def test_main_evaluates_existing_artifact_without_running_pytest(
    monkeypatch,
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "existing-artifact.json"
    artifact_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "behavior_validation_artifact",
                "summary": {
                    "total": 5,
                    "passed": 5,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "exit_code": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=str(artifact_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=True,
        ),
    )
    monkeypatch.setattr(
        MODULE,
        "_run_behavior_pytest",
        lambda **_: (_ for _ in ()).throw(AssertionError("pytest should not run in artifact-input mode")),
    )

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["summary"]["total"] == 5
    assert payload["gate"]["status"] == "pass"
    assert payload["gate"]["violations"] == []
    assert payload["gate"]["violation_context"]["artifact_input_schema_version"] is None
    assert payload["gate"]["violation_context"]["expected_artifact_schema_version"] == MODULE.ARTIFACT_SCHEMA_VERSION


def test_main_fails_ci_gate_when_existing_artifact_schema_major_version_is_incompatible(
    monkeypatch,
    tmp_path: Path,
) -> None:
    input_artifact_path = tmp_path / "major-mismatch-input.json"
    output_artifact_path = tmp_path / "major-mismatch-output.json"
    input_artifact_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "behavior_validation_artifact",
                "artifact_schema_version": "2.0.0",
                "summary": {
                    "total": 5,
                    "passed": 5,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "exit_code": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(output_artifact_path),
            artifact_input_path=str(input_artifact_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=True,
        ),
    )

    exit_code = MODULE.main()

    payload = MODULE.json.loads(output_artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_ARTIFACT_SCHEMA_MAJOR_VERSION_MISMATCH]
    assert payload["gate"]["violation_context"]["artifact_input_schema_version"] == "2.0.0"
    assert payload["gate"]["violation_context"]["artifact_input_schema_major"] == 2
    assert payload["gate"]["violation_context"]["expected_artifact_schema_major"] == 1


def test_main_keeps_operator_mode_backward_compatible_for_schema_major_version_mismatch(
    monkeypatch,
    tmp_path: Path,
) -> None:
    input_artifact_path = tmp_path / "major-mismatch-input.json"
    output_artifact_path = tmp_path / "major-mismatch-output.json"
    input_artifact_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "behavior_validation_artifact",
                "artifact_schema_version": "2.0.0",
                "summary": {
                    "total": 5,
                    "passed": 5,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "exit_code": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(output_artifact_path),
            artifact_input_path=str(input_artifact_path),
            print_artifact_json=False,
            gate_mode="operator",
            ci_require_tests=True,
        ),
    )

    exit_code = MODULE.main()

    payload = MODULE.json.loads(output_artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["gate"]["status"] == "pass"
    assert payload["gate"]["violations"] == []
    assert payload["gate"]["violation_context"]["artifact_input_schema_version"] == "2.0.0"
    assert payload["gate"]["violation_context"]["artifact_input_schema_major"] == 2
    assert payload["gate"]["violation_context"]["expected_artifact_schema_major"] == 1


def test_main_marks_ci_gate_failed_when_existing_artifact_summary_is_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "invalid-artifact.json"
    artifact_path.write_text(MODULE.json.dumps({"kind": "behavior_validation_artifact"}), encoding="utf-8")

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=str(artifact_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=True,
        ),
    )

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_ARTIFACT_SUMMARY_MISSING]


def test_main_marks_artifact_input_unreadable_for_missing_artifact_path(
    monkeypatch,
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "missing-output.json"
    missing_input = tmp_path / "does-not-exist.json"

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=str(missing_input),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=True,
        ),
    )

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert MODULE.GATE_REASON_ARTIFACT_INPUT_UNREADABLE in payload["gate"]["violations"]
    assert MODULE.GATE_REASON_ARTIFACT_SUMMARY_MISSING in payload["gate"]["violations"]


def test_main_marks_artifact_summary_invalid_when_existing_summary_is_not_numeric(
    monkeypatch,
    tmp_path: Path,
) -> None:
    input_artifact_path = tmp_path / "invalid-summary-input.json"
    output_artifact_path = tmp_path / "invalid-summary-output.json"
    input_artifact_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "behavior_validation_artifact",
                "summary": {
                    "total": "x",
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "exit_code": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(output_artifact_path),
            artifact_input_path=str(input_artifact_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=True,
        ),
    )

    exit_code = MODULE.main()

    payload = MODULE.json.loads(output_artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_ARTIFACT_SUMMARY_INVALID]


def test_main_records_incident_evidence_summary_when_valid_input_is_provided(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "memory_load": 1,
                    "perception": 2,
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": True,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "break_glass_only",
                        "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                        "event_debug_query_compat_enabled": False,
                        "event_debug_shared_ingress_retirement_ready": True,
                        "event_debug_shared_ingress_sunset_ready": True,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                        "cutover_proof_ready": False,
                        "cutover_proof_state": "external_scheduler_target_only",
                        "maintenance_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "proactive_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "duplicate_protection_posture": {
                            "state": "single_owner_boundary_clear",
                        },
                    },
                    "memory_retrieval": dict(VALID_RETRIEVAL_INCIDENT_POSTURE),
                    "conversation_channels.telegram": {
                        "policy_owner": "telegram_conversation_reliability_telemetry",
                        "round_trip_state": "provider_backed_ready",
                        "bot_token_configured": True,
                    },
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                        "tool_grounded_learning": dict(VALID_TOOL_GROUNDED_LEARNING_POLICY),
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "attention": {
                        "attention_policy_owner": "durable_attention_inbox_policy",
                        "coordination_mode": "durable_inbox",
                        "deployment_readiness": {
                            "selected_coordination_mode": "durable_inbox",
                            "contract_store_state": "repository_backed_contract_store_active",
                            "store_available": True,
                        },
                    },
                    "runtime_topology.attention_switch": {
                        "policy_owner": "runtime_topology_finalization",
                        "selected_mode": "durable_inbox",
                        "production_default_change_ready": True,
                    },
                    "proactive": {
                        "policy_owner": "proactive_runtime_policy",
                        "enabled": True,
                        "production_baseline_ready": True,
                        "production_baseline_state": "external_scheduler_target_owner",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=True,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_NO_BEHAVIOR_TESTS_COLLECTED]
    assert payload["incident_evidence"] == {
        "checked": True,
        "path": str(incident_evidence_path),
        "schema_version": "1.0.0",
        "policy_owner": "incident_evidence_export_policy",
        "policy_surface_complete": True,
        "stage_count": 3,
        "debug_exception_state": "shared_debug_break_glass_only",
        "scheduler_cutover_proof_state": "external_scheduler_target_only",
        "retrieval_alignment_state": "aligned_with_defined_lifecycle_baseline",
        "retrieval_provider_drift_state": "aligned_target_provider",
    }
    assert payload["gate"]["violation_context"]["incident_evidence_policy_surface_complete"] is True
    assert payload["gate"]["violation_context"]["incident_evidence_stage_count"] == 3
    assert payload["gate"]["violation_context"]["incident_evidence_debug_admin_policy_owner"] == (
        "dedicated_admin_debug_ingress_policy"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_debug_exception_state"] == (
        "shared_debug_break_glass_only"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_telegram_conversation_policy_owner"] == (
        "telegram_conversation_reliability_telemetry"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_attention_policy_owner"] == (
        "durable_attention_inbox_policy"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_retrieval_policy_owner"] == (
        "retrieval_lifecycle_policy"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_retrieval_provider_effective"] == "openai"
    assert payload["gate"]["violation_context"]["incident_evidence_retrieval_execution_class"] == (
        "provider_owned_openai_api"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_retrieval_provider_drift_state"] == (
        "aligned_target_provider"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_retrieval_alignment_state"] == (
        "aligned_with_defined_lifecycle_baseline"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_retrieval_pending_gaps"] == []
    assert payload["gate"]["violation_context"]["incident_evidence_tool_grounded_policy_owner"] == (
        "tool_grounded_learning_policy"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_tool_grounded_capture_owner"] == (
        "action_owned_external_read_summaries_only"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_tool_grounded_allowed_read_operations"] == [
        "calendar.read_availability",
        "cloud_drive.list_files",
        "knowledge_search.search_web",
        "task_system.list_tasks",
        "web_browser.read_page",
    ]
    assert payload["gate"]["violation_context"]["incident_evidence_attention_selected_coordination_mode"] == (
        "durable_inbox"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_attention_contract_store_state"] == (
        "repository_backed_contract_store_active"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_attention_runtime_topology_policy_owner"] == (
        "runtime_topology_finalization"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_proactive_policy_owner"] == (
        "proactive_runtime_policy"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_proactive_enabled"] is True
    assert payload["gate"]["violation_context"]["incident_evidence_proactive_production_baseline_state"] == (
        "external_scheduler_target_owner"
    )


def test_main_fails_when_incident_evidence_durable_attention_posture_is_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": True,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "break_glass_only",
                        "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                        "event_debug_query_compat_enabled": False,
                        "event_debug_shared_ingress_retirement_ready": True,
                        "event_debug_shared_ingress_sunset_ready": True,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                        "cutover_proof_ready": False,
                        "cutover_proof_state": "external_scheduler_target_only",
                        "maintenance_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "proactive_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "duplicate_protection_posture": {
                            "state": "single_owner_boundary_clear",
                        },
                    },
                    "memory_retrieval": dict(VALID_RETRIEVAL_INCIDENT_POSTURE),
                    "conversation_channels.telegram": {
                        "policy_owner": "telegram_conversation_reliability_telemetry",
                        "round_trip_state": "provider_backed_ready",
                        "bot_token_configured": True,
                    },
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                        "tool_grounded_learning": dict(VALID_TOOL_GROUNDED_LEARNING_POLICY),
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "proactive": {
                        "policy_owner": "proactive_runtime_policy",
                        "enabled": True,
                        "production_baseline_ready": True,
                        "production_baseline_state": "external_scheduler_target_owner",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=False,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_INCIDENT_EVIDENCE_DURABLE_ATTENTION_INVALID]
    assert payload["gate"]["violation_context"]["incident_evidence_attention_policy_owner"] is None


def test_main_fails_when_incident_evidence_policy_surface_is_incomplete(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": False,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "break_glass_only",
                        "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                        "event_debug_query_compat_enabled": False,
                        "event_debug_shared_ingress_retirement_ready": True,
                        "event_debug_shared_ingress_sunset_ready": True,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                        "cutover_proof_ready": False,
                        "cutover_proof_state": "external_scheduler_target_only",
                        "maintenance_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "proactive_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "duplicate_protection_posture": {
                            "state": "single_owner_boundary_clear",
                        },
                    },
                    "memory_retrieval": dict(VALID_RETRIEVAL_INCIDENT_POSTURE),
                    "conversation_channels.telegram": {
                        "policy_owner": "telegram_conversation_reliability_telemetry",
                        "round_trip_state": "provider_backed_ready",
                        "bot_token_configured": True,
                    },
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                        "tool_grounded_learning": dict(VALID_TOOL_GROUNDED_LEARNING_POLICY),
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "attention": {
                        "attention_policy_owner": "durable_attention_inbox_policy",
                        "coordination_mode": "durable_inbox",
                        "deployment_readiness": {
                            "selected_coordination_mode": "durable_inbox",
                            "contract_store_state": "repository_backed_contract_store_active",
                            "store_available": True,
                        },
                    },
                    "runtime_topology.attention_switch": {
                        "policy_owner": "runtime_topology_finalization",
                        "selected_mode": "durable_inbox",
                        "production_default_change_ready": True,
                    },
                    "proactive": {
                        "policy_owner": "proactive_runtime_policy",
                        "enabled": True,
                        "production_baseline_ready": True,
                        "production_baseline_state": "external_scheduler_target_owner",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=False,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_INCIDENT_EVIDENCE_POLICY_SURFACE_INCOMPLETE]
    assert payload["incident_evidence"]["policy_surface_complete"] is False


def test_main_fails_when_incident_evidence_tool_grounded_learning_contract_is_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": True,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "break_glass_only",
                        "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                        "event_debug_query_compat_enabled": False,
                        "event_debug_shared_ingress_retirement_ready": True,
                        "event_debug_shared_ingress_sunset_ready": True,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                        "cutover_proof_ready": False,
                        "cutover_proof_state": "external_scheduler_target_only",
                        "maintenance_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "proactive_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "duplicate_protection_posture": {
                            "state": "single_owner_boundary_clear",
                        },
                    },
                    "memory_retrieval": dict(VALID_RETRIEVAL_INCIDENT_POSTURE),
                    "conversation_channels.telegram": {
                        "policy_owner": "telegram_conversation_reliability_telemetry",
                        "round_trip_state": "provider_backed_ready",
                        "bot_token_configured": True,
                    },
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "attention": {
                        "attention_policy_owner": "durable_attention_inbox_policy",
                        "coordination_mode": "durable_inbox",
                        "deployment_readiness": {
                            "selected_coordination_mode": "durable_inbox",
                            "contract_store_state": "repository_backed_contract_store_active",
                            "store_available": True,
                        },
                    },
                    "runtime_topology.attention_switch": {
                        "policy_owner": "runtime_topology_finalization",
                        "selected_mode": "durable_inbox",
                        "production_default_change_ready": True,
                    },
                    "proactive": {
                        "policy_owner": "proactive_runtime_policy",
                        "enabled": True,
                        "production_baseline_ready": True,
                        "production_baseline_state": "external_scheduler_target_owner",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=False,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_INCIDENT_EVIDENCE_V1_READINESS_INVALID]
    assert payload["gate"]["violation_context"]["incident_evidence_tool_grounded_policy_owner"] is None


def test_main_fails_when_incident_evidence_debug_posture_does_not_match_dedicated_admin_only_baseline(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": True,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "compatibility",
                        "event_debug_shared_ingress_posture": "shared_route_compatibility",
                        "event_debug_query_compat_enabled": True,
                        "event_debug_shared_ingress_retirement_ready": False,
                        "event_debug_shared_ingress_sunset_ready": False,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_still_in_compatibility_mode",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                        "cutover_proof_ready": False,
                        "cutover_proof_state": "external_scheduler_target_only",
                        "maintenance_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "proactive_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "duplicate_protection_posture": {
                            "state": "single_owner_boundary_clear",
                        },
                    },
                    "memory_retrieval": dict(VALID_RETRIEVAL_INCIDENT_POSTURE),
                    "conversation_channels.telegram": {
                        "policy_owner": "telegram_conversation_reliability_telemetry",
                        "round_trip_state": "provider_backed_ready",
                        "bot_token_configured": True,
                    },
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                        "tool_grounded_learning": dict(VALID_TOOL_GROUNDED_LEARNING_POLICY),
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "attention": {
                        "attention_policy_owner": "durable_attention_inbox_policy",
                        "coordination_mode": "durable_inbox",
                        "deployment_readiness": {
                            "selected_coordination_mode": "durable_inbox",
                            "contract_store_state": "repository_backed_contract_store_active",
                            "store_available": True,
                        },
                    },
                    "runtime_topology.attention_switch": {
                        "policy_owner": "runtime_topology_finalization",
                        "selected_mode": "durable_inbox",
                        "production_default_change_ready": True,
                    },
                    "proactive": {
                        "policy_owner": "proactive_runtime_policy",
                        "enabled": True,
                        "production_baseline_ready": True,
                        "production_baseline_state": "external_scheduler_target_owner",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=False,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [
        MODULE.GATE_REASON_INCIDENT_EVIDENCE_DEBUG_POSTURE_INVALID,
        MODULE.GATE_REASON_INCIDENT_EVIDENCE_DEBUG_EXCEPTION_STATE_INVALID,
    ]
    assert payload["incident_evidence"]["debug_exception_state"] is None


def test_main_fails_when_incident_evidence_external_cadence_cutover_proof_is_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": True,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "break_glass_only",
                        "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                        "event_debug_query_compat_enabled": False,
                        "event_debug_shared_ingress_retirement_ready": True,
                        "event_debug_shared_ingress_sunset_ready": True,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                    },
                    "memory_retrieval": dict(VALID_RETRIEVAL_INCIDENT_POSTURE),
                    "conversation_channels.telegram": {
                        "policy_owner": "telegram_conversation_reliability_telemetry",
                        "round_trip_state": "provider_backed_ready",
                        "bot_token_configured": True,
                    },
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                        "tool_grounded_learning": dict(VALID_TOOL_GROUNDED_LEARNING_POLICY),
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "attention": {
                        "attention_policy_owner": "durable_attention_inbox_policy",
                        "coordination_mode": "durable_inbox",
                        "deployment_readiness": {
                            "selected_coordination_mode": "durable_inbox",
                            "contract_store_state": "repository_backed_contract_store_active",
                            "store_available": True,
                        },
                    },
                    "runtime_topology.attention_switch": {
                        "policy_owner": "runtime_topology_finalization",
                        "selected_mode": "durable_inbox",
                        "production_default_change_ready": True,
                    },
                    "proactive": {
                        "policy_owner": "proactive_runtime_policy",
                        "enabled": True,
                        "production_baseline_ready": True,
                        "production_baseline_state": "external_scheduler_target_owner",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=False,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_INCIDENT_EVIDENCE_EXTERNAL_CADENCE_PROOF_INVALID]
    assert payload["incident_evidence"]["scheduler_cutover_proof_state"] is None


def test_main_fails_when_incident_evidence_telegram_conversation_surface_is_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": True,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "break_glass_only",
                        "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                        "event_debug_query_compat_enabled": False,
                        "event_debug_shared_ingress_retirement_ready": True,
                        "event_debug_shared_ingress_sunset_ready": True,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                        "cutover_proof_ready": False,
                        "cutover_proof_state": "external_scheduler_target_only",
                        "maintenance_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "proactive_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "duplicate_protection_posture": {
                            "state": "single_owner_boundary_clear",
                        },
                    },
                    "memory_retrieval": dict(VALID_RETRIEVAL_INCIDENT_POSTURE),
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                        "tool_grounded_learning": dict(VALID_TOOL_GROUNDED_LEARNING_POLICY),
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "attention": {
                        "attention_policy_owner": "durable_attention_inbox_policy",
                        "coordination_mode": "durable_inbox",
                        "deployment_readiness": {
                            "selected_coordination_mode": "durable_inbox",
                            "contract_store_state": "repository_backed_contract_store_active",
                            "store_available": True,
                        },
                    },
                    "runtime_topology.attention_switch": {
                        "policy_owner": "runtime_topology_finalization",
                        "selected_mode": "durable_inbox",
                        "production_default_change_ready": True,
                    },
                    "proactive": {
                        "policy_owner": "proactive_runtime_policy",
                        "enabled": True,
                        "production_baseline_ready": True,
                        "production_baseline_state": "external_scheduler_target_owner",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=False,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_INCIDENT_EVIDENCE_TELEGRAM_CONVERSATION_INVALID]
    assert payload["gate"]["violation_context"]["incident_evidence_telegram_conversation_policy_owner"] is None


def test_main_fails_when_incident_evidence_proactive_posture_is_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": True,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "break_glass_only",
                        "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                        "event_debug_query_compat_enabled": False,
                        "event_debug_shared_ingress_retirement_ready": True,
                        "event_debug_shared_ingress_sunset_ready": True,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                        "cutover_proof_ready": False,
                        "cutover_proof_state": "external_scheduler_target_only",
                        "maintenance_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "proactive_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "duplicate_protection_posture": {
                            "state": "single_owner_boundary_clear",
                        },
                    },
                    "memory_retrieval": dict(VALID_RETRIEVAL_INCIDENT_POSTURE),
                    "conversation_channels.telegram": {
                        "policy_owner": "telegram_conversation_reliability_telemetry",
                        "round_trip_state": "provider_backed_ready",
                        "bot_token_configured": True,
                    },
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                        "tool_grounded_learning": dict(VALID_TOOL_GROUNDED_LEARNING_POLICY),
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "attention": {
                        "attention_policy_owner": "durable_attention_inbox_policy",
                        "coordination_mode": "durable_inbox",
                        "deployment_readiness": {
                            "selected_coordination_mode": "durable_inbox",
                            "contract_store_state": "repository_backed_contract_store_active",
                            "store_available": True,
                        },
                    },
                    "runtime_topology.attention_switch": {
                        "policy_owner": "runtime_topology_finalization",
                        "selected_mode": "durable_inbox",
                        "production_default_change_ready": True,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=False,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_INCIDENT_EVIDENCE_PROACTIVE_INVALID]
    assert payload["gate"]["violation_context"]["incident_evidence_proactive_policy_owner"] is None


def test_main_fails_when_incident_evidence_retrieval_alignment_drifts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    incident_evidence_path = tmp_path / "incident-evidence.json"
    artifact_path = tmp_path / "behavior-report.json"
    broken_retrieval = dict(VALID_RETRIEVAL_INCIDENT_POSTURE)
    broken_retrieval["semantic_embedding_provider_effective"] = "deterministic"
    broken_retrieval["semantic_embedding_execution_class"] = "deterministic_baseline"
    broken_retrieval["semantic_embedding_production_baseline_state"] = "deterministic_compatibility_baseline"
    broken_retrieval["retrieval_lifecycle_provider_drift_state"] = "compatibility_fallback_active"
    broken_retrieval["retrieval_lifecycle_alignment_state"] = "lifecycle_gaps_present"
    broken_retrieval["retrieval_lifecycle_pending_gaps"] = ["provider_baseline_not_aligned"]
    incident_evidence_path.write_text(
        MODULE.json.dumps(
            {
                "kind": "runtime_incident_evidence",
                "schema_version": "1.0.0",
                "policy_owner": "incident_evidence_export_policy",
                "stage_timings_ms": {
                    "total": 9,
                },
                "policy_surface_coverage": {
                    "complete": True,
                },
                "policy_posture": {
                    "runtime_policy": {
                        "event_debug_admin_policy_owner": "dedicated_admin_debug_ingress_policy",
                        "event_debug_admin_ingress_target_path": "/internal/event/debug",
                        "event_debug_shared_ingress_mode": "break_glass_only",
                        "event_debug_shared_ingress_posture": "shared_route_break_glass_only",
                        "event_debug_query_compat_enabled": False,
                        "event_debug_shared_ingress_retirement_ready": True,
                        "event_debug_shared_ingress_sunset_ready": True,
                        "event_debug_shared_ingress_sunset_reason": "shared_debug_route_break_glass_only",
                    },
                    "scheduler.external_owner_policy": {
                        "policy_owner": "external_scheduler_cadence_policy",
                        "cutover_proof_owner": "external_scheduler_cutover_proof_policy",
                        "cutover_proof_ready": False,
                        "cutover_proof_state": "external_scheduler_target_only",
                        "maintenance_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "proactive_run_evidence": {
                            "evidence_state": "missing_external_run_evidence",
                        },
                        "duplicate_protection_posture": {
                            "state": "single_owner_boundary_clear",
                        },
                    },
                    "memory_retrieval": broken_retrieval,
                    "conversation_channels.telegram": {
                        "policy_owner": "telegram_conversation_reliability_telemetry",
                        "round_trip_state": "provider_backed_ready",
                        "bot_token_configured": True,
                    },
                    "learned_state": {
                        "policy_owner": "learned_state_inspection_policy",
                        "internal_inspection_path": "/internal/state/inspect",
                        "tool_grounded_learning": dict(VALID_TOOL_GROUNDED_LEARNING_POLICY),
                    },
                    "v1_readiness": {
                        "policy_owner": "v1_release_readiness_policy",
                        "product_stage": "v1_no_ui_life_assistant",
                        "conversation_gate_state": "conversation_surface_ready",
                        "learned_state_gate_state": "inspection_surface_ready",
                        "required_behavior_scenarios": VALID_V1_REQUIRED_BEHAVIOR_SCENARIOS,
                        "approved_tool_slices": VALID_V1_APPROVED_TOOL_SLICES,
                    },
                    "attention": {
                        "attention_policy_owner": "durable_attention_inbox_policy",
                        "coordination_mode": "durable_inbox",
                        "deployment_readiness": {
                            "selected_coordination_mode": "durable_inbox",
                            "contract_store_state": "repository_backed_contract_store_active",
                            "store_available": True,
                        },
                    },
                    "runtime_topology.attention_switch": {
                        "policy_owner": "runtime_topology_finalization",
                        "selected_mode": "durable_inbox",
                        "production_default_change_ready": True,
                    },
                    "proactive": {
                        "policy_owner": "proactive_runtime_policy",
                        "enabled": True,
                        "production_baseline_ready": True,
                        "production_baseline_state": "external_scheduler_target_owner",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: Namespace(
            python_exe="python",
            artifact_path=str(artifact_path),
            artifact_input_path=None,
            incident_evidence_input_path=str(incident_evidence_path),
            print_artifact_json=False,
            gate_mode="ci",
            ci_require_tests=False,
        ),
    )
    monkeypatch.setattr(MODULE, "_run_behavior_pytest", lambda **_: (0, ["python", "-m", "pytest"]))
    monkeypatch.setattr(MODULE, "_parse_junit_results", lambda **_: [])

    exit_code = MODULE.main()

    payload = MODULE.json.loads(artifact_path.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["gate"]["status"] == "fail"
    assert payload["gate"]["violations"] == [MODULE.GATE_REASON_INCIDENT_EVIDENCE_RETRIEVAL_ALIGNMENT_INVALID]
    assert payload["incident_evidence"]["retrieval_alignment_state"] == "lifecycle_gaps_present"
    assert payload["incident_evidence"]["retrieval_provider_drift_state"] == "compatibility_fallback_active"
