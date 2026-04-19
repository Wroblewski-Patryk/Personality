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

`GET /health` now includes a `runtime_policy` object with non-secret active
runtime flags (for example `startup_schema_mode`, `event_debug_enabled`, and
`event_debug_source`) plus debug-route posture markers
(`event_debug_token_required`, `production_debug_token_required`,
`event_debug_query_compat_enabled`, `event_debug_query_compat_source`,
`event_debug_query_compat_telemetry`,
`event_debug_query_compat_allow_rate`,
`event_debug_query_compat_block_rate`,
`event_debug_query_compat_recommendation`,
`event_debug_query_compat_sunset_ready`,
`event_debug_query_compat_sunset_reason`,
`event_debug_query_compat_recent_attempts_total`,
`event_debug_query_compat_recent_allow_rate`,
`event_debug_query_compat_recent_block_rate`,
`event_debug_query_compat_recent_state`,
`event_debug_query_compat_stale_after_seconds`,
`event_debug_query_compat_last_attempt_age_seconds`,
`event_debug_query_compat_last_attempt_state`,
`event_debug_query_compat_activity_state`,
`event_debug_query_compat_activity_hint`, `debug_access_posture`,
`debug_token_policy_hint`) plus
strict-rollout readiness signals
(`production_policy_mismatches`, `production_policy_mismatch_count`,
`strict_startup_blocked`, and `strict_rollout_ready`) plus rollout guidance
signals (`recommended_production_policy_enforcement`, `strict_rollout_hint`),
so operators can verify active policy posture, detect strict-mode startup
risks, assess strict-rollout readiness, and track compatibility-route sunset
readiness during incident triage and release smoke.
Observed compat attempts now always keep sunset recommendation in
`migrate_clients_before_disabling_compat` until clients are moved away from
`POST /event?debug=true`.
Compat activity posture fields now distinguish disabled/no-traffic/stale-history
vs recent traffic so migration windows can separate historical noise from active
compat dependency.

`GET /health` also includes a `scheduler` object with cadence posture
(`enabled`, `running`, interval settings) and latest reflection/maintenance
tick summaries.

`GET /health` now also includes an `attention` object with burst-turn assembly
posture (`burst_window_ms`, `answered_ttl_seconds`, `stale_turn_seconds`) and
live turn counters (`pending`, `claimed`, `answered`) to support burst-message
triage and operator verification of attention gate behavior.

`GET /health` now also includes a `memory_retrieval` object with semantic
retrieval posture:

- `semantic_vector_enabled`
- `semantic_retrieval_mode` (`hybrid_vector_lexical|lexical_only`)
- `semantic_embedding_provider_ready`
- `semantic_embedding_posture` (`ready|fallback_deterministic`)
- `semantic_embedding_provider_requested`
- `semantic_embedding_provider_effective`
- `semantic_embedding_provider_hint`
- `semantic_embedding_model_requested`
- `semantic_embedding_model_effective`
- `semantic_embedding_dimensions`
- `semantic_embedding_warning_state`
- `semantic_embedding_warning_hint`
- `semantic_embedding_source_kinds`

When semantic vectors are enabled and a non-implemented provider is requested
(for example `EMBEDDING_PROVIDER=openai` today), startup emits
`embedding_strategy_warning` with requested/effective provider-model posture
and deterministic fallback hint.

On startup, production now emits an explicit warning when
`EVENT_DEBUG_ENABLED=true`. Treat this warning as a release-hardening signal:
disable debug payload exposure in production unless there is a short-lived,
intentional incident-debug window.

When production debug payload exposure is enabled without `EVENT_DEBUG_TOKEN`
and `PRODUCTION_DEBUG_TOKEN_REQUIRED=true`, startup emits a warning
recommending token configuration for debug access hardening.

When production debug payload exposure is enabled with
`PRODUCTION_DEBUG_TOKEN_REQUIRED=false`, startup also emits a warning so
relaxed debug-token hardening posture is explicit to operators.

When production debug payload exposure is enabled and compatibility
`POST /event?debug=true` route is also explicitly enabled
(`EVENT_DEBUG_QUERY_COMPAT_ENABLED=true`), startup emits a warning to keep
compatibility-surface hardening visible.

On startup, production also emits an explicit warning when
`STARTUP_SCHEMA_MODE=create_tables`. Treat this as a temporary compatibility
path warning: production should normally run migration-first startup mode.

