# Task

## Header
- ID: PRJ-648
- Title: Implement truthful v1-readiness gate evaluation
- Status: BACKLOG
- Owner: Backend Builder
- Depends on: PRJ-647
- Priority: P0

## Context
Current `/health.v1_readiness` mixes core and extension posture and some gate
fields are still static or surface-validity-oriented instead of reflecting
live runtime truth.

## Goal
Make `v1_readiness` a truthful runtime summary derived from the approved core
`v1` acceptance boundary and live owner surfaces.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Core no-UI `v1` gate fields are derived from live source surfaces instead of hardcoded ready states.
- [ ] Extension posture such as organizer daily use is either separated from core gates or explicitly marked as non-blocking extension readiness.
- [ ] Conversation and deploy-parity semantics no longer overstate readiness when only a weaker posture is present.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted `/health` and runtime-policy coverage
- Manual checks: inspect `/health.v1_readiness` against underlying `/health.*` source sections
- Screenshots/logs:
- High-risk checks: avoid creating a second acceptance engine outside existing health and policy owners

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/10_future_vision.md`, `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: runtime reality, testing, ops guidance

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
The intent is to tighten truthfulness, not to widen the product scope.
