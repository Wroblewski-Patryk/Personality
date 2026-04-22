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
`event_debug_admin_policy_owner`, `event_debug_admin_ingress_target_path`,
`event_debug_admin_posture_state`,
`event_debug_shared_ingress_retirement_target`,
`event_debug_shared_ingress_retirement_cutover_posture`,
`event_debug_shared_ingress_retirement_gate_checklist`,
`event_debug_shared_ingress_retirement_gate_state`,
`event_debug_shared_ingress_retirement_ready`,
`event_debug_shared_ingress_retirement_blockers`,
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
`debug_token_policy_hint`,
`startup_schema_compatibility_posture`,
`startup_schema_compatibility_sunset_ready`,
`startup_schema_compatibility_sunset_reason`,
`event_debug_shared_ingress_sunset_ready`,
`event_debug_shared_ingress_sunset_reason`,
`compatibility_sunset_ready`, and
`compatibility_sunset_blockers`) plus
strict-rollout readiness signals
(`production_policy_mismatches`, `production_policy_mismatch_count`,
`strict_startup_blocked`, and `strict_rollout_ready`) plus rollout guidance
signals (`recommended_production_policy_enforcement`, `strict_rollout_hint`),
so operators can verify active policy posture, detect strict-mode startup
risks, assess strict-rollout readiness, and track compatibility-route sunset
readiness during incident triage and release smoke.
`GET /health.release_readiness` now also exposes a compact release gate
snapshot (`ready`, `violations`) derived from those runtime-policy fields so
smoke scripts can fail fast on deployment drift.
Observed compat attempts now always keep sunset recommendation in
`migrate_clients_before_disabling_compat` until clients are moved away from
`POST /event?debug=true`.
Compat activity posture fields now distinguish disabled/no-traffic/stale-history
vs recent traffic so migration windows can separate historical noise from active
compat dependency.

`GET /health` also includes a `scheduler` object with cadence posture
(`execution_mode`, cadence owners, dispatch/readiness posture, interval
settings), latest reflection/maintenance tick summaries, and
`external_owner_policy` for the target external cadence baseline.

`GET /health` now also includes a `proactive` object with live proactive
cadence posture:

- shared policy owner and selected cadence owner
- delivery-target and candidate-selection baselines
- anti-spam contract defaults (cooldown, recent outbound threshold,
  unanswered threshold)
- latest proactive tick summary and last tick timestamp

Use `/health.proactive` together with `/health.scheduler.last_proactive_summary`
when triaging why proactive outreach is quiet, blocked, or actively delivering.

`GET /health` now also includes a `role_skill` object with the current
role-versus-skill maturity baseline:

- shared policy owner
- metadata-only execution boundary
- whether planning carries selected skills forward
- explicit confirmation that action cannot execute selected skills directly

`GET /health` now also includes an `attention` object with burst-turn assembly
posture (`coordination_mode`, owner/readiness semantics, timing windows) and
live turn counters (`pending`, `claimed`, `answered`) to support burst-message
triage and owner-mode rollout verification.
`GET /health.attention` also exposes durable contract-store posture through
`persistence_owner`, `parity_state`, `contract_store_mode`,
`deployment_readiness.contract_store_state`, `stale_cleanup_candidates`, and
`answered_cleanup_candidates`, so operators can distinguish in-memory owner
mode from repository-backed durable inbox behavior and cleanup pressure.
`GET /health.attention.timing_policy` now also exposes the production timing
baseline (`120ms` burst window, `5s` answered TTL, `30s` stale cleanup) plus
alignment posture for the currently selected config values.

`GET /health` now also includes an `affective` object for live affective-turn
triage:

- heuristic affective-input ownership posture from perception
- assessment rollout posture and fallback visibility for the current runtime

When investigating empathy/support behavior drift, pair `/health.affective`
with runtime `system_debug.adaptive_state.affective_input_policy` and
`system_debug.adaptive_state.affective_resolution` so you can distinguish
heuristic input, policy-disabled fallback, classifier-unavailable fallback,
and final affective outcome.

`GET /health` now also includes `conversation_channels.telegram` for
conversation-reliability triage:

- `policy_owner=telegram_conversation_reliability_telemetry`
- `round_trip_ready`
- `round_trip_state` (`provider_backed_ready|missing_bot_token`)
- `bot_token_configured`
- `webhook_secret_configured`
- ingress counters:
  - `ingress_attempts`
  - `ingress_rejections`
  - `ingress_queued`
  - `ingress_processed`
  - `ingress_runtime_failures`
- delivery counters:
  - `delivery_attempts`
  - `delivery_successes`
  - `delivery_failures`
- `last_ingress` and `last_delivery`

Use this surface first when Telegram appears silent in production. It tells
you whether the webhook reached the service, whether the secret was rejected,
whether the turn was coalesced into a queue, and whether outbound delivery
ever ran.

`GET /health` now also includes a `memory_retrieval` object with semantic
retrieval posture:

- `semantic_vector_enabled`
- `semantic_retrieval_mode` (`hybrid_vector_lexical|lexical_only`)
- `semantic_embedding_execution_class`
  (`deterministic_baseline|local_provider_owned|provider_owned_openai_api|fallback_to_deterministic`)
