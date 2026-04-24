# Task

## Header
- ID: PRJ-635
- Title: Freeze the time-aware planned-work baseline for core no-UI V1
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-631
- Priority: P0

## Context
The approved architecture change replaces a standalone reminder mindset with one
shared future-work model driven by planning, scheduler reevaluation, and the
existing action boundary.

## Goal
Freeze one canonical architecture baseline where planned future work is part of
core no-UI `v1`, while organizer-tool activation remains a later extension.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Canonical architecture docs define planned future work as an extension of internal planning state.
- [x] Core no-UI `v1` closure no longer depends on organizer-tool credentials.
- [x] Planning/context truth seeds the next implementation queue from this revised baseline.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: not run; doc-only architecture slice
- Manual checks:
  - compared the revised core-`v1` boundary across `docs/architecture/10_future_vision.md`,
    `docs/architecture/12_data_model.md`, `docs/architecture/16_agent_contracts.md`,
    `docs/planning/next-iteration-plan.md`, and `docs/planning/open-decisions.md`
  - verified that organizer-tool activation is no longer described as a core
    `v1` prerequisite and that due planned work still crosses the normal
    foreground path
- Screenshots/logs:
- High-risk checks: do not keep organizer tooling as a hidden blocker for core `v1` after this revision

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`, `docs/architecture/10_future_vision.md`, `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`, `docs/architecture/12_data_model.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: user-approved revision on 2026-04-24 for time-aware planned work as part of core `v1`
- Follow-up architecture doc updates: planning/context truth completed in this slice; later runtime/testing/ops docs remain for implementation slices

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
This slice is architectural and planning-first by design.
`PRJ-636` is now the next active follow-up.
