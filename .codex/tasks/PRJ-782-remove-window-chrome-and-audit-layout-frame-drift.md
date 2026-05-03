# Task

## Header
- ID: PRJ-782
- Title: Remove fake window chrome and realign flagship layout framing
- Task Type: design
- Current Stage: planning
- Status: BLOCKED
- Owner: Frontend Builder
- Depends on: PRJ-776, PRJ-781
- Priority: P1

## Context
The deployed frontend now confirms a product-direction mismatch in the shared
layout frame. The current public and authenticated shells still render a fake
browser-style `WindowChrome`, but explicit user feedback on 2026-04-29
rejected that packaging. The canonical layout should feel premium and framed,
but not simulate browser controls or a title bar.

## Goal
Remove the fake top chrome from shared layout surfaces and update the canonical
layout plan so future convergence work targets a frame-first shell without
browser-window ornament.

## Deliverable For This Stage
One frontend slice that:
- removes `WindowChrome` from public and authenticated shells
- preserves the premium framed shell without introducing a replacement chrome
- records the new canonical frame decision in source-of-truth docs and task
  context
- captures the next highest-value remaining drift for layout and dashboard

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `docs/planning/layout-dashboard-public-home-canonical-master-audit.md`
- `docs/ux/design-memory.md`
- `docs/ux/canonical-web-screen-reference-set.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-782-remove-window-chrome-and-audit-layout-frame-drift.md`

## Implementation Plan
1. Record the explicit user decision that fake browser chrome is not part of
   the canonical flagship layout.
2. Remove the shared `WindowChrome` wrapper from both public and authenticated
   shell branches in `web/src/App.tsx`.
3. Remove obsolete `aion-window-chrome*` styling from `web/src/index.css` and
   rebalance shell body framing if needed.
4. Update the master audit and design memory so later layout and dashboard
   passes converge toward the new frame-first direction.
5. Sync task board and project state with the production audit finding and the
   implementation result.
6. Validate with focused frontend build and diff checks.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- no `WindowChrome` markup remains in the rendered public or authenticated shell
- source-of-truth docs no longer describe fake browser chrome as canonical
- layout framing still reads premium after chrome removal
- build and focused diff checks pass

## Definition of Done
- [ ] Fake browser chrome is removed from shared layout surfaces.
- [x] Canonical docs reflect the new frame-first shell rule.
- [x] Focused frontend validation evidence is attached.

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
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/planning/layout-dashboard-public-home-canonical-master-audit.md docs/ux/design-memory.md docs/ux/canonical-web-screen-reference-set.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/tasks/PRJ-782-remove-window-chrome-and-audit-layout-frame-drift.md`
- Manual checks:
  - deployed public-home screenshot reviewed before implementation
  - local post-change screenshot reviewed after chrome removal
  - 2026-05-03 closure sync reviewed `web/src/App.tsx`,
    `web/src/index.css`, `docs/ux/design-memory.md`,
    `docs/ux/flagship-baseline-transfer.md`, and
    `.codex/context/TASK_BOARD.md`
  - confirmed current shell source uses `aion-public-shell`,
    `aion-shell-window`, and `aion-shell-frame-canonical` without a
    `WindowChrome` component
  - 2026-05-03 follow-up found that later public-home work reintroduced
    browser-like chrome under `aion-public-browser-chrome`, so the component
    removal is true but the broader no-fake-controls rule is not currently
    satisfied
  - confirmed design memory records the frame-first rule:
    no simulated browser controls, title bars, or fake window chrome
  - confirmed later `PRJ-800A`, `PRJ-800B`, `PRJ-868`, and `PRJ-875` carry
    active shell/frame refinement and proof history
  - `git diff --check` passed
- Screenshots/logs:
  - `.codex/artifacts/deploy-public-home-audit-2026-04-29.png`
  - `.codex/artifacts/local-public-home-no-window-chrome-2026-04-29.png`
- High-risk checks:
  - public landing still exposes auth entry and top-level navigation after the layout cleanup

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/27_codex_instructions.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - user explicitly rejected `WindowChrome` in the deployed layout on 2026-04-29
- Follow-up architecture doc updates:
  - not applicable

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aviary-sidebar-layout-canonical-reference-v1.png`
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- Canonical visual target:
  - shared flagship layout frame for public and authenticated shells
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - flagship utility bar
  - canonical authenticated sidebar spine
