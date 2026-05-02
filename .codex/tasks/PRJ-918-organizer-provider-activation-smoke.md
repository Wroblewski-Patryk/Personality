# Task

## Header
- ID: PRJ-918
- Title: Organizer Provider Activation Smoke
- Task Type: release
- Current Stage: verification
- Status: BLOCKED
- Owner: Ops/Release
- Depends on: PRJ-917
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 918
- Operation Mode: ARCHITECT

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
`PRJ-917` created the organizer provider activation runbook. The live smoke can
only run after the operator configures ClickUp, Google Calendar, and Google
Drive credentials in the active deployment environment.

## Goal
Run a production organizer provider activation smoke after credentials are
configured, or explicitly record the blocker if credentials are still missing.

## Scope
- `.codex/tasks/PRJ-918-organizer-provider-activation-smoke.md`
- `docs/planning/v1-organizer-provider-activation-smoke.md`
- `docs/planning/v1-release-audit-and-execution-plan.md`
- `docs/planning/v1-core-acceptance-bundle.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Success Signal
- User or operator problem: organizer daily-use readiness should not be claimed
  before provider-backed operations are actually configured and smoked.
- Expected product or reliability outcome: the smoke is either passed with real
  provider evidence or blocked with exact missing settings.
- How success will be observed: production `/health` provider activation
  state.
- Post-launch learning needed: no

## Deliverable For This Stage
A blocked smoke record with exact operator preconditions.

## Constraints
- do not add provider secrets to the repo
- do not mutate production settings from this task
- do not run provider smoke while `/health` reports missing credentials
- do not downgrade the blocker into a passing local-only test

## Validation Evidence
- Production health reviewed on 2026-05-03:
  - `connectors.organizer_tool_stack.readiness_state=provider_credentials_missing`
  - `connectors.organizer_tool_stack.provider_ready_operation_count=0`
  - `connectors.organizer_tool_stack.provider_total_operation_count=5`
  - `connectors.organizer_tool_stack.daily_use_state=daily_use_workflows_blocked_by_provider_activation`
  - missing ClickUp settings:
    - `CLICKUP_API_TOKEN`
    - `CLICKUP_LIST_ID`
  - missing Google Calendar settings:
    - `GOOGLE_CALENDAR_ACCESS_TOKEN`
    - `GOOGLE_CALENDAR_CALENDAR_ID`
  - required Google Calendar setting still part of activation:
    - `GOOGLE_CALENDAR_TIMEZONE`
  - missing Google Drive settings:
    - `GOOGLE_DRIVE_ACCESS_TOKEN`
    - `GOOGLE_DRIVE_FOLDER_ID`
- `git diff --check`
  - result: passed

## Result Report

- Task summary: organizer provider activation smoke is blocked by missing
  production provider credentials.
- Files changed:
  - `.codex/tasks/PRJ-918-organizer-provider-activation-smoke.md`
  - `docs/planning/v1-organizer-provider-activation-smoke.md`
  - `docs/planning/v1-release-audit-and-execution-plan.md`
  - `docs/planning/v1-core-acceptance-bundle.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- Tests run:
  - production `/health` organizer snapshot review
  - `git diff --check`
- Deployment impact: none; evidence/blocker update only.
- Next tiny task: `PRJ-920` Minimal External Health Monitor.
