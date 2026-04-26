# Task

## Header
- ID: PRJ-747
- Title: Tighten proactive wakeup execution and anti-spam behavior
- Task Type: fix
- Current Stage: verification
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-746
- Priority: P0

## Context
Even after transcript truth was clarified, proactive cadence still needed to
avoid speaking on every plain time check-in and needed a sturdier unanswered
counter that ignored unrelated internal rows.

## Goal
Keep scheduler wakeups available for conscious analysis while making low-value
time check-ins silent and preventing repeat outreach without a reply.

## Deliverable For This Stage
Verified runtime behavior changes that reduce plain `time_checkin` eagerness
and make unanswered-proactive counting robust against internal/system rows.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] plain `time_checkin` no longer interrupts by default without active work or strong relation signal
- [x] unanswered proactive counting ignores internal/system rows instead of resetting prematurely
- [x] consciously justified proactive delivery still remains possible

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
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_memory_repository.py tests/test_action_executor.py tests/test_runtime_pipeline.py; Pop-Location`
- Manual checks:
  - reviewed `backend/app/proactive/engine.py`
  - reviewed proactive counters in `backend/app/memory/repository.py`
- Screenshots/logs:
  - n/a
- High-risk checks:
  - blocked-task proactive warnings still stay deliverable when opt-in and delivery target are present

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/23_proactive_system.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - `PRJ-745`
- Follow-up architecture doc updates:
  - already synchronized

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: medium
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - not required
- Rollback note:
  - revert proactive threshold changes and candidate-state helpers

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
This slice intentionally does not implement cross-channel escalation after
silence.
