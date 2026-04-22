# PROJECT_STATE

Last updated: 2026-04-22

## Product Snapshot

- Name: Personality / AION
- Goal: build a memory-aware AI runtime that receives events, reasons through a
  structured pipeline, replies through API or Telegram, and learns lightweight
  user preferences over time
- Commercial model: TBD
- Current phase: post-convergence follow-up discovery and hardening

## Product Decisions (Confirmed)

- 2026-04-16: this repo uses a project-specific agent workflow adapted to the
  Python, FastAPI, and AION stack.
- 2026-04-16: reflection is treated as a real app-local durable worker concern,
  not as a purely hypothetical future subsystem.
- 2026-04-17: `POST /event` exposes the smaller public response by default and
  the full internal runtime result only through `debug=true`.
- 2026-04-17: episodic memory persists both typed JSON payloads and a
  human-readable summary, with payload-first readers and legacy fallback.
- 2026-04-17: motivation uses only the documented shared mode set
  (`respond|ignore|analyze|execute|clarify`).
- 2026-04-18: runtime stages emit structured `start/success/failure` logs with
  `event_id`, `trace_id`, stage name, duration, and short summaries through the
  shared scaffold in `app/core/logging.py`.
- 2026-04-18: goal/task selection and progress-history signal logic now has
  shared utility owners in `app/utils/goal_task_selection.py` and
  `app/utils/progress_signals.py`, and runtime heuristics consume those helpers
  across context, planning, motivation, and reflection.
- 2026-04-18: event normalization now enforces an explicit API boundary
  (`source=api`, `subsource=event_endpoint`, normalized `payload.text`) and
  keeps debug details behind the explicit debug response path.
- 2026-04-18: startup schema ownership now defaults to migration-first behavior,
  while `create_tables()` remains only as an explicit compatibility mode.
- 2026-04-18: runtime now passes an explicit `ActionDelivery` contract from
  expression into action, keeping side effects inside action while reducing
  implicit stage coupling.
- 2026-04-18: action delivery now routes through an integration-level
  dispatcher (`DeliveryRouter`) so channel dispatch logic is owned by
  integrations while the action boundary remains explicit.
- 2026-04-19: startup now emits an explicit production warning when
  `EVENT_DEBUG_ENABLED=true`, so debug payload exposure policy is visible in
  logs before serving requests.
- 2026-04-19: debug payload exposure now uses environment-aware defaults:
  enabled by default in non-production, disabled by default in production
  unless explicitly enabled.
- 2026-04-19: production runtime policy checks now support explicit enforcement
  mode (`warn|strict`), so policy mismatches can be warning-only or fail-fast
  on startup.
- 2026-04-19: startup strict-policy fail-fast behavior is now pinned with a
  lifespan-level regression test that verifies block-before-database-init.
- 2026-04-19: startup strict-policy fail-fast lifecycle coverage now spans both
  mismatch families (debug exposure and schema compatibility mode).
- 2026-04-19: runtime policy mismatch detection now has a shared owner reused by
  startup and `/health`, and health now exposes a mismatch preview list for
  operator triage.
- 2026-04-19: runtime policy now exposes strict-rollout readiness signals
  (`production_policy_mismatch_count`, `strict_startup_blocked`,
  `strict_rollout_ready`) through shared helpers reused by startup and `/health`.
- 2026-04-19: runtime policy now also exposes strict-rollout recommendation
  signals (`recommended_production_policy_enforcement`, `strict_rollout_hint`),
  and startup emits an informational hint when production warn mode is strict-ready.
- 2026-04-19: debug payload access now supports optional token gating via
  `EVENT_DEBUG_TOKEN`, with policy visibility and startup warnings aligned.
- 2026-04-19: API event normalization now supports `X-AION-User-Id` fallback
  (when `meta.user_id` is missing), making user-scoped language/profile memory
  handling safer for multi-user API traffic.
- 2026-04-21: runtime now has a shared `identity_policy` owner for profile
  language continuity versus conclusion-owned learned preferences, and the
  same baseline is exposed through `/health.identity` and runtime
  `system_debug.adaptive_state.identity_policy`.
- 2026-04-21: language continuity now also has explicit operator/debug
  posture: `/health.identity.language_continuity` exposes the baseline
  precedence and supported codes, while runtime
  `system_debug.adaptive_state.language_continuity` exposes selected source,
  candidate continuity inputs, and fallback posture for the current event.
- 2026-04-19: runtime now carries a first-class affective contract slot
  (`affect_label`, `intensity`, `needs_support`, `confidence`, `source`,
  `evidence`) populated by deterministic perception placeholders.
- 2026-04-19: runtime now includes an AI-assisted affective assessor stage with
  deterministic fallback, so affective source can be traced as
  `ai_classifier` or `fallback` in stage-level runtime logs.
- 2026-04-19: motivation, role, and expression now consume
  `perception.affective` as the primary support/emotion signal, making
  supportive behavior traceable to one affective owner across runtime stages.
- 2026-04-19: empathy-oriented regression fixtures now pin emotionally heavy,
  ambiguous, and mixed-intent support quality across motivation, expression,
  and runtime integration tests.
- 2026-04-19: conclusions now support scoped storage
  (`scope_type=global|goal|task`, `scope_key`) and reflection writes
  goal-operational conclusions with goal scope, enabling scope-aware repository
  queries.
- 2026-04-19: runtime memory consumers now resolve scoped reflection state by
  primary active goal with global fallback, reducing cross-goal leakage across
  context, motivation, planning, and milestone enrichment.
- 2026-04-19: episodic payloads now persist lightweight affective tags and
  reflection derives reusable affective conclusions
  (`affective_support_pattern`, `affective_support_sensitivity`) consumed by
  runtime preferences, context summaries, and motivation scoring.
- 2026-04-19: runtime memory retrieval now loads deeper context
  (`MEMORY_LOAD_LIMIT=12`) and ranks memory candidates with affective relevance
  in addition to language, layer mode, topical overlap, and importance.
- 2026-04-19: repository and docs now share explicit memory-layer vocabulary
  (`episodic`, `semantic`, `affective`, `operational`) with layer-aware
  repository APIs for episodic retrieval, conclusion filtering, and operational
  memory reads.
- 2026-04-19: planning now emits explicit typed `domain_intents`
  (`upsert_goal`, `upsert_task`, `update_task_status`,
  `update_response_style`, `update_collaboration_preference`, `noop`), and
  action now executes only those intents for durable domain writes.
- 2026-04-19: reflection logic is now split into concern-owned modules
  (`goal_conclusions`, `adaptive_signals`, `affective_signals`), keeping
  worker orchestration separate from inference ownership.
- 2026-04-19: adaptive reflection signals (`preferred_role`, `theta`,
  collaboration fallback) now require outcome evidence and user-visible cues,
  reducing self-reinforcement loops from role-only traces.
- 2026-04-20: canonical adaptive influence governance policy is now explicit in
  architecture contracts, including evidence thresholds, precedence, and
  tie-break boundaries for affective, relation, preference, and theta signals.
- 2026-04-19: milestone pressure heuristics now prefer phase consistency and
  arc/transition evidence over pure time-window drift.
- 2026-04-19: runtime now exposes an explicit graph migration boundary through
  `GraphRuntimeState` contracts, runtime-result conversion helpers, and
  graph-compatible stage adapters around current foreground modules.
- 2026-04-19: foreground stage orchestration (`perception -> ... -> action`)
  now runs through LangGraph `StateGraph` nodes while preserving stage-level
  contracts, logs, and existing runtime/API behavior.
- 2026-04-19: documentation now explicitly separates canonical architecture in
  `docs/architecture/` from transitional implementation reality in
  `docs/implementation/runtime-reality.md`, so human-oriented design intent can
  stay stable while runtime details remain searchable.
- 2026-04-19: OpenAI prompt construction now supports optional LangChain
  templates through a compatibility wrapper while preserving non-LangChain
  fallback behavior.
- 2026-04-19: semantic retrieval contracts and storage are now explicit:
  embedding/retrieval contract types, pgvector-ready schema scaffolding, and
  deterministic embedding fallback helpers are all first-class runtime surfaces.
- 2026-04-19: runtime memory retrieval now supports hybrid lexical + vector
  scoring across episodic, semantic, and affective memory layers, with
  diagnostics emitted for retrieval observability.
- 2026-04-19: semantic vector retrieval posture is now explicit through
  `SEMANTIC_VECTOR_ENABLED`; runtime/action now honor that gate and
  `GET /health` exposes `memory_retrieval.semantic_vector_enabled` plus
  `memory_retrieval.semantic_retrieval_mode`
  (`hybrid_vector_lexical|lexical_only`).
- 2026-04-22: retrieval provider completion now treats `openai` as the target
  provider-owned production baseline when `OPENAI_API_KEY` is configured,
  keeps `local_hybrid` as an explicit local transition path, and keeps
  deterministic execution as the compatibility fallback baseline.
- 2026-04-22: embedding materialization now has one shared owner path across
  repository and action persistence; OpenAI provider-owned execution uses a
  dedicated client, while `/health.memory_retrieval` exposes
  `semantic_embedding_production_baseline`,
  `semantic_embedding_production_baseline_state`, and
  `semantic_embedding_production_baseline_hint` for rollout triage.
