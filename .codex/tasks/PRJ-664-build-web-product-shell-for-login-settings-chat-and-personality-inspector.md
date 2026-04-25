# Task

## Header
- ID: PRJ-664
- Title: Build the web product shell for login, settings, chat, and personality inspection
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-663
- Priority: P1

## Context
The repository now has the approved `backend/`, `web/`, and `mobile/`
topology. Backend-owned auth/session and app-facing endpoints already exist,
but `web/` is still only a scaffold. The next smallest useful slice is a real
browser product shell that consumes the backend session, chat, settings, and
personality overview contracts without introducing client-side domain drift.

## Goal
Ship the first functional `web/` shell for first-party use:

- unauthenticated login/register entry
- authenticated chat workspace
- authenticated user settings
- authenticated personality inspector over backend-provided sections

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `web/` can authenticate against backend-owned session endpoints.
- [x] `web/` exposes chat, settings, and personality inspection as real UI surfaces.
- [x] `web/` remains a client over backend truth rather than recreating backend domain logic.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `npm run build`
- Manual checks:
  - verified login/register, settings, chat, and inspector all consume `/app/*` contracts
- Screenshots/logs:
  - production build succeeded after the shell implementation
- High-risk checks:
  - personality view reads backend overview sections instead of debug-only routes

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

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
The first shell may use lightweight in-app routing as long as production
serving and deep links remain compatible with the approved `web/` client
ownership boundary.
