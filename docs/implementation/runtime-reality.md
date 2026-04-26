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
- `/health.identity.language_continuity` now exposes the language-continuity
  policy baseline (precedence, supported codes, source families), while
  `system_debug.adaptive_state.language_continuity` exposes selected source,
  candidate continuity inputs, and fallback posture for the current event

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
- `/health.affective` now exposes the perception-owned affective input policy
  alongside assessment rollout posture
- runtime `system_debug.adaptive_state` now exposes both
  `affective_input_policy` and per-turn `affective_resolution`, so operators
  can distinguish heuristic input from final affective outcome and fallback
  reuse
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

### Tool-grounded learning capture

The live runtime now treats selected external reads as bounded learned-state
inputs instead of leaving them permanently turn-local.

Current implementation details:

- `ActionExecutor` is the only owner that may reduce approved provider-backed
  read results into tool-grounded learning candidates
- approved source families are currently:
  - `knowledge_search.search_web`
  - `web_browser.read_page`
  - `task_system.list_tasks`
  - `calendar.read_availability`
  - `cloud_drive.list_files`
- memory persistence still happens through normal semantic conclusion writes
  after action execution; there is no side path that writes raw provider
  payloads directly into learned state
- learned-state inspection now exposes tool-grounded semantic conclusions as a
  visible subset of learned knowledge instead of mixing them silently with
  other semantic conclusions

Current evidence surfaces:

- `/health.learned_state.tool_grounded_learning`
- `incident_evidence.policy_posture["learned_state"].tool_grounded_learning`
- internal `GET /internal/state/inspect?user_id=...` knowledge summaries
- behavior-validation scenarios `T17.1..T17.2`

### Durable capability-record catalog

The live runtime now exposes one fuller backend capability-record catalog
instead of leaving future callers to reconstruct role, skill, and connector
truth from unrelated surfaces.

Current implementation details:

- `/health.capability_catalog` exposes the global runtime policy posture for:
  - described role presets
  - described skill records
  - runtime selection surfaces
  - authorization posture for approved tool families and operations
- internal `GET /internal/state/inspect?user_id=...` exposes the same catalog
  with a user-scoped `authorization_subject` so future UI/admin callers can
  tell whether they are reading global policy truth or a user-scoped
  authorization view
- role presets are surfaced as descriptive durable records with
  `selection_authority=runtime_turn_selection`; they do not override runtime
  role selection
- skill records remain metadata-only guidance and are surfaced through
  `described_skill_ids`, registry metadata, and current-turn selection
  visibility; they do not grant executable authority by themselves
- tool authorization remains bound to existing connector permission gates and
  provider-readiness posture:
  - public read operations such as `knowledge_search.search_web` and
    `web_browser.read_page` remain authorized without opt-in
  - organizer reads remain authorization-visible but opt-in-bound
  - organizer mutations remain confirmation-gated

Current evidence surfaces:

- `/health.capability_catalog.capability_record_truth_model`
- `/health.capability_catalog.role_posture`
- `/health.capability_catalog.skill_catalog_posture`
- `/health.capability_catalog.tool_and_connector_posture`
- internal `GET /internal/state/inspect?user_id=...`
- release smoke capability-catalog contract verification
- runtime behavior regression proving that a work-partner website-reading turn
  does not imply unrelated organizer mutation authority

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

Production retrieval baseline (`PRJ-476`, planning contract):

- provider ownership:
  - `openai` is the target provider-owned production baseline when
    `OPENAI_API_KEY` is configured
  - `local_hybrid` remains a local transition path
  - `deterministic` remains the explicit compatibility fallback baseline
- refresh ownership: `on_write` during rollout, with `manual` as explicit
  operator override
- family rollout order: `episodic+semantic` first, then `affective`, then
  `relation`
- `/health.memory_retrieval.semantic_embedding_execution_class` now exposes
  `deterministic_baseline`, `local_provider_owned`,
  `provider_owned_openai_api`, or `fallback_to_deterministic` as the current
  execution posture
- `/health.memory_retrieval` now also exposes one explicit production-baseline
  contract:
  `semantic_embedding_production_baseline=openai_api_embeddings` plus
  `semantic_embedding_production_baseline_state` and
  `semantic_embedding_production_baseline_hint`
