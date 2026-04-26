# Task

## Header
- ID: PRJ-743
- Title: Dashboard Chat Personality Canonical Polish And Proof
- Task Type: design
- Current Stage: implementation
- Status: IN_PROGRESS
- Owner: Frontend Builder
- Depends on: PRJ-742
- Priority: P0

## Context
The authenticated shell now has a real `/dashboard` route and the flagship
overview is materially closer to the canonical dashboard reference. The main
remaining gap is no longer route topology, but visual parity and premium
material polish across `dashboard`, `chat`, and `personality`.

## Goal
Close the next explicit parity gap between the implemented route family and the
canonical route assets through material polish, responsive proof, and deploy
comparison.

## Deliverable For This Stage
- one execution-ready parity task after `PRJ-742`
- explicit drift categories for `dashboard`, `chat`, and `personality`
- validation and evidence expectations for the next implementation slice

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] The next parity slice is concretely bounded.
- [x] Remaining drift to the canonical dashboard, chat, and personality assets
      is described in implementation terms.
- [x] Validation expectations are explicit for local and deployed proof.

## Stage Exit Criteria
- [ ] The output matches the declared `Current Stage`.
- [ ] Work from later stages was not mixed in without explicit approval.
- [ ] Risks and assumptions for this stage are stated clearly.

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
  - reviewed canonical dashboard, chat, and personality references
  - confirmed public production runtime build revision parity through:
    - `GET /health`
    - root HTML build meta tag
- Screenshots/logs:
  - authenticated deployed screenshot proof still pending because a safe
    browser-auth path was not available in this turn
- High-risk checks:
  - no new backend contract added
  - no parallel dashboard system introduced

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
  - none expected

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
  - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - flagship overview stage
  - flagship utility bar
  - integrated composer tray
  - embodied cognition motif
- New shared pattern introduced: no
- Design-memory entry reused:
  - `docs/ux/design-memory.md`
- Design-memory update required: possible
- State checks: loading | empty | success
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: pointer | keyboard | touch
- Accessibility checks:
  - hierarchy readability
  - image should support the route, not carry the route alone
- Parity evidence:
  - local screenshot proof
  - deployed screenshot proof

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - none
- Rollback note:
  - revert `web/src/` shell and route polish changes

## Review Checklist (mandatory)
- [ ] Current stage is declared and respected.
- [ ] Deliverable for the current stage is complete.
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This task is now active. The first execution pass added:

- a dashboard-specific convergence loop plan:
  - `docs/planning/dashboard-canonical-convergence-loop-plan.md`
- another dashboard polish slice:
  - stronger rail support surfaces
  - recent-activity tier inside guidance
  - a more integrated flow-band layout

Remaining work is still mainly visual parity quality, not architecture or
backend contract shape.
