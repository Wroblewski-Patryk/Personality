# Task

## Header
- ID: PRJ-810
- Title: Plan Internal Chat And Telegram Message Quality
- Task Type: research
- Current Stage: planning
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-714, PRJ-774, PRJ-643
- Priority: P1

## Context
The internal authenticated app chat is the canonical conversation owner, while
Telegram is a linked transport surface after explicit linking. Fresh user notes
report that internal chat messages can appear lost until refresh, long messages
look cut off, and Markdown markers are visible instead of styled text in both
internal chat and Telegram.

The repository already has a shared transcript contract, optimistic web chat
items, Telegram delivery segmentation, and Telegram Markdown-to-HTML delivery
support. This planning task analyzes the remaining gaps and records an
execution-ready lane without implementing code changes.

## Goal
Create one repo-owned implementation plan for improving internal chat
reliability, full-length rendering, Telegram segmentation, and Markdown display
while preserving the canonical transcript and action-owned transport
adaptation boundaries.

## Success Signal
- User or operator problem:
  - chat messages no longer appear lost
  - long replies remain fully readable
  - Markdown displays as formatting instead of raw markers
  - Telegram long replies arrive in ordered readable parts
- Expected product or reliability outcome:
  - internal chat and Telegram feel like consistent views over one canonical
    conversation
- How success will be observed:
  - targeted backend tests, web build, and responsive chat screenshot proof in
    later implementation tasks
- Post-launch learning needed: yes

## Deliverable For This Stage
One planning document that captures the user's notes, codebase analysis,
architecture fit, implementation queue, acceptance criteria, and validation
commands for the next bounded tasks.

