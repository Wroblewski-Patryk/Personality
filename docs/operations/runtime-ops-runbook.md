# Runtime Ops Runbook

## Scope

This runbook covers the currently implemented AION MVP service, not the full long-term architecture described in the numbered docs.

## Service Responsibilities

- accept incoming events through FastAPI
- normalize incoming payloads
- run the in-process orchestration pipeline
- persist short-term episode memory in PostgreSQL
- optionally send Telegram replies
- optionally generate replies with OpenAI

## Health And Readiness

- App health endpoint:
  - `GET /health`
- Docker compose stack includes health checks for Postgres and, in the Coolify variant, the app container.

## Required Environment Variables

- `DATABASE_URL`
- `APP_ENV`
- `APP_PORT`
- `LOG_LEVEL`

Production-only required in practice:

- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`

Recommended when Telegram webhooks are enabled:

- `TELEGRAM_WEBHOOK_SECRET`

## Common Operator Flows

### Start Local Stack

```powershell
docker compose up --build
```

### Run Repeatable Manual Smoke

Windows PowerShell:

```powershell
.\scripts\run_release_smoke.ps1 -BaseUrl "http://localhost:8000"
```

Windows PowerShell with UTF-8 payload check:

```powershell
.\scripts\run_release_smoke.ps1 `
  -BaseUrl "http://localhost:8000" `
  -Text "zażółć gęślą jaźń"
```

Debian / bash:

```bash
./scripts/run_release_smoke.sh "http://localhost:8000"
```

Optional debug payload:

```powershell
.\scripts\run_release_smoke.ps1 -BaseUrl "http://localhost:8000" -Debug
```

### Run Health Check

```powershell
curl http://localhost:8000/health
```

### Send Manual Event

```powershell
curl -X POST http://localhost:8000/event `
  -H "Content-Type: application/json" `
  -d "{\"text\":\"hello AION\"}"
```

Use the smoke helper when you want a repeatable operator check instead of crafting requests manually.

### Configure Telegram Webhook

Use the helper script or call:

`POST /telegram/set-webhook`

with a webhook URL and optional secret token.

## Known Operational Limits

- there is no background queue or worker isolation yet
- reflection is durable but still app-local, not isolated into a separate worker process yet
- startup table creation still coexists with the new Alembic baseline during the current migration transition
- runtime logging is present, but there is no external observability stack yet
- proactive systems are still architectural intent, not live ops surfaces

## Incident Triage Shortlist

If a request path fails:

1. check whether the app booted with valid env vars
2. verify Postgres health and connection string
3. confirm whether OpenAI fallback behavior is acceptable for the failing scenario
4. for Telegram issues, verify webhook secret, bot token, and `chat_id` presence
5. inspect structured logs for `event_id`, `trace_id`, and action status