- `semantic_embedding_production_baseline`
- `semantic_embedding_production_baseline_state`
- `semantic_embedding_production_baseline_hint`
- `semantic_embedding_provider_ready`
- `semantic_embedding_posture` (`ready|fallback_deterministic`)
- `semantic_embedding_provider_requested`
- `semantic_embedding_provider_effective`
- `semantic_embedding_provider_hint`
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
- `retrieval_lifecycle_policy_owner`
- `retrieval_lifecycle_target_provider_baseline`
- `retrieval_lifecycle_transition_provider_baseline`
- `retrieval_lifecycle_steady_state_refresh_owner`
- `retrieval_lifecycle_source_rollout_baseline`
- `retrieval_lifecycle_relation_source_posture`
- `retrieval_lifecycle_fallback_retirement_posture`
- `retrieval_lifecycle_provider_drift_state`
- `retrieval_lifecycle_provider_drift_hint`
- `retrieval_lifecycle_alignment_state`
- `retrieval_lifecycle_alignment_hint`
- `retrieval_lifecycle_pending_gaps`

When semantic vectors are enabled and `EMBEDDING_PROVIDER=openai` is requested
without `OPENAI_API_KEY`, startup emits `embedding_strategy_warning` with
requested/effective provider-model posture, explicit
`openai_api_key_missing_fallback_deterministic` hint, and the same
provider-ownership / owner-strategy diagnostics visible in `/health`.

Operator interpretation for retrieval production baseline:

- `semantic_embedding_production_baseline=openai_api_embeddings` is the target
  steady-state owner for production retrieval
- `semantic_embedding_production_baseline_state=aligned_openai_provider_owned`
  means OpenAI provider-owned execution is active and aligned
- `semantic_embedding_production_baseline_state=requested_openai_fallback_active`
  means production baseline was requested but runtime is still falling back
  because OpenAI credentials are missing
- `semantic_embedding_production_baseline_state=local_transition_provider_owned`
  means `local_hybrid` is active as a local transition path, not the final
  production owner
- `semantic_embedding_production_baseline_state=deterministic_compatibility_baseline`
  means runtime is still on the explicit compatibility fallback posture

Operator interpretation for retrieval lifecycle closure:

- `retrieval_lifecycle_policy_owner=retrieval_lifecycle_policy` is the shared
  source of truth for target provider owner, transition owner, steady-state
  refresh owner, source-rollout completion baseline, and fallback retirement
  posture
- `retrieval_lifecycle_target_provider_baseline=openai_api_embeddings` remains
  the target steady-state provider owner, while
  `retrieval_lifecycle_transition_provider_baseline=local_hybrid` records the
  bounded local transition path
- `retrieval_lifecycle_source_rollout_baseline=semantic_and_affective_sources_enabled`
  means semantic plus affective families are the foreground rollout completion
  baseline; relation remains an explicit optional follow-on family reflected by
  `retrieval_lifecycle_relation_source_posture`
- treat `retrieval_lifecycle_relation_source_posture=optional_follow_on_family`
  as the intended steady-state posture, not as a rollout gap by itself
- `retrieval_lifecycle_relation_source_policy_owner=relation_source_retrieval_policy`
  means runtime is using the explicit optional-family governance owner rather
  than leaving relation-source posture as an inferred side effect
- `retrieval_lifecycle_relation_source_state=optional_family_not_enabled` means
  the semantic+affective foreground baseline is complete and relation remains
  intentionally disabled
- `retrieval_lifecycle_relation_source_state=optional_family_enabled` means
  relation embeddings are enabled, but still do not redefine steady-state
  rollout completion
- `retrieval_lifecycle_relation_source_state=enabled_ahead_of_baseline` means
  relation was turned on before semantic+affective baseline completion and
  should be treated as a bounded governance warning, not as baseline readiness
- `retrieval_lifecycle_provider_drift_state=aligned_target_provider` means the
  effective provider owner matches the selected steady-state lifecycle target
- `retrieval_lifecycle_provider_drift_state=transition_provider_active` means
  runtime is still intentionally on `local_hybrid`
- `retrieval_lifecycle_provider_drift_state=compatibility_fallback_active`
  means runtime is still on deterministic compatibility fallback
- `retrieval_lifecycle_alignment_state=lifecycle_gaps_present` means rollout is
  not yet at the intended steady-state baseline and exact blockers are listed
  in `retrieval_lifecycle_pending_gaps`
- treat `provider_baseline_not_aligned`,
  `foreground_source_rollout_incomplete`, and
  `refresh_owner_not_aligned` in `retrieval_lifecycle_pending_gaps` as rollout
  blockers when deciding whether retrieval is actually at its intended
  lifecycle baseline

When provider-ownership fallback is active and
`EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT=strict`, startup emits
`embedding_strategy_block` and fails fast until effective provider ownership is
aligned.

When semantic vectors are enabled with `EMBEDDING_PROVIDER=deterministic` and a
non-baseline model name is requested, startup emits
`embedding_model_governance_warning` to indicate deterministic embedding
behavior remains fixed even when model label changes.

When deterministic custom-model-name governance posture is active and
`EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT=strict`, startup emits
`embedding_model_governance_block` and fails fast until model governance
posture is aligned.

When semantic vectors are enabled but embedding source coverage excludes both
`semantic` and `affective`, startup emits `embedding_source_coverage_warning`
so operators can see that vector retrieval path is configured without
high-signal vector source families, with explicit source-rollout diagnostics
for next-step guidance.

When vectors are enabled and source rollout still has a pending next source
kind, startup emits `embedding_source_rollout_hint` with rollout completion
state, next source kind, enabled/missing source sets, and rollout progress.

When vectors are enabled, source rollout is still pending, and
`EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT=warn`, startup emits
`embedding_source_rollout_warning` to keep pending rollout posture visible,
including recommendation/alignment diagnostics.

When vectors are enabled, source rollout is still pending, and
`EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT=strict`, startup emits
`embedding_source_rollout_block` and fails fast until source rollout is
complete, including recommendation/alignment diagnostics.

