# AION Backend

This directory contains the current production runtime for AION / Personality.

Implemented scope:

- FastAPI API with `POST /event`
- first-party auth/session endpoints under `/app/auth/*`
- first-party app endpoints for `/app/me`, `/app/chat/*`, and `/app/personality/overview`
- event normalization (`event_id`, `trace_id`, timestamp)
- runtime pipeline, memory, reflection, cadence workers, and delivery routing
- Telegram webhook compatibility
- PostgreSQL persistence and Alembic migrations
- Dockerized runtime image used by local compose and Coolify deploys

## Local Backend Workflow

Run tests from the backend working directory:

```powershell
Push-Location .\backend
..\.venv\Scripts\python -m pytest -q
Pop-Location
```

Apply migrations directly when needed:

```powershell
Push-Location .\backend
..\.venv\Scripts\python -m alembic -c alembic.ini upgrade head
Pop-Location
```

Helper scripts live under `backend/scripts/` and are intended to be executed
from the repository root, for example:

```powershell
.\backend\scripts\setup_windows.ps1
.\backend\scripts\generate_telegram_webhook_secret.ps1 -UpdateEnv
.\backend\scripts\run_release_smoke.ps1 -BaseUrl "http://localhost:8000"
```

## Production Image

The production image is still built from the root `docker/Dockerfile`, but it
installs and runs the package from `backend/`.

## First-Party Client Surfaces

Current app-facing backend surfaces for `web/` and later `mobile/`:

- `POST /app/auth/register`
- `POST /app/auth/login`
- `POST /app/auth/logout`
- `GET /app/me`
- `PATCH /app/me/settings`
- `GET /app/chat/history`
- `POST /app/chat/message`
- `GET /app/personality/overview`
