# Task

## Header
- ID: PRJ-813
- Title: Prove Full-Length Internal Chat Message Rendering
- Task Type: design
- Current Stage: verification
- Status: DONE
- Owner: QA/Test
- Depends on: PRJ-812
- Priority: P1

## Context
User-reported long assistant replies looked visually cut off in the internal
chat. The message body needed proof that it expands naturally while the
transcript remains scrollable.

## Goal
Prove long Markdown-rich transcript messages are fully reachable on desktop,
tablet, and mobile.

## Scope
- `web/src/index.css`
- `.codex/artifacts/prj811-815-chat-message-quality/`

## Implementation Plan
1. Preserve transcript scrolling.
2. Ensure message copy does not use clamping or hidden overflow.
3. Use Playwright route mocks to seed a backend-shaped long transcript.
4. Capture desktop, tablet, and mobile screenshots plus DOM metrics.

## Acceptance Criteria
- Message copy has visible overflow and matching scroll/client height.
- Transcript is scrollable.
- Markdown-rich content remains visible and semantic.

## Definition of Done
- [x] Responsive screenshots captured.
- [x] Proof JSON records no raw supported Markdown markers.
- [x] Web build passes.

## Validation Evidence
- Tests:
  - `Push-Location .\web; npm run build; Pop-Location`
- Manual checks:
  - Playwright responsive proof
- Screenshots/logs:
  - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-proof.json`

## UX/UI Evidence
- Design source type: approved_snapshot
- Design source reference: existing chat route pattern plus user notes
- Responsive checks: desktop | tablet | mobile
- Accessibility checks:
  - semantic elements are rendered as normal React DOM nodes

## Result Report
- Task summary:
  - full-length chat message rendering has responsive proof.
- Files changed:
  - `web/src/index.css`
- How tested:
  - Playwright screenshots and web build.
- What is incomplete:
  - none.
- Next steps:
  - PRJ-814.
