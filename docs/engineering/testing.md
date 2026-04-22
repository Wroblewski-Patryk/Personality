# Testing Strategy

## Current Automated Coverage

The repository currently contains lightweight backend-focused tests for:

- event normalization
- expression behavior
- end-to-end runtime pipeline composition with fake dependencies
- deployment-trigger and release-smoke script regressions

Canonical behavior-validation expectations now also live in:

- `docs/architecture/29_runtime_behavior_testing.md`

That architecture file defines when passing unit and integration tests are
still insufficient because the runtime has not yet proven memory influence,
continuity, or decision integrity across time.

Primary command:

```powershell
.\.venv\Scripts\python -m pytest -q
```

Behavior-validation command (system-debug + scenario harness baseline):

```powershell
.\scripts\run_behavior_validation.ps1 -GateMode operator
```

CI gate behavior-validation command (artifact + fail-fast gate posture):

```powershell
.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json
```

Artifact-input gate evaluation command (CI split-stage, no pytest rerun):

```powershell
.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactInputPath artifacts/behavior_validation/report.json -ArtifactPath artifacts/behavior_validation/report.gate.json
```

## Testing Layers For This Repo

- Unit tests:
  - heuristic agent logic
  - config validation
  - event normalization
  - repository helpers that can be exercised without a live service
- Integration tests:
  - FastAPI endpoints
  - database-backed memory persistence
  - Telegram/OpenAI adapter boundaries using mocks or fakes
- Manual smoke checks:
  - Docker startup
  - health endpoint
  - API roundtrip through `POST /event`
  - Telegram webhook flow in a non-production environment
- Behavior-driven system checks:
  - internal debug-mode validation of perception/context/motivation/role/plan
    and retrieved memory (`system_debug` contract surface)
  - user-simulation scenarios without debug payloads
  - persistence, continuity, and failure-mode scenarios across time

## Required Checks By Change Type

- Runtime stage changes:
  - update or add tests around changed stage outputs
  - run the full pytest suite
- API contract changes:
  - add endpoint-level coverage
  - confirm the returned serialized shape still matches expectations
- Memory or database changes:
  - add repository or integration coverage
  - verify startup table creation or migration behavior
  - when migration files change, validate the Alembic path explicitly
- Integration changes:
  - mock external providers
  - verify fallback behavior when providers are unavailable
- Release/deployment script changes:
  - add or update script-level regressions for evidence artifacts, failure
    posture, and smoke compatibility behavior
  - verify Windows PowerShell execution path in this workspace
  - keep bash logic symmetric and document when live bash execution is blocked
- Health/governance snapshot changes:
  - extend endpoint-level coverage for new policy or alignment fields
  - pin both baseline and customized-override posture when the contract is
    rollout-sensitive

## Risk Areas To Keep Honest

- placeholder values presented as real runtime facts
- hidden side effects outside `ActionExecutor`
- changes that break Telegram-specific payload handling
- changes that silently disable memory persistence
- changes that rely on live OpenAI responses in automated tests

## Evidence Preference

For meaningful repo changes, leave behind:

- the exact test command used
- pass/fail result
- a short note if coverage is still missing for a known edge case
- a scenario-level behavior note when the touched subsystem is memory,
  reflection, planning, language continuity, relation influence, or proactive
  behavior
- for release-readiness-sensitive slices, behavior validation evidence from:
  - `.\scripts\run_behavior_validation.ps1 -GateMode operator`
  - `./scripts/run_behavior_validation.sh --gate-mode operator`
- for deployment-trigger or release-smoke changes, script regression evidence
  from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py`
- for runtime-topology, adaptive-governance, planning-governance, or
  deployment-policy surface changes, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
- for retrieval-provider rollout changes, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
- for embedding execution-class diagnostics slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- for connector execution-policy slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
- for typed future-write ownership slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py tests/test_scheduler_worker.py`
- for `ActionDelivery` extensibility slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
- for compatibility-sunset readiness slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
- for shared debug-ingress vocabulary convergence slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
- for affective input and resolution diagnostics slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
- for background adaptive-output convergence slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`
- for identity/profile ownership slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
- for durable attention parity slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_memory_repository.py tests/test_config.py`
- for role-and-skill capability slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_action_executor.py`
- for retrieval-depth and theta-governance slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_role_agent.py tests/test_planning_agent.py tests/test_memory_repository.py`
- for role-selection evidence slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
- for affective rollout-policy slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`
- for reflection-scope governance slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
  - coverage should pin all three surfaces:
    - reflection writer scope selection
    - repository canonicalization/filtering for scoped vs global conclusions
    - runtime no-cross-goal leakage when scoped rows coexist with global
      adaptive outputs
- for durable attention contract-store slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  - coverage should pin:
    - repository-backed attention turn persistence
    - durable-inbox route parity with burst coalescing semantics
    - cleanup-candidate visibility and answered/stale row cleanup
- for CI-sensitive slices, behavior gate evidence from:
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - `./scripts/run_behavior_validation.sh --gate-mode ci --artifact-path artifacts/behavior_validation/report.json`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactInputPath artifacts/behavior_validation/report.json -ArtifactPath artifacts/behavior_validation/report.gate.json`
  - `./scripts/run_behavior_validation.sh --gate-mode ci --artifact-input-path artifacts/behavior_validation/report.json --artifact-path artifacts/behavior_validation/report.gate.json`
- artifact contract notes for CI parsers:
  - `artifact_schema_version` identifies schema evolution
  - `gate_reason_taxonomy_version` identifies reason-code taxonomy
  - `gate.violation_context` carries machine-readable context for gate reasons
  - CI artifact-input evaluation now blocks on incompatible
    `artifact_schema_version` major values, while operator mode remains
    backward-compatible for local inspection

Useful migration verification command:

```powershell
.\.venv\Scripts\python -m alembic upgrade head --sql
```