Startup now also emits `embedding_source_rollout_enforcement_hint` to expose
current enforcement vs recommended rollout posture
(`aligned|below_recommendation|above_recommendation`).

When semantic vectors are enabled and `EMBEDDING_REFRESH_MODE=manual`, startup
also emits `embedding_refresh_warning` so operators can confirm that a separate
manual refresh process exists for embedding updates.

Startup now also emits `embedding_refresh_hint` when refresh mode is not
aligned with rollout recommendation posture (for example manual override before
mature rollout, or on-write posture before recommended manual mode after full
source rollout).

Startup now also emits `embedding_strategy_hint` with strict-rollout readiness,
recommendations, and enforcement-alignment posture so operators can decide
whether to keep `warn`, switch to `strict`, or normalize mixed enforcement
settings before rollout.

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

Migration-first schema parity baseline:

- treat Alembic head as the bootstrap owner for the full live runtime schema,
  including `aion_attention_turn` and `aion_subconscious_proposal`
- when schema-affecting slices land, require both migration evidence and a
  fresh migration-parity regression before treating docs/runtime inventory as
  release truth

`PRODUCTION_POLICY_ENFORCEMENT` controls whether these production-policy
mismatches are warning-only (`warn`) or startup-blocking (`strict`).
Runtime default is now environment-aware: production defaults to `strict`,
non-production defaults to `warn`, and explicit config keeps override ownership.
Current debug-related mismatch examples include
`event_debug_enabled=true`, `event_debug_query_compat_enabled=true`, and
`event_debug_token_missing=true`.

## Target Production Baseline (PRJ-296)

Target release posture for production is:

- `STARTUP_SCHEMA_MODE=migrate`
- `PRODUCTION_POLICY_ENFORCEMENT=strict`
- `EVENT_DEBUG_ENABLED=false`
- `EVENT_DEBUG_QUERY_COMPAT_ENABLED=false`
- `PRODUCTION_DEBUG_TOKEN_REQUIRED=true`

If an incident requires temporary production debug exposure, keep
`EVENT_DEBUG_TOKEN` configured, keep
`PRODUCTION_DEBUG_TOKEN_REQUIRED=true`, and disable debug exposure immediately
after the incident window.

Operator release gate:

- verify `/health.release_readiness.ready=true`
- verify `/health.runtime_policy.production_policy_mismatches` is empty
- verify `/health.runtime_policy.strict_startup_blocked=false`
- verify `/health.runtime_policy.event_debug_query_compat_enabled=false`
- verify `/health.runtime_policy.startup_schema_compatibility_sunset_ready=true`
- verify `/health.runtime_policy.event_debug_shared_ingress_sunset_ready=true`
- verify `/health.runtime_policy.compatibility_sunset_ready=true`

## Internal Debug Ingress Boundary (PRJ-307)

Target posture:

- public API endpoint keeps compact user-facing behavior (`POST /event`)
- full runtime debug payload access is served through a dedicated internal/admin
  ingress boundary
- shared public API endpoint is not the long-term owner of debug payload ingress

Current transitional posture:

- `POST /internal/event/debug` is now the primary internal debug ingress
- `/health.runtime_policy.event_debug_admin_*` is the canonical machine-visible
  source for that dedicated-admin target posture
- shared `POST /event/debug` still runs on the shared API service endpoint
  behind runtime policy gates and is treated as compatibility surface
- shared ingress mode is explicitly configurable via
  `EVENT_DEBUG_SHARED_INGRESS_MODE=compatibility|break_glass_only`
- compatibility `POST /event?debug=true` remains deprecated and should stay
  disabled in production baseline

Ownership boundary:

1. Runtime/API owner:
   - debug payload schema and policy telemetry semantics
     (`debug_access_posture`, compat telemetry, strict mismatch previews)
2. Ops/Release owner:
   - ingress routing, network/auth restrictions, and release/rollback evidence
     for dedicated internal debug ingress

Migration guardrails:

1. keep `EVENT_DEBUG_ENABLED=false` in production baseline unless a temporary
   incident-debug window is explicitly approved
2. when temporary production debug is enabled, require
   `EVENT_DEBUG_TOKEN` + `PRODUCTION_DEBUG_TOKEN_REQUIRED=true` and record an
   explicit rollback/expiry window
3. before retiring shared-endpoint debug in production, verify dedicated
   internal ingress is operator-reachable and release evidence no longer depends
   on `POST /event/debug` from public endpoint paths
4. treat `/health.runtime_policy.event_debug_shared_ingress_retirement_blockers`
   as the live checklist for any remaining shared compat dependence before
   tightening or removing public debug compatibility surfaces

## `create_tables` Compatibility Removal Guardrails (PRJ-306)

Before removing `STARTUP_SCHEMA_MODE=create_tables` support from runtime code,
all of these must be true:

1. production and pre-production operate migration-only (`STARTUP_SCHEMA_MODE=migrate`)
2. no active runbook/rollback path depends on `create_tables`
3. release gates remain green for consecutive release windows, including:
   - `/health.runtime_policy.production_policy_mismatches` stays empty for
     startup-schema posture
   - release smoke passes without compatibility bootstrap fallback
4. migration smoke (`alembic upgrade` + startup + release smoke) is the only
   approved bootstrap path in release evidence
5. migration smoke must reach the full live model set, including durable
   attention and subconscious proposal tables, without relying on
   `create_tables`

Removal rollout order:

1. freeze new compatibility usage (allow only local/test exceptions)
2. remove compatibility startup branch from runtime code
3. remove compatibility-only docs/config references and obsolete tests

## Deployment And Release Path (PRJ-298/PRJ-299)

Primary deployment path:

