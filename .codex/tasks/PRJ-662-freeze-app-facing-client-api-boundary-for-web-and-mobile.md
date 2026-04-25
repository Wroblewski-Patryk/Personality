# Task

## Header
- ID: PRJ-662
- Title: Freeze the app-facing client API boundary for web and mobile
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-661
- Priority: P1

## Context
`v2` needs client-safe backend surfaces instead of exposing operator-only debug
inspection paths directly to product clients.

## Goal
Freeze one initial app-facing API boundary for user session, settings, chat,
and personality overview.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] First-party app routes are explicitly separated from internal debug routes.
- [x] The client boundary covers `me`, settings, chat, and personality overview.
- [x] Docs describe these as backend-owned app-facing surfaces.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "app_"; Pop-Location`
- Manual checks: verified app routes use auth sessions and existing backend truth
- Screenshots/logs:
- High-risk checks: product clients do not use `/internal/state/inspect` directly

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/v2-product-entry-plan.md`, `docs/overview.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: approved UI-safe app-facing API direction
- Follow-up architecture doc updates: reflected in overview, backend README, and v2 plan progress

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
The app-facing boundary intentionally reuses the runtime and learned-state
truth instead of introducing a parallel client model.
