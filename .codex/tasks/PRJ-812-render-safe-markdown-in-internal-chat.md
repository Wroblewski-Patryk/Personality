# Task

## Header
- ID: PRJ-812
- Title: Render Safe Markdown In Internal Chat
- Task Type: feature
- Current Stage: verification
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-811
- Priority: P1

## Context
Chat transcript text was rendered directly as plain text, so assistant replies
showed Markdown markers such as `**bold**` and `*italic*`.

## Goal
Render a safe Markdown subset inside existing chat bubbles without raw HTML
injection.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`

## Implementation Plan
1. Add a tiny React-element Markdown renderer for the supported chat subset.
2. Render paragraphs, ordered lists, unordered lists, bold, italic, inline code,
   and fenced code.
3. Style rendered elements inside the existing chat message copy class.
4. Validate with web build and screenshot proof.

## Acceptance Criteria
- Supported Markdown markers are rendered semantically.
- User-authored HTML remains escaped by React.
- The existing chat bubble pattern is reused.

## Definition of Done
- [x] Web build passes.
- [x] Markdown-rich screenshot proof exists.
- [x] No `dangerouslySetInnerHTML` is used.

## Validation Evidence
- Tests:
  - `Push-Location .\web; npm run build; Pop-Location`
- Manual checks:
  - Playwright metrics confirm `strong`, `em`, `ol`, `ul`, and `pre code`
    render while raw supported markers are absent.
- Screenshots/logs:
  - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-desktop.png`
  - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-tablet.png`
  - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-mobile.png`

## Architecture Evidence
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no

## Result Report
- Task summary:
  - internal chat now renders safe Markdown through React elements.
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
- How tested:
  - web build and responsive browser proof.
- What is incomplete:
  - none.
- Next steps:
  - PRJ-813.
