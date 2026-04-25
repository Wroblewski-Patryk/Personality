# Local Development

## Prerequisites

- Python 3.11+
- Node.js 22+ with npm
- Docker Desktop or another local Docker environment
- PowerShell on Windows for the provided helper scripts

## Recommended Setup On Windows

1. Create the virtual environment and install dependencies:

```powershell
.\backend\scripts\setup_windows.ps1
```

2. Fill required values in `.env`:

- `DATABASE_URL`
- `OPENAI_API_KEY` if OpenAI replies should be enabled
- `TELEGRAM_BOT_TOKEN` if Telegram delivery should be enabled
- `TELEGRAM_WEBHOOK_SECRET` for webhook protection
- `EVENT_DEBUG_ENABLED` (optional) to override debug payload exposure:
  - default in local/non-production is enabled
  - production default is disabled unless explicitly enabled
- `EVENT_DEBUG_TOKEN` (optional) to require `X-AION-Debug-Token` for
  debug payload routes (`POST /event/debug` and `POST /event?debug=true`)
- `EVENT_DEBUG_QUERY_COMPAT_ENABLED` (optional) to control compatibility
  `POST /event?debug=true` route:
  - default in local/non-production is enabled
  - production default is disabled unless explicitly enabled
- `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` (optional, default `20`) to tune
  rolling-window size for compat-route trend telemetry in `/health`
- `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS` (optional, default `86400`)
  to tune when last compat-route attempt is marked as stale in `/health`
- `SEMANTIC_VECTOR_ENABLED` (optional, default `true`) to switch semantic
  retrieval between `hybrid_vector_lexical` and `lexical_only` modes
- `EMBEDDING_PROVIDER` (optional, default `deterministic`) to declare requested
  embedding provider posture (`deterministic|local_hybrid|openai`)
- `EMBEDDING_MODEL` (optional, default `deterministic-v1`) to set requested
  embedding model posture for runtime visibility
- `EMBEDDING_DIMENSIONS` (optional, default `32`) to tune embedding/query
  vector dimensions
- `EMBEDDING_SOURCE_KINDS` (optional, default
  `episodic,semantic,affective`) to control which memory families persist
  embedding records (`episodic|semantic|affective|relation`)
- `EMBEDDING_REFRESH_MODE` (optional, default `on_write`) to declare embedding
  refresh ownership posture (`on_write|manual`)
- `EMBEDDING_REFRESH_INTERVAL_SECONDS` (optional, default `21600`) to declare
  expected embedding refresh cadence interval in seconds (must be at least
  `60`)
- `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` (optional, default `warn`) to
  decide whether provider-ownership fallback stays warning-only or blocks
  startup (`warn|strict`)
- `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` (optional, default `warn`) to
  decide whether deterministic custom-model-name governance posture stays
  warning-only or blocks startup (`warn|strict`)
- `PRODUCTION_DEBUG_TOKEN_REQUIRED` (optional, default `true`) to enforce
  debug-token configuration for production debug payload access
- `ATTENTION_BURST_WINDOW_MS` (optional) to tune Telegram burst coalescing
  latency
- `ATTENTION_ANSWERED_TTL_SECONDS` and `ATTENTION_STALE_TURN_SECONDS`
  (optional) to tune in-memory turn lifecycle cleanup behavior

3. Run tests:

```powershell
Push-Location .\backend
..\.venv\Scripts\python -m pytest -q
Pop-Location
```

4. Start the local stack:

```powershell
docker compose up --build
```

5. Start the browser client in dev mode when working on `web/`:

```powershell
Push-Location .\web
npm install
npm run dev
Pop-Location
```

Notes for local product development:

- Vite proxies `/app`, `/health`, `/event`, and `/internal` to
  `http://127.0.0.1:8000`
- the backend can therefore keep same-origin-style API calls in `web/`
- production serving comes from the backend image after `web/dist` is built

## Database Migrations

The repo now has an Alembic baseline for the current schema.

Recommended local command:

```powershell
.\backend\scripts\run_db_migrations.ps1
```

Equivalent direct command:

```powershell
.\.venv\Scripts\python -m alembic -c .\backend\alembic.ini upgrade head
```

Important current behavior:

- startup defaults to migration-first schema ownership (`STARTUP_SCHEMA_MODE=migrate`)
- Alembic is the formal path for schema evolution
- compatibility bootstrap still exists behind `STARTUP_SCHEMA_MODE=create_tables` and should only be used for controlled fallback scenarios

## Useful Commands

Run app locally with Docker:

```powershell
docker compose up --build
```

Run tests inside the virtual environment:

```powershell
Push-Location .\backend
..\.venv\Scripts\python -m pytest -q
Pop-Location
```

Build the web workspace:

```powershell
Push-Location .\web
npm run build
Pop-Location
```

Generate a Telegram webhook secret and optionally update `.env`:

```powershell
.\backend\scripts\generate_telegram_webhook_secret.ps1 -UpdateEnv
```

Set the Telegram webhook:

```powershell
.\backend\scripts\set_telegram_webhook.ps1 -WebhookUrl https://your-host.example/event
```

## Local Verification

- Health check:

```powershell
curl http://localhost:8000/health
```

- Sample event:

```powershell
curl -X POST http://localhost:8000/event `
  -H "Content-Type: application/json" `
  -d "{\"text\":\"hello AION\"}"
```

- Sample event with explicit API user identity (recommended for multi-user API
  usage):

```powershell
curl -X POST http://localhost:8000/event `
  -H "Content-Type: application/json" `
  -H "X-AION-User-Id: demo-user-42" `
  -d "{\"text\":\"hello AION\"}"
```

- Sample explicit debug event with token (when `EVENT_DEBUG_TOKEN` is configured):

```powershell
curl -X POST "http://localhost:8000/event/debug" `
  -H "Content-Type: application/json" `
  -H "X-AION-Debug-Token: your-debug-token" `
  -d "{\"text\":\"debug hello\"}"
```

- Compatibility debug event with token (same policy gate):

```powershell
curl -X POST "http://localhost:8000/event?debug=true" `
  -H "Content-Type: application/json" `
  -H "X-AION-Debug-Token: your-debug-token" `
  -d "{\"text\":\"debug hello\"}"
```

Compat responses include headers that mark migration posture:
`X-AION-Debug-Compat`, `X-AION-Debug-Compat-Deprecated`, and `Link`.

In production, `POST /event?debug=true` is disabled by default; set
`EVENT_DEBUG_QUERY_COMPAT_ENABLED=true` only for short-lived migration windows.

## Troubleshooting

- If startup fails immediately, check missing environment variables first.
- If OpenAI replies fall back to echo behavior, verify `OPENAI_API_KEY`.
- If Telegram delivery fails, confirm `chat_id` is present in the normalized event and that the bot token is valid.
- If database access fails, verify `DATABASE_URL` and whether the Postgres container is healthy.
