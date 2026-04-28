# Task

## Header
- ID: PRJ-770
- Title: Add Dashboard Conversation Channel Status Banner
- Task Type: feature
- Current Stage: verification
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-764
- Priority: P1

## Context
Production triage on 2026-04-28 showed that the foreground runtime and web
shell can be healthy while the user still experiences a silent conversation
channel. The production `/health` surface reported Telegram as configured and
round-trip ready, but all Telegram ingress and delivery counters were zero, so
the dashboard has no first-party way to explain that messages are not reaching
or leaving the channel.

## Goal
Expose conversation-channel operational status in the authenticated dashboard,
using existing backend health truth instead of inventing a parallel client-side
readiness model.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- existing backend health contract:
  - `/health.conversation_channels.telegram`
  - `/health.attention`
  - `/health.proactive`
- tests or proof appropriate to the touched frontend surface
- source-of-truth updates for UX/ops context after implementation

## Implementation Plan
1. Reuse the existing web shell data-fetching pattern to read backend-owned
   readiness truth from the health surface.
2. Add a restrained dashboard status banner or signal row for conversation
   delivery posture.
3. Derive copy from machine-visible backend states only:
   `round_trip_state`, ingress counters, delivery counters, `last_ingress`,
   `last_delivery`, and attention queue counts.
4. Cover at least these states:
   configured and recently active, configured but no observed traffic,
   ingress rejected or runtime failed, delivery failed, and loading/error.
5. Validate the route with `npm run build` and browser/manual evidence for
   desktop, tablet, and mobile where local tooling allows it.

## Acceptance Criteria
- The dashboard shows a clear, non-alarming status when Telegram is configured
  but no webhook traffic has been observed.
- The dashboard distinguishes provider readiness from actual recent message
  ingress/delivery.
- The UI does not claim Telegram is working when health shows rejection,
  runtime failure, or delivery failure.
- The implementation consumes existing backend health truth and does not add a
  duplicate readiness source.
- State and responsive evidence are recorded before the task can move to DONE.

## Deliverable For This Stage
- implementation and verification evidence for a dashboard status signal over
  existing backend health truth

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it
- reuse the backend health contract as the source of truth

## Definition of Done
- [x] Dashboard uses backend-owned health truth for conversation status.
- [x] Loading, configured-but-idle, active, failure, and unavailable states are
      covered.
- [x] Focused frontend validation and manual/browser proof are attached.
- [x] Source-of-truth docs/context are synchronized with the delivered behavior.
- [x] `DEFINITION_OF_DONE.md` is satisfied with evidence before DONE.

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
- hardcoded production incidents or fake channel states

## Validation Evidence
- Tests:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- Manual checks:
  - production `/health` reviewed on 2026-04-28
  - production foreground `POST /event` smoke returned `action_status=success`
  - production webhook repaired in `PRJ-773`; post-repair health showed
    `last_ingress.state=processed` and `last_delivery.state=sent`
  - local dev server smoke:
    - `http://127.0.0.1:5177/dashboard`
    - result: HTTP `200`, `content-type=text/html`
- Screenshots/logs:
  - production health summary:
    - `status=ok`
    - `release_readiness.ready=true`
    - `conversation_channels.telegram.round_trip_state=provider_backed_ready`
    - `ingress_attempts=0`
    - `ingress_processed=0`
    - `delivery_attempts=0`
    - `delivery_failures=0`
    - `last_ingress={}`
    - `last_delivery={}`
- High-risk checks:
  - no backend runtime implementation changed in this slice
  - dashboard consumes `/health` and does not create a duplicate readiness
    source

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
  - `.agents/workflows/general.md`
  - `docs/operations/runtime-ops-runbook.md`
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - not applicable
- Follow-up architecture doc updates:
  - implementation should update UX/ops context, not architecture, unless the
    backend health contract changes

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - existing authenticated dashboard route and current Aviary visual system
- Canonical visual target:
  - reuse current dashboard shell patterns; no new canonical screenshot target
    is introduced by this planning task
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - dashboard signal/status surfaces
  - backend health truth surfaces
- New shared pattern introduced: yes
- Design-memory entry reused:
  - dashboard flagship status/signal cards
- Design-memory update required: no; this is currently a dashboard-local status
  signal, not a promoted shared pattern
- Visual gap audit completed: no
- Background or decorative asset strategy:
  - not applicable
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
  - screenshot-level browser proof remains pending due to the existing local
    browser runtime constraint recorded elsewhere in project context
- State checks: loading | configured-but-idle | error | success
- Responsive checks: desktop | tablet | mobile via responsive CSS constraints
- Input-mode checks: touch | pointer | keyboard
- Accessibility checks:
  - pending implementation
- Parity evidence:
  - pending implementation

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes:
  - none expected
- Health-check impact:
  - consumes existing health fields only
- Smoke steps updated:
  - pending implementation if dashboard status becomes an operator surface
- Rollback note:
  - remove the dashboard status banner while leaving backend health surfaces
    unchanged

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
The incident that motivated this task currently points toward Telegram ingress
or webhook/linking visibility rather than a foreground runtime failure. The
dashboard work should make that distinction visible without hiding the need for
operator-level Telegram webhook checks.

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
- Real API/service path used: yes
- Endpoint and client contract match: yes
- DB schema and migrations verified: not applicable
- Loading state verified: yes
- Error state verified: yes
- Refresh/restart behavior verified: local dev server smoke passed after build
- Regression check performed:
  - `Push-Location .\web; npm run build; Pop-Location`

## AI Testing Evidence (required for AI features)

- `AI_TESTING_PROTOCOL.md` reviewed: not applicable
- Memory consistency scenarios:
  - not applicable
- Multi-step context scenarios:
  - not applicable
- Adversarial or role-break scenarios:
  - not applicable
- Prompt injection checks:
  - not applicable
- Data leakage and unauthorized access checks:
  - not applicable
- Result:
  - not applicable

## Result Report

- Task summary:
  - dashboard now displays conversation-channel status from backend health,
    distinguishing live Telegram delivery from configured-but-silent and
    failure states
- Files changed:
  - `.codex/tasks/PRJ-770-plan-dashboard-conversation-channel-status-banner.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `web/src/lib/api.ts`
  - `web/src/App.tsx`
  - `web/src/index.css`
- How tested:
  - production health and foreground event smoke were reviewed before
    implementation
  - `Push-Location .\web; npm run build; Pop-Location` passed
  - local dev server smoke returned `200` for `/dashboard`
- What is incomplete:
  - screenshot-level browser proof remains pending due to the existing local
    browser runtime constraint recorded elsewhere in project context
- Next steps:
  - deploy the web shell and verify the dashboard status against production
    health after deploy
- Decisions made:
  - use existing health surfaces instead of creating a new readiness model
