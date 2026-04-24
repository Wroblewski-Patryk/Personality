# Task

## Header
- ID: PRJ-652
- Title: Implement explicit foreground awareness for time and approved tools
- Status: BACKLOG
- Owner: Backend Builder
- Depends on: PRJ-651
- Priority: P0

## Context
The runtime already carries `event.timestamp`, planned-work state, tool
readiness, and bounded web capability truth, but the active turn and reply
prompt still do not consistently receive an explicit awareness summary for
those capabilities.

## Goal
Implement one bounded foreground-awareness path that makes current time,
approved tool posture, and active planned-work posture explicitly visible to
the turn without widening side-effect authority.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Runtime state and/or context surfaces expose bounded current-time and planned-work awareness to the active turn.
- [ ] Reply-prompt or equivalent foreground prompt surfaces expose approved bounded-tool posture without claiming extra execution authority.
- [ ] Existing planning and action boundaries remain unchanged, and capability awareness reuses current runtime truth rather than duplicating it.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted runtime, planning, prompt-path, and regression coverage
- Manual checks: inspect context/debug/prompt inputs on turns that mention time or imply external lookup without explicit trigger phrases
- Screenshots/logs:
- High-risk checks: avoid a second capability registry or prompt-only fiction that disagrees with runtime source surfaces

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: runtime reality and testing guidance

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
The point is not to make the model autonomous. The point is to make existing
bounded capabilities explicit and reliable in normal foreground reasoning.
