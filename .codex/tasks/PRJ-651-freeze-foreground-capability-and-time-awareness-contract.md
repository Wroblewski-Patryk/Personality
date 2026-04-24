# Task

## Header
- ID: PRJ-651
- Title: Freeze the foreground capability-and-time awareness contract
- Status: BACKLOG
- Owner: Planning Agent
- Depends on: PRJ-650
- Priority: P0

## Context
Fresh code-level analysis shows that core no-UI `v1` already implements
planning, time-aware planned work, bounded web search, page reading, and
tool-grounded learning. But the active foreground turn still learns about
these capabilities only indirectly in several places, which makes the product
feel less aware than the runtime really is.

## Goal
Freeze one explicit contract for how current time, active planned-work
posture, and approved bounded tool families become visible to the active turn
without widening execution authority beyond the existing planning and action
boundary.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Canonical docs define a bounded foreground-awareness contract for time, active planned work, and approved tool posture.
- [ ] The contract explicitly separates awareness from execution authority, keeping planning and action as the only execution owners.
- [ ] The next implementation slice has one clear target for runtime/context/prompt changes.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: architecture and runtime-contract cross-review
- Manual checks: compare `15_runtime_flow.md`, `16_agent_contracts.md`, `runtime.py`, `planning.py`, and OpenAI prompt surfaces
- Screenshots/logs:
- High-risk checks: avoid turning capability awareness into a second authorization or execution engine

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`, `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: runtime reality, testing guidance, planning truth, and context

## Review Checklist (mandatory)
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice is about bounded self-knowledge of existing capability, not about
adding new tools or changing execution authority.
