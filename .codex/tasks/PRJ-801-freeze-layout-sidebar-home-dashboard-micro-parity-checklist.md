# Task

## Header
- ID: PRJ-801
- Title: Freeze the micro parity checklist for layout, sidebar, home, and dashboard
- Task Type: research
- Current Stage: planning
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-800
- Priority: P1

## Context
`PRJ-800` created the master parity ledger for `layout + sidebar + home +
dashboard`, but the user explicitly asked whether every element had really been
analyzed. The master ledger is structural and execution-oriented; this follow-up
task exists to enumerate the remaining visible sub-elements so future passes do
not skip small but high-impact differences.

## Goal
Create one micro-level parity checklist that enumerates the visible sub-elements
still requiring review or implementation for the current canonical web lane.

## Deliverable For This Stage
Planning-only output:

- one checklist that marks sub-elements as `MATCHED`, `DRIFT`, or `BLOCKED`
- a supplement to the master parity ledger, not a replacement

## Scope
- `docs/planning/layout-sidebar-home-dashboard-micro-parity-checklist.md`
- `.codex/tasks/PRJ-801-freeze-layout-sidebar-home-dashboard-micro-parity-checklist.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Review the master ledger and canonical screenshots already frozen in repo.
2. Expand each audited surface into visible sub-elements.
3. Mark each sub-element by current audit status.
4. Sync the checklist into the project context so later tasks can move items
   from `DRIFT` to `MATCHED`.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- checklist covers parent layout, sidebar, public home, and dashboard
- checklist is more detailed than the structural master ledger
- blocking items are called out explicitly
- source-of-truth context is updated

## Definition of Done
- [x] A micro parity checklist exists for the current canonical web lane.
- [x] The checklist distinguishes `MATCHED`, `DRIFT`, and `BLOCKED`.
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
  - document and code-structure review only
- Manual checks:
  - compared current implementation layers and canonical surface expectations
- Screenshots/logs:
  - canonical asset set reused as the visual baseline
- High-risk checks:
  - route-contract limitation for full sidebar inventory remains explicitly flagged

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
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - canonical raster assets remain the authority for atmosphere and embodiment
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
  - checklist intentionally records remaining drift; it does not implement fixes
- State checks: not applicable
- Responsive checks: desktop | tablet | mobile planning requirement recorded
- Input-mode checks: pointer | keyboard planning requirement recorded
- Accessibility checks:
  - later implementation must preserve clarity while tightening composition
- Parity evidence:
  - this checklist supplements the master ledger and should guide future screenshot-proof passes

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
- This checklist is intentionally strict; many entries remain `DRIFT` until a
  real deploy screenshot loop confirms closure.

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
  - not applicable in this planning-only slice

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
  - added a micro-level parity checklist for every major visible element in the
    current `layout + sidebar + home + dashboard` lane
- Files changed:
  - `docs/planning/layout-sidebar-home-dashboard-micro-parity-checklist.md`
  - `.codex/tasks/PRJ-801-freeze-layout-sidebar-home-dashboard-micro-parity-checklist.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - audited current code structure and existing canonical planning artifacts
- What is incomplete:
  - the implementation passes themselves
- Next steps:
  - use the checklist as acceptance gates for the next execution slices
- Decisions made:
  - future parity work should now explicitly move checklist items from `DRIFT`
    to `MATCHED`
