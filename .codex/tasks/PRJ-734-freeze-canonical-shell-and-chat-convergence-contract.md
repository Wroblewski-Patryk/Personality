# Task

## Header
- ID: PRJ-734
- Title: Freeze Canonical Shell And Chat Convergence Contract
- Task Type: design
- Current Stage: planning
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-728, PRJ-731, PRJ-733
- Priority: P1

## Context
The repository now has an approved canonical web screen-set and several local
implementation passes for the authenticated shell and `chat`. Production and
local proof show clear progress, but the current implementation still drifts
from the canonical `chat` target in shell weight, panel hierarchy, support
column behavior, and cross-route shell consistency.

The next work should not be a loose polish loop. It needs one explicit
convergence contract so the following implementation slices move toward the
same accepted shell and route posture.

## Goal
Freeze the gap analysis and execution order required to converge the
authenticated shell, `chat`, and later `personality` toward the approved
canonical route targets.

## Deliverable For This Stage
- one execution-ready convergence plan in `docs/planning/`
- one task seed for the next implementation lane
- one source-of-truth update recording that the current gap is compositional
  fidelity, not basic visual direction

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] The current shell and `chat` drift is documented against the canonical references.
- [x] A detailed execution queue exists for parent shell, `chat`, and `personality` convergence.
- [x] Context truth records the new convergence lane and its acceptance posture.

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
  - not applicable; planning and documentation scope only
- Manual checks:
  - reviewed:
    - `docs/ux/aion-visual-motif-system.md`
    - `docs/ux/canonical-web-screen-reference-set.md`
    - `docs/ux/design-memory.md`
    - `docs/ux/visual-direction-brief.md`
    - `docs/ux/screen-quality-checklist.md`
  - compared the current local `chat` proof with the canonical `chat` reference
- Screenshots/logs:
  - canonical target:
    - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
  - current local proof:
    - `.codex/artifacts/chat-premium-polish-pass-desktop.png`
- High-risk checks:
  - ensured the task remained planning-only and did not quietly implement UI changes

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
  - none required; this lane is within approved web-shell and UX boundaries

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - embodied cognition motif
  - timeline-backed metadata
  - chat background artwork
- New shared pattern introduced: no
- Design-memory entry reused:
  - `docs/ux/design-memory.md`
- Design-memory update required: no
- State checks: loading | empty | error | success
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: touch | pointer | keyboard
- Accessibility checks:
  - deferred to the proof slice planned in `PRJ-740`
- Parity evidence:
  - drift recorded from the canonical `chat` reference into
    `docs/planning/canonical-authenticated-shell-and-chat-convergence-plan.md`

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: none
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - none
- Rollback note:
  - revert planning and context updates only

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
The main finding is that the product no longer lacks a visual direction. It
now lacks stricter compositional convergence between the parent shell and the
canonical route targets, especially `chat`.