- 2026-04-19: embedding strategy posture is now explicit through
  `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, and `EMBEDDING_DIMENSIONS` with
  deterministic-fallback visibility in `GET /health.memory_retrieval`
  (requested vs effective provider/model plus fallback hint).
- 2026-04-19: embedding provider readiness posture is now explicit through
  `GET /health.memory_retrieval` fields
  (`semantic_embedding_provider_ready`,
  `semantic_embedding_posture=ready|fallback_deterministic`) and startup now
  emits `embedding_strategy_warning` when requested provider posture falls
  back to deterministic execution.
- 2026-04-19: `MemoryRepository` now persists conclusion embedding shells with
  configured effective embedding posture (model/dimensions) and explicit
  requested-vs-effective provider metadata instead of hardcoded
  `pending/0` placeholders.
- 2026-04-19: embedding strategy warning posture semantics are now shared
  across startup logging and `/health.memory_retrieval` through one helper,
  with explicit warning fields
  (`semantic_embedding_warning_state`, `semantic_embedding_warning_hint`).
- 2026-04-19: embedding persistence scope is now explicit through
  `EMBEDDING_SOURCE_KINDS`; action/repository embedding writes respect enabled
  source families, and `/health.memory_retrieval` exposes configured source
  kinds for operator visibility.
- 2026-04-19: embedding source-coverage posture for current retrieval path is
  now explicit across `/health.memory_retrieval` and startup warning logs via
  shared coverage-state semantics.
- 2026-04-19: embedding refresh-cadence posture is now explicit through
  `EMBEDDING_REFRESH_MODE` (`on_write|manual`) and
  `EMBEDDING_REFRESH_INTERVAL_SECONDS`; `/health.memory_retrieval` exposes
  refresh posture fields and startup emits `embedding_refresh_warning` when
  vectors are enabled in manual mode.
- 2026-04-19: embedding refresh posture semantics are now owned by the shared
  embedding strategy helper, including derived refresh diagnostics
  (`semantic_embedding_refresh_state`,
  `semantic_embedding_refresh_hint`) reused by both `/health.memory_retrieval`
  and startup warning flow.
- 2026-04-19: embedding model-governance posture is now explicit through shared
  diagnostics (`semantic_embedding_model_governance_state`,
  `semantic_embedding_model_governance_hint`) reused by `/health.memory_retrieval`
  and startup warning flow (`embedding_model_governance_warning`).
- 2026-04-19: embedding provider-ownership posture is now explicit through
  shared diagnostics (`semantic_embedding_provider_ownership_state`,
  `semantic_embedding_provider_ownership_hint`) reused by
  `/health.memory_retrieval` and startup fallback warning flow.
- 2026-04-19: embedding provider-ownership enforcement posture is now explicit
  through `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` (`warn|strict`) and shared
  enforcement diagnostics in `/health.memory_retrieval`; strict mode can now
  block startup when provider ownership fallback remains active.
- 2026-04-19: embedding model-governance enforcement posture is now explicit
  through `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` (`warn|strict`) and shared
  enforcement diagnostics in `/health.memory_retrieval`; strict mode can now
  block startup for deterministic custom-model-name governance violations.
- 2026-04-19: embedding owner-strategy recommendation posture is now explicit
  through shared diagnostics
  (`semantic_embedding_owner_strategy_state`,
  `semantic_embedding_owner_strategy_hint`,
  `semantic_embedding_owner_strategy_recommendation`) reused by
  `/health.memory_retrieval` and startup fallback warning flow.
- 2026-04-19: embedding source-rollout recommendation posture is now explicit
  through shared diagnostics
  (`semantic_embedding_source_rollout_state`,
  `semantic_embedding_source_rollout_hint`,
  `semantic_embedding_source_rollout_recommendation`) reused by
  `/health.memory_retrieval` and startup source-coverage warning flow.
- 2026-04-20: embedding strict-rollout preflight posture is now explicit
  through shared diagnostics
  (`semantic_embedding_strict_rollout_violations`,
  `semantic_embedding_strict_rollout_violation_count`,
  `semantic_embedding_strict_rollout_ready`,
  `semantic_embedding_strict_rollout_state`,
  `semantic_embedding_strict_rollout_hint`) reused by `/health` and startup.
- 2026-04-20: embedding strict-rollout recommendation and enforcement-alignment
  posture are now explicit through shared diagnostics
  (`semantic_embedding_strict_rollout_recommendation`,
  `semantic_embedding_recommended_provider_ownership_enforcement`,
  `semantic_embedding_recommended_model_governance_enforcement`,
  `semantic_embedding_provider_ownership_enforcement_alignment`,
  `semantic_embedding_model_governance_enforcement_alignment`,
  `semantic_embedding_enforcement_alignment_state`,
  `semantic_embedding_enforcement_alignment_hint`) in
  `/health.memory_retrieval`.
- 2026-04-20: startup now emits `embedding_strategy_hint` with strict-rollout
  readiness, violation summary, recommendation, and enforcement-alignment
  diagnostics from one shared embedding strategy snapshot owner.
- 2026-04-20: source-rollout sequencing posture is now explicit through shared
  diagnostics
  (`semantic_embedding_source_rollout_order`,
  `semantic_embedding_source_rollout_enabled_sources`,
  `semantic_embedding_source_rollout_missing_sources`,
  `semantic_embedding_source_rollout_next_source_kind`,
  `semantic_embedding_source_rollout_completion_state`,
  `semantic_embedding_source_rollout_phase_index`,
  `semantic_embedding_source_rollout_phase_total`,
  `semantic_embedding_source_rollout_progress_percent`) in
  `/health.memory_retrieval`.
- 2026-04-20: source-rollout state now distinguishes relation-inclusive full
  activation posture (`all_vector_sources_enabled`) from semantic+affective
  baseline rollout posture.
- 2026-04-20: startup now emits `embedding_source_rollout_hint` whenever
  vectors are enabled and source rollout still has a pending next source kind.
- 2026-04-20: refresh cadence posture is now explicit through shared diagnostics
  (`semantic_embedding_refresh_cadence_state`,
  `semantic_embedding_refresh_cadence_hint`) in `/health.memory_retrieval`.
- 2026-04-20: refresh recommendation and alignment posture are now explicit
  through shared diagnostics (`semantic_embedding_recommended_refresh_mode`,
  `semantic_embedding_refresh_alignment_state`,
  `semantic_embedding_refresh_alignment_hint`) in `/health.memory_retrieval`.
- 2026-04-20: startup now emits `embedding_refresh_hint` whenever refresh
  posture deviates from rollout recommendation, and manual refresh warnings now
  include cadence diagnostics.
- 2026-04-20: source-rollout enforcement posture is now explicit through
  `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` (`warn|strict`) plus shared
  diagnostics (`semantic_embedding_source_rollout_enforcement`,
  `semantic_embedding_source_rollout_enforcement_state`,
  `semantic_embedding_source_rollout_enforcement_hint`) in
  `/health.memory_retrieval`; startup now emits
  `embedding_source_rollout_warning` in warn mode and
  `embedding_source_rollout_block` in strict mode for pending rollout states.
- 2026-04-20: source-rollout enforcement recommendation/alignment posture is
  now explicit through shared diagnostics
  (`semantic_embedding_recommended_source_rollout_enforcement`,
  `semantic_embedding_source_rollout_enforcement_alignment`,
  `semantic_embedding_source_rollout_enforcement_alignment_state`,
  `semantic_embedding_source_rollout_enforcement_alignment_hint`) in
  `/health.memory_retrieval`; startup now emits
  `embedding_source_rollout_enforcement_hint` and warning/block logs include
  the same recommendation/alignment diagnostics.
- 2026-04-19: relation memory is now a first-class subsystem (`aion_relation`)
  with scoped repository APIs; reflection derives relation updates and runtime
  stages now consume high-confidence relation cues across context, role,
  planning, and expression.
- 2026-04-19: scheduler-originated event contracts and cadence boundaries are
  now explicit (`scheduler_enabled`, reflection/maintenance/proactive
  intervals), preparing the runtime for scheduled and out-of-process execution.
- 2026-04-19: reflection runtime mode is now explicit (`in_process|deferred`);
  runtime persists reflection enqueue tasks even without in-process worker
  ownership, and reflection worker now supports one-shot pending-task execution
  for future scheduler/out-of-process drivers.
- 2026-04-19: scheduler cadence is now live for reflection and maintenance;
  scheduler runtime uses contract-bounded intervals, mode-aware reflection
  dispatch guardrails, and `/health` scheduler visibility for operations.
- 2026-04-19: subconscious proposal persistence and conscious handoff decisions
  are now explicit runtime owners, including read-only subconscious research
  policy/tool boundaries and proposal lifecycle tracking.
- 2026-04-19: proactive scheduler flow now applies an explicit attention gate
  before outreach planning, and connector-facing planning contracts now include
  permission gates plus typed calendar/task synchronization intents.
- 2026-04-19: `POST /event?debug=true` now emits explicit compatibility headers
  (`X-AION-Debug-Compat`, `Link`) that point to `POST /event/debug`, keeping
  migration intent machine-visible while preserving backward compatibility.
- 2026-04-20: internal debug ingress ownership now uses
  `POST /internal/event/debug` as the primary `system_debug` boundary;
  `POST /event/debug` is now explicit shared-route compatibility ingress, and
  `POST /event?debug=true` compatibility headers now point to the internal
  route.
- 2026-04-20: shared debug ingress posture is now explicitly configurable
  (`EVENT_DEBUG_SHARED_INGRESS_MODE=compatibility|break_glass_only`); in
  `break_glass_only` mode `POST /event/debug` requires explicit
  `X-AION-Debug-Break-Glass: true` override while internal ingress
  `POST /internal/event/debug` remains the primary diagnostics path.
- 2026-04-19: `/health` now exposes explicit attention turn-assembly posture
  (`burst_window_ms`, turn TTLs, `pending|claimed|answered` counters), making
  burst-coalescing diagnostics operator-visible without changing runtime turn
  behavior.
- 2026-04-19: attention turn-assembly timing is now explicitly configurable via
  runtime env/config (`ATTENTION_BURST_WINDOW_MS`,
  `ATTENTION_ANSWERED_TTL_SECONDS`, `ATTENTION_STALE_TURN_SECONDS`) with
  bounded validation and startup wiring into the shared coordinator.
- 2026-04-19: production debug payload access now supports explicit
  token-requirement policy (`PRODUCTION_DEBUG_TOKEN_REQUIRED`, default `true`);
  debug endpoints reject production access when debug exposure is enabled but no
  token is configured under that policy mode.
- 2026-04-19: runtime policy now exposes explicit debug hardening posture
  (`debug_access_posture`, `debug_token_policy_hint`) across health and startup
  policy logging, including dedicated warnings for relaxed
  `PRODUCTION_DEBUG_TOKEN_REQUIRED=false` production debug mode.
- 2026-04-19: strict production policy mismatch posture now includes
  `event_debug_token_missing=true` when debug exposure is enabled, token
  requirement mode is active, and no debug token is configured.
- 2026-04-19: compatibility debug query route posture is now explicitly
  hardening-oriented: `EVENT_DEBUG_QUERY_COMPAT_ENABLED` defaults to disabled
  in production, startup warnings surface explicit production opt-in, and
  strict mismatch previews include `event_debug_query_compat_enabled=true`
  when compatibility route stays enabled in production.
- 2026-04-19: compatibility `POST /event?debug=true` sunset readiness is now
  operator-visible through in-process telemetry
  (`event_debug_query_compat_telemetry`) and explicit compat deprecation
  response header (`X-AION-Debug-Compat-Deprecated=true`).
- 2026-04-19: `/health.runtime_policy` now includes compat sunset decision
  signals (`event_debug_query_compat_allow_rate`,
  `event_debug_query_compat_block_rate`,
  `event_debug_query_compat_recommendation`) derived from telemetry outcomes.
- 2026-04-19: `/health.runtime_policy` now also includes explicit compat sunset
  decision fields (`event_debug_query_compat_sunset_ready`,
  `event_debug_query_compat_sunset_reason`) for machine-readable
  go/no-go posture.
- 2026-04-19: `/health.runtime_policy` now also exposes rolling compat trend
  signals (`event_debug_query_compat_recent_attempts_total`,
  `event_debug_query_compat_recent_allow_rate`,
  `event_debug_query_compat_recent_block_rate`,
  `event_debug_query_compat_recent_state`) derived from telemetry snapshots.
- 2026-04-19: compat recommendation and sunset posture now treat any observed
  compat attempts as migration-needed, while rolling-window trend signals remain
  explicit release-window diagnostics.
- 2026-04-19: compat rolling-window size is now configurable via
  `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` (default `20`, minimum `1`) and is
  wired consistently across lifespan and request-level telemetry fallback.
- 2026-04-19: compat-route freshness posture is now explicit in
  `/health.runtime_policy`
  (`event_debug_query_compat_stale_after_seconds`,
  `event_debug_query_compat_last_attempt_age_seconds`,
  `event_debug_query_compat_last_attempt_state`) with config-driven stale-age
  threshold via `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`.
- 2026-04-19: `/health.runtime_policy` now also exposes compat activity posture
  fields (`event_debug_query_compat_activity_state`,
  `event_debug_query_compat_activity_hint`) so operators can distinguish
  disabled/no-attempt/stale-history/recent-traffic compat dependency states
  without weakening existing sunset-ready contract semantics.

## Technical Baseline

- Backend: Python 3.11, FastAPI, Pydantic v2
- Frontend: none in current repository scope
- Mobile: none in current repository scope
- Database: PostgreSQL with SQLAlchemy async and asyncpg
- Infra: Docker Compose locally, Coolify-targeted compose for deployment
- Hosting target: VPS deployment via Compose/Coolify-oriented runtime docs
- Deployment shape: API-first runtime with app-local reflection worker behavior
- Runtime services: FastAPI app, database, optional Telegram webhook path
- Background jobs / workers: reflection runs as an app-local durable concern;
  scheduler cadence can now trigger reflection/maintenance routines in-process,
  and reflection runtime mode can be `in_process` or `deferred`
- Persistent storage: PostgreSQL
- Health / readiness checks: `GET /health`, `POST /event` smoke, optional
  Telegram webhook verification
- Environment files: `.env`, Docker Compose env wiring, deployment env values
  documented in runtime ops docs
- Observability: stage timings and structured stage-level runtime logs both
  exist
- MCP / external tools: Playwright available locally for future browser-driven
  checks

## Validation Commands

- Lint: not configured yet
- Typecheck: not configured yet
- Unit tests: `.\.venv\Scripts\python -m pytest -q`
- Integration tests: `.\.venv\Scripts\python -m pytest -q tests/<file>.py`
- E2E / smoke: `docker compose up --build`
- Other high-risk checks:
  - `curl http://localhost:8000/health`
  - `curl -X POST http://localhost:8000/event ...`
  - Telegram webhook setup or delivery smoke when integration code changes

## Deployment Contract

- Primary deploy path: Docker Compose locally and Coolify-targeted container
  deployment
- Coolify app/service layout: documented in `docs/operations/runtime-ops-runbook.md`
- Dockerfiles / compose paths: `docker-compose.yml`, project Docker assets in
  repo root
- Required secrets: OpenAI credentials, database connection, Telegram bot
  configuration where relevant
- Public URLs / ports: local API default `http://localhost:8000`
- Backup / restore expectation: database safety and release smoke remain part of
  runtime ops runbook
- Rollback trigger and method: revert to previous container/image plus rerun
  health and `/event` smoke

## Current Focus

