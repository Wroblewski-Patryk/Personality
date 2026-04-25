# Task

## Header
- ID: PRJ-671
- Title: Build the web tools screen from backend truth
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-670
- Priority: P1

## Context
The first web shell currently exposes chat, settings, and personality
inspection. Users now need a dedicated tools surface that explains what the
personality can use and what still needs provider setup or user linking.

## Goal
Add a dedicated web tools screen that renders grouped tools and channels
directly from the backend tools overview contract.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- keep the client thin and backend-truth driven
- do not imply configurability where backend does not support mutation yet

## Definition of Done
- [ ] The web app includes a dedicated tools route and navigation entry.
- [ ] The screen groups tools into clear sections such as Communication, Task
  Management, Knowledge and Web, and Internal.
- [ ] Integral capabilities render as always-on or read-only with truthful UI.
- [ ] Provider-blocked or link-required tools render clear status and guidance.
- [ ] Web tests or focused rendering checks cover the major states.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location web; npm run build; Pop-Location`
- Manual checks: `web` now exposes a dedicated `Tools` route backed by `/app/tools/overview`
- Screenshots/logs:
- High-risk checks: verify the UI never drifts from backend state labels

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: docs/architecture/16_agent_contracts.md; docs/planning/v2-product-entry-plan.md
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: web product shell docs if route map changes

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
The initial screen should favor truthful status language over dense forms.

Completed on 2026-04-25:
- added a dedicated `Tools` route to the web shell
- grouped cards now render communication, task management, knowledge/web, and
  organizer truth from backend payloads
- UI stays read-only for states that are not yet persisted or linked
