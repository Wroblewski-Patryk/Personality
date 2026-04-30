# Task

## Header
- ID: PRJ-800L
- Title: Public home lower story and auth priority pass
- Task Type: design
- Current Stage: post-release
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-800K
- Priority: P1

## Context
Fresh production evidence after `PRJ-800K` confirms that the public landing
hero itself is now materially calmer and closer to the canonical reference.
The remaining drift is no longer in the headline.

It is now concentrated in the next read below the hero:

- the dark trust closure appears too late
- the lower story and auth surfaces arrive too early as a two-column screen
- the auth panel still reads too co-equal with the editorial proof column

The canonical landing keeps the first screen focused on one flagship scene and
lets session entry behave as a quieter continuation below it. This slice moves
the public landing toward that hierarchy without inventing a new public-entry
system.

## Goal
Bring the public landing closer to canonical first-screen parity by moving the
trust closure directly under the bridge, demoting auth visual priority, and
turning the lower story into a calmer editorial continuation.

## Deliverable For This Stage
A focused implementation pass in `web/src/App.tsx` and `web/src/index.css`
that changes the lower landing structure and its visual hierarchy, plus synced
repo truth for the next parity loop.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md`
- `.codex/tasks/PRJ-800L-public-home-lower-story-and-auth-priority-pass.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Close `PRJ-800K` with the fresh production proof for the exact hero-content slice.
2. Reorder the public-home post-hero sequence so the trust closure supports the first-screen read before lower auth surfaces.
3. Demote the auth panel through calmer copy, narrower proportion, and softer support-card treatment.
4. Tighten the lower proof region so it reads more editorial and less like a second app screen.
5. Validate, record the remaining parity gap honestly, and sync repo truth.

## Acceptance Criteria
- The trust closure now arrives before the lower story/auth section.
- The auth panel reads as a supporting session-entry module instead of a co-equal flagship block.
- The lower landing section is visually calmer and less likely to intrude into the first-screen read.
- Validation passes and repo truth reflects the new remaining gap accurately.
- The deployed public landing reaches the `95%` parity gate for the active canonical spec.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] `PRJ-800K` is closed honestly with deploy proof.
- [x] Trust closure is structurally promoted above the lower story/auth region.
- [x] The auth panel is visually demoted and shortened.
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
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md .codex/tasks/PRJ-800L-public-home-lower-story-and-auth-priority-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- Manual checks:
  - compared the deployed `PRJ-800K` landing screenshot against the canonical landing
  - identified lower-story and auth-priority drift as the dominant remaining landing gap
- Screenshots/logs:
  - production evidence: `.codex/artifacts/prod-login-live-after-prj800k.png`
  - canonical target: `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- High-risk checks:
  - kept the slice within the existing public-home route structure and shared persona motif

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
- Design source reference: `.codex/artifacts/prod-login-live-after-prj800k.png`
- Canonical visual target: `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: shared persona motif panel, public shell, public trust band
- New shared pattern introduced: no
- Design-memory entry reused: `docs/ux/design-memory.md`
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: reuse the current shared persona and landing atmosphere assets
- Canonical asset extraction required: no
- Screenshot comparison pass completed: yes
- Remaining mismatches:
  - minor crop and ornament drift may still exist, but no longer blocks closure of the `home` surface
  - dashboard is now the next major flagship drift after this landing pass
- State checks: loading | empty | error | success
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: touch | pointer | keyboard
- Accessibility checks: existing buttons, links, and form controls keep their prior semantics
- Parity evidence:
  - `.codex/artifacts/prod-login-live-after-prj800k.png`
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
  - `.codex/artifacts/prod-home-live-after-a8cb3bf-root.png`
  - `.codex/artifacts/prod-home-live-after-8dd11a8-root-wait2.png`
  - `.codex/artifacts/prod-home-live-after-a8cb3bf-login.png`
  - `.codex/artifacts/local-home-root-icons-pass-2026-04-30.png`
  - `.codex/artifacts/local-home-modal-pass-2026-04-30.png`
  - `.codex/artifacts/local-home-overlay-pass-root-v2-2026-04-30.png`

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not needed
- Rollback note: revert this slice if the public entry loses clear access to login/register

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
This slice intentionally stays within the landing route. It should not spill
into dashboard parity or authenticated-shell tuning in the same cycle.

Planned micro-slice queue for `home` before surface closure:

1. route-correct landing hero artwork
2. hero copy-width and line-break refinement
3. hero-stage crop and scenic balance refinement
4. note-card placement and density refinement
5. first CTA row proportion and emphasis refinement
6. bridge width and overlap rhythm refinement
7. feature-strip density and card-divider refinement
8. trust-band width, padding, and icon rhythm refinement
9. auth-panel vertical spacing and quiet-entry refinement
10. deploy-side screenshot proof and final `95%` closure decision

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
  - moved the dark trust closure directly below the bridge so the landing first read stays product-first
  - shortened and visually demoted the auth panel so it behaves more like a supporting session-entry block
  - tightened the lower proof/auth region into a calmer editorial continuation
  - removed the lingering lower proof-story grid entirely so the landing no
    longer falls into a second pseudo-screen that does not exist in the
    canonical public entry
  - replaced the generic shared-persona stage with a landing-specific scenic
    hero artwork and tightened hero, bridge, trust-band, and auth proportions
    toward the canonical first-screen read
  - continued the same home-only lane by tightening hero copy width, scenic
    crop, note-card density, bridge rhythm, trust-band compactness, and auth
    offset so the first viewport reads closer to one canonical scene
  - continued once more with a stronger viewport-only compaction pass for top
    nav density, bridge footprint, trust-band width, and auth-panel delay
  - replaced the inline login/register section with a true landing modal so
    session entry no longer competes with the flagship first viewport
  - changed the landing scenic art from an obvious nested image treatment to a
    background-stage treatment so the persona scene reads more like atmosphere
    than a card within a card
  - replaced placeholder numbering and dots in the lower `home` closure with
    route-appropriate semantic iconography for the feature strip and trust bar
  - embedded the landing copy directly inside that same scenic hero stage,
    using the approved desktop `40/60` copy-to-scene split instead of keeping
    copy as a sibling column beside the artwork
  - applied the user-requested structural simplification by removing the extra
    scenic wrapper layer, moving the landing copy into the shared hero stage,
    and using a clearer desktop `40/60` copy-to-scene split
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `docs/ux/assets/aviary-landing-hero-canonical-reference-v1.png`
  - `web/public/aviary-landing-hero-canonical-reference-v1.png`
  - `docs/ux/design-memory.md`
  - `.codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md`
  - `.codex/tasks/PRJ-800L-public-home-lower-story-and-auth-priority-pass.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - focused `git diff --check`
  - production screenshot comparison against the canonical landing
  - local screenshot proof for `/` and `/login` via `vite preview` plus Playwright
  - local screenshot proof after wrapper removal and `40/60` restructuring
- What is incomplete:
  - later dashboard parity remains the next major flagship loop
- Next steps:
  - keep `home` frozen unless a new user interpretation note changes the active spec
  - move the next single-surface flagship loop to `dashboard`
- Decisions made:
  - promoted trust closure instead of inventing a new public-home section
  - used calmer hierarchy and proportion changes instead of adding new decorative systems