1. push `main`
2. allow configured Coolify source automation/webhook to trigger deployment
3. verify target commit is running before declaring release complete

Explicit fallback path (when automation is delayed or missing):

1. trigger Coolify deploy webhook manually:
   - Windows: `.\scripts\trigger_coolify_deploy_webhook.ps1`
   - Debian/bash: `./scripts/trigger_coolify_deploy_webhook.sh`
   - optional evidence capture:
     - Windows:
       `.\scripts\trigger_coolify_deploy_webhook.ps1 -EvidencePath artifacts/deploy/coolify-webhook.json`
     - Debian/bash:
       `./scripts/trigger_coolify_deploy_webhook.sh "<webhook_url>" "<webhook_secret>" "" "main" "" "" "codex" artifacts/deploy/coolify-webhook.json`
2. if webhook trigger is unavailable, run Coolify UI redeploy for the same app
3. verify target commit is running before release smoke

Release smoke ownership:

- release operator (Ops/Release owner of the deploy) runs:
  - Windows: `.\scripts\run_release_smoke.ps1 -BaseUrl "<deployment_url>"`
  - Debian/bash: `./scripts/run_release_smoke.sh "<deployment_url>"`
- when deployment-trigger evidence was captured, release smoke can verify it
  before the HTTP smoke roundtrip:
  - Windows:
    `.\scripts\run_release_smoke.ps1 -BaseUrl "<deployment_url>" -DeploymentEvidencePath artifacts/deploy/coolify-webhook.json`
  - Debian/bash:
    `./scripts/run_release_smoke.sh "<deployment_url>" "" "manual-smoke" "false" artifacts/deploy/coolify-webhook.json`
- deployment evidence verification remains optional so existing smoke posture
  stays backward-compatible when no evidence artifact is available.
- smoke now fails fast when `/health.release_readiness.ready=false`
  (or when fallback policy-gate checks detect drift on older runtimes).
- smoke now also fails fast when
  `/health.reflection.deployment_readiness.ready=false`
  (or when fallback reflection handoff/task-health checks detect deployment
  readiness blockers on older runtimes).
- when deployment evidence is provided, smoke also fails fast if the artifact
  kind is wrong, the webhook response was unsuccessful, or the artifact age
  exceeds the selected max-age window.
- smoke now also fails fast when compatibility-sunset evidence fields are
  missing or internally inconsistent, and includes the verified
  migration-bootstrap/shared-debug-ingress posture in the JSON summary.
- release is not considered complete until smoke passes (`GET /health` plus
  `POST /event` roundtrip).
- release-readiness now also requires behavior-validation evidence for the
  living-system baseline:
  - operator evidence mode (local/manual):
    - Windows: `.\scripts\run_behavior_validation.ps1 -GateMode operator`
    - Debian/bash: `./scripts/run_behavior_validation.sh --gate-mode operator`
  - CI gate mode (fail-fast on gate violations):
    - Windows:
      `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
    - Debian/bash:
      `./scripts/run_behavior_validation.sh --gate-mode ci --artifact-path artifacts/behavior_validation/report.json`
  - CI split-stage mode (evaluate pre-generated artifact only):
    - Windows:
      `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactInputPath artifacts/behavior_validation/report.json -ArtifactPath artifacts/behavior_validation/report.gate.json`
    - Debian/bash:
      `./scripts/run_behavior_validation.sh --gate-mode ci --artifact-input-path artifacts/behavior_validation/report.json --artifact-path artifacts/behavior_validation/report.gate.json`
  - required focus: internal `system_debug` surface plus scenario checks for
    memory influence, multi-session continuity, failure-mode stability,
    connector execution posture, proactive cadence posture, metadata-only
    role/skill boundary, deferred reflection expectations, and
    `relation_source_policy` posture versus `/health.memory_retrieval`.
  - artifact contract now includes explicit
    `artifact_schema_version` + `gate_reason_taxonomy_version`, and gate output
    includes `violation_context` for deterministic machine parsing.

Rollback posture:

1. if release smoke fails, stop rollout and keep previous known-good release as
   active baseline
2. redeploy previous known-good commit via Coolify (webhook or UI fallback)
3. rerun release smoke against restored deployment URL

## Required Environment Variables

- `DATABASE_URL`
- `APP_ENV`
- `APP_PORT`
- `LOG_LEVEL`

Production-only required in practice:

- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`

Required for the first live provider-backed connector path:

- `CLICKUP_API_TOKEN`
- `CLICKUP_LIST_ID`

Next bounded connector-read baseline selected for implementation:

- `calendar:read_availability`
- provider hint target: `google_calendar`
- expected operator posture after implementation:
  - `policy_only` when no adapter is present yet
  - `credentials_missing` when adapter lands without provider credentials
  - `provider_backed_ready` when the selected provider path is configured
- safe output contract stays bounded to availability evidence, not raw event
  payloads
- current live bounded path is now
  `calendar.google_calendar_read_availability` in
  `/health.connectors.execution_baseline`
- treat `state=credentials_missing` as configuration drift only for the bounded
  calendar read adapter, not as permission to widen other calendar operations
- treat `state=provider_backed_ready` as permission for action to execute only
  explicit `read_only` availability intents; create/update/cancel operations
  remain policy-only unless separately approved

Current bounded cloud-drive metadata-read baseline:

- `cloud_drive:list_files`
- provider hint target: `google_drive`
- current live bounded path is now `cloud_drive.google_drive_list_files` in
  `/health.connectors.execution_baseline`
- expected operator posture:
  - `credentials_missing` when runtime lacks provider credentials for bounded
    metadata-read execution
  - `provider_backed_ready` when the selected provider path is configured