- `/health.memory_retrieval` now also exposes one explicit retrieval lifecycle
  contract owned by `retrieval_lifecycle_policy`:
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

Retrieval lifecycle interpretation (`PRJ-504..PRJ-507`):

- target steady-state provider baseline is still
  `openai_api_embeddings` when OpenAI credentials are present
- `local_hybrid` remains an explicit transition owner rather than a production
  steady-state target
- deterministic execution remains the explicit compatibility fallback posture,
  not an unowned failure mode
- semantic plus affective sources are treated as the foreground rollout
  completion baseline; relation stays an explicit optional follow-on source
  family after that baseline is stable
- relation retrieval completion is now explicitly frozen as optional rather
  than pending:
  relation records remain live adaptive inputs for context/role/planning, but
  relation embeddings do not define steady-state retrieval completion
- `/health.memory_retrieval` now also exposes explicit relation-source policy
  evidence:
  `retrieval_lifecycle_relation_source_policy_owner`,
  `retrieval_lifecycle_relation_source_state`,
  `retrieval_lifecycle_relation_source_hint`,
  `retrieval_lifecycle_relation_source_recommendation`, and
  `retrieval_lifecycle_relation_source_enabled`
- `retrieval_lifecycle_provider_drift_state` distinguishes whether runtime is
  aligned with the target owner, still on the local transition owner, or still
  on compatibility fallback
- `retrieval_lifecycle_alignment_state` plus
  `retrieval_lifecycle_pending_gaps` summarize whether provider owner, refresh
  owner, and source-rollout posture match the selected steady-state lifecycle
  baseline in one surface

Current limitation:

- OpenAI provider-owned embedding materialization is now live when
  `EMBEDDING_PROVIDER=openai` and `OPENAI_API_KEY` is configured.
- when `EMBEDDING_PROVIDER=openai` is requested without `OPENAI_API_KEY`,
  runtime falls back to deterministic execution with explicit
  `openai_api_key_missing_fallback_deterministic` posture.
- provider-owned lifecycle tuning beyond this baseline remains future follow-up
  work.
- release smoke now consumes the retrieval lifecycle contract directly and
  records policy owner, provider drift posture, alignment state, and pending
  lifecycle gaps in the smoke summary instead of inferring lifecycle truth only
  from embedding provider fields
- the current production retrieval baseline is now expected to stay aligned:
  - `semantic_embedding_provider_requested=openai`
  - `semantic_embedding_provider_effective=openai`
  - `semantic_embedding_model_requested=text-embedding-3-small`
  - `semantic_embedding_model_effective=text-embedding-3-small`
  - `semantic_embedding_execution_class=provider_owned_openai_api`
  - `semantic_embedding_production_baseline_state=aligned_openai_provider_owned`
  - `retrieval_lifecycle_provider_drift_state=aligned_target_provider`
  - `retrieval_lifecycle_alignment_state=aligned_with_defined_lifecycle_baseline`
  - `retrieval_lifecycle_pending_gaps=[]`
- exported `incident_evidence`, incident-evidence bundles, and CI behavior
  validation now consume the same retrieval-alignment posture instead of
  treating retrieval drift as operator-only warning evidence
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
  relation-source optional-family posture, bounded theta influence, and
  selected/planned skill metadata
- `/health.memory_retrieval.retrieval_depth_policy` exposes the same policy
  owner instead of leaving load-depth semantics only inside orchestrator code
- runtime `system_debug.adaptive_state.relation_source_policy` now mirrors the
  `/health.memory_retrieval` owner/state contract for event-scoped behavior
  evidence

### Role and skill boundary

The live runtime now exposes one explicit role/skill maturity baseline:

- role selection remains the behavior owner for the turn
- `app/core/skill_registry.py` selects bounded capability metadata only
- skills remain metadata-only hints and do not execute tools or side effects
- `app/core/role_skill_policy.py` is now the shared owner for that boundary
- `/health.role_skill` plus `system_debug.adaptive_state.role_skill_policy`
  expose the same metadata-only execution boundary
