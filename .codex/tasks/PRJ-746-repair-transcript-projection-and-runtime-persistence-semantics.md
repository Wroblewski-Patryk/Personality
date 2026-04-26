# Task

## Header
- ID: PRJ-746
- Title: Repair transcript projection and runtime persistence semantics
- Task Type: fix
- Current Stage: verification
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-745
- Priority: P0

## Context
The shared transcript was projecting scheduler-owned synthetic event text as
user-authored messages. Episodic persistence needed a machine-distinguishable
visibility contract so internal wakeups could remain durable without leaking
into product-facing chat history.

## Goal
Make runtime persistence and `/app/chat/history` truthful without creating a
second chat store.

## Deliverable For This Stage
Verified backend changes that mark transcript visibility in persisted payloads
and project only user-visible turns into app history.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] persisted episodes include bounded transcript-visibility metadata
- [x] scheduler prompts no longer appear as user-authored transcript turns
- [x] delivered scheduler outreach can still appear as assistant-visible transcript output

## Stage Exit Criteria
- [x] The output matches the declared `Current Stage`.
- [x] Work from later stages was not mixed in without explicit approval.
- [x] Risks and assumptions for this stage are stated clearly.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval
- implicit stage skipping

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py; Pop-Location`
- Manual checks:
  - reviewed transcript projection in `backend/app/memory/repository.py`
  - reviewed episodic persistence in `backend/app/core/action.py`
- Screenshots/logs:
  - n/a
- High-risk checks:
  - shared app transcript still merges app and Telegram turns under one user continuity owner

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: no
- Approval reference if architecture changed:
  - `PRJ-745`
- Follow-up architecture doc updates:
  - completed before implementation

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: medium
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - not required
- Rollback note:
  - revert `backend/app/core/action.py` and `backend/app/memory/repository.py`

## Review Checklist (mandatory)
- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Backward-compat fallback still keeps old scheduler deliveries visible when the
stored row proves successful outbound delivery.
