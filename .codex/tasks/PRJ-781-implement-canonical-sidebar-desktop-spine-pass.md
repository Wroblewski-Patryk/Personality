# Task

## Header
- ID: PRJ-781
- Title: Implement canonical sidebar desktop spine pass
- Task Type: design
- Current Stage: implementation
- Status: IN_PROGRESS
- Owner: Frontend Builder
- Depends on: PRJ-780
- Priority: P1

## Context
`PRJ-780` froze the authenticated sidebar as the canonical layout spine for the
parent shell. This task implements the first real desktop convergence slice
using the current route contract only.

## Goal
Bring the authenticated desktop sidebar materially closer to the canonical
reference in width, brand hierarchy, nav anatomy, active state, and support
stack composition.

## Deliverable For This Stage
One frontend slice in `web/src/App.tsx` and `web/src/index.css` that:
- redesigns the desktop rail around the canonical sidebar spine
- replaces token letters with line icons
- removes secondary nav description lines
- rebuilds the support stack into health, identity, and quote cards
- preserves current route behavior and account access

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-781-implement-canonical-sidebar-desktop-spine-pass.md`

## Implementation Plan
1. Add sidebar-specific brand and icon primitives.
2. Rebuild desktop nav rows to match the canonical one-line icon-led anatomy.
3. Adjust rail proportion, padding, material, and active pill treatment.
4. Redesign support stack into compact health, identity, and quote cards.
5. Preserve account access through the existing shell account state.
6. Validate with focused frontend build and diff checks.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- desktop authenticated rail is visibly closer to the frozen canonical sidebar
- navigation remains backed only by currently implemented routes
- support stack reads as one canonical family instead of generic panels
- build and focused diff checks pass

## Definition of Done
- [ ] Desktop sidebar spine is materially closer to the canonical rail.
- [ ] Current route behavior remains intact.
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
  - sidebar JSX and CSS reviewed against the canonical sidebar plan
- Screenshots/logs:
  - browser screenshot parity remains the next loop
- High-risk checks:
  - only current real routes remain interactive

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/27_codex_instructions.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: yes
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - full canonical route inventory still needs a separate route-expansion decision

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aviary-sidebar-layout-canonical-reference-v1.png`
- Canonical visual target:
  - authenticated desktop sidebar layout
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - canonical authenticated sidebar spine
- New shared pattern introduced: no
- Design-memory entry reused:
  - canonical authenticated sidebar spine
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - preserve the warm paper-like rail and lower closure wash
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
  - full 1:1 nav inventory remains blocked by current route-contract scope
  - post-deploy pixel tuning still needed
- State checks: success
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - nav remains button-based and keyboard focusable
- Parity evidence:
  - local desktop rail moved closer in anatomy, but screenshot proof is still pending

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - revert the frontend slice if the new rail harms shell usability

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
- This task intentionally uses only implemented routes to avoid silent contract
  expansion.

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
  - shell route changes still use the existing route change handler

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
  - implemented the first desktop sidebar convergence pass around the frozen canonical rail
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/tasks/PRJ-781-implement-canonical-sidebar-desktop-spine-pass.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css`
- What is incomplete:
  - deploy screenshot parity
  - full canonical module inventory
- Next steps:
  - compare deployed desktop shell against the canonical sidebar image and tune spacing/materials
- Decisions made:
  - preserve current route contract and focus on anatomy-first convergence
