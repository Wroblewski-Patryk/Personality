# Runtime Reality

## Purpose

This document describes the implementation reality of the repository today.

It is intentionally separate from `docs/architecture/`, which remains the canonical description of the intended AION design.

If this file and `docs/architecture/` ever disagree:

- `docs/architecture/` wins as design intent
- this file records the live implementation and transitional choices

---

## Canonical vs Implemented Foreground Flow

Canonical architectural order:

`event -> perception -> context -> motivation -> role -> planning -> expression -> action -> memory -> reflection`

Current implemented foreground order:

`event -> state load -> identity -> perception -> context -> motivation -> role -> planning -> expression -> action -> memory -> reflection enqueue`

Notes:

- the runtime loads baseline state before deeper reasoning
- foreground stage execution (`perception` through `action`) now runs through
  LangGraph `StateGraph` nodes
- expression currently prepares the outbound message before action executes delivery
- action remains the only place where side effects occur

---

## Delivery and Side-Effect Boundary

The current runtime uses an explicit delivery handoff between expression and action.

Current implementation details:

- `ExpressionAgent` produces message, tone, language, and channel-oriented output
- expression stage materializes an explicit `ActionDelivery` handoff contract
- `ActionDelivery` now includes a bounded `execution_envelope` that can carry
  connector intent snapshots and permission-gate posture without creating a
  connector-specific expression handoff
- `ActionExecutor` consumes that delivery object and validates
  `execution_envelope` parity against planning before delivery side effects
- `DeliveryRouter` owns the channel-specific dispatch behavior and may append
  bounded execution-envelope visibility notes for operator-facing traces

This is a runtime convenience and transport contract, not a replacement for the canonical cognitive order.

---

## Graph Compatibility Boundary

The runtime now defines an explicit compatibility layer for future LangGraph
migration without changing foreground behavior first.

Current implementation details:

- `app/core/graph_state.py` defines `GraphRuntimeState` plus conversion helpers
  between current `RuntimeResult` and graph-compatible state.
- `app/core/graph_adapters.py` wraps existing stage modules
  (`perception`, `affective_assessment`, `context`, `motivation`, `role`,
  `planning`, `expression`, `action`) so they can be called with one shared
  graph state contract.
- `expression_to_action_delivery(...)` is now shared between the current
  orchestrator and graph-ready adapters to keep delivery shaping semantics
  consistent.

Transition note:

- the live foreground runtime now uses a hybrid orchestration model in
  `app/core/runtime.py`: baseline load and post-action persistence remain in
  Python orchestration, while cognitive foreground stages execute through
  `app/core/runtime_graph.py`
- this compatibility boundary exists to enable incremental migration instead of
  a big-bang rewrite

## Foreground Convergence Contract (PRJ-276)

Target-state ownership for foreground convergence is now explicit in
`docs/architecture/16_agent_contracts.md`.

Current implementation already follows that ownership split:

- runtime-owned pre-graph segment:
  `memory_load` plus shared state seed assembly in `app/core/runtime.py`
- graph-owned stage segment:
  `perception -> affective_assessment -> context -> motivation -> role ->
  planning -> expression -> action` in `app/core/runtime_graph.py`
- runtime-owned post-graph segment:
  `memory_persist` and `reflection_enqueue` in `app/core/runtime.py`

Runtime boundary ownership is now explicit in orchestrator structure:

- `_build_foreground_graph_state_seed(...)` owns pre-graph state handoff
- `_run_foreground_stage_graph(...)` owns graph-stage execution boundary checks
- `_run_post_graph_followups(...)` owns runtime follow-up persistence/trigger
  stages after graph completion

Targeted contract diff review for this slice:

- canonical docs keep the cognitive order and ownership principles
- runtime-reality keeps transitional wiring explicit without redefining
  architecture
- next boundary-alignment implementation slice is `PRJ-278`

---

## Current Runtime Contracts

### Optional LangChain prompt wrappers

OpenAI prompt construction now supports an optional LangChain utility path:

- `app/integrations/openai/prompting.py` wraps prompt assembly with
  LangChain-compatible templates when available
- runtime behavior remains fully functional without LangChain dependencies
- LangChain remains a utility layer, not a runtime orchestration dependency

### Motivation modes

The live runtime currently uses:

- `respond`
- `ignore`
- `analyze`
- `execute`
- `clarify`