- Main active objective: make stage boundaries and architecture traceability
  explicit without regressing current runtime behavior, then deepen the runtime
  toward affective understanding, scoped memory, and stronger action intent
  ownership
- Active `PRJ` execution queue is complete through `PRJ-299`; execution is
  now in Group 19 production memory retrieval rollout after completing Group 18
  background reflection topology and baseline definition in `PRJ-284`.
- `PRJ-288` is the current `READY` implementation slice to define adaptive
  evidence thresholds and influence governance before adaptive signals spread
  further through runtime behavior.
- Top blockers:
  - runtime currently emits connector intents and permission gates but does not
    yet execute provider-backed calendar/task/drive integrations
- Success criteria for this phase:
  - shared goal and milestone signals keep one clear implementation owner
  - runtime stage decisions are observable through structured logs
  - event and startup contracts stay explicit and regression-covered
  - docs, task board, learning journal, and code stay synchronized after each
    slice

## Recent Progress

- 2026-04-20: `PRJ-287` is complete: production retrieval rollout posture is
  now regression-pinned across embedding-strategy, health API, context, and
  runtime pipeline suites, and planning/context docs are synchronized to the
  post-PRJ-286 rollout state.
- 2026-04-20: `PRJ-286` is complete: affective and relation embedding families
  now participate in source-gated rollout with explicit refresh ownership
  metadata (`materialized_on_write` vs `pending_manual_refresh`), and relation
  vectors are now materialized when relation source rollout is enabled.
- 2026-04-20: `PRJ-285` is complete: semantic conclusion embeddings now
  materialize vectors on write (with deterministic fallback posture when
  requested provider execution is unavailable), and episodic embeddings now
  honor explicit refresh ownership (`on_write` vs `manual`) with materialization
  status metadata.
- 2026-04-20: `PRJ-284` is complete: production retrieval baseline is now
  explicitly defined in canonical planning/architecture/runtime-reality/ops
  docs for provider ownership, refresh ownership, and family rollout order
  (`episodic+semantic -> affective -> relation`).
- 2026-04-20: `PRJ-283` is complete: background-topology regressions now pin
  worker-mode handoff guarantees across `/health.reflection.topology`,
  scheduler runtime log posture, and reflection retry skip semantics for
  exhausted tasks.
- 2026-04-20: `PRJ-282` is complete: `/health.reflection.topology` now exposes
  explicit handoff ownership for enqueue/dispatch/queue-drain/retry posture,
  and scheduler reflection tick logs now include mode-aware handoff fields for
  in-process versus external-driver operation.
- 2026-04-20: `PRJ-281` is complete: runtime and scheduler now share one
  reflection enqueue/dispatch boundary contract, with explicit mode-aware
  dispatch decisions (`in_process|deferred`) and regression coverage for the
  shared boundary behavior.
- 2026-04-20: `PRJ-280` is complete: reflection topology ownership is now
  explicit across `in_process|deferred` worker modes, durable queue semantics,
  and operator health posture boundaries in canonical docs and runtime reality.
- 2026-04-20: `PRJ-279` is complete: foreground architecture-parity regressions
  now pin runtime/API/logging boundary order invariants, and planning/context
  docs are synchronized to the converged foreground boundary.
- 2026-04-20: `PRJ-278` is complete: graph/runtime orchestration boundaries are
  now explicit in orchestrator structure (`pre-graph seed`, `graph run`,
  `post-graph follow-up`) with regression coverage.
- 2026-04-20: `PRJ-277` is complete: expression now emits an explicit
  response-execution handoff contract consumed by action, reducing implicit
  delivery coupling.
- 2026-04-20: `PRJ-276` is complete: canonical runtime-flow and
  agent-contract docs now define one explicit foreground ownership split
  (runtime baseline-load and post-action follow-up segments versus graph-owned
  stage spine), and migration invariants now pin stable stage outputs, stage
  ordering, and side-effect ownership while convergence continues.
- 2026-04-19: `PRJ-237` is complete: source-coverage posture for semantic
  retrieval is now operator-visible in `/health.memory_retrieval`, and startup
  warnings now use the same shared coverage-state semantics when vectors are
  enabled with partial/missing semantic-affective source coverage.
- 2026-04-19: `PRJ-237` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`
  passed with `154 passed`.
- 2026-04-19: `PRJ-236` is complete: embedding source-family scope is now
  configurable (`EMBEDDING_SOURCE_KINDS`), runtime embedding writes are gated
  by enabled families, and `/health.memory_retrieval` now exposes effective
  source-kind posture.
- 2026-04-19: `PRJ-236` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`
  passed with `151 passed`.
- 2026-04-19: `PRJ-235` is complete: embedding strategy warning-state semantics
  are now shared between startup logging and `/health.memory_retrieval`, and
  health exposes explicit warning-state/hint fields for operators.
- 2026-04-19: `PRJ-235` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `63 passed`.
- 2026-04-19: `PRJ-234` is complete: conclusion-driven semantic/affective
  embedding shells now use configured effective embedding model/dimensions and
  store requested-vs-effective provider metadata with explicit
  `pending_vector_materialization` status.
- 2026-04-19: `PRJ-234` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`
  passed with `51 passed`.
- 2026-04-19: `PRJ-233` is complete: embedding-provider fallback readiness is
  now operator-visible in `/health.memory_retrieval`, and startup logs now
  warn when configured embedding provider/model posture is not yet executable
  and falls back to deterministic vectors.
- 2026-04-19: `PRJ-233` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  passed with `158 passed`.
- 2026-04-19: `PRJ-232` is complete: embedding strategy config posture is now
  explicit (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`),
  runtime/action keep deterministic fallback semantics for non-implemented
  providers, and `/health.memory_retrieval` now surfaces requested vs
  effective embedding posture with fallback hint.
- 2026-04-19: `PRJ-232` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `142 passed`.
- 2026-04-19: `PRJ-231` is complete: semantic retrieval now has an explicit
  runtime feature gate (`SEMANTIC_VECTOR_ENABLED`) and operator-visible
  `/health.memory_retrieval` posture, while action/runtime preserve default
  hybrid behavior unless lexical-only mode is explicitly selected.
- 2026-04-19: `PRJ-231` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `136 passed`.
- 2026-04-19: `PRJ-221..PRJ-230` are complete: compat activity posture is now
  explicit in `/health.runtime_policy`, including stale-historical vs
  recent-attempt migration states and action hints.
- 2026-04-19: `PRJ-221..PRJ-230` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_config.py`
  passed with `92 passed`.
- 2026-04-19: `PRJ-211..PRJ-220` are complete: compat-route freshness telemetry
  is now policy-visible in `/health.runtime_policy` with config-bounded stale
  threshold and regression coverage across config, telemetry helper, and API.
- 2026-04-19: `PRJ-211..PRJ-220` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_config.py`
  passed with `87 passed`.
- 2026-04-19: `PRJ-201..PRJ-210` are complete: compat telemetry recent-window
  size is now config-driven with bounded validation and regression coverage
  across config, telemetry, and API health contract behavior.
- 2026-04-19: `PRJ-201..PRJ-210` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `94 passed`.
- 2026-04-19: `PRJ-191..PRJ-200` are complete: compat rolling trend slice now
  exposes recent-window counters and state mapping while preserving
  attempt-based migration recommendation posture.
- 2026-04-19: `PRJ-191..PRJ-200` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `89 passed`.
- 2026-04-19: `PRJ-181..PRJ-190` are complete: compat telemetry now includes
  rolling-window counters and `/health.runtime_policy` now exposes recent-trend
  attempts/rates/state for migration-window observability.
- 2026-04-19: `PRJ-181..PRJ-190` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `89 passed`.
- 2026-04-19: `PRJ-171..PRJ-180` are complete: compat-route sunset posture now
  includes explicit machine-readable readiness/reason signals, and recommendation
  logic now treats any observed compat attempts as migration-needed.
- 2026-04-19: `PRJ-171..PRJ-180` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `86 passed`.
- 2026-04-19: `PRJ-161..PRJ-170` are complete: compat sunset recommendation
  guidance is now explicit in `/health.runtime_policy` via allow/block rates
  and recommendation hints derived from compat telemetry.
- 2026-04-19: `PRJ-161..PRJ-170` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `85 passed`.
- 2026-04-19: `PRJ-151..PRJ-160` are complete: compat debug-route sunset
  readiness now includes explicit in-process telemetry counters, deprecation
  response header contract, and synchronized docs/context coverage.
- 2026-04-19: `PRJ-151..PRJ-160` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `82 passed`.
- 2026-04-19: `PRJ-141..PRJ-150` are complete: production debug query-compat
  hardening now has shared mismatch helper ownership, stricter startup/API
  regression coverage, and synchronized docs/context for
  `EVENT_DEBUG_QUERY_COMPAT_ENABLED` posture.
- 2026-04-19: `PRJ-141..PRJ-150` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`
  passed with `79 passed`.
- 2026-04-19: `PRJ-131..PRJ-140` are complete: strict rollout mismatch
  handling now includes `event_debug_token_missing=true` for production
  token-missing posture, and runtime-policy, startup-policy, API health tests,
  and docs/context are synchronized.
- 2026-04-19: `PRJ-131..PRJ-140` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`
  passed with `71 passed`.
- 2026-04-19: `PRJ-121..PRJ-130` are complete: runtime policy now emits
  explicit debug access posture/hint fields, startup policy logs warn when
  production debug runs with relaxed token requirement, and docs/context are
  synchronized for operator-visible debug hardening posture.
- 2026-04-19: `PRJ-121..PRJ-130` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`
  passed with `71 passed`.
- 2026-04-19: `PRJ-111..PRJ-120` are complete: production debug-token
  requirement is now explicit (`PRODUCTION_DEBUG_TOKEN_REQUIRED`), debug route
  access guard enforces production token posture when configured, runtime policy
  snapshots expose the new signal, and ops/config/context docs are synchronized.
- 2026-04-19: `PRJ-111..PRJ-120` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `68 passed`.
- 2026-04-19: `PRJ-101..PRJ-110` are complete: attention timing controls are
  now first-class settings, startup coordinator wiring is config-driven, config
  defaults/validation are regression-covered, and architecture/ops/context docs
  are synchronized for the attention hardening slice.
- 2026-04-19: `PRJ-101..PRJ-110` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_main_lifespan_policy.py tests/test_api_routes.py`
  passed with `48 passed`.
- 2026-04-19: `PRJ-100` is complete: `GET /health` now returns an explicit
  `attention` snapshot (`burst_window_ms`, `answered_ttl_seconds`,
  `stale_turn_seconds`, `pending|claimed|answered`) so burst-turn posture is
  visible in operations/debug workflows.
- 2026-04-19: `PRJ-100` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` passed with
  `29 passed`.
- 2026-04-19: `PRJ-099` is complete: `POST /event?debug=true` now adds explicit
  compatibility headers (`X-AION-Debug-Compat`, `Link`) pointing to
  `POST /event/debug` while preserving backward compatibility.
- 2026-04-19: `PRJ-099` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` passed with
  `28 passed`.
- 2026-04-19: `PRJ-098` is complete: API now exposes explicit
  `POST /event/debug` for internal full-runtime payload inspection while
  preserving `POST /event?debug=true` compatibility, both guarded by the same
  debug policy/token access checks.
- 2026-04-19: `PRJ-098` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` passed with
  `28 passed`; full suite also passes with `433 passed`.
- 2026-04-19: `PRJ-097` is complete: reflection now derives
  `suggest_connector_expansion` proposals from repeated unmet connector needs,
  planning promotes accepted proposals into bounded
  `connector_capability_discovery_intent` outputs, and action persists explicit
  `connector_expansion_update` traces without connector side effects.
- 2026-04-19: `PRJ-097` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_reflection_worker.py`
  passed with `158 passed`; full suite also passes with `429 passed`.
- 2026-04-19: `PRJ-096` is complete: planning and action contracts now include
  connected-drive access intents with explicit `read_only|suggestion_only|mutate_with_confirmation`
  modes, cloud-drive permission gates, and durable episode payload trace
  (`drive_connector_update`) without bypassing action boundaries.
- 2026-04-19: `PRJ-096` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`
  passed with `116 passed`.
- 2026-04-19: `PRJ-087..PRJ-095` are complete: internal planning ownership is
  now explicitly separated from external connector projections, subconscious
  proposals are persisted with conscious handoff resolution, read-only
  subconscious research policy is contract-owned, proactive flow applies an
  explicit attention gate, and connector contracts now expose permission gates
  plus typed calendar/task synchronization intents.
- 2026-04-19: validation for `PRJ-087..PRJ-095` is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`
  passed with `269 passed`.
