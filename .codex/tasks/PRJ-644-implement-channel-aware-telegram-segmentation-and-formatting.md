# Task

## Header
- ID: PRJ-644
- Title: Implement channel-aware Telegram segmentation and formatting
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-643
- Priority: P1

## Context
Telegram has a hard message-length ceiling and a specific parse/render model,
but current delivery sends one raw message without channel-aware adaptation.

## Goal
Implement channel-aware Telegram delivery that can segment long messages and
apply safe markdown rendering without hardcoding the same limits into other
channels.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Telegram delivery segments long outbound content according to a channel-owned limit.
- [x] Telegram rendering uses an explicit formatting policy instead of raw literal markdown passing through by accident.
- [x] API and future UI channels remain free to use different limits and formatting capabilities.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_telegram_client.py tests/test_action_executor.py -k "telegram or delivery_router" tests/test_api_routes.py -k "telegram_link or telegram_webhook or telegram" tests/test_runtime_pipeline.py -k "telegram"; Pop-Location`
- Manual checks: cross-review that segmentation and formatting stay inside `DeliveryRouter` + `TelegramClient`, not planning or expression
- Screenshots/logs:
- High-risk checks: long-message segmentation preserves delivery order, supported markdown normalizes into explicit Telegram HTML parse mode, unsafe markdown falls back to plain text

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/16_agent_contracts.md`, `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: runtime reality, testing, runbook

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This should land as delivery-layer adaptation, not as prompt-shaping pressure on
expression output.

Implemented through the existing `DeliveryRouter` and `TelegramClient`
boundary. Telegram delivery now:

- splits long responses by transport-owned limits with paragraph/newline/space
  preference before hard splitting
- normalizes a bounded markdown subset (`**bold**`, inline code, fenced code)
  into Telegram HTML parse mode
- falls back to plain text when markdown is structurally unsafe
