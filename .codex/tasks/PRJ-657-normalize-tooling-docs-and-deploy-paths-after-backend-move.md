# Task

## Header
- ID: PRJ-657
- Title: Normalize tooling, docs, and deploy paths after the `backend/` move
- Status: DONE
- Owner: Ops/Release
- Depends on: PRJ-656
- Priority: P1

## Context
After the runtime moved into `backend/`, root Docker, compose, helper scripts,
and operator docs still needed path normalization so post-push deploys and
developer workflows would keep using the same backend truth.

## Goal
Make the repository root behave as a stable launcher and deployment shell for
the moved backend.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Root Docker and compose files resolve the moved backend.
- [x] Helper scripts and hooks resolve the shared root `.venv` and Alembic config.
- [x] Local-development and testing docs reflect the new invocation paths.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_coolify_compose.py tests/test_deployment_trigger_scripts.py; Pop-Location`
- Manual checks: `docker compose config`
- Screenshots/logs:
- High-risk checks: root deployment flow still builds the backend package from `backend/`

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/13_repository_structure.md`, `docs/governance/repository-structure-policy.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: `PRJ-655`
- Follow-up architecture doc updates: reflected in root README, backend README, engineering docs, and task/context truth

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
This task covered the operational side of the topology migration only.