- `work_partner` is now a live backend role under that same owner:
  - it remains a role of the same personality, not a separate persona
  - it carries a bounded skill mix for work organization and decision support
  - it may orchestrate only already approved tools through explicit typed
    intents and the action boundary
- planning may carry selected skills forward, but action still requires
  explicit typed intents and delivery/action contracts for any execution
  posture

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
Health output now also exposes explicit dedicated-admin target posture through
`event_debug_admin_policy_owner`, `event_debug_admin_ingress_target_kind`,
`event_debug_admin_ingress_target_path`, `event_debug_admin_operator_default`,
and `event_debug_admin_posture_state`, plus
`event_debug_shared_ingress_retirement_ready` and
`event_debug_shared_ingress_retirement_blockers` so operators can distinguish
dedicated-admin alignment from remaining shared-compat dependencies.
Runtime policy now also exposes explicit enforcement/removal windows through
`startup_schema_removal_window` and
`event_debug_shared_ingress_enforcement_window`.
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
- behavior validation now also covers metadata-only role/skill boundary
  posture, connector execution posture, proactive cadence posture, and
  deferred reflection enqueue expectations through the shared artifact flow

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
  `app/workers/scheduler.py` for reflection, maintenance, and proactive
  routines
- proactive cadence is now live in the in-process scheduler through
  repository-backed candidate selection, bounded scheduler event emission, and
  normal runtime execution
- scheduler runtime posture and latest tick summaries are visible through
  `GET /health`
- maintenance/proactive cadence dispatch now uses shared owner-aware boundary
  decisions (`in_process_owner_mode|externalized_owner_mode`) and scheduler
  maintenance path explicitly no-ops in externalized posture
- `/health.scheduler.external_owner_policy` now exposes the shared external
  cadence-owner baseline through one machine-visible contract:
  `policy_owner=external_scheduler_cadence_policy`,
  `target_execution_mode=externalized`, canonical
  `maintenance_entrypoint_path=scripts/run_maintenance_tick_once.py`, canonical
  `proactive_entrypoint_path=scripts/run_proactive_tick_once.py`, and explicit
  in-process fallback posture
- this surface now also exposes cutover-proof posture instead of only target
  mode:
  - `maintenance_run_evidence` and `proactive_run_evidence` distinguish
    `missing|stale|recent_success|recent_non_success`
  - `duplicate_protection_posture.state` exposes the bounded single-owner
    boundary between external cadence entrypoints and app-local fallback
  - `cutover_proof_ready` keeps proven cutover distinct from mere target-mode
    selection
- `/health.proactive` now exposes the shared proactive runtime policy owner,
  selected cadence owner, delivery-target baseline, candidate-selection
  baseline, anti-spam thresholds, latest proactive tick summary, and the live
  enabled-versus-disabled production posture
- Coolify production now runs the bounded proactive baseline with:
  - `enabled=true`
  - `production_baseline_ready=true`
  - `production_baseline_state=external_scheduler_target_owner`
  - recent external cadence proof from
    `/health.scheduler.external_owner_policy.proactive_run_evidence`

`PRJ-308` now defines the target cadence-ownership direction:

- long-term production cadence ownership for maintenance/proactive wakeups now
  runs through a dedicated external scheduler owner on Coolify production
- app-local scheduler cadence remains fallback and local-development posture,
  not the active production owner baseline
- the canonical external cadence entrypoints are now frozen for operator and
  release usage: `scripts/run_maintenance_tick_once.py` and
  `scripts/run_proactive_tick_once.py`
- production `/health.scheduler.external_owner_policy` now reports the proven
  externalized baseline through recent repository-backed cadence evidence plus
  bounded duplicate-protection posture
- runtime remains the owner of scheduled-event contract normalization and
  guardrail/conscious execution boundaries regardless of cadence owner

---

## Current Persisted Runtime State

The codebase currently persists these concrete tables:

- `aion_memory`
- `aion_profile`
- `aion_conclusion`
- `aion_semantic_embedding`
- `aion_theta`
- `aion_relation`
- `aion_attention_turn`
- `aion_goal`
- `aion_task`
- `aion_goal_progress`
- `aion_goal_milestone`
- `aion_goal_milestone_history`
- `aion_reflection_task`
- `aion_subconscious_proposal`

