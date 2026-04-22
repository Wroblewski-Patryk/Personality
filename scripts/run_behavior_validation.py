from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


BEHAVIOR_TEST_TARGETS = [
    "tests/test_api_routes.py",
    "tests/test_runtime_pipeline.py",
]
BEHAVIOR_FILTER = (
    "system_debug_behavior_contract "
    "or system_debug_surface "
    "or behavior_harness_outputs_structured_contract_results "
    "or runtime_behavior_"
)
DEFAULT_ARTIFACT_PATH = Path("artifacts/behavior_validation/report.json")
ARTIFACT_SCHEMA_VERSION = "1.1.0"
GATE_REASON_TAXONOMY_VERSION = "v1"
GATE_REASON_FAILED_CASES_DETECTED = "failed_cases_detected"
GATE_REASON_ERROR_CASES_DETECTED = "error_cases_detected"
GATE_REASON_PYTEST_EXIT_CODE_NON_ZERO = "pytest_exit_code_non_zero"
GATE_REASON_NO_BEHAVIOR_TESTS_COLLECTED = "no_behavior_validation_tests_collected"
GATE_REASON_ARTIFACT_INPUT_UNREADABLE = "artifact_input_unreadable"
GATE_REASON_ARTIFACT_SUMMARY_MISSING = "artifact_summary_missing"
GATE_REASON_ARTIFACT_SUMMARY_INVALID = "artifact_summary_invalid"
GATE_REASON_ARTIFACT_SCHEMA_MAJOR_VERSION_MISMATCH = "artifact_schema_major_version_mismatch"
GATE_REASON_INCIDENT_EVIDENCE_INPUT_UNREADABLE = "incident_evidence_input_unreadable"
GATE_REASON_INCIDENT_EVIDENCE_KIND_INVALID = "incident_evidence_kind_invalid"
GATE_REASON_INCIDENT_EVIDENCE_SCHEMA_MAJOR_VERSION_MISMATCH = "incident_evidence_schema_major_version_mismatch"
GATE_REASON_INCIDENT_EVIDENCE_POLICY_SURFACE_INCOMPLETE = "incident_evidence_policy_surface_incomplete"
GATE_REASON_INCIDENT_EVIDENCE_DEBUG_POSTURE_INVALID = "incident_evidence_debug_posture_invalid"
GATE_REASON_INCIDENT_EVIDENCE_DEBUG_EXCEPTION_STATE_INVALID = "incident_evidence_debug_exception_state_invalid"


@dataclass(frozen=True)
class ValidationCaseResult:
    nodeid: str
    status: str
    reason: str
    duration_seconds: float


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run behavior-validation pytest slice and emit machine-readable artifact.",
    )
    parser.add_argument(
        "--python-exe",
        default=sys.executable,
        help="Python interpreter used to execute pytest (defaults to current interpreter).",
    )
    parser.add_argument(
        "--artifact-path",
        default=None,
        help="Path for JSON artifact output.",
    )
    parser.add_argument(
        "--artifact-input-path",
        default=None,
        help="Optional existing artifact path for local gate evaluation without running pytest.",
    )
    parser.add_argument(
        "--print-artifact-json",
        action="store_true",
        help="Also print artifact JSON payload to stdout.",
    )
    parser.add_argument(
        "--incident-evidence-input-path",
        default=None,
        help="Optional existing runtime incident-evidence JSON exported from debug-mode runtime surfaces.",
    )
    parser.add_argument(
        "--gate-mode",
        choices=("operator", "ci"),
        default="operator",
        help=(
            "Gate posture: operator keeps pytest exit-code behavior; ci enables "
            "artifact-driven gate semantics."
        ),
    )
    parser.add_argument(
        "--ci-require-tests",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="In ci mode, fail when no behavior-validation tests were collected.",
    )
    return parser.parse_args()


def _run_behavior_pytest(*, python_exe: str, junit_path: Path) -> tuple[int, list[str]]:
    cmd = [
        python_exe,
        "-m",
        "pytest",
        "-q",
        *BEHAVIOR_TEST_TARGETS,
        "-k",
        BEHAVIOR_FILTER,
        f"--junitxml={junit_path}",
    ]
    completed = subprocess.run(cmd, check=False)
    return completed.returncode, cmd


