# Task

## Header
- ID: PRJ-602
- Title: Add release and incident evidence for organizer-tool activation posture
- Status: DONE
- Owner: QA/Test
- Depends on: PRJ-601
- Priority: P1

## Context
The organizer-tool stack now exposes an actionable activation snapshot through
`/health`, but release smoke and incident evidence still treat organizer
readiness at a coarser level.

## Goal
Make organizer-tool activation posture part of release and incident evidence.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] release smoke validates the organizer activation snapshot
- [x] incident evidence and bundle checks validate the same activation snapshot
- [x] regression coverage pins the activation evidence contract

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_api_routes.py` -> `111 passed`
- Manual checks:
- Screenshots/logs:
- High-risk checks:

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/16_agent_contracts.md`, `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

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
This slice should extend the existing organizer-tool smoke and incident
evidence path rather than introducing a separate activation validator.
