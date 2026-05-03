# Task

## Header
- ID: PRJ-828
- Title: Authenticated sidebar decomponentize support stack
- Task Type: design
- Current Stage: release
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-827
- Priority: P1

## Context
The sidebar has already received two exactness slices. The next remaining
drift is structural polish inside the lower stack: the cards still rely on
screen-local utility classes that keep the rail feeling more componentized than
the canonical sidebar.

## Goal
Remove redundant support-stack utility framing and let the sidebar lower cards
be controlled primarily by shared sidebar CSS, so the rail can read as one
canonical layout surface.

## Success Signal
- User or operator problem:
  - the lower sidebar stack still feels slightly too assembled from generic
    panels instead of reading as one canonical rail family
- Expected product or reliability outcome:
  - cleaner support-stack anatomy and easier final pixel-close tuning
- How success will be observed:
  - the lower cards rely less on ad hoc utility rounding/padding and more on
    sidebar-specific rules
- Post-launch learning needed: no

## Deliverable For This Stage
A bounded sidebar-only cleanup slice removing redundant utility framing from
the lower support stack and tightening final card rhythm.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Remove redundant support-stack rounding/padding utility classes from JSX.
2. Move final card geometry and spacing control into sidebar-specific CSS.
3. Tighten the lower-stack visual family to read more monolithically.
4. Run focused validation and sync context.

## Acceptance Criteria
- lower support cards no longer depend on redundant utility rounding/padding
- sidebar-specific CSS fully controls their visible geometry
- the lower stack reads calmer and less assembled
- focused validation passes

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] JSX support-stack utility framing is reduced.
- [x] Sidebar CSS owns the lower-card geometry.
- [x] Focused validation evidence is attached.

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
  - reviewed the lower sidebar stack after the previous support-closure pass
    and targeted only redundant utility framing plus card-family cohesion
- Screenshots/logs:
  - deploy-side sidebar proof still pending
- High-risk checks:
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-828-authenticated-sidebar-decomponentize-support-stack.md`

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/sidebar-layout-canonical-convergence-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference: `docs/ux/assets/aviary-sidebar-layout-canonical-reference-v1.png`
- Canonical visual target: authenticated desktop sidebar support stack
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: authenticated sidebar support stack
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
- Accessibility checks: not in this bounded slice
- Parity evidence:

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: no
- Rollback note: revert sidebar support-stack cleanup slice
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
This slice stays strictly inside the authenticated desktop sidebar support
stack.

## Closure Sync - 2026-05-03

- Current release status:
  - DONE as a historical authenticated-sidebar support-stack CSS ownership
    slice.
- Current source truth:
  - `web/src/App.tsx` keeps the support-stack structure on sidebar-specific
    class hooks.
  - `web/src/index.css` owns the support-card border, shadow, background,
    spacing, and geometry through `.aion-sidebar-*` rules.
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
- Existing workaround or pain: lower sidebar stack still carries generic panel
  utility feel
- Smallest useful slice: support-stack decomponentization
- Success metric or signal: calmer canonical lower stack
- Feature flag, staged rollout, or disable path: no
- Post-launch feedback or metric check: deploy-side visual compare

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: not applicable
- Critical user journey: authenticated shell opening
- SLI: visual parity only
- SLO: not applicable
- Error budget posture: not applicable
- Health/readiness check: `npm run build`
- Logs, dashboard, or alert route: not applicable
- Smoke command or manual smoke: desktop sidebar visual read
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
  - removed redundant utility rounding/padding from the lower support stack and
    moved final card geometry ownership into sidebar-specific CSS
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/tasks/PRJ-828-authenticated-sidebar-decomponentize-support-stack.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-828-authenticated-sidebar-decomponentize-support-stack.md`
- What is incomplete:
  - deploy-side proof for the sidebar rail is still needed before moving to the
    next surface group
- Next steps:
  - compare the deployed authenticated sidebar
  - if it clears the parity gate, move from sidebar to dashboard slices
- Decisions made:
  - kept the slice strictly inside the sidebar support stack and did not reopen
    any route-local UI