These names describe implementation reality, not the canonical abstraction layer.

Migration parity note:

- Alembic head now also creates the full table set above, including
  `aion_attention_turn` and `aion_subconscious_proposal`
- schema-baseline regressions exercise fresh `alembic upgrade head` so
  migration-first bootstrap stays aligned with the live runtime inventory

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

### V1 workflow interpretation

The current no-UI `v1` lane is intentionally narrower than a full
calendar-grade reminder product.

Selected workflow baseline:

- reminder capture and follow-up should run through:
  explicit task capture -> learned proactive preference -> scheduler proactive
  tick -> planning -> expression -> action
- daily planning should run through:
  explicit operational goal/task capture plus same-turn planning help
- task or goal check-ins should run through:
  active work retrieval, task-status updates, proactive `time_checkin` or
  `goal_stagnation` events, and scoped reflection continuity

Current proven bounded examples:

- explicit reminder phrasing such as `Remind me to send the release summary
  tomorrow.` creates an internal active task anchor and persists
  `proactive_opt_in=true` through the normal planning -> action -> conclusions
  path
- explicit daily-support phrasing such as `Help me plan tomorrow.` creates the
  bounded task anchor `plan tomorrow` instead of a separate planning subsystem
- behavior-validation scenario `T13.1` proves the combined path:
  reminder capture -> daily planning capture -> scheduler-owned proactive
  follow-up delivery

Explicit non-goals for this `v1` lane:

- no separate reminder subsystem outside goals/tasks plus proactive cadence
- no free-form due-date scheduling contract yet
- no dedicated reminder UI or admin workflow yet

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
- `scripts/run_reflection_queue_once.py` now provides one explicit
  external-driver entrypoint for draining the durable reflection queue once,
  with `run_reflection_queue_once.ps1` and `.sh` wrappers for operator use

Deployment baseline update (`PRJ-480..PRJ-483`):

- `REFLECTION_RUNTIME_MODE=deferred` is now the explicit target production
  posture for external-driver queue drain
- `in_process` reflection remains compatibility posture for local or
  transitional environments
- release smoke now fails fast when reflection deployment-readiness blockers
  are present in `/health.reflection.deployment_readiness`
- `/health.reflection.external_driver_policy` now exposes the canonical
  external-driver owner, entrypoint path, wrapper paths, and whether the
  current runtime posture is aligned with the deferred external-worker target
- `/health.reflection.supervision` now exposes one shared supervision contract
  owned by `deferred_reflection_supervision_policy`, including:
  - `queue_health_state`
  - `blocking_signals`
  - `recovery_actions`
  - `production_supervision_ready`
  - `production_supervision_state`
  - `production_supervision_hint`
- startup logs and release smoke now consume that same supervision contract, so
  deferred reflection backlog pressure and recovery posture are visible outside
  ad hoc `/health` inspection
- reflection scope governance now treats cross-goal leakage as a shared
  reader/writer contract problem, not only as a worker-local heuristic
- Coolify production now runs this lane on the externalized baseline:
  `/health.reflection.external_driver_policy.selected_runtime_mode=deferred`,
  `/health.reflection.supervision.production_supervision_ready=true`, and the
  app container no longer owns the active reflection queue drain

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
- Coolify production now runs this lane on the durable baseline:
  `/health.attention.coordination_mode=durable_inbox`,
  `/health.attention.contract_store_mode=repository_backed`, and
  `/health.runtime_topology.attention_switch.selected_mode=durable_inbox`
- release and incident proof for this lane now also includes:
  - exported `incident_evidence.policy_posture["attention"]`
  - exported `incident_evidence.policy_posture["runtime_topology.attention_switch"]`
  - release-smoke validation of the same durable-attention fields from live
    `/health`
  - behavior-validation regression for burst coalescing under
    `durable_inbox`
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
- `/health.connectors` now exposes the connector authorization matrix plus the
  capability-proposal boundary so connector rollout stays explicit
- action now fails fast on connector intent mode mismatch before delivery side
  effects and persists connector guardrail posture alongside connector intent
  updates for runtime-visible triage
