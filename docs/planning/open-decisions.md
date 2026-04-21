# Open Decisions

## Why This File Exists

The current repo already works as an MVP slice, but several architecture-level docs describe systems that are not implemented yet. This file keeps the next real decisions visible and tied to the current codebase.

## Target-State Convergence Stance (2026-04-20)

- For the next execution queue, prefer slices that reduce transitional wiring
  and move code toward the canonical architecture even when the current
  implementation can support temporary shortcuts.
- Treat `docs/architecture/02_architecture.md`,
  `docs/architecture/15_runtime_flow.md`, and
  `docs/architecture/16_agent_contracts.md` as the target shape for new work.
  Use `docs/implementation/runtime-reality.md` to describe current constraints
  and rollout guardrails, not to redefine the architecture.
- Resolve the currently open decision clusters through the queued groups in
  `docs/planning/next-iteration-plan.md` and
  `.codex/context/TASK_BOARD.md`:
  - `PRJ-276..PRJ-279`: foreground runtime convergence (`3a`, `3b`)
  - `PRJ-280..PRJ-283`: background reflection topology (`1`, `12`)
  - `PRJ-284..PRJ-287`: production memory retrieval rollout (`5`, `5d`,
    `5e`, `9a`)
  - `PRJ-288..PRJ-291`: adaptive cognition governance (`4`, `4a`, `10`,
    `10a`, `10b`, `11`)
  - `PRJ-292..PRJ-295`: attention/proposal execution boundary (`12a`, `12b`,
    `12c`)
  - `PRJ-296..PRJ-299`: operational hardening and release truth (`2`, `3`,
    `6`, `7`)
  - `PRJ-301..PRJ-304`: reflection deployment baseline and readiness rollout
    (`1`, `12` follow-up)
  - `PRJ-306..PRJ-309`: post-reflection hardening decisions (`2` follow-up,
    `3` follow-up, `12` follow-up)
  - `PRJ-310..PRJ-313`: runtime behavior testing architecture and internal
    validation surface (`3`, `5`, `12`) - complete
  - `PRJ-314..PRJ-317`: memory/continuity/failure validation scenarios and
    release gating (`5`, `8`, `9`, `12`) - complete
  - `PRJ-318..PRJ-321`: internal debug ingress migration
    (`3` implementation follow-up) - complete
  - `PRJ-322..PRJ-325`: scheduler externalization and attention ownership
    (`1`, `12`, `12a` implementation follow-up) - complete
  - `PRJ-326..PRJ-329`: identity, language, and profile boundary hardening
    (`8`, `9`) - complete
  - `PRJ-330..PRJ-333`: relation lifecycle and trust influence rollout
    (`9a`, `10`, `12`) - complete
  - `PRJ-334..PRJ-337`: goal/task inference and typed-intent expansion
    (`5a`, `10a`, `12c`) - complete
  - `PRJ-339..PRJ-342`: manual runtime reliability fixes
    (`3`, `13`) - complete
  - `PRJ-343..PRJ-346`: relation-aware inferred promotion governance
    (`9a`, `10a`) - complete
  - `PRJ-347..PRJ-350`: behavior-validation CI-ingestion follow-up
    (`13`) - queued
- reflection deployment lane is complete through `PRJ-304`, and
  post-reflection hardening decisions are now complete through `PRJ-309`.
- runtime behavior-validation lane is now complete through `PRJ-317`.
- next architecture-to-code queue is now seeded through `PRJ-350`.
- Introduce new feature surface only when it advances one of those convergence
  lanes or removes a documented transitional shortcut.

## Active Decisions

### 1. Reflection Placeholder vs Real Reflection

- Current repo fact:
  - runtime now has a lightweight background reflection worker backed by a durable `aion_reflection_task` queue in Postgres.
  - `RuntimeResult.reflection_triggered` is returned as `True` when reflection was successfully persisted and queued after episode persistence.
  - failed reflection tasks now retry with bounded backoff inside the app process.
  - `GET /health` now exposes a lightweight reflection snapshot with worker state and queue/task counts.
  - `PRJ-280` now defines explicit topology ownership across
    `in_process|deferred` modes, durable enqueue ownership, queue/retry
    semantics, and operator-visible health posture boundaries.
  - `PRJ-281` now extracts a shared enqueue/dispatch boundary contract consumed
    by both runtime follow-up and scheduler tick ownership paths.
  - `PRJ-282` now exposes worker-mode handoff posture through
    `/health.reflection.topology` and scheduler runtime logs so queue-drain and
    retry ownership are explicit for in-process and deferred operation.
  - `PRJ-283` now pins those ownership guarantees with regressions and keeps
    planning/context/ops docs aligned to the converged background topology.
  - `/health.reflection` now exposes deployment-readiness posture
    (`ready`, `blocking_signals`, baseline/selected runtime mode) so reflection
    mode migration no longer depends on log-only interpretation.
  - release smoke scripts now treat reflection deployment-readiness blockers as
    release-failing signals (with explicit fallback checks for older runtimes
    that do not yet expose the readiness snapshot).
- Decision (PRJ-301 reflection deployment baseline, 2026-04-20):
  - production deployment baseline remains
    `REFLECTION_RUNTIME_MODE=in_process` for now, so reflection dispatch keeps
    a local owner while post-convergence hardening continues.
  - `REFLECTION_RUNTIME_MODE=deferred` is a controlled rollout posture, not a
    default baseline.
  - deferred rollout readiness requires all of:
    - explicit external dispatch owner runbook and on-call ownership
    - `/health.reflection.topology.external_driver_expected=true` and
      `queue_drain_owner=external_driver`
    - sustained queue stability in deferred posture (no recurring growth in
      pending backlog and no persistent `stuck_processing`/`exhausted_failed`)
    - scheduler/runtime logs proving mode-consistent dispatch handoff
      (`scheduler_tick_dispatch=false` with external-driver expectation)
    - release smoke and rollback steps updated to include reflection-mode
      readiness checks
- Remaining follow-up decision:
  - once deferred readiness criteria are continuously satisfied, should
    production default move from `in_process` to `deferred`?

### 2. Migration Strategy

