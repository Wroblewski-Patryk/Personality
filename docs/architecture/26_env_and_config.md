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

Target posture:

- production baseline uses `migrate`
- `create_tables` is a temporary compatibility path pending
  `PRJ-306` removal guardrail satisfaction

`EVENT_DEBUG_ENABLED`

Controls whether debug runtime payloads may be exposed through the event API.

`EVENT_DEBUG_TOKEN`

Optional debug-access token for debug payload routes
(`POST /internal/event/debug`, shared compatibility `POST /event/debug`, and
compatibility query route `POST /event?debug=true`).
When set, debug payload responses require `X-AION-Debug-Token` to match.

`EVENT_DEBUG_QUERY_COMPAT_ENABLED`

Controls whether compatibility debug query route `POST /event?debug=true`
remains enabled.

Default behavior is environment-aware:

- non-production default: `true`
- production default: `false`

When disabled, callers must use explicit internal debug route
`POST /internal/event/debug` (shared `POST /event/debug` remains a transitional
compatibility path).

`EVENT_DEBUG_SHARED_INGRESS_MODE`

Controls shared-endpoint debug posture for `POST /event/debug`.

Allowed values:

- `compatibility` (default): shared endpoint remains available as compatibility
  ingress and emits migration headers.
- `break_glass_only`: shared endpoint requires explicit
  `X-AION-Debug-Break-Glass: true` override for emergency usage while keeping
  internal ingress (`POST /internal/event/debug`) as primary path.

`EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW`

Controls rolling-window size used for compat-route telemetry trend fields in
`/health.runtime_policy`.

Default: `20` (must be at least `1`).

`EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`

Controls when the latest compat-route attempt should be treated as stale in
`/health.runtime_policy` freshness signals.

Default: `86400` (must be at least `1`).

`CLICKUP_API_TOKEN`

Optional provider credential for the first live connector execution path.

When both `CLICKUP_API_TOKEN` and `CLICKUP_LIST_ID` are configured, action may
execute `task_system:create_task` for `provider_hint=clickup` through the
provider-backed ClickUp adapter.

`CLICKUP_LIST_ID`

Optional ClickUp list target for the first live connector execution path.

Without both ClickUp fields present, `/health.connectors.execution_baseline`
must remain in `credentials_missing` posture and task-system execution stays
policy-only at runtime.

`SEMANTIC_VECTOR_ENABLED`

Controls whether semantic retrieval and embedding persistence use vector
operations.

Default: `true`.

When `false`, runtime retrieval remains lexical-only while keeping the same
hybrid retrieval API surface.

When `DATABASE_URL` targets PostgreSQL and semantic vectors remain enabled, the
runtime also requires the Python `pgvector` package at startup. AION now
blocks startup before database initialization if PostgreSQL vector retrieval is
configured without that runtime binding, because foreground `/event`
processing would otherwise fail even while `/health` still appears healthy.

`EMBEDDING_PROVIDER`

Controls which embedding provider is requested by runtime configuration.

Allowed values:

- `deterministic` (explicit compatibility baseline)
- `local_hybrid` (local provider-owned transition path)
- `openai` (target provider-owned production baseline when `OPENAI_API_KEY`
  is configured)

Default: `deterministic`.

`EMBEDDING_MODEL`

Requested embedding model identifier for embedding strategy posture.

Default: `deterministic-v1`.

`EMBEDDING_DIMENSIONS`

Embedding vector dimensions used by deterministic baseline and query vectors.

Default: `32` (must be at least `1`).

`EMBEDDING_SOURCE_KINDS`

Comma-separated list of memory source families that should persist embedding
records.

Allowed kinds:

- `episodic`
- `semantic`
- `affective`
- `relation`

Default: `episodic,semantic,affective`.

`EMBEDDING_REFRESH_MODE`

Controls embedding refresh cadence ownership posture.

Allowed values:

- `on_write`
- `manual`

Default: `on_write`.

`EMBEDDING_REFRESH_INTERVAL_SECONDS`

Expected embedding refresh cadence interval in seconds.

Default: `21600` (must be at least `60`).

`EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT`

Controls whether provider-ownership fallback posture is warning-only or
startup-blocking.

Allowed values:

- `warn`
- `strict`

Default: `warn`.

`EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT`

Controls whether deterministic custom-model-name governance posture is
warning-only or startup-blocking.

Allowed values:

- `warn`
- `strict`

Default: `warn`.

`EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT`

Controls whether pending source-rollout posture is warning-only or
startup-blocking.

Allowed values:

- `warn`
- `strict`

Default: `warn`.

### Production Retrieval Baseline (PRJ-476)

The production retrieval baseline for rollout is:

- provider ownership baseline:
  - `openai` is the target provider-owned production baseline when
    `OPENAI_API_KEY` is configured
  - `local_hybrid` remains an explicit local transition path, not the target
    production owner
  - `deterministic` remains the explicit compatibility fallback baseline
- refresh ownership baseline:
  - `on_write` owns materialization during rollout; `manual` remains explicit
    operator override
- family rollout order:
  - `episodic+semantic` baseline first, then `affective`, then `relation`
- enforcement posture:
  - keep source-rollout enforcement aligned with pending rollout phases, and
    move to strict-only recommendation once relation rollout is complete

`PRODUCTION_DEBUG_TOKEN_REQUIRED`

Controls whether production debug payload access requires a configured debug
token when debug exposure is enabled.

Default: `true`.

`PRODUCTION_POLICY_ENFORCEMENT`

Controls how production policy mismatches are handled.

Allowed values:

- warn
- strict

Default resolution:

- production: `strict`
- non-production: `warn`
- explicit `PRODUCTION_POLICY_ENFORCEMENT` keeps override ownership

### Target Production Policy Baseline (PRJ-296)

Target production posture is:

- `STARTUP_SCHEMA_MODE=migrate`
- `PRODUCTION_POLICY_ENFORCEMENT=strict`
- `EVENT_DEBUG_ENABLED=false`
- `EVENT_DEBUG_QUERY_COMPAT_ENABLED=false`
- `PRODUCTION_DEBUG_TOKEN_REQUIRED=true`

This target baseline defines release intent.
Runtime now applies production-aware strict default enforcement for this
baseline while keeping explicit `warn` override as a controlled escape hatch.
`/health.runtime_policy` mismatch diagnostics remain the canonical drift signal.

### Internal Debug Ingress Boundary (PRJ-307)

Target ingress contract:

- public API ingress keeps compact response posture and must not expose full
  runtime payloads
- full debug payload access belongs to a dedicated internal/admin ingress
  boundary, not the shared public API endpoint
- temporary production debug windows remain token-gated and explicitly
  time-bounded

Current transitional posture:

- `POST /internal/event/debug` is now the explicit primary internal debug
  ingress for full runtime payload inspection
- shared `POST /event/debug` is still served by the same app endpoint as
  public API traffic and remains a compatibility surface during migration
- shared ingress posture is explicitly configurable
  (`EVENT_DEBUG_SHARED_INGRESS_MODE=compatibility|break_glass_only`)
- deprecated compatibility `POST /event?debug=true` remains migration-only and
  should stay disabled in production baseline

### `create_tables` Removal Criteria (PRJ-306)

Compatibility `STARTUP_SCHEMA_MODE=create_tables` should be removed only after:

- production and pre-production run migration-only startup with no active
  exceptions
- release windows show empty `runtime_policy.production_policy_mismatches`
  for startup-schema posture in consecutive releases
- migration smoke and release smoke are validated as the only bootstrap path
- runbook rollback no longer depends on `create_tables` as a fallback

`GET /health` runtime policy visibility now includes:

- effective policy flags
- `event_debug_token_required` to indicate whether debug token header is required
- `production_debug_token_required` to indicate whether production requires a
  configured debug token for debug payload access
- `event_debug_query_compat_enabled` to indicate whether compatibility
  `POST /event?debug=true` path is enabled
- `event_debug_query_compat_source` to indicate whether compat-route posture
  comes from explicit config or environment default
- `event_debug_ingress_owner` to describe internal-vs-shared ingress ownership
  posture
- `event_debug_internal_ingress_path` and `event_debug_shared_ingress_path` to
  expose canonical debug route path ownership
- `event_debug_shared_ingress_mode`,
  `event_debug_shared_ingress_break_glass_required`, and
  `event_debug_shared_ingress_posture` to expose final shared-route
  compatibility versus break-glass posture
