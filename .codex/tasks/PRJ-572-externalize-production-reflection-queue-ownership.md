# Task

## Header
- ID: PRJ-572
- Title: Externalize production reflection queue ownership
- Status: IN_PROGRESS
- Owner: Ops/Release
- Depends on: PRJ-571
- Priority: P0

## Context
Live production `/health.reflection.external_driver_policy` still reports
`selected_runtime_mode=in_process`, so the app process continues to own
reflection queue drain even though the repo already has a deferred external
driver contract and canonical drain entrypoint.

## Goal
Switch the production Coolify baseline to `REFLECTION_RUNTIME_MODE=deferred`,
deploy it, and verify that production no longer starts the app-local reflection
worker while Telegram/API foreground turn handling remains healthy.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Coolify production compose defaults `REFLECTION_RUNTIME_MODE` to `deferred`.
- [ ] production `/health.reflection.external_driver_policy.selected_runtime_mode`
  reports `deferred`.
- [ ] Telegram/API foreground turn handling remains healthy after deploy.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
- Manual checks:
- Screenshots/logs:
- High-risk checks:

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - update deployment/runbook truth for current production reflection mode

## Review Checklist (mandatory)
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice intentionally changes only reflection runtime ownership. Scheduler
cadence ownership remains for `PRJ-573`.
