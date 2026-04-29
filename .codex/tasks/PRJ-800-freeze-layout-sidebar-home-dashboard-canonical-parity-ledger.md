# Task

## Header
- ID: PRJ-800
- Title: Freeze the canonical parity ledger for layout, sidebar, home, and dashboard
- Task Type: research
- Current Stage: planning
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-795, PRJ-796
- Priority: P1

## Context
The current web shell is directionally close to the approved flagship look,
but convergence work has been happening in many small slices. The user asked
for one proper, detail-oriented analysis of the remaining differences between
the running implementation and the canonical targets for:

- parent layout
- authenticated sidebar
- public home
- dashboard

The purpose of this task is to stop ad-hoc polishing and create one execution-
ready ledger of what still differs and in which order it should be fixed.

## Goal
Produce one detailed canonical parity ledger that converts the remaining visual
drift in `layout + sidebar + home + dashboard` into a disciplined execution
queue.

## Deliverable For This Stage
Planning-only output:

- one master audit document with detailed current-vs-target differences
- a recommended implementation order
- explicit blocking issues for true screenshot parity

## Scope
- `docs/planning/layout-sidebar-home-dashboard-canonical-parity-master-ledger.md`
- `.codex/tasks/PRJ-800-freeze-layout-sidebar-home-dashboard-canonical-parity-ledger.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Review the current canonical screen set and supporting UX source-of-truth.
2. Review the current shell and route implementation in `web/src/App.tsx` and
   `web/src/index.css`.
3. Group remaining drift by surface and by reusable layer rather than by
   isolated CSS selectors.
4. Convert the audit into one execution queue that starts with structure before
   continuing into polish.
5. Sync the result into project context.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- the audit covers `layout`, `sidebar`, `home`, and `dashboard`
- the audit clearly distinguishes structural drift from cosmetic drift
- the next execution order is explicit
- source-of-truth context is updated

## Definition of Done
- [x] Remaining visual differences are documented in one master ledger.
- [x] The next implementation order is explicit and actionable.
- [x] Relevant source-of-truth files are synchronized.

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
  - document and context review only
- Manual checks:
  - compared current code structure against the frozen canonical web screen set
- Screenshots/logs:
  - existing canonical assets and prior parity notes were used as the visual baseline
- High-risk checks:
  - route-contract mismatch for the full sidebar inventory was called out explicitly

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/27_codex_instructions.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - not applicable

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/canonical-web-screen-reference-set.md`
- Canonical visual target:
  - parent layout
  - authenticated sidebar
  - public home
  - dashboard
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - canonical authenticated sidebar spine
  - landing-first public entry
  - flagship overview stage
- New shared pattern introduced: no
- Design-memory entry reused:
  - frame-first flagship shell
  - canonical authenticated sidebar spine
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - existing canonical raster assets remain the authority where illustration matters
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
  - fresh deploy screenshots are still required before final sign-off
- State checks: not applicable
- Responsive checks: desktop | tablet | mobile planning requirement recorded
- Input-mode checks: pointer | keyboard planning requirement recorded
- Accessibility checks:
  - future execution tasks must preserve route clarity while reducing shell chrome
- Parity evidence:
  - this task produces the ledger that future parity passes must execute against

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: none
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - not applicable

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
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
- This planning slice intentionally does not implement new UI changes.

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

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: yes
- Endpoint and client contract match: yes
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: not applicable
- Regression check performed:
  - not applicable in this planning-only task

## AI Testing Evidence (required for AI features)

- `AI_TESTING_PROTOCOL.md` reviewed: not applicable
- Memory consistency scenarios:
- Multi-step context scenarios:
- Adversarial or role-break scenarios:
- Prompt injection checks:
- Data leakage and unauthorized access checks:
- Result:

## Result Report

- Task summary:
  - created one master parity ledger for the remaining structural and visual
    drift in `layout + sidebar + home + dashboard`
- Files changed:
  - `docs/planning/layout-sidebar-home-dashboard-canonical-parity-master-ledger.md`
  - `.codex/tasks/PRJ-800-freeze-layout-sidebar-home-dashboard-canonical-parity-ledger.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - reviewed current implementation structure and canonical references
- What is incomplete:
  - the execution slices themselves
  - fresh screenshot-parity captures after the next deploy loop
- Next steps:
  - execute the queue from shell/frame exactness through dashboard parity
- Decisions made:
  - future convergence for this lane should now favor larger structural passes
    over isolated micro-polish
