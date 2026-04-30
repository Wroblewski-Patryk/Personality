# Task

## Header
- ID: PRJ-814
- Title: Improve Telegram Sentence-Aware Segmentation
- Task Type: fix
- Current Stage: verification
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-810
- Priority: P1

## Context
Telegram has a hard message limit and the repo already segments long delivery
below expression. The splitter preferred paragraph, newline, then whitespace,
but did not explicitly prefer sentence boundaries.

## Goal
Prefer paragraph, newline, sentence, and then word boundaries before any
last-resort hard split.

## Scope
- `backend/app/integrations/delivery_router.py`
- `backend/tests/test_delivery_router.py`

## Implementation Plan
1. Add sentence-boundary split detection below paragraph/newline boundaries.
2. Keep word-boundary fallback.
3. Keep hard splitting only when no safe boundary exists.
4. Add focused delivery-router tests.

## Acceptance Criteria
- Segments stay within Telegram limits.
- Normal prose splits on sentence boundaries when possible.
- Word boundaries are preferred before hard splitting.
- Segment order is preserved.

## Definition of Done
- [x] Delivery-router tests pass.
- [x] No transcript storage shape changes.
- [x] Transport adaptation remains below expression.

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_telegram_client.py; Pop-Location`
    - `15 passed`

## Architecture Evidence
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no

## Result Report
- Task summary:
  - Telegram segmentation now prefers sentence boundaries before word fallback.
- Files changed:
  - `backend/app/integrations/delivery_router.py`
  - `backend/tests/test_delivery_router.py`
- How tested:
  - focused backend tests.
- What is incomplete:
  - none.
- Next steps:
  - PRJ-815.
