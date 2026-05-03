# Task

## Header
- ID: PRJ-824
- Title: Authenticated Shell Utility Bar Calm Pass
- Task Type: design
- Current Stage: release
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-823
- Priority: P1

## Context
The latest deploy-side home proof indicates that the public landing is now
close enough to stop broad polishing and return to the next closure group in
the canonical 100-slice map. The next dependent surface is the authenticated
shell frame.

## Goal
Calm the authenticated shell utility bar and route-canvas opening so flagship
routes read less like a reusable app shell and more like premium surfaces
hosted by one quiet frame.

## Success Signal
- User or operator problem:
  - authenticated routes still start under a utility bar that feels too
    operational and too visually heavy
- Expected product or reliability outcome:
  - shell chrome competes less with the route surface
- How success will be observed:
  - the utility bar feels lighter and the route surface gains more authority
- Post-launch learning needed: no

## Deliverable For This Stage
A bounded CSS-only authenticated-shell refinement pass plus context updates.

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
1. Reduce utility-bar chrome weight, padding, and cardiness.
2. Tighten search, signal, and action-pill rhythm so the route surface regains
   priority.
3. Slightly tighten the canvas opening around the utility band.
4. Run focused validation and sync context.

## Acceptance Criteria
- utility bar is visibly calmer
- route canvas reads more dominant relative to shell chrome
- no route-local structure is changed in this slice
- focused validation passes

## Definition of Done
- [x] utility-bar styles are refined
- [x] context is synced
- [x] focused validation evidence is attached

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
  - reviewed the authenticated utility-bar anatomy against the current shell
    exactness goal after confirming fresh deploy-side `home` proof
- Screenshots/logs:
  - `home` deploy-side evidence reused for closure decision:
    - `.codex/artifacts/prj823-prod-home-root-proof.png`
    - `.codex/artifacts/prj823-prod-home-proof.png`
- High-risk checks:
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-824-authenticated-shell-utility-bar-calm-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`

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
- Existing shared pattern reused: flagship utility bar and shell frame
- New shared pattern introduced: no
- Design-memory entry reused: yes
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: unchanged
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches: live proof still needed
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
- Rollback note: revert the bounded shell CSS slice
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
This slice intentionally starts the authenticated shell group and does not yet
touch sidebar exactness or route-local dashboard/chat/personality composition.

## Closure Sync - 2026-05-03

- Current release status:
  - DONE as a historical authenticated-shell utility-bar calm slice.
- Current source truth:
  - `web/src/App.tsx` keeps `ShellUtilityBar` mounted inside the authenticated
    shell toolbar.
  - `web/src/index.css` keeps the route-shared `.aion-utility-*` CSS for the
    calmer context, search, action, and account-control posture.
  - `docs/ux/design-memory.md` records the flagship utility bar as the shared
    authenticated route pattern.
- Superseding proof owners:
  - `PRJ-868` canonical layout foundation.
  - `PRJ-875` canonical UI final route sweep.
  - `docs/ux/flagship-baseline-transfer.md`.
- Browser/mockup note:
  - the shared authenticated shell should remain premium and composed without
    simulated browser controls, title bars, or fake window chrome.
- Closure evidence:
  - reviewed this task history, current authenticated shell source, design
    memory, flagship baseline transfer, and later project/board proof.
  - no runtime files were changed by this closure sync.

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
- Existing workaround or pain: shell chrome still reads too operational
- Smallest useful slice: CSS-only utility-bar calm pass
- Success metric or signal: route surface gains more visual authority
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
  - opened the authenticated-shell group with a bounded utility-bar calm pass
    after confirming that `home` is now close enough to stop broad polish
- Files changed:
  - `web/src/index.css`
  - `.codex/tasks/PRJ-824-authenticated-shell-utility-bar-calm-pass.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-824-authenticated-shell-utility-bar-calm-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- What is incomplete:
  - deploy-side proof of the calmer authenticated shell is still needed
- Next steps:
  - compare the deployed authenticated shell
  - continue the next bounded shell or sidebar slice depending on the remaining drift
- Decisions made:
  - treated `home` as sufficiently close to the parity gate based on fresh
    deploy-side proof and moved to the next dependent surface group