`PRODUCTION_POLICY_ENFORCEMENT` controls whether these production-policy
mismatches are warning-only (`warn`, default) or startup-blocking (`strict`).
Use `strict` when production hardening requires fail-fast policy enforcement.
Current debug-related mismatch examples include
`event_debug_enabled=true`, `event_debug_query_compat_enabled=true`, and
`event_debug_token_missing=true`.

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
- `EVENT_DEBUG_ENABLED` to control whether debug payload routes
  (`POST /event/debug` and compatibility `POST /event?debug=true`) can expose
  full internal runtime payloads (production default is disabled unless
  explicitly enabled)
- `EVENT_DEBUG_TOKEN` (optional) to require `X-AION-Debug-Token` for
  debug payload route access
- `EVENT_DEBUG_QUERY_COMPAT_ENABLED` (optional) to explicitly enable or disable
  compatibility `POST /event?debug=true` route (production default is disabled)
- `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` (optional, default `20`) to control
  rolling-window size used by compat-route trend telemetry
- `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS` (optional, default `86400`)
  to control stale-age threshold used by compat-route freshness telemetry
- `SEMANTIC_VECTOR_ENABLED` (optional, default `true`) to toggle semantic
  vector retrieval/persistence posture (`true` for hybrid vector+lexical,
  `false` for lexical-only)
- `EMBEDDING_PROVIDER` (optional, default `deterministic`) to declare requested
  embedding provider posture (`openai` currently falls back to deterministic)
- `EMBEDDING_MODEL` (optional, default `deterministic-v1`) to configure
  requested embedding model posture
- `EMBEDDING_DIMENSIONS` (optional, default `32`) to control embedding/query
  vector dimensions
- `EMBEDDING_SOURCE_KINDS` (optional, default
  `episodic,semantic,affective`) to control which memory families persist
  embedding records (`episodic|semantic|affective|relation`)
- `PRODUCTION_DEBUG_TOKEN_REQUIRED` (`true|false`, default `true`) to require
  a configured debug token for production debug payload access when debug
  exposure is enabled
- `PRODUCTION_POLICY_ENFORCEMENT` (`warn|strict`) to decide whether production
  policy mismatches remain warning-only or block startup
- `ATTENTION_BURST_WINDOW_MS` (optional) to tune burst-message coalescing
  latency and aggregation behavior
- `ATTENTION_ANSWERED_TTL_SECONDS` and `ATTENTION_STALE_TURN_SECONDS` (optional)
  to tune in-memory turn lifecycle cleanup behavior

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
.\scripts\run_release_smoke.ps1 -BaseUrl "http://localhost:8000" -IncludeDebug
```

Optional debug payload with token:

```powershell
curl -X POST "http://localhost:8000/event/debug" `
  -H "Content-Type: application/json" `
  -H "X-AION-Debug-Token: <token>" `
  -d "{\"text\":\"debug check\"}"
```

Compatibility debug payload with token:

```powershell
curl -X POST "http://localhost:8000/event?debug=true" `
  -H "Content-Type: application/json" `
  -H "X-AION-Debug-Token: <token>" `
  -d "{\"text\":\"debug check\"}"
```

When compat route is accepted, response includes compatibility/deprecation
headers that point to `POST /event/debug` as the preferred internal path.

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

For multi-user API traffic, prefer sending `X-AION-User-Id` (or explicit
`meta.user_id` in payload) so profile and memory signals stay user-scoped
instead of defaulting to shared `anonymous` state.

Use the smoke helper when you want a repeatable operator check instead of crafting requests manually.

### Configure Telegram Webhook

Use the helper script or call:

`POST /telegram/set-webhook`

with a webhook URL and optional secret token.

## Known Operational Limits

- there is no background queue or worker isolation yet
- reflection is durable and scheduler cadence is now available in-process, but
  neither reflection nor scheduler is isolated into a separate worker process yet
- startup now defaults to migration-first schema ownership; `create_tables()` remains only as a compatibility path behind `STARTUP_SCHEMA_MODE=create_tables`
- runtime logging is present, but there is no external observability stack yet
- proactive systems are still architectural intent, not live ops surfaces

## Incident Triage Shortlist

If a request path fails:

1. check whether the app booted with valid env vars
2. verify Postgres health and connection string
3. confirm whether OpenAI fallback behavior is acceptable for the failing scenario
4. for Telegram issues, verify webhook secret, bot token, and `chat_id` presence
5. inspect structured logs for `event_id`, `trace_id`, and action status
