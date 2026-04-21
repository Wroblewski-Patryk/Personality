# Testing Strategy

## Current Automated Coverage

The repository currently contains lightweight backend-focused tests for:

- event normalization
- expression behavior
- end-to-end runtime pipeline composition with fake dependencies

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
- for CI-sensitive slices, behavior gate evidence from:
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - `./scripts/run_behavior_validation.sh --gate-mode ci --artifact-path artifacts/behavior_validation/report.json`

Useful migration verification command:

```powershell
.\.venv\Scripts\python -m alembic upgrade head --sql
```