- `/health.connectors.execution_baseline` now exposes the first live
  provider-backed connector family baseline:
  `task_system.clickup_create_task` and `task_system.clickup_list_tasks`
  become `provider_backed_ready` only when both `CLICKUP_API_TOKEN` and
  `CLICKUP_LIST_ID` are configured
- `ActionExecutor` can now execute the first provider-backed connector action
  path for `ExternalTaskSyncDomainIntent(operation="create_task",
  provider_hint="clickup")` through `app/integrations/task_system/`
  before normal delivery continues
- `ActionExecutor` can now also execute the first provider-backed connector
  read path for `ExternalTaskSyncDomainIntent(operation="list_tasks",
  provider_hint="clickup", mode="read_only")` and returns bounded execution
  notes instead of widening planning/context ownership
- `ActionExecutor` can now also execute the first bounded calendar live-read
  path for `CalendarSchedulingIntentDomainIntent(operation="read_availability",
  provider_hint="google_calendar", mode="read_only")`
- bounded calendar execution remains action-owned and returns only normalized
  window/timezone posture, busy-window count, and top free-slot preview
  instead of raw event titles, attendee lists, or descriptions
- `/health.connectors.execution_baseline` now exposes
  `calendar.google_calendar_read_availability` with machine-visible
  `credentials_missing|provider_backed_ready` posture for that bounded read
  adapter
- `ActionExecutor` can now also execute the first bounded cloud-drive
  metadata-read path for
  `ConnectedDriveAccessDomainIntent(operation="list_files",
  provider_hint="google_drive", mode="read_only")`
- bounded cloud-drive execution remains action-owned and returns only metadata
  previews such as file name, provider id, mime type, and modified-time hints
  instead of document body content, downloads, or write semantics
- `/health.connectors.execution_baseline` now also exposes
  `cloud_drive.google_drive_list_files` with machine-visible
  `credentials_missing|provider_backed_ready` posture for that bounded read
  adapter
- `/health.connectors.web_knowledge_tools` now exposes the shared
  web-knowledge tooling owner, metadata-only skill boundary, fallback posture,
  and the first selected provider-backed execution posture for:
  - `knowledge_search` via `duckduckgo_html`
  - `web_browser` via `generic_http`
- that same surface now includes `website_reading_workflow`, which is the
  bounded no-UI `v1` contract for:
  - direct URL review
  - search-first page review
  - selected provider path
  - bounded read semantics
  - action-owned memory-capture boundary
  - operator-visible blockers and next actions
- `/health.connectors.execution_baseline` now also exposes:
  - `knowledge_search.search_web` as
    `provider_backed_without_credentials/provider_backed_ready`
  - `knowledge_search.suggest_search` as a planning-only suggestion surface
  - `web_browser.read_page` as
    `provider_backed_without_credentials/provider_backed_ready`
  - `web_browser.suggest_page_review` as a planning-only suggestion surface
  - `task_system.clickup_update_task` as the first bounded organization
    mutation slice beyond task creation and task listing
- `/health.connectors.organizer_tool_stack` now exposes one shared operator and
  release-acceptance snapshot for the frozen first production organizer stack:
  approved operations, read-only operations, confirmation-required operations,
  opt-in-required operations, ready operations, credential-gap operations, and
  readiness state
 - the same surface now includes `activation_snapshot`, which is the canonical
   operator onboarding view for the frozen stack:
   - `policy_owner=production_organizer_tool_activation`
   - `provider_activation_state`
   - `provider_activation_ready` versus `provider_activation_total`
   - `provider_requirements` for ClickUp, Google Calendar, and Google Drive
   - provider-specific `missing_settings`
   - provider-specific `next_action`
   - top-level `next_actions`
 - the same surface now includes `daily_use_workflows`,
   `daily_use_ready_workflow_count`, `daily_use_total_workflow_count`,
   `daily_use_ready_workflows`, `daily_use_blocked_workflows`,
   `daily_use_state`, and `daily_use_hint`, so operators and future UI callers
   can see whether the frozen ClickUp, Google Calendar, and Google Drive flows
   are truly ready for day-to-day use rather than only contractually approved
- these live tool slices still remain bounded:
  - search returns result evidence only
  - browser returns page-read evidence only
  - ClickUp updates return status-level mutation evidence only
