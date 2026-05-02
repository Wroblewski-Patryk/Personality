# Task

## Header
- ID: PRJ-916
- Title: Web Empty And Error State Audit
- Task Type: verification
- Current Stage: verification
- Status: DONE
- Owner: QA/Test
- Depends on: PRJ-915
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 916
- Operation Mode: BUILDER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
The web product-honesty lane removed the most visible static metrics from
Personality and Dashboard. The next gate was a route-state audit to confirm the
first-party shell remains nonblank, responsive, and free of raw technical
leakage in empty/success and backend-error postures.

## Goal
Verify first-party route state behavior after the web product-honesty changes.

## Scope
- `.codex/tasks/PRJ-916-web-empty-and-error-state-audit.md`
- `docs/planning/v1-web-empty-and-error-state-audit.md`
- `docs/planning/v1-release-audit-and-execution-plan.md`
- `docs/planning/v1-core-acceptance-bundle.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Success Signal
- User or operator problem: the web app should not look production-ready while
  primary routes are blank, overflowing, or leaking stack traces during empty
  account or backend-error states.
- Expected product or reliability outcome: current first-party route states are
  audited with local evidence and any found blocker is explicit.
- How success will be observed: web build, authenticated route smoke, and
  backend-down smoke pass.
- Post-launch learning needed: no

## Deliverable For This Stage
Verification evidence and release-plan updates. No runtime change was required.

## Constraints
- do not mutate production data
- do not introduce fake state just to satisfy the audit
- do not commit generated screenshots or temporary smoke scripts
- keep production route evidence separate until a deploy-parity smoke runs

## Implementation Plan
1. Run the web build.
2. Start a local backend with a temporary SQLite database.
3. Run the authenticated route smoke across primary first-party routes on
   desktop and mobile.
4. Stop the backend.
5. Run a backend-down smoke against `/dashboard`.
6. Record evidence and update source-of-truth docs.

## Acceptance Criteria
- `/login` renders for unauthenticated state.
- Authenticated first-party routes render nonblank in empty/success posture.
- Desktop and mobile route checks have no failures.
- Backend-down posture does not show raw stack traces, SQLAlchemy/asyncpg
  errors, or page-level horizontal overflow.
- No unexpected console errors remain.

## Definition of Done
- [x] `npm run build` passed.
- [x] Authenticated route smoke passed with 24 route/viewport checks.
- [x] Backend-down smoke passed for `/dashboard` mobile posture.
- [x] Context and planning docs were updated.
- [x] `git diff --check` passed.

## Validation Evidence
- Tests:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - bundled Node + Playwright authenticated route smoke
  - result: passed:
    - `routeChecks=24`
    - `failures=0`
    - `unexpectedConsoleIssueCount=0`
    - `benignConsoleIssueCount=2`
    - `screenshots=8`
  - bundled Node + Playwright backend-down dashboard smoke
  - result: passed:
    - `checks=1`
    - `failures=0`
    - `unexpectedConsoleIssueCount=0`
    - `screenshots=1`
  - `git diff --check`
  - result: passed
- Manual checks:
  - local backend `/health` returned `200` during the route smoke
  - temporary local backend was stopped before the backend-down smoke
- Screenshots/logs:
  - `.codex/artifacts/prj913-web-v1-route-smoke/route-smoke-results.json`
  - `.codex/artifacts/prj916-web-route-state-audit/backend-down-smoke-results.json`
  - `.codex/artifacts/prj916-web-route-state-audit/backend-down-dashboard-mobile.png`
- High-risk checks:
  - production was not mutated
  - generated `.codex/tmp` and screenshot artifacts remain uncommitted

## Result Report

- Task summary: verified first-party web route empty/success and backend-error
  postures after the product-honesty updates; no runtime fix was required.
- Files changed:
  - `.codex/tasks/PRJ-916-web-empty-and-error-state-audit.md`
  - `docs/planning/v1-web-empty-and-error-state-audit.md`
  - `docs/planning/v1-release-audit-and-execution-plan.md`
  - `docs/planning/v1-core-acceptance-bundle.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- Tests run:
  - `Push-Location .\web; npm run build; Pop-Location`
  - bundled Node + Playwright authenticated route smoke
  - bundled Node + Playwright backend-down dashboard smoke
  - `git diff --check`
- Deployment impact: none; documentation/evidence update only.
- Next tiny task: `PRJ-917` Organizer Provider Credential Activation Runbook.
