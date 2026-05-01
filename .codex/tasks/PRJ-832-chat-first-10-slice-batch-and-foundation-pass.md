# Task

## Header
- ID: PRJ-832
- Title: Chat first 10 slice batch and foundation pass
- Task Type: design
- Current Stage: implementation
- Status: IN_PROGRESS
- Owner: Frontend Builder
- Depends on: PRJ-816, PRJ-831
- Priority: P1

## Context
The user explicitly redirected the active flagship closure lane from
`dashboard` to `chat`. A dedicated chat parity lane already exists in
`PRJ-816`, but it has accumulated many bounded refinements without a fresh,
frozen batch map for the current route-only closure work.

## Goal
Freeze a dedicated 100-slice closure map for `chat` and implement the first
bounded foundation batch so the route continues toward canonical parity in a
governed way.

## Success Signal
- User or operator problem:
  - chat still feels visibly unfinished and needs a clearer small-slice
    execution lane
- Expected product or reliability outcome:
  - chat closure work can proceed in explicit bounded batches instead of broad
    polishing
- How success will be observed:
  - a route-specific 100-slice map exists and the first chat foundation batch
    is implemented
- Post-launch learning needed: no

## Deliverable For This Stage
A dedicated 100-slice chat map plus the first bounded implementation batch
covering topbar calmness, transcript cadence, and bubble-material foundations.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `docs/planning/canonical-100-slice-closure-map.md`
- `docs/planning/chat-canonical-100-slice-closure-map.md`
- `.codex/tasks/PRJ-832-chat-first-10-slice-batch-and-foundation-pass.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Freeze a route-specific 100-slice closure map for `chat`.
2. Move the active-surface note in the canonical closure map from
   `dashboard` to `chat`.
3. Implement the first bounded foundation batch for `chat`:
   - topbar calmness
   - transcript cadence
   - assistant and user bubble parity
4. Run focused validation and sync project truth.

## Acceptance Criteria
- a dedicated `chat` 100-slice map exists
- canonical planning truth points to `chat` as the active surface group
- the chat topbar is calmer and more canonical
- transcript and bubble surfaces are visibly closer to the canonical route
- focused validation passes

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Definition of Done
- [ ] Chat 100-slice map is written.
- [ ] First bounded chat foundation batch is implemented.
- [ ] Focused validation evidence is attached.

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
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/planning/canonical-100-slice-closure-map.md docs/planning/chat-canonical-100-slice-closure-map.md .codex/tasks/PRJ-832-chat-first-10-slice-batch-and-foundation-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- Manual checks:
  - route-only audit against `docs/ux/assets/aion-chat-canonical-reference-v4.png`
- Screenshots/logs:
  - deploy-side proof still pending
- High-risk checks:
  - preserve the existing transcript contract and composer/send flow

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
  - shared canonical persona figure
  - integrated composer tray
- New shared pattern introduced: no
- Design-memory entry reused:
  - chat background artwork
  - route-specific persona adaptation
- Design-memory update required: no
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - reuse existing chat artwork and embodied persona stage
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
  - live deploy-side proof still pending
- State checks: loading | empty | success
- Feedback locality checked: yes
- Raw technical errors hidden from end users: yes
- Responsive checks: desktop
- Input-mode checks: pointer | keyboard
- Accessibility checks:
  - preserved existing transcript, textarea, and button semantics
- Parity evidence:
  - canonical reference plus current local route audit

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - revert the bounded route-only `chat` batch if transcript readability or
    send posture regresses
- Observability or alerting impact: none
- Staged rollout or feature flag: none

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
This task intentionally redirects the active surface group from `dashboard` to
`chat` by explicit user instruction.

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
  - transcript, optimistic send, and composer contract remain unchanged

## AI Testing Evidence (required for AI features)

- `AI_TESTING_PROTOCOL.md` reviewed: not applicable
- Memory consistency scenarios:
- Multi-step context scenarios:
- Adversarial or role-break scenarios:
- Prompt injection checks:
- Data leakage and unauthorized access checks:
- Result:

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: not applicable
- Data classification: not applicable
- Trust boundaries: not applicable
- Permission or ownership checks: not applicable
- Abuse cases: not applicable
- Secret handling: none
- Security tests or scans: not applicable
- Fail-closed behavior: not applicable
- Residual risk: low

## Result Report

- Task summary:
  - froze a dedicated 100-slice closure map for `chat`
  - redirected canonical planning truth from `dashboard` to `chat`
  - implemented the first bounded chat foundation batch across topbar calmness,
    transcript cadence, and assistant/user bubble parity
  - implemented the next bounded portrait-and-rail batch across portrait-stage
    authority, calmer portrait notes/connectors, and a narrower cognitive rail
  - implemented the next bounded density batch across motivation, active goal,
    related memory, and suggested actions
  - implemented the next bounded composer-and-transcript batch across quick
    actions, composer tray density, and long-form transcript polish
  - implemented the next bounded transcript-first balance batch across topbar
    control weight, lead-card hierarchy, and rail width
  - implemented the next bounded chrome-reduction batch across top controls,
    quick actions, and scenic-note copy density
  - implemented one more bounded chrome-trim batch by reducing the remaining
    top controls to one summary pill, reducing quick actions to one primary
    suggestion, and matching both with calmer solo-material styling
  - implemented one more bounded right-rail copy batch by shortening current
    intent, active-goal, and memory body copy while tightening compact-panel
    and support-row spacing
  - implemented one more bounded portrait-note batch by shortening scenic-note
    copy, lightening note-card material, and shifting a little more desktop
    authority back to the transcript column
  - implemented one more bounded rail-material batch by softening topbar
    closure, reducing compact-panel weight, lightening support accents, and
    narrowing the desktop rail proportion again
  - implemented one more bounded lead-typography batch by reducing emblem
    weight, tightening lead-card spacing, and softening rail title/body scale
  - implemented one more bounded motivation-density batch by reducing
    motivation-card padding/scale and tightening the active-goal footer rhythm
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `docs/planning/canonical-100-slice-closure-map.md`
  - `docs/planning/chat-canonical-100-slice-closure-map.md`
  - `.codex/tasks/PRJ-832-chat-first-10-slice-batch-and-foundation-pass.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/planning/canonical-100-slice-closure-map.md docs/planning/chat-canonical-100-slice-closure-map.md .codex/tasks/PRJ-832-chat-first-10-slice-batch-and-foundation-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- What is incomplete:
  - deploy-side proof for the new chat batch
  - remaining batches beyond the foundation pass
- Next steps:
  - compare the deployed chat after the motivation-density and goal-footer batch
  - if needed, open the next bounded chat continuation lane only for remaining
    proof-backed drift
- Decisions made:
  - active flagship work is redirected from `dashboard` to `chat` by explicit
    user instruction
