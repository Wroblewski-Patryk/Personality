# Task

## Header
- ID: PRJ-800H
- Title: Make Public Entry Landing-First
- Task Type: design
- Current Stage: verification
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-800G
- Priority: P0

## Context
Production evidence shows that the public entry still behaves like an
authenticated-first route:

- `/` normalizes to `/dashboard`
- the fullscreen bootstrap spinner renders before the public landing can appear
- headless and first-load experiences therefore show "Preparing your workspace"
  instead of the canonical public landing

This is a structural layout issue, not a decorative one. It conflicts with the
canonical requirement that public entry is landing-first and that the landing is
the true public shell.

## Goal
Make the public entry landing-first so `/` and unauthenticated entry render the
public landing immediately, while authenticated bootstrap remains intact for
private routes.

## Deliverable For This Stage
A production-ready route/bootstrap refinement in `web/src/App.tsx`, plus any
required source-of-truth updates, validated by build and focused local route
evidence.

## Scope
- `web/src/App.tsx`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-800H-make-public-entry-landing-first.md`

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Implementation Plan
1. Change route normalization so `/` resolves to the public landing route.
2. Limit the fullscreen bootstrap spinner to authenticated/private entry only.
3. Preserve the existing bootstrap and authenticated redirect behavior.
4. Validate build plus route-level local screenshots for `/` and `/login`.
5. Sync task board and project state.

## Acceptance Criteria
- `/` resolves to the public landing instead of private dashboard entry.
- Unauthenticated first-load no longer shows the fullscreen bootstrap card.
- Authenticated bootstrap remains intact for private routes.
- Build and focused diff validation pass.

## Definition of Done
- [x] Root route is landing-first.
- [x] Public entry no longer blocks behind fullscreen bootstrap.
- [x] Authenticated bootstrap behavior is preserved.
- [x] Build and focused diff validation pass.
- [x] Task board and project state are updated in the same slice.

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
  - `git diff --check -- web/src/App.tsx .codex/tasks/PRJ-800H-make-public-entry-landing-first.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- Manual checks:
  - verified that local `/` renders the same public landing as `/login`
  - verified that the fullscreen bootstrap card no longer blocks public entry
- Screenshots/logs:
  - `.codex/artifacts/local-root-after-prj800h.png`
  - `.codex/artifacts/local-login-after-prj800h.png`
  - `.codex/artifacts/prod-root-live-wait-2026-04-29.png`
  - `.codex/artifacts/prod-login-live-2026-04-29.png`
- High-risk checks:
  - preserved authenticated bootstrap behavior by keeping fullscreen bootstrap
    for private routes only

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/planning/layout-sidebar-home-dashboard-canonical-parity-master-ledger.md`
  - `docs/planning/layout-dashboard-public-home-canonical-master-audit.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- Canonical visual target: public home flagship landing as true public entry
- Fidelity target: structural_parity
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: current public landing shell
- New shared pattern introduced: no
- Design-memory entry reused: landing-first public shell direction
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: reuse existing assets only
- Canonical asset extraction required: no
- Screenshot comparison pass completed: partial
- Remaining mismatches:
  - deploy-side proof still required after the route/bootstrap change
- State checks: loading, success
- Responsive checks: desktop-focused in this slice
- Input-mode checks: pointer
- Accessibility checks: public content order and route-first rendering
- Parity evidence:
  - `.codex/artifacts/prod-root-live-wait-2026-04-29.png`
  - `.codex/artifacts/prod-login-live-2026-04-29.png`

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: no
- Rollback note: revert public-entry route/bootstrap slice

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
This slice is intentionally structural: it fixes the public-entry contract
before any further decorative parity work on the landing.

## Production-Grade Required Contract

Every task must include these mandatory sections before it can move to `READY`
or `IN_PROGRESS`:

- `Goal`
- `Scope` with exact files, modules, routes, APIs, schemas, docs, or runtime surfaces
- `Implementation Plan` with step-by-step execution and validation
- `Acceptance Criteria` with testable conditions
- `Definition of Done` using `DEFINITION_OF_DONE.md`
- `Result Report`

Runtime tasks must be delivered as a vertical slice: UI -> logic -> API -> DB
-> validation -> error handling -> test. Partial implementations, mock-only
paths, placeholders, fake data, and temporary fixes are forbidden.

## Integration Evidence

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: yes
- Endpoint and client contract match: yes
- DB schema and migrations verified: not applicable
- Loading state verified: yes
- Error state verified: not applicable
- Refresh/restart behavior verified: yes
- Regression check performed: build plus route screenshot checks

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
  - corrected the public-entry contract so the public landing is rendered
    immediately on `/` and `/login`, while authenticated routes keep their
    existing bootstrap behavior
- Files changed:
  - `web/src/App.tsx`
  - `.codex/tasks/PRJ-800H-make-public-entry-landing-first.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx .codex/tasks/PRJ-800H-make-public-entry-landing-first.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - local headless screenshots for `/` and `/login`
- What is incomplete:
  - deploy-side confirmation still needs the new revision to go live
- Next steps:
  - confirm on production that `/` no longer flashes the fullscreen bootstrap card
  - continue the next visual parity loop on `home` and `dashboard`
- Decisions made:
  - resolved `/` to the public landing route
  - kept the existing bootstrap mechanism but scoped fullscreen blocking to private entry only
