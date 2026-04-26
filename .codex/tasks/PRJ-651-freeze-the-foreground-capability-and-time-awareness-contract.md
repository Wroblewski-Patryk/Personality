# Task

## Header
- ID: PRJ-651
- Title: Freeze the foreground capability-and-time awareness contract
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-650
- Priority: P0

## Context
Core no-UI `v1` capabilities are now implemented and `v1_readiness` is more
truthful, but the active foreground turn still lacks one explicit contract for
how current time, active planned-work posture, and approved bounded tool
families become visible without widening execution authority.

## Goal
Freeze one explicit foreground-awareness contract for time and approved tool
posture before implementation changes in `PRJ-652`.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Canonical architecture defines what foreground time/capability awareness may expose to the active turn.
- [x] The contract keeps execution authority unchanged and below the planning/expression/action boundary.
- [x] Planning and context truth point cleanly to `PRJ-652` as implementation of that frozen contract.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: architecture and runtime-contract cross-review
- Manual checks: reviewed `docs/architecture/16_agent_contracts.md`, `docs/planning/next-iteration-plan.md`, `docs/planning/open-decisions.md`, `.codex/context/TASK_BOARD.md`, and `.codex/context/PROJECT_STATE.md`
- Screenshots/logs:
- High-risk checks: do not turn foreground awareness into a second execution or authorization engine

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/16_agent_contracts.md`, `docs/architecture/10_future_vision.md`, `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: planning/context sync completed in this slice

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
This slice freezes visibility and ownership only. It does not yet implement the
foreground-awareness payload path.
