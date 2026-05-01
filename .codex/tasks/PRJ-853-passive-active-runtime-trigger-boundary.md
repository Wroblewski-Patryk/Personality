# Task

## Header
- ID: PRJ-853
- Title: Freeze Passive/Active Runtime Trigger Boundary And Planned-Action Observer
- Task Type: design
- Current Stage: verification
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-841
- Priority: P0
- Coverage Ledger Rows: not applicable
- Iteration: 853
- Operation Mode: BUILDER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
The repository already has a conscious/subconscious split, planned work, proposal handoff, and proactive guardrails. Fresh user direction clarifies that the next architecture layer should distinguish external future-facing planning from the internal execution loop of an admitted foreground turn.

Current proactive cadence can still behave too much like generic autonomous outreach because a scheduler tick can select candidates and start the full conscious runtime. The target architecture should instead use passive background cognition to create or update planned work/proposals, then use a cheap planned-action observer to wake consciousness only when something is actually due or actionable.

## Goal
Freeze one architecture contract for passive versus active runtime triggers so subconscious/background cadence cannot directly stimulate conscious outreach without due planned work, actionable proposal state, or a real foreground event.

## Success Signal
- User or operator problem: AION should stop treating time-passing cadence as a reason to message the user.
- Expected product or reliability outcome: inferred care/check-ins remain possible, but only as learned planned work or proposals that later cross attention/conscious gates.
- How success will be observed: architecture and planning truth describe planned-action observer posture and separate it from the internal execution path of an admitted turn.
- Post-launch learning needed: yes

## Deliverable For This Stage
Architecture/planning source-of-truth updates only. Runtime code changes are intentionally deferred.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it
- keep external future-facing planning separate from the internal foreground execution loop

## Scope
- `docs/architecture/02_architecture.md`
- `docs/architecture/15_runtime_flow.md`
- `docs/architecture/16_agent_contracts.md`
- `docs/architecture/23_proactive_system.md`
- `docs/implementation/runtime-reality.md`
- `docs/planning/next-iteration-plan.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/context/LEARNING_JOURNAL.md`
- `.codex/tasks/PRJ-853-passive-active-runtime-trigger-boundary.md`

## Implementation Plan
1. Update canonical architecture to state that external contact/care/outreach planning becomes planned work or proposals, not a scheduler-coded obligation.
2. Add planned-action observer semantics before full foreground execution.
3. Clarify that this boundary does not alter the internal execution loop after a foreground stimulus is admitted.
4. Record current runtime drift and next implementation queue.
5. Sync task board and project state.
6. Run text/diff validation.

## Acceptance Criteria
- [x] Architecture explicitly forbids generic subconscious/scheduler cadence from waking consciousness merely because time passed.
- [x] Planned-action observer is recorded as the target bridge from passive planning to active execution.
- [x] Relationship care/check-ins may still be inferred, but only into planned work or proposals.
- [x] Internal foreground execution remains unchanged after a stimulus is admitted.
- [x] Follow-up implementation queue is seeded without changing runtime behavior.

## Definition of Done
- [x] DEFINITION_OF_DONE.md posture is satisfied for a docs-only architecture task.
- [x] Canonical docs and runtime reality are aligned.
- [x] Task board and project state are updated.
- [x] Validation evidence is attached.

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
- runtime code changes in this planning/architecture slice

## Validation Evidence
- Tests: not applicable; docs-only architecture contract.
- Manual checks: canonical architecture, runtime reality, planning, task, and context cross-review.
- Screenshots/logs: not applicable.
- High-risk checks: confirmed the change targets external future-facing planning only and does not alter the internal execution loop.
- Coverage ledger updated: not applicable
- Coverage rows closed or changed: none

