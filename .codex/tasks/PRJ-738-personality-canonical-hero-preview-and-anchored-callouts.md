# Task

## Header
- ID: PRJ-738
- Title: Personality Canonical Hero Preview And Anchored Callouts
- Task Type: design
- Current Stage: implementation
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-737
- Priority: P1

## Context
The `personality` route still drifts furthest from its canonical reference.
The current hero is too generic, too system-like, and not rich enough in
symbolic embodied mapping.

## Goal
Implement a richer personality preview hero that uses a route-specific figure
asset and anchored callouts closer to the canonical personality reference.

## Deliverable For This Stage
- one route-specific personality figure asset stored in docs and web public assets
- one richer `personality` hero composition in `web/src/`
- source-of-truth sync recording the new preview posture

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] `personality` uses a route-specific embodied figure asset instead of a generic placeholder.
- [x] The preview includes anchored conceptual callouts closer to the canonical map.
- [x] The route now reads more like a flagship personality showcase than a payload summary.

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
  - compared the updated hero posture against the canonical personality reference
- Screenshots/logs:
  - asset:
    - `docs/ux/assets/aion-personality-figure-reference-v1.png`
    - `web/public/aion-personality-figure-reference-v1.png`
- High-risk checks:
  - kept the route within existing frontend/backend ownership boundaries

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
  - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - embodied cognition motif
  - route-specific illustration support
- New shared pattern introduced: no
- Design-memory entry reused:
  - `docs/ux/design-memory.md`
- Design-memory update required: yes
- State checks: success
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - no new build-visible regressions
- Parity evidence:
  - hero fidelity and figure richness moved materially closer to the canonical
    personality route

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - none
- Rollback note:
  - revert route asset and `web/src/` hero changes

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
This slice focuses on top preview fidelity, not final responsive proof.
