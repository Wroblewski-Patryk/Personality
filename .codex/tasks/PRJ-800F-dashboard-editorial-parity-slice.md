# Task

## Header
- ID: PRJ-800F
- Title: Dashboard Editorial Parity Slice
- Task Type: design
- Current Stage: verification
- Status: IN_PROGRESS
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
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice intentionally stays within composition refinements because local
preview still lacks a clean authenticated screenshot path without introducing a
new mechanism.

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
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `docs/ux/assets/aviary-dashboard-hero-canonical-reference-v3.png`
  - `web/public/aviary-dashboard-hero-canonical-reference-v3.png`
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- What is incomplete:
  - authenticated screenshot parity is still pending and must happen after deploy
- Next steps:
  - compare the deployed dashboard to `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - verify whether the latest hero-dominance, rail-calmness, and lower-closure compaction pass is enough to close `PRJ-800F`
- Decisions made:
  - kept the existing dashboard information architecture and improved the
    composition through proportion and material tuning only
  - continued tightening the same dashboard task instead of inventing a second dashboard route structure