- 2026-04-19: full regression remains green after dual-loop/connector contract
  coverage expansion:
  `.\.venv\Scripts\python -m pytest -q` passed with `425 passed`.
- 2026-04-19: `PRJ-086` is complete: Telegram burst events now flow through a
  shared attention-turn coordinator that coalesces rapid pending messages into
  one assembled turn and enforces `pending|claimed|answered` ownership before
  foreground runtime execution.
- 2026-04-19: `PRJ-086` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `85 passed`.
- 2026-04-19: `PRJ-085` is complete: runtime graph-state contracts now define
  explicit `attention_inbox`, `pending_turn`, `subconscious_proposals`, and
  `proposal_handoffs` surfaces, and architecture/implementation docs now align
  on one attention-inbox and proposal-handoff vocabulary.
- 2026-04-19: `PRJ-085` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`
  passed with `53 passed`.
- 2026-04-19: `PRJ-084` is complete: proactive delivery now enforces explicit
  user opt-in, outbound/unanswered throttle limits, and delivery-target checks
  before outreach; proactive scheduler deliveries now route via Telegram when a
  `chat_id` target is present.
- 2026-04-19: `PRJ-084` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `82 passed`; extended proactive regression command also passes
  with `177 passed`.
- 2026-04-19: `PRJ-083` is complete: scheduler proactive payloads now normalize
  trigger/importance/urgency plus user-context guardrails, a dedicated proactive
  decision engine now computes interruption-aware outreach decisions, and
  motivation/planning now consume typed proactive decisions for either defer or
  proactive message plans.
- 2026-04-19: `PRJ-083` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `124 passed`.
- 2026-04-19: `PRJ-082` is complete: an in-process scheduler worker now runs
  reflection and maintenance cadence independently from user-event turns,
  reflection dispatch is mode-aware (`in_process|deferred` guardrails), and
  `/health` now exposes scheduler runtime posture and latest tick summaries.
- 2026-04-19: `PRJ-082` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_scheduler_contracts.py tests/test_api_routes.py tests/test_config.py tests/test_reflection_worker.py tests/test_main_lifespan_policy.py`
  passed with `89 passed`; full suite also passes with `395 passed`.
- 2026-04-19: `PRJ-081` is complete: reflection enqueue no longer depends on an
  active in-process worker, runtime now supports deferred reflection mode, and
  reflection worker exposes one-shot queue drain execution for future
  out-of-process/scheduler usage.
- 2026-04-19: targeted `PRJ-081` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`
  passed with `124 passed`.
- 2026-04-19: `PRJ-072..PRJ-080` are complete: optional LangChain prompt
  wrappers landed, semantic retrieval contracts plus pgvector scaffold were
  added, hybrid retrieval diagnostics are now observable, relation storage and
  reflection updates are live, runtime stages became relation-aware, and
  scheduler/cadence contracts were formalized.
- 2026-04-19: validation for the `PRJ-072..PRJ-080` slice is green:
  `.\.venv\Scripts\python -m pytest -q` now passes with `382 passed`, and
  `.\.venv\Scripts\python -m alembic upgrade head --sql` includes both new
  revisions (`20260419_0004`, `20260419_0005`).
- 2026-04-19: `PRJ-071` is complete: foreground stage execution now runs
  through LangGraph with graph-compatible adapters and preserved runtime
  contract behavior; regressions remain green.
- 2026-04-19: `PRJ-069..PRJ-070` are complete: the repo now has an explicit
  graph-compatible state contract (`GraphRuntimeState`), runtime-result
  conversion helpers, and graph-ready adapters around current stage modules,
  with targeted contract tests and runtime regressions passing.
- 2026-04-19: planning and execution context now extend through `PRJ-097`,
  adding explicit follow-up groups for dual-loop coordination, attention
  gating, batched conversation handling, subconscious proposal handoff, and
  future external productivity connector boundaries.
- 2026-04-19: supplemental docs outside `docs/architecture/` now describe the
  planned attention inbox, turn assembly, subconscious proposal handoff, and
  internal-planning-vs-connector boundary so near-term direction is documented
  without rewriting canonical architecture files.
- 2026-04-19: `PRJ-061..PRJ-064` are complete: memory-layer contracts are
  formalized in docs/repository APIs, planning now owns explicit typed domain
  intents, action executes only explicit intents for durable writes, and
  contract tests now pin the planning-owned intent / action-owned execution
  boundary end to end.
- 2026-04-19: `PRJ-065..PRJ-068` are complete: reflection was split into
  concern-owned modules, adaptive updates now require stronger outcome
  evidence, low-leverage milestone pressure drift heuristics were pruned, and
  multi-goal reflection/planning behavior is now regression-covered.

- 2026-04-17: release smoke helper now covers health plus event verification,
  including optional UTF-8 payload and debug-response checks.
- 2026-04-17: next execution roadmap was regrouped into small task batches
  under `docs/planning/next-iteration-plan.md` and `.codex/context/TASK_BOARD.md`.
- 2026-04-17: emotional-turn contract tests now describe supportive behavior
  through documented runtime surfaces instead of the removed `support` mode.
- 2026-04-18: agent workflow context was refreshed to align with the current
  template-era standard, including learning-journal support and corrected
  canonical doc paths.
- 2026-04-18: runtime now emits structured stage-level logs for `memory_load`
  through `state_refresh`, and regression tests cover both success and failure
  logging paths.
- 2026-04-18: shared signal extraction group is complete (`PRJ-011..PRJ-013`);
  heuristic modules were reduced (`context: 801->751`, `planning: 755->676`,
  `motivation: 560->489`, `reflection: 1362->1318`) with behavior preserved by
  regression tests.
- 2026-04-18: the post-`PRJ-016` planning queue was expanded with future
  `Stage Boundary Alignment` and `Architecture Traceability And Contract Tests`
  groups so architecture-parity follow-up is visible without displacing the
  current execution order.
- 2026-04-18: `PRJ-015` and `PRJ-016` are complete: API boundary normalization
  is explicit and test-covered, and startup now defaults to migration-first with
  an explicit compatibility toggle.
- 2026-04-18: `PRJ-017` is complete: expression-to-action handoff now uses a
  dedicated `ActionDelivery` contract and regression tests pin the API/Telegram
  delivery path through that contract.
- 2026-04-18: `PRJ-019` is complete: overview and architecture docs now map
  runtime stages to code ownership and primary validation surfaces, with public
  vs debug runtime contract boundaries made explicit.
- 2026-04-18: `PRJ-018` is complete: action delivery dispatch moved to
  integration ownership through `DeliveryRouter`, preserving API/Telegram
  behavior while reducing action/integration coupling.
- 2026-04-18: `PRJ-020` is complete: runtime flow now has contract-level smoke
  tests across runtime pipeline, API response shape, and stage-level logging
  payload invariants.
- 2026-04-18: `PRJ-021` is complete: debug payload exposure for
  `POST /event?debug=true` is now explicitly gated by config and covered by API
  and config tests.
- 2026-04-19: `PRJ-022` is complete: `/health` now exposes non-secret runtime
  policy flags (`startup_schema_mode`, `event_debug_enabled`) for operator
  traceability, with API tests and docs synchronized.
- 2026-04-19: `PRJ-023` is complete: startup now warns when production runs with
  debug payload exposure enabled, with targeted tests and docs synchronized.
- 2026-04-19: `PRJ-024` is complete: startup now warns when production runs in
  schema compatibility mode (`STARTUP_SCHEMA_MODE=create_tables`), with
  targeted tests and docs synchronized.
- 2026-04-19: `PRJ-025` is complete: debug payload policy now has production-safe
  default behavior with explicit source visibility in `/health`, and tests/docs
  are synchronized.
- 2026-04-19: `PRJ-026` is complete: production runtime-policy enforcement now
  supports `warn|strict`, startup can fail fast on policy mismatches when
  strict mode is active, and `/health` exposes the enforcement posture.
- 2026-04-19: `PRJ-027` is complete: startup strict-policy behavior now has a
  lifespan-level fail-fast regression test that confirms policy mismatch blocks
  runtime before database initialization.
- 2026-04-19: `PRJ-028` is complete: strict startup-policy lifecycle tests now
  cover both debug and schema mismatch paths, confirming fail-fast behavior
  before database initialization side effects.
- 2026-04-19: `PRJ-029` is complete: runtime policy logic now has a shared core
  helper used by startup and `/health`, and `/health` now exposes
  `production_policy_mismatches` with regression coverage for startup/API
  consumers.
- 2026-04-19: `PRJ-030..PRJ-039` are complete: runtime policy now includes
  strict rollout readiness helpers and `/health` contract fields
  (`production_policy_mismatch_count`, `strict_startup_blocked`,
  `strict_rollout_ready`), startup and health now share the same strict-block
  semantics, and regression coverage/docs/context were synchronized.
- 2026-04-19: `PRJ-040..PRJ-045` are complete: runtime policy now includes
  strict rollout recommendation helpers and `/health` contract fields
  (`recommended_production_policy_enforcement`, `strict_rollout_hint`),
  startup now logs strict-ready rollout hints in production warn mode, and
  regression coverage/docs/context were synchronized.
- 2026-04-19: `PRJ-046..PRJ-051` are complete: debug payload access now
  supports optional token gating (`EVENT_DEBUG_TOKEN` and
  `X-AION-Debug-Token`), health policy now exposes token-required state,
  startup warns when production debug exposure is enabled without token, and
  regression coverage/docs/context were synchronized.
- 2026-04-19: `PRJ-052` is complete: `POST /event` now accepts
  `X-AION-User-Id` as fallback identity when `meta.user_id` is omitted,
  normalization/API tests now pin user-id precedence, and docs/context were
  synchronized for multi-user API safety.
- 2026-04-19: `PRJ-053` is complete: runtime contracts now include explicit
  affective assessment fields, perception emits deterministic affective
  placeholders, runtime exposes top-level affective state, and
  architecture/planning/context docs plus regression tests were synchronized.
- 2026-04-19: `PRJ-054` is complete: runtime now runs a dedicated affective
  assessor stage that can normalize LLM classification and safely fall back
  when unavailable or invalid, with regression tests and docs/context aligned.
- 2026-04-19: `PRJ-055` is complete: motivation, role, and expression now use
  the shared affective contract (`perception.affective`) as their support
  signal owner, replacing local emotional keyword ladders and adding
  affective-driven regression coverage.
- 2026-04-19: `PRJ-056` is complete: empathy-oriented shared fixtures now cover
  emotionally heavy, ambiguous, and mixed-intent turns, and support-quality
  regression coverage was expanded across motivation, expression, and runtime.
- 2026-04-19: `PRJ-057` is complete: scoped conclusions were introduced for
  global/goal/task context in schema, repository APIs, and reflection writes,
  with scope-aware tests and migration validation synchronized.
- 2026-04-19: `PRJ-058` is complete: runtime now consumes goal-scoped
  reflection state with global fallback, and regression tests pin no-leakage
  behavior across context, motivation, planning, and runtime.
- 2026-04-19: `PRJ-059` is complete: episodic memory now carries affective
  tags, reflection derives slower-moving affective conclusions, and runtime
  consumers reuse those signals across turns.
- 2026-04-19: `PRJ-060` is complete: runtime memory loading and context
  retrieval now go beyond latest-five depth with affective-aware ranking and
  compression.
- 2026-04-19: architecture docs were realigned so `docs/architecture/` again
  describes the canonical cognitive flow, while runtime-delivery shortcuts,
  live storage names, and policy details were moved into
  `docs/implementation/runtime-reality.md` and linked from the docs index.
- 2026-04-19: planning docs and execution context were extended through
  `PRJ-084`, adding grouped follow-up slices for affective understanding,
  scoped memory, explicit action intents, adaptive-signal governance, graph
  orchestration adoption, semantic retrieval infrastructure, relation system,
  and scheduled/proactive runtime.
- 2026-04-20: planning, board, and open-decisions context now extend through
  `PRJ-299`, shifting the next queue from generic architecture hardening toward
  target-state convergence across foreground runtime boundaries, background
  reflection topology, production retrieval rollout, adaptive governance,
  dual-loop execution boundaries, and operational hardening.
- 2026-04-20: foreground convergence group is now complete through `PRJ-279`;
  background topology convergence is complete through `PRJ-283`; production
  retrieval implementation is complete through `PRJ-287`; adaptive governance
  policy baseline is complete through `PRJ-288`; runtime behavior-validation
  lane is now complete through `PRJ-317`.
- 2026-04-20: `PRJ-288` is complete: architecture contracts now define explicit
  adaptive influence evidence gates, precedence, and tie-break guardrails for
  affective, relation, preference, and theta signals.
- 2026-04-20: `PRJ-288` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `151 passed`.
- 2026-04-20: `PRJ-289` is complete: role, motivation, and planning now consume
  shared governed adaptive-policy helpers (`app/core/adaptive_policy.py`) for
  relation evidence thresholds, preferred-role gating, theta dominance, and
  adaptive tie-break posture checks.
- 2026-04-20: `PRJ-289` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_adaptive_policy.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `156 passed`.
- 2026-04-20: `PRJ-290` is complete: proactive decision and attention gating
  now consume governed relation/theta policy surfaces from
  `app/core/adaptive_policy.py`, and adaptive cues can tighten proactive
  posture without bypassing attention or anti-spam guardrails.
- 2026-04-20: `PRJ-290` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_adaptive_policy.py`
  passed with `176 passed`.
