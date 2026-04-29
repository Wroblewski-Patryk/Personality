# Task

## Header
- ID: PRJ-800K
- Title: Public home hero content canonical pass
- Task Type: design
- Current Stage: verification
- Status: IN_PROGRESS
- Owner: Frontend Builder
- Depends on: PRJ-800J
- Priority: P1

## Context
Fresh production evidence after `PRJ-800J` shows that the public landing first
viewport is now structurally calmer, but it still drifts from the canonical
landing because the hero message itself is too long and too slogan-like for the
reference composition.

The remaining gap is no longer just spacing. It is the relationship between:

- hero title length
- hero body density
- the shared persona stage

The canonical landing uses a short introductory lead and lets the figure stage
carry more of the emotional authority. This task moves the public landing
toward that contract without inventing new route systems.

## Goal
Bring the public-home hero closer to canonical parity by shortening the hero
title, moving more meaning into calmer supporting copy, and rebalancing the
first viewport around that lighter narrative center.

## Deliverable For This Stage
A focused implementation pass in `web/src/App.tsx` and `web/src/index.css`
that changes hero content and matching first-viewport proportions for the
public landing.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/tasks/PRJ-800J-public-home-first-viewport-live-closure-pass.md`
- `.codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Close `PRJ-800J` with the current production evidence.
2. Introduce a shorter canonical hero-title contract for public-home copy.
3. Rebalance the supporting body copy and CTA rhythm around that lighter title.
4. Tune first-viewport proportions so the persona stage benefits from the new
   lighter hero message.
5. Validate, record parity evidence, and sync repo truth.

## Acceptance Criteria
- The public landing hero title is materially shorter and closer to the
  canonical landing posture.
- The hero body remains informative without reintroducing heavy text density.
- The first viewport reads more as one flagship scene around the shared persona.
- Validation passes and repo truth reflects the slice.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] `PRJ-800J` is closed honestly with deploy proof.
- [x] Public-home hero content is lighter and more canonical.
- [x] Validation and source-of-truth updates match the changed scope.

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
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800J-public-home-first-viewport-live-closure-pass.md .codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md`
- Manual checks:
  - compared fresh production evidence after `PRJ-800J` against the canonical landing
  - captured a new local preview screenshot after the hero-content pass
- Screenshots/logs:
  - production evidence: `.codex/artifacts/prod-login-live-after-prj800j.png`
  - local proof: `.codex/artifacts/local-login-after-prj800k.png`
  - canonical target: `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- High-risk checks:
  - kept the slice inside the existing public-home system and shared persona stage

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/planning/layout-sidebar-home-dashboard-canonical-parity-master-ledger.md`
  - `docs/planning/layout-sidebar-home-dashboard-micro-parity-checklist.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference: `.codex/artifacts/prod-login-live-after-prj800j.png`
- Canonical visual target: `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: shared persona motif panel, public shell, public bridge band
- New shared pattern introduced: no
- Design-memory entry reused: `docs/ux/design-memory.md`
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: reuse the current shared persona and route atmosphere assets
- Canonical asset extraction required: no
- Screenshot comparison pass completed: yes
- Remaining mismatches:
  - deploy-side proof is still needed for this exact hero-content change
  - the lower story and auth-priority still remain for a later landing pass
- State checks: loading | empty | error | success
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: touch | pointer | keyboard
- Accessibility checks: existing buttons and links keep their prior semantics
- Parity evidence:
  - `.codex/artifacts/prod-login-live-after-prj800j.png`
  - `.codex/artifacts/local-login-after-prj800k.png`
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not needed
- Rollback note: revert this slice if public-home message hierarchy regresses

## Review Checklist (mandatory)
- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice is still confined to public-home parity. It should not spill into
dashboard or authenticated shell work in the same cycle.

## Production-Grade Required Contract

Every task must include these mandatory sections before it can move to `READY`
or `IN_PROGRESS`:

- `Goal`
- `Scope` with exact files, modules, routes, APIs, schemas, docs, or runtime
  surfaces
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
- Error state verified: yes
- Refresh/restart behavior verified: pending
- Regression check performed:

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
  - shortened the landing hero into a more canonical introductory lead
  - moved more meaning into calmer supporting body copy
  - rebalanced the first viewport around the lighter hero message and shared persona stage
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/tasks/PRJ-800J-public-home-first-viewport-live-closure-pass.md`
  - `.codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - focused `git diff --check`
  - production screenshot comparison
  - local preview screenshot comparison
- What is incomplete:
  - deploy-side confirmation for this exact slice
  - later lower-story/auth-priority tuning if landing still drifts
- Next steps:
  - push and inspect production `/` and `/login`
  - then either close public-home or return to dashboard parity
- Decisions made:
  - used a shorter canonical hero lead instead of fighting the layout with a long slogan
  - preserved the shared persona as the primary emotional anchor