- Current repo fact:
  - the repo now has an Alembic baseline rooted in the current SQLAlchemy metadata, with an initial revision under `migrations/versions/`.
  - startup now defaults to migration-first behavior and skips `create_tables()` unless `STARTUP_SCHEMA_MODE=create_tables` is explicitly enabled.
  - `GET /health` now exposes active non-secret runtime policy flags, including `startup_schema_mode` and `production_policy_enforcement`, so operators can verify migration policy posture on the live runtime.
  - `GET /health` now also exposes startup-policy mismatch preview, readiness, and guidance signals (`production_policy_mismatches`, `production_policy_mismatch_count`, `strict_startup_blocked`, `strict_rollout_ready`, `recommended_production_policy_enforcement`, `strict_rollout_hint`) for operator triage.
  - startup now emits a production warning when `STARTUP_SCHEMA_MODE=create_tables` to keep compatibility mode visible in runtime logs.
  - startup can now run in strict production-policy mode (`PRODUCTION_POLICY_ENFORCEMENT=strict`) and hard-fail on policy mismatch instead of warning-only behavior.
  - strict policy fail-fast behavior is pinned at lifespan entry by regression tests for both mismatch families (`EVENT_DEBUG_ENABLED=true` and `STARTUP_SCHEMA_MODE=create_tables`) to prevent startup-order drift.
  - runtime-policy mismatch detection now uses one shared helper owner so startup and `/health` stay aligned.
  - startup and `/health` now share the same strict-block semantics through shared readiness helpers (`strict_startup_blocked`, `strict_rollout_ready`).
  - startup now emits an informational strict-rollout hint when production runs in `warn` mode and strict rollout is ready.
  - production policy enforcement now resolves to `strict` by default in
    production when `PRODUCTION_POLICY_ENFORCEMENT` is unset, while explicit
    `warn` remains a controlled override.
  - `GET /health` now exposes `release_readiness` (`ready`, `violations`) so
    release smoke can fail fast when production-policy drift appears.
  - `scripts/run_release_smoke.{ps1,sh}` now enforce that release-readiness
    gate and stop the release when drift signals are present.
- Decision (PRJ-296 target production baseline, 2026-04-20):
  - target production startup posture is migration-only
    (`STARTUP_SCHEMA_MODE=migrate`); `create_tables` remains a temporary
    compatibility fallback path.
  - target production policy posture is strict
    (`PRODUCTION_POLICY_ENFORCEMENT=strict`) so mismatch conditions fail fast
    instead of staying warning-only.
  - release-readiness checks should treat non-empty
    `runtime_policy.production_policy_mismatches` as baseline drift.
- Decision (PRJ-306 migration compatibility removal criteria, 2026-04-20):
  - `create_tables` compatibility path can be removed only when all guardrails
    are true:
    - production and pre-production environments run with
      `STARTUP_SCHEMA_MODE=migrate` and no approved exceptions
    - release gates stay green with
      `runtime_policy.production_policy_mismatches` empty across at least two
      consecutive release windows
    - no operational rollback/runbook step depends on `create_tables` as a
      recovery path
    - migration smoke (`alembic upgrade` + app startup + release smoke)
      is validated as the sole bootstrap route for the same release windows
  - removal rollout order is:
    - freeze: disallow new `create_tables` usage outside local/test-only
      contexts
    - remove: delete compatibility startup branch and associated policy
      mismatch path
    - clean up: remove obsolete docs/config references and compatibility-only
      tests
- Remaining follow-up decision:
  - after guardrails are met, in which release window should the actual code
    removal of `create_tables` be scheduled?

### 3. Public API Shape