- safe output contract must stay metadata-only:
  - bounded file-name preview
  - provider file id
  - mime type or provider file kind
  - modified-time or recency note
  - optional truncation or next-page note
- document body content, downloads, and write semantics remain out of scope
  for this lane
- treat `state=credentials_missing` as configuration drift only for the
  bounded Google Drive metadata adapter, not as permission to widen other
  cloud-drive operations
- treat `state=provider_backed_ready` as permission for action to execute only
  explicit `read_only` `list_files` typed intents through the Google Drive
  metadata adapter

Recommended when Telegram webhooks are enabled:

- `TELEGRAM_WEBHOOK_SECRET`
- `EVENT_DEBUG_ENABLED` to control whether debug payload routes
  (`POST /internal/event/debug`, shared `POST /event/debug`, and compatibility
  `POST /event?debug=true`) can expose full internal runtime payloads
  (production default is disabled unless explicitly enabled)
- `EVENT_DEBUG_TOKEN` (optional) to require `X-AION-Debug-Token` for
  debug payload route access
- `EVENT_DEBUG_SHARED_INGRESS_MODE` (optional, default `compatibility`) to
  control shared endpoint posture (`compatibility|break_glass_only`) for
  `POST /event/debug`
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
  embedding provider posture (`deterministic|local_hybrid|openai`)
- `EMBEDDING_MODEL` (optional, default `deterministic-v1`) to configure
  requested embedding model posture
- `EMBEDDING_DIMENSIONS` (optional, default `32`) to control embedding/query
  vector dimensions
- `EMBEDDING_SOURCE_KINDS` (optional, default
  `episodic,semantic,affective`) to control which memory families persist
  embedding records (`episodic|semantic|affective|relation`)
- `EMBEDDING_REFRESH_MODE` (optional, default `on_write`) to define embedding
  refresh ownership posture (`on_write|manual`)
- `EMBEDDING_REFRESH_INTERVAL_SECONDS` (optional, default `21600`) to declare
  expected embedding refresh cadence interval in seconds (must be at least
  `60`)
- `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` (`warn|strict`, default `warn`)
  to decide whether provider-ownership fallback remains warning-only or blocks
  startup
- `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` (`warn|strict`, default `warn`) to
  decide whether deterministic custom-model-name governance posture remains
  warning-only or blocks startup
- `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` (`warn|strict`, default `warn`) to
  decide whether pending source-rollout posture remains warning-only or blocks
  startup
- production retrieval rollout baseline (`PRJ-476`):
  - provider owner target is OpenAI API embeddings when `OPENAI_API_KEY` is
    configured
  - `local_hybrid` remains a local transition path
  - deterministic remains the explicit compatibility fallback baseline
  - refresh owner baseline is `on_write` during rollout (`manual` only as
    explicit operator override)
  - family rollout order is `episodic+semantic`, then `affective`, then
    `relation`
- `PRODUCTION_DEBUG_TOKEN_REQUIRED` (`true|false`, default `true`) to require
  a configured debug token for production debug payload access when debug
  exposure is enabled
- `PRODUCTION_POLICY_ENFORCEMENT` (`warn|strict`) to decide whether production
  policy mismatches remain warning-only or block startup
  (default: `strict` in production, `warn` outside production)
- `SCHEDULER_EXECUTION_MODE` (`in_process|externalized`) to define maintenance
  and proactive cadence owner posture
- `ATTENTION_BURST_WINDOW_MS` (optional) to tune burst-message coalescing
  latency and aggregation behavior
- `ATTENTION_ANSWERED_TTL_SECONDS` and `ATTENTION_STALE_TURN_SECONDS` (optional)
  to tune in-memory turn lifecycle cleanup behavior
- `ATTENTION_COORDINATION_MODE` (`in_process|durable_inbox`) to define
  turn-assembly owner posture and rollout expectation

## Common Operator Flows

## Reflection Topology Posture

Current reflection runtime topology is explicit and mode-aware:

- `REFLECTION_RUNTIME_MODE=in_process`:
  app-local worker can dispatch queued reflection tasks immediately
- `REFLECTION_RUNTIME_MODE=deferred`:
  foreground still enqueues tasks durably, while dispatch is expected from an
  external scheduler/worker driver

Current external-driver operating baseline (PRJ-480..PRJ-483):

- `REFLECTION_RUNTIME_MODE=deferred` is now the explicit target production
  posture for externalized reflection dispatch ownership
- the canonical queue-drain entrypoint is
  `scripts/run_reflection_queue_once.py`
- operator wrappers are:
  - Windows: `.\scripts\run_reflection_queue_once.ps1`
  - Debian/bash: `./scripts/run_reflection_queue_once.sh`
- app-local `in_process` worker remains compatibility posture for local or
  transitional environments, not the target external-worker baseline

Deferred readiness criteria (all required before production-default switch):

1. external dispatcher ownership is explicit in runbook/release ownership
2. `/health.reflection.topology.external_driver_expected=true` and
   `queue_drain_owner=external_driver`
3. deferred queue posture is stable (`pending` backlog does not show recurring
   growth; `stuck_processing=0`; `exhausted_failed=0` during release windows)
4. mode-consistent handoff is visible in scheduler/runtime logs
   (`scheduler_tick_dispatch=false` with external dispatch expectation)
5. release smoke + rollback procedures include reflection deployment readiness
   checks for the selected mode

Operator checks:

- verify `/health.reflection` queue snapshot and worker-running posture
- verify `/health.reflection.deployment_readiness`:
  - `ready`
  - `blocking_signals`
  - `baseline_runtime_mode`
  - `selected_runtime_mode`