def _status_from_testcase(testcase: ElementTree.Element) -> tuple[str, str]:
    failure = testcase.find("failure")
    if failure is not None:
        return "fail", str(failure.attrib.get("message") or "failure")
    error = testcase.find("error")
    if error is not None:
        return "error", str(error.attrib.get("message") or "error")
    skipped = testcase.find("skipped")
    if skipped is not None:
        return "skip", str(skipped.attrib.get("message") or "skipped")
    return "pass", ""


def _parse_junit_results(*, junit_path: Path) -> list[ValidationCaseResult]:
    if not junit_path.exists():
        return []
    root = ElementTree.parse(junit_path).getroot()
    results: list[ValidationCaseResult] = []
    for testcase in root.iter("testcase"):
        classname = str(testcase.attrib.get("classname", "")).strip()
        name = str(testcase.attrib.get("name", "")).strip()
        nodeid = f"{classname}::{name}" if classname else name
        status, reason = _status_from_testcase(testcase)
        try:
            duration = float(testcase.attrib.get("time", 0.0) or 0.0)
        except (TypeError, ValueError):
            duration = 0.0
        results.append(
            ValidationCaseResult(
                nodeid=nodeid,
                status=status,
                reason=reason,
                duration_seconds=round(duration, 6),
            )
        )
    return results


def _artifact_payload(*, exit_code: int, pytest_cmd: list[str], results: list[ValidationCaseResult]) -> dict[str, Any]:
    counts = {
        "pass": 0,
        "fail": 0,
        "error": 0,
        "skip": 0,
    }
    for item in results:
        if item.status in counts:
            counts[item.status] += 1

    return {
        "kind": "behavior_validation_artifact",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "gate_reason_taxonomy_version": GATE_REASON_TAXONOMY_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pytest_cmd": pytest_cmd,
        "summary": {
            "total": len(results),
            "passed": counts["pass"],
            "failed": counts["fail"],
            "errors": counts["error"],
            "skipped": counts["skip"],
            "exit_code": exit_code,
        },
        "results": [
            {
                "nodeid": item.nodeid,
                "status": item.status,
                "reason": item.reason,
                "duration_seconds": item.duration_seconds,
            }
            for item in results
        ],
    }


def _evaluate_gate(
    *,
    gate_mode: str,
    summary: dict[str, int],
    ci_require_tests: bool,
) -> tuple[str, list[str], dict[str, int]]:
    context = {
        "summary_total": int(summary.get("total", 0)),
        "summary_failed": int(summary.get("failed", 0)),
        "summary_errors": int(summary.get("errors", 0)),
        "pytest_exit_code": int(summary.get("exit_code", 1)),
    }

    if gate_mode == "operator":
        if context["pytest_exit_code"] == 0:
            return "pass", [], context
        return "fail", [GATE_REASON_PYTEST_EXIT_CODE_NON_ZERO], context

    violations: list[str] = []
    if context["summary_failed"] > 0:
        violations.append(GATE_REASON_FAILED_CASES_DETECTED)
    if context["summary_errors"] > 0:
        violations.append(GATE_REASON_ERROR_CASES_DETECTED)
    if context["pytest_exit_code"] != 0:
        violations.append(GATE_REASON_PYTEST_EXIT_CODE_NON_ZERO)
    if ci_require_tests and context["summary_total"] == 0:
        violations.append(GATE_REASON_NO_BEHAVIOR_TESTS_COLLECTED)

    if violations:
        return "fail", violations, context
    return "pass", [], context


