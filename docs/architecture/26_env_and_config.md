# Environment and Configuration

## Purpose

This document defines how AION manages environment variables and configuration.

Proper configuration ensures:

- security
- flexibility
- safe deployment
- clean separation between code and environment

Without it:

- secrets leak
- runtime behavior becomes inconsistent
- environments drift

---

## Core Principle

Configuration must be external.

Never hardcode:

- API keys
- database credentials
- tokens
- deployment-specific flags

---

## Environment File

Use `.env` for local development.

Example:

```text
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_token
DATABASE_URL=postgresql://user:password@db:5432/aion
APP_ENV=development
APP_PORT=8000
```

---

## Required Variables

### Core

`OPENAI_API_KEY`

Used for LLM calls.

`TELEGRAM_BOT_TOKEN`

Used for Telegram integration.

`DATABASE_URL`

Used for PostgreSQL connection.

`APP_ENV`

Defines runtime environment:

- development
- staging
- production

`APP_PORT`

Defines the FastAPI port.

---

## Optional Variables

`LOG_LEVEL`

Options:

- debug
- info
- warning
- error

`STARTUP_SCHEMA_MODE`

Controls schema bootstrap strategy on startup.

Allowed values:

- migrate
- create_tables

`EVENT_DEBUG_ENABLED`

Controls whether debug runtime payloads may be exposed through the event API.

`EVENT_DEBUG_TOKEN`

Optional debug-access token for debug payload routes
(`POST /event/debug` and compatibility `POST /event?debug=true`).
When set, debug payload responses require `X-AION-Debug-Token` to match.

`EVENT_DEBUG_QUERY_COMPAT_ENABLED`

Controls whether compatibility debug query route `POST /event?debug=true`
remains enabled.

Default behavior is environment-aware:

- non-production default: `true`
- production default: `false`

When disabled, callers must use explicit internal debug route
`POST /event/debug`.

`EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW`

Controls rolling-window size used for compat-route telemetry trend fields in
`/health.runtime_policy`.

Default: `20` (must be at least `1`).

`EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`

Controls when the latest compat-route attempt should be treated as stale in
`/health.runtime_policy` freshness signals.

Default: `86400` (must be at least `1`).

`SEMANTIC_VECTOR_ENABLED`

Controls whether semantic retrieval and embedding persistence use vector
operations.

Default: `true`.

When `false`, runtime retrieval remains lexical-only while keeping the same
hybrid retrieval API surface.

`PRODUCTION_DEBUG_TOKEN_REQUIRED`

Controls whether production debug payload access requires a configured debug
token when debug exposure is enabled.

Default: `true`.

`PRODUCTION_POLICY_ENFORCEMENT`

Controls how production policy mismatches are handled.

Allowed values:

- warn
- strict

`GET /health` runtime policy visibility now includes:

- effective policy flags
- `event_debug_token_required` to indicate whether debug token header is required
- `production_debug_token_required` to indicate whether production requires a
  configured debug token for debug payload access
- `event_debug_query_compat_enabled` to indicate whether compatibility
  `POST /event?debug=true` path is enabled
- `event_debug_query_compat_source` to indicate whether compat-route posture
  comes from explicit config or environment default
- `event_debug_query_compat_telemetry` with in-process compat-route usage
  counters (`attempts_total`, `allowed_total`, `blocked_total`) and last-attempt
  timestamps for sunset-readiness tracking
- `event_debug_query_compat_allow_rate` and
  `event_debug_query_compat_block_rate` to summarize current compat-route
  success/failure split
- `event_debug_query_compat_recommendation` to provide concise compat sunset
  guidance (`compat_disabled`,
  `no_compat_traffic_detected_disable_when_possible`,
  `migrate_clients_before_disabling_compat`)
- `event_debug_query_compat_sunset_ready` and
  `event_debug_query_compat_sunset_reason` to expose explicit machine-readable
  go/no-go sunset posture
  (`compat_disabled|no_compat_attempts_detected|compat_attempts_detected_migration_needed`)
- `event_debug_query_compat_recent_attempts_total`,
  `event_debug_query_compat_recent_allow_rate`,
  `event_debug_query_compat_recent_block_rate`, and
  `event_debug_query_compat_recent_state` to summarize rolling-window compat
  route trend posture (`compat_disabled|no_recent_attempts|mostly_blocked|mixed|mostly_allowed`)
- `event_debug_query_compat_stale_after_seconds`,
  `event_debug_query_compat_last_attempt_age_seconds`, and
  `event_debug_query_compat_last_attempt_state` to expose whether observed
  compat traffic is fresh vs stale
  (`no_attempts_recorded|fresh|stale`)
- `event_debug_query_compat_activity_state` and
  `event_debug_query_compat_activity_hint` to summarize migration activity
  posture (`compat_disabled|no_attempts_observed|stale_historical_attempts|recent_attempts_observed`)
  and next-action guidance
  (`compat_disabled_no_action|can_disable_when_ready|verify_stale_clients_before_disable|keep_compat_until_recent_clients_migrate`)
