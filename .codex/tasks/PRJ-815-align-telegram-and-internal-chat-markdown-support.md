# Task

## Header
- ID: PRJ-815
- Title: Align Telegram And Internal Chat Markdown Support
- Task Type: feature
- Current Stage: verification
- Status: DONE
- Owner: Backend Builder | Frontend Builder
- Depends on: PRJ-812, PRJ-814
- Priority: P1

## Context
Telegram supported bold and code formatting, while internal chat had no
Markdown rendering. The user example depends on bold and italic emphasis.

## Goal
Align the approved safe Markdown subset across internal chat rendering and
Telegram delivery metadata.

## Scope
- `backend/app/integrations/delivery_router.py`
- `backend/app/integrations/telegram/telemetry.py`
- `backend/tests/test_delivery_router.py`
- `backend/tests/test_api_routes.py`
- `web/src/App.tsx`
- `web/src/index.css`
- docs and context files for the lane

## Implementation Plan
1. Add Telegram italic formatting support with escaping and unsafe fallback.
2. Update Telegram supported Markdown metadata.
3. Keep list support as plain-text readability in Telegram and semantic list
   rendering in internal chat.
4. Update docs and context.
5. Run focused backend tests, API health regression, web build, and responsive
   proof.

## Acceptance Criteria
- Telegram reports the supported Markdown subset truthfully.
- Telegram safe italic and bold render via HTML parse mode.
- Unsafe Markdown falls back to plain text.
- Internal chat renders the same main subset safely.

## Definition of Done
- [x] Focused backend delivery tests pass.
- [x] Web build passes.
- [x] Responsive proof exists.
- [x] Docs and context are synced.

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_telegram_client.py; Pop-Location`
    - `15 passed`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "telegram_round_trip_readiness_state or chat"; Pop-Location`
    - `9 passed, 108 deselected`
- Manual checks:
  - Playwright responsive proof

## Architecture Evidence
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no

## Result Report
- Task summary:
  - Telegram and internal chat now share a safe Markdown quality baseline.
- Files changed:
  - `backend/app/integrations/delivery_router.py`
  - `backend/app/integrations/telegram/telemetry.py`
  - `backend/tests/test_delivery_router.py`
  - `backend/tests/test_api_routes.py`
  - `web/src/App.tsx`
  - `web/src/index.css`
  - docs/context files
- How tested:
  - focused backend tests, API health/chat regression, web build, and
    responsive proof.
- What is incomplete:
  - none.
- Next steps:
  - final validation and commit.