## Scope
- `docs/planning/internal-chat-and-telegram-message-quality-plan.md`
- `.codex/tasks/PRJ-810-plan-internal-chat-and-telegram-message-quality.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `docs/planning/next-iteration-plan.md`

Analysis reviewed but did not modify:

- `web/src/App.tsx`
- `web/src/index.css`
- `web/src/lib/api.ts`
- `backend/app/api/routes.py`
- `backend/app/memory/repository.py`
- `backend/app/integrations/delivery_router.py`
- `backend/app/integrations/telegram/telemetry.py`
- `backend/app/integrations/telegram/client.py`
- `backend/tests/test_delivery_router.py`
- `backend/tests/test_telegram_client.py`
- `backend/tests/test_api_routes.py`

## Implementation Plan
1. Review canonical context and the task template.
2. Review architecture and planning docs for chat, Telegram, delivery, and
   transcript ownership.
3. Inspect current backend delivery, transcript projection, Telegram telemetry,
   web chat rendering, and optimistic reconciliation code.
4. Identify likely causes and current partial implementations.
5. Write a bounded execution plan that reuses existing systems.
6. Sync source-of-truth context files with the new plan.
7. Run a documentation diff sanity check.

## Acceptance Criteria
- The plan records the user's internal-chat and Telegram notes.
- The plan identifies current repo strengths and concrete gaps.
- The plan preserves:
  - one canonical app transcript
  - no second durable chat store
  - Telegram segmentation below expression in action/integration delivery
  - safe Markdown rendering only
- The plan breaks implementation into tiny, testable, reversible tasks.
- Validation commands are attached per task.
- Source-of-truth files point to the new plan.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it
- repository artifacts must stay in English
- do not implement code during this planning task

## Definition of Done
- [x] `DEFINITION_OF_DONE.md` planning-relevant checks are satisfied with
  evidence.
- [x] The plan file exists and is execution-ready.
- [x] The task board, project state, and next-iteration plan reference the new
  lane.
- [x] Architecture alignment and mismatch posture are recorded.

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
- code implementation in this planning slice

## Validation Evidence
- Tests:
  - not run; this is a planning-only documentation slice
- Manual checks:
  - reviewed current chat and Telegram code paths listed in Scope
  - reviewed canonical chat, delivery, runtime, logging, and behavior-testing
    docs
- Screenshots/logs:
  - not applicable for planning
- High-risk checks:
  - confirmed the plan keeps Telegram transport adaptation below expression
  - confirmed the plan does not add a second chat store

## Architecture Evidence
- Architecture source reviewed:
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/17_logging_and_debugging.md`
  - `docs/architecture/29_runtime_behavior_testing.md`
  - `docs/planning/shared-chat-transcript-and-telegram-continuity-plan.md`
  - `docs/planning/canonical-multi-channel-conversation-and-relational-outreach-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: not applicable
- Follow-up architecture doc updates:
  - none required before implementation; existing contracts already allow this
    lane

## UX/UI Evidence
- Design source type: approved_snapshot
- Design source reference: existing chat route canonical direction and user
  notes from 2026-04-30
- Canonical visual target: internal chat route message transcript behavior
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - current chat transcript bubbles and metadata row
- New shared pattern introduced: no
- Design-memory entry reused:
  - existing chat transcript source-of-truth posture
- Design-memory update required: no for planning; only if implementation
  introduces a new reusable Markdown message pattern
- Visual gap audit completed: planning-level only
- Background or decorative asset strategy: unchanged
- Canonical asset extraction required: no
- Screenshot comparison pass completed: not applicable in planning
- Remaining mismatches:
  - implementation tasks must prove full-length and Markdown-rich messages on
    desktop, tablet, and mobile
- State checks: loading | empty | error | success planned for implementation
- Feedback locality checked: planned
- Raw technical errors hidden from end users: planned
- Responsive checks: desktop | tablet | mobile planned
- Input-mode checks: touch | pointer | keyboard planned
- Accessibility checks:
  - Markdown output must remain semantic and readable by assistive technology
- Parity evidence:
  - to be captured in `PRJ-813`

## Deployment / Ops Evidence
- Deploy impact: low
- Env or secret changes: none expected
- Health-check impact:
  - possible Telegram supported-Markdown metadata update in `PRJ-815`
- Smoke steps updated:
  - not in this planning slice
- Rollback note:
  - revert web Markdown renderer/reconciliation changes or delivery-router
    segmentation changes independently if a later implementation regresses
    chat delivery
- Observability or alerting impact:
  - Telegram delivery telemetry already exposes segmentation and formatting
    posture; later tasks may update supported Markdown metadata
- Staged rollout or feature flag:
  - not required for the planning slice

## Review Checklist
- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run or marked not applicable for planning.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Likely implementation insight from analysis:

- internal chat disappearance may be caused by local reconciliation removing
  optimistic items by event id rather than exact message identity
- internal chat Markdown is currently absent because transcript text is rendered
  directly as text
- Telegram already has partial segmentation and Markdown support, so the next
  work should refine rather than replace it

## Production-Grade Required Contract

Every task must include these mandatory sections before it can move to `READY`
or `IN_PROGRESS`:

- `Goal`
- `Scope` with exact files, modules, routes, APIs, schemas, docs, or runtime
  surfaces
- `Implementation Plan` with step-by-step execution and validation
- `Acceptance Criteria` with testable conditions
- `Definition of Done` using `DEFINITION_OF_DONE.md`
- `Result Report`

Runtime tasks must be delivered as a vertical slice: UI -> logic -> API -> DB
-> validation -> error handling -> test. Partial implementations, mock-only
paths, placeholders, fake data, and temporary fixes are forbidden.

## Integration Evidence

- `INTEGRATION_CHECKLIST.md` reviewed: yes
- Real API/service path used: analysis only
- Endpoint and client contract match: yes, plan preserves `/app/chat/history`
  and `/app/chat/message`
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable for planning
- Error state verified: not applicable for planning
- Refresh/restart behavior verified:
  - identified as a target for `PRJ-811`
- Regression check performed:
  - not run; planning-only slice

## Product / Discovery Evidence
- Problem validated: yes
- User or operator affected:
  - first-party internal chat and linked Telegram user
- Existing workaround or pain:
  - refresh makes apparently missing messages reappear
  - raw Markdown markers reduce readability
  - long Telegram replies need readable segmentation
- Smallest useful slice:
  - fix internal chat local reconciliation first
- Success metric or signal:
  - no message disappears during send/refresh; Markdown-rich long reply renders
    correctly in app and Telegram tests
- Feature flag, staged rollout, or disable path: not applicable
- Post-launch feedback or metric check:
  - watch Telegram delivery telemetry and collect one live/manual chat proof
    after deployment

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: no
- Critical user journey:
  - user sends/receives a long Markdown-rich answer through internal chat or
    Telegram
- SLI:
  - message visible in canonical transcript and delivered transport segments
    under limit
- SLO:
  - not defined for planning
- Error budget posture: not applicable
- Health/readiness check:
  - `/health.conversation_channels.telegram`
- Logs, dashboard, or alert route:
  - Telegram delivery telemetry and runtime action result
- Smoke command or manual smoke:
  - planned in implementation tasks
- Rollback or disable path:
  - revert scoped web renderer or delivery-router change

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: no
- Data classification:
  - user-authored chat content
- Trust boundaries:
  - web renderer must not render unsanitized HTML
  - Telegram formatting must escape HTML before parse-mode delivery
- Permission or ownership checks:
  - authenticated `/app/*` routes stay unchanged
- Abuse cases:
  - user sends Markdown containing raw HTML or malformed formatting
- Secret handling:
  - no secret changes
- Security tests or scans:
  - planned safe-rendering tests
- Fail-closed behavior:
  - unsafe Telegram Markdown falls back to plain text
- Residual risk:
  - implementation must choose a safe Markdown renderer or sanitizer

## AI Testing Evidence

- `AI_TESTING_PROTOCOL.md` reviewed: no
- Memory consistency scenarios:
  - planned through transcript continuity tests
- Multi-step context scenarios:
  - not required for this planning task
- Adversarial or role-break scenarios:
  - Markdown injection should be tested in implementation
- Prompt injection checks:
  - not applicable to planning
- Data leakage and unauthorized access checks:
  - authenticated chat route boundaries stay unchanged
- Result:
  - no AI-runtime behavior changed

## Result Report

- Task summary:
  - created an execution-ready plan for internal chat reliability,
    full-length rendering, Telegram segmentation, and Markdown support
- Files changed:
  - `docs/planning/internal-chat-and-telegram-message-quality-plan.md`
  - `.codex/tasks/PRJ-810-plan-internal-chat-and-telegram-message-quality.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `docs/planning/next-iteration-plan.md`
- How tested:
  - planning-only manual cross-review; no automated tests run
- What is incomplete:
  - implementation tasks `PRJ-811..PRJ-815` remain to be executed
- Next steps:
  - start `PRJ-811` as the smallest safe implementation slice
- Decisions made:
  - keep canonical transcript ownership unchanged
  - refine existing Telegram delivery router instead of replacing it
