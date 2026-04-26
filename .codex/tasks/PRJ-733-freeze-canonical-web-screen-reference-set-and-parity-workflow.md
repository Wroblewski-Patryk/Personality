# Task

## Header
- ID: PRJ-733
- Title: Freeze Canonical Web Screen Reference Set And Screenshot-Parity Workflow
- Task Type: design
- Current Stage: implementation
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-723, PRJ-728, PRJ-731
- Priority: P1

## Context
The user approved a new canonical visual target for the current web-first AION
experience and asked that future route changes converge toward those images.
The repository already carries motif-level UX truth, but it did not yet store
the newly approved landing, dashboard, personality, and chat targets together
with a route-level screenshot-parity workflow.

## Goal
Freeze the user-approved canonical web screen references inside the repository
and document the required post-deploy screenshot comparison workflow for future
web UX changes.

## Deliverable For This Stage
Repository UX documentation and context truth updated to:
- store the canonical screen assets in `docs/ux/assets/`
- define the approved screen-set and parity workflow in `docs/ux/`
- sync project context so later work treats those references as the web UX
  source of truth

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] Canonical approved screen images are stored in the repository.
- [x] UX docs define the new screen-set and screenshot-parity workflow.
- [x] Project context records the new canonical design-source truth.

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
  - not applicable; docs and asset sync only
- Manual checks:
  - verified the approved source files were copied into `docs/ux/assets/`
  - cross-reviewed `docs/ux/`, `.codex/context/PROJECT_STATE.md`, and
    `.codex/context/TASK_BOARD.md`
- Screenshots/logs:
  - canonical assets:
    - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
    - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
    - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
    - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
- High-risk checks:
  - ensured the update stayed in documentation and source-of-truth scope only

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
  - none required; UX truth lives in `docs/ux/`

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
  - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - `docs/ux/aion-visual-motif-system.md`
  - `docs/ux/design-memory.md`
- New shared pattern introduced: no
- Design-memory entry reused:
  - embodied cognition motif
  - chat background artwork
- Design-memory update required: yes
- State checks: loading | empty | error | success
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: touch | pointer | keyboard
- Accessibility checks:
  - documentation only; future parity captures remain required per route task
- Parity evidence:
  - workflow frozen in `docs/ux/canonical-web-screen-reference-set.md`

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: none
- Env or secret changes:
  - none
- Health-check impact:
  - none
- Smoke steps updated:
  - none
- Rollback note:
  - revert doc and asset additions only

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
Future web-route implementation slices should now treat the canonical screen
set as the visual convergence target and record post-deploy screenshot proof
against those references before claiming parity.