- 2026-04-20: `PRJ-291` is complete: adaptive-governance regressions now pin
  anti-feedback-loop behavior in reflection, goal-scoped relation retrieval in
  runtime proactive attention gating, and sub-threshold adaptive influence
  boundaries across role/motivation/planning consumers.
- 2026-04-20: `PRJ-291` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `206 passed`.
- 2026-04-20: `PRJ-292` is complete: canonical dual-loop ownership is now
  explicit for attention turn assembly (`attention_inbox`, `pending_turn`),
  conscious proposal handoff decisions (`proposal_handoffs`), and action-side
  execution boundaries after planning decisions.
- 2026-04-20: `PRJ-292` validation is recorded as doc-and-context sync plus
  targeted dual-loop contract review across
  `docs/architecture/15_runtime_flow.md`,
  `docs/architecture/16_agent_contracts.md`,
  `docs/planning/open-decisions.md`,
  `docs/implementation/runtime-reality.md`,
  `.codex/context/TASK_BOARD.md`, and
  `docs/planning/next-iteration-plan.md`.
- 2026-04-20: `PRJ-293` is complete: subconscious proposal persistence now
  supports conscious re-entry from retriable lifecycle states
  (`pending|deferred`), planning skips non-retriable proposal states, and
  conscious handoff decisions continue to gate resolution before proposal-driven
  side-effect shaping.
- 2026-04-20: `PRJ-293` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_planning_agent.py`
  passed with `193 passed`.
- 2026-04-20: `PRJ-294` is complete: proactive outreach and connector
  permission-gate outcomes now share one conscious execution boundary, keeping
  connector discovery and proactive delivery aligned with the same plan/action
  gating model.
- 2026-04-20: `PRJ-294` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_planning_agent.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `181 passed`.
- 2026-04-20: `PRJ-295` is complete: dual-loop execution-boundary regressions
  now pin proactive-path separation from proposal handoff and connector
  permission-gate intent shaping, while attention turn assembly and conscious
  proposal resolution remain covered end to end.
- 2026-04-20: `PRJ-295` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py tests/test_action_executor.py tests/test_planning_agent.py`
  passed with `229 passed`.
- 2026-04-20: `PRJ-296` is complete: target production baseline now explicitly
  defines migration-only startup posture, strict production policy target, and
  internal debug boundary expectations (public compact event path, debug route
  hardening, production compat-route disable baseline).
- 2026-04-20: `PRJ-296` validation is recorded as doc-and-context sync plus
  targeted production-baseline review across
  `docs/planning/open-decisions.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `.codex/context/TASK_BOARD.md`, and
  `docs/planning/next-iteration-plan.md`.
- 2026-04-20: `PRJ-297` is complete: runtime policy now resolves production
  enforcement to `strict` by default when unset, while explicit
  `PRODUCTION_POLICY_ENFORCEMENT=warn` remains a controlled override; startup
  and `/health` policy surfaces now reflect that production-aware default.
- 2026-04-20: `PRJ-297` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`
  passed with `142 passed`.
- 2026-04-20: `PRJ-298` is complete: deployment trigger ownership now has one
  explicit operations baseline (Coolify automation first, explicit webhook/UI
  fallback), and release smoke ownership is codified as a release gate.
- 2026-04-20: `PRJ-298` validation is green:
  `.\.venv\Scripts\python -m pytest -q`
  passed with `598 passed`.
- 2026-04-20: `PRJ-299` is complete: `/health` now exposes a compact
  `release_readiness` gate snapshot (`ready`, `violations`) derived from
  runtime-policy release guardrails, and release smoke scripts fail fast on
  production-policy drift.
- 2026-04-20: `PRJ-299` validation is green:
  `.\.venv\Scripts\python -m pytest -q`
  passed with `602 passed`.
- 2026-04-20: `PRJ-300` is complete: first post-convergence planning queue is
  now seeded through `PRJ-304`, keeping execution continuity after
  operational-hardening closure (`PRJ-299`).
- 2026-04-20: `PRJ-300` validation is recorded as doc-and-context sync plus
  targeted planning coherence review across
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`,
  `.codex/context/PROJECT_STATE.md`, and
  `docs/planning/open-decisions.md`.
- 2026-04-20: `PRJ-301` is complete: production reflection deployment baseline
  now stays `REFLECTION_RUNTIME_MODE=in_process` by default, while deferred
  dispatch is explicitly gated behind external-readiness criteria.
- 2026-04-20: `PRJ-301` validation is recorded as doc-and-context sync plus
  targeted reflection-topology contract review across
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/implementation/runtime-reality.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-302` is complete: `/health.reflection` now exposes
  deployment-readiness posture (`ready`, `blocking_signals`,
  baseline/selected runtime mode) derived from runtime mode, topology, worker
  state, and reflection task health signals.
- 2026-04-20: `PRJ-302` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_reflection_worker.py`
  passed with `119 passed`.
- 2026-04-20: `PRJ-303` is complete: reflection deployment-readiness
  regressions now pin blocker semantics in shared scheduler contracts and
  `/health`, while release smoke scripts now fail fast on reflection readiness
  blockers with explicit fallback checks for older runtimes.
- 2026-04-20: `PRJ-303` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_scheduler_contracts.py`
  passed with `120 passed`.
- 2026-04-20: `PRJ-304` is complete: reflection deployment baseline/readiness
  docs are now synchronized across planning, runtime-reality, and operations
  runbook surfaces, including consistent release/rollback readiness gating.
- 2026-04-20: `PRJ-304` validation is recorded as doc-and-context sync plus
  targeted ops-runbook review across
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-305` is complete: post-reflection hardening queue is now
  seeded through `PRJ-309`, keeping execution continuity after reflection lane
  closure (`PRJ-304`).
- 2026-04-20: `PRJ-305` validation is recorded as doc-and-context sync plus
  targeted planning coherence review across
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`,
  `.codex/context/PROJECT_STATE.md`, and
  `docs/planning/open-decisions.md`.
- 2026-04-20: `PRJ-306` is complete: migration strategy now has explicit
  criteria and rollout guardrails for removing `create_tables` compatibility
  startup path without reopening production baseline decisions.
- 2026-04-20: `PRJ-306` validation is recorded as doc-and-context sync plus
  targeted migration-strategy review across
  `docs/planning/open-decisions.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-307` is complete: public API follow-up decision now defines
  explicit target internal debug ingress boundary and migration ownership away
  from shared public API service endpoint posture.
- 2026-04-20: `PRJ-307` validation is recorded as doc-and-context sync plus
  targeted public-api boundary review across
  `docs/planning/open-decisions.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-308` is complete: scheduler/proactive follow-up now defines
  explicit long-term external cadence ownership posture while keeping app-local
  scheduler cadence as transitional/fallback rollout surface.
- 2026-04-20: `PRJ-308` validation is recorded as doc-and-context sync plus
  targeted scheduler-boundary review across
  `docs/planning/open-decisions.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-309` is complete: post-reflection hardening queue decisions
  are now synchronized across planning, project state, and operations runbook
  before entering runtime behavior-validation execution lane.
- 2026-04-20: `PRJ-309` validation is recorded as doc-and-context sync plus
  targeted cross-doc consistency review across
  `docs/planning/open-decisions.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: canonical architecture now includes
  `docs/architecture/29_runtime_behavior_testing.md`, which defines required
  system-debug visibility, user-simulation mode, and behavior-driven validation
  expectations for memory, continuity, decision integrity, and failure
  handling.
- 2026-04-20: execution planning now extends through `PRJ-317`, adding a
  runtime-behavior validation lane for internal debug surfaces, memory
  influence checks, continuity scenarios, and failure-mode behavior gating.
- 2026-04-20: `PRJ-310..PRJ-313` are complete: runtime now exposes a canonical
  `system_debug` validation surface and behavior-harness helpers with
  structured scenario output (`test_id`, `status`, `reason`, `trace_id`,
  `notes`), and docs/context are synchronized to that contract.
- 2026-04-20: `PRJ-314..PRJ-316` are complete: scenario coverage now validates
  memory `write -> retrieve -> influence -> delayed recall`, multi-session
  continuity/personality stability, and contradiction/missing-data/noisy-input
  resilience.
- 2026-04-20: `PRJ-317` is complete: release-readiness now includes explicit
  behavior-validation evidence via `scripts/run_behavior_validation.{ps1,sh}`
  in addition to full regression checks.
- 2026-04-20: runtime behavior-validation checks are green:
  - `.\scripts\run_behavior_validation.ps1` passed with `6 passed`.
  - `.\.venv\Scripts\python -m pytest -q` passed with `612 passed`.
- 2026-04-20: execution planning now extends through `PRJ-337`, adding
  implementation lanes for internal debug ingress migration, scheduler
  externalization and attention ownership, identity/language boundary
  hardening, relation lifecycle rollout, and inferred goal/task growth through
  typed intents.
- 2026-04-20: `PRJ-318` is complete: runtime now exposes
  `POST /internal/event/debug` as the primary debug ingress, keeps
  `POST /event/debug` as compatibility ingress with explicit shared-route
  migration headers, and extends runtime policy snapshot with
  debug-ingress ownership/path posture fields.
- 2026-04-20: `PRJ-318` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`
  passed with `108 passed`.
- 2026-04-20: `PRJ-319` is complete: shared debug ingress now supports
  explicit `compatibility|break_glass_only` modes, break-glass override is
  enforced for shared endpoint access in `break_glass_only` mode, and runtime
  policy now surfaces shared-ingress break-glass posture fields.
- 2026-04-20: `PRJ-319` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `153 passed`.
- 2026-04-20: `PRJ-320` is complete: regression coverage now pins
  break-glass shared-ingress posture and health visibility for internal/shared
  debug ingress migration semantics.
- 2026-04-20: `PRJ-320` also extends release smoke scripts
  (`scripts/run_release_smoke.ps1`, `scripts/run_release_smoke.sh`) with
  explicit internal/shared debug-ingress contract checks
  (path ownership, shared mode, break-glass requirement, posture consistency).
- 2026-04-20: `PRJ-320` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`
  passed with `113 passed`.
- 2026-04-20: `PRJ-321` is complete: canonical docs, planning notes, and
  operations runbook now align with internal debug ingress migration reality
  (`POST /internal/event/debug` primary, shared `POST /event/debug`
  compatibility posture, break-glass controls, and updated compat headers).
- 2026-04-20: `PRJ-321` validation is recorded as doc-and-context sync plus
  targeted debug-ingress cross-doc review across
  `docs/overview.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-322` is complete: scheduler cadence ownership now has one
  explicit execution-mode contract (`in_process|externalized`) with shared
  scheduler-readiness posture, worker snapshot ownership fields, and
  `/health.scheduler` owner visibility for maintenance/proactive cadence.
- 2026-04-20: `PRJ-322` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_config.py`
  passed with `129 passed`.
- 2026-04-20: `PRJ-323` is complete: maintenance/proactive cadence now use
  shared owner-aware dispatch decisions, and scheduler maintenance execution
  explicitly respects `in_process|externalized` ownership mode with
  machine-visible dispatch reasons.
- 2026-04-20: `PRJ-323` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_api_routes.py`
  passed with `157 passed`.
- 2026-04-20: `PRJ-324` is complete: attention coordination now exposes
  explicit owner posture (`in_process|durable_inbox`) with deployment-readiness
  diagnostics and durable-owner blocker semantics in `/health.attention`.
- 2026-04-20: `PRJ-324` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_scheduler_contracts.py tests/test_config.py`
  passed with `188 passed`.