## Architecture Evidence
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/05_conscious_subconscious.md`
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/23_proactive_system.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: no
- Approval reference if architecture changed: user approved "warstwa 2" passive/active direction in chat.
- Follow-up architecture doc updates: implementation follow-ups seeded as `PRJ-854..PRJ-858`.

## UX/UI Evidence
- Design source type: not applicable
- Design source reference: not applicable
- Canonical visual target: not applicable
- Fidelity target: not applicable
- Stitch used: no
- Experience-quality bar reviewed: not applicable
- Visual-direction brief reviewed: not applicable
- Existing shared pattern reused: not applicable
- New shared pattern introduced: no
- Design-memory entry reused: not applicable
- Design-memory update required: no
- Visual gap audit completed: not applicable
- Background or decorative asset strategy: not applicable
- Canonical asset extraction required: no
- Screenshot comparison pass completed: not applicable
- Remaining mismatches: none
- State checks: not applicable
- Feedback locality checked: not applicable
- Raw technical errors hidden from end users: not applicable
- Responsive checks: not applicable
- Input-mode checks: not applicable
- Accessibility checks: not applicable
- Parity evidence: not applicable

## Deployment / Ops Evidence
- Deploy impact: none
- Env or secret changes: none
- Health-check impact: future follow-up should expose observer posture
- Smoke steps updated: no runtime smoke change in this task
- Rollback note: revert docs/context updates; runtime unchanged
- Observability or alerting impact: future follow-up should add observer health/debug posture
- Staged rollout or feature flag: future implementation should keep proactive rollback via `PROACTIVE_ENABLED=false`

## Review Checklist
- [x] Process self-audit completed before implementation.
- [x] Autonomous loop evidence covers all seven steps.
- [x] Exactly one priority task was completed in this iteration.
- [x] Operation mode was selected according to iteration rotation.
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
This task intentionally avoids runtime behavior changes. The next narrow implementation should introduce observer policy/visibility before rerouting proactive cadence.

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
- Problem validated: yes
- User or operator affected: user receiving unwanted repeated outreach
- Existing workaround or pain: asking the personality not to message repeatedly did not fully stop proactive cadence symptoms
- Smallest useful slice: architecture contract only
- Success metric or signal: future proactive cadence emits no foreground event when observer finds no due/actionable item
- Feature flag, staged rollout, or disable path: yes, existing proactive disable posture remains rollback
- Post-launch feedback or metric check: inspect proactive delivery counts and silent no-op evidence after implementation

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: not applicable
- Critical user journey: proactive outreach and planned-work follow-up
- SLI: future follow-up should measure observer no-op versus due handoff counts
- SLO: not defined in this docs-only slice
- Error budget posture: not applicable
- Health/readiness check: future follow-up should add observer posture
- Logs, dashboard, or alert route: future follow-up
- Smoke command or manual smoke: docs diff validation
- Rollback or disable path: revert docs; runtime unchanged

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: not applicable
- Endpoint and client contract match: not applicable
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: not applicable
- Regression check performed: docs cross-review

## AI Testing Evidence

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: not applicable
- Data classification: architecture docs only
- Trust boundaries: conscious runtime remains side-effect owner
- Permission or ownership checks: background loops remain passive
- Abuse cases: unwanted repeated outreach from time-passing cadence
- Secret handling: no secrets touched
- Security tests or scans: not applicable
- Fail-closed behavior: future implementation should no-op when no due/actionable item exists
- Residual risk: runtime still needs implementation follow-up

- `AI_TESTING_PROTOCOL.md` reviewed: not applicable for docs-only slice
- Memory consistency scenarios: future `PRJ-857`
- Multi-step context scenarios: future `PRJ-857`
- Adversarial or role-break scenarios: future implementation follow-up
- Prompt injection checks: not applicable
- Data leakage and unauthorized access checks: not applicable
- Result: planning-only

## Result Report

- Task summary: froze passive/active trigger boundary and planned-action observer target.
- Files changed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/23_proactive_system.md`
  - `docs/implementation/runtime-reality.md`
  - `docs/planning/next-iteration-plan.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/LEARNING_JOURNAL.md`
  - `.codex/tasks/PRJ-853-passive-active-runtime-trigger-boundary.md`
- How tested: `git diff --check`
- What is incomplete: runtime implementation still uses current proactive cadence path.
- Next steps: `PRJ-854` planned-action observer policy and health/debug posture.
- Decisions made: external future-facing planning is passive until a due/actionable item crosses attention.

## Autonomous Loop Evidence

### 1. Analyze Current State
- Issues: proactive cadence can still be interpreted as generic active outreach.
- Gaps: no explicit planned-action observer contract.
- Inconsistencies: architecture intent allows silent background work, while implementation still has a fuller proactive tick path.
- Architecture constraints: background may propose but not execute; action owns side effects.

### 2. Select One Priority Task
- Selected task: `PRJ-853`
- Priority rationale: unwanted proactive messages are user-visible trust damage.
- Why other candidates were deferred: runtime changes need the trigger contract first.

### 3. Plan Implementation
- Files or surfaces to modify: canonical architecture, runtime reality, planning, task/context truth.
- Logic: passive triggers write state; active triggers execute only after attention admission.
- Edge cases: relationship care remains possible without hard-coding contact cadence.

### 4. Execute Implementation
- Implementation notes: docs-only architecture sync; no runtime code changed.

### 5. Verify and Test
- Validation performed: `git diff --check`
- Result: pass

### 6. Self-Review
- Simpler option considered: disabling proactive entirely.
- Technical debt introduced: no
- Scalability assessment: observer model reduces unnecessary foreground runs.
- Refinements made: explicitly separated external planning from internal turn execution.

### 7. Update Documentation and Knowledge
- Docs updated: yes
- Context updated: yes
- Learning journal updated: yes
