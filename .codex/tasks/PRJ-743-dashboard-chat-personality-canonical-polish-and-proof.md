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
  - authenticated deployed screenshot proof now exists in:
    - `.codex/artifacts/production-audit-2026-04-26/dashboard-desktop.png`
    - `.codex/artifacts/production-audit-2026-04-26/chat-desktop.png`
    - `.codex/artifacts/production-audit-2026-04-26/personality-desktop.png`
    - `.codex/artifacts/production-audit-2026-04-26/dashboard-mobile.png`
    - `.codex/artifacts/production-audit-2026-04-26/chat-mobile.png`
    - `.codex/artifacts/production-audit-2026-04-26/personality-mobile.png`
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
  - `docs/ux/assets/aion-chat-canonical-reference-v4.png`
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
- a further asset-backed dashboard slice now also exists:
  - scenic intention-card artwork
  - scenic summary-band artwork
  - live wiring of those assets into the dashboard route

Remaining work is still mainly visual parity quality, not architecture or
backend contract shape.

Latest implementation pass in this task:

- shared shell utility chrome now moves closer to the canonical references
  through:
  - continuity
  - language
  - linked-channel signal pills
- dashboard now has a dedicated hero-stage atmosphere asset:
  - `docs/ux/assets/aion-dashboard-hero-atmosphere-reference-v1.png`
  - `web/public/aion-dashboard-hero-atmosphere-reference-v1.png`
- dashboard hero stage now adds:
  - scenic cognition-field depth
  - a lower figure caption
  - stronger perceived connective detail from signal cards toward the figure
- chat now gets a calmer ambient shell overlay instead of relying only on
  panel styling
- personality now gets explicit connective callout lines so the hero reads
  more like one embodied system and less like floating cards

Next smallest remaining parity slice after this pass:

- browser-verified proportion tuning for dashboard hero stage
- cognitive-flow band simplification if it still reads too modular
- post-deploy screenshot comparison for dashboard, chat, and personality

Additional refinement pass now complete:

- the dashboard cognitive-flow row now uses a tighter, less card-heavy visual
  rhythm
- the dashboard current-phase sidecard now reads more like one premium
  orchestration object
- personality side insight panels now use a more editorial surface family
  instead of reading like four equal generic boxes
- chat support surfaces now also use a softer premium material treatment so
  the right column supports the transcript more quietly
- the flagship route proportions are now closer to the canonical references:
  - wider dashboard hero center
  - slightly calmer guidance-column share
  - larger personality hero figure stage
  - slightly more transcript-first chat stage balance
- the shared flagship shell and panel tiering were also tightened:
  - utility bar now feels more inset and premium
  - dashboard guidance, recent, and intention tiers are more distinct
  - personality side panels now read less like equal cards and more like one
    curated editorial stack
- visible route-family branding is also being normalized toward AION so old
  naming does not undercut the premium canonical presentation

Production-audit-backed refinement pass now also complete:

- one logged-in production audit was executed on:
  - `https://aviary.luckysparrow.ch`
- detailed audit findings and the bounded final convergence queue now live in:
  - `docs/planning/flagship-production-audit-and-final-convergence-plan.md`
- the current local implementation now responds to the highest-value audited
  gaps through:
  - removing redundant route-hero banners from `dashboard` and `personality`
  - shortening the dashboard by removing the extra module-entry / route
    highlights row
  - moving dashboard hero chips into the actual flagship stage
  - adding a premium starter transcript for zero-history `chat`
  - moving the `chat` portrait panel higher in the support column
  - removing the long payload-browser section from the flagship
    `personality` route

Latest calming-and-compression pass now also complete:

- `dashboard` now has a simpler scenic closure:
  - the lower closure has been reduced to one premium summary band
  - the scenic half now carries more visual weight than the stats half
- `chat` is now closer to the canonical conversation-first target:
  - transcript metadata is reduced to calmer time-first cues
  - raw payload details no longer crowd the flagship transcript surface
  - the support column no longer ends with the extra `response path` card
  - the send control and headline emblem are now visually normalized through
    route CSS treatment
- `personality` is now shorter and closer to the canonical preview route:
  - the extra `layer map` explainer block below the hero and timeline has been
    removed
  - the flagship route now centers the figure stage, timeline, and right-side
    conscious / subconscious / recent-activity stack
- one environment constraint is now explicit for proof planning:
  - in-app browser automation is currently blocked locally because the
    available `node_repl` runtime reports Node `v22.13.0`, while the browser
    runtime requires `>= v22.22.0`
  - until that is upgraded, live compare loops should continue using manual
    deploy review plus stored screenshot evidence

Latest hero-stage-and-callout pass now also complete:

- `dashboard` now gives the canonical embodied center more authority:
  - signal cards use stronger premium material and longer visual connectors
  - the hero figure stage is larger and carries more internal atmosphere
  - the desktop stage split now gives more room to the central cognition scene
- `chat` now moves closer to the canonical portrait posture:
  - the portrait crop is warmer and less left-heavy
  - the planning overlay now sits lower and reads more like one calm inset
  - the desktop support column now yields slightly more space back to the
    transcript
- `personality` now improves embodied-map readability:
  - the figure stage is taller
  - anchored callouts are brighter and easier to locate
  - connector endpoints are now more legible, so the route reads more like one
    symbolic system instead of floating labels

Latest shell-tiering-and-highlight pass now also complete:

- `dashboard` guidance now reads more like an editorial stack:
  - the first guidance card is visually promoted as the lead recommendation
  - the following cards are calmer and less equal-weight, closer to the
    canonical curated-column feel
- `chat` top controls now feel less app-heavy:
  - control pills are denser, quieter, and better tiered
  - the continuity pill carries the strongest emphasis while linked channels
    no longer dominates the row
- `personality` right-column highlights now have stronger hierarchy:
  - the key signal card becomes the anchor tile in the metric grid
  - the remaining summary cards now read as supporting signals instead of four
    equal blocks
