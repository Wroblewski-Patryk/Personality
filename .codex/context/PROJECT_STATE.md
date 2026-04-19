# PROJECT_STATE

Last updated: 2026-04-19

## Product Snapshot

- Name: Personality / AION
- Goal: build a memory-aware AI runtime that receives events, reasons through a
  structured pipeline, replies through API or Telegram, and learns lightweight
  user preferences over time
- Commercial model: TBD
- Current phase: runtime contract hardening and observability uplift

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
- Active `PRJ` execution queue is complete through `PRJ-236`; the next slice
  should be derived from `docs/planning/open-decisions.md` and registered as
  `READY` before implementation.
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