- 2026-04-20: `PRJ-325` is complete: docs/context/runbook are synchronized with
  owner-aware scheduler cadence posture and attention owner/readiness posture
  (`SCHEDULER_EXECUTION_MODE`, `ATTENTION_COORDINATION_MODE`, and health
  ownership/readiness fields).
- 2026-04-20: `PRJ-325` validation is recorded as doc-and-context sync plus
  targeted scheduler/attention cross-doc review across
  `docs/overview.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-326` is complete: runtime identity loading now enforces an
  explicit owner boundary where `aion_profile` remains the durable owner for
  profile language, while identity response/collaboration preferences are
  sourced from conclusion-owned runtime preference inputs only.
- 2026-04-20: `PRJ-326` also keeps relation-derived collaboration fallback for
  planning/expression tie-break behavior without leaking that fallback into
  identity continuity fields.
- 2026-04-20: `PRJ-326` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `136 passed`.
- 2026-04-20: `PRJ-327` is complete: language detection now follows explicit
  precedence across current-turn lexical signals, recent memory continuity, and
  durable profile preference.
- 2026-04-20: `PRJ-327` also expands continuity parsing to use
  `payload.response_language` hints from episodic memory and ignores
  unsupported language codes before falling back to profile/default posture.
- 2026-04-20: `PRJ-327` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_context_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`
  passed with `140 passed`.
- 2026-04-20: `PRJ-328` is complete: identity/language continuity regressions
  now pin ambiguous-turn language continuity across runtime session restarts
  and profile-backed fallback behavior.
- 2026-04-20: `PRJ-328` also adds API fallback regression coverage to ensure
  `X-AION-User-Id` remains per-request identity fallback and does not leak into
  later requests without explicit identity input.
- 2026-04-20: `PRJ-328` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `141 passed`.
- 2026-04-21: `PRJ-329` is complete: canonical docs, runtime-reality notes,
  planning notes, and project context now share one identity/language/profile
  continuity baseline.
- 2026-04-21: `PRJ-329` sync explicitly records profile-versus-conclusion
  identity ownership (`aion_profile` language owner, conclusion-owned response
  and collaboration preferences), language continuity precedence, and
  request-scoped API identity fallback (`meta.user_id` ->
  `X-AION-User-Id` -> `anonymous`).
- 2026-04-21: `PRJ-329` validation is recorded as doc-and-context sync plus
  targeted identity-boundary cross-doc review across
  `docs/overview.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-330` is complete: relation retrieval now applies
  age-aware confidence revalidation with evidence-sensitive decay and explicit
  expiration posture for stale relation signals.
- 2026-04-21: `PRJ-330` also refreshes relation durability by blending
  repeated same-value relation evidence in upsert paths and allows reflection
  to persist relation-only revalidation updates (`delivery_reliability=low_trust`)
  without requiring a conclusion/theta write in the same turn.
- 2026-04-21: `PRJ-330` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
  passed with `155 passed`.
- 2026-04-21: `PRJ-331` is complete: trust governance now shapes proactive
  interruption behavior through shared relation/theta-aware cost adjustments,
  trust-calibrated proactive relevance, and low-trust/high-trust outreach
  output posture (including tone-oriented plan steps).
- 2026-04-21: `PRJ-331` also extends foreground trust influence so motivation
  uses delivery-reliability tie-breaks on ambiguous turns while planning adds
  explicit confidence posture steps (`plan_with_confident_next_step`,
  `plan_with_cautious_validation`) and trust-aware proactive outreach tone
  steps (`use_confident_outreach_tone`, `use_low_pressure_outreach_tone`).
- 2026-04-21: `PRJ-331` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_adaptive_policy.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `172 passed`.
- 2026-04-21: `PRJ-331` required board validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `247 passed`.
- 2026-04-21: `PRJ-338` is complete: Telegram delivery now hardens exception
  boundaries (`4xx/5xx`, timeout, transport failure) in
  `DeliveryRouter`, degrading failures to structured
  `ActionResult(status=fail)` responses instead of uncaught action-stage
  exceptions that surface as endpoint 500s.
- 2026-04-21: `PRJ-338` also adds fail-path regression coverage across delivery
  router, action executor, runtime pipeline, and debug ingress API boundaries,
  including explicit `/internal/event/debug` fail-action response posture.
- 2026-04-21: `PRJ-338` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `160 passed`.
- 2026-04-21: `PRJ-338` app-lifespan manual smoke attempt through
  `POST /internal/event/debug` was blocked in this workspace by unresolved DB
  host startup dependency (`socket.gaierror [Errno 11001] getaddrinfo failed`);
  the recurring execution guardrail is captured in
  `.codex/context/LEARNING_JOURNAL.md`.
- 2026-04-21: `PRJ-332` is complete: relation lifecycle and trust-influence
  regressions now pin value-shift lifecycle reset posture in repository
  relation upserts, medium-trust derivation in reflection, low-confidence
  trust gating for proactive attention, and low-confidence support-intensity
  relation gating for expression tone selection.
- 2026-04-21: `PRJ-332` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_expression_agent.py`
  passed with `175 passed`.
- 2026-04-21: `PRJ-333` is complete: docs/planning/context now share one
  relation lifecycle and trust-influence baseline, including relation refresh
  vs value-shift reset posture, age-aware revalidation/expiration, and
  low-confidence trust-signal guardrails.
- 2026-04-21: `PRJ-333` validation is recorded as doc-and-context sync plus
  targeted relation-lifecycle cross-doc review across
  `docs/overview.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-334` is complete: planning now promotes bounded inferred
  goal/task intents from repeated blocker evidence when explicit declaration
  patterns are absent, while preserving confidence/evidence gates and
  duplicate guards against active planning state.
- 2026-04-21: `PRJ-334` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`
  passed with `167 passed`.
- 2026-04-21: `PRJ-335` is complete: inferred planning writes now use explicit
  typed intents (`promote_inferred_goal`, `promote_inferred_task`,
  `maintain_task_status`) and action executes those intents as the only owner
  of durable inferred promotion and maintenance writes.
- 2026-04-21: `PRJ-335` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  passed with `150 passed`.
- 2026-04-21: `PRJ-336` is complete: inference safety and duplicate-avoidance
  regressions now pin non-repeated/weak-signal no-promotion posture and
  no-duplicate behavior when matching active inferred planning state already
  exists.
- 2026-04-21: `PRJ-336` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py`
  passed with `202 passed`.
- 2026-04-21: `PRJ-337` is complete: architecture/planning/runtime-reality
  docs plus context truth now share one baseline for bounded inferred
  goal/task promotion, typed inferred and maintenance intents, and action-owned
  durable execution boundaries.
- 2026-04-21: `PRJ-337` validation is recorded as doc-and-context sync plus
  targeted planning-autonomy cross-doc review across
  `docs/architecture/16_agent_contracts.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-339` is complete: affective classifier integration now uses
  structured parse/schema gates plus explicit fallback diagnostics, and runtime
  affective stage logs include fallback reason traces to avoid silent drift.
- 2026-04-21: `PRJ-339` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_openai_client.py tests/test_affective_contract.py tests/test_expression_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `165 passed`.
- 2026-04-21: `PRJ-340` is complete: planning goal/task detection now supports
  deterministic natural inline command phrasing in English and Polish
  (for example `add goal ...`, `add task ...`, `dodaj cel ...`,
  `dodaj zadanie ...`) in addition to strict prefix-only forms.
- 2026-04-21: `PRJ-340` also keeps false-positive guardrails for non-command
  mentions and preserves typed domain-intent extraction boundaries
  (`upsert_goal|upsert_task`) through shared signal utilities.
- 2026-04-21: `PRJ-340` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_goal_task_signals.py`
  passed with `204 passed`.
- 2026-04-21: `PRJ-341` is complete: operator-facing Telegram smoke workflow
  now includes explicit webhook/listen mode switching probes
  (`getWebhookInfo -> deleteWebhook -> getUpdates -> setWebhook`) across
  PowerShell and bash scripts.
- 2026-04-21: `PRJ-341` also adds runbook-level precondition checks for
  reliable delivery triage (`/start` handshake, known `chat_id`, bot token,
  webhook secret parity) to reduce false-negative Telegram diagnostics.
- 2026-04-21: `PRJ-341` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_event_normalization.py tests/test_delivery_router.py`
  passed with `83 passed`.
- 2026-04-21: `PRJ-341` live Telegram smoke execution is not recorded in this
  workspace because runtime bot credentials are unavailable here; evidence
  coverage is provided through shipped operator scripts and runbook checklist.
- 2026-04-21: `PRJ-342` is complete: planning docs, operations runbook, and
  context truth now align for manual runtime reliability fixes through
  `PRJ-342`.
- 2026-04-21: `PRJ-342` also seeds the next derived architecture queue
  (`PRJ-343..PRJ-346`) for relation-aware inferred promotion governance
  follow-up.
- 2026-04-21: `PRJ-342` validation is recorded as doc-and-context sync plus
  targeted cross-reference checks across
  `docs/planning/next-iteration-plan.md`,
  `docs/planning/open-decisions.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-343` is complete: inferred goal/task promotion gating now
  uses delivery-reliability posture (`low_trust|medium_trust|high_trust`)
  through deterministic thresholds while keeping explicit declaration intents
  unaffected.
- 2026-04-21: `PRJ-343` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_adaptive_policy.py`
  passed with `145 passed`.
- 2026-04-21: `PRJ-344` is complete: inferred-promotion gate diagnostics are
  now explicit in planning output (`reason=...`, `result=...`) and available in
  runtime `system_debug.plan.inferred_promotion_diagnostics`.
- 2026-04-21: `PRJ-344` also extends API debug contract coverage so
  `/internal/event/debug` plan payload remains stable while exposing inferred
  promotion diagnostics for operator triage.
- 2026-04-21: `PRJ-344` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `200 passed`.
- 2026-04-21: `PRJ-345` is complete: regression coverage now pins trust-aware
  inferred promotion gates and diagnostics across planning/runtime paths
  (including low-trust repeated-signal guardrails and high-trust/medium-trust
  promotion behavior).
- 2026-04-21: `PRJ-345` also extends debug-surface coverage so inferred gate
  diagnostics remain visible and contract-stable in runtime and API debug
  responses.
- 2026-04-21: `PRJ-345` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py`
  passed with `251 passed`.
- 2026-04-21: `PRJ-346` is complete: architecture/runtime/planning/context
  docs now align on trust-aware inferred promotion thresholds and
  machine-visible inferred gate diagnostics posture.
- 2026-04-21: `PRJ-346` also seeds the next derived queue
  (`PRJ-347..PRJ-350`) for behavior-validation CI-ingestion follow-up.
- 2026-04-21: `PRJ-346` validation is recorded as doc-and-context sync plus
  targeted cross-reference checks across
  `docs/architecture/16_agent_contracts.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/next-iteration-plan.md`,
  `docs/planning/open-decisions.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-347` is complete: behavior validation now has a shared
  Python entrypoint (`scripts/run_behavior_validation.py`) that emits a
  machine-readable JSON artifact with summary counts, per-test status, and
  pytest exit-code posture for CI ingestion.
- 2026-04-21: `PRJ-347` also updates both shell wrappers
  (`run_behavior_validation.ps1`, `run_behavior_validation.sh`) to consume the
  shared artifact-producing path without breaking local/operator behavior.
- 2026-04-21: `PRJ-347` validation is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj347-report.json`
  passed with `6 passed`.
- 2026-04-21: `PRJ-347` scope regression is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `140 passed`.
- 2026-04-21: `PRJ-348` is complete: behavior-validation release scripts now
  expose explicit gate posture controls (`operator|ci`) and CI mode can fail
  fast using artifact-level gate semantics.
- 2026-04-21: `PRJ-348` also extends artifact output with machine-readable gate
  metadata (`gate.mode`, `gate.status`, `gate.violations`) so CI consumers and
  operators share one contract.
- 2026-04-21: `PRJ-348` validation is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj348-operator.json --gate-mode operator`
  passed with `6 passed`.
