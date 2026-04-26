# Task

## Header
- ID: PRJ-736
- Title: Chat Transcript, Quick Actions, And Composer Convergence
- Task Type: design
- Current Stage: implementation
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-735
- Priority: P1

## Context
After `PRJ-735`, the main remaining `chat` drift was no longer the high-level
layout. It was the reading rhythm of the transcript, the density of the top
controls, and the integration quality of quick actions with the composer.

The canonical `chat` target still reads calmer, more editorial, and less
modular than the local route.

## Goal
Refine transcript surfaces, top controls, and the bottom action zone so the
main `chat` experience feels closer to the canonical premium conversation
reference.

## Deliverable For This Stage
- `chat` top controls reduced into lighter stacked pills
- transcript cards restyled to feel more conversational and less inspector-like
- quick actions and composer integrated into one calmer bottom action region
- context truth updated with the new comparison outcome and next remaining drift

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] Top controls read lighter and calmer than in the previous pass.
- [x] Transcript metadata and details no longer dominate message cards.
- [x] Quick actions and composer feel more like one shared premium tray.

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
  - reviewed the transcript, top controls, and bottom action region against
    `docs/ux/assets/aion-chat-canonical-reference-v2.png`
  - confirmed the route now reads more like a conversation surface and less
    like a composed dashboard module
- Screenshots/logs:
  - no new authenticated screenshot capture in this slice
  - screenshot parity remains part of `PRJ-740` and `PRJ-741`
- High-risk checks:
  - kept the route backend-contract-driven and avoided introducing new view-local state systems

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
  - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - chat background artwork
  - embodied cognition motif
  - timeline-backed metadata
- New shared pattern introduced: no
- Design-memory entry reused:
  - `docs/ux/design-memory.md`
- Design-memory update required: no
- State checks: success
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - no new build-visible regressions
  - full interaction and contrast review remains queued in `PRJ-740`
- Parity evidence:
  - this slice improves:
    - calmer transcript metadata
    - lighter top control posture
    - tighter action-chip and composer relationship
  - remaining drift:
    - the route still needs a more magical but restrained final premium polish
    - mobile and tablet still need explicit parity proof
    - post-deploy screenshot comparison still remains required before parity claims

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - none
- Rollback note:
  - revert `web/src/App.tsx` and `web/src/index.css`

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
The next best slice is no longer transcript mechanics. It is route-family
polish and parity proof across breakpoints, with `personality` brought onto the
same refined shell standard.
