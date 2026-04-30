# Task

## Header
- ID: PRJ-816
- Title: Close the chat route toward canonical parity
- Task Type: design
- Current Stage: implementation
- Status: IN_PROGRESS
- Owner: Frontend Builder
- Depends on: PRJ-800L, PRJ-796
- Priority: P1

## Context
`home` is closed above the current parity gate and the user explicitly
redirected the active flagship surface to `chat`. The current chat route is
functional and already uses the shared Aviary persona, yet it still drifts
from `docs/ux/assets/aion-chat-canonical-reference-v4.png`. The strongest gap
is structural: the route still reads as `thread + stacked support column`
instead of a composed `thread + embodied stage + cognitive rail`.

## Goal
Bring the web `chat` route above the current `97%` parity gate against the
approved canonical chat reference, starting with the largest structural gaps.

## Success Signal
- User or operator problem:
  - chat still feels visibly unfinished relative to the canonical target
- Expected product or reliability outcome:
  - chat reads as one premium conversation workspace with transcript-first
    hierarchy, a route-correct embodied presence, and a calmer cognitive rail
- How success will be observed:
  - desktop screenshot comparison against the canonical chat reference shows
    only minor residual ornament drift
- Post-launch learning needed: no

## Deliverable For This Stage
One implementation slice that:
- reshapes the desktop chat workspace toward `thread + portrait + cognitive rail`
- upgrades the composer into a more canonical premium tray
- improves transcript presence and support hierarchy without opening other
  flagship routes

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/tasks/PRJ-816-chat-canonical-parity-closure-lane.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Audit current chat drift against `docs/ux/assets/aion-chat-canonical-reference-v4.png`
   and the latest available route proofs.
2. Restructure chat into a clearer desktop composition with one transcript
   column, one embodied portrait stage, and one cognitive context rail.
3. Tighten the transcript metadata and assistant avatar treatment so the
   message thread feels calmer and more premium.
4. Upgrade the composer into a more canonical tray with integrated mode tabs
   and steadier support controls.
5. Validate with frontend build and focused diff checks, then sync task and
   project truth.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- chat uses a clearer canonical structure than the current stacked support
  column
- the portrait panel reads as a route-specific conversation stage, not a reused
  personality panel
- the right rail shows clearer canonical hierarchy for intent, memory, actions,
  and proactive continuity
- the composer reads as one premium instrument, not a loose stack of controls
- build and focused diff checks pass

## Definition of Done
- [ ] Chat layout is materially closer to the canonical composition.
- [ ] The strongest remaining drift is smaller than the pre-slice structural gap.
- [ ] Validation evidence is attached.

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
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-816-chat-canonical-parity-closure-lane.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- Manual checks:
  - compared the canonical chat reference with the latest stored desktop proofs
    and targeted the largest structural drift first
- Screenshots/logs:
  - current audit uses:
    - `docs/ux/assets/aion-chat-canonical-reference-v4.png`
    - `.codex/artifacts/production-audit-2026-04-26/chat-desktop.png`
    - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-desktop.png`
- High-risk checks:
  - preserve the current backend-owned transcript contract and send flow

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/27_codex_instructions.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - not applicable

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-chat-canonical-reference-v4.png`
- Canonical visual target:
  - chat route canonical parity
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - conversation shell
  - integrated composer tray
  - shared canonical persona figure
- New shared pattern introduced: no
- Design-memory entry reused:
  - chat background artwork
  - route-specific persona adaptation
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - reuse the existing route-specific chat background art and the shared
    canonical persona crop
- Canonical asset extraction required: no
- Screenshot comparison pass completed: yes
- Remaining mismatches:
  - live IAB proof is blocked in this session by the current Node runtime floor
- State checks: loading | empty | success
- Feedback locality checked: yes
- Raw technical errors hidden from end users: yes
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - preserved the existing transcript, textarea, and button semantics while
    restructuring the layout
- Parity evidence:
  - current audit source images listed above

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - revert the route-only chat slice if transcript or composer readability regresses
- Observability or alerting impact: none
- Staged rollout or feature flag: none

## Review Checklist (mandatory)
- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
- The current session cannot run fresh in-app browser screenshots because the
  available Node runtime is below the browser plugin minimum. This slice uses
  the canonical asset plus the freshest available stored route proofs instead.