### Identity and language continuity boundary

The live runtime now enforces explicit identity and language ownership:

- `aion_profile.preferred_language` is the durable profile owner for language
  continuity in identity loading
- `response_style` and `collaboration_preference` are conclusion-owned runtime
  preference inputs, not durable profile fields
- relation fallback cues may shape stage-level tie-break behavior, but they do
  not rewrite identity profile continuity fields
- `app/core/identity_policy.py` is now the shared owner for that boundary, and
  `/health.identity` plus `system_debug.adaptive_state.identity_policy` expose
  the same ownership snapshot for operator/debug visibility

Language decision precedence is now explicit:

- explicit language request
- language-specific diacritic signal
- strong keyword signal
- continuity resolution from recent memory and profile
- weak keyword signal
- default fallback (`en`)

Continuity parsing now accepts structured episodic language hints from payload
(`payload.response_language` and `payload.language`) plus summary fallback, but
only for supported runtime language codes (`en|pl`).

API identity fallback for language/profile continuity is request-scoped and
explicit: `meta.user_id` -> `X-AION-User-Id` -> `anonymous`.

### Affective assessment slot

The live runtime now carries an explicit affective contract slot per turn:

- `affect_label`
- `intensity`
- `needs_support`
- `confidence`
- `source`
- `evidence`

Current implementation posture:

- perception emits deterministic placeholder signals as baseline
- runtime runs a dedicated `affective_assessment` stage that can consume LLM
  classification and normalize it to the shared contract
- affective-assessment rollout is now governed by one explicit policy owner,
  with environment-default enablement (`enabled` outside production,
  `disabled` in production) unless explicitly overridden
- when LLM classification is unavailable or invalid, the stage falls back to
  deterministic baseline signals and marks source as `fallback`
- policy-disabled fallback and classifier-unavailable fallback are now separate
  machine-visible postures in runtime policy and system-debug surfaces
- motivation, role, and expression now consume `perception.affective` as the
  primary support/emotion signal owner for turn behavior

### Affective memory signals

The live runtime now persists lightweight affective memory hints in episodic
payloads and reflects them into slower-moving semantic signals:

- episodic payload fields: `affect_label`, `affect_intensity`,
  `affect_needs_support`, `affect_source`, `affect_evidence`
- reflection conclusions: `affective_support_pattern`,
  `affective_support_sensitivity`
- runtime consumption: context summary and motivation scoring can reuse these
  reflected affective signals across turns

### Scoped conclusions

The live runtime now supports scoped semantic conclusions:

- `aion_conclusion` rows include `scope_type` and `scope_key`
- scoped uniqueness is `(user_id, kind, scope_type, scope_key)`
- reflection writes goal-operational conclusions with goal scope
- reflection scope ownership is now centralized in
  `app/core/reflection_scope_policy.py`
- goal-progress and milestone conclusions remain goal-scoped, while
  affective/adaptive reflection outputs stay user-global by default
- repository/runtime readers now canonicalize invalid scoped overrides for
  global reflection outputs instead of letting them shadow global posture

Current transition note:

- runtime consumers now perform scope-aware reads by primary active goal with
  global fallback, reducing cross-goal leakage in context, motivation,
  planning, and milestone enrichment

### Retrieval depth and compression

The live runtime no longer depends on a strict latest-five memory fetch:

- runtime currently loads up to 12 recent episodes before context selection
- context applies ranking/compression across language match, memory layer mode,
  topical overlap, affective relevance, and importance
- final context memory hint remains compressed to the top relevant items

Repository memory-layer API vocabulary is now explicit in code:

- `get_recent_episodic_memory(...)`
- `get_conclusions_for_layer(..., layer=\"semantic|affective|operational\")`
- `get_operational_memory_view(...)`
- `conclusion_memory_layer(kind)` classification helper

Hybrid retrieval surfaces are now also explicit:

- semantic embeddings are stored in `aion_semantic_embedding`
- `get_hybrid_memory_bundle(...)` merges episodic, semantic, and affective
  candidates with lexical overlap plus vector similarity scoring
- runtime logs and memory diagnostics now expose hybrid retrieval signals
  (lexical/vector hit counts) for observability
- episodic, semantic-conclusion, affective-conclusion, and relation embedding
  rows now materialize on write when source-family gates are enabled, with
  explicit materialization status metadata (`materialized_on_write`)
