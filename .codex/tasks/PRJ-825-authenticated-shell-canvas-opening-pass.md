# Task

## Header
- ID: PRJ-825
- Title: Authenticated Shell Canvas Opening Pass
- Task Type: design
- Current Stage: implementation
- Status: IN_PROGRESS
- Owner: Frontend Builder
- Depends on: PRJ-824
- Priority: P1

## Context
The first authenticated-shell slice reduced utility-bar heaviness. The next
remaining shell-level drift is the opening relationship between rail, toolbar,
background atmosphere, and route canvas.

## Goal
Tighten the authenticated shell canvas opening so the active route surface
starts more authoritatively and the shell backdrop recedes further.

## Success Signal
- User or operator problem:
  - the shell still feels a little too padded and atmospheric before the route
    surface takes over
- Expected product or reliability outcome:
  - route content feels more immediate and flagship-like
- How success will be observed:
  - less visual dead air between shell frame parts and calmer backdrop presence
- Post-launch learning needed: no

## Deliverable For This Stage
A bounded CSS-only shell pass targeting outer padding, frame gap, shell
backdrop, and toolbar-to-canvas spacing.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Scope
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Tighten the outer shell body padding and frame gap.
2. Reduce decorative shell-backdrop intensity.
3. Reduce toolbar spacing before the route canvas.
4. Run focused validation and sync context.

## Acceptance Criteria
- the shell opening is visibly tighter and calmer
- backdrop atmosphere is less competitive with route content
- no route-local layout is changed in this slice
- focused validation passes

## Definition of Done
- [ ] shell opening styles are refined
- [ ] context is synced
- [ ] focused validation evidence is attached

## Stage Exit Criteria
- [ ] The output matches the declared `Current Stage`.
- [ ] Work from later stages was not mixed in without explicit approval.
- [ ] Risks and assumptions for this stage are stated clearly.

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
  - reviewed the shell-opening anatomy after the previous utility-bar calm
    slice and targeted only frame-level spacing and backdrop drift
- Screenshots/logs:
  - deploy-side shell proof still pending
- High-risk checks:
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-825-authenticated-shell-canvas-opening-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/ux/canonical-visual-implementation-workflow.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference: `docs/planning/canonical-100-slice-closure-map.md`
- Canonical visual target: authenticated shell frame
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: authenticated shell frame
- New shared pattern introduced: no
- Design-memory entry reused: yes
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: unchanged
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches: deploy-side proof still needed
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
- Rollback note: revert bounded shell CSS slice
- Observability or alerting impact: none
- Staged rollout or feature flag: no

## Review Checklist (mandatory)
- [ ] Current stage is declared and respected.
- [ ] Deliverable for the current stage is complete.
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice stays on shared authenticated frame logic only, before sidebar
exactness begins.

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

## Product / Discovery Evidence
- Problem validated: yes
- User or operator affected: authenticated users across flagship routes
- Existing workaround or pain: shell opening still feels slightly over-padded
- Smallest useful slice: CSS-only frame-opening pass
- Success metric or signal: route canvas reads more immediate and premium
- Feature flag, staged rollout, or disable path: no
- Post-launch feedback or metric check: visual deploy check

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: not applicable
- Critical user journey: authenticated route framing
- SLI: visual parity only
- SLO: not applicable
- Error budget posture: not applicable
- Health/readiness check: not applicable
- Logs, dashboard, or alert route: not applicable
- Smoke command or manual smoke: `Push-Location .\web; npm run build; Pop-Location`
- Rollback or disable path: revert bounded slice

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: not applicable
- Endpoint and client contract match: not applicable
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: not applicable
- Regression check performed: focused build and diff validation

## AI Testing Evidence (required for AI features)

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: not applicable
- Data classification: none
- Trust boundaries: unchanged
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
  - refined the authenticated shell opening by reducing outer padding, frame
    gap, backdrop intensity, and toolbar spacing before the route canvas
- Files changed:
  - `web/src/index.css`
  - `.codex/tasks/PRJ-825-authenticated-shell-canvas-opening-pass.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-825-authenticated-shell-canvas-opening-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- What is incomplete:
  - deploy-side screenshot proof of the calmer shell is still required
- Next steps:
  - compare the deployed authenticated shell
  - if the frame is calm enough, start the first sidebar exactness slice
- Decisions made:
  - kept the slice CSS-only and frame-scoped to avoid opening sidebar and
    route-local polish in parallel
