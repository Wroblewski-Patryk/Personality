# Task

## Header
- ID: PRJ-656
- Title: Move the current Python runtime into `backend/` without behavior drift
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-655
- Priority: P1

## Context
The approved `v2` topology requires the current Python runtime to move from the
repository root into `backend/` while preserving runtime semantics, import
behavior, tests, scripts, and deploy readiness.

## Goal
Relocate the current backend code and its Python-runtime ownership files into
`backend/`, then repair the repository so local development and deploy flows
still point at the same backend truth.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Current backend runtime files live under `backend/`.
- [x] Root-level compose, docs, and helper flows still resolve the moved backend correctly.
- [x] Validation proves there is no behavior drift from the move itself.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_coolify_compose.py tests/test_schema_baseline.py tests/test_deployment_trigger_scripts.py; Pop-Location`
  - `npm run build` in `web/`
- Manual checks:
  - `docker compose config`
  - confirmed root Dockerfile installs the package from `backend/`
  - confirmed helper wrappers resolve the shared root `.venv` and `backend/alembic.ini`
- Screenshots/logs:
- High-risk checks:
  - `tests/test_behavior_validation_script.py` still has pre-existing assertion drift around `incident_evidence_v1_readiness`; it was observed during validation but is unrelated to the repository-topology move itself

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/13_repository_structure.md`, `docs/governance/repository-structure-policy.md`, `docs/planning/v2-product-entry-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: `PRJ-655` approved topology freeze
- Follow-up architecture doc updates: completed for repository topology, local-dev, testing, root README, and backend workspace bootstrap

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
Critical write scope completed:

- runtime, tests, scripts, migrations, and package metadata now live under
  `backend/`
- root Docker and compose wiring resolve the moved backend
- `web/` now has an initial React + TypeScript + Vite + Tailwind + daisyUI
  scaffold
- `mobile/` now has a product-level placeholder without prematurely freezing a
  mobile stack