- manual refresh ownership keeps vector rows explicit with
  `pending_manual_refresh` status instead of immediate vector materialization
- source-family rollout remains explicit through `EMBEDDING_SOURCE_KINDS`
  gating, so each family can be enabled progressively without implicit writes

Production retrieval baseline (`PRJ-284`, planning contract):

- provider ownership: deterministic effective owner until provider execution is
  implemented
- refresh ownership: `on_write` during rollout, with `manual` as explicit
  operator override
- family rollout order: `episodic+semantic` first, then `affective`, then
  `relation`

Current limitation:

- deterministic fallback embeddings are live; requested non-implemented
  providers still fall back to deterministic execution, and provider-owned
  embedding lifecycle/tuning are planned follow-up work.
- `/health.memory_retrieval` now exposes explicit warning posture fields
  (`semantic_embedding_warning_state`, `semantic_embedding_warning_hint`) and
  startup warning logs reuse the same warning-state semantics.
- embedding persistence scope is now explicitly configurable through
  `EMBEDDING_SOURCE_KINDS` (`episodic|semantic|affective|relation`), and
  health exposes effective configured source families.
- health also exposes source-coverage posture for current retrieval path
  (`semantic_embedding_source_coverage_state`,
  `semantic_embedding_source_coverage_hint`), and startup warning logs reuse
  this shared coverage-state semantics.
- embedding refresh-cadence posture is now explicit through
  `EMBEDDING_REFRESH_MODE` and `EMBEDDING_REFRESH_INTERVAL_SECONDS`, surfaced
  in `/health.memory_retrieval` and startup warning logs
  (`embedding_refresh_warning`) when vectors are enabled with manual mode.
- refresh posture now also includes shared derived diagnostics
  (`semantic_embedding_refresh_state`,
  `semantic_embedding_refresh_hint`) so startup and health use one refresh
  semantics owner.
- model-governance posture is now also explicit through shared diagnostics
  (`semantic_embedding_model_governance_state`,
  `semantic_embedding_model_governance_hint`) so startup and health align on
  deterministic custom-model-name visibility.
- provider-ownership posture is now explicit through shared diagnostics
  (`semantic_embedding_provider_ownership_state`,
  `semantic_embedding_provider_ownership_hint`) so startup fallback warnings
  and health diagnostics use the same ownership semantics.
- provider-ownership enforcement posture is now explicit through
  `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` and helper-owned diagnostics
  (`semantic_embedding_provider_ownership_enforcement`,
  `semantic_embedding_provider_ownership_enforcement_state`,
  `semantic_embedding_provider_ownership_enforcement_hint`), enabling strict
  startup block mode for unresolved fallback ownership posture.
- model-governance enforcement posture is now explicit through
  `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` and helper-owned diagnostics
  (`semantic_embedding_model_governance_enforcement`,
  `semantic_embedding_model_governance_enforcement_state`,
  `semantic_embedding_model_governance_enforcement_hint`), enabling strict
  startup block mode for deterministic custom-model-name governance posture.
- owner-strategy recommendation posture is now explicit through helper-owned
  diagnostics (`semantic_embedding_owner_strategy_state`,
  `semantic_embedding_owner_strategy_hint`,
  `semantic_embedding_owner_strategy_recommendation`) for vectors-disabled,
  deterministic baseline/manual, and fallback provider ownership states.
- source-rollout recommendation posture is now explicit through helper-owned
  diagnostics (`semantic_embedding_source_rollout_state`,
  `semantic_embedding_source_rollout_hint`,
  `semantic_embedding_source_rollout_recommendation`) for semantic+affective
  baseline, single-source rollout phases, and foundational-only source sets.
- source-rollout sequencing posture is now explicit through helper-owned
  diagnostics (`semantic_embedding_source_rollout_order`,
  `semantic_embedding_source_rollout_enabled_sources`,
  `semantic_embedding_source_rollout_missing_sources`,
  `semantic_embedding_source_rollout_next_source_kind`,
  `semantic_embedding_source_rollout_completion_state`,
  `semantic_embedding_source_rollout_phase_index`,
  `semantic_embedding_source_rollout_phase_total`,
  `semantic_embedding_source_rollout_progress_percent`), including explicit
  all-sources-enabled posture (`all_vector_sources_enabled`).
