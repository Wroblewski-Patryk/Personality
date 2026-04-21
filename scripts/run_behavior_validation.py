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
        default=str(DEFAULT_ARTIFACT_PATH),
        help="Path for JSON artifact output.",
    )
    parser.add_argument(
        "--print-artifact-json",
        action="store_true",
        help="Also print artifact JSON payload to stdout.",
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
) -> tuple[str, list[str]]:
    if gate_mode == "operator":
        if int(summary.get("exit_code", 1)) == 0:
            return "pass", []
        return "fail", [f"pytest_exit_code_non_zero:{summary.get('exit_code', 1)}"]

    violations: list[str] = []
    if int(summary.get("failed", 0)) > 0:
        violations.append("failed_cases_detected")
    if int(summary.get("errors", 0)) > 0:
        violations.append("error_cases_detected")
    if int(summary.get("exit_code", 1)) != 0:
        violations.append(f"pytest_exit_code_non_zero:{summary.get('exit_code', 1)}")
    if ci_require_tests and int(summary.get("total", 0)) == 0:
        violations.append("no_behavior_validation_tests_collected")

    if violations:
        return "fail", violations
    return "pass", []


def main() -> int:
    args = _parse_args()
    artifact_path = Path(args.artifact_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(prefix="aion_behavior_validation_", suffix=".xml", delete=False) as handle:
        junit_path = Path(handle.name)

    exit_code, pytest_cmd = _run_behavior_pytest(
        python_exe=str(args.python_exe),
        junit_path=junit_path,
    )
    results = _parse_junit_results(junit_path=junit_path)
    payload = _artifact_payload(exit_code=exit_code, pytest_cmd=pytest_cmd, results=results)
    summary = payload["summary"]
    gate_status, gate_violations = _evaluate_gate(
        gate_mode=str(args.gate_mode),
        summary=summary,
        ci_require_tests=bool(args.ci_require_tests),
    )
    payload["gate"] = {
        "mode": str(args.gate_mode),
        "status": gate_status,
        "violations": gate_violations,
        "ci_require_tests": bool(args.ci_require_tests),
    }
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
    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
