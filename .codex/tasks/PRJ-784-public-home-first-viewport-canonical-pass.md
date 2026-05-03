# Task

## Header
- ID: PRJ-784
- Title: Rebuild public home first viewport toward canonical landing parity
- Task Type: design
- Current Stage: release
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-782
- Priority: P1

## Context
After removing fake window chrome in `PRJ-782`, the strongest remaining gap in
the public landing is the first viewport. The deployed and local screenshots
still show a fragmented composition: left hero copy, right abstract motif
panel, and a separate lower card strip. The canonical landing instead reads as
one coherent flagship scene with a real embodied figure, anchored cognition
cards, and a bridge band that closes the first viewport gracefully.

## Goal
Bring the public landing first viewport materially closer to the canonical
landing by unifying the hero scene around a real figure asset and a connected
feature bridge.

## Deliverable For This Stage
One frontend slice that:
- replaces the abstract hero placeholder with an embodied image-led stage
- integrates the cognition cards into that hero stage
- upgrades the lower feature strip into a bridge band closer to the canonical
  first-viewport closure
- reduces redundant hero copy signals that compete with the main headline

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-784-public-home-first-viewport-canonical-pass.md`

## Implementation Plan
1. Replace the current abstract `MotifFigurePanel` treatment with a landing
   stage centered on the approved embodied figure asset already in `web/public`.
2. Integrate the cognition highlight cards around the figure inside the same
   stage so the hero reads as one scene rather than a panel plus notes.
3. Remove the extra hero kicker if it weakens the canonical hierarchy.
4. Rework the first strip under the hero into a connected bridge band with the
   existing pillar content and a quieter trust/proof closure.
5. Validate with frontend build, diff checks, and a fresh local screenshot.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- the public hero uses a real embodied figure rather than a purely abstract
  placeholder
- cognition cards are visually integrated into the hero stage
- the first strip under the hero reads as a bridge band rather than generic
  repeated cards
- build and focused diff checks pass

## Definition of Done
- [x] The public landing first viewport is materially closer to the canonical landing.
- [x] Existing auth entry behavior remains intact.
- [x] Focused frontend validation and screenshot evidence are attached.

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
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-784-public-home-first-viewport-canonical-pass.md`
- Manual checks:
  - compared the local first viewport against the canonical landing reference
  - 2026-05-03 closure sync reviewed `web/src/App.tsx`,
    `web/src/index.css`, `docs/ux/design-memory.md`,
    `.codex/context/TASK_BOARD.md`, and later PRJ-866/PRJ-869/PRJ-875
    evidence
  - confirmed current public landing uses `LANDING_HERO_ART_SRC`,
    `aion-public-hero`, `aion-public-hero-stage`, integrated motif notes, and
    `aion-public-feature-bridge`
  - confirmed `PRJ-782` user clarification supersedes browser-frame cues from
    canonical images: browser mockup frames are preview context and ignored in
    implementation
  - `Select-String -Path web\src\App.tsx,web\src\index.css -Pattern
    "aion-public-browser|WindowChrome|aion-window-chrome"` returned no matches
  - `Push-Location .\web; npm run build; Pop-Location` passed
  - `git diff --check` passed
- Screenshots/logs:
  - `.codex/artifacts/local-public-home-hero-pass-v2-2026-04-29.png`
- High-risk checks:
  - public CTA and auth-entry scroll behavior remained intact

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
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- Canonical visual target:
  - public home / landing first viewport
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - frame-first flagship shell
  - brand logotype and font pairing
- New shared pattern introduced: no
- Design-memory entry reused:
  - frame-first flagship shell
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - reuse the existing embodied figure asset instead of abstract CSS-only
    placeholders for the hero anchor
- Canonical asset extraction required: no
- Screenshot comparison pass completed: yes
- Remaining mismatches:
  - the hero still needs a closer bust-scale relationship to the canonical landing
  - the lower public story grid still feels more product-panel than editorial landing
  - dashboard still needs its own structural pass
- State checks: success
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - auth CTA and nav controls remain code-native and reachable
- Parity evidence:
  - local screenshot after implementation was compared to the canonical landing image

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - revert the public landing slice if the new stage harms readability or auth access

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
- This slice intentionally stops at the first viewport and its bridge band.
- Browser-window framing in later canonical screenshots or board notes is not
  implementation guidance. Per 2026-05-03 user clarification, browser mockup
  chrome is presentation context and must be ignored.

## 2026-05-03 Closure Sync

- This is a historical public-home first-viewport implementation slice, no
  longer an active `IN_PROGRESS` task.
- Later `PRJ-866`, `PRJ-869`, and `PRJ-875` carry the active landing proof
  trail, but their browser-window/frame wording is superseded by the
  `PRJ-782` decision resolution and `docs/ux/design-memory.md`.
- Current public landing source keeps the embodied/scenic hero stage and
  bridge band while removing browser mockup chrome.
- Remaining landing parity work should proceed from the chrome-free shell and
  compare against the canonical content/composition, not the preview browser
  container.

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
  - public entry still anchors auth navigation and CTA scroll behavior

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
  - rebuilt the landing first viewport around a real embodied figure stage and
    a connected bridge band under the hero
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/tasks/PRJ-784-public-home-first-viewport-canonical-pass.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-784-public-home-first-viewport-canonical-pass.md`
  - local screenshot review via `.codex/artifacts/local-public-home-hero-pass-v2-2026-04-29.png`
- What is incomplete:
  - lower landing story grid
  - tighter canonical bust-scale and proof rhythm
  - dashboard structural pass
- Next steps:
  - refine the public story grid and right-side proof density
  - then run the next dashboard structural convergence slice
- Decisions made:
  - the public first viewport now prefers a real embodied asset over abstract
    CSS-only placeholder geometry

## Closure Result Report

- Goal:
  - close `PRJ-784` after resolving the public chrome-free landing direction
- Scope:
  - task status, evidence, and context sync only
- Implementation Plan:
  - verify current public landing source
  - verify later landing proof owners
  - record the PRJ-782 browser-mockup clarification as superseding old
    browser-frame cues
  - update project context and board state
- Acceptance Criteria:
  - no stale `IN_PROGRESS` state remains for `PRJ-784`
  - public first viewport remains on the embodied/scenic landing path
  - no browser mockup chrome is treated as canonical implementation guidance
  - auth entry behavior remains unchanged
- Definition of Done:
  - original validation evidence is preserved
  - current source review is recorded
  - later PRJ-866/PRJ-869/PRJ-875 proof ownership is recorded
  - context files are updated
  - `Push-Location .\web; npm run build; Pop-Location` passes
  - `git diff --check` passes
- Next:
  - review `PRJ-800A`/landing follow-up drift entries for stale browser-frame
    wording before reopening route-local visual work