- strict-rollout preflight posture is now explicit through helper-owned
  diagnostics (`semantic_embedding_strict_rollout_violations`,
  `semantic_embedding_strict_rollout_violation_count`,
  `semantic_embedding_strict_rollout_ready`,
  `semantic_embedding_strict_rollout_state`,
  `semantic_embedding_strict_rollout_hint`,
  `semantic_embedding_strict_rollout_recommendation`) and enforcement guidance
  fields (`semantic_embedding_recommended_provider_ownership_enforcement`,
  `semantic_embedding_recommended_model_governance_enforcement`,
  `semantic_embedding_provider_ownership_enforcement_alignment`,
  `semantic_embedding_model_governance_enforcement_alignment`,
  `semantic_embedding_enforcement_alignment_state`,
  `semantic_embedding_enforcement_alignment_hint`) so startup and health expose
  one strict-rollout recommendation/alignment owner.
- startup now emits `embedding_strategy_hint` with strict-rollout readiness,
  recommendation, violation summary, and enforcement-alignment diagnostics when
  vectors are enabled.
- startup now also emits `embedding_source_rollout_hint` when vectors are
  enabled and rollout still has a pending next source kind.
- source-rollout enforcement posture is now explicit through
  `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` and shared diagnostics
  (`semantic_embedding_source_rollout_enforcement`,
  `semantic_embedding_source_rollout_enforcement_state`,
  `semantic_embedding_source_rollout_enforcement_hint`), enabling
  warn-mode rollout visibility and strict-mode startup block behavior while
  rollout remains pending.
- source-rollout enforcement recommendation/alignment posture is now explicit
  through shared diagnostics
  (`semantic_embedding_recommended_source_rollout_enforcement`,
  `semantic_embedding_source_rollout_enforcement_alignment`,
  `semantic_embedding_source_rollout_enforcement_alignment_state`,
  `semantic_embedding_source_rollout_enforcement_alignment_hint`), so startup
  and `/health` share one recommendation/alignment owner for source-rollout
  enforcement.
- startup now emits `embedding_source_rollout_enforcement_hint` and
  recommendation/alignment-enriched warning/block logs for source-rollout
  enforcement posture.
- refresh cadence posture is now explicit through helper-owned diagnostics
  (`semantic_embedding_refresh_cadence_state`,
  `semantic_embedding_refresh_cadence_hint`) plus refresh recommendation and
  alignment diagnostics
  (`semantic_embedding_recommended_refresh_mode`,
  `semantic_embedding_refresh_alignment_state`,
  `semantic_embedding_refresh_alignment_hint`) so `/health` and startup use one
  refresh strategy owner.
- startup now emits `embedding_refresh_hint` whenever refresh mode deviates from
  rollout recommendation posture.

Retrieval-depth governance is now also explicit:

- `app/core/retrieval_policy.py` owns a shared retrieval-depth policy snapshot
  for runtime and `/health`
- runtime `system_debug.adaptive_state` now includes retrieval-depth posture,
  bounded theta influence, and selected/planned skill metadata
- `/health.memory_retrieval.retrieval_depth_policy` exposes the same policy
  owner instead of leaving load-depth semantics only inside orchestrator code

### Event API behavior

`POST /event` currently returns:

- a compact public response by default
- an optional debug payload when `debug=true`, debug exposure is enabled by
  policy, and compatibility query route is enabled
- explicit primary internal debug route `POST /internal/event/debug` for full
  runtime inspection when debug exposure is enabled
- shared `POST /event/debug` remains available as compatibility ingress during
  migration and supports explicit posture modes
  (`compatibility|break_glass_only`)
- debug responses now include an explicit `system_debug` surface with canonical
  behavior-validation fields:
  - normalized event metadata and identifiers
  - perception output
  - retrieved memory bundle (`episodic|semantic|affective|relations`) plus
    retrieval diagnostics
  - context, motivation, role, plan summary with explicit domain intents
  - expression and action result
- when API payload metadata omits `meta.user_id`, runtime can use
  `X-AION-User-Id` as a fallback identity key before defaulting to `anonymous`
- for Telegram burst traffic, non-owner duplicate events can return a compact
  queued response (`queue.queued=true` plus reason metadata) instead of running
  duplicate foreground turns

### Health behavior

`GET /health` currently exposes:

- app status
- reflection worker queue snapshot
- non-secret runtime policy flags
- scheduler cadence posture (`execution_mode`, cadence owners, dispatch reasons,
  readiness/blockers) and latest tick summaries
