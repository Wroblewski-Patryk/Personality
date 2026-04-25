# Task

## Header
- ID: PRJ-711
- Title: Plan the shared chat transcript and linked Telegram continuity lane
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-684
- Priority: P1

## Context
Fresh user product feedback on 2026-04-25 confirms that linked Telegram
identity continuity is no longer the main gap. The current runtime can already
persist linked Telegram and first-party app turns under the same backend
`user_id`, but the first-party chat experience still does not present that
continuity as one shared conversation transcript.

Current repo facts:

- linked Telegram ingress now resolves to the authenticated backend user after
  link confirmation, so shared memory continuity is available at the identity
  layer
- `GET /app/chat/history` still returns memory-oriented entries instead of a
  message transcript
- `web/src/App.tsx` renders live local `sessionMessages` separately from the
  backend-loaded continuity list, so the product does not yet behave like one
  continuous chat across Telegram, web, and the future mobile client
- `mobile/` is still deferred, so the correct next step is to freeze the
  shared backend contract and web UX behavior that mobile will later reuse

This task freezes an execution-ready implementation lane so the repo can move
from "shared memory owner" to "shared conversation transcript" without adding a
new chat subsystem or bypassing the existing event, action, and memory flow.

## Goal
Create one detailed, execution-ready plan for a shared cross-channel chat
transcript so linked Telegram, web, and future mobile clients can show one
continuous conversation from the moment the channel is linked.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] a detailed execution plan exists in repo for the shared transcript lane
- [x] the next implementation slices are seeded in source-of-truth planning
  and context files
- [x] a recurring planning guardrail is recorded in the learning journal

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - none; planning and context sync only
- Manual checks:
  - cross-review of backend chat history contract, Telegram link continuity
    path, web chat rendering, and mobile baseline docs against the fresh user
    product request from 2026-04-25
- Screenshots/logs:
  - none
- High-risk checks:
  - the plan must reuse the existing event -> action -> memory pipeline and
    linked identity owner instead of proposing a second conversation store
  - the plan must keep Telegram optional and bounded to post-link continuity
    only

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/26_env_and_config.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - none
- Follow-up architecture doc updates:
  - later implementation slices should update canonical docs only if the app
    chat contract or shared client baseline changes after verification

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
The detailed execution plan lives in
`docs/planning/shared-chat-transcript-and-telegram-continuity-plan.md`.

The seeded implementation lane is:

- `PRJ-712` Shared Chat Transcript Contract Freeze
- `PRJ-713` Backend Transcript Projection And Chat History API Update
- `PRJ-714` Web Chat Thread Unification And Scroll Behavior
- `PRJ-715` Cross-Channel Regression Proof For Linked Telegram And App Chat
- `PRJ-716` Shared Client Baseline And Product Docs Sync
- `PRJ-717` Final Validation, Context Sync, And Learning Closure