## Production-Grade Required Contract

Every task must include these mandatory sections before it can move to `READY` or `IN_PROGRESS`:

- `Goal`
- `Scope` with exact files, modules, routes, APIs, schemas, docs, or runtime surfaces
- `Implementation Plan` with step-by-step execution and validation
- `Acceptance Criteria` with testable conditions
- `Definition of Done` using `DEFINITION_OF_DONE.md`
- `Result Report`

Runtime tasks must be delivered as a vertical slice: UI -> logic -> API -> DB -> validation -> error handling -> test. Partial implementations, mock-only paths, placeholders, fake data, and temporary fixes are forbidden.

## Integration Evidence

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: yes
- Endpoint and client contract match: yes
- DB schema and migrations verified: not applicable
- Loading state verified: pending
- Error state verified: pending
- Refresh/restart behavior verified: pending
- Regression check performed:
  - the backend-owned transcript contract, optimistic send flow, and existing
    Markdown rendering remain intact after the route restructure

## AI Testing Evidence (required for AI features)

- `AI_TESTING_PROTOCOL.md` reviewed: not applicable
- Memory consistency scenarios:
- Multi-step context scenarios:
- Adversarial or role-break scenarios:
- Prompt injection checks:
- Data leakage and unauthorized access checks:
- Result:

## Result Report

- Task summary:
  - opened a dedicated chat-only parity lane and closed the first major
    structural gap by reshaping the route into thread column, embodied stage,
    and cognitive rail
  - completed one additional chat-only refinement pass that:
    - tightened transcript density and bubble hierarchy
    - made the embodied stage larger and calmer
    - shortened right-rail copy so the route reads less like an app panel
    - replaced rough text glyphs in the composer with real icon components
    - repaired the chat-specific Polish copy that was still visibly mangled by
      encoding drift
  - completed one more visual-only compression pass that:
    - removed the extra route-description paragraph from the chat topbar
    - tightened the topbar pills and stage spacing
    - gave the embodied panel more authority against the transcript and rail
    - replaced the remaining rail action glyph with a CSS-owned arrow
  - completed one more canonical cleanup pass that:
    - removed the extra `Persona` pill from the chat topbar
    - removed the non-canonical mode-tab row above the composer
    - simplified the composer tray so the thread reads less like a tool panel
      and closer to the approved conversation-first reference
  - completed one more proportion-and-rail pass that:
    - replaced sidebar-style mini-links in the right rail with calmer status
      accents
    - tightened right-rail panel padding and spacing
    - enlarged the embodied persona crop and reduced portrait-note weight so
      the central stage carries more of the route authority
  - completed one more transcript-first rhythm pass that:
    - reduced the quick-action tray from four chips to three
    - removed the extra helper sentence below the composer
    - tightened topbar, transcript, and composer spacing so the thread keeps
      more of the visual attention
  - completed one more surface-polish pass that:
    - replaced the chat headline star with the Aviary logomark treatment
    - reduced topbar control-pill density
    - tightened message-card widths and padding for calmer transcript rhythm
  - completed one more right-rail shortening pass that:
    - reduced related-memory items from three to two
    - reduced suggested actions from three to two
    - shortened the proactive check-in action label
    - tightened memory and action card spacing for a less list-heavy rail
  - completed one more rail consolidation pass that:
    - reduced motivation metrics from four to three
    - folded proactive check-in into the active-goal card instead of keeping a
      separate rail section
    - tightened topbar spacing and message-meta rhythm for a calmer read
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/tasks/PRJ-816-chat-canonical-parity-closure-lane.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - focused `git diff --check`
  - canonical-to-proof audit using the stored reference and latest available
    chat screenshots
- What is incomplete:
  - live screenshot proof for this exact post-slice implementation
  - final deploy-side decision on whether the remaining drift is small enough
    to call the route above the `97%` gate
- Next steps:
  - compare the deployed chat against the canonical reference
  - if needed, spend one last bounded slice only on portrait crop, topbar
    density, and closure polish
- Decisions made:
  - active flagship work is temporarily redirected from `dashboard` to `chat`
    by explicit user instruction
  - keep the existing shared chat background artwork and canonical persona,
    but adapt the route through structure and context hierarchy instead of
    inventing a separate being