- attention turn-assembly posture (`coordination_mode`, owner posture,
  readiness/blockers, timing windows, pending/claimed/answered counters)

Production debug access now also supports explicit token-requirement policy via
`PRODUCTION_DEBUG_TOKEN_REQUIRED` (default `true`).
Compatibility `POST /event?debug=true` route now supports explicit
environment-aware policy via `EVENT_DEBUG_QUERY_COMPAT_ENABLED`
(default `true` outside production, `false` in production).
`PRJ-307` now defines target debug ingress boundary: full runtime debug payload
access now uses dedicated internal route `POST /internal/event/debug` as the
primary ingress path; shared-endpoint `POST /event/debug` remains transitional
compatibility surface owned by explicit shared-ingress posture controls.
Target production baseline is now explicitly documented as migration-only +
strict policy posture with debug exposure disabled by default; runtime rollout
now enforces production strict policy by default when enforcement is unset, and
explicit `warn` override remains the controlled temporary escape hatch.
`create_tables` compatibility remains transitional and is now governed by
explicit removal guardrails (`PRJ-306`) documented in planning/ops docs.
Runtime policy health output now also includes `debug_access_posture` and
`debug_token_policy_hint` plus compat-route posture markers
(`event_debug_query_compat_enabled`, `event_debug_query_compat_source`) and
compat-route usage telemetry (`event_debug_query_compat_telemetry`) for
operator-visible debug access hardening posture.
Health output now also exposes explicit debug-ingress ownership/posture fields:
`event_debug_ingress_owner`, `event_debug_internal_ingress_path`,
`event_debug_shared_ingress_path`, `event_debug_shared_ingress_mode`,
`event_debug_shared_ingress_break_glass_required`, and
`event_debug_shared_ingress_posture`.
Health output also exposes derived compat sunset signals:
`event_debug_query_compat_allow_rate`, `event_debug_query_compat_block_rate`,
`event_debug_query_compat_recommendation`,
`event_debug_query_compat_sunset_ready`, and
`event_debug_query_compat_sunset_reason`.
Any observed compat attempts (even blocked ones) are treated as migration-needed
for sunset recommendation until compat traffic disappears or compat route is
already disabled.
Health output now also includes rolling-window trend fields:
`event_debug_query_compat_recent_attempts_total`,
`event_debug_query_compat_recent_allow_rate`,
`event_debug_query_compat_recent_block_rate`, and
`event_debug_query_compat_recent_state`.
Rolling-window size is now configurable via
`EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` (default `20`).
Health output also includes compat freshness fields:
`event_debug_query_compat_stale_after_seconds`,
`event_debug_query_compat_last_attempt_age_seconds`, and
`event_debug_query_compat_last_attempt_state` so operators can distinguish
stale historical compat traffic from fresh migration-window usage.
Freshness stale threshold is configurable via
`EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS` (default `86400`).
Health output now also includes activity posture fields:
`event_debug_query_compat_activity_state` and
`event_debug_query_compat_activity_hint`, which summarize
disabled/no-attempt/stale-historical/recent-attempt states for migration
decision support while keeping the stricter sunset-ready contract unchanged.
Strict rollout mismatch previews now include
`event_debug_token_missing=true` when production debug exposure is enabled
without a configured token while token requirement mode is active.
Strict mismatch previews also include `event_debug_query_compat_enabled=true`
when production debug exposure keeps compatibility query route enabled.
Compat-route accepted responses now include explicit deprecation headers:
`X-AION-Debug-Compat`, `X-AION-Debug-Compat-Deprecated`, and `Link`.

---

## Relation Runtime Reality

Relation memory is now a first-class live subsystem:

- `aion_relation` stores scoped relation records with confidence, source,
  evidence count, and decay metadata
- reflection derives relation updates from recurring interaction signals and
  persists them through repository-owned relation APIs
- runtime now loads high-confidence relations and passes relation cues into
  context, role, planning, and expression stage logic

Current behavior:

- relation lifecycle is now explicit: repeated same-value observations refresh
  confidence/evidence posture, value-shift observations reset evidence posture,
  and stale signals weaken or expire through age-aware confidence revalidation
- trust influence now extends beyond tie-break posture into proactive behavior:
  `delivery_reliability` can shape interruption cost, proactive relevance,
  outreach confidence posture, and delivery guard pressure through shared
  adaptive policy owners
