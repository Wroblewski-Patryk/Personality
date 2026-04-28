# Task

## Header
- ID: PRJ-773
- Title: Verify Production Telegram Webhook And Plan Repair
- Task Type: release
- Current Stage: verification
- Status: DONE
- Owner: Ops/Release
- Depends on: PRJ-767
- Priority: P0

## Context
The user reported that production messages are not receiving replies. Production
health and foreground API smoke show that the runtime is alive, while Telegram
traffic telemetry was initially empty. A synthetic Telegram-shaped POST without
the webhook secret was rejected and recorded by telemetry, proving that the
production `/event` route recognizes Telegram webhook payloads and updates the
health surface when traffic reaches it.

## Goal
Restore the live bot webhook to the canonical production endpoint using the
existing production-owned `/telegram/set-webhook` path, then verify real
Telegram ingress and delivery through backend health telemetry.

## Scope
- production host:
  - `https://aviary.luckysparrow.ch`
- production Telegram webhook target:
  - `https://aviary.luckysparrow.ch/event`
- existing scripts:
  - `backend/scripts/run_telegram_mode_smoke.ps1`
  - `backend/scripts/run_telegram_mode_smoke.sh`
  - `backend/scripts/set_telegram_webhook.ps1`
  - `backend/scripts/set_telegram_webhook.sh`
- existing health surfaces:
  - `/health.conversation_channels.telegram`
  - `/health.attention`
  - `/health.deployment`

## Implementation Plan
1. Capture a pre-check production health snapshot and record:
   `conversation_channels.telegram`, `attention`, and `deployment`.
2. Prefer the existing production-owned webhook setter when the app already has
   the correct bot token and webhook secret configured:
   ```powershell
   $body = @{ webhook_url = "https://aviary.luckysparrow.ch/event" } | ConvertTo-Json -Compress
   Invoke-RestMethod `
     -Method Post `
     -Uri "https://aviary.luckysparrow.ch/telegram/set-webhook" `
     -ContentType "application/json" `
     -Body $body
   ```
3. If provider inspection is still needed later, run:
   ```powershell
   Push-Location .\backend
   .\scripts\run_telegram_mode_smoke.ps1 `
     -BotToken "<telegram_bot_token>" `
     -ExpectedWebhookUrl "https://aviary.luckysparrow.ch/event" `
     -RestoreWebhookUrl "https://aviary.luckysparrow.ch/event" `
     -SecretToken "<telegram_webhook_secret>" `
     -RequiredChatId "<known_chat_id>"
   Pop-Location
   ```
4. Interpret the provider output:
   - `webhook_mode.matches_expected=false` means repair the webhook URL.
   - empty `current_url` means the bot is not in webhook mode.
   - high `pending_update_count` means Telegram is collecting undelivered
     updates and the webhook is not being consumed successfully.
   - `listen_probe.updates_count>0` after deleting webhook means the bot is
     receiving user messages, but webhook delivery was misconfigured or blocked.
   - missing `required_chat_id` means the user is on the wrong bot/chat, has not
     sent `/start`, or the chosen chat id is wrong.
5. Repair based on evidence:
   - wrong or empty webhook URL:
     ```powershell
     Push-Location .\backend
     .\scripts\set_telegram_webhook.ps1 `
       -ApiBase "https://aviary.luckysparrow.ch" `
       -WebhookUrl "https://aviary.luckysparrow.ch/event" `
       -SecretToken "<telegram_webhook_secret>"
     Pop-Location
     ```
   - wrong secret:
     re-run `set_telegram_webhook` with the exact production
     `TELEGRAM_WEBHOOK_SECRET` value, then send one real Telegram message.
   - wrong bot/chat:
     confirm the active bot token in Coolify, send `/start` to that bot, then
     restart the link flow from the authenticated app tools surface.
   - webhook correct but health still shows no ingress after a real message:
     inspect Coolify proxy logs and Telegram `last_error_message` /
     `last_error_date` from `getWebhookInfo`.
6. After repair, send one real Telegram message and confirm:
   - `/health.conversation_channels.telegram.ingress_attempts` increments
   - `last_ingress.state` becomes `processed` or `queued`
   - `delivery_attempts` increments for a processed user-authored message
   - `last_delivery.state=sent` for a successful reply

## Acceptance Criteria
- The production-owned webhook setter returns `ok=true`.
- A post-repair Telegram update increments production ingress telemetry.
- Production health records `last_ingress.state=processed`.
- Production health records `last_delivery.state=sent`.
- The selected repair is recorded with health evidence.

## Deliverable For This Stage
- verification evidence for the production webhook reset and successful
  Telegram ingress/delivery

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it
- do not print or store Telegram secret values in repository artifacts
- do not drop pending Telegram updates unless the user explicitly accepts the
  risk

