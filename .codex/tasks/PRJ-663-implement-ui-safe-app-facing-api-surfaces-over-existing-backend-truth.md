# Task

## Header
- ID: PRJ-663
- Title: Implement UI-safe app-facing API surfaces over existing backend truth
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-662
- Priority: P1

## Context
With auth and client-boundary contracts frozen, backend needed real app-facing
routes for first-party clients.

## Goal
Implement session-backed app routes for user snapshot, settings, chat, and
personality overview using existing backend truth.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `GET /app/me` and `PATCH /app/me/settings` resolve current user and settings.
- [x] `GET /app/chat/history` and `POST /app/chat/message` reuse existing backend memory/runtime surfaces.
- [x] `GET /app/personality/overview` reuses the bounded learned-state snapshot under session auth.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "app_"; Pop-Location`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py; Pop-Location`
- Manual checks: verified app chat requests run under the authenticated runtime user id
- Screenshots/logs:
- High-risk checks: app routes wrap existing runtime and learned-state logic instead of copying it

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/v2-product-entry-plan.md`, `docs/overview.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: approved UI-safe app-facing API direction
- Follow-up architecture doc updates: reflected in overview, backend README, v2 plan progress, and task/context truth

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
This slice establishes the backend contract that the next `web/` shell can
consume directly.
