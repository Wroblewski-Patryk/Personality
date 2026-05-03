# Task

## Header
- ID: PRJ-826
- Title: Authenticated sidebar lockup and nav rhythm pass
- Task Type: design
- Current Stage: release
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-824, PRJ-825
- Priority: P1

## Context
The canonical closure map moved the active flagship lane from `home` to the
authenticated shell. The shell frame now has two calming passes, so the next
smallest safe slice is the first exactness pass on the desktop sidebar.

## Goal
Bring the authenticated desktop sidebar closer to the canonical reference by
calming the rail width, brand lockup, nav-row rhythm, and lower closure stack
without reopening route-local interiors.

## Success Signal
- User or operator problem:
  - The sidebar still feels chunkier and more component-heavy than the
    canonical rail.
- Expected product or reliability outcome:
  - The authenticated shell reads more like one premium editorial spine.
- How success will be observed:
  - The desktop rail appears narrower, calmer, and closer to the canonical
    sidebar screenshot.
- Post-launch learning needed: no

## Deliverable For This Stage
A bounded desktop-sidebar implementation slice plus updated repository truth.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Tighten the sidebar rail width and shell gap.
2. Refine sidebar brand lockup scale and subtitle posture.
3. Compress nav-row height, icon scale, and active-pill softness.
4. Tighten the lower support stack rhythm.
5. Remove visible glyph/encoding drift in the utility emblem and sidebar quote.
6. Run focused build and diff validation.

## Acceptance Criteria
- The desktop sidebar is visually narrower and calmer than before.
- Brand lockup and nav rows are closer to the canonical sidebar rhythm.
- No visible mojibake remains in the shell emblem or sidebar quote.
- Only authenticated shell/sidebar surfaces are touched in this slice.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] Sidebar lockup and nav rhythm are refined in code.
- [x] Visible glyph drift is removed from the active desktop shell.
- [x] Build and focused diff validation pass.

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
- Manual checks:
  - reviewed the sidebar lockup, nav rows, and support stack against the
    canonical sidebar rail plan before changing route-local surfaces
- Screenshots/logs:
  - deploy-side sidebar proof still pending
- High-risk checks:
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-826-authenticated-sidebar-lockup-and-nav-rhythm-pass.md`

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/ux/design-memory.md`, `docs/planning/sidebar-layout-canonical-convergence-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference: `docs/ux/assets/aviary-sidebar-layout-canonical-reference-v1.png`
- Canonical visual target: authenticated desktop sidebar
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: authenticated shell + sidebar support stack
- New shared pattern introduced: no
- Design-memory entry reused: sidebar canonical rail contract
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: existing shell assets only
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
- State checks: success
- Feedback locality checked: yes
- Raw technical errors hidden from end users: yes
- Responsive checks: desktop
- Input-mode checks: pointer
- Accessibility checks: visual glyph cleanup only
- Parity evidence:

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: no
- Rollback note: revert shell/sidebar style slice
- Observability or alerting impact: none
- Staged rollout or feature flag: no

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
- [x] Learning journal update was not required; no new recurring pitfall was
  confirmed in this closure sync.

## Notes
This slice intentionally stays inside the authenticated desktop shell and does
not reopen `dashboard`, `chat`, or `personality`.

## Closure Sync - 2026-05-03

- Current release status:
  - DONE as a historical authenticated-sidebar lockup and nav rhythm slice.
- Current source truth:
  - `web/src/App.tsx` keeps `SidebarBrandBlock`, `SidebarGlyph`,
    `ShellNavButton`, `aion-app-rail`, `aion-sidebar-nav`, and the sidebar
    support stack.
  - `web/src/index.css` keeps the narrower rail, brand lockup, nav-row,
    support-card, and quote-signature rules from this slice.
  - `docs/ux/design-memory.md` records the canonical authenticated sidebar
    spine as a shared route pattern.
- Superseding proof owners:
  - `PRJ-868` canonical layout foundation.
  - `PRJ-875` canonical UI final route sweep.
  - `docs/ux/flagship-baseline-transfer.md`.
- Closure evidence:
  - reviewed this task history, current sidebar source, design memory,
    flagship baseline transfer, and later project/board proof.
  - no runtime files were changed by this closure sync.

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

## Product / Discovery Evidence
- Problem validated: yes
- User or operator affected: authenticated desktop users
- Existing workaround or pain: sidebar still reads chunkier than the canonical rail
- Smallest useful slice: lockup + nav rhythm + glyph cleanup
- Success metric or signal: calmer, narrower desktop rail closer to canonical
- Feature flag, staged rollout, or disable path: no
- Post-launch feedback or metric check: no

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: not applicable
- Critical user journey: authenticated shell opening
- SLI: not applicable
- SLO: not applicable
- Error budget posture: not applicable
- Health/readiness check: `npm run build`
- Logs, dashboard, or alert route: not applicable
- Smoke command or manual smoke: desktop shell visual read
- Rollback or disable path: revert slice

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: not applicable
- Endpoint and client contract match: not applicable
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: not applicable
- Regression check performed: focused shell/sidebar diff

## AI Testing Evidence (required for AI features)

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: not applicable
- Data classification: not applicable
- Trust boundaries: not applicable
- Permission or ownership checks: not applicable
- Abuse cases: not applicable
- Secret handling: none
- Security tests or scans: not applicable
- Fail-closed behavior: not applicable
- Residual risk: low

- `AI_TESTING_PROTOCOL.md` reviewed: not applicable
- Memory consistency scenarios:
- Multi-step context scenarios:
- Adversarial or role-break scenarios:
- Prompt injection checks:
- Data leakage and unauthorized access checks:
- Result:

## Result Report

- Task summary:
  - tightened the authenticated sidebar rail width, brand lockup, nav rhythm,
    and lower support stack while removing visible glyph drift from the shell
    emblem and quote closure
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/tasks/PRJ-826-authenticated-sidebar-lockup-and-nav-rhythm-pass.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-826-authenticated-sidebar-lockup-and-nav-rhythm-pass.md`
- What is incomplete:
  - deploy-side screenshot proof for the authenticated shell/sidebar pair
- Next steps:
  - compare deployed sidebar against the canonical sidebar reference
  - if still needed, take one more bounded slice on support-card emblem weight
    and bottom-stack spacing
- Decisions made:
  - kept the slice inside shared authenticated shell/sidebar surfaces only
  - replaced visible broken glyph text with CSS/structural rendering instead of
    more fragile literal characters