## Definition of Done
- [x] Telegram `getWebhookInfo` evidence is captured without leaking secrets.
      Not required for this repair because the production-owned webhook setter
      returned `ok=true` and used configured production secret state.
- [x] Webhook URL and secret posture are verified.
- [x] Real chat-id delivery path is verified.
- [x] Production `/health.conversation_channels.telegram` shows real ingress
      and delivery evidence after repair.
- [x] Context and ops notes are updated with the result and any confirmed
      recurring pitfall.
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
- committing secret values, bot tokens, chat ids, or raw provider payloads with
  private user content

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "telegram" tests/test_delivery_router.py tests/test_telegram_client.py tests/test_runtime_pipeline.py -k "telegram"; Pop-Location`
  - result: `24 passed, 210 deselected`
- Manual checks:
  - `GET https://aviary.luckysparrow.ch/health`
  - `POST https://aviary.luckysparrow.ch/event` API smoke
  - synthetic Telegram-shaped POST without secret
  - `POST https://aviary.luckysparrow.ch/telegram/set-webhook`
- Screenshots/logs:
  - pre-probe production health showed:
    - `status=ok`
    - `release_readiness.ready=true`
    - `conversation_channels.telegram.round_trip_state=provider_backed_ready`
    - `ingress_attempts=0`
    - `delivery_attempts=0`
    - `last_ingress={}`
    - `last_delivery={}`
  - synthetic probe returned:
    - `403 Invalid Telegram webhook secret token.`
  - post-probe health showed:
    - `ingress_attempts=1`
    - `ingress_rejections=1`
    - `last_ingress.state=rejected`
    - `last_ingress.reason=invalid_webhook_secret`
  - webhook reset response:
    - `ok=true`
    - `result=true`
    - `description=Webhook was set`
  - post-repair production health showed:
    - `ingress_attempts=2`
    - `ingress_rejections=1`
    - `ingress_processed=1`
    - `ingress_runtime_failures=0`
    - `delivery_attempts=1`
    - `delivery_successes=1`
    - `delivery_failures=0`
    - `last_ingress.state=processed`
    - `last_ingress.reason=runtime_result_ready`
    - `last_delivery.state=sent`
    - `last_delivery.note=telegram_message_sent`
- High-risk checks:
  - production webhook was reset through the existing server-owned
    `/telegram/set-webhook` route
  - no pending Telegram updates were deleted

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/LEARNING_JOURNAL.md`
  - `docs/operations/runtime-ops-runbook.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - not applicable
- Follow-up architecture doc updates:
  - not expected unless provider checks reveal a contract mismatch

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - not applicable; this is provider/runtime analysis
- Canonical visual target:
  - not applicable
- Fidelity target: structurally_faithful
- Stitch used: no
- Experience-quality bar reviewed: not applicable
- Visual-direction brief reviewed: not applicable
- Existing shared pattern reused:
  - not applicable
- New shared pattern introduced: no
- Design-memory entry reused:
  - not applicable
- Design-memory update required: no
- Visual gap audit completed: not applicable
- Background or decorative asset strategy:
  - not applicable
- Canonical asset extraction required: no
- Screenshot comparison pass completed: not applicable
- Remaining mismatches:
  - not applicable
- State checks: loading | empty | error | success
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: touch | pointer | keyboard
- Accessibility checks:
  - not applicable
- Parity evidence:
  - not applicable

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes:
  - none; existing production bot token and webhook secret were reused
- Health-check impact:
  - `/health.conversation_channels.telegram` now shows real ingress and
    delivery evidence
- Smoke steps updated:
  - production webhook reset was verified through `/telegram/set-webhook` and
    `/health.conversation_channels.telegram`
- Rollback note:
  - restore webhook to the previous `getWebhookInfo.result.url` and secret if
    the repair makes delivery worse

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
The immediate repair did not require printing or locally loading secrets because
the production app already had the bot token and webhook secret configured and
could call Telegram's `setWebhook` through the existing server-owned endpoint.

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
- Loading state verified: not applicable
- Error state verified: yes
- Refresh/restart behavior verified: production health showed successful real
  ingress and delivery after webhook reset
- Regression check performed:
  - focused Telegram API/delivery/runtime regression suite passed

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
  - production runtime was healthy; Telegram traffic was not reaching
    `/event`; resetting the webhook through production `/telegram/set-webhook`
    restored real ingress and delivery
- Files changed:
  - `.codex/tasks/PRJ-773-verify-production-telegram-webhook-and-plan-repair.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - health smoke, API foreground smoke, synthetic Telegram ingress rejection,
    production webhook reset, post-repair health proof, focused regression
    tests
- What is incomplete:
  - dashboard still needs PRJ-770 so this kind of configured-but-silent channel
    state is visible before manual triage
- Next steps:
  - implement PRJ-770 dashboard channel status visibility
- Decisions made:
  - use the existing production-owned webhook setter instead of exposing secrets
    in the local shell