- Current repo fact:
  - `POST /event` now returns a smaller public response by default: event identifiers, reply payload, and a compact runtime summary.
  - the full serialized runtime result is exposed through primary internal
    route `POST /internal/event/debug`, plus transitional compatibility routes
    `POST /event/debug` (shared endpoint) and
    `POST /event?debug=true` (query compatibility path), guarded by explicit
    config (`EVENT_DEBUG_ENABLED`) with environment-aware defaults (enabled in
    non-production, disabled in production unless explicitly enabled).
  - `POST /event?debug=true` now emits explicit compatibility headers
    (`X-AION-Debug-Compat`, `Link`) that point operators to
    `POST /internal/event/debug` as the preferred internal debug route.
  - shared `POST /event/debug` now emits explicit compatibility headers
    (`X-AION-Debug-Shared-Compat`, `X-AION-Debug-Shared-Mode`,
    `X-AION-Debug-Shared-Posture`) and can run in
    `compatibility|break_glass_only` mode through
    `EVENT_DEBUG_SHARED_INGRESS_MODE`.
  - compat-route responses now also emit
    `X-AION-Debug-Compat-Deprecated=true` and runtime health now exposes
    `event_debug_query_compat_telemetry` counters plus derived compat sunset
    recommendation signals (`event_debug_query_compat_allow_rate`,
    `event_debug_query_compat_block_rate`,
    `event_debug_query_compat_recommendation`) plus explicit sunset posture
    signals (`event_debug_query_compat_sunset_ready`,
    `event_debug_query_compat_sunset_reason`) for migration tracking.
  - compat recommendation logic now treats any observed compat attempts as
    migration-needed (not only successful compat responses), so blocked
    attempts still count as active migration work.
  - health policy now also exposes rolling compat trend signals
    (`event_debug_query_compat_recent_attempts_total`,
    `event_debug_query_compat_recent_allow_rate`,
    `event_debug_query_compat_recent_block_rate`,
    `event_debug_query_compat_recent_state`) to support release-window
    migration monitoring.
  - rolling compat trend window size is now configurable via
    `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` (default `20`).
  - health policy now also exposes compat freshness posture
    (`event_debug_query_compat_stale_after_seconds`,
    `event_debug_query_compat_last_attempt_age_seconds`,
    `event_debug_query_compat_last_attempt_state`) so migration decisions can
    distinguish fresh usage from stale historical attempts.
  - health policy now also exposes compat activity posture
    (`event_debug_query_compat_activity_state`,
    `event_debug_query_compat_activity_hint`) so operators can separate
    disabled/no-attempt/stale-history/recent-traffic compatibility states
    without changing the stricter sunset-ready decision contract.
  - stale-age threshold for that freshness posture is configurable via
    `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS` (default `86400`).
  - compatibility `POST /event?debug=true` route now has an explicit
    environment-aware policy surface (`EVENT_DEBUG_QUERY_COMPAT_ENABLED`):
    enabled by default outside production and disabled by default in
    production unless explicitly enabled.
  - when `EVENT_DEBUG_TOKEN` is configured, `POST /event?debug=true` also requires `X-AION-Debug-Token`.
  - when `EVENT_DEBUG_TOKEN` is configured, both
    `POST /internal/event/debug` and `POST /event/debug` require
    `X-AION-Debug-Token`.
  - production can now enforce debug-token configuration through
    `PRODUCTION_DEBUG_TOKEN_REQUIRED` (default `true`); when enabled and
    production debug payload exposure is active without a configured token,
    debug endpoints reject access.
  - `GET /health` now exposes `event_debug_enabled`, `event_debug_token_required`,
    `production_debug_token_required`, `debug_access_posture`,
    `debug_token_policy_hint`, `event_debug_source`, and
    `production_policy_enforcement` so operators can verify effective policy,
    token-gate posture, policy source, and enforcement mode.
  - `/health` also exposes strict-rollout readiness and recommendation signals so operators can detect production-hardening mismatches before a strict-mode rollout and decide when to switch enforcement.
  - startup now emits a production warning when `EVENT_DEBUG_ENABLED=true` so the policy remains visible even before handling requests.
  - startup warns when production debug payload exposure is enabled without
    `EVENT_DEBUG_TOKEN` while `PRODUCTION_DEBUG_TOKEN_REQUIRED=true`.
  - startup also warns when production debug payload exposure is enabled with
    `PRODUCTION_DEBUG_TOKEN_REQUIRED=false`, making relaxed token-hardening
    posture explicit.
  - startup can now hard-fail in production when debug payload exposure is enabled and strict enforcement mode is active.
  - strict mismatch posture now also includes
      `event_debug_token_missing=true` when debug exposure is enabled in
      production, token requirement is enabled, and no debug token is
      configured.
  - strict mismatch posture also includes
    `event_debug_query_compat_enabled=true` when production debug exposure
    keeps compatibility query-debug route enabled.
  - strict-mode hard-fail behavior is test-covered at startup lifecycle level across both debug and schema mismatch paths, not only at helper-function level.
  - production now uses strict policy enforcement as the default when
    enforcement mode is unset, and explicit `warn` keeps temporary override
    ownership visible.
- Decision (PRJ-296 target production baseline, 2026-04-20):
  - production public API posture stays compact on `POST /event`; full runtime
    payload remains an internal diagnostics surface.
  - production baseline keeps debug exposure disabled by default
    (`EVENT_DEBUG_ENABLED=false`) and keeps compatibility query-debug route
    disabled (`EVENT_DEBUG_QUERY_COMPAT_ENABLED=false`).
  - when a temporary incident-debug window is explicitly enabled in production,
    debug payload access must stay token-gated
    (`EVENT_DEBUG_TOKEN` configured and
    `PRODUCTION_DEBUG_TOKEN_REQUIRED=true`).
  - strict production policy enforcement should treat debug-exposure mismatch
    states as release-blocking drift.
- Decision (PRJ-307 internal debug ingress boundary, 2026-04-20):
  - target ingress contract is:
    - public API ingress keeps `POST /event` compact and must not expose full
      runtime payloads
    - full runtime debug payload access belongs to a dedicated internal/admin
      ingress boundary (not a shared public API service endpoint)
  - migration posture is:
    - current primary debug ingress path is `POST /internal/event/debug`
    - current `POST /event/debug` on shared API service endpoint is a
      transitional compatibility posture
    - shared endpoint posture can be tightened to break-glass-only mode
      (`EVENT_DEBUG_SHARED_INGRESS_MODE=break_glass_only`) while preserving
      explicit emergency override via `X-AION-Debug-Break-Glass: true`
    - deprecated compatibility `POST /event?debug=true` remains migration-only
      and should stay disabled in production baseline
    - production incident-debug usage should migrate to dedicated internal
      ingress first, then shared-endpoint debug exposure should be retired as
      default posture
  - ownership boundaries are:
    - runtime/API owners keep debug payload schema and policy telemetry
      semantics (`debug_access_posture`, compat telemetry, strict mismatch
      previews)
    - Ops/Release owns ingress routing, network/auth controls, and
      release/rollback evidence for the dedicated debug ingress path
- Remaining follow-up decision:
  - in which release window should production enforce dedicated internal
    ingress-only debug access (shared-endpoint debug disabled except
    break-glass override)?

### 3a. Expression vs Action Ordering

- Current repo fact:
  - canonical architecture describes `... -> planning -> expression -> action -> memory -> reflection`.
  - foreground runtime now materializes an explicit response-execution handoff
    (`ActionDelivery`) at expression output, and action consumes that handoff
    directly.
  - action still delegates channel delivery to integration-owned routing
    (`DeliveryRouter`), so integration dispatch consumes explicit handoff
    payload while side effects remain action-triggered.
- Decision needed:
  - should future connector-heavy flows keep one shared `ActionDelivery`
    contract, or introduce connector-specific handoff extensions while
    preserving expression/action ownership boundaries?

### 3b. Graph Orchestration Adoption

- Current repo fact:
  - architecture docs describe `LangGraph` as the intended orchestration layer,
    and foreground stage execution now runs through LangGraph `StateGraph`.
  - foreground ownership convergence for Group 17 is now complete:
    - `PRJ-276` defined canonical ownership and migration invariants
    - `PRJ-277` made expression-to-action handoff explicit
    - `PRJ-278` made runtime-owned pre/post graph segments explicit in code
    - `PRJ-279` pinned parity regressions and synchronized docs/context
  - baseline-state load plus post-action persistence/reflection still run
    outside graph execution by design, with explicit ownership boundaries.
  - runtime keeps an explicit graph-compatibility boundary
    (`GraphRuntimeState`, conversion helpers, stage adapters) for incremental
    migration without contract drift.
  - `PRJ-276` now defines the target foreground ownership boundary and migration
    invariants in canonical docs:
    - runtime-owned: baseline load, episodic memory write, reflection trigger
    - graph-owned: cognitive stage graph (`perception -> ... -> action`)
  - `LangChain` is described as optional support, not the architectural core.