- 2026-04-21: `PRJ-348` CI posture validation is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj348-ci.json --gate-mode ci`
  passed with `6 passed`.
- 2026-04-21: `PRJ-348` required regression scope is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `101 passed`.
- 2026-04-21: `PRJ-349` is complete: script-level regressions now pin
  behavior-validation artifact gate semantics for `operator` and `ci` modes,
  including explicit CI fail-fast posture when no tests are collected.
- 2026-04-21: `PRJ-349` regression contract now verifies artifact gate fields
  (`gate.mode`, `gate.status`, `gate.violations`, `gate.ci_require_tests`) and
  preserves operator-mode exit behavior.
- 2026-04-21: `PRJ-349` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py`
  passed with `5 passed`.
- 2026-04-21: `PRJ-349` required regression scope is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `176 passed`.
- 2026-04-21: `PRJ-350` is complete: planning, operations runbook, testing
  guidance, and context truth now align on behavior-validation artifact
  contract and `operator|ci` gate posture.
- 2026-04-21: `PRJ-350` also seeds the next derived queue
  (`PRJ-351..PRJ-354`) for behavior-validation artifact-governance follow-up.
- 2026-04-21: `PRJ-350` validation is recorded as doc-and-context sync plus
  targeted cross-reference checks across
  `docs/planning/next-iteration-plan.md`,
  `docs/planning/open-decisions.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/engineering/testing.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-351` is complete: behavior-validation artifact output now
  includes explicit schema-version metadata and normalized gate-reason
  taxonomy/version fields for deterministic CI parsing.
- 2026-04-21: `PRJ-351` also adds explicit gate `violation_context` payload so
  reason codes can be interpreted without parsing free-text fragments.
- 2026-04-21: `PRJ-351` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_runtime_pipeline.py`
  passed with `80 passed`.
- 2026-04-21: `PRJ-351` artifact smoke is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj351-report.json --gate-mode ci`
  passed with `6 passed`.
- 2026-04-21: `PRJ-352` is complete: behavior-validation script now supports
  local artifact-input gate evaluation mode for CI consumers without rerunning
  pytest.
- 2026-04-21: `PRJ-352` also hardens artifact-input parsing with UTF-8 BOM
  tolerance so PowerShell-authored artifact payloads remain readable by gate
  evaluation flows.
- 2026-04-21: `PRJ-352` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `108 passed`.
- 2026-04-21: `PRJ-352` artifact-input smoke is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-input-path artifacts/behavior_validation/prj352-input.json --artifact-path artifacts/behavior_validation/prj352-output.json --gate-mode ci`
  produced `gate_status=pass`.
- 2026-04-21: `PRJ-353` is complete: regression coverage now pins
  schema-version metadata, normalized gate reason codes, and artifact-input
  failure posture (`missing`, `summary_missing`, `summary_invalid`).
- 2026-04-21: `PRJ-353` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `186 passed`.
- 2026-04-21: `PRJ-354` is complete: planning, operations runbook, testing
  guidance, and context truth now align on behavior-validation artifact
  governance posture (schema versioning, taxonomy, and artifact-input
  evaluation mode).
- 2026-04-21: `PRJ-354` also seeds the next derived queue
  (`PRJ-355..PRJ-358`) for deployment-trigger SLO instrumentation follow-up.
- 2026-04-21: `PRJ-354` validation is recorded as doc-and-context sync plus
  targeted cross-reference checks across
  `docs/planning/next-iteration-plan.md`,
  `docs/planning/open-decisions.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/engineering/testing.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-355` is complete: Coolify deploy trigger now has a shared
  evidence-capable Python owner with optional machine-readable output for
  webhook invocation metadata and response posture.
- 2026-04-21: `PRJ-355` also aligns PowerShell/bash trigger wrappers onto the
  shared Python entrypoint so deployment evidence semantics remain consistent
  across operator environments.
- 2026-04-21: `PRJ-355` validation is green:
  `.\.venv\Scripts\python .\scripts\trigger_coolify_deploy_webhook.py --help`
  verified argument contract, and
  `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `101 passed`.
- 2026-04-21: `PRJ-356` is complete: release-smoke scripts now support optional
  deployment-trigger evidence verification with freshness and successful
  webhook response checks in both PowerShell and bash paths.
- 2026-04-21: `PRJ-356` preserves backward-compatible smoke behavior when
  deployment evidence is not provided.
- 2026-04-21: `PRJ-356` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `101 passed`.
- 2026-04-21: `PRJ-357` is complete: deployment-trigger SLO instrumentation is
  now regression-covered through a dedicated script suite that pins Coolify
  evidence shape for success/failure paths plus release-smoke optional
  evidence omission, freshness checks, and unsuccessful-webhook failure
  posture.
- 2026-04-21: `PRJ-357` also hardens PowerShell release-smoke compatibility by
  routing deployment-evidence JSON parsing through a version-tolerant
  `ConvertFrom-Json` helper instead of assuming `-Depth` support.
- 2026-04-21: `PRJ-357` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py`
  passed with `6 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `101 passed`.
- 2026-04-21: `PRJ-358` is complete: planning, testing, operations runbook,
  and context truth now align on deployment-trigger evidence capture,
  optional release-smoke evidence verification, and the new regression
  coverage for Group 34.
- 2026-04-21: `PRJ-358` also closes the currently seeded deployment-trigger
  SLO instrumentation lane (`PRJ-355..PRJ-358`); the next execution slice
  should now be derived from planning docs and open decisions because no task
  remains in `READY`.
- 2026-04-21: `PRJ-359` is complete: behavior-validation artifact gate
  evaluation now treats incompatible `artifact_schema_version` major values as
  CI-blocking posture while preserving operator-mode compatibility for local
  inspection of older artifacts.
- 2026-04-21: `PRJ-359` also makes schema-major compatibility machine-visible
  through gate violation context (`artifact_input_schema_version`,
  `artifact_input_schema_major`, `expected_artifact_schema_version`,
  `expected_artifact_schema_major`).
- 2026-04-21: `PRJ-359` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py`
  passed with `12 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `176 passed`.
- 2026-04-21: `PRJ-360` is complete: planning docs, testing guidance, and
  context truth now align on schema-major compatibility governance for
  behavior-validation artifacts.
- 2026-04-21: `PRJ-360` also closes the current compatibility-governance
  follow-up lane; no task remains in `READY`, so the next slice should again
  be derived from planning docs and open decisions.
- 2026-04-21: `PRJ-361` is complete: `/health.attention` now exposes explicit
  production timing baseline posture for burst coalescing (`120ms`), answered
  turn retention (`5s`), and stale-turn cleanup (`30s`) together with
  alignment diagnostics for customized overrides.
- 2026-04-21: `PRJ-361` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py`
  passed with `111 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_main_runtime_policy.py`
  passed with `111 passed`.
- 2026-04-21: `PRJ-362` is complete: planning docs, operations guidance, and
  context truth now align on the attention timing production baseline and
  health-visible alignment posture.
- 2026-04-21: `PRJ-362` also closes the current attention timing baseline
  governance slice; no task remains in `READY`, so the next slice should again
  be derived from planning docs and open decisions.
- 2026-04-21: the next architecture-to-code queue is now seeded through
  `PRJ-378`.
- 2026-04-21: newly planned Groups 37 through 40 now turn the remaining
  architecture follow-ups into executable lanes for connector execution
  policy, future-write typed intents, `ActionDelivery` extensibility, and
  compatibility-sunset readiness.
- 2026-04-21: `PRJ-363` is now the first `READY` task, focused on defining one
  shared connector operation policy before more connector/provider behavior is
  added.
- 2026-04-21: `PRJ-363` is complete: connector operation defaults now have one
  shared owner in `app/core/connector_policy.py` across `calendar`,
  `task_system`, and `cloud_drive`.
- 2026-04-21: `PRJ-363` also moves planner connector intent mode selection onto
  that shared policy owner, replacing open-coded local mode literals while
  preserving the current external side-effect boundary.
- 2026-04-21: `PRJ-363` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
  passed with `91 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `141 passed`.
- 2026-04-21: `PRJ-364` is complete: planning permission gates now consume the
  shared connector-policy helper and action now fails fast on inconsistent
  connector intent mode posture before response delivery.
- 2026-04-21: `PRJ-364` also persists connector guardrail posture in runtime
  memory payloads alongside connector intent update traces for operator triage.
- 2026-04-21: `PRJ-365` is complete: regressions now pin shared-policy-derived
  connector permission gates for read-only, suggestion-only, mutation, and
  proposal-only posture plus action-side connector mode mismatch blocking.
- 2026-04-21: `PRJ-365` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
  passed with `95 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `141 passed`.
- 2026-04-21: `PRJ-366` is complete: architecture, implementation reality,
  planning docs, testing guidance, and context truth now align on the shared
  connector execution-policy baseline and action guardrail posture.
- 2026-04-21: Group 37 (`PRJ-363..PRJ-366`) is now complete.
- 2026-04-21: `PRJ-367` is complete: runtime contracts now define
  `maintain_relation` and `update_proactive_state` as first-class typed
  intent families for future durable writes.
- 2026-04-21: `PRJ-367` also moves proactive planning off generic `noop`
  placeholders when durable proactive-state posture still needs to be
  recorded.
- 2026-04-21: `PRJ-368` is complete: action now executes
  relation-maintenance and proactive follow-up state only from explicit typed
  intents, and proactive paths now persist state through typed ownership even
  when delivery is deferred.
- 2026-04-21: `PRJ-369` is complete: regressions now pin typed future-write
  boundaries across planning, action, runtime, reflection, and scheduler
  paths so relation/proactive durable writes cannot drift back to generic
  mutation posture.
- 2026-04-21: `PRJ-369` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py tests/test_scheduler_worker.py`
  passed with `225 passed`.
- 2026-04-21: `PRJ-370` is complete: architecture, implementation reality,
  planning docs, testing guidance, and context truth now align on expanded
  typed-intent ownership for proactive follow-up state and
  relation-maintenance writes.
- 2026-04-21: Group 38 (`PRJ-367..PRJ-370`) is now complete.
- 2026-04-21: `PRJ-371..PRJ-373` are complete: `ActionDelivery` now carries a
  bounded connector-safe execution envelope, action validates envelope parity
  against planning before side effects, and regressions pin shared handoff
  stability across runtime, graph adapters, and delivery routing.
- 2026-04-21: Group 39 (`PRJ-371..PRJ-374`) is now complete.
- 2026-04-21: Group 39 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
  passed with `138 passed`.
- 2026-04-21: `PRJ-374` is complete: architecture, runtime-reality, planning
  docs, testing guidance, and context truth now align on one shared
  extensible `ActionDelivery` contract with connector-safe execution
  envelopes and bounded routing visibility.
- 2026-04-21: `PRJ-375..PRJ-377` are complete: `/health.runtime_policy` now
  exposes compatibility-sunset readiness for migration-only bootstrap and
  shared debug ingress retirement, startup logs surface the same posture, and
  release smoke verifies evidence presence/coherence before using it as
  release evidence.
- 2026-04-21: Group 40 (`PRJ-375..PRJ-378`) is now complete.
- 2026-04-21: Group 40 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
  passed with `127 passed`.
- 2026-04-21: `PRJ-378` is complete: architecture, operations guidance,
  planning docs, testing guidance, and context truth now align on
  compatibility-sunset readiness governance for migration bootstrap and shared
  debug ingress posture.
- 2026-04-21: no `READY` task remains after Group 40; the next slice should
  be derived again from planning docs and open decisions.
- 2026-04-21: the next architecture-to-code queue is now seeded through
  `PRJ-394`.
- 2026-04-21: newly planned Groups 41 through 44 now turn the remaining
  architecture follow-ups into executable lanes for background adaptive-output
  ownership, durable attention-inbox rollout, role-and-skill capability
  convergence, and retrieval/theta governance.
- 2026-04-21: `PRJ-379` is now the first `READY` task, focused on defining one
  shared adaptive-output contract for reflection/background runtime results
  before durable attention and role/skill follow-ups build on that boundary.
- 2026-04-21: `PRJ-379..PRJ-382` are complete: reflection/background runtime
  now has one explicit adaptive-output summary contract, reflection snapshots
  expose that summary, `/health.reflection` surfaces adaptive-output posture,
  and runtime `system_debug.adaptive_state` carries bounded background-owned
  adaptive visibility without foreground theta mutation.
- 2026-04-21: `PRJ-383..PRJ-386` are complete: durable attention rollout now
  uses explicit `persistence_owner` and `parity_state` semantics, and
  `ATTENTION_COORDINATION_MODE=durable_inbox` preserves the same turn-assembly
  behavior baseline instead of reporting a placeholder blocker posture.