- New shared pattern introduced: no
- Design-memory entry reused:
  - canonical authenticated sidebar spine
- Design-memory update required: yes
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - preserve the warm premium shell material without fake title-bar ornament
- Canonical asset extraction required: no
- Screenshot comparison pass completed: yes
- Remaining mismatches:
  - public home still needs deeper canonical hero parity
  - dashboard still needs another structural parity pass after the shell cleanup
- State checks: success
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - removal of decorative chrome must not reduce navigation or account access
- Parity evidence:
  - deployed public landing screenshot showed fake browser chrome as a major
    mismatch and directly motivated this slice

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - revert the layout slice if shell framing loses clarity or hierarchy

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
- This slice intentionally removes the rejected shell ornament before more
  dashboard-local polishing.

## 2026-05-03 Decision Blocker Sync

- This is a historical shell-frame correction slice, but it cannot be closed
  as `DONE` while current public-home code contains browser-like shell
  ornament under `aion-public-browser-chrome`.
- Current runtime shell code does not expose the rejected `WindowChrome`
  component or `aion-window-chrome*` styling, but later public-home work
  reintroduced browser controls under a different class family.
- `docs/ux/design-memory.md` is the durable source of truth for the
  frame-first rule: shells may be premium and inset, but must not simulate
  browser controls or fake window chrome.
- Later `PRJ-800A`, `PRJ-800B`, `PRJ-868`, and `PRJ-875` carry the active
  frame, sidebar, and route-sweep proof trail.
- Decision required:
  - either keep the later browser-window reference as the canonical landing
    direction and update `PRJ-782` plus design memory, or remove
    `aion-public-browser-chrome` from public home and preserve the
    frame-first/no-browser-controls rule.

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
  - public and authenticated shell branches still render inside the shared
    premium frame without route-contract changes

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
  - removed the rejected fake browser chrome from both shared shell branches and
    updated canonical docs so future layout work targets a frame-first shell
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `docs/planning/layout-dashboard-public-home-canonical-master-audit.md`
  - `docs/ux/design-memory.md`
  - `docs/ux/canonical-web-screen-reference-set.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/tasks/PRJ-782-remove-window-chrome-and-audit-layout-frame-drift.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/planning/layout-dashboard-public-home-canonical-master-audit.md docs/ux/design-memory.md docs/ux/canonical-web-screen-reference-set.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/tasks/PRJ-782-remove-window-chrome-and-audit-layout-frame-drift.md`
  - local screenshot review via `.codex/artifacts/local-public-home-no-window-chrome-2026-04-29.png`
- What is incomplete:
  - public landing still needs another parity pass for hero density and lower storytelling rhythm
  - dashboard still needs a new structural convergence slice on the cleaned shell
- Next steps:
  - tune public-home hero proportions and lower-story density on the chrome-free frame
  - then run the next dashboard structural pass on the same shared layout
- Decisions made:
  - fake browser-window chrome is no longer considered canonical for Aviary
  - the flagship shell should remain inset and premium without title-bar ornament

## Closure Result Report

- Goal:
  - identify why `PRJ-782` cannot be closed without a product/design decision
- Scope:
  - task status, task evidence, and context sync only
- Implementation Plan:
  - verify current shell source and durable UX decision docs
  - identify later proof owners
  - mark the historical task blocked if later source contradicts the decision
  - update project context and board state
- Acceptance Criteria:
  - no stale `IN_PROGRESS` state remains for `PRJ-782`
  - the `WindowChrome` versus public browser-chrome mismatch is explicit
  - no runtime, route, auth, or backend behavior changes are introduced
- Definition of Done:
  - original validation evidence is preserved
  - current source review is recorded
  - later `PRJ-800A`, `PRJ-800B`, `PRJ-868`, and `PRJ-875` ownership is recorded
  - context files are updated
  - `git diff --check` passes
- Next:
  - obtain a decision on whether public home should keep the later
    browser-window frame or return to the frame-first/no-browser-controls rule
