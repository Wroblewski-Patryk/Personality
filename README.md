# AION - MVP Iteration 1

This repository contains the first working implementation of the AION runtime loop.

Implemented scope:
- FastAPI API with `POST /event`
- Event normalization (`event_id`, `trace_id`, timestamp)
- Minimal runtime pipeline
- Telegram webhook compatibility
- PostgreSQL memory write and retrieval
- Dockerized app + database

## Quick Start

1. Copy env template:

```bash
cp .env.example .env
```

2. Fill required variables in `.env`:
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional, defaults to `gpt-4o-mini`)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET` (recommended)
- `DATABASE_URL`

Generate webhook secret automatically:

```powershell
.\scripts\generate_telegram_webhook_secret.ps1 -UpdateEnv
```

3. Start with Docker:

```bash
docker compose up --build
```

4. Health check:

```bash
curl http://localhost:8000/health
```

5. Send test event:

```bash
curl -X POST http://localhost:8000/event ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"hello AION\"}"
```

## API Endpoints

- `GET /health`
- `POST /event`
  - default response: stable public reply payload
  - optional debug payload: `POST /event?debug=true`
- `POST /telegram/set-webhook`

Manual smoke helper:

```powershell
.\scripts\run_release_smoke.ps1 -BaseUrl "http://localhost:8000"
```

## Local Windows Environment

```powershell
.\scripts\setup_windows.ps1
.\.venv\Scripts\python -m pytest -q
```

Apply the current schema baseline explicitly:

```powershell
.\scripts\run_db_migrations.ps1
```

Optional pip upgrade:

```powershell
.\scripts\setup_windows.ps1 -UpgradePip
```

## Coolify Deployment

Use `docker-compose.coolify.yml` in Coolify and configure env vars in the Coolify UI.

Full guide:
- `docs/28_local_windows_and_coolify_deploy.md`
