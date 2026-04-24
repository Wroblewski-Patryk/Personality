# Task

## Header
- ID: PRJ-634
- Title: Wire runtime build revision to Coolify predefined source commit
- Status: DONE
- Owner: Ops/Release
- Depends on: PRJ-616
- Priority: P0

## Context
Repo-driven deploy automation is repaired and production now auto-deploys again,
but release smoke still fails because live `/health.deployment.runtime_build_revision`
remains `unknown`.

## Goal
Align the Coolify compose/runtime wiring with the real predefined commit variable
contract so live production exposes a machine-visible commit SHA.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Coolify runtime wiring uses the correct predefined source-commit posture.
- [x] Targeted regression coverage pins the same compose/runtime assumption.
- [x] Live production exposes a non-`unknown` `runtime_build_revision` and release smoke passes.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted Coolify compose and deployment-smoke regression coverage
- Manual checks: live production `/health.deployment` plus release smoke
- Screenshots/logs: production deploy parity evidence after push
- High-risk checks: do not weaken release smoke to accept missing build revision

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/26_env_and_config.md`, `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: ops/runbook and planning/context truth if the predefined-variable contract changes

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
Official Coolify docs state that runtime applications should expose predefined
commit SHA through a regular environment variable value such as
`MY_VARIABLE=$SOURCE_COMMIT`, while build-time inclusion is a separate opt-in.

Implementation note:
- `docker-compose.coolify.yml` now references the application-owned
  `APP_BUILD_REVISION` variable instead of referencing `SOURCE_COMMIT`
  directly.
- The canonical Coolify app now stores `APP_BUILD_REVISION=$SOURCE_COMMIT` as
  a runtime-only variable, and the previously shadowing `SOURCE_COMMIT=unknown`
  variable has been removed from the application environment.

## Evidence
- Repo-side wiring now uses `${APP_BUILD_REVISION:-unknown}` in
  `docker-compose.coolify.yml` for both runtime env and build args, so the
  Coolify application owns the actual source-commit mapping.
- Canonical Coolify app `jr1oehwlzl8tcn3h8gh2vvih` now stores
  `APP_BUILD_REVISION=$SOURCE_COMMIT` as a runtime-only environment variable,
  and the user-created `SOURCE_COMMIT` variables were removed to avoid
  shadowing the predefined Coolify variable.
- Production `GET /health` now reports
  `deployment.runtime_build_revision=6585681e57bf2e93cdc7b12bd8286aacb950709d`,
  `runtime_build_revision_state=runtime_build_revision_declared`, and
  `runtime_provenance_state=primary_runtime_provenance_declared`.
- `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`
  now passes against the live production URL.
