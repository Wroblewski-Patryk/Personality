# Task

## Header
- ID: PRJ-672
- Title: Add user-owned tool and channel enablement preferences
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-669, PRJ-670
- Priority: P1

## Context
Some parts of the tools model should be user-owned choices rather than global
runtime truth. Existing settings already store a few user preferences through
backend-owned profile and conclusion mechanisms, so tool enablement should
reuse that ownership path where possible.

## Goal
Allow backend-owned user preferences for selected tools and channels without
introducing browser-managed provider credentials or a second preference system.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- reuse existing preference storage where feasible
- keep user enablement separate from provider readiness and execution policy

## Definition of Done
- [ ] Allowed tool and channel toggles are persisted through backend-owned user
  preference mechanisms.
- [ ] The tools overview response includes current user enablement state.
- [ ] Unsupported or integral capabilities remain non-toggleable in the API.
- [ ] Focused backend tests cover persistence and readback of enablement state.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location backend; ..\.venv\Scripts\python -m pytest -q tests\test_api_routes.py; Pop-Location`; `Push-Location web; npm run build; Pop-Location`
- Manual checks: `web` tools screen now updates supported toggle state through `PATCH /app/tools/preferences`
- Screenshots/logs:
- High-risk checks: verify toggles do not bypass confirmation, opt-in, or
  provider credential boundaries

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: docs/architecture/16_agent_contracts.md; docs/architecture/26_env_and_config.md
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: settings and app-facing contract docs

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
Likely first candidates:
- telegram_enabled
- preferred_communication_channels
- selected tool families when the backend says user toggles are allowed

Completed on 2026-04-25:
- persisted booleans for `telegram_enabled`, `clickup_enabled`,
  `google_calendar_enabled`, and `google_drive_enabled`
- wired `PATCH /app/tools/preferences`
- updated `GET /app/tools/overview` and the `web` tools route to reflect
  requested versus effective enabled state