- `startup_schema_compatibility_posture`,
  `startup_schema_compatibility_sunset_ready`, and
  `startup_schema_compatibility_sunset_reason` to expose whether migration-only
  bootstrap is already in removal-ready posture
- `event_debug_shared_ingress_sunset_ready` and
  `event_debug_shared_ingress_sunset_reason` to expose whether shared debug
  ingress is already retired from normal production use
- `compatibility_sunset_ready` and `compatibility_sunset_blockers` to expose
  aggregate readiness for scheduling actual compatibility-path removal windows
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
- `release_readiness` gate snapshot (`ready`, `violations`) derived from
  runtime-policy release guardrails for smoke automation

`GET /health` also includes `memory_retrieval` posture fields:

- `semantic_vector_enabled`
- `semantic_retrieval_mode`
  (`hybrid_vector_lexical|lexical_only`)
- `semantic_embedding_provider_ready`
- `semantic_embedding_posture`
  (`ready|fallback_deterministic`)
- `semantic_embedding_provider_requested`
- `semantic_embedding_provider_effective`
- `semantic_embedding_provider_hint`
- `semantic_embedding_execution_class`
- `semantic_embedding_production_baseline`
- `semantic_embedding_production_baseline_state`
- `semantic_embedding_production_baseline_hint`
- `semantic_embedding_provider_ownership_state`
- `semantic_embedding_provider_ownership_hint`
- `semantic_embedding_provider_ownership_enforcement`
- `semantic_embedding_provider_ownership_enforcement_state`
- `semantic_embedding_provider_ownership_enforcement_hint`
- `semantic_embedding_owner_strategy_state`
- `semantic_embedding_owner_strategy_hint`
- `semantic_embedding_owner_strategy_recommendation`
- `semantic_embedding_model_requested`
- `semantic_embedding_model_effective`
- `semantic_embedding_model_governance_state`
- `semantic_embedding_model_governance_hint`
- `semantic_embedding_model_governance_enforcement`
- `semantic_embedding_model_governance_enforcement_state`
- `semantic_embedding_model_governance_enforcement_hint`
- `semantic_embedding_strict_rollout_violations`
- `semantic_embedding_strict_rollout_violation_count`
- `semantic_embedding_strict_rollout_ready`
- `semantic_embedding_strict_rollout_state`
- `semantic_embedding_strict_rollout_hint`
- `semantic_embedding_strict_rollout_recommendation`
- `semantic_embedding_recommended_provider_ownership_enforcement`
- `semantic_embedding_recommended_model_governance_enforcement`
- `semantic_embedding_provider_ownership_enforcement_alignment`
- `semantic_embedding_model_governance_enforcement_alignment`
- `semantic_embedding_enforcement_alignment_state`
- `semantic_embedding_enforcement_alignment_hint`
- `semantic_embedding_dimensions`
- `semantic_embedding_warning_state`
- `semantic_embedding_warning_hint`
- `semantic_embedding_source_kinds`
- `semantic_embedding_source_coverage_state`
- `semantic_embedding_source_coverage_hint`
- `semantic_embedding_source_rollout_state`
- `semantic_embedding_source_rollout_hint`
- `semantic_embedding_source_rollout_recommendation`
- `semantic_embedding_source_rollout_order`
- `semantic_embedding_source_rollout_enabled_sources`
- `semantic_embedding_source_rollout_missing_sources`
- `semantic_embedding_source_rollout_next_source_kind`
- `semantic_embedding_source_rollout_completion_state`
- `semantic_embedding_source_rollout_phase_index`
- `semantic_embedding_source_rollout_phase_total`
- `semantic_embedding_source_rollout_progress_percent`
- `semantic_embedding_source_rollout_enforcement`
- `semantic_embedding_source_rollout_enforcement_state`
- `semantic_embedding_source_rollout_enforcement_hint`
- `semantic_embedding_recommended_source_rollout_enforcement`
- `semantic_embedding_source_rollout_enforcement_alignment`
- `semantic_embedding_source_rollout_enforcement_alignment_state`
- `semantic_embedding_source_rollout_enforcement_alignment_hint`
- `semantic_embedding_refresh_mode`
- `semantic_embedding_refresh_interval_seconds`
- `semantic_embedding_refresh_state`
- `semantic_embedding_refresh_hint`
- `semantic_embedding_refresh_cadence_state`
- `semantic_embedding_refresh_cadence_hint`
- `semantic_embedding_recommended_refresh_mode`
- `semantic_embedding_refresh_alignment_state`
- `semantic_embedding_refresh_alignment_hint`