def _load_artifact_payload(*, artifact_input_path: Path) -> tuple[dict[str, Any], list[str]]:
    if not artifact_input_path.exists():
        return {}, [GATE_REASON_ARTIFACT_INPUT_UNREADABLE]

    try:
        raw = json.loads(artifact_input_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {}, [GATE_REASON_ARTIFACT_INPUT_UNREADABLE]

    if not isinstance(raw, dict):
        return {}, [GATE_REASON_ARTIFACT_INPUT_UNREADABLE]
    return dict(raw), []


def _coerce_artifact_summary(payload: dict[str, Any]) -> tuple[dict[str, int] | None, list[str]]:
    raw_summary = payload.get("summary")
    if not isinstance(raw_summary, dict):
        return None, [GATE_REASON_ARTIFACT_SUMMARY_MISSING]

    keys = ("total", "passed", "failed", "errors", "skipped", "exit_code")
    summary: dict[str, int] = {}
    try:
        for key in keys:
            summary[key] = int(raw_summary[key])
    except (KeyError, TypeError, ValueError):
        return None, [GATE_REASON_ARTIFACT_SUMMARY_INVALID]
    return summary, []


def _schema_major(version: Any) -> int | None:
    if not isinstance(version, str):
        return None
    raw = version.strip()
    if not raw:
        return None
    major_text = raw.split(".", 1)[0]
    try:
        return int(major_text)
    except ValueError:
        return None


def _load_incident_evidence_payload(*, incident_evidence_input_path: Path) -> tuple[dict[str, Any], list[str]]:
    if not incident_evidence_input_path.exists():
        return {}, [GATE_REASON_INCIDENT_EVIDENCE_INPUT_UNREADABLE]

    try:
        raw = json.loads(incident_evidence_input_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {}, [GATE_REASON_INCIDENT_EVIDENCE_INPUT_UNREADABLE]

    if not isinstance(raw, dict):
        return {}, [GATE_REASON_INCIDENT_EVIDENCE_INPUT_UNREADABLE]
    return dict(raw), []


def _evaluate_incident_evidence_input(
    *,
    incident_evidence_payload: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    expected_debug_admin_policy_owner = "dedicated_admin_debug_ingress_policy"
    expected_debug_admin_ingress_target_path = "/internal/event/debug"
    expected_debug_shared_ingress_mode = "break_glass_only"
    expected_debug_shared_ingress_posture = "shared_route_break_glass_only"
    allowed_debug_exception_reasons = {
        "shared_debug_route_break_glass_only",
        "shared_debug_route_disabled_with_debug_payload_off",
    }
    context: dict[str, Any] = {
        "incident_evidence_schema_version": incident_evidence_payload.get("schema_version"),
        "incident_evidence_schema_major": _schema_major(incident_evidence_payload.get("schema_version")),
        "expected_incident_evidence_schema_major": 1,
        "incident_evidence_policy_owner": incident_evidence_payload.get("policy_owner"),
        "incident_evidence_policy_surface_complete": False,
        "incident_evidence_stage_count": 0,
        "incident_evidence_debug_admin_policy_owner": None,
        "incident_evidence_debug_admin_ingress_target_path": None,
        "incident_evidence_debug_shared_ingress_mode": None,
        "incident_evidence_debug_shared_ingress_posture": None,
        "incident_evidence_debug_query_compat_enabled": None,
        "incident_evidence_debug_retirement_ready": None,
        "incident_evidence_debug_sunset_ready": None,
        "incident_evidence_debug_exception_reason": None,
        "incident_evidence_debug_exception_state": None,
    }
    violations: list[str] = []

    if incident_evidence_payload.get("kind") != "runtime_incident_evidence":
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_KIND_INVALID)

    schema_major = _schema_major(incident_evidence_payload.get("schema_version"))
    if schema_major is not None and schema_major != 1:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_SCHEMA_MAJOR_VERSION_MISMATCH)

    policy_surface_coverage = incident_evidence_payload.get("policy_surface_coverage")
    if isinstance(policy_surface_coverage, dict):
        context["incident_evidence_policy_surface_complete"] = bool(policy_surface_coverage.get("complete", False))
    if not context["incident_evidence_policy_surface_complete"]:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_POLICY_SURFACE_INCOMPLETE)

    stage_timings = incident_evidence_payload.get("stage_timings_ms")
    if isinstance(stage_timings, dict):
        context["incident_evidence_stage_count"] = len(stage_timings)

    runtime_policy = {}
    policy_posture = incident_evidence_payload.get("policy_posture")
    if isinstance(policy_posture, dict):
        candidate_runtime_policy = policy_posture.get("runtime_policy")
        if isinstance(candidate_runtime_policy, dict):
            runtime_policy = candidate_runtime_policy

    context["incident_evidence_debug_admin_policy_owner"] = runtime_policy.get("event_debug_admin_policy_owner")
    context["incident_evidence_debug_admin_ingress_target_path"] = runtime_policy.get(
        "event_debug_admin_ingress_target_path"
    )
    context["incident_evidence_debug_shared_ingress_mode"] = runtime_policy.get("event_debug_shared_ingress_mode")
    context["incident_evidence_debug_shared_ingress_posture"] = runtime_policy.get(
        "event_debug_shared_ingress_posture"
    )
    context["incident_evidence_debug_query_compat_enabled"] = runtime_policy.get("event_debug_query_compat_enabled")
    context["incident_evidence_debug_retirement_ready"] = runtime_policy.get(
        "event_debug_shared_ingress_retirement_ready"
    )
    context["incident_evidence_debug_sunset_ready"] = runtime_policy.get("event_debug_shared_ingress_sunset_ready")
    context["incident_evidence_debug_exception_reason"] = runtime_policy.get(
        "event_debug_shared_ingress_sunset_reason"
    )

    debug_posture_valid = (
        runtime_policy.get("event_debug_admin_policy_owner") == expected_debug_admin_policy_owner
        and runtime_policy.get("event_debug_admin_ingress_target_path") == expected_debug_admin_ingress_target_path
        and runtime_policy.get("event_debug_shared_ingress_mode") == expected_debug_shared_ingress_mode
        and runtime_policy.get("event_debug_shared_ingress_posture") == expected_debug_shared_ingress_posture
        and runtime_policy.get("event_debug_query_compat_enabled") is False
        and runtime_policy.get("event_debug_shared_ingress_retirement_ready") is True
        and runtime_policy.get("event_debug_shared_ingress_sunset_ready") is True
    )
    if not debug_posture_valid:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_DEBUG_POSTURE_INVALID)

    debug_exception_reason = runtime_policy.get("event_debug_shared_ingress_sunset_reason")
    if debug_exception_reason in allowed_debug_exception_reasons:
        context["incident_evidence_debug_exception_state"] = (
            "shared_debug_disabled"
            if debug_exception_reason == "shared_debug_route_disabled_with_debug_payload_off"
            else "shared_debug_break_glass_only"
        )
    else:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_DEBUG_EXCEPTION_STATE_INVALID)

    return violations, context


