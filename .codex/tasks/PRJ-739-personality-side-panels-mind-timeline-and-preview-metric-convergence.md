# Task

## Header
- ID: PRJ-739
- Title: Personality Side Panels, Mind Timeline, And Preview Metric Convergence
- Task Type: design
- Current Stage: implementation
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-738
- Priority: P1

## Context
The canonical personality reference relies not only on the figure hero, but
also on the surrounding explanatory structure: side panels, the mind-layer
timeline, and calmer signal summaries.

## Goal
Implement the supporting preview structure around the richer personality hero
so the route reads more like the canonical embodied overview.

## Deliverable For This Stage
- side insight panels
- mind-layer timeline treatment
- calmer preview metrics aligned with the figure hero
- source-of-truth sync describing the new personality-preview baseline

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] `personality` has stronger side insight panels.
- [x] `personality` includes a clearer mind-layer timeline treatment.
- [x] Preview metrics now support the route hero instead of competing with it.

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
  - compared the updated preview structure against the canonical personality
    reference
- Screenshots/logs:
  - no fresh screenshot artifact in this slice
- High-risk checks:
  - preserved the lower overview section rather than deleting useful backend-owned detail

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
  - timeline-backed metadata
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
  - side-structure and timeline fidelity moved closer to the canonical
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
  - revert personality preview structure changes

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
Further work now shifts from structure into cross-route polish and proof.