- `debug_access_posture` to summarize live debug-route access mode
  (`disabled|token_gated|production_token_required_missing|open_no_token`)
- `debug_token_policy_hint` to provide a concise next-action hint for debug
  access hardening posture
- policy source markers (for debug defaults)
- `production_policy_mismatches` preview list for strict-mode rollout safety
  (for example `event_debug_enabled=true`,
  `event_debug_query_compat_enabled=true`, `event_debug_token_missing=true`,
  `startup_schema_mode=create_tables`)
- `production_policy_mismatch_count` for quick triage summary
- `strict_startup_blocked` to indicate current strict-mode startup block state
- `strict_rollout_ready` to indicate no strict-mode mismatches are present
- `recommended_production_policy_enforcement` to guide rollout posture
- `strict_rollout_hint` to provide a concise rollout action summary

`GET /health` also includes `memory_retrieval` posture fields:

- `semantic_vector_enabled`
- `semantic_retrieval_mode`
  (`hybrid_vector_lexical|lexical_only`)

Compatibility route `POST /event?debug=true` also emits:

- `X-AION-Debug-Compat: query_debug_route_is_compatibility_use_post_event_debug`
- `X-AION-Debug-Compat-Deprecated: true`
- `Link: </event/debug>; rel="alternate"`

`REFLECTION_INTERVAL`

Controls background reflection cadence when such scheduling is enabled.

`SCHEDULER_ENABLED`

Enables or disables in-process scheduler cadence for reflection and maintenance
routines.

`MAINTENANCE_INTERVAL`

Controls background maintenance cadence when scheduler execution is enabled.

`PROACTIVE_ENABLED`

Enables or disables proactive system behavior when that subsystem exists.

`PROACTIVE_INTERVAL`

Controls proactive cadence when proactive runtime behavior is enabled.

`ATTENTION_BURST_WINDOW_MS`

Controls the short coalescing window for bursty Telegram user messages.
Lower values reduce wait time before processing; higher values increase
coalescing tolerance.

`ATTENTION_ANSWERED_TTL_SECONDS`

Controls how long answered turn records stay in memory before cleanup.
Must be at least `0.5`.

`ATTENTION_STALE_TURN_SECONDS`

Controls when pending or claimed turns are treated as stale and evicted.
Must be greater than or equal to `ATTENTION_ANSWERED_TTL_SECONDS`.

---

## Configuration Loading

Use a central config loader in Python.

Recommended shape:

- pydantic settings
- environment variable loading
- startup-time validation

Config should be loaded once at startup and passed through the app as a shared runtime object.

---

## Config Structure (Example)

Logical groups:

- api_keys
- database
- runtime
- features
- policy

Example object:

```json
{
  "api_keys": {
    "openai": "...",
    "telegram": "..."
  },
  "database": {
    "url": "..."
  },
  "runtime": {
    "env": "development",
    "port": 8000,
    "log_level": "info"
  },
  "policy": {
    "startup_schema_mode": "migrate",
    "event_debug_enabled": true,
    "production_policy_enforcement": "warn"
  }
}
```

---

## Environment Separation

Different environments must use different configuration values.

### Development

- local database
- local secrets
- verbose logging
- permissive debugging

### Staging

- production-like configuration
- safe but realistic validation path

### Production

- real secrets
- explicit policy posture
- minimal debug exposure
- safe startup behavior

---

## Secrets Management

Never:

- commit `.env` to Git
- expose secrets in logs
- place secrets in docs or sample payloads

Use:

- `.env` locally
- environment variables in deployment
- secret management tooling when infrastructure matures

---

## Docker Integration

Pass variables via:

- `docker-compose.yml`
- deployment environment configuration

Example:

```yaml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - DATABASE_URL=${DATABASE_URL}
```

---

## Validation

At startup, the system should:

- validate required variables
- fail fast when critical config is missing
- expose only safe policy visibility
- log clear configuration errors

---

## Default Values

Only safe defaults should exist for:

- port
- log level
- non-secret runtime behavior

Never provide silent defaults for:

- API keys
- database credentials
- externally sensitive production behavior

---

## Feature Flags

Configuration may enable or disable subsystems such as:

- reflection loop
- proactive behavior
- debug payload exposure

Feature flags must remain explicit and discoverable.

---

## Runtime Access

All modules should access configuration through:

- a central config object
- injected app state
- typed runtime settings

Not by reading environment variables ad hoc throughout the codebase.

---

## Logging Config

Config should define:

- log level
- structured logging posture
- debug exposure posture
- production policy handling

---

## Future Extensions

- config versioning
- remote config service
- dynamic reload for selected flags

---

## Final Principle

Configuration separates the system from its environment.

If config is clean:

- deployment is safer
- runtime policy is inspectable
- debugging is easier

If config is messy, the whole runtime becomes fragile.
