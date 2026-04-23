# Task

## Header
- ID: PRJ-590
- Title: Add regression and release evidence for learned-state introspection
- Status: DONE
- Owner: QA/Test
- Depends on: PRJ-589
- Priority: P2

## Context
`PRJ-589` widened learned-state inspection surfaces with richer bounded growth,
role/skill, and planning continuity summaries. Release and incident-evidence
flows must now pin that richer contract instead of only checking owner/path
posture.

## Goal
Make learned-state introspection regressions and smoke/evidence checks prove the
richer backend-owned inspection contract.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] smoke checks validate the richer learned-state contract from `/health` and incident evidence
- [x] targeted regressions pin the richer learned-state posture in smoke fixtures
- [x] evidence remains bounded to backend-owned learned-state contract fields

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py` -> `126 passed`
- Manual checks:
- Screenshots/logs:
- High-risk checks:

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/17_logging_and_debugging.md`
  - `docs/architecture/29_runtime_behavior_testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - `PRJ-591`

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
The release/evidence lane should stay on section contracts and bounded summary
metadata, not full user-specific learned-state payloads.
