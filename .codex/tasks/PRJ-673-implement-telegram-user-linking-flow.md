# Task

## Header
- ID: PRJ-673
- Title: Implement Telegram user linking for backend auth identities
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-669, PRJ-672
- Priority: P1

## Context
The product already has Telegram runtime delivery and browser auth, but there
is no first-party user-linking flow that binds an authenticated browser user to
their Telegram identity. The requested tools UI should reveal Telegram as a
channel that can be enabled and linked, not as a place to paste bot secrets.

## Goal
Add a backend-owned Telegram linking flow between app auth identities and
Telegram channel identities so the tools screen can guide users through setup.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- keep bot credentials in environment configuration
- ensure linking is explicit, bounded, and user-owned

## Definition of Done
- [x] The backend exposes a bounded app-facing Telegram linking flow.
- [x] The flow provides a truthful link state for the current authenticated
  user.
- [x] The implementation does not require browser-side secret entry.
- [x] The tools overview reflects Telegram provider readiness, user enablement,
  and link state separately.
- [x] Focused backend tests cover creation, confirmation, and readback of link
  state.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "telegram_link or tools_overview or tools_preferences"; Pop-Location`
  - `Push-Location backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py; Pop-Location`
  - `Push-Location web; npm run build; Pop-Location`
- Manual checks:
  - Telegram tools card now shows code generation and confirmation guidance only when user enablement is on and backend still reports `link_state != linked`
- Screenshots/logs:
- High-risk checks: linking cannot attach the wrong Telegram identity to the
  wrong authenticated user

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: docs/architecture/16_agent_contracts.md; docs/architecture/26_env_and_config.md
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: channel-linking contract docs and ops notes

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Preferred UX posture:
- user enables Telegram in the tools UI
- backend issues a bounded linking instruction or token
- user confirms from Telegram
- backend records the channel linkage
