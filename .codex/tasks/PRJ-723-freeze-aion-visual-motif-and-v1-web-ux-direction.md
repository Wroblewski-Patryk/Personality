# Task

## Header
- ID: PRJ-723
- Title: Freeze AION Visual Motif And V1 Web UX Direction
- Task Type: design
- Current Stage: planning
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-722
- Priority: P1

## Context
The repository has an accepted functional web shell and an approved warm,
calm, product-facing direction, but it still lacks one explicit hero motif that
can unify `chat`, `personality`, `tools`, `settings`, and later `mobile`
surfaces under the same memorable visual language.

The user approved a new concept direction: a humane synthetic figure mapped to
the AION cognitive pipeline through symbolic pins, timeline layers, and compact
metadata callouts. That direction must now be frozen as repository truth before
future UI implementation slices use it inconsistently.

## Goal
Freeze one approved UX/UI reference package for the next visual lane:

- save the concept image in the repository as the current approved snapshot
- record the motif, layout rules, color posture, and section-by-section usage
- seed the next implementation lane for web-first rollout without changing
  architecture or backend-owned product contracts

## Deliverable For This Stage
- one design-source document in `docs/ux/` that references the approved image
- one explicit implementation roadmap for applying the motif across `web/`
- source-of-truth updates in task board, project state, and design memory

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] The approved snapshot is saved inside the repository.
- [x] The motif and UX direction are documented as reusable project truth.
- [x] The next web implementation lane is broken into concrete follow-up tasks.

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
- Tests: `git diff --check` on changed planning and UX files
- Manual checks:
  - confirmed the image asset is stored under `docs/ux/assets/`
  - cross-checked the motif against `docs/ux/visual-direction-brief.md`
  - confirmed the deliverable stays in planning and documentation scope
- Screenshots/logs:
  - approved snapshot: `docs/ux/assets/aion-visual-motif-reference.png`
- High-risk checks:
  - no backend or frontend contract changes introduced during planning

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: none

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-visual-motif-reference.png`
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - conversation shell
  - settings groups
  - capability cards
- New shared pattern introduced: yes
- Design-memory entry reused:
  - `docs/ux/design-memory.md`
- Design-memory update required: yes
- State checks: loading | empty | error | success planned per route motif
- Responsive checks: desktop | tablet | mobile planned
- Input-mode checks: touch | pointer | keyboard planned
- Accessibility checks:
  - text contrast
  - decorative-vs-informational illustration separation
  - reduced-motion parity
- Parity evidence:
  - same motif now documented for web-first rollout and later mobile transfer

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: none
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: no
- Rollback note: revert the design-source docs and asset if direction changes

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
- This task intentionally freezes direction and execution order only.
- Actual screen implementation should start in the next explicit web lane.
