# Task

## Header
- ID: PRJ-745
- Title: Freeze transcript truth and communication governance contract
- Task Type: fix
- Current Stage: verification
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-744
- Priority: P0

## Context
Production evidence showed scheduler-owned proactive ticks surfacing in the
shared transcript as if they were user-authored turns. The repo also needed a
clear contract for when user-originated turns must receive a reply and when
internal wakeups may stay silent.

## Goal
Freeze one explicit architecture contract for transcript truth and the
user-vs-scheduler communication boundary.

## Deliverable For This Stage
Verified architecture docs that define transcript visibility and conscious
outbound governance for user turns versus scheduler wakeups.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] shared transcript contract forbids scheduler wakeups from projecting as `role=user`
- [x] communication governance defines silent internal wakeups versus conscious outbound delivery
- [x] architecture docs match the implemented runtime boundary

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
  - architecture/runtime/code cross-review
- Manual checks:
  - reviewed `docs/architecture/16_agent_contracts.md`
  - reviewed `docs/architecture/23_proactive_system.md`
- Screenshots/logs:
  - n/a
- High-risk checks:
  - transcript truth remains backed by the shared episodic memory store

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/23_proactive_system.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: no
- Approval reference if architecture changed:
  - user-approved repair lane from `PRJ-744`
- Follow-up architecture doc updates:
  - completed in the files above

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - not required for this docs-only slice
- Rollback note:
  - revert contract docs if implementation is reverted

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
Cross-channel escalation remains intentionally open and was not implemented in
this slice.
