# Internal Chat And Telegram Message Quality Plan

## Purpose

This plan turns the latest user notes about the internal chat and Telegram
delivery into one bounded implementation lane.

The goal is not to create a new messaging system. The goal is to harden the
existing canonical app transcript, keep Telegram as a transport adaptation
layer, and make Markdown display consistently across both surfaces.

## User Notes Analyzed

Fresh notes from 2026-04-30 report:

- internal chat messages sometimes look lost and only appear after refresh
- internal chat messages should not be visually truncated
- Telegram should split long replies into smaller messages without cutting
  words, preferably on sentence boundaries, while honoring Telegram limits
- Markdown should render in Telegram and in the internal chat instead of
  showing raw markers such as `**bold**` and `*italic*`
- the observed assistant reply contains Markdown emphasis and a long answer
  that appears visually cut off in the internal chat

## Current Repo Analysis

### Existing Systems To Reuse

- `/app/chat/history` is already the backend-owned canonical transcript
  surface.
- `web/src/App.tsx` already renders transient local chat items for in-flight
  sends and then reconciles them against durable history.
- `backend/app/memory/repository.py` already projects episodic turn memory into
  bounded transcript items.
- `backend/app/integrations/delivery_router.py` already adapts Telegram
  delivery below expression, including:
  - bounded message segmentation
  - `parse_mode="HTML"` for supported Markdown
  - plain-text fallback for unsafe Markdown
- `backend/app/integrations/telegram/telemetry.py` already exposes Telegram
  delivery limit, segment target, formatting posture, and last delivery
  metadata through health surfaces.
- Existing regression anchors already cover chat routes, memory transcript
  projection, Telegram delivery routing, and Telegram client parse mode.

### Gaps Found

1. Internal chat local reconciliation is too broad.
   - `reconcileLocalTranscriptItems()` removes local items when either the
     durable message id or durable event id exists.
   - If the backend history refresh contains one durable item for an event but
     not the matching local assistant item yet, the local assistant item can be
     removed early and appear to vanish until a later refresh.
   - The fix should reconcile by exact message identity, or by role-aware
     event identity, not event id alone.

2. Internal chat has no Markdown renderer.
   - `web/src/App.tsx` renders message text directly inside a paragraph.
   - `web/src/index.css` preserves line breaks with `white-space: pre-line`,
     but no Markdown markers are transformed into semantic HTML.
   - The user-visible symptom matches this: raw `**...**` and `*...*` markers
     are shown instead of styled text.

3. Internal chat should prove full-length rendering.
   - The current message copy itself is not line-clamped, but the route has
     nested layout constraints and a scrollable transcript.
   - A long assistant message should be verified in desktop, tablet, and mobile
     views so message text wraps and remains accessible rather than appearing
     cut off by container sizing or preview-specific classes.

4. Telegram segmentation is implemented but not sentence-prioritized enough.
   - `_split_telegram_text()` currently prefers paragraph, newline, then space.
   - That prevents many word cuts, but it does not explicitly prefer sentence
     endings before word boundaries.
   - The fallback still hard-cuts text when one token exceeds Telegram limits;
     that fallback should remain last-resort and be explicitly covered.

5. Telegram Markdown support is partial.
   - Current supported Markdown is `bold`, `inline_code`, and `fenced_code`.
   - The user example also uses italic emphasis through `*...*`.
   - If internal chat and Telegram should feel consistent, the shared supported
     subset should cover at least bold, italic, inline code, fenced code,
     bullet/numbered list readability, and safe links if approved.

## Architecture Fit

This lane fits the existing architecture because:

- the app transcript remains canonical and backend-owned
- the web client remains a thin `/app/*` renderer over transcript items
- Telegram delivery adaptation stays below expression in action/integration
  routing
- Markdown rendering is display or transport formatting, not a second
  expression pass
- no second durable chat store is introduced

Architecture sources reviewed:

- `docs/architecture/15_runtime_flow.md`
- `docs/architecture/16_agent_contracts.md`
- `docs/architecture/17_logging_and_debugging.md`
- `docs/architecture/29_runtime_behavior_testing.md`
- `docs/planning/shared-chat-transcript-and-telegram-continuity-plan.md`
- `docs/planning/canonical-multi-channel-conversation-and-relational-outreach-plan.md`

## Implementation Queue

### PRJ-811 - Fix Internal Chat Local Transcript Reconciliation

Goal:

- stop local optimistic user or assistant messages from disappearing during
  the post-send history refresh.

Scope:

- `web/src/App.tsx`
- optional frontend regression harness if one exists or is introduced in a
  minimal repo-consistent way

Implementation plan:

1. Replace event-id-only local reconciliation with exact message-id matching,
   or role-aware `(event_id, role)` matching.
2. Keep local assistant replies until a durable assistant transcript item for
   the same event exists.
3. Keep local delivered user turn until the durable user transcript item exists.
4. Add a focused helper-level test if the web stack supports it; otherwise
   document manual/browser proof in the task evidence.

Acceptance criteria:

- a returned assistant reply remains visible immediately after
  `/app/chat/message`
- a history refresh containing only the user side of the event cannot remove
  the local assistant side
- backend history remains the final source of truth
- no second durable chat store is introduced

Validation:

- `Push-Location .\web; npm run build; Pop-Location`
- focused browser/manual proof with a delayed or partial history refresh

### PRJ-812 - Render Safe Markdown In Internal Chat

Goal:

- render the same safe Markdown subset in the internal chat instead of showing
  raw markers.

Scope:

- `web/src/App.tsx`
- `web/src/index.css`
- `web/package.json` only if a vetted existing dependency is preferred over a
  tiny local renderer

Implementation plan:

