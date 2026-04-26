# Task

## Header
- ID: PRJ-737
- Title: Dashboard-First Utility Bar And Shared Shell Framing
- Task Type: design
- Current Stage: implementation
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-736
- Priority: P1

## Context
The canonical dashboard reference shows a stronger flagship authenticated shell
than the current app. The route content has improved, but the top utility
chrome and shell framing still lag behind the dashboard-quality target.

## Goal
Implement a richer shared authenticated shell posture that brings dashboard
quality into the existing route system without introducing a new route.

## Deliverable For This Stage
- shared utility top bar and stronger flagship shell framing in `web/src/`
- source-of-truth sync for the updated dashboard-first shell posture

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] Shared authenticated shell includes a premium utility top bar.
- [x] Route framing feels closer to the canonical dashboard posture.
- [x] The change preserves current route topology and shared shell reuse.

## Stage Exit Criteria
- [x] The output matches the declared `Current Stage`.
- [x] Work from later stages was not mixed in without explicit approval.
- [x] Risks and assumptions for this stage are stated clearly.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval
- implicit stage skipping

## Validation Evidence
- Tests:
  - `Push-Location .\web; npm run build; Pop-Location`
- Manual checks:
  - compared the updated shared shell posture against the canonical dashboard
    and chat references
- Screenshots/logs:
  - local screenshot parity remains queued to `PRJ-741`
- High-risk checks:
  - preserved existing route ownership and route list

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - not applicable
- Follow-up architecture doc updates:
  - none required

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - authenticated shell
  - embodied cognition motif
- New shared pattern introduced: no
- Design-memory entry reused:
  - `docs/ux/design-memory.md`
- Design-memory update required: no
- State checks: success
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - no new build-visible regressions
- Parity evidence:
  - shell utility chrome and flagship framing moved closer to the canonical
    dashboard posture

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - none
- Rollback note:
  - revert shell UI changes in `web/src/`

## Review Checklist (mandatory)
- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice intentionally upgrades shell quality without inventing a separate
dashboard route.
