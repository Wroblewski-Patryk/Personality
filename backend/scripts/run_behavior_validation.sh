#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
elif [[ -x "${REPO_ROOT}/.venv/Scripts/python" ]]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/Scripts/python"
else
  PYTHON_BIN="python3"
fi

ARTIFACT_PATH="artifacts/behavior_validation/report.json"
PRINT_ARTIFACT_JSON="false"
GATE_MODE="operator"
CI_REQUIRE_TESTS="true"
ARTIFACT_INPUT_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --artifact-path)
      ARTIFACT_PATH="${2:-$ARTIFACT_PATH}"
      shift 2
      ;;
    --print-artifact-json)
      PRINT_ARTIFACT_JSON="true"
      shift
      ;;
    --gate-mode)
      GATE_MODE="${2:-$GATE_MODE}"
      shift 2
      ;;
    --ci-require-tests)
      CI_REQUIRE_TESTS="true"
      shift
      ;;
    --no-ci-require-tests)
      CI_REQUIRE_TESTS="false"
      shift
      ;;
    --artifact-input-path)
      ARTIFACT_INPUT_PATH="${2:-$ARTIFACT_INPUT_PATH}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ "$GATE_MODE" != "operator" && "$GATE_MODE" != "ci" ]]; then
  echo "Invalid --gate-mode value: $GATE_MODE (expected: operator|ci)" >&2
  exit 1
fi

ARGS=(
  "${SCRIPT_DIR}/run_behavior_validation.py"
  "--python-exe" "$PYTHON_BIN"
  "--artifact-path" "$ARTIFACT_PATH"
  "--gate-mode" "$GATE_MODE"
)
if [[ -n "$ARTIFACT_INPUT_PATH" ]]; then
  ARGS+=("--artifact-input-path" "$ARTIFACT_INPUT_PATH")
fi
if [[ "$PRINT_ARTIFACT_JSON" == "true" ]]; then
  ARGS+=("--print-artifact-json")
fi
if [[ "$CI_REQUIRE_TESTS" == "true" ]]; then
  ARGS+=("--ci-require-tests")
else
  ARGS+=("--no-ci-require-tests")
fi

cd "$REPO_ROOT"
"$PYTHON_BIN" "${ARGS[@]}"