- low-confidence relation cues remain descriptive-only and are filtered before
  trust-sensitive planning/expression/proactive behavior paths can consume them
- proactive relevance and scheduler attention gating now consume governed
  relation/theta policy surfaces from `app/core/adaptive_policy.py`
- adaptive relation/theta cues may tighten proactive posture, but attention and
  anti-spam gate boundaries remain explicit owners

---

## Scheduler Contract Reality

Scheduler-facing runtime contracts are now explicit:

- scheduler events are normalized through dedicated contract helpers
- source/subsource and payload shape checks are centralized in
  `app/core/scheduler_contracts.py`
- runtime config includes scheduler and cadence boundaries:
  `SCHEDULER_ENABLED`, `SCHEDULER_EXECUTION_MODE`, `REFLECTION_INTERVAL`,
  `MAINTENANCE_INTERVAL`, `PROACTIVE_ENABLED`, `PROACTIVE_INTERVAL`
- in-process scheduler cadence is now implemented through
  `app/workers/scheduler.py` for reflection and maintenance routines
- proactive ticks now have a live decision and delivery-guard path when a
  scheduler proactive event is received
- scheduler runtime posture and latest tick summaries are visible through
  `GET /health`
- maintenance/proactive cadence dispatch now uses shared owner-aware boundary
  decisions (`in_process_owner_mode|externalized_owner_mode`) and scheduler
  maintenance path explicitly no-ops in externalized posture

`PRJ-308` now defines the target cadence-ownership direction:

- long-term production cadence ownership for maintenance/proactive wakeups
  should move to a dedicated external scheduler owner
- app-local scheduler cadence remains transitional during rollout and as an
  explicit fallback path
- runtime remains the owner of scheduled-event contract normalization and
  guardrail/conscious execution boundaries regardless of cadence owner

Current limitation:

- autonomous proactive cadence loops are not yet live in scheduler worker.

---

## Current Persisted Runtime State

The codebase currently persists these concrete tables:

- `aion_memory`
- `aion_profile`
- `aion_conclusion`
- `aion_semantic_embedding`
- `aion_theta`
- `aion_relation`
- `aion_goal`
- `aion_task`
- `aion_goal_progress`
- `aion_goal_milestone`
- `aion_goal_milestone_history`
- `aion_reflection_task`

These names describe implementation reality, not the canonical abstraction layer.

---

## Current Goal and Task Capability

Today the runtime can already:

- load active goals and tasks before deeper planning
- use goal and task relevance during context, motivation, and planning
- create lightweight goals from explicit user phrasing
- create lightweight tasks from explicit user phrasing
- promote bounded inferred goals/tasks from repeated blocker evidence when
  explicit declarations are absent
- apply delivery-reliability-aware trust gates to inferred promotion thresholds
  (`low_trust` uses stricter importance and repeated-signal requirements;
  `high_trust` allows bounded lower-threshold promotion)
- update task status from explicit progress signals
- maintain matching task status from inferred blocker evidence without creating
  duplicate task records
- refresh returned goal and task state after action-layer writes

Current intent-ownership boundary:

- planning emits explicit `domain_intents` (goal/task/task-status plus
  inferred-promotion and maintenance intents, plus preference intents, or
  `noop`)
- planning now also emits explicit future-write intents for proactive follow-up
  state (`update_proactive_state`) and can represent relation-maintenance
  writes through `maintain_relation`
- planning also emits `inferred_promotion_diagnostics`
  (`reason=...`, `result=...`) so inferred trust-gate posture is machine-visible
- action executes those typed intents and no longer reparses raw user text for
  durable domain writes; proactive follow-up state no longer hides behind
  generic `noop` when the runtime still needs a durable state trace
- runtime `system_debug.plan` now carries those inferred diagnostics for
  operator-facing debug triage
- role selection now also emits bounded `selected_skills` capability metadata
  from `app/core/skill_registry.py`, and planning carries that metadata
  forward without turning skills into tools or side-effect owners
- role selection now routes through `app/core/role_selection_policy.py`, which
  exposes `selection_reason` and `selection_evidence` metadata on role outputs
  and system-debug surfaces so role precedence stops living only in local agent
  conditionals

Reflection also derives lightweight operational signals such as:

- `preferred_role`
- `collaboration_preference`
- `goal_progress_score`
- `goal_progress_trend`
- `goal_progress_arc`
- `goal_milestone_state`
- `goal_milestone_transition`
- `goal_milestone_arc`
- `goal_milestone_pressure`
- `goal_milestone_dependency_state`
- `goal_milestone_due_state`
- `goal_milestone_due_window`
- `goal_milestone_risk`

---

## Current Reflection Reality

Reflection is already a real subsystem in the repository.

Current behavior:

- reflection tasks are durably written to Postgres
- the app hosts an in-process worker
- runtime mode is explicit (`in_process|deferred`)
- failed tasks can be retried with bounded backoff
- queue visibility is exposed through health reporting
- `/health.reflection` now includes a deployment-readiness snapshot
  (`ready`, `blocking_signals`, selected/baseline runtime mode) so reflection
  mode posture no longer depends on log-only interpretation
- reflection updates conclusions, theta, and lightweight goal-progress signals
- reflection inference ownership is now split into concern modules:
  - `app/reflection/goal_conclusions.py`
  - `app/reflection/adaptive_signals.py`
  - `app/reflection/affective_signals.py`
- adaptive updates now require outcome evidence and user-visible cues so
  `preferred_role`, `theta`, and collaboration fallback are less likely to
  self-reinforce from role-only traces
- milestone pressure heuristics now prefer phase consistency plus
  arc/transition evidence over pure time-window drift
- canonical adaptive influence governance policy is now documented in
  `docs/architecture/16_agent_contracts.md`, including explicit evidence gates
  and precedence for affective, relation, preference, and theta signals
- foreground cognition stages now consume a shared policy owner
  (`app/core/adaptive_policy.py`) for relation thresholds, preferred-role
  evidence gating, theta dominance, and adaptive tie-break posture checks
- proactive decision and scheduler attention gate now consume the same policy
  owner for relation/theta cues through explicit helper surfaces
- regression coverage now pins anti-feedback-loop behavior,
  goal-scoped relation anti-leakage for proactive attention gating, and
  sub-threshold adaptive influence boundaries across role/motivation/planning
- reflection snapshots now expose `adaptive_output_summary`, which provides one
  bounded background-owned view of conclusion kinds, relation types, progress
  signals, proposal types, and theta-update posture produced by the worker
- `/health.reflection.adaptive_outputs` and runtime
  `system_debug.adaptive_state.background_adaptive_outputs` now surface that
  adaptive-output posture for operator/debug visibility without giving the
  foreground loop write ownership over adaptive state

Current topology ownership split:

- foreground runtime owns enqueue (`reflection_enqueue`) after
  `memory_persist`
- queue persistence/retry semantics are durable and mode-independent
- worker dispatch owner depends on runtime mode:
  - `in_process`: app-local worker can dispatch immediately
  - `deferred`: pending queue is expected to be drained by external
    scheduler/worker driver

Deployment baseline update (`PRJ-301`):

- production default remains `REFLECTION_RUNTIME_MODE=in_process`
- deferred mode is treated as rollout posture with explicit
  external-dispatch readiness criteria documented in
  `docs/operations/runtime-ops-runbook.md`
- release smoke now fails fast when reflection deployment-readiness blockers
  are present in `/health.reflection.deployment_readiness`
- reflection scope governance now treats cross-goal leakage as a shared
  reader/writer contract problem, not only as a worker-local heuristic

This is more advanced than a purely conceptual background loop, but still
lighter than the long-term architecture could become.

---

## Coordination Direction (Live Baseline)

The repository now includes a live conscious/subconscious coordination baseline
and keeps additional expansion work explicitly queued.

The coordination direction remains:

- one explicit attention inbox for user turns, scheduler wakeups, and
  subconscious proposals
- turn assembly for bursty chat traffic so multiple rapid user messages can be
  answered as one conscious turn instead of one reply per raw message
- subconscious-to-conscious proposal handoff instead of direct subconscious
  messaging
- explicit attention gating before proactive delivery
- conscious wakeups and subconscious cadence treated as separate runtime
  concerns

What is already live:

- runtime graph-state contracts now explicitly model `attention_inbox`,
  `pending_turn`, `subconscious_proposals`, and `proposal_handoffs`
- canonical architecture now also records explicit ownership for this boundary:
  attention owns turn assembly state, planning owns proposal handoff decisions,
  and action remains the only side-effect owner
