# Task

## Header
- ID: PRJ-661
- Title: Implement the backend auth/session baseline for first-party clients
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-660
- Priority: P1

## Context
With the contract frozen, backend needed durable auth user and session storage
plus actual login/logout/register endpoints.

## Goal
Add backend-owned auth tables, session handling, password verification, and
first-party auth endpoints.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Durable auth user and auth session tables exist in models and Alembic.
- [x] Backend exposes register/login/logout endpoints for first-party clients.
- [x] Session cookies are backend-owned and validated server-side.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "app_"; Pop-Location`
- Manual checks: confirmed cookie issuance and session-backed `GET /app/me`
- Screenshots/logs:
- High-risk checks: passwords are stored as PBKDF2 hashes and session tokens are stored as SHA-256 hashes

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/v2-product-entry-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: approved backend-owned auth direction
- Follow-up architecture doc updates: reflected in overview and backend README

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
This baseline is deliberately session-cookie first so `web/` and later
`mobile/` can share one backend-owned identity boundary.
