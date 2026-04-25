# Task

## Header
- ID: PRJ-701
- Title: Canonical Docs And Testing Guidance Sync
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-700
- Priority: P2

## Context
The lane changes user-facing runtime behavior and foreground contracts, so
canonical architecture and testing guidance must describe the same repaired
truth as the implementation.

## Goal
Sync architecture and engineering-testing guidance with the new
foreground-awareness, truthful-capability, and bounded external-read behavior.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] canonical architecture docs describe the foreground-awareness contract
- [x] behavior-testing docs include the repaired scenario family
- [x] engineering testing guidance lists the focused validation command for this lane

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - doc-and-context sync supported by the same focused green pytest suite for the lane
- Manual checks:
  - cross-review of architecture, testing guidance, and context truth
- Screenshots/logs:
  - none
- High-risk checks:
  - docs remain architecture-owned and avoid describing the implementation as a second subsystem

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/29_runtime_behavior_testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - none
- Follow-up architecture doc updates:
  - completed in this task

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
Docs updated:
- `docs/architecture/15_runtime_flow.md`
- `docs/architecture/16_agent_contracts.md`
- `docs/architecture/29_runtime_behavior_testing.md`
- `docs/engineering/testing.md`
