# Task

## Header
- ID: PRJ-694
- Title: Add bounded health retry to release smoke for transient deploy-time 503 responses
- Status: DONE
- Owner: Ops/Release
- Depends on: PRJ-693
- Priority: P1

## Context
Live production smoke on 2026-04-25 briefly returned `503 Service Unavailable`
before the same deployment converged and passed on retry. Release smoke already
had strict deploy-parity assertions and optional parity waiting, but it still
treated any transient `/health` transport failure as an immediate hard stop.

## Goal
Keep release smoke strict, but allow a small bounded retry budget for transient
`/health` failures during deploy convergence.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `backend/scripts/run_release_smoke.ps1` retries `/health` with a bounded
  attempt budget and retry delay.
- [x] regression tests cover both transient-success and retry-budget-exhausted
  failure.
- [x] ops docs and context truth record the transient-503 guardrail.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py; Pop-Location`
- Manual checks:
  - `.\backend\scripts\run_release_smoke.ps1 -BaseUrl "https://personality.luckysparrow.ch"`
- Screenshots/logs:
  - live smoke on 2026-04-25 first observed transient `503 Service Unavailable`
    and later passed without code changes beyond bounded retry support
- High-risk checks:
  - release smoke still fails after the retry budget is exhausted
  - deploy parity and health assertions remain unchanged once `/health`
    responds successfully

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/28_local_windows_and_coolify_deploy.md`
  - `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - none
- Follow-up architecture doc updates:
  - ops and deploy docs now mention bounded `/health` retry posture during
    deploy convergence

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
This retry budget is intentionally small and applies only to `/health` fetches.
It smooths over short deploy-time unavailability without turning release smoke
into a long generic polling loop.