- verify `/health.reflection.topology` handoff posture:
  - `queue_drain_owner`
  - `external_driver_expected`
  - `runtime_enqueue_dispatch` / `runtime_enqueue_reason`
  - `scheduler_tick_dispatch` / `scheduler_tick_reason`
  - retry guardrails (`max_attempts`, `retry_backoff_seconds`)
- verify `/health.reflection.external_driver_policy`:
  - `policy_owner=deferred_reflection_external_worker`
  - `entrypoint_path=scripts/run_reflection_queue_once.py`
  - `production_baseline_ready`
  - `production_baseline_state`
  - `production_baseline_hint`
- verify `/health.reflection.supervision`:
  - `policy_owner=deferred_reflection_supervision_policy`
  - `queue_health_state`
  - `production_supervision_ready`
  - `production_supervision_state`
  - `blocking_signals`
  - `recovery_actions`
- verify `/health.scheduler` owner posture:
  - `execution_mode`
  - `maintenance_cadence_owner` / `proactive_cadence_owner`
  - `cadence_execution.selected_execution_mode`
  - `cadence_execution.maintenance_tick_dispatch` /
    `cadence_execution.maintenance_tick_reason`
  - `cadence_execution.proactive_tick_dispatch` /
    `cadence_execution.proactive_tick_reason`
  - `cadence_execution.ready` / `cadence_execution.blocking_signals`
  - `external_owner_policy.policy_owner=external_scheduler_cadence_policy`
  - `external_owner_policy.target_execution_mode=externalized`
  - `external_owner_policy.maintenance_entrypoint_path=scripts/run_maintenance_tick_once.py`
  - `external_owner_policy.proactive_entrypoint_path=scripts/run_proactive_tick_once.py`
  - `external_owner_policy.production_baseline_ready`
- treat growing pending queue in deferred mode as external-dispatch signal
  rather than foreground failure
- treat `queue_health_state=active_backlog_under_supervision` as a recoverable
  backlog posture, not an immediate release failure by itself
- treat `queue_health_state=recovery_required` or any non-empty
  `blocking_signals` as the operator signal that reflection durability needs
  intervention before deferred mode can be treated as healthy release posture
- use the external driver entrypoint for one-shot drain checks:
  - Windows: `.\scripts\run_reflection_queue_once.ps1 -Limit 10`
  - Debian/bash: `./scripts/run_reflection_queue_once.sh 10`
- verify `aion.scheduler` `scheduler_reflection_tick` logs include
  `runtime_mode`, `queue_drain_owner`, and `retry_owner` for worker-mode
  triage

Regression anchors:

- `tests/test_api_routes.py` pins `/health.reflection.topology` handoff fields
- `tests/test_scheduler_worker.py` pins scheduler worker-mode log posture
- `tests/test_reflection_worker.py` pins exhausted-retry skip behavior in
  drain-once processing

Ownership invariants:

- enqueue remains foreground-follow-up owned (`memory_persist` then
  `reflection_enqueue`)
- retry/backoff semantics remain queue-owned across runtime modes
- reflection execution must not block foreground response completion

## Scheduler Cadence Ownership Boundary (PRJ-308)

Target posture:

- long-term production cadence ownership for maintenance/proactive wakeups moves
  to a dedicated external scheduler owner
- app-local scheduler cadence remains transitional and fallback-oriented during
  rollout or incident recovery
- the canonical production entrypoints for that owner are
  `scripts/run_maintenance_tick_once.py` and
  `scripts/run_proactive_tick_once.py`; wrapper scripts are convenience layers
  only

Ownership boundaries:

1. Runtime owner:
   - scheduler event normalization contract
   - guardrail checks and conscious execution boundaries for scheduled events
2. Scheduler owner:
   - cadence triggering, retries/backoff, and runtime wakeup delivery posture
   - production availability/on-call ownership for scheduler path

Rollout guardrails before production cadence externalization:

1. explicit runbook ownership and rollback steps for external scheduler path
2. idempotent scheduler-event contract checks validated in regression and smoke
   evidence
3. release smoke coverage verifies selected cadence owner path and alerting
   visibility

Cutover proof baseline for treating the external scheduler as the real owner:

1. `external_owner_policy.selected_execution_mode=externalized`
2. recent successful maintenance tick evidence from the canonical external
   entrypoint
3. recent successful proactive tick evidence from the canonical external
   entrypoint
4. bounded duplicate-protection or idempotency evidence for both cadence
   entrypoints
5. explicit stale-or-missing evidence posture visible in health or release
   evidence
6. rollback posture that keeps app-local scheduler ownership as the explicit
   recovery baseline when any proof item is missing

These proof items are now machine-visible through
`/health.scheduler.external_owner_policy`:

- `maintenance_run_evidence`
- `proactive_run_evidence`
- `duplicate_protection_posture`
- `cutover_proof_ready`

Interpretation:

- `selected_execution_mode=externalized` plus `cutover_proof_ready=false`
  means the repo is targeting external ownership but has not yet proven
  cutover readiness
- `cutover_proof_ready=true` means recent run evidence and bounded
  duplicate-protection posture are both present for the current cadence
  baseline
- release smoke now validates that those proof fields exist and use recognized
  states
- behavior-validation gate logic now validates the same proof surface from
  exported `incident_evidence`

## Post-Reflection Hardening Baseline (PRJ-309)

Post-reflection hardening decisions are synchronized through `PRJ-309`:

- migration-first startup remains the production target and `create_tables`
  compatibility removal guardrails stay explicit
- internal debug ingress target boundary is defined and shared-endpoint debug
  posture is treated as transitional
- scheduler cadence ownership target is explicit (external long-term owner,
  app-local transitional fallback)
