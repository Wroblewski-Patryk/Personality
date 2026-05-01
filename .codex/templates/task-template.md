# Task

## Header
- ID: PRJ-XXX
- Title:
- Task Type: fix | feature | refactor | design | research | release
- Current Stage: intake | analysis | planning | implementation | verification | release | post-release
- Status: BACKLOG | READY | IN_PROGRESS | BLOCKED | REVIEW | DONE
- Owner: Planning Agent | Product Docs Agent | Backend Builder | Frontend Builder | QA/Test | Security | DB/Migrations | Ops/Release | Review
- Depends on:
- Priority: P0 | P1 | P2
- Coverage Ledger Rows:
- Iteration:
- Operation Mode: BUILDER | ARCHITECT | TESTER

## Process Self-Audit
- [ ] All seven autonomous loop steps are planned.
- [ ] No loop step is being skipped.
- [ ] Exactly one priority task is selected.
- [ ] Operation mode matches the iteration number.
- [ ] The task is aligned with repository source-of-truth documents.
## Context
Where this work sits in the current project flow and architecture.

## Goal
What must be achieved by this task.

## Success Signal
- User or operator problem:
- Expected product or reliability outcome:
- How success will be observed:
- Post-launch learning needed: yes | no

## Deliverable For This Stage
Describe exactly what should be produced in the current stage only.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [ ] concrete completion condition 1
- [ ] concrete completion condition 2
- [ ] concrete completion condition 3

## Stage Exit Criteria
- [ ] The output matches the declared `Current Stage`.
- [ ] Work from later stages was not mixed in without explicit approval.
- [ ] Risks and assumptions for this stage are stated clearly.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval
- implicit stage skipping

## Validation Evidence
- Tests:
- Manual checks:
- Screenshots/logs:
- High-risk checks:
- Coverage ledger updated: yes | no | not applicable
- Coverage rows closed or changed:

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
- Fits approved architecture: yes | no
- Mismatch discovered: yes | no
- Decision required from user: yes | no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: figma | approved_snapshot | stitch_exception
- Design source reference:
- Canonical visual target:
- Fidelity target: pixel_close | structurally_faithful | style_inspired
- Stitch used: yes | no
- Experience-quality bar reviewed: yes | no
- Visual-direction brief reviewed: yes | no
- Existing shared pattern reused:
- New shared pattern introduced: yes | no
- Design-memory entry reused:
- Design-memory update required: yes | no
- Visual gap audit completed: yes | no
- Background or decorative asset strategy:
- Canonical asset extraction required: yes | no
- Screenshot comparison pass completed: yes | no
- Remaining mismatches:
- State checks: loading | empty | error | success
- Feedback locality checked: yes | no
- Raw technical errors hidden from end users: yes | no | not applicable
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: touch | pointer | keyboard
- Accessibility checks:
- Parity evidence:

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: none | low | medium | high
- Env or secret changes:
- Health-check impact:
- Smoke steps updated:
- Rollback note:
- Observability or alerting impact:
- Staged rollout or feature flag:

## Review Checklist (mandatory)
- [ ] Process self-audit completed before implementation.
- [ ] Autonomous loop evidence covers all seven steps.
- [ ] Exactly one priority task was completed in this iteration.
- [ ] Operation mode was selected according to iteration rotation.
- [ ] Current stage is declared and respected.
- [ ] Deliverable for the current stage is complete.
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Risks, assumptions, links.

## Production-Grade Required Contract

Every task must include these mandatory sections before it can move to `READY` or `IN_PROGRESS`:

- `Goal`
- `Scope` with exact files, modules, routes, APIs, schemas, docs, or runtime surfaces
- `Implementation Plan` with step-by-step execution and validation
- `Acceptance Criteria` with testable conditions
- `Definition of Done` using `DEFINITION_OF_DONE.md`
- `Result Report`

Runtime tasks must be delivered as a vertical slice: UI -> logic -> API -> DB -> validation -> error handling -> test. Partial implementations, mock-only paths, placeholders, fake data, and temporary fixes are forbidden.

## Integration Evidence

## Product / Discovery Evidence
- Problem validated: yes | no | not applicable
- User or operator affected:
- Existing workaround or pain:
- Smallest useful slice:
- Success metric or signal:
- Feature flag, staged rollout, or disable path: yes | no | not applicable
- Post-launch feedback or metric check:

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: yes | no | not applicable
- Critical user journey:
- SLI:
- SLO:
- Error budget posture: healthy | burning | exhausted | not applicable
- Health/readiness check:
- Logs, dashboard, or alert route:
- Smoke command or manual smoke:
- Rollback or disable path:

- `INTEGRATION_CHECKLIST.md` reviewed: yes | no | not applicable
- Real API/service path used: yes | no | not applicable
- Endpoint and client contract match: yes | no | not applicable
- DB schema and migrations verified: yes | no | not applicable
- Loading state verified: yes | no | not applicable
- Error state verified: yes | no | not applicable
- Refresh/restart behavior verified: yes | no | not applicable
- Regression check performed:

## AI Testing Evidence (required for AI features)

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: yes | no | not applicable
- Data classification:
- Trust boundaries:
- Permission or ownership checks:
- Abuse cases:
- Secret handling:
- Security tests or scans:
- Fail-closed behavior:
- Residual risk:

- `AI_TESTING_PROTOCOL.md` reviewed: yes | no | not applicable
- Memory consistency scenarios:
- Multi-step context scenarios:
- Adversarial or role-break scenarios:
- Prompt injection checks:
- Data leakage and unauthorized access checks:
- Result:

## Result Report

- Task summary:
- Files changed:
- How tested:
- What is incomplete:
- Next steps:
- Decisions made:

## Autonomous Loop Evidence

### 1. Analyze Current State
- Issues:
- Gaps:
- Inconsistencies:
- Architecture constraints:

### 2. Select One Priority Task
- Selected task:
- Priority rationale:
- Why other candidates were deferred:

### 3. Plan Implementation
- Files or surfaces to modify:
- Logic:
- Edge cases:

### 4. Execute Implementation
- Implementation notes:

### 5. Verify and Test
- Validation performed:
- Result:

### 6. Self-Review
- Simpler option considered:
- Technical debt introduced: yes | no
- Scalability assessment:
- Refinements made:

### 7. Update Documentation and Knowledge
- Docs updated:
- Context updated:
- Learning journal updated: yes | no | not applicable.