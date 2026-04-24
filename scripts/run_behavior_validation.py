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
GATE_REASON_INCIDENT_EVIDENCE_EXTERNAL_CADENCE_PROOF_INVALID = "incident_evidence_external_cadence_proof_invalid"
GATE_REASON_INCIDENT_EVIDENCE_TELEGRAM_CONVERSATION_INVALID = "incident_evidence_telegram_conversation_invalid"
GATE_REASON_INCIDENT_EVIDENCE_V1_READINESS_INVALID = "incident_evidence_v1_readiness_invalid"
GATE_REASON_INCIDENT_EVIDENCE_DURABLE_ATTENTION_INVALID = "incident_evidence_durable_attention_invalid"
GATE_REASON_INCIDENT_EVIDENCE_PROACTIVE_INVALID = "incident_evidence_proactive_invalid"
GATE_REASON_INCIDENT_EVIDENCE_RETRIEVAL_ALIGNMENT_INVALID = "incident_evidence_retrieval_alignment_invalid"
EXPECTED_TOOL_GROUNDED_READ_OPERATIONS = {
    "knowledge_search.search_web",
    "web_browser.read_page",
    "task_system.list_tasks",
    "calendar.read_availability",
    "cloud_drive.list_files",
}


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
        "incident_evidence_scheduler_cutover_proof_owner": None,
        "incident_evidence_scheduler_cutover_proof_ready": None,
        "incident_evidence_scheduler_cutover_proof_state": None,
        "incident_evidence_scheduler_maintenance_evidence_state": None,
        "incident_evidence_scheduler_proactive_evidence_state": None,
        "incident_evidence_scheduler_duplicate_protection_state": None,
        "incident_evidence_telegram_conversation_policy_owner": None,
        "incident_evidence_telegram_conversation_round_trip_state": None,
        "incident_evidence_telegram_conversation_bot_token_configured": None,
        "incident_evidence_v1_readiness_policy_owner": None,
        "incident_evidence_v1_readiness_product_stage": None,
        "incident_evidence_v1_readiness_conversation_gate_state": None,
        "incident_evidence_v1_readiness_learned_state_gate_state": None,
        "incident_evidence_v1_time_aware_planned_work_policy_owner": None,
        "incident_evidence_v1_time_aware_planned_work_delivery_path": None,
        "incident_evidence_v1_time_aware_planned_work_recurrence_owner": None,
        "incident_evidence_v1_time_aware_planned_work_gate_state": None,
        "incident_evidence_attention_policy_owner": None,
        "incident_evidence_attention_selected_coordination_mode": None,
        "incident_evidence_attention_contract_store_state": None,
        "incident_evidence_attention_store_available": None,
        "incident_evidence_attention_runtime_topology_policy_owner": None,
        "incident_evidence_attention_runtime_topology_selected_mode": None,
        "incident_evidence_attention_runtime_topology_ready": None,
        "incident_evidence_proactive_policy_owner": None,
        "incident_evidence_proactive_enabled": None,
        "incident_evidence_proactive_production_baseline_ready": None,
        "incident_evidence_proactive_production_baseline_state": None,
        "incident_evidence_retrieval_policy_owner": None,
        "incident_evidence_retrieval_provider_requested": None,
        "incident_evidence_retrieval_provider_effective": None,
        "incident_evidence_retrieval_model_requested": None,
        "incident_evidence_retrieval_model_effective": None,
        "incident_evidence_retrieval_execution_class": None,
        "incident_evidence_retrieval_baseline_state": None,
        "incident_evidence_retrieval_provider_drift_state": None,
        "incident_evidence_retrieval_alignment_state": None,
        "incident_evidence_retrieval_pending_gaps": None,
        "incident_evidence_tool_grounded_policy_owner": None,
        "incident_evidence_tool_grounded_capture_owner": None,
        "incident_evidence_tool_grounded_persistence_owner": None,
        "incident_evidence_tool_grounded_allowed_read_operations": None,
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

    scheduler_policy = {}
    if isinstance(policy_posture, dict):
        candidate_scheduler_policy = policy_posture.get("scheduler.external_owner_policy")
        if isinstance(candidate_scheduler_policy, dict):
            scheduler_policy = candidate_scheduler_policy
    telegram_conversation_policy = {}
    if isinstance(policy_posture, dict):
        candidate_telegram_conversation_policy = policy_posture.get("conversation_channels.telegram")
        if isinstance(candidate_telegram_conversation_policy, dict):
            telegram_conversation_policy = candidate_telegram_conversation_policy
    v1_readiness_policy = {}
    if isinstance(policy_posture, dict):
        candidate_v1_readiness_policy = policy_posture.get("v1_readiness")
        if isinstance(candidate_v1_readiness_policy, dict):
            v1_readiness_policy = candidate_v1_readiness_policy
    attention_policy = {}
    if isinstance(policy_posture, dict):
        candidate_attention_policy = policy_posture.get("attention")
        if isinstance(candidate_attention_policy, dict):
            attention_policy = candidate_attention_policy
    topology_attention_policy = {}
    if isinstance(policy_posture, dict):
        candidate_topology_attention_policy = policy_posture.get("runtime_topology.attention_switch")
        if isinstance(candidate_topology_attention_policy, dict):
            topology_attention_policy = candidate_topology_attention_policy
    proactive_policy = {}
    if isinstance(policy_posture, dict):
        candidate_proactive_policy = policy_posture.get("proactive")
        if isinstance(candidate_proactive_policy, dict):
            proactive_policy = candidate_proactive_policy
    retrieval_policy = {}
    if isinstance(policy_posture, dict):
        candidate_retrieval_policy = policy_posture.get("memory_retrieval")
        if isinstance(candidate_retrieval_policy, dict):
            retrieval_policy = candidate_retrieval_policy

    maintenance_evidence = scheduler_policy.get("maintenance_run_evidence")
    proactive_evidence = scheduler_policy.get("proactive_run_evidence")
    duplicate_protection = scheduler_policy.get("duplicate_protection_posture")
    context["incident_evidence_scheduler_cutover_proof_owner"] = scheduler_policy.get("cutover_proof_owner")
    context["incident_evidence_scheduler_cutover_proof_ready"] = scheduler_policy.get("cutover_proof_ready")
    context["incident_evidence_scheduler_cutover_proof_state"] = scheduler_policy.get("cutover_proof_state")
    if isinstance(maintenance_evidence, dict):
        context["incident_evidence_scheduler_maintenance_evidence_state"] = maintenance_evidence.get(
            "evidence_state"
        )
    if isinstance(proactive_evidence, dict):
        context["incident_evidence_scheduler_proactive_evidence_state"] = proactive_evidence.get(
            "evidence_state"
        )
    if isinstance(duplicate_protection, dict):
        context["incident_evidence_scheduler_duplicate_protection_state"] = duplicate_protection.get("state")

    valid_external_cadence_states = {
        "missing_external_run_evidence",
        "stale_external_run_evidence",
        "recent_external_run_evidence",
        "recent_external_run_non_success",
    }
    valid_duplicate_protection_states = {
        "single_owner_boundary_clear",
        "app_local_conflict_detected",
    }
    external_cadence_proof_valid = (
        scheduler_policy.get("policy_owner") == "external_scheduler_cadence_policy"
        and scheduler_policy.get("cutover_proof_owner") == "external_scheduler_cutover_proof_policy"
        and isinstance(scheduler_policy.get("cutover_proof_ready"), bool)
        and isinstance(scheduler_policy.get("cutover_proof_state"), str)
        and context["incident_evidence_scheduler_maintenance_evidence_state"] in valid_external_cadence_states
        and context["incident_evidence_scheduler_proactive_evidence_state"] in valid_external_cadence_states
        and context["incident_evidence_scheduler_duplicate_protection_state"] in valid_duplicate_protection_states
    )
    if not external_cadence_proof_valid:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_EXTERNAL_CADENCE_PROOF_INVALID)

    context["incident_evidence_telegram_conversation_policy_owner"] = telegram_conversation_policy.get("policy_owner")
    context["incident_evidence_telegram_conversation_round_trip_state"] = telegram_conversation_policy.get(
        "round_trip_state"
    )
    context["incident_evidence_telegram_conversation_bot_token_configured"] = telegram_conversation_policy.get(
        "bot_token_configured"
    )
    valid_telegram_round_trip_states = {
        "provider_backed_ready",
        "missing_bot_token",
    }
    telegram_conversation_valid = (
        telegram_conversation_policy.get("policy_owner") == "telegram_conversation_reliability_telemetry"
        and telegram_conversation_policy.get("round_trip_state") in valid_telegram_round_trip_states
        and isinstance(telegram_conversation_policy.get("bot_token_configured"), bool)
    )
    if not telegram_conversation_valid:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_TELEGRAM_CONVERSATION_INVALID)

    context["incident_evidence_v1_readiness_policy_owner"] = v1_readiness_policy.get("policy_owner")
    context["incident_evidence_v1_readiness_product_stage"] = v1_readiness_policy.get("product_stage")
    context["incident_evidence_v1_readiness_conversation_gate_state"] = v1_readiness_policy.get(
        "conversation_gate_state"
    )
    context["incident_evidence_v1_readiness_learned_state_gate_state"] = v1_readiness_policy.get(
        "learned_state_gate_state"
    )
    context["incident_evidence_v1_time_aware_planned_work_policy_owner"] = v1_readiness_policy.get(
        "time_aware_planned_work_policy_owner"
    )
    context["incident_evidence_v1_time_aware_planned_work_delivery_path"] = v1_readiness_policy.get(
        "time_aware_planned_work_delivery_path"
    )
    context["incident_evidence_v1_time_aware_planned_work_recurrence_owner"] = v1_readiness_policy.get(
        "time_aware_planned_work_recurrence_owner"
    )
    context["incident_evidence_v1_time_aware_planned_work_gate_state"] = v1_readiness_policy.get(
        "time_aware_planned_work_gate_state"
    )
    learned_state_policy = {}
    if isinstance(policy_posture, dict):
        candidate_learned_state_policy = policy_posture.get("learned_state")
        if isinstance(candidate_learned_state_policy, dict):
            learned_state_policy = candidate_learned_state_policy
    tool_grounded_policy = learned_state_policy.get("tool_grounded_learning")
    if not isinstance(tool_grounded_policy, dict):
        tool_grounded_policy = {}
    context["incident_evidence_tool_grounded_policy_owner"] = tool_grounded_policy.get("policy_owner")
    context["incident_evidence_tool_grounded_capture_owner"] = tool_grounded_policy.get("capture_owner")
    context["incident_evidence_tool_grounded_persistence_owner"] = tool_grounded_policy.get("persistence_owner")
    context["incident_evidence_tool_grounded_allowed_read_operations"] = sorted(
        set(tool_grounded_policy.get("allowed_read_operations") or [])
    )
    required_behavior_scenarios = set(v1_readiness_policy.get("required_behavior_scenarios") or [])
    approved_tool_slices = set(v1_readiness_policy.get("approved_tool_slices") or [])
    tool_grounded_valid = (
        tool_grounded_policy.get("policy_owner") == "tool_grounded_learning_policy"
        and tool_grounded_policy.get("capture_owner") == "action_owned_external_read_summaries_only"
        and tool_grounded_policy.get("persistence_owner") == "memory_conclusion_write_after_action"
        and set(tool_grounded_policy.get("allowed_read_operations") or []) == EXPECTED_TOOL_GROUNDED_READ_OPERATIONS
        and tool_grounded_policy.get("execution_bypass_allowed") is False
        and tool_grounded_policy.get("self_modifying_skill_learning_allowed") is False
    )
    v1_readiness_valid = (
        v1_readiness_policy.get("policy_owner") == "v1_release_readiness_policy"
        and v1_readiness_policy.get("product_stage") == "v1_no_ui_life_assistant"
        and v1_readiness_policy.get("conversation_gate_state") == "conversation_surface_ready"
        and v1_readiness_policy.get("learned_state_gate_state") == "inspection_surface_ready"
        and {
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
            "T19.1",
            "T19.2",
        }.issubset(required_behavior_scenarios)
        and {
            "knowledge_search.search_web",
            "web_browser.read_page",
            "task_system.clickup_list_tasks",
            "task_system.clickup_update_task",
            "calendar.google_calendar_read_availability",
            "cloud_drive.google_drive_list_files",
        }.issubset(approved_tool_slices)
        and tool_grounded_valid
        and v1_readiness_policy.get("time_aware_planned_work_policy_owner")
        == "internal_time_aware_planned_work_policy"
        and v1_readiness_policy.get("time_aware_planned_work_delivery_path")
        == "attention_to_planning_to_expression_to_action"
        and v1_readiness_policy.get("time_aware_planned_work_recurrence_owner")
        == "scheduler_reevaluation_with_foreground_handoff"
        and v1_readiness_policy.get("time_aware_planned_work_gate_state")
        == "foreground_due_delivery_and_recurring_reevaluation_ready"
    )
    if not v1_readiness_valid:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_V1_READINESS_INVALID)

    attention_deployment_readiness = attention_policy.get("deployment_readiness")
    if not isinstance(attention_deployment_readiness, dict):
        attention_deployment_readiness = {}
    context["incident_evidence_attention_policy_owner"] = attention_policy.get("attention_policy_owner")
    context["incident_evidence_attention_selected_coordination_mode"] = attention_policy.get("coordination_mode")
    context["incident_evidence_attention_contract_store_state"] = attention_deployment_readiness.get(
        "contract_store_state"
    )
    context["incident_evidence_attention_store_available"] = attention_deployment_readiness.get("store_available")
    context["incident_evidence_attention_runtime_topology_policy_owner"] = topology_attention_policy.get(
        "policy_owner"
    )
    context["incident_evidence_attention_runtime_topology_selected_mode"] = topology_attention_policy.get(
        "selected_mode"
    )
    context["incident_evidence_attention_runtime_topology_ready"] = topology_attention_policy.get(
        "production_default_change_ready"
    )
    durable_attention_valid = (
        attention_policy.get("attention_policy_owner") == "durable_attention_inbox_policy"
        and attention_policy.get("coordination_mode") == "durable_inbox"
        and attention_deployment_readiness.get("selected_coordination_mode") == "durable_inbox"
        and attention_deployment_readiness.get("contract_store_state") == "repository_backed_contract_store_active"
        and attention_deployment_readiness.get("store_available") is True
        and topology_attention_policy.get("policy_owner") == "runtime_topology_finalization"
        and topology_attention_policy.get("selected_mode") == "durable_inbox"
        and topology_attention_policy.get("production_default_change_ready") is True
    )
    if not durable_attention_valid:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_DURABLE_ATTENTION_INVALID)

    context["incident_evidence_proactive_policy_owner"] = proactive_policy.get("policy_owner")
    context["incident_evidence_proactive_enabled"] = proactive_policy.get("enabled")
    context["incident_evidence_proactive_production_baseline_ready"] = proactive_policy.get(
        "production_baseline_ready"
    )
    context["incident_evidence_proactive_production_baseline_state"] = proactive_policy.get(
        "production_baseline_state"
    )
    proactive_valid = (
        proactive_policy.get("policy_owner") == "proactive_runtime_policy"
        and proactive_policy.get("enabled") is True
        and proactive_policy.get("production_baseline_ready") is True
        and proactive_policy.get("production_baseline_state") != "disabled_by_policy"
    )
    if not proactive_valid:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_PROACTIVE_INVALID)

    retrieval_pending_gaps = retrieval_policy.get("retrieval_lifecycle_pending_gaps")
    if isinstance(retrieval_pending_gaps, list):
        context["incident_evidence_retrieval_pending_gaps"] = list(retrieval_pending_gaps)
    else:
        context["incident_evidence_retrieval_pending_gaps"] = retrieval_pending_gaps
    context["incident_evidence_retrieval_policy_owner"] = retrieval_policy.get("retrieval_lifecycle_policy_owner")
    context["incident_evidence_retrieval_provider_requested"] = retrieval_policy.get(
        "semantic_embedding_provider_requested"
    )
    context["incident_evidence_retrieval_provider_effective"] = retrieval_policy.get(
        "semantic_embedding_provider_effective"
    )
    context["incident_evidence_retrieval_model_requested"] = retrieval_policy.get(
        "semantic_embedding_model_requested"
    )
    context["incident_evidence_retrieval_model_effective"] = retrieval_policy.get(
        "semantic_embedding_model_effective"
    )
    context["incident_evidence_retrieval_execution_class"] = retrieval_policy.get(
        "semantic_embedding_execution_class"
    )
    context["incident_evidence_retrieval_baseline_state"] = retrieval_policy.get(
        "semantic_embedding_production_baseline_state"
    )
    context["incident_evidence_retrieval_provider_drift_state"] = retrieval_policy.get(
        "retrieval_lifecycle_provider_drift_state"
    )
    context["incident_evidence_retrieval_alignment_state"] = retrieval_policy.get(
        "retrieval_lifecycle_alignment_state"
    )
    retrieval_alignment_valid = (
        retrieval_policy.get("retrieval_lifecycle_policy_owner") == "retrieval_lifecycle_policy"
        and retrieval_policy.get("semantic_embedding_provider_requested") == "openai"
        and retrieval_policy.get("semantic_embedding_provider_effective") == "openai"
        and retrieval_policy.get("semantic_embedding_model_requested") == "text-embedding-3-small"
        and retrieval_policy.get("semantic_embedding_model_effective") == "text-embedding-3-small"
        and retrieval_policy.get("semantic_embedding_execution_class") == "provider_owned_openai_api"
        and retrieval_policy.get("semantic_embedding_production_baseline_state")
        == "aligned_openai_provider_owned"
        and retrieval_policy.get("retrieval_lifecycle_provider_drift_state") == "aligned_target_provider"
        and retrieval_policy.get("retrieval_lifecycle_alignment_state")
        == "aligned_with_defined_lifecycle_baseline"
        and retrieval_pending_gaps == []
    )
    if not retrieval_alignment_valid:
        violations.append(GATE_REASON_INCIDENT_EVIDENCE_RETRIEVAL_ALIGNMENT_INVALID)

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
        "scheduler_cutover_proof_state": None,
        "retrieval_alignment_state": None,
        "retrieval_provider_drift_state": None,
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
                "scheduler_cutover_proof_state": incident_context.get(
                    "incident_evidence_scheduler_cutover_proof_state"
                ),
                "retrieval_alignment_state": incident_context.get(
                    "incident_evidence_retrieval_alignment_state"
                ),
                "retrieval_provider_drift_state": incident_context.get(
                    "incident_evidence_retrieval_provider_drift_state"
                ),
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
                "scheduler_cutover_proof_state": None,
                "retrieval_alignment_state": None,
                "retrieval_provider_drift_state": None,
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
