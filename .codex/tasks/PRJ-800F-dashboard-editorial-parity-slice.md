# Task

## Header
- ID: PRJ-800F
- Title: Dashboard Editorial Parity Slice
- Task Type: design
- Current Stage: release
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-800D, PRJ-800E
- Priority: P1

## Context
`PRJ-800D` brought the dashboard much closer to the canonical composition, and
`PRJ-800E` stabilized the public landing family. The remaining dashboard drift
is now concentrated in three visible zones:

- the central figure stage still needs stronger dominance relative to the side cards
- the right editorial rail is still slightly heavier and more card-like than the canonical reference
- the lower closure is still a bit too tall and modular instead of panoramic

Because local preview does not have a clean authenticated session path without
adding new mechanics, this slice focuses on bounded composition refinements that
reuse the existing dashboard contract and prepare the next deploy-side compare.

## Goal
Refine the dashboard composition so the hero, editorial rail, and lower closure
read closer to the canonical flagship tableau without inventing new structures.

## Deliverable For This Stage
A focused dashboard parity slice in `web/src/App.tsx` and `web/src/index.css`
that tightens the canonical composition and is ready for deploy-side screenshot
comparison.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Implementation Plan
1. Increase figure-stage dominance and calm the side signal columns.
2. Tighten the editorial rail so guidance, recent activity, and intention read
   closer to the canonical right stack.
3. Compress the flow-to-summary cadence and make the bottom closure feel more
   panoramic.
4. Validate build and focused diff checks.
5. Sync task board and project state with the current slice status.

## Acceptance Criteria
- Dashboard hero reads more like one central flagship scene.
- Right rail feels less like stacked cards and more like an editorial support rail.
- Lower closure feels calmer and closer to the panoramic canonical ending.
- Build and focused diff validation pass.

## Definition of Done
- [x] Figure-stage dominance is improved.
- [x] Right rail pacing is calmer.
- [x] Lower closure is more panoramic.
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
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- Manual checks:
  - compared the current dashboard structure and styling directly against
    `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - used the existing parity ledger and micro-checklist to target the highest
    remaining compositional drift
  - 2026-05-03 closure sync reviewed `web/src/App.tsx`,
    `web/src/index.css`, `docs/ux/dashboard-proof-matrix.md`,
    `docs/ux/design-memory.md`, `docs/ux/flagship-baseline-transfer.md`,
    `.codex/context/TASK_BOARD.md`, and `.codex/context/PROJECT_STATE.md`
  - confirmed current source uses `DASHBOARD_HERO_ART_SRC` with
    `aviary-dashboard-hero-canonical-reference-v4.png`
  - confirmed later `PRJ-870` and `PRJ-875` carry screenshot/build proof for
    the dashboard route after this editorial parity lane
  - `git diff --check` passed
- Screenshots/logs:
  - canonical reference: `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
- High-risk checks:
  - avoided introducing any new dashboard structures or mock-only surfaces

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
- Design source reference:
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
- Canonical visual target: authenticated dashboard flagship route
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: authenticated shell, canonical persona continuity
- New shared pattern introduced: no
- Design-memory entry reused: shared canonical persona continuity
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: reuse existing dashboard atmosphere and scenic closure assets
- Background or decorative asset strategy: use one integrated dashboard hero artwork plus the existing scenic closure assets
- Background or decorative asset strategy: use one integrated dashboard hero artwork with dashboard-specific guidance/orchestration props plus the existing scenic closure assets
- Canonical asset extraction required: no
- Screenshot comparison pass completed: partial
- Remaining mismatches:
  - deploy-side screenshot compare still required for authenticated proof
- State checks: success
- Responsive checks: desktop-focused in this slice
- Input-mode checks: pointer
- Accessibility checks: content order, action labels, heading hierarchy
- Parity evidence:
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: no
- Rollback note: revert dashboard editorial parity slice

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
This slice intentionally stays within composition refinements because local
preview still lacks a clean authenticated screenshot path without introducing a
new mechanism.

## 2026-05-03 Closure Sync

- This dashboard editorial parity lane is historical and no longer an active
  `IN_PROGRESS` task.
