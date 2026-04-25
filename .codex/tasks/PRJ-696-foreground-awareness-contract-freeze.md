# Task

## Header
- ID: PRJ-696
- Title: Foreground Awareness Contract Freeze
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-695
- Priority: P1

## Context
The repo already had linked identity continuity, event timestamps, bounded web
search, and bounded page-read execution, but the active answer path still did
not receive one explicit foreground contract for those facts.

## Goal
Freeze one explicit foreground-awareness contract that reuses the current
runtime, identity, and bounded-tool systems without widening authority.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] context and identity contracts expose bounded foreground-awareness fields
- [x] canonical architecture docs describe the same contract
- [x] no second memory, identity, or tooling subsystem was introduced

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_identity_service.py tests/test_expression_agent.py; Pop-Location`
- Manual checks:
  - cross-review of runtime contracts, context output, identity output, and
    architecture docs
- Screenshots/logs:
  - none
- High-risk checks:
  - foreground-awareness data remains descriptive only and does not bypass the
    planning -> expression -> action boundary

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - none
- Follow-up architecture doc updates:
  - completed in this lane

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Implemented through existing runtime/context/identity contracts in
`backend/app/core/contracts.py`, `backend/app/agents/context.py`, and
`backend/app/identity/service.py`.
