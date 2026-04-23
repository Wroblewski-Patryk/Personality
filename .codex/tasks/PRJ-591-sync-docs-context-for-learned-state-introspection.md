# Task

## Header
- ID: PRJ-591
- Title: Sync docs/context for learned-state introspection
- Status: DONE
- Owner: Product Docs
- Depends on: PRJ-590
- Priority: P2

## Context
`PRJ-589..PRJ-590` widened the backend-owned learned-state surfaces and made
release smoke plus incident-evidence validation pin the richer bounded
contract. Canonical docs and planning truth must now describe that live
baseline instead of the older owner/path-only posture.

## Goal
Synchronize canonical docs, runtime reality, testing guidance, ops notes, and
planning/context truth around the richer learned-state and personality-growth
inspection baseline.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] canonical docs describe the richer learned-state section and summary contract
- [x] runtime reality, testing guidance, and ops notes describe the same backend-owned growth surfaces
- [x] planning/context truth records `PRJ-591` closure and moves the queue to `PRJ-592`

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py` -> `126 passed`
- Manual checks:
  - cross-review of `docs/architecture/16_agent_contracts.md`,
    `docs/implementation/runtime-reality.md`,
    `docs/engineering/testing.md`, and
    `docs/operations/runtime-ops-runbook.md`
- Screenshots/logs:
- High-risk checks:
  - docs must stay aligned with the bounded learned-state contract and must not imply self-modifying executable skill learning

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/17_logging_and_debugging.md`
  - `docs/architecture/29_runtime_behavior_testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - none

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
This slice remains bounded to backend-owned summaries. It documents richer
inspection surfaces for future UI or admin consumers without turning learned
state into a second execution system.
