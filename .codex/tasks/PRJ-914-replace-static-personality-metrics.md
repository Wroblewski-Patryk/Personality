# Task

## Header
- ID: PRJ-914
- Title: Replace Remaining Static Personality Metrics
- Task Type: implementation
- Current Stage: verification
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-913
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 914
- Operation Mode: BUILDER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
The web-v1 route smoke is green, but the Personality route still had
presentation values that implied live runtime truth without being backed by
`/app/personality/overview`.

## Goal
Remove misleading static Personality metrics and replace them with values
derived from the existing authenticated overview contract.

## Scope
- `web/src/App.tsx`
- `.codex/tasks/PRJ-914-replace-static-personality-metrics.md`
- `docs/planning/v1-replace-static-personality-metrics.md`
- `docs/planning/v1-release-audit-and-execution-plan.md`
- `docs/planning/v1-core-acceptance-bundle.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Success Signal
- User or operator problem: the Personality screen should not show fake
  precision such as static clarity percentages or fixed intuition strength.
- Expected product or reliability outcome: visible Personality metrics are
  either derived from backend overview data or clearly presented as empty
  runtime state.
- How success will be observed: web build and focused Personality smoke pass
  on desktop and mobile.
- Post-launch learning needed: no

## Deliverable For This Stage
A narrow frontend update and verification evidence proving the Personality
route no longer exposes the removed static claims.

## Constraints
- reuse the existing `/app/personality/overview` contract
- do not introduce new API endpoints
- do not invent new persisted state or mock data
- do not broaden the task into dashboard or chat honesty work
- do not commit generated screenshots, local databases, or temporary scripts

## Implementation Plan
1. Read the current Personality route data bindings.
2. Identify static values that imply live runtime metrics.
3. Derive replacement values from `planning_state`, `learned_knowledge`,
   `identity_state`, and `role_skill_state`.
4. Build the web app.
5. Run a focused desktop/mobile smoke for `/personality` against a local real
   backend.
6. Record evidence and update source-of-truth docs.

## Acceptance Criteria
- Personality clarity no longer shows a fixed percentage.
- Personality energy/load/focus values are derived from active goals, tasks,
  blocked tasks, or pending proposals.
- Personality intuition is derived from overview knowledge signals instead of
  a fixed qualitative label.
- Skill count no longer falls back to a fake static number.
- Desktop and mobile focused smoke pass without overflow or raw technical
  leakage.

## Definition of Done
- [x] Static `87%`, `Strong`, and fallback `18` Personality claims are removed.
- [x] Replacement values are derived from overview data already available to
  the route.
- [x] `npm run build` passed.
- [x] Focused `/personality` desktop/mobile smoke passed.
- [x] Context and planning docs were updated.
- [x] `git diff --check` passed.

## Stage Exit Criteria
- [x] The output matches the declared `Current Stage`.
- [x] Work from later stages was not mixed in without explicit approval.
- [x] Risks and assumptions for this stage are stated clearly.

## Forbidden
- new systems without approval
- duplicated overview-fetching logic
- temporary bypasses, hacks, or workaround-only paths
- fake product metrics or mock-only truth
- implicit stage skipping

## Validation Evidence
- Tests:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - bundled Node + Playwright focused Personality metrics smoke
  - result: passed:
    - `checks=2`
    - `failures=0`
    - `unexpectedConsoleIssueCount=0`
    - `benignConsoleIssueCount=2`
    - `screenshots=2`
  - `git diff --check`
  - result: passed
- Manual checks:
  - local backend `/health` returned `200`
  - smoke used a local registered user and real `/app/*` endpoints through
    Vite proxy
  - removed static claims were not present in the rendered Personality route
- Screenshots/logs:
  - `.codex/artifacts/prj914-personality-metrics/personality-metrics-smoke-results.json`
  - `.codex/artifacts/prj914-personality-metrics/personality-desktop.png`
  - `.codex/artifacts/prj914-personality-metrics/personality-mobile.png`
- High-risk checks:
  - production was not mutated
  - temporary local backend was stopped
  - generated `.codex/tmp` and screenshot artifacts remain uncommitted
- Coverage ledger updated: not applicable
- Coverage rows closed or changed: none

## Architecture Evidence
- Architecture source reviewed:
  - `docs/planning/v1-release-audit-and-execution-plan.md`
  - `docs/ux/screen-quality-checklist.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: not applicable
- Follow-up architecture doc updates: none

## UX/UI Evidence
- Design source type: approved_snapshot_and_product_honesty_lane
- Design source reference: existing canonical Personality route implementation
  plus `PRJ-914` release plan
- Canonical visual target: current Personality route with honest runtime data
- Fidelity target: product_honesty_without_visual_relayout
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: existing Personality callouts and signal rows
- New shared pattern introduced: no
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: no asset change
- Screenshot comparison pass completed: focused screenshot proof captured
- Remaining mismatches: dashboard and broader empty/error state honesty remain
  in PRJ-915/PRJ-916
- State checks: empty and success covered through local empty account posture
- Feedback locality checked: yes
- Raw technical errors hidden from end users: yes
- Responsive checks: desktop, mobile
- Input-mode checks: pointer through route load; keyboard not expanded in this
  slice
- Accessibility checks: labels remained text-readable; no full a11y audit in
  this slice
- Parity evidence: local screenshots listed above

## Deployment / Ops Evidence
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: no
- Rollback note: revert the `web/src/App.tsx` Personality metric binding
  changes
- Observability or alerting impact: none
- Staged rollout or feature flag: not applicable

## Review Checklist
- [x] Process self-audit completed before implementation.
- [x] Autonomous loop evidence covers all seven steps.
- [x] Exactly one priority task was completed in this iteration.
- [x] Operation mode was selected according to iteration rotation.
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

## Result Report

- Task summary: removed misleading static Personality route metrics and
  grounded the visible values in existing overview data.
- Files changed:
  - `web/src/App.tsx`
  - `.codex/tasks/PRJ-914-replace-static-personality-metrics.md`
  - `docs/planning/v1-replace-static-personality-metrics.md`
  - `docs/planning/v1-release-audit-and-execution-plan.md`
  - `docs/planning/v1-core-acceptance-bundle.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- Tests run:
  - `Push-Location .\web; npm run build; Pop-Location`
  - bundled Node + Playwright focused Personality metrics smoke
  - `git diff --check`
- Deployment impact: frontend-only display binding change; requires normal
  web redeploy after push.
- Next tiny task: `PRJ-915` Backend-Backed Dashboard Summary Surface.