- release smoke now checks `/health.scheduler.external_owner_policy` for the
  same target owner, entrypoint paths, and baseline readiness that startup
  logs expose
- attention owner posture is explicit (`in_process|durable_inbox`) with
  readiness blockers surfaced in `/health.attention.deployment_readiness`

Next execution lane after this sync:

- runtime behavior validation architecture and scenarios (`PRJ-310..PRJ-317`)
  extend release confidence from subsystem health checks to
  memory/continuity/failure behavior evidence

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

With `-IncludeDebug`, release smoke now also validates exported
`incident_evidence` directly and records its schema version, stage count, and
policy-surface coverage in the smoke summary.

For dedicated debug-ingress retirement, `-IncludeDebug` now also proves:

- dedicated-admin target path remains `/internal/event/debug`
- shared debug posture remains `break_glass_only`
- query compatibility remains disabled in incident evidence
- rollback exception is explicit as either
  `shared_debug_break_glass_only` or `shared_debug_disabled`
- Telegram conversation posture is present in exported incident evidence under
  `policy_posture["conversation_channels.telegram"]`

## Incident Evidence Bundle Baseline

Operator-ready incident evidence should be captured as one bounded bundle:

- `manifest.json`
- `incident_evidence.json`
- `health_snapshot.json`
- optional `behavior_validation_report.json`

Recommended artifact root:

- `artifacts/incident_evidence/<captured_at_utc>_<trace_id_or_event_id>/`

Current source-of-truth mapping:

- `incident_evidence.json` comes from debug-mode runtime output
- `health_snapshot.json` comes from `GET /health`
- `behavior_validation_report.json` is attached only when validation was run
  for the same investigation window
- the canonical collection helper is
  `scripts/export_incident_evidence_bundle.py`

Retention baseline:

- keep the latest successful release bundle
- keep the latest failing release or incident bundle
- keep active incident bundles until incident closure plus rollback review

Canonical helper flow:

```powershell
.\.venv\Scripts\python .\scripts\export_incident_evidence_bundle.py `
  --base-url "http://localhost:8000"
```

Optional attachment flow when behavior validation already exists:

```powershell
.\.venv\Scripts\python .\scripts\export_incident_evidence_bundle.py `
  --base-url "http://localhost:8000" `
  --behavior-validation-report-path "artifacts/behavior_validation/report.json"
```

Bundle verification through release smoke:

```powershell
.\scripts\run_release_smoke.ps1 `
  -BaseUrl "http://localhost:8000" `
  -IncidentEvidenceBundlePath "artifacts/incident_evidence/<captured_at_utc>_<trace_id_or_event_id>"
```

Bundle verification now also checks the same dedicated-admin debug posture
from `incident_evidence.json`, so retirement proof does not depend only on the
live `/health.runtime_policy` snapshot.
Bundle verification now also checks Telegram conversation posture from
`incident_evidence.json`, so `v1` conversation reliability does not depend
only on live `/health` during release or incident review.

Optional debug payload with token:

```powershell
curl -X POST "http://localhost:8000/internal/event/debug" `
  -H "Content-Type: application/json" `
  -H "X-AION-Debug-Token: <token>" `
  -d "{\"text\":\"debug check\"}"
```

Shared compatibility debug payload in break-glass mode:

```powershell
curl -X POST "http://localhost:8000/event/debug" `
  -H "Content-Type: application/json" `
  -H "X-AION-Debug-Break-Glass: true" `
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
headers that point to `POST /internal/event/debug` as the preferred internal
path.

Production default posture now treats shared `POST /event/debug` as
break-glass-only when no explicit override is configured; use
`POST /internal/event/debug` as the normal operator ingress.

Shared debug retirement gate baseline:

- cutover posture:
  `dedicated_internal_admin_route_primary_shared_routes_break_glass_then_remove`
- required checklist:
  - `normal_operator_debug_uses_dedicated_internal_admin_route`
  - `shared_event_debug_route_is_break_glass_only_or_disabled`
  - `query_debug_compatibility_route_disabled`
  - `release_smoke_green_for_dedicated_admin_debug_path`
  - `rollback_notes_cover_shared_debug_break_glass_reenablement`
- treat `event_debug_shared_ingress_retirement_gate_state` as the compact
  machine-visible summary:
  - `shared_debug_compatibility_retirement_blocked`: shared route or query
    compat is still active in normal flows
  - `shared_debug_break_glass_retirement_gate_ready`: runtime is at
    break-glass-only posture and ready for the next enforcement/removal step
  - `shared_debug_disabled_retirement_gate_satisfied`: debug payload is off, so
    no shared ingress remains to retire operationally
- treat incident-evidence posture as the release-proof companion to those
  `/health.runtime_policy` fields:
  - release smoke must stay green for live debug `incident_evidence`
  - bundle verification must stay green for `incident_evidence.json`
  - behavior-validation CI gate must stay green when incident evidence is
    attached to the same release or incident investigation

### Run Health Check

```powershell
curl http://localhost:8000/health
```

Important health surfaces for current release checks:

- `runtime_policy.startup_schema_removal_window`
- `runtime_policy.event_debug_shared_ingress_enforcement_window`
- `observability`
  - shared export policy owner
  - `export_artifact_available`
  - `incident_export_ready`
- `affective`
  - heuristic-input ownership baseline
  - assessment rollout/fallback posture for live empathy triage
- `runtime_topology`
- `role_skill`
  - shared role/skill policy owner
  - metadata-only execution boundary
  - planning carry-forward posture and action-side execution denial
- `proactive`
  - shared proactive policy owner and selected cadence owner
  - delivery-target baseline and candidate-selection baseline
  - anti-spam threshold snapshot plus latest proactive tick summary