1. Choose the smallest safe renderer consistent with the web stack.
2. Render assistant and user transcript text as sanitized Markdown output.
3. Support at least:
   - bold
   - italic
   - inline code
   - fenced code
   - ordered and unordered lists
   - paragraphs and line breaks
4. Style Markdown elements inside existing chat message surfaces without
   creating a new visual pattern.
5. Keep unsafe HTML out of rendered messages.

Acceptance criteria:

- `**bold**` renders as bold
- `*italic*` renders as italic
- code and fenced code render safely
- lists remain readable inside chat bubbles
- user-authored raw HTML is escaped or sanitized
- no raw Markdown markers remain for the supported subset

Validation:

- `Push-Location .\web; npm run build; Pop-Location`
- screenshot proof for a long Markdown-rich assistant reply on desktop,
  tablet, and mobile

### PRJ-813 - Prove Full-Length Internal Chat Message Rendering

Goal:

- ensure long internal chat messages remain fully accessible and do not appear
  visually cut off.

Scope:

- `web/src/App.tsx`
- `web/src/index.css`
- `.codex/artifacts/` screenshot evidence

Implementation plan:

1. Seed or simulate a long assistant transcript item using the same shape as
   `/app/chat/history`.
2. Check the chat route with a message longer than the user's reported sample.
3. Remove any preview-only or container-level style that clamps real messages.
4. Preserve transcript scrolling while ensuring each message bubble itself can
   expand naturally.
5. Capture responsive evidence.

Acceptance criteria:

- long assistant text wraps within the bubble
- the full message is reachable by scrolling the transcript/page
- no line clamp, text overflow, or fixed-height bubble cuts the message body
- desktop, tablet, and mobile screenshots show coherent readable layout

Validation:

- `Push-Location .\web; npm run build; Pop-Location`
- browser or Playwright screenshots saved under `.codex/artifacts/`

### PRJ-814 - Improve Telegram Sentence-Aware Segmentation

Goal:

- split Telegram replies on semantic boundaries before falling back to word or
  hard length boundaries.

Scope:

- `backend/app/integrations/delivery_router.py`
- `backend/tests/test_delivery_router.py`
- `backend/app/integrations/telegram/telemetry.py` if supported Markdown or
  segmentation posture metadata changes

Implementation plan:

1. Keep `TELEGRAM_DELIVERY_MESSAGE_LIMIT=4096`.
2. Keep a safer segment target below the hard limit.
3. Update `_preferred_split_index()` to prefer:
   - paragraph boundary
   - newline boundary
   - sentence-ending punctuation followed by whitespace
   - whitespace
   - final hard split only when no safe boundary exists
4. Add tests proving ordered segments, limit compliance, no word cuts in normal
   text, and sentence-priority behavior.
5. Preserve one canonical app transcript row for the assistant reply.

Acceptance criteria:

- all Telegram segments are `<= 4096` characters
- normal prose splits at sentence or paragraph boundaries
- words are not cut when any safe boundary exists
- impossible over-limit tokens use the documented last-resort hard split
- segment order is preserved
- app transcript does not store one row per Telegram segment

Validation:

- `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py; Pop-Location`
- targeted chat/API regression if transcript behavior is touched

### PRJ-815 - Align Telegram And Internal Chat Markdown Support

Goal:

- make the supported Markdown subset explicit and consistent between Telegram
  delivery and internal chat rendering.

Scope:

- `backend/app/integrations/delivery_router.py`
- `backend/app/integrations/telegram/telemetry.py`
- `backend/tests/test_delivery_router.py`
- `web/src/App.tsx`
- `web/src/index.css`
- docs/context files touched by this lane

Implementation plan:

1. Extend Telegram formatting support to italic if the renderer can do it
   safely.
2. Decide whether links are supported now or intentionally deferred.
3. Update `TELEGRAM_DELIVERY_SUPPORTED_MARKDOWN` to reflect truth.
4. Keep Telegram formatting as HTML parse mode with escaping, or fall back to
   plain text when formatting is unsafe.
5. Document any intentional differences between internal chat and Telegram
   when Telegram cannot safely match a web rendering feature.

Acceptance criteria:

- supported Markdown is documented by code and health metadata
- Telegram bold/italic/code examples render with parse mode when safe
- unsupported or malformed Markdown falls back safely
- internal chat and Telegram have matching behavior for the approved subset
- tests cover malformed Markdown fallback and safe formatting

Validation:

- `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_telegram_client.py; Pop-Location`
- `Push-Location .\web; npm run build; Pop-Location`
- final doc/context sync check

## Recommended Order

1. `PRJ-811`
2. `PRJ-812`
3. `PRJ-813`
4. `PRJ-814`
5. `PRJ-815`

Why this order:

- first stop messages from appearing lost
- then render Markdown in the canonical internal chat
- then prove long internal messages remain fully readable
- then refine Telegram segmentation
- finally align the cross-channel Markdown subset and metadata

## Risks And Guardrails

- Do not move Telegram splitting into expression or planning.
- Do not store Telegram segments as separate transcript messages.
- Do not introduce a second chat history store in the browser.
- Do not render raw HTML from chat content.
- Do not claim Telegram and web support identical Markdown unless tests prove
  the exact subset.
- Keep screenshot proof scoped to the chat surface only; do not reopen broader
  flagship dashboard or landing work in this lane.

## Definition Of Done For The Lane

- internal chat sends no longer show disappearing local items
- supported Markdown renders in the internal chat
- long internal chat messages remain fully readable
- Telegram splits long replies under Telegram limits, in order, with sentence
  and word boundaries preferred
- Telegram safe Markdown support and fallback are test-covered
- backend tests, web build, responsive proof, docs, and context truth all agree
  on the final behavior
