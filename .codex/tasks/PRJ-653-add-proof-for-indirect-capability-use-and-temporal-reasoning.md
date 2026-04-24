# Task

## Header
- ID: PRJ-653
- Title: Add proof for indirect capability use and temporal reasoning
- Status: BACKLOG
- Owner: QA/Test
- Depends on: PRJ-652
- Priority: P0

## Context
Current tests already prove keyword-triggered web search, page reading, and
planned-work flows. The remaining risk is that the runtime still underuses
those capabilities on indirect turns because awareness stays implicit.

## Goal
Add regression and behavior proof that the personality can use bounded
time/tool awareness on indirect, non-keyword-triggered turns without breaking
existing planning and action boundaries.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Regression tests cover indirect temporal reasoning beyond explicit `today|tomorrow` trigger phrases.
- [ ] Regression or behavior scenarios cover indirect bounded-tool use beyond explicit `search the web|read page` trigger phrasing.
- [ ] Proof fails when awareness surfaces drift back to hidden-only heuristics or prompt fiction.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted pytest plus behavior scenarios
- Manual checks: compare indirect-turn behavior before versus after awareness surfacing
- Screenshots/logs:
- High-risk checks: avoid tests that only recheck serialization or explicit keyword paths

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/29_runtime_behavior_testing.md`, `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: testing guidance and behavior evidence notes

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
This slice should prove operational awareness, not just that existing explicit
commands still work.
