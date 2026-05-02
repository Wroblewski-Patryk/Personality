# V1 Organizer Provider Activation Smoke

Last updated: 2026-05-03

## Status

`PRJ-918` is BLOCKED.

Production provider credentials are still missing, so live organizer provider
smoke was not run.

## Production Health Evidence

Checked on 2026-05-03 through `GET https://aviary.luckysparrow.ch/health`.

- `/health.connectors.organizer_tool_stack.readiness_state`:
  `provider_credentials_missing`
- `/health.connectors.organizer_tool_stack.provider_ready_operation_count`:
  `0`
- `/health.connectors.organizer_tool_stack.provider_total_operation_count`:
  `5`
- `/health.connectors.organizer_tool_stack.daily_use_state`:
  `daily_use_workflows_blocked_by_provider_activation`
- `/health.connectors.organizer_tool_stack.daily_use_ready_workflow_count`:
  `0`
- `/health.connectors.organizer_tool_stack.daily_use_total_workflow_count`:
  `3`

Missing or required settings before this smoke can run:

- ClickUp:
  - `CLICKUP_API_TOKEN`
  - `CLICKUP_LIST_ID`
- Google Calendar:
  - `GOOGLE_CALENDAR_ACCESS_TOKEN`
  - `GOOGLE_CALENDAR_CALENDAR_ID`
  - `GOOGLE_CALENDAR_TIMEZONE`
- Google Drive:
  - `GOOGLE_DRIVE_ACCESS_TOKEN`
  - `GOOGLE_DRIVE_FOLDER_ID`

## Unblock Criteria

1. Configure the settings through
   `docs/operations/organizer-provider-activation-runbook.md`.
2. Redeploy production.
3. Confirm `/health.connectors.organizer_tool_stack.provider_ready_operation_count=5`.
4. Confirm `/health.connectors.organizer_tool_stack.daily_use_ready_workflow_count=3`.
5. Enable user opt-in for the target smoke account.
6. Run the live provider smoke.

## Validation

- `git diff --check`
  - passed

No provider secret values were added to the repository.