- The task accumulated multiple bounded dashboard passes: hero hierarchy,
  right rail calming, CTA hierarchy, figure-caption removal, unified hero
  artwork, route-corrected dashboard hero artwork, proportions, crop/spacing,
  callout scale, and flow/closure rhythm.
- Current active dashboard truth points to:
  - `docs/ux/dashboard-proof-matrix.md`
  - `docs/ux/design-memory.md`
  - `docs/ux/flagship-baseline-transfer.md`
  - `web/src/App.tsx`
  - `web/src/index.css`
- Later proof owners:
  - `PRJ-870` dashboard `99%` canonical evidence pass
  - `PRJ-875` canonical UI final route sweep
- Remaining dashboard proof gaps should be tracked from those newer artifacts,
  not by keeping `PRJ-800F` open.

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
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: yes
- Regression check performed: build plus focused diff checks

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
  - refined the dashboard composition toward the canonical editorial read by
    tightening the hero hierarchy, calming the right rail, and compressing the
    lower closure
  - continued the same lane by pruning dashboard CTA clutter so the route
    reads less like an operational control panel and more like one flagship
    tableau
  - corrected that decluttering pass by restoring the quiet support actions
    that do exist in the canonical dashboard, while keeping them visually soft
    and secondary
  - continued the same single-surface lane by removing the non-canonical
    figure caption, simplifying recent-activity rows, and trimming extra
    narrative copy from the intention card
  - replaced the split dashboard hero implementation with one integrated wide
    hero artwork so the shared persona, atmosphere, and cognition details read
    as one continuous scenic stage
  - replaced that first integrated hero with a route-corrected dashboard
    variant that removes `personality` props and uses orchestration and
    cognition-field symbols instead
  - continued the same single-surface lane with a proportions-only pass that
    gives the center hero more authority, narrows the editorial rail, and
    flattens the lower closure so the whole route reads less like stacked cards
    and more like one flagship tableau
  - continued once more with a crop-and-spacing pass that lifts the dashboard
    persona higher in frame, narrows the right rail density, and lets the
    closure scenic panel breathe more like the canonical panoramic ending
  - continued again with a signal-and-callout scale pass that reduces the card
    feel of side metrics, figure notes, and harmony ornament so the screen
    reads more like one illustration-led product surface
  - continued with a flow-and-closure rhythm pass that softens the center
    orchestration instrument and compresses the lower cards so the bottom half
    reads more like one calm continuation of the hero
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `docs/ux/assets/aviary-dashboard-hero-canonical-reference-v3.png`
  - `docs/ux/assets/aviary-dashboard-hero-canonical-reference-v4.png`
  - `web/public/aviary-dashboard-hero-canonical-reference-v3.png`
  - `web/public/aviary-dashboard-hero-canonical-reference-v4.png`
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- What is incomplete:
  - authenticated screenshot parity is still pending and must happen after deploy
  - the old `v3` dashboard hero asset can now be retired later if no historical
    reference path still needs it
- Next steps:
  - compare the deployed dashboard to `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - verify whether the new route-corrected hero artwork plus the latest
    hero-dominance, rail-calmness, and lower-closure compaction pass are
    enough to close `PRJ-800F`
- Decisions made:
  - kept the existing dashboard information architecture and improved the
    composition through proportion and material tuning only
  - continued tightening the same dashboard task instead of inventing a second dashboard route structure

## Closure Result Report

- Goal:
  - close stale `PRJ-800F` after confirming later dashboard proof owners carry
    the active route evidence
- Scope:
  - task status, task evidence, and context sync only
- Implementation Plan:
  - verify current dashboard source and approved hero asset
  - record later proof owners
  - mark the historical task done
  - update project context and task board
- Acceptance Criteria:
  - no stale `IN_PROGRESS` state remains for `PRJ-800F`
  - dashboard editorial parity history is preserved
  - current dashboard truth points to PRJ-870/PRJ-875 and dashboard proof docs
  - no route, API, auth, DB, or runtime behavior changes are introduced
- Definition of Done:
  - original build and diff evidence is preserved
  - current source review is recorded
  - later screenshot/build proof ownership is recorded
  - context files are updated
  - `git diff --check` passes
- Next:
  - review `PRJ-800G` public home production parity slice for stale status