- 2026-04-21: `PRJ-387..PRJ-390` are complete: role selection now emits
  bounded `selected_skills` capability metadata from a shared skill registry,
  planning carries the same selected-skill posture forward, and skills remain
  metadata-only capabilities rather than tool or side-effect owners.
- 2026-04-21: `PRJ-391..PRJ-394` are complete: runtime and `/health` now share
  one retrieval-depth policy snapshot plus bounded theta-influence diagnostics
  across role, motivation, planning, and expression, and `system_debug` also
  exposes adaptive-state metadata for retrieval depth, theta posture, and
  selected/planned skills.
- 2026-04-21: Group 41 through Group 44 are now complete, so no `READY` task
  remains on the task board after `PRJ-394`; the next queue should again be
  derived from planning docs and open decisions.
- 2026-04-21: the next architecture-to-code queue is now seeded through
  `PRJ-410`.
- 2026-04-21: newly planned Groups 45 through 48 now turn the remaining
  architecture follow-ups into executable lanes for role-selection evidence,
  affective rollout policy, reflection scope governance, and durable attention
  contract-store rollout.
- 2026-04-21: `PRJ-395..PRJ-398` are complete: role selection now has a shared
  policy owner (`app/core/role_selection_policy.py`) with explicit
  `selection_reason` and `selection_evidence` metadata on role outputs and
  system-debug surfaces.
- 2026-04-21: Group 45 (`PRJ-395..PRJ-398`) is now complete.
- 2026-04-21: Group 45 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `160 passed`, and
  `.\.venv\Scripts\python -m pytest -q`
  passed with `729 passed`.
- 2026-04-21: `PRJ-399` is now the first `READY` task, focused on explicit
  rollout policy ownership for AI-assisted affective assessment.
- 2026-04-21: `PRJ-399..PRJ-402` are complete: affective assessment now has an
  explicit rollout policy owner with environment-default enablement semantics,
  policy-disabled fallback posture, and machine-visible runtime policy / debug
  snapshots.
- 2026-04-21: Group 46 (`PRJ-399..PRJ-402`) is now complete.
- 2026-04-21: Group 46 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_config.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `199 passed`, and
  `.\.venv\Scripts\python -m pytest -q`
  passed with `734 passed`.
- 2026-04-21: `PRJ-403..PRJ-406` are complete: reflection outputs now share an
  explicit scope owner (`app/core/reflection_scope_policy.py`) that keeps
  goal-progress and milestone conclusions goal-scoped while preserving
  adaptive/affective reflection outputs as user-global by default.
- 2026-04-21: `MemoryRepository`, reflection worker scope resolution, and
  runtime test doubles now canonicalize reflection scopes through the shared
  policy owner, so invalid scoped overrides for global reflection outputs no
  longer leak into runtime preferences or scoped conclusion reads.
- 2026-04-21: Group 47 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
  passed with `172 passed`.
- 2026-04-21: `PRJ-407..PRJ-410` are complete: durable attention now has a
  repository-backed contract store through `aion_attention_turn`,
  `MemoryRepository` attention primitives, and durable-mode coordinator usage
  without changing burst coalescing semantics.
- 2026-04-21: `/health.attention` now exposes repository-backed contract-store
  posture and cleanup visibility (`contract_store_mode`,
  `contract_store_state`, cleanup candidates) instead of parity-only owner
  metadata.
- 2026-04-21: Group 48 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_graph_state_contract.py`
  passed with `122 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py`
  passed with `79 passed`.
- 2026-04-21: the next architecture-to-code queue is now seeded through
  `PRJ-414`.
- 2026-04-21: `PRJ-411` is complete: identity/profile ownership now has one
  shared policy owner in `app/core/identity_policy.py`, and `/health.identity`
  plus runtime `system_debug.adaptive_state.identity_policy` expose the same
  boundary for operator/debug visibility.
- 2026-04-21: `PRJ-411` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `149 passed`.
- 2026-04-21: `PRJ-412` is complete: language continuity posture is now
  explicit through `/health.identity.language_continuity` and runtime
  `system_debug.adaptive_state.language_continuity`.
- 2026-04-21: `PRJ-412` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `149 passed`.
- 2026-04-21: `PRJ-413` is complete: explicit-request posture,
  profile-continuity posture, and unsupported-profile fallback are now
  regression-pinned across language utility and runtime paths.
- 2026-04-21: `PRJ-413` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `165 passed`.
- 2026-04-21: `PRJ-414` is complete: architecture, runtime-reality, planning
  docs, testing guidance, and context truth now align on the shared
  identity-policy owner plus language-continuity diagnostics baseline.
- 2026-04-21: Group 49 (`PRJ-411..PRJ-414`) is now complete.
- 2026-04-21: no seeded `READY` task remains after Group 49; the next
  architecture slice should again be derived from planning docs and open
  decisions.
- 2026-04-22: the next architecture-to-code queue is now seeded through
  `PRJ-442`.
- 2026-04-22: newly planned Groups 50 through 56 now turn the remaining open
  architecture decisions into explicit convergence lanes for runtime topology
  finalization, production-boundary hardening, retrieval plus
  affective-memory productionization, adaptive identity governance,
  goal/task-plus-proposal governance, scheduler and connector capability
  convergence, and deployment standard plus release-reliability closure.
- 2026-04-22: `PRJ-415` is now the first `READY` task, focused on defining the
  production switch criteria for deferred reflection and durable attention
  ownership before any default-mode or release-window change is attempted.
- 2026-04-22: `PRJ-415..PRJ-442` are complete.
- 2026-04-22: Groups 50 through 56 are now complete: runtime topology switch
  policy is explicit, production debug ingress defaults to break-glass-only
  posture when not explicitly overridden, retrieval now supports a local
  provider-owned hybrid embedding path, health/runtime debug expose adaptive
  identity plus planning/connector governance snapshots, and deployment health
  plus release smoke now expose the selected hosting and trigger-SLO baseline.
- 2026-04-22: no seeded `READY` task remains after Group 56; the next
  architecture slice should again be derived from planning docs and any newly
  discovered post-convergence follow-ups.
- 2026-04-22: `PRJ-443` is complete: stale queue-seeding notes from earlier
  convergence waves were pruned from the top-level planning/context surfaces so
  the repo now has one shared post-convergence operating stance instead of a
  stack of historical queue headers.
- 2026-04-22: `PRJ-444..PRJ-447` are complete: shared debug-ingress posture
  vocabulary now uses final route-owned labels
  (`shared_route_compatibility|shared_route_break_glass_only`) across runtime
  policy, response headers, release smoke, and canonical docs.
- 2026-04-22: `PRJ-448..PRJ-451` are complete: `/health.affective` and runtime
  `system_debug.adaptive_state` now distinguish perception-owned affective
  input from final affective assessment resolution, including fallback-reuse
  diagnostics.
- 2026-04-22: `PRJ-452..PRJ-453` are complete: `/health.memory_retrieval` now
  exposes `semantic_embedding_execution_class` so deterministic baseline,
  local provider-owned execution, and fallback-to-deterministic posture are
  machine-visible in one field.
- 2026-04-22: `PRJ-454` is complete: top-level planning/context surfaces now
  consistently describe post-`PRJ-453` follow-up discovery mode and no longer
  keep stale references to the older seeded `PRJ-415..PRJ-442` queue as if it
  were still the current planning baseline.
- 2026-04-22: `PRJ-455..PRJ-457` are complete: canonical attention docs,
  config guidance, ops runbook notes, and planning/context surfaces now align
  on repository-backed `aion_attention_turn` durable inbox posture and the
  exact `/health.attention` contract-store visibility fields used for
  operator triage.
- 2026-04-22: `PRJ-458..PRJ-460` are complete: runtime reality now includes
  `aion_subconscious_proposal` in the live persisted schema inventory, and the
  runbook plus planning/context surfaces now describe the concrete operator
  meaning of post-convergence health surfaces for planning, connectors,
  adaptive identity governance, and deployment.
- 2026-04-22: `PRJ-461..PRJ-463` are complete: the runbook and
  planning/context surfaces now treat `/health.affective` and
  `memory_retrieval.semantic_embedding_execution_class` as explicit
  operator-facing diagnostics for empathy triage and retrieval execution
  posture.
- 2026-04-22: architecture-conformance analysis is now refreshed against
  canonical docs plus live runtime code. The highest-priority remaining gap is
  migration parity between `app/memory/models.py` and Alembic revisions,
  followed by canonical-doc consistency cleanup and productionization of still
  rollout-shaped subsystems (connector execution, retrieval provider path,
  background worker topology, proactive cadence, role/skill maturity, and
  behavior-validation breadth).
- 2026-04-22: a new post-convergence queue is now seeded through `PRJ-491`,
  starting with Group 63 for migration parity and schema governance.
- 2026-04-22: `PRJ-464..PRJ-467` are complete: Alembic head now includes
  durable attention (`aion_attention_turn`) and subconscious proposal
  (`aion_subconscious_proposal`) tables, and schema-baseline regressions now
  exercise a fresh `alembic upgrade head` instead of trusting metadata alone.
- 2026-04-22: migration-first schema ownership is now explicit as a release
  truth for the full current model set, reducing deployment drift between live
  runtime tables and bootstrap path.
- 2026-04-22: the next `READY` lane is Group 64 (`PRJ-468..PRJ-471`),
  focused on canonical architecture-doc consistency after schema truth was
  restored.
- 2026-04-22: `PRJ-468..PRJ-471` are complete: canonical docs no longer carry
  a competing older flow where `action` precedes `expression`, and action docs
  now distinguish action-owned side effects from runtime-owned post-action
  follow-ups such as episodic memory persistence and reflection enqueue.
- 2026-04-22: `docs/README.md` and `docs/overview.md` now explicitly direct
  readers to `02_architecture.md`, `15_runtime_flow.md`, and
  `16_agent_contracts.md` as the canonical ordering/ownership set.
- 2026-04-22: the next `READY` lane is Group 65 (`PRJ-472..PRJ-475`),
  focused on connector execution productionization.
- 2026-04-22: `PRJ-472..PRJ-475` are complete: the first live provider-backed
  connector path is now explicit and implemented through ClickUp task
  creation, while calendar, cloud-drive, and remaining task-system operations
  stay policy-only on purpose.
- 2026-04-22: action now executes
  `ExternalTaskSyncDomainIntent(operation="create_task", provider_hint="clickup")`
  through a dedicated provider adapter when `CLICKUP_API_TOKEN` and
  `CLICKUP_LIST_ID` are configured, without relaxing the existing
  `planning -> expression -> action` boundary or shared connector policy.
- 2026-04-22: `/health.connectors.execution_baseline` now exposes one machine-
  visible connector execution owner plus readiness posture for the selected
  ClickUp live path (`provider_backed_ready|credentials_missing`).
- 2026-04-22: Group 65 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  passed with `181 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  passed with `184 passed`.
- 2026-04-22: the next `READY` lane is Group 66 (`PRJ-476..PRJ-479`),
  focused on retrieval provider completion.

## Working Agreements

- Keep task board and project state synchronized.
- Keep planning docs synchronized with task board.
- Keep changes small and reversible.
- Validate touched areas before marking done.
- Keep repository artifacts in English.
- Communicate with users in their language.
- Delegate with explicit ownership and avoid overlapping subagent write scope.
- Use the default loop:
  `plan -> implement -> test -> architecture review -> sync context`.
- Treat deployment docs and smoke checks as part of done-state for runtime
  changes.

## Canonical Context

- `.codex/context/PROJECT_STATE.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/LEARNING_JOURNAL.md`
- `.agents/workflows/general.md`
- `.agents/workflows/subagent-orchestration.md`

## Canonical Docs

- `docs/README.md`
- `docs/overview.md`
- `docs/architecture/02_architecture.md`
- `docs/architecture/15_runtime_flow.md`
- `docs/architecture/16_agent_contracts.md`
- `docs/architecture/17_logging_and_debugging.md`
- `docs/architecture/29_runtime_behavior_testing.md`
- `docs/architecture/26_env_and_config.md`
- `docs/architecture/27_codex_instructions.md`
- `docs/engineering/local-development.md`
- `docs/engineering/testing.md`
- `docs/planning/next-iteration-plan.md`
- `docs/planning/open-decisions.md`
- `docs/operations/runtime-ops-runbook.md`

## Optional Project Docs

- Add only if the repository truly needs them.
- Record their canonical paths here once they exist.
- `docs/implementation/runtime-reality.md`
