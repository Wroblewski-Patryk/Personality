# Task

## Header
- ID: PRJ-692
- Title: Normalize Coolify deploy startup around one repo-owned Alembic migration owner
- Status: DONE
- Owner: Ops/Release
- Depends on: PRJ-691
- Priority: P1

## Context
The web UX/UI lane introduced a new Alembic revision for `ui_language`, which
surfaced a deployment gap in the repository-driven Coolify baseline. The
current `docker-compose.coolify.yml` starts long-lived services directly after
database health, but it does not define a repo-owned migration step before the
app and externalized cadence workers boot.

## Goal
Make repository-driven Coolify deploys apply pending Alembic migrations
automatically before the app and cadence services start, while keeping one
explicit migration owner instead of duplicating `upgrade head` logic across
multiple runtime services.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `docker-compose.coolify.yml` defines one migration owner that runs
  `python -m alembic -c /app/backend/alembic.ini upgrade head` after database
  health.
- [x] the Coolify `app`, `maintenance_cadence`, and `proactive_cadence`
  services wait for migration completion before startup.
- [x] deployment and ops docs describe the same repo-driven auto-migration
  baseline and the operator verification path.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `docker compose -f docker-compose.coolify.yml config`
- Manual checks:
  - verified the Coolify compose baseline now includes a one-shot `migrate`
    service plus `service_completed_successfully` dependencies for the
    long-lived runtime services
- Screenshots/logs:
  - local `docker compose -f docker-compose.coolify.yml config` resolved the
    final compose graph without schema errors
- High-risk checks:
  - migration ownership stays single-path; `app` startup itself still expects
    migrations rather than re-running `alembic upgrade head`

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/26_env_and_config.md`
  - `docs/architecture/28_local_windows_and_coolify_deploy.md`
  - `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: no
- Approval reference if architecture changed:
  - none
- Follow-up architecture doc updates:
  - Coolify deploy guidance and ops runbook now record the auto-migration
    owner and verification path

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This task keeps migration-first startup repo-driven for Coolify without
assuming a paid GitHub automation layer or a separate out-of-band deploy hook.