- `planning_governance`
  - inferred goal/task growth posture
  - fixed proposal-decision baseline
- `memory_retrieval.semantic_embedding_execution_class`
  - whether retrieval is currently running as deterministic baseline,
    local provider-owned execution, OpenAI provider-owned execution, or
    provider-requested fallback
  - pair it with
    `memory_retrieval.semantic_embedding_production_baseline_state` to tell
    whether runtime is aligned with the target OpenAI production owner,
    still on a local transition path, or still on compatibility fallback
- `memory_retrieval.retrieval_lifecycle_alignment_state`
  - whether retrieval is actually aligned with the selected steady-state
    lifecycle baseline
  - treat `lifecycle_gaps_present` as the high-signal summary field for
    rollout blockers before reading deeper embedding diagnostics
- `memory_retrieval.retrieval_lifecycle_pending_gaps`
  - exact lifecycle blockers across provider owner, refresh owner, and
    foreground source-rollout completion
- `connectors`
  - connector authorization matrix
  - capability-proposal posture for not-yet-authorized expansion
  - `execution_baseline` shows whether the current live provider-backed
    task-system paths are configured
  - `task_system.clickup_create_task.state=credentials_missing` means the repo
    is still in policy-only posture for task creation at runtime
  - `task_system.clickup_create_task.state=provider_backed_ready` means action
    may execute ClickUp task creation after expression when the plan emits the
    matching typed intent
  - `task_system.clickup_list_tasks.state=credentials_missing` means the repo
    is still policy-only for provider-backed task reads at runtime
  - `task_system.clickup_list_tasks.state=provider_backed_ready` means action
    may execute a bounded ClickUp task read from explicit `read_only` typed
    intents without widening planning or context ownership
  - `task_system.read_capable_live_paths` versus
    `task_system.mutation_live_paths` shows which live surfaces already exist
    under the task-system family
  - `calendar.google_calendar_read_availability.state=credentials_missing`
    means the bounded calendar live-read adapter exists but runtime lacks
    credentials for provider-backed execution
  - `calendar.google_calendar_read_availability.state=provider_backed_ready`
    means action may execute only bounded `read_availability` typed intents
    through the Google Calendar adapter
  - `calendar.other_operations` should remain policy-only after this slice
  - `cloud_drive.google_drive_list_files.state=credentials_missing` means the
    bounded cloud-drive metadata adapter exists but runtime lacks provider
    credentials for execution
  - `cloud_drive.google_drive_list_files.state=provider_backed_ready` means
    action may execute only bounded `list_files` typed intents through the
    Google Drive metadata adapter
  - `cloud_drive.other_operations` should remain policy-only after this slice
- `identity.adaptive_governance`
  - bounded authority model for role horizon, affective rollout,
    preferences, theta, and multilingual/profile posture
- `deployment`
  - hosting baseline selection
  - deployment-trigger SLO posture consumed by release smoke

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

### Run Telegram Mode Smoke (Webhook + Temporary Listen Probe)

Use the dedicated smoke helper to validate both Telegram delivery modes:

- webhook mode visibility (`getWebhookInfo`)
- temporary listen diagnostics (`deleteWebhook -> getUpdates`)
- webhook restore (`setWebhook`)

Windows PowerShell:

```powershell
.\scripts\run_telegram_mode_smoke.ps1 `
  -ExpectedWebhookUrl "https://your-domain.tld/event" `
  -RestoreWebhookUrl "https://your-domain.tld/event" `
  -SecretToken "<telegram_webhook_secret>" `
  -RequiredChatId "<chat_id>"
```

Debian / bash:

```bash
./scripts/run_telegram_mode_smoke.sh \
  --expected-webhook-url "https://your-domain.tld/event" \
  --restore-webhook-url "https://your-domain.tld/event" \
  --secret-token "<telegram_webhook_secret>" \
  --required-chat-id "<chat_id>"
```

Preconditions checklist (required for reliable Telegram delivery triage):

1. Bot-start handshake is complete in target chat (`/start` was sent to the bot).
2. `chat_id` is known and passed as `RequiredChatId` (or `--required-chat-id`) for strict validation.
3. Bot token is configured (`TELEGRAM_BOT_TOKEN`) before running the smoke helper.
4. If webhook secret validation is enabled, pass the same secret used by runtime webhook ingress.

## Known Operational Limits

- there is no background queue or worker isolation yet
- reflection now has an explicit external-driver queue-drain entrypoint, but
  worker supervision and recovery posture are now bounded by explicit
  supervision policy and release evidence
- startup now defaults to migration-first schema ownership; `create_tables()` remains only as a compatibility path behind `STARTUP_SCHEMA_MODE=create_tables`
- runtime now has exportable JSON incident evidence plus a canonical bundle
  helper, but there is still no external observability stack with dashboards
  or centralized trace storage
- proactive cadence is live in-process today, while external scheduler
  ownership is now the explicit target posture with machine-visible fallback
  evidence

## Incident Triage Shortlist

If a request path fails:

1. check whether the app booted with valid env vars
2. verify Postgres health and connection string
3. confirm whether OpenAI fallback behavior is acceptable for the failing scenario
4. for Telegram issues, verify webhook secret, bot token, and `chat_id` presence
5. inspect `/health.conversation_channels.telegram`:
   - rejected ingress means secret mismatch or malformed webhook path
   - queued ingress means burst coalescing/turn ownership is active
   - missing bot token means delivery cannot be provider-backed
   - delivery failures expose whether the problem is missing `chat_id`,
     Telegram API failure, or transport exception
6. inspect structured logs for `event_id`, `trace_id`, and action status
