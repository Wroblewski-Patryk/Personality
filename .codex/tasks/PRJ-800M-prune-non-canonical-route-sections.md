# Task

## Header
- ID: PRJ-800M
- Title: Prune non-canonical route sections from flagship views
- Task Type: design
- Current Stage: verification
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-800L, PRJ-800F
- Priority: P1

## Context
The canonical screen set is now stable enough that some remaining drift is no
longer about styling or spacing. It is about extra sections that simply do not
exist in the canonical route compositions.

The current flagship routes still include a few supporting blocks that create
unnecessary modular noise:

- `chat` still ends with a separate feature strip outside the main workspace
- `personality` still includes extra preview navigation, summary chips, and a
  highlights panel that are not part of the canonical personality composition
- `home` needs an explicit re-check to confirm whether any extra whole section
  still remains after the previous landing passes

This slice removes those route-level extras so future parity work can focus on
the sections that genuinely belong to the canonical layouts.

## Goal
Remove non-canonical sections from the flagship routes that still carry them,
confirm whether `home` still has any extra whole section to prune, and leave
`dashboard` structurally unchanged where its remaining drift is compositional
rather than sectional.

## Deliverable For This Stage
A route-pruning implementation pass in `web/src/App.tsx` and `web/src/index.css`
plus synced repo truth describing which sections were removed and why.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/tasks/PRJ-800M-prune-non-canonical-route-sections.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Re-check `home` against the canonical landing and confirm whether any extra whole section still remains.
2. Remove the separate chat feature strip that sits outside the canonical conversation workspace.
3. Remove non-canonical `personality` sections that duplicate overview/support behavior.
4. Keep `dashboard` structurally intact in this slice and document that no clearly extra whole section remained there.
5. Validate build and focused diff checks, then sync repo truth.

## Acceptance Criteria
- `home` is explicitly checked and documented as either pruned or already structurally clean in this slice.
- `chat` no longer renders the separate feature strip below the main workspace.
- `personality` no longer renders the extra preview-nav section, summary-chip row, and extra highlights panel.
- `dashboard` is explicitly checked and left structurally unchanged in this slice.
- Validation passes and task/context notes explain the pruning decisions.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [x] Non-canonical sections were removed from the touched flagship routes where they still existed.
- [x] Remaining route structures still respect the product contract.
- [x] Validation and repo truth match the actual pruning slice.

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
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800M-prune-non-canonical-route-sections.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- Manual checks:
  - compared route section structure against `docs/ux/canonical-web-screen-reference-set.md`
  - verified that the removed sections were absent from the canonical compositions
  - confirmed that the current `home` JSX no longer contains the older proof-stack section that earlier parity notes referred to
- Screenshots/logs:
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - `docs/ux/assets/aion-chat-canonical-reference-v4.png`
  - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
- High-risk checks:
  - preserved route access and core user tasks while removing the extra sections

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/ux/canonical-web-screen-reference-set.md`
  - `docs/planning/layout-sidebar-home-dashboard-canonical-parity-master-ledger.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - `docs/ux/assets/aion-chat-canonical-reference-v4.png`
  - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
- Canonical visual target: flagship route section inventory
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused: yes
- New shared pattern introduced: no
- Design-memory entry reused: `docs/ux/design-memory.md`
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy: reuse existing approved route assets only
- Canonical asset extraction required: no
- Screenshot comparison pass completed: partial
- Remaining mismatches:
  - deploy-side screenshot proof still required after pruning
  - later parity passes are still needed for spacing, hierarchy, and responsive closure
- State checks: success
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: pointer | keyboard | touch
- Accessibility checks: preserved heading order, route access, and form semantics
- Parity evidence:
  - canonical references listed above

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not needed
- Rollback note: restore removed sections if product contract or route access regresses

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
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice is intentionally about section inventory, not final visual polish.
It should make later screenshot-parity work easier by reducing structural noise.

## Production-Grade Required Contract

Every task must include these mandatory sections before it can move to `READY`
or `IN_PROGRESS`:

- `Goal`
- `Scope` with exact files, modules, routes, APIs, schemas, docs, or runtime surfaces
- `Implementation Plan` with step-by-step execution and validation
- `Acceptance Criteria` with testable conditions
- `Definition of Done` using `DEFINITION_OF_DONE.md`
- `Result Report`

Runtime tasks must be delivered as a vertical slice: UI -> logic -> API -> DB
-> validation -> error handling -> test. Partial implementations, mock-only
paths, placeholders, fake data, and temporary fixes are forbidden.

## Integration Evidence

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: yes
- Endpoint and client contract match: yes
- DB schema and migrations verified: not applicable
- Loading state verified: yes
- Error state verified: yes
- Refresh/restart behavior verified: pending
- Regression check performed: build plus focused diff checks

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
  - removed route sections that have no canonical counterpart in the approved flagship screens
  - confirmed that `home` no longer contained the earlier proof-stack section and therefore required verification rather than another structural cut
  - kept `dashboard` structurally intact because its remaining drift is compositional, not about extra sections
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/tasks/PRJ-800M-prune-non-canonical-route-sections.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - focused `git diff --check`
- What is incomplete:
  - deploy-side screenshot proof for the pruned route set
  - later visual parity passes for layout, spacing, and responsive behavior
- Next steps:
  - inspect the deployed flagship routes after pruning
  - continue parity work on the remaining canonical sections only
- Decisions made:
  - removed only sections that had no canonical counterpart instead of doing another broad redesign
  - treated `dashboard` as checked-but-kept for this slice
