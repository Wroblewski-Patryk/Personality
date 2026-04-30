# Task

## Header
- ID: PRJ-811
- Title: Fix Internal Chat Local Transcript Reconciliation
- Task Type: fix
- Current Stage: verification
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-810
- Priority: P1

## Context
Internal chat uses `/app/chat/history` as durable transcript truth and local
optimistic items for immediate send feedback. The previous reconciliation
removed local items when any durable item shared the same `event_id`.

## Goal
Keep local user and assistant items visible until the matching durable
transcript item exists.

## Scope
- `web/src/App.tsx`

## Implementation Plan
1. Review optimistic transcript merge helper.
2. Replace event-only reconciliation with exact message id plus
   `(event_id, role)` matching.
3. Validate through web build and long-message browser proof.

## Acceptance Criteria
- A durable user item cannot remove a local assistant reply for the same event.
- Durable history remains the source of truth.
- No second chat store is introduced.

## Definition of Done
- [x] `DEFINITION_OF_DONE.md` applicable checks are satisfied with evidence.
- [x] Web build passes.
- [x] Responsive proof uses backend-shaped chat transcript items.

## Validation Evidence
- Tests:
  - `Push-Location .\web; npm run build; Pop-Location`
- Manual checks:
  - Playwright proof with mocked `/app/chat/history`
- Screenshots/logs:
  - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-proof.json`

## Architecture Evidence
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/planning/shared-chat-transcript-and-telegram-continuity-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no

## Result Report
- Task summary:
  - local transcript reconciliation is now role-aware.
- Files changed:
  - `web/src/App.tsx`
- How tested:
  - web build and Playwright proof.
- What is incomplete:
  - none.
- Next steps:
  - PRJ-812.
