# Task

## Header
- ID: PRJ-779
- Title: Dashboard structural canonical convergence pass
- Task Type: design
- Current Stage: implementation
- Status: IN_PROGRESS
- Owner: Frontend Builder
- Depends on: PRJ-776
- Priority: P1

## Context
After `PRJ-776`, the parent shell and public home moved much closer to the
canonical structure. The next highest-value gap is the authenticated
`dashboard`, which still needs stronger hero authority, calmer editorial
sidebar pacing, a less widget-like flow bridge, and a more differentiated
lower closure.

## Goal
Reshape the dashboard so it reads more like one canonical flagship tableau and
less like stacked dashboard modules.

## Deliverable For This Stage
One frontend slice in `web/src/App.tsx` and `web/src/index.css` that:
- strengthens the dashboard hero as one cognition scene
- editorializes the right column
- simplifies the flow bridge
- differentiates lower information roles
- reduces late-route stat density in favor of scenic closure

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-779-dashboard-structural-canonical-convergence-pass.md`

## Implementation Plan
1. Add a hero-note bridge so the central dashboard stage reads as one field.
2. Reorder and compress the editorial sidebar around guidance, intention,
   channel status, and recent activity.
3. Simplify `cognitive flow` by moving current-phase meaning into the bridge
   itself and removing the competing sidecard.
4. Expand lower-grid role separation with a dedicated reflection surface.
5. Reduce summary metrics density so the scenic closure dominates the ending.
6. Validate with focused frontend build and diff checks.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- dashboard no longer reads as hero plus a second mini-dashboard
- flow bridge feels integrated rather than like a separate widget plus sidecard
- right sidebar has clearer editorial pacing
- closure gives more visual authority to the scenic summary than to stat blocks

## Definition of Done
- [ ] Dashboard structure is materially closer to the canonical audit target.
- [ ] No route contracts or data ownership rules changed.
- [ ] Focused frontend validation evidence is attached.

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
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css`
- Manual checks:
  - structure review against the dashboard sections named in the master audit
- Screenshots/logs:
  - browser screenshot parity remains a follow-up loop
- High-risk checks:
  - dashboard continues using the same derived runtime data and health inputs

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/27_codex_instructions.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
- Canonical visual target:
  - authenticated dashboard flagship overview
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - flagship overview stage
  - dashboard scenic closure
- New shared pattern introduced: no
- Design-memory entry reused:
  - flagship overview stage
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - keep using existing raster atmosphere and closure assets
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
  - browser screenshot parity still pending
  - final responsive crop tuning may still be needed after deploy review
- State checks: success
- Responsive checks: desktop | mobile
- Input-mode checks: pointer | touch
- Accessibility checks:
  - semantic sections preserved
  - buttons remain keyboard-focusable
- Parity evidence:
  - local structure moved closer to the audit's `hero authority / sidebar / flow bridge / lower closure` sequence

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - revert this frontend slice if dashboard composition regresses

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
- This slice intentionally stops before browser screenshot parity and further
  route-family refinement.

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
- Refresh/restart behavior verified: yes
- Regression check performed:
  - existing dashboard-derived runtime summaries still drive the same surfaces

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
  - reshaped dashboard composition toward the canonical flagship read with a calmer sidebar, integrated flow bridge, and more differentiated lower closure
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/tasks/PRJ-779-dashboard-structural-canonical-convergence-pass.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css`
- What is incomplete:
  - browser screenshot parity and any remaining crop tuning after deploy review
- Next steps:
  - capture fresh deploy screenshots and compare `public home + dashboard` against canonical references
- Decisions made:
  - keep existing data and assets; change composition and pacing only
