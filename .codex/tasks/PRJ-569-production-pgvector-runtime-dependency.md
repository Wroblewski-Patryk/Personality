# Task

## Header
- ID: PRJ-569
- Title: Block broken PostgreSQL vector startup when pgvector runtime dependency is missing
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-568
- Priority: P0

## Context
Production Telegram ingress reached the service, but `/event` returned `500`
and `/health.conversation_channels.telegram.last_ingress.reason` reported
`runtime_exception:ProgrammingError`. The current runtime uses PostgreSQL-backed
semantic retrieval during foreground turn processing, while `pgvector` was only
an optional Python dependency. That allowed the service to boot into a state
where `/health` worked but foreground event processing could still fail.

## Goal
Make PostgreSQL semantic-vector runtime dependencies explicit and startup
blocking so production cannot silently boot into a broken event-processing
state.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `pgvector` is part of the normal runtime dependency set used for deploys.
- [x] App startup blocks before database initialization when PostgreSQL vectors
  are enabled but the Python `pgvector` binding is unavailable.
- [x] Focused tests prove the startup block and repo truth is updated.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py`
- Manual checks: Production `/health.conversation_channels.telegram.last_ingress.reason`
  showed `runtime_exception:ProgrammingError` before the fix.
- Screenshots/logs: n/a
- High-risk checks: Startup now blocks before database init for broken PostgreSQL
  vector runtime wiring.

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: env/config and ops notes for pgvector runtime dependency

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
This is a production hardening fix for deploy/runtime packaging parity, not a
behavior change to the foreground pipeline.