- all non-selected calendar, task-system, and cloud-drive operations remain
  policy-only by design until broader read-scope boundaries and more provider
  adapters are introduced
- `/health.runtime_topology` now exposes the reflection/attention switch policy
  and fixed graph/proposal baseline, while `/health.planning_governance`
  exposes bounded inferred goal/task growth and fixed proposal decisions
- retrieval now supports a local provider-owned `local_hybrid` embedding path,
  and retrieval depth policy now surfaces explicit production default depth
  alignment
- `/health.identity.adaptive_governance` now exposes the bounded future
  authority model for role horizon, affective rollout, preferences, theta, and
  multilingual/profile posture
- `/health.deployment` now exposes the selected hosting baseline and
  deployment-trigger SLO posture consumed by release smoke
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

## Current Observability Export Reality

The live runtime now has an explicit machine-readable observability export
baseline:

- `app/core/observability_policy.py` owns the minimum incident-evidence
  contract through `incident_evidence_export_policy`
- `GET /health.observability` exposes:
  - the shared policy owner
  - required incident-evidence fields
  - required policy-posture surfaces
  - whether exportable incident evidence is ready
- debug-mode event responses now expose `incident_evidence` with:
  - `trace_id`, `event_id`, `source`
  - `duration_ms`
  - full `stage_timings_ms`
  - policy posture snapshots for:
    - `runtime_policy`
    - `memory_retrieval`
    - `learned_state`
    - `proactive`
    - `attention`
    - `runtime_topology.attention_switch`
    - `scheduler.external_owner_policy`
    - `reflection.supervision`
    - `connectors.execution_baseline`
- release smoke now validates this export directly in debug mode
- behavior-validation artifacts can optionally ingest an exported
  `incident_evidence` JSON file and record its summary in the same gate output
- dedicated debug-ingress retirement evidence is now checked from exported
  incident evidence too:
  - release smoke validates dedicated-admin-only debug posture from live
    `incident_evidence.policy_posture.runtime_policy`
  - bundle verification validates the same posture from
    `incident_evidence.json`
  - behavior-validation CI gates fail on debug-posture drift or missing
    rollback-exception posture
- external cadence cutover evidence is now checked through both release and
  behavior-validation flows:
  - release smoke validates proof owner, per-cadence evidence states, and
    duplicate-protection posture from `/health.scheduler.external_owner_policy`
  - behavior-validation CI gates fail on incomplete
    `incident_evidence.policy_posture["scheduler.external_owner_policy"]`
    explicit rollback-exception state

Current limitation:

- this is an exportable JSON evidence baseline, not yet a full external
  observability stack with dashboards, aggregation, or tracing backend
- the canonical operator bundle shape is now defined as:
  - `manifest.json`
  - `incident_evidence.json`
  - `health_snapshot.json`
  - optional `behavior_validation_report.json`
- current runtime now also provides a canonical bundle helper at
  `scripts/export_incident_evidence_bundle.py`; that helper collects the
  existing runtime-owned surfaces into the frozen bundle shape
- `incident_evidence.json` remains owned by the debug/runtime export contract,
  while `health_snapshot.json` remains owned by `GET /health`
- `/health.conversation_channels.telegram` now exposes one shared Telegram
  conversation-reliability telemetry owner with:
  - `round_trip_ready`
  - `round_trip_state`
  - delivery-adaptation posture:
    - `delivery_adaptation_policy_owner`
    - `delivery_segmentation_state`
    - `delivery_formatting_state`
    - `delivery_message_limit`
    - `delivery_segment_target`
    - `delivery_supported_markdown`
  - token/secret configuration posture
  - ingress counters and last-ingress evidence
  - delivery counters and last-delivery evidence
- Telegram-specific delivery shaping stays below expression:
  - long outbound replies are segmented inside delivery routing according to
    transport-owned limits
  - supported markdown is normalized into Telegram HTML parse mode
  - structurally unsafe markdown falls back to plain text
  - this does not imply the same limits or formatting posture for API or later
    first-party UI channels
- debug-mode `incident_evidence.policy_posture` now also includes
  `conversation_channels.telegram`, so release smoke and behavior-validation
  gates can verify Telegram conversation posture from exported evidence rather
  than only from live `/health`
