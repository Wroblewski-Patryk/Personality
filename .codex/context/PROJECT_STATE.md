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
- 2026-04-19: documentation now explicitly separates canonical architecture in
  `docs/architecture/` from transitional implementation reality in
  `docs/implementation/runtime-reality.md`, so human-oriented design intent can
  stay stable while runtime details remain searchable.

## Technical Baseline

- Backend: Python 3.11, FastAPI, Pydantic v2
- Frontend: none in current repository scope
- Mobile: none in current repository scope
- Database: PostgreSQL with SQLAlchemy async and asyncpg
- Infra: Docker Compose locally, Coolify-targeted compose for deployment
- Hosting target: VPS deployment via Compose/Coolify-oriented runtime docs
- Deployment shape: API-first runtime with app-local reflection worker behavior
- Runtime services: FastAPI app, database, optional Telegram webhook path
- Background jobs / workers: reflection currently runs in-process as an
  app-local durable concern
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
- Active execution queue now extends through `PRJ-097`.
- Top blockers:
  - reflection subsystem is still concentrated in `app/reflection/worker.py`
    and needs concern-owned module split (`PRJ-065`)
  - adaptive signals still risk self-reinforcement loops without stronger
    evidence thresholds (`PRJ-066`)
  - conscious/subconscious coordination still lacks explicit attention inbox,
    proposal handoff, and burst-message coalescing, so rapid conversations and
    proactive wakeups can drift into duplicate or poorly gated behavior
    (`PRJ-085..PRJ-092`)
  - external productivity integrations (calendar, task providers, cloud drives)
    still need explicit connector contracts, permission gates, and action
    boundaries before the personality can safely operate across user systems
    (`PRJ-093..PRJ-097`)
  - architecture-level stack directions (`LangGraph`, `pgvector`, scheduler,
    relation system, proactive runtime) still are not implemented in the live
    runtime and now require explicit rollout groups
- Success criteria for this phase:
  - shared goal and milestone signals keep one clear implementation owner
  - runtime stage decisions are observable through structured logs
  - event and startup contracts stay explicit and regression-covered
  - docs, task board, learning journal, and code stay synchronized after each
    slice

## Recent Progress

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