- Decision needed:
  - should any non-stage segments move into graph-owned nodes in a future phase,
    or should current pre/post graph ownership stay the long-term baseline?
  - where does LangChain actually reduce complexity, and where would it only
    add more framework surface?

### 4. Role Selection

- Current repo fact:
  - runtime role now uses lightweight heuristic selection (`friend`, `analyst`, `executor`, `mentor`, `advisor`), can use a reflected `preferred_role` as a tie-breaker for more ambiguous turns, and can also fall back to lightweight reflected theta bias when explicit heuristics do not decide the turn.
- Decision needed:
  - when should role selection move from heuristics into a richer module with user-state, memory, and goal-aware logic?

### 4a. Affective Assessment Strategy

- Current repo fact:
  - runtime now has a first-class affective contract slot
    (`affect_label`, `intensity`, `needs_support`, `confidence`, `source`,
    `evidence`) and a dedicated affective assessor stage.
  - when available, the assessor can consume LLM classification and normalize
    it to the shared contract; when unavailable or invalid, it falls back
    deterministically.
  - motivation, role, and expression now consume `perception.affective` as the
    shared support/emotion signal owner.
- Decision needed:
  - should AI-assisted affective classification be enabled by default in all
    non-production environments, or behind an explicit feature gate?
  - which affective outputs deserve first-class contract fields
    (`label|intensity|needs_support|confidence|source|evidence`)?

### 5. Memory Retrieval Depth

- Current repo fact:
  - runtime now loads up to 12 recent memory rows for context selection.
  - persisted episodes now keep lightweight structured runtime fields in a typed payload, while still keeping a readable summary.
  - perception now emits lightweight `topic_tags`, and memory persistence reuses them before falling back to raw lexical tokens.
  - context and reflection now read episodic memory payload-first and fall back to old summary-only rows only when needed.
  - context now prefers memories tagged with the same response language as the current turn before falling back to untagged older context.
  - within that pool, context now distinguishes between `continuity` and `semantic` memory, applies affective relevance scoring, and prefers topically overlapping memories before falling back to lower-signal items.
  - for more specific requests, context now skips unrelated memory entirely instead of forcing a weak fallback; ambiguous short follow-ups can still reuse continuity memory.
  - context also now receives lightweight semantic conclusions and can include stable user preferences alongside episodic recall.
- Decision needed:
  - when to replace heuristic ranking with a hybrid lexical plus vector retrieval path?
  - what should be the default load depth in production once vector retrieval exists?

### 5b. Affective Memory Model

- Current repo fact:
  - episodic payloads now persist lightweight affective tags
    (`affect_label`, `affect_intensity`, `affect_needs_support`,
    `affect_source`, `affect_evidence`).
  - reflection now derives slower-moving affective conclusions
    (`affective_support_pattern`, `affective_support_sensitivity`) from recent
    episodic traces.
- Decision needed:
  - should affective memory be a separate persisted memory family, or an
    orthogonal layer carried by episodic and semantic records?
  - which affective signals should remain transient turn-state and which should
    become durable long-term patterns?

### 5c. Reflection Scope And Multi-Goal Leakage

- Current repo fact:
  - reflection now supports scoped conclusions (`scope_type`, `scope_key`) and
    persists goal-operational conclusions with goal scope.
  - runtime consumers now resolve a primary active goal and read scoped
    conclusions/preferences with global fallback, reducing cross-goal leakage in
    context, motivation, planning, and milestone enrichment.
- Decision needed:
  - which reflection outputs should be global per user, and which must become
    goal-scoped or task-scoped before the runtime grows further?

### 5d. Vector Retrieval Activation

- Current repo fact:
  - runtime now has a semantic embedding contract, deterministic embedding
    fallback helpers, pgvector-ready schema/migration scaffolding, and hybrid
    lexical-plus-vector retrieval APIs.
  - semantic vector retrieval now has an explicit runtime feature gate
    (`SEMANTIC_VECTOR_ENABLED`) and `/health` operator visibility through
    `memory_retrieval.semantic_vector_enabled` and
    `memory_retrieval.semantic_retrieval_mode`
    (`hybrid_vector_lexical|lexical_only`).
  - runtime memory load now consumes hybrid retrieval diagnostics with explicit
    rollout posture in `/health`.
- Decision (resolved in `PRJ-284`, 2026-04-20):
  - keep `SEMANTIC_VECTOR_ENABLED=true` as the target production baseline,
    while preserving explicit lexical-only behavior when vectors are disabled
  - keep vector retrieval as the default runtime retrieval path for enabled
    source families
  - keep deterministic fallback explicit until provider-backed execution is
    implemented and validated
- Follow-up decision:
  - decide when to switch default provider posture from deterministic baseline
    to provider-owned execution after provider implementation lands

### 5e. Embedding Strategy