Compatibility route `POST /event?debug=true` also emits:

- `X-AION-Debug-Compat: query_debug_route_is_compatibility_use_internal_event_debug`
- `X-AION-Debug-Compat-Deprecated: true`
- `Link: </internal/event/debug>; rel="alternate"`

Shared compatibility route `POST /event/debug` emits:

- `X-AION-Debug-Shared-Compat: shared_debug_route_is_compatibility_use_internal_event_debug`
- `X-AION-Debug-Shared-Compat-Deprecated: true`
- `X-AION-Debug-Shared-Mode: compatibility|break_glass_only`
- `X-AION-Debug-Shared-Posture: shared_route_compatibility|shared_route_break_glass_only`

`REFLECTION_INTERVAL`

Controls background reflection cadence when such scheduling is enabled.

`REFLECTION_RUNTIME_MODE`

Controls who owns queued reflection dispatch:

- `in_process`: app-local worker may dispatch immediately
- `deferred`: foreground enqueue stays durable, dispatch is expected from an
  external scheduler/worker driver

Target deployment baseline (PRJ-301):

- production default remains `REFLECTION_RUNTIME_MODE=in_process`
- `deferred` is rollout-only until explicit external-dispatch readiness
  criteria are satisfied

`SCHEDULER_ENABLED`

Enables or disables in-process scheduler cadence for reflection and maintenance
routines.

`SCHEDULER_EXECUTION_MODE`

Controls who owns maintenance/proactive cadence dispatch posture:

- `in_process`: app-local scheduler worker is the active cadence owner
- `externalized`: external scheduler owner is expected; in-process cadence
  dispatch is treated as disabled posture

Health posture (`/health.scheduler`) now exposes this owner mode through:

- `execution_mode`
- `maintenance_cadence_owner` / `proactive_cadence_owner`
- `cadence_execution` (`selected_execution_mode`, dispatch booleans/reasons,
  `ready`, `blocking_signals`)

`MAINTENANCE_INTERVAL`

Controls background maintenance cadence when scheduler execution is enabled.

`PROACTIVE_ENABLED`

Enables or disables proactive system behavior when that subsystem exists.

`PROACTIVE_INTERVAL`

Controls proactive cadence when proactive runtime behavior is enabled.

### Scheduler Cadence Ownership Boundary (PRJ-308)

Target ownership posture:

- long-term production cadence ownership for maintenance/proactive wakeups moves
  to a dedicated external scheduler path
- app-local scheduler cadence remains transitional for local development,
  controlled fallback, and rollout windows

Ownership split:

- runtime owns scheduled-event normalization plus guardrail/conscious execution
  boundaries
- scheduler owner owns cadence triggering, retries/backoff, and
  availability/on-call ownership

`ATTENTION_BURST_WINDOW_MS`

Controls the short coalescing window for bursty Telegram user messages.
Lower values reduce wait time before processing; higher values increase
coalescing tolerance.

`ATTENTION_COORDINATION_MODE`

Controls attention turn-assembly owner posture:

- `in_process`: in-memory turn coordinator owns burst-message assembly
- `durable_inbox`: attention boundary uses repository-backed
  `aion_attention_turn` storage while keeping the same burst-message assembly
  semantics

Health posture (`/health.attention`) now exposes this owner mode through:

- `coordination_mode`
- `turn_state_owner`
- `durable_inbox_expected`
- `deployment_readiness` (`selected_coordination_mode`, `ready`,
  `blocking_signals`)
- `persistence_owner` and `parity_state`
- `contract_store_mode`
- `deployment_readiness.contract_store_state`
- `stale_cleanup_candidates` and `answered_cleanup_candidates`

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
    "env": "production",
    "port": 8000,
    "log_level": "info"
  },
  "policy": {
    "startup_schema_mode": "migrate",
    "event_debug_enabled": false,
    "production_policy_enforcement": "strict"
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
