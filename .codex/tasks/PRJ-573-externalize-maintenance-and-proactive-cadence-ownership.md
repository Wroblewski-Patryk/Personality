# Task

## Header
- ID: PRJ-573
- Title: Externalize maintenance and proactive cadence ownership
- Status: IN_PROGRESS
- Owner: Ops/Release
- Depends on: PRJ-572
- Priority: P0

## Context
Production `/health.scheduler.external_owner_policy` still reports
`selected_execution_mode=in_process`, which keeps maintenance and proactive
cadence ownership inside the app process even though the repo already exposes
canonical external entrypoints and cutover-proof posture for both cadence
families.

## Goal
Switch the repository-driven Coolify production baseline to
`SCHEDULER_EXECUTION_MODE=externalized`, add dedicated external cadence
services that invoke the canonical maintenance and proactive entrypoints, and
verify that production `/health.scheduler.external_owner_policy` reports the
externalized baseline without regressing Telegram foreground handling.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Coolify production compose defaults `SCHEDULER_EXECUTION_MODE` to
      `externalized`.
- [ ] repository-driven Coolify production includes dedicated cadence services
      that run the canonical `run_maintenance_tick_once.py` and
      `run_proactive_tick_once.py` entrypoints.
- [ ] production `/health.scheduler.external_owner_policy` reports
      `selected_execution_mode=externalized`.
- [ ] production reflection supervision no longer reports
      `external_scheduler_owner_not_selected`.
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
  - update deployment/runbook truth for external cadence ownership baseline

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
This slice intentionally externalizes cadence ownership only. Broader doc sync
for post-v1 production hardening remains in `PRJ-574`.