- Current repo fact:
  - code now defines embedding contracts and deterministic fallback vectors for
    episodic/semantic retrieval surfaces.
  - embedding strategy config posture is now explicit
    (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`) and
    `/health.memory_retrieval` now exposes requested/effective
    provider-model posture plus deterministic-fallback hint for
    non-implemented providers.
  - `/health.memory_retrieval` now also exposes explicit provider readiness
    posture (`semantic_embedding_provider_ready`,
    `semantic_embedding_posture`) and startup logs now emit
    `embedding_strategy_warning` when a requested provider falls back to
    deterministic execution.
  - semantic/affective conclusion embeddings, episodic embeddings, and relation
    embeddings now honor explicit refresh ownership with
    `materialized_on_write` versus `pending_manual_refresh` status.
  - source-family rollout remains explicitly gated by
    `EMBEDDING_SOURCE_KINDS`, allowing progressive enablement across
    `semantic|affective|relation` without implicit writes.
  - startup warnings and health diagnostics now share one embedding warning
    posture owner; `/health.memory_retrieval` exposes
    `semantic_embedding_warning_state` and
    `semantic_embedding_warning_hint` for machine-readable fallback posture.
  - embedding persistence scope is now explicit through
    `EMBEDDING_SOURCE_KINDS`, so runtime can limit which memory families
    (`episodic|semantic|affective|relation`) persist embedding records.
  - source-coverage posture for current vector retrieval path is now explicit
    through `semantic_embedding_source_coverage_state` and
    `semantic_embedding_source_coverage_hint`, with startup warnings using the
    same shared coverage-state semantics.
  - embedding refresh-cadence posture is now explicit through
    `EMBEDDING_REFRESH_MODE` (`on_write|manual`) and
    `EMBEDDING_REFRESH_INTERVAL_SECONDS`; `/health.memory_retrieval` now
    surfaces `semantic_embedding_refresh_mode` and
    `semantic_embedding_refresh_interval_seconds`; shared helper-owned refresh
    diagnostics (`semantic_embedding_refresh_state`,
    `semantic_embedding_refresh_hint`) now align startup and health semantics,
    and startup emits `embedding_refresh_warning` when vectors are enabled in
    manual mode.
  - model-governance posture is now explicit through shared diagnostics
    (`semantic_embedding_model_governance_state`,
    `semantic_embedding_model_governance_hint`) and startup warning visibility
    (`embedding_model_governance_warning`) for deterministic custom-model-name
    posture.
  - provider-ownership posture is now explicit through shared diagnostics
    (`semantic_embedding_provider_ownership_state`,
    `semantic_embedding_provider_ownership_hint`) and startup fallback warning
    enrichment.
  - provider-ownership enforcement posture is now explicit through
    `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` (`warn|strict`) and shared
    enforcement diagnostics
    (`semantic_embedding_provider_ownership_enforcement`,
    `semantic_embedding_provider_ownership_enforcement_state`,
    `semantic_embedding_provider_ownership_enforcement_hint`), including
    strict-mode startup block behavior for unresolved fallback ownership.
  - model-governance enforcement posture is now explicit through
    `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` (`warn|strict`) and shared
    enforcement diagnostics
    (`semantic_embedding_model_governance_enforcement`,
    `semantic_embedding_model_governance_enforcement_state`,
    `semantic_embedding_model_governance_enforcement_hint`), including
    strict-mode startup block behavior for deterministic custom-model-name
    governance posture.
  - owner-strategy recommendation posture is now explicit through shared
    diagnostics (`semantic_embedding_owner_strategy_state`,
    `semantic_embedding_owner_strategy_hint`,
    `semantic_embedding_owner_strategy_recommendation`) so provider+refresh
    ownership strategy is machine-visible in health and startup diagnostics.
  - source-rollout recommendation posture is now explicit through shared
    diagnostics (`semantic_embedding_source_rollout_state`,
    `semantic_embedding_source_rollout_hint`,
    `semantic_embedding_source_rollout_recommendation`) so next memory-family
    rollout step is machine-visible in health and startup diagnostics.
  - strict-rollout preflight posture is now explicit through shared diagnostics
    (`semantic_embedding_strict_rollout_violations`,
    `semantic_embedding_strict_rollout_violation_count`,
    `semantic_embedding_strict_rollout_ready`,
    `semantic_embedding_strict_rollout_state`,
    `semantic_embedding_strict_rollout_hint`,
    `semantic_embedding_strict_rollout_recommendation`) and enforcement
    recommendation/alignment fields
    (`semantic_embedding_recommended_provider_ownership_enforcement`,
    `semantic_embedding_recommended_model_governance_enforcement`,
    `semantic_embedding_provider_ownership_enforcement_alignment`,
    `semantic_embedding_model_governance_enforcement_alignment`,
    `semantic_embedding_enforcement_alignment_state`,
    `semantic_embedding_enforcement_alignment_hint`); startup now emits
    `embedding_strategy_hint` for rollout guidance.
  - source-rollout sequencing posture is now explicit through shared diagnostics
    (`semantic_embedding_source_rollout_order`,
    `semantic_embedding_source_rollout_enabled_sources`,
    `semantic_embedding_source_rollout_missing_sources`,
    `semantic_embedding_source_rollout_next_source_kind`,
    `semantic_embedding_source_rollout_completion_state`,
    `semantic_embedding_source_rollout_phase_index`,
    `semantic_embedding_source_rollout_phase_total`,
    `semantic_embedding_source_rollout_progress_percent`), and startup now
    emits `embedding_source_rollout_hint` while rollout remains in progress.
  - source-rollout enforcement posture is now explicit through
    `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` (`warn|strict`) plus shared
    diagnostics (`semantic_embedding_source_rollout_enforcement`,
    `semantic_embedding_source_rollout_enforcement_state`,
    `semantic_embedding_source_rollout_enforcement_hint`); startup now emits
    `embedding_source_rollout_warning` in warn mode and
    `embedding_source_rollout_block` with fail-fast behavior in strict mode
    while rollout is still pending.
  - source-rollout enforcement recommendation/alignment posture is now explicit
    through shared diagnostics
    (`semantic_embedding_recommended_source_rollout_enforcement`,
    `semantic_embedding_source_rollout_enforcement_alignment`,
    `semantic_embedding_source_rollout_enforcement_alignment_state`,
    `semantic_embedding_source_rollout_enforcement_alignment_hint`), and
    startup now emits `embedding_source_rollout_enforcement_hint` plus
    recommendation/alignment-enriched warning/block logs.
  - refresh cadence and rollout-alignment posture are now explicit through
    shared diagnostics (`semantic_embedding_refresh_cadence_state`,
    `semantic_embedding_refresh_cadence_hint`,
    `semantic_embedding_recommended_refresh_mode`,
    `semantic_embedding_refresh_alignment_state`,
    `semantic_embedding_refresh_alignment_hint`), and startup now emits
    `embedding_refresh_hint` when refresh posture deviates from recommendation.
- Decision (resolved in `PRJ-284`, 2026-04-20):
  - provider ownership baseline:
    - deterministic remains the effective production owner until requested
      provider execution is implemented; fallback diagnostics stay explicit
  - refresh ownership baseline:
    - `on_write` is the rollout baseline owner for vector materialization;
      `manual` stays an explicit operator override with documented process
      expectations
  - memory-family rollout order:
    - phase 1: episodic + semantic materialization baseline
    - phase 2: affective materialization rollout
    - phase 3: relation materialization rollout and full-source completion
  - enforcement rollout posture:
    - keep source-rollout enforcement aligned to `warn` while relation is
      pending; recommend `strict` after full rollout completion
- Follow-up decision:
  - once provider-backed execution exists, decide the production default timing
    for moving from deterministic baseline owner to provider-owned execution

### 5a. Goal And Task Scope

- Current repo fact:
- runtime now loads active goals and active tasks, includes them in the runtime result, refreshes them after Action-layer writes, lets context/motivation/planning react to them, can seed lightweight goals/tasks from explicit user phrases such as `My goal is to ...` and `I need to ...`, can update task status from explicit progress phrases such as `I fixed ...`, and reflection can now derive a lightweight semantic `goal_execution_state` like `blocked`, `recovering`, `advancing`, `progressing`, or `stagnating`, plus a lightweight `goal_progress_score`, `goal_progress_trend`, `goal_progress_arc`, `goal_milestone_state`, `goal_milestone_transition`, `goal_milestone_arc`, `goal_milestone_pressure`, `goal_milestone_dependency_state`, `goal_milestone_due_state`, `goal_milestone_due_window`, `goal_milestone_risk`, and `goal_completion_criteria`; it also persists a short goal-level progress history in `aion_goal_progress`, syncs lightweight `aion_goal_milestone` objects for the active goal focus, persists short `aion_goal_milestone_history` snapshots, and runtime enriches those milestone objects with the current operational arc/pressure/dependency/due/due-window/risk/completion signals without introducing a heavier milestone schema yet.
- Decision needed:
  - should goal and task creation stay limited to explicit user declarations for MVP, or should the system begin inferring and creating them from plans and repeated execution patterns?

### 6. Deployment Path After Coolify

- Current repo fact:
  - docs and compose files already support local Docker and Coolify.
- Decision (PRJ-298 operational baseline, 2026-04-20):
  - Coolify is the active production deployment baseline for this repository.
  - `docker-compose.coolify.yml` is the deployment source of truth for this
    baseline, while `docker-compose.yml` remains local-development oriented.
  - hosting-standard replacement is explicitly future work; runtime slices must
    not assume another deployment platform until operations records that change.
- Remaining follow-up decision:
  - when should the project formally migrate from Coolify baseline to a
    different hosting standard?

### 7. Deployment Trigger Reliability

- Current repo fact:
  - after pushing `main`, production required a manual redeploy from Coolify before the latest commit became live.
  - a manually sent, correctly signed GitHub-style webhook request to the configured Coolify endpoint successfully queued a deployment on 2026-04-15.
  - the repo now has a repeatable release smoke helper for `GET /health` plus `POST /event`, so manual verification no longer depends on hand-written curl snippets.
- Decision (PRJ-298 operational baseline, 2026-04-20):
  - deploy trigger posture is `automation_first_with_explicit_manual_fallback`:
    GitHub/Coolify webhook automation is preferred when it fires correctly.
  - manual fallback remains explicit and supported through
    `scripts/trigger_coolify_deploy_webhook.{ps1,sh}` or direct Coolify UI
    redeploy when automation is missing or delayed.
  - release completion requires running
    `scripts/run_release_smoke.{ps1,sh}` against the deployed URL and treating
    smoke failure as a release-blocking signal.
- Remaining follow-up decision:
  - what objective webhook-delivery SLO should allow manual fallback to become
    exception-only instead of routine fallback posture?

### 8. Language Handling Strategy

- Current repo fact:
  - runtime now makes an explicit per-event language decision and uses
    precedence across current-turn signals, recent-memory continuity, and
    profile continuity.
  - continuity parsing now uses structured episodic payload hints
    (`payload.response_language` and `payload.language`) plus summary fallback,
    while ignoring unsupported language codes.
  - API identity fallback is now explicit and request-scoped
    (`meta.user_id` -> `X-AION-User-Id` -> `anonymous`), reducing accidental
    language/profile bleed from shared anonymous traffic.
- Decision needed:
  - should language handling stay heuristic-plus-profile for the MVP, or should it move to a richer user preference model and broader multilingual support once more channels are added?

### 9. Lightweight Profile Scope

- Current repo fact:
  - runtime now persists lightweight language preference in `aion_profile`
    while semantic response/collaboration preferences stay conclusion-owned in
    `aion_conclusion`.
  - identity loading now keeps that owner boundary explicit: relation fallback
    cues may shape stage behavior but do not become durable profile identity
    fields.
  - runtime builds a lightweight `IdentitySnapshot` from profile language plus
    conclusion/theta inputs without merging those ownership surfaces.
- Decision needed:
  - should `aion_profile` remain limited to durable interaction preferences such as language, while `aion_conclusion` carries generalized learned preferences, or should those concerns merge into one wider identity-linked profile later?

### 9a. Relation System Rollout

- Current repo fact:
  - runtime now persists scoped relation records (`aion_relation`) with
    confidence/source/evidence/decay fields and reflection-driven updates.
  - runtime now loads high-confidence relations and applies relation cues in
    context, role, planning, and expression paths.
- Decision (baseline resolved in `PRJ-330..PRJ-333`, 2026-04-21):
  - relation lifecycle is now explicit:
    - repeated same-value observations refresh confidence/evidence posture
    - value-shift observations reset evidence/decay posture
    - stale relation signals weaken via age-aware revalidation and expire when
      confidence drops below expiration threshold
  - trust influence is now explicit:
    - delivery reliability cues now shape motivation/planning confidence
      posture and proactive interruption/relevance behavior through shared
      adaptive policy owners
  - low-confidence relation cues remain descriptive-only and must not directly
    drive trust-sensitive planning/expression/proactive behavior.
- Follow-up implementation (resolved in `PRJ-343..PRJ-346`, 2026-04-21):
  - inferred goal/task promotion now applies delivery-reliability-aware trust
    thresholds (`low_trust|medium_trust|high_trust`) while explicit
    user-declared intent paths remain unaffected
  - inferred promotion gate diagnostics (`reason=...`, `result=...`) are now
    explicit in planning and runtime debug surfaces

### 10. Preference Influence Scope

- Current repo fact:
- stable `response_style` conclusions now influence context, planning, and expression.
- stable `preferred_role` conclusions can now influence role selection on ambiguous turns.
- stable `collaboration_preference` conclusions can now influence context, role selection, motivation, planning, and expression on ambiguous turns, and explicit user phrases like `step by step` or `do it for me` are now captured as episodic collaboration markers for reflection.
- reflected theta now provides a softer runtime bias toward support, analysis, or execution behavior without hard-overriding explicit signals, and that bias can now shape role selection, motivation mode, planning stance, and expression tone on ambiguous turns.
- Decision (baseline resolved in `PRJ-288`, 2026-04-20):
  - `response_style` remains formatting-oriented and may shape expression/planning structure, not execution ownership
  - `preferred_role` remains a role tie-break signal only, gated by confidence (`>= 0.72`) and ambiguous-turn posture
  - `collaboration_preference` may shape role/motivation/planning/expression only through ambiguous-turn tie-break paths
- Follow-up decision:
  - after `PRJ-289..PRJ-290`, decide whether any preference signal should
    influence proactive or attention-gate posture beyond current foreground
    tie-break scope

### 10a. Action Intent Ownership

- Current repo fact:
  - planning now emits explicit typed `domain_intents` for goal/task/task-status,
    inferred promotion (`promote_inferred_goal`, `promote_inferred_task`),
    maintenance status alignment (`maintain_task_status`), and preference
    updates, plus `noop` when no domain write should occur.
  - action now executes only explicit intents and no longer reparses raw user
    text for durable domain writes.
- Decision (baseline expanded in `PRJ-334..PRJ-336`, 2026-04-21):
  - inferred goal/task growth now remains subordinate to explicit typed-intent
    ownership in planning contracts
  - repeated-blocker maintenance writes now also require explicit typed
    intents before action can mutate durable task state
  - duplicate/no-unsafe inferred promotion behavior is now regression-pinned
    in planning and runtime suites.
- Follow-up decision:
  - decide whether additional future writes (for example relation lifecycle
    maintenance or proactive scheduling state) should also require dedicated
    typed intents instead of reusing generic intent families.

### 10b. Adaptive Signal Governance

- Current repo fact:
  - reflection now requires outcome evidence and user-visible cues for
    adaptive updates (`preferred_role`, `theta`, collaboration fallback) to
    reduce feedback loops from role-only traces.
- Decision (resolved in `PRJ-288`, 2026-04-20):
  - adaptive influence now has one explicit baseline policy contract in
    `docs/architecture/16_agent_contracts.md`
  - evidence thresholds are explicit:
    - relation cues require confidence `>= 0.68` (`>= 0.70` for role
      collaboration tie-break)
    - role preference tie-break requires `preferred_role_confidence >= 0.72`
    - theta influence requires dominant bias `>= 0.58`
  - signal precedence is explicit:
    - affective safety/support cues first
    - relation/preference cues next
    - theta last
  - below-threshold adaptive signals are descriptive-only and must not alter
    role, motivation mode, planning steps, or expression tone
- Follow-up decision:
  - complete shared policy-owner adoption across role/motivation/planning
    (`PRJ-289`) and attention/proactive consumers (`PRJ-290`)

### 11. Theta Scope And Durability

- Current repo fact:
  - reflection now updates a lightweight `aion_theta` state from repeated recent role patterns, and runtime can use that state as a soft bias for role selection, motivation, planning, and expression on ambiguous turns.
- Decision (interim baseline resolved in `PRJ-288`, 2026-04-20):
  - theta stays a lightweight adaptive tie-break signal, not a dominant
    identity owner
  - theta influence remains ambiguity-gated and threshold-gated
    (`dominant_bias >= 0.58`)
- Follow-up decision:
  - after adaptive-governance regressions in `PRJ-291`, decide whether theta
    should remain bounded to tie-break posture or gain broader long-horizon
    influence

### 12. Scheduler And Proactive Runtime

- Current repo fact:
  - scheduler event normalization contracts are now explicit, including cadence
    and source/subsource runtime boundaries.
  - runtime config now includes scheduler/reflection/maintenance/proactive
    interval controls.
  - an in-process scheduler worker can now run reflection and maintenance
    cadence (`SCHEDULER_ENABLED`) and exposes scheduler posture/tick summaries
    through `GET /health`.
  - proactive scheduler ticks now run through a dedicated decision engine with
    interruption-cost guardrails and typed plan/motivation outputs.
  - proactive delivery now enforces baseline guardrails (user opt-in, outbound
    and unanswered throttle checks, delivery-target requirement) before outreach.
- Decision (PRJ-322 scheduler execution owner posture, 2026-04-20):
  - scheduler cadence execution mode is now explicit through
    `SCHEDULER_EXECUTION_MODE` (`in_process|externalized`)
  - `/health.scheduler` now exposes owner-mode and readiness posture
    (`execution_mode`, cadence owners, dispatch reasons, blocker list)
- Decision (PRJ-323 shared cadence dispatch boundary, 2026-04-20):
  - maintenance and proactive cadence now share one owner-aware dispatch
    boundary in runtime contracts
  - maintenance execution now explicitly no-ops under externalized owner posture
    instead of relying on implicit in-process assumptions
- Decision (PRJ-301 scheduler/reflection baseline, 2026-04-20):
  - scheduled reflection baseline stays in-process first
    (`REFLECTION_RUNTIME_MODE=in_process`) with durable enqueue semantics.
  - deferred reflection dispatch remains opt-in and requires the explicit
    readiness criteria recorded in decision `1`.
- Decision (PRJ-308 maintenance/proactive cadence ownership boundary, 2026-04-20):
  - long-term target posture:
    - cadence ownership for maintenance and proactive wakeups moves to a
      dedicated external scheduler path after reflection external-dispatch
      posture is stable
    - app-local scheduler ownership remains transitional and local-development
      friendly, not the final production ownership model
  - ownership boundaries:
    - runtime keeps event-contract normalization, guardrail evaluation, and
      conscious execution boundaries for scheduled events
    - external scheduler owner controls cadence triggering, retry/backoff
      operations, and production on-call ownership for scheduler availability
  - rollout guardrails:
    - move production cadence ownership only after explicit runbook ownership,
      idempotent scheduler-event contract checks, and release smoke coverage for
      selected owner path
    - keep app-local scheduler as explicit fallback while external ownership
      SLOs and rollback path are being proven
- Remaining follow-up decision:
  - with `PRJ-295` complete, should conscious attention boundary ownership
    remain in-process coordination, or move to a dedicated durable
    attention-inbox owner in later rollout?

### 12a. Attention Inbox And Turn Assembly

- Current repo fact:
  - runtime contracts now expose explicit graph-state surfaces for
    `attention_inbox`, `pending_turn`, `subconscious_proposals`, and
    `proposal_handoffs`.
  - `POST /event` now executes baseline Telegram burst-message coalescing with
    `pending|claimed|answered` turn ownership; duplicate/non-owner burst events
    are returned as queued no-op responses instead of running duplicate
    foreground turns.
  - `GET /health` now exposes an explicit `attention` snapshot with
    `burst_window_ms`, turn TTL values, and `pending|claimed|answered`
    counters, making burst-coalescing posture operator-visible.
  - attention timing now has explicit runtime config controls:
    `ATTENTION_BURST_WINDOW_MS`, `ATTENTION_ANSWERED_TTL_SECONDS`,
    `ATTENTION_STALE_TURN_SECONDS`.
- Decision (PRJ-292 baseline):
  - attention boundary is the canonical owner of turn assembly, pending-turn
    state, and burst-message coalescing status transitions.
  - timing windows remain config-owned by the attention boundary through
    `ATTENTION_BURST_WINDOW_MS`, `ATTENTION_ANSWERED_TTL_SECONDS`, and
    `ATTENTION_STALE_TURN_SECONDS`.
- Decision (PRJ-324 attention owner posture, 2026-04-20):
  - attention coordination owner mode is now explicit through
    `ATTENTION_COORDINATION_MODE` (`in_process|durable_inbox`)
  - `/health.attention` now exposes owner-mode deployment readiness posture
    (`coordination_mode`, `turn_state_owner`, `deployment_readiness`) for
    durable-inbox rollout preparation
- Remaining follow-up decision:
  - what production-default timing values should be promoted as the release
    baseline once dual-loop rollout stabilizes?

### 12b. Conscious vs Subconscious Coordination Boundary

- Current repo fact:
  - the architecture already states that subconscious processing does not
    communicate directly with the user, and runtime contracts now model a
    first-class proposal handoff surface between subconscious and conscious
    paths.
  - proposal persistence/promotion now runs end to end in live runtime:
    reflection persists proposal records, runtime loads retriable proposal
    states (`pending|deferred`), planning emits conscious handoff decisions, and
    runtime resolves proposal lifecycle status from those decisions.
  - planning now includes explicit proposal persistence, conscious promotion
    rules, read-only subconscious tool policy, and separate wakeup/cadence
    slices (`PRJ-088..PRJ-091`).
- Decision (PRJ-292 baseline):
  - subconscious outputs become durable proposals in the explicit proposal
    contract surface (`ask_user`, `research_topic`, `suggest_goal`,
    `nudge_user`, `suggest_connector_expansion`), not immediate actions.
  - conscious planning is the canonical owner of proposal handoff decisions
    (`accept|merge|defer|discard`) and corresponding durable status mapping
    (`accepted|merged|deferred|discarded`).
  - subconscious research remains read-only by default (`research_policy=read_only`);
    any broader authority requires a future architecture-contract change.
- Remaining follow-up decision:
  - should future proposal classes add new conscious decisions beyond
    `accept|merge|defer|discard`, or keep this decision set fixed?

### 12c. Internal Planning State And External Connector Boundary

- Current repo fact:
  - internal goals/tasks already influence cognition and action, but the repo
    does not yet define a connector contract for calendar, task-system, or
    cloud-drive integrations.
  - planning now includes explicit connector and permission-gate slices
    (`PRJ-087`, `PRJ-093..PRJ-097`).
- Decision needed:
  - where should the system draw the line between internal planning state and
    user-authorized external productivity systems?
  - which connector operations should default to read-only, which should be
    suggestion-only, and which are safe to execute directly once the user opted
    in?
  - how should the personality propose new capabilities or connectors without
    self-authorizing access to outside systems?

### 13. Runtime Behavior Validation Surface

- Current repo fact:
  - the repository has broad unit and integration coverage plus runtime-policy,
    health, scheduler, and memory contract tests.
  - canonical behavior-validation contract now exists in
    `docs/architecture/29_runtime_behavior_testing.md`.
  - internal debug responses now expose an explicit `system_debug` payload with
    event normalization metadata, memory bundle visibility, context,
    motivation, role, plan intents, expression, and action result traces.
  - behavior-harness helpers now emit structured scenario outputs
    (`test_id`, `status`, `reason`, `trace_id`, `notes`) for repeatable
    execution and evidence capture.
  - practical testing has shown that a subsystem can look well implemented
    through contracts and still fail to influence later behavior in a useful
    way (for example memory that persists but does not shape future turns).
- Decision (resolved in `PRJ-310..PRJ-317`, 2026-04-20):
  - mandatory internal debug fields are now defined and implemented through the
    shared `system_debug` validation surface.
  - behavior-driven scenario checks are now part of release-readiness evidence
    through `scripts/run_behavior_validation.{ps1,sh}`.
  - required scenario families now include:
    - memory `write -> retrieve -> influence -> delayed recall`
    - multi-session continuity and personality stability
    - contradiction, missing-data, and noisy-input resilience
- Remaining follow-up decision:
  - behavior-validation CI-ingestion follow-up is now queued in
    `PRJ-347..PRJ-350` to decide and implement machine-readable artifact and
    gate posture without removing existing command-and-evidence release checks.
