# Task

## Header
- ID: PRJ-638
- Title: Implement foreground delivery for due planned work
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-637
- Priority: P0

## Context
Once due work reaches attention, foreground runtime should treat it as a normal
planning and action problem instead of special-casing reminder delivery.

## Goal
Implement canonical foreground handling for due planned work through planning,
expression, and action.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Due planned work can result in a Telegram or API follow-up through the existing foreground path.
- [x] Completion, snooze, and cancellation semantics remain explicit state transitions.
- [x] No direct delivery path exists outside planning -> expression -> action.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted runtime pipeline and action coverage
- Manual checks: verify due work produces normal foreground turn artifacts
- Screenshots/logs:
- High-risk checks: do not let planned work bypass the action boundary

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`, `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: testing and ops notes

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
This is still internal-first planning state; organizer sync remains a later extension.

## Result

- due planned-work handoffs now re-enter the normal foreground runtime path
  and are delivered through the existing `planning -> expression -> action`
  boundary instead of a scheduler-owned direct-send shortcut
- scheduler maintenance now emits one foreground runtime event per newly-due
  work item and the due-query baseline avoids repeated redispatch of already
  `due` rows
- proposal handoff resolution remains explicit, so scheduled due delivery still
  leaves normal conscious-turn artifacts and proposal lifecycle evidence

## Validation Evidence

- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_scheduler_worker.py tests/test_runtime_pipeline.py`
- Manual checks:
  - reviewed the foreground path to confirm due planned work only reaches
    Telegram via the existing runtime action boundary
- High-risk checks:
  - due items no longer re-enter cadence selection after they are marked `due`
    during scheduler reevaluation