def _evaluate_artifact_schema_compatibility(
    *,
    gate_mode: str,
    artifact_schema_version: Any,
) -> tuple[list[str], dict[str, Any]]:
    input_major = _schema_major(artifact_schema_version)
    expected_major = _schema_major(ARTIFACT_SCHEMA_VERSION)
    context: dict[str, Any] = {
        "artifact_input_schema_version": artifact_schema_version,
        "artifact_input_schema_major": input_major,
        "expected_artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "expected_artifact_schema_major": expected_major,
    }

    if gate_mode != "ci":
        return [], context
    if input_major is None or expected_major is None:
        return [], context
    if input_major != expected_major:
        return [GATE_REASON_ARTIFACT_SCHEMA_MAJOR_VERSION_MISMATCH], context
    return [], context


def main() -> int:
    args = _parse_args()
    artifact_input_path = Path(args.artifact_input_path) if args.artifact_input_path else None
    incident_evidence_input_raw = getattr(args, "incident_evidence_input_path", None)
    incident_evidence_input_path = Path(incident_evidence_input_raw) if incident_evidence_input_raw else None
    if args.artifact_path:
        artifact_path = Path(args.artifact_path)
    elif artifact_input_path is not None:
        artifact_path = artifact_input_path
    else:
        artifact_path = DEFAULT_ARTIFACT_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any]
    gate_status: str
    gate_violations: list[str]
    gate_context: dict[str, Any]

    if artifact_input_path is None:
        with tempfile.NamedTemporaryFile(prefix="aion_behavior_validation_", suffix=".xml", delete=False) as handle:
            junit_path = Path(handle.name)

        exit_code, pytest_cmd = _run_behavior_pytest(
            python_exe=str(args.python_exe),
            junit_path=junit_path,
        )
        results = _parse_junit_results(junit_path=junit_path)
        payload = _artifact_payload(exit_code=exit_code, pytest_cmd=pytest_cmd, results=results)
        summary = payload["summary"]
        gate_status, gate_violations, gate_context = _evaluate_gate(
            gate_mode=str(args.gate_mode),
            summary=summary,
            ci_require_tests=bool(args.ci_require_tests),
        )
    else:
        payload, read_violations = _load_artifact_payload(artifact_input_path=artifact_input_path)
        summary, summary_violations = _coerce_artifact_summary(payload)
        schema_violations, schema_context = _evaluate_artifact_schema_compatibility(
            gate_mode=str(args.gate_mode),
            artifact_schema_version=payload.get("artifact_schema_version"),
        )
        payload["kind"] = "behavior_validation_artifact"
        payload["artifact_schema_version"] = ARTIFACT_SCHEMA_VERSION
        payload["gate_reason_taxonomy_version"] = GATE_REASON_TAXONOMY_VERSION
        payload["generated_at"] = datetime.now(timezone.utc).isoformat()

        if summary is None:
            summary = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "exit_code": 1,
            }
            payload["summary"] = summary
            gate_status = "fail"
            gate_violations = [*read_violations, *summary_violations]
            gate_context = {
                "summary_total": 0,
                "summary_failed": 0,
                "summary_errors": 0,
                "pytest_exit_code": 1,
            }
            gate_context.update(schema_context)
        else:
            payload["summary"] = summary
            gate_status, gate_violations, gate_context = _evaluate_gate(
                gate_mode=str(args.gate_mode),
                summary=summary,
                ci_require_tests=bool(args.ci_require_tests),
            )
            gate_context.update(schema_context)
            if schema_violations:
                gate_status = "fail"
                gate_violations = [*schema_violations, *gate_violations]
            if read_violations:
                gate_status = "fail"
                gate_violations = [*read_violations, *gate_violations]

    incident_evidence_summary: dict[str, Any] = {
        "checked": False,
        "path": str(incident_evidence_input_path) if incident_evidence_input_path is not None else "",
        "schema_version": None,
        "policy_owner": None,
        "policy_surface_complete": None,
        "stage_count": None,
        "debug_exception_state": None,
    }
    if incident_evidence_input_path is not None:
        incident_payload, incident_read_violations = _load_incident_evidence_payload(
            incident_evidence_input_path=incident_evidence_input_path
        )
        incident_violations: list[str] = []
        incident_context: dict[str, Any] = {}
        if not incident_read_violations:
            incident_violations, incident_context = _evaluate_incident_evidence_input(
                incident_evidence_payload=incident_payload
            )
            incident_evidence_summary = {
                "checked": True,
                "path": str(incident_evidence_input_path),
                "schema_version": incident_context.get("incident_evidence_schema_version"),
                "policy_owner": incident_context.get("incident_evidence_policy_owner"),
                "policy_surface_complete": incident_context.get("incident_evidence_policy_surface_complete"),
                "stage_count": incident_context.get("incident_evidence_stage_count"),
                "debug_exception_state": incident_context.get("incident_evidence_debug_exception_state"),
            }
        else:
            incident_evidence_summary = {
                "checked": True,
                "path": str(incident_evidence_input_path),
                "schema_version": None,
                "policy_owner": None,
                "policy_surface_complete": False,
                "stage_count": 0,
                "debug_exception_state": None,
            }
        if incident_read_violations or incident_violations:
            gate_status = "fail"
            gate_violations = [*incident_read_violations, *incident_violations, *gate_violations]
        gate_context.update(incident_context)

    payload["gate"] = {
        "mode": str(args.gate_mode),
        "status": gate_status,
        "reason_taxonomy_version": GATE_REASON_TAXONOMY_VERSION,
        "violations": gate_violations,
        "violation_context": gate_context,
        "ci_require_tests": bool(args.ci_require_tests),
    }
    payload["incident_evidence"] = incident_evidence_summary
    artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        (
            "behavior_validation_artifact "
            f"path={artifact_path} total={summary['total']} passed={summary['passed']} "
            f"failed={summary['failed']} errors={summary['errors']} skipped={summary['skipped']} "
            f"exit_code={summary['exit_code']} gate_mode={args.gate_mode} "
            f"gate_status={gate_status} gate_violations={len(gate_violations)}"
        )
    )
    if args.print_artifact_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    if str(args.gate_mode) == "ci" and gate_status != "pass":
        return 1
    return int(summary["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