- `POST /event` applies Telegram burst coalescing through one in-memory
  attention-turn coordinator; rapid pending messages can assemble into one turn
  and duplicate/non-owner burst events return queued metadata instead of
  triggering duplicate runtime runs
- attention coordination owner posture is now explicit through
  `ATTENTION_COORDINATION_MODE` (`in_process|durable_inbox`) and
  `/health.attention` readiness fields (`coordination_mode`,
  `turn_state_owner`, `deployment_readiness`)
- `/health.attention` now also exposes durable-rollout parity fields
  (`persistence_owner`, `parity_state`), and `durable_inbox` mode preserves the
  same burst coalescing / claimed-turn / answered-turn semantics as
  `in_process`
- `durable_inbox` mode now also persists active turn-assembly state through a
  repository-backed `aion_attention_turn` contract store instead of remaining
  parity-only scaffolding
- `/health.attention` now exposes durable contract-store posture and cleanup
  visibility (`contract_store_mode`, `contract_store_state`,
  `stale_cleanup_candidates`, `answered_cleanup_candidates`)
- attention turn timing is now runtime-configurable through
  `ATTENTION_BURST_WINDOW_MS`, `ATTENTION_ANSWERED_TTL_SECONDS`, and
  `ATTENTION_STALE_TURN_SECONDS`
- reflection now derives and persists subconscious proposals with explicit
  proposal lifecycle state (`pending|accepted|merged|deferred|discarded`)
- conscious runtime now treats `pending|deferred` proposals as retriable input
  for proposal re-entry and skips non-retriable statuses during planning
- conscious planning/runtime now records proposal handoff decisions and resolves
  persisted proposals only after conscious acceptance/defer/discard decisions
- subconscious research proposals now carry explicit read-only policy/tool
  bounds (`research_policy`, `allowed_tools`)
- proactive scheduler events now pass through an explicit attention gate
  (quiet-hours, cooldown, unanswered-backlog with adaptive-only tightening
  limits) before delivery planning
- proactive planning now records the resulting delivery posture through typed
  `update_proactive_state` intents
- proactive outreach outcomes and connector permission-gate outcomes now share
  the same conscious plan/action execution boundary
- planning/action contracts now include connector permission-gate outputs plus
  typed calendar/task/drive connector intents without direct provider side
  effects
- relation-maintenance writes can now also pass through that same typed
  action boundary through explicit `maintain_relation` intents
- connector operation posture now has one shared owner in
  `app/core/connector_policy.py`, reused by planner gate shaping and action
  guardrails across `calendar`, `task_system`, and `cloud_drive`
- action now fails fast on connector intent mode mismatch before delivery side
  effects and persists connector guardrail posture alongside connector intent
  updates for runtime-visible triage
- regression coverage now explicitly pins that proactive scheduler plans stay
  separate from proposal handoff resolution and connector permission-gate intent
  shaping, while API attention turn assembly and conscious proposal resolution
  remain covered end to end

Important non-live notes:

- subconscious runtime is still not allowed to communicate with the user
  directly
- conscious runtime remains the only owner of user-visible delivery and other
  external side effects

This coordination model baseline is now implemented through `PRJ-295`.

---

## Internal Planning State vs External Systems (Planned)

Goals and tasks are treated as integral internal planning state of the
personality, not as a detached external plugin.

Planned clarification:

- internal goals/tasks remain part of cognition, motivation, planning, and
  reflection
- connected external systems such as calendars, task apps, and cloud drives
  are treated as authorized integration surfaces, not as replacements for
  internal planning state
- future connector support should project or synchronize internal planning into
  user-authorized external systems only through explicit action-layer
  boundaries

This boundary is now implemented through `PRJ-096`, with capability-discovery
follow-up still queued in `PRJ-097`.

---

## Current Runtime Policy Flags

The repository currently supports these notable runtime policy controls:

- `STARTUP_SCHEMA_MODE`
- `EVENT_DEBUG_ENABLED`
- `PRODUCTION_POLICY_ENFORCEMENT`

Current policy posture:

- migration-first startup is the default
- debug payload exposure is environment-aware
- production policy mismatches can warn or fail fast depending on enforcement mode

---

## Why This Split Exists

This document exists so that:

- canonical architecture can stay clean and human-oriented
- temporary implementation choices remain searchable
- runtime truth does not silently overwrite architectural intent

That split is deliberate and should be preserved.
