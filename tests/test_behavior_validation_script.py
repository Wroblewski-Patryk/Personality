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
    }
    assert payload["gate"]["violation_context"]["incident_evidence_policy_surface_complete"] is True
    assert payload["gate"]["violation_context"]["incident_evidence_stage_count"] == 3
    assert payload["gate"]["violation_context"]["incident_evidence_debug_admin_policy_owner"] == (
        "dedicated_admin_debug_ingress_policy"
    )
    assert payload["gate"]["violation_context"]["incident_evidence_debug_exception_state"] == (
        "shared_debug_break_glass_only"
    )


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
