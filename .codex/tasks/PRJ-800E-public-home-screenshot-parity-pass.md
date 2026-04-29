# Task

## Header
- ID: PRJ-800E
- Title: Public Home Screenshot Parity Pass
- Task Type: design
- Current Stage: verification
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-800C, PRJ-800D
- Priority: P1

## Context
After `PRJ-800C`, the public landing moved closer to the canonical editorial
direction. After `PRJ-800D`, the dashboard structure was compressed. A fresh
local screenshot comparison against
`docs/ux/assets/aion-landing-canonical-reference-v1.png` shows the landing is
still too sectional in the first viewport:

- the hero copy still behaves too much like a left column plus separate motif panel
- the motif stage feels boxed instead of integrated into one flagship scene
- the bridge band is still too content-heavy and repetitive below the hero

## Goal
Bring the public home first viewport and immediate continuation materially
closer to the canonical landing through screenshot-driven refinements to the
nav, hero, motif stage, and bridge band.

## Deliverable For This Stage
A production-ready public-home parity refinement pass in `web/src/App.tsx` and
`web/src/index.css`, validated by local build and screenshot evidence.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-800E-public-home-screenshot-parity-pass.md`

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Implementation Plan
1. Tighten the public nav and CTA hierarchy so the top frame feels lighter and
   closer to the canonical landing.
2. Remove unnecessary hero eyebrow treatment and give the hero copy more
   canonical headline/body rhythm.
3. Enlarge and soften the motif stage so it reads as one flagship scene rather
   than a separate bordered card.
4. Simplify the bridge band to reduce repetition and support the hero instead
   of competing with it.
5. Validate build, capture local screenshot evidence, and sync source-of-truth
   files.

## Acceptance Criteria
- Public landing first viewport reads closer to one integrated flagship scene.
- Motif figure and notes feel less boxed and more canonical in scale/placement.
- The bridge band is calmer and less repetitive.
- Build and focused diff checks pass.

## Definition of Done
- [x] Public nav and CTA hierarchy are calmer.
- [x] Hero copy is closer to canonical rhythm.
- [x] Motif stage is more integrated and less panel-like.
- [x] Bridge band repetition is reduced.
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
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800E-public-home-screenshot-parity-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- Manual checks:
  - compared the fresh local public-home screenshot against the canonical landing
    and used the remaining drift to drive one more integrated-scene refinement
- Screenshots/logs:
  - `.codex/artifacts/local-home-after-prj800d.png`
  - `.codex/artifacts/local-home-after-prj800e.png`
  - `.codex/artifacts/local-home-after-prj800e-v2.png`
- High-risk checks:
  - verified the negative-margin bridge treatment collapses back to normal flow
    for narrower breakpoints

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/ux/canonical-visual-implementation-workflow.md`
  - `docs/ux/background-and-decorative-asset-strategy.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- Canonical visual target: public home flagship landing
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: public landing shell, shared canonical persona
- New shared pattern introduced: no
- Design-memory entry reused: shared canonical persona continuity
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: reuse existing persona and motif surfaces
- Canonical asset extraction required: no
- Screenshot comparison pass completed: yes
- Remaining mismatches:
  - deployed screenshot compare still required
  - landing still needs later micro-tuning in headline brevity and browser-shell
    atmosphere if full `1:1` parity remains the goal
- State checks: success
- Responsive checks: desktop
- Input-mode checks: pointer
- Accessibility checks: content order, button presence, headline hierarchy
- Parity evidence:
  - `.codex/artifacts/local-home-after-prj800d.png`

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: no
- Rollback note: revert public-home parity slice

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
This slice is intentionally limited to the public home because the local route
without a persisted session cannot render the full authenticated dashboard.

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
- Regression check performed: local preview screenshot plus build

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
  - refined the public landing through screenshot-driven parity work so the
    first viewport and bridge band behave more like one flagship scene and less
    like stacked sections
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/tasks/PRJ-800E-public-home-screenshot-parity-pass.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800E-public-home-screenshot-parity-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - captured and visually reviewed `.codex/artifacts/local-home-after-prj800e-v2.png`
    against `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- What is incomplete:
  - deploy-side screenshot proof is still required
  - perfect browser-shell parity is intentionally deferred because the user
    already rejected the previous fake window-chrome wrapper approach
- Next steps:
  - compare the deployed landing after this push
  - then continue with the next dashboard screenshot-parity closure loop
- Decisions made:
  - kept the landing free of a fake window wrapper while still borrowing the
    canonical integrated-scene rhythm
  - used overlap and material changes instead of introducing a new landing
    structure
