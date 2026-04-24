# Task

## Header
- ID: PRJ-610
- Title: Add release and regression evidence for the capability catalog
- Status: DONE
- Owner: QA/Test
- Depends on: PRJ-609
- Priority: P1

## Context
The backend capability catalog is now exposed for future UI/admin callers, but
release and regression evidence still need to prove that the catalog stays
stable across `/health`, bundle validation, and test fixtures.

## Goal
Pin the bounded capability-catalog contract in targeted regressions and release
smoke so future UI bootstrap work can trust the backend surface.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] release smoke validates the bounded capability-catalog contract from live
      `/health`.
- [x] incident-evidence bundle validation validates the same capability-catalog
      contract from `health_snapshot.json`.
- [x] targeted regressions pin both successful and partial capability-catalog
      paths.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
- Manual checks:
  - none
- Screenshots/logs:
  - none
- High-risk checks:
  - keep release-smoke capability validation bounded to the approved catalog
    surface rather than inventing new owner logic

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - n/a
- Follow-up architecture doc updates:
  - docs/testing/runbook sync deferred to `PRJ-611`

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Capability-catalog proof is intentionally release-smoke and bundle based,
without pretending the catalog is part of `incident_evidence.policy_posture`.