- debug-mode `incident_evidence.policy_posture["proactive"]` now mirrors the
  same live bounded proactive baseline from `/health.proactive`, so release
  smoke and behavior-validation gates fail when proactive is missing, disabled,
  or drifted from the shared owner contract
- `/health.learned_state` now exposes the shared learned-state inspection
  policy owner, the canonical internal inspection path, and the bounded
  learned-state section contract for `identity_state`, `learned_knowledge`,
  `role_skill_state`, and `planning_state`
- `/health.api_readiness` now exposes the shared backend API-readiness owner
  plus the health, inspection, connector, and current-turn debug surfaces that
  later `v2` UI callers should consume
- `/health.capability_catalog` now exposes the shared backend capability
  catalog owner and one bounded aggregation of:
  - role posture
  - metadata-only skill catalog posture
  - organizer and web-knowledge tool posture
  - learned-state linkage for future UI/admin callers
- `GET /internal/state/inspect?user_id=...` now exposes bounded backend-owned
  snapshots for:
  - `api_readiness`
  - `capability_catalog`
  - `identity_state`
  - `learned_knowledge`
  - `role_skill_state`
  - `planning_state`
  and the richer bounded summary views:
  - `identity_state.preference_summary`
  - `learned_knowledge.knowledge_summary`
  - `learned_knowledge.reflection_growth_summary`
  - `role_skill_state.selection_visibility_summary`
  - `planning_state.continuity_summary`
- debug-mode `incident_evidence.policy_posture["learned_state"]` mirrors that
  health-level owner, path, and section-contract metadata so release smoke and
  behavior-validation gates can verify future-UI inspection readiness from
  exported evidence too
- release smoke and incident-evidence bundle validation now also pin the
  bounded capability-catalog contract from live `/health.capability_catalog`
  and exported `health_snapshot.json`, so future UI/bootstrap work does not
  have to trust an undocumented aggregation shape
- the current bounded interpretation of `personality growth introspection` is:
  - learned preferences and learned knowledge summaries from repository-owned
    profile, runtime preferences, and conclusions
  - role and skill metadata visibility, not executable self-modifying skill
    learning
  - planning continuity through active goals, tasks, milestones, and pending
    proposals
  - reflection-backed growth signals remain summaries owned by memory and
    reflection systems, not a second growth engine
- runtime `system_debug.adaptive_state["web_knowledge_tools"]` now mirrors the
  same selected provider-backed posture as `/health.connectors.web_knowledge_tools`
  for operator triage and future UI bootstrap
- release smoke and incident-evidence bundles now validate the same
  `website_reading_workflow` contract instead of relying only on direct
  `/health` inspection
- behavior validation now proves these live bounded tool slices through:
  - `T14.1` analyst-driven DuckDuckGo search
  - `T14.2` analyst-driven generic HTTP page read
  - `T14.3` executor-aligned ClickUp task update
- behavior validation now also proves backend work-partner orchestration
  through:
  - `T15.1` work-partner organization with bounded search plus ClickUp update
  - `T15.2` work-partner decision support with bounded page-read browsing
- organizer-tool production readiness is now also proven through:
  - `T16.1` work-partner ClickUp task listing
  - `T16.2` work-partner Google Calendar availability reads
  - `T16.3` work-partner Google Drive metadata listing
- release smoke and incident-evidence bundles now validate the same organizer
  daily-use contract instead of relying only on direct `/health` inspection
- `/health.v1_readiness` now mirrors that organizer proof with
  `organizer_daily_use_state`, workflow counts, ready/blocked workflow ids,
  and explicit extension-only fields
- after the core-v1 boundary revision, that organizer posture should be treated
  as mirrored extension readiness rather than as a hidden core no-UI `v1`
  blocker
- `/health.v1_readiness.final_acceptance_gate_states` now stays limited to the
  core no-UI `v1` bundle:
  - conversation reliability
  - learned-state inspection
  - website reading
  - tool-grounded learning
  - time-aware planned work
  - deploy parity
- `/health.v1_readiness.extension_gate_states.organizer_daily_use` keeps the
  organizer daily-use mirror visible without redefining core `v1` closure

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
