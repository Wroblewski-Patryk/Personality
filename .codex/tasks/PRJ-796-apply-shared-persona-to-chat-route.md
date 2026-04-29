# Task

## Header
- ID: PRJ-796
- Title: Apply the shared canonical persona to the chat route
- Task Type: design
- Current Stage: implementation
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-795
- Priority: P1

## Context
`PRJ-795` froze one shared canonical Aviary persona figure for flagship routes.
The strongest remaining continuity gap is now `chat`: the right-side portrait
panel still leans on older route-specific background treatment instead of
showing the same persona adapted for conversation context.

## Goal
Bring `chat` materially closer to the canonical route language by making the
shared persona visible inside the support column and transcript posture.

## Deliverable For This Stage
One frontend slice that:
- uses the shared canonical persona asset inside the chat portrait panel
- adapts the same being with conversation-specific callouts and calmer support
  copy
- strengthens transcript continuity with a persona-led assistant avatar

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-796-apply-shared-persona-to-chat-route.md`

## Implementation Plan
1. Introduce chat-specific note content derived from current route state such
   as focus, memory cues, language, and linked-channel continuity.
2. Replace the current portrait panel treatment with the shared persona image
   plus route-specific decorative notes.
3. Adapt the assistant avatar so transcript continuity also reflects the same
   embodied identity.
4. Validate with frontend build and focused diff checks.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- the shared canonical persona appears in the chat portrait panel
- the portrait panel reads as conversation-specific rather than generic
- transcript avatar treatment aligns with the shared persona continuity
- build and focused diff checks pass

## Definition of Done
- [x] Chat visually reuses the canonical persona rather than a separate being.
- [x] Route-specific chat adaptation is visible through notes, crop, or support cues.
- [x] Validation evidence is attached.

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
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/tasks/PRJ-796-apply-shared-persona-to-chat-route.md`
- Manual checks:
  - verified the chat route now points to the shared persona asset in both the support portrait and assistant avatar treatment
- Screenshots/logs:
  - frontend production build completed successfully
- High-risk checks:
  - transcript, composer, and support column structure remained intact after the portrait swap

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
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
  - `docs/ux/assets/aviary-persona-figure-canonical-reference-v1.png`
- Canonical visual target:
  - chat route shared-persona continuity
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - shared canonical persona figure
  - integrated composer tray
- New shared pattern introduced: no
- Design-memory entry reused:
  - shared canonical persona figure
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - keep atmospheric art support but let the shared raster persona become the
    route anchor
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
  - post-deploy crop and spacing tuning will still be needed
- State checks: success
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - persona art remains decorative and does not displace transcript or composer
- Parity evidence:
  - to be captured after implementation

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - revert the portrait-panel slice if the support column loses readability

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
- This slice intentionally focuses on the chat portrait column and transcript
  identity cues before broader route parity polish.

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
- Loading state verified: yes
- Error state verified: yes
- Refresh/restart behavior verified: yes
- Regression check performed:
  - transcript, support column, and composer still render on the current chat route

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
  - adapted the chat route to the shared canonical persona through a real
    portrait figure, conversation-specific note cards, and a persona-led
    assistant avatar
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/tasks/PRJ-796-apply-shared-persona-to-chat-route.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - focused `git diff --check`
  - active-reference verification in `web/src/App.tsx` and `web/src/index.css`
- What is incomplete:
  - deploy screenshot tuning for portrait crop and note spacing
  - another parity loop for dashboard and personality after live review
- Next steps:
  - compare the deployed chat route against the canonical chat reference
  - continue with the next cross-route parity pass for dashboard and personality
- Decisions made:
  - the chat support portrait should keep ambient route art, but the shared
    canonical persona is now the main embodied anchor rather than a separate
    route-local image treatment
