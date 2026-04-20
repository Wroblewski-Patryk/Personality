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
- Introduce new feature surface only when it advances one of those convergence
  lanes or removes a documented transitional shortcut.

## Active Decisions

### 1. Reflection Placeholder vs Real Reflection

- Current repo fact:
  - runtime now has a lightweight background reflection worker backed by a durable `aion_reflection_task` queue in Postgres.
  - `RuntimeResult.reflection_triggered` is returned as `True` when reflection was successfully persisted and queued after episode persistence.
  - failed reflection tasks now retry with bounded backoff inside the app process.
  - `GET /health` now exposes a lightweight reflection snapshot with worker state and queue/task counts.
- Decision needed:
  - should this app-local durable worker stay as the MVP baseline, or should reflection move into a separate external worker or scheduler before more complex consolidation is added?

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
- Decision needed:
  - when is it safe to remove the compatibility-only `create_tables()` path entirely and keep strict migration-only startup in every environment?
  - should production default to strict policy enforcement, or keep `warn` as the default while strict mode remains opt-in?

### 3. Public API Shape

- Current repo fact:
  - `POST /event` now returns a smaller public response by default: event identifiers, reply payload, and a compact runtime summary.
  - the full serialized runtime result is exposed through both
    `POST /event/debug` (explicit internal debug path) and
    `POST /event?debug=true` (compatibility path), guarded by explicit config
    (`EVENT_DEBUG_ENABLED`) with environment-aware defaults (enabled in
    non-production, disabled in production unless explicitly enabled).
  - `POST /event?debug=true` now emits explicit compatibility headers
    (`X-AION-Debug-Compat`, `Link`) that point operators to
    `POST /event/debug` as the preferred internal debug route.
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
  - when `EVENT_DEBUG_TOKEN` is configured, `POST /event/debug` also requires
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
- Decision needed:
  - should the full debug payload remain available on the same endpoint through `debug=true`, or should it move to a more clearly internal-only path before wider production use?
  - should production require `EVENT_DEBUG_TOKEN` whenever debug exposure is enabled, or keep token gating optional?
  - should the config default stay open for local-first debugging, or switch to
    disabled-by-default for production-hardening?
  - should production default to strict policy enforcement for this mismatch, or
    keep warning mode as the baseline?

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
  - runtime memory load now consumes hybrid retrieval diagnostics, but provider
    embedding ownership and production retrieval posture are not finalized yet.
- Decision needed:
  - should provider-backed embeddings become default, or stay optional while
    deterministic fallback remains baseline?
  - should vector retrieval start as optional enrichment behind feature flags,
    or become part of the default retrieval path once it exists?

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
  - conclusion-driven semantic/affective embedding shells now persist with
    configured effective model/dimensions plus requested/effective provider
    metadata and explicit `pending_vector_materialization` status.
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
- Decision needed:
  - which embedding provider and refresh strategy should own semantic memory
    vectors?
  - which memory families should be embedded first: episodic, semantic,
    affective, relation, or all of them?

### 5a. Goal And Task Scope

- Current repo fact:
- runtime now loads active goals and active tasks, includes them in the runtime result, refreshes them after Action-layer writes, lets context/motivation/planning react to them, can seed lightweight goals/tasks from explicit user phrases such as `My goal is to ...` and `I need to ...`, can update task status from explicit progress phrases such as `I fixed ...`, and reflection can now derive a lightweight semantic `goal_execution_state` like `blocked`, `recovering`, `advancing`, `progressing`, or `stagnating`, plus a lightweight `goal_progress_score`, `goal_progress_trend`, `goal_progress_arc`, `goal_milestone_state`, `goal_milestone_transition`, `goal_milestone_arc`, `goal_milestone_pressure`, `goal_milestone_dependency_state`, `goal_milestone_due_state`, `goal_milestone_due_window`, `goal_milestone_risk`, and `goal_completion_criteria`; it also persists a short goal-level progress history in `aion_goal_progress`, syncs lightweight `aion_goal_milestone` objects for the active goal focus, persists short `aion_goal_milestone_history` snapshots, and runtime enriches those milestone objects with the current operational arc/pressure/dependency/due/due-window/risk/completion signals without introducing a heavier milestone schema yet.
- Decision needed:
  - should goal and task creation stay limited to explicit user declarations for MVP, or should the system begin inferring and creating them from plans and repeated execution patterns?

### 6. Deployment Path After Coolify

- Current repo fact:
  - docs and compose files already support local Docker and Coolify.
- Decision needed:
  - is Coolify the intended production baseline, or only a temporary path until a different hosting standard is chosen?

### 7. Deployment Trigger Reliability

- Current repo fact:
  - after pushing `main`, production required a manual redeploy from Coolify before the latest commit became live.
  - a manually sent, correctly signed GitHub-style webhook request to the configured Coolify endpoint successfully queued a deployment on 2026-04-15.
  - the repo now has a repeatable release smoke helper for `GET /health` plus `POST /event`, so manual verification no longer depends on hand-written curl snippets.
- Decision needed:
  - should deploys rely on GitHub webhooks, polling, or an explicit manual release step until automation is trustworthy?
  - until GitHub-side webhook delivery is verified, should manual redeploy remain the explicit release fallback?

### 8. Language Handling Strategy

- Current repo fact:
  - runtime now makes an explicit per-event language decision, propagates it through perception and expression, stores response-language hints in episodic memory for short follow-up turns, and keeps a lightweight `aion_profile` preferred language for ambiguous turns when recent memory is not enough.
  - API callers can now provide `X-AION-User-Id` as a fallback identity key when `meta.user_id` is omitted, reducing accidental language/profile bleed caused by shared `anonymous` API traffic.
- Decision needed:
  - should language handling stay heuristic-plus-profile for the MVP, or should it move to a richer user preference model and broader multilingual support once more channels are added?

### 9. Lightweight Profile Scope

- Current repo fact:
  - runtime now persists a lightweight language preference in `aion_profile`, keeps semantic preferences in `aion_conclusion`, and builds a lightweight runtime `IdentitySnapshot` from that state plus theta.
- Decision needed:
  - should `aion_profile` remain limited to durable interaction preferences such as language, while `aion_conclusion` carries generalized learned preferences, or should those concerns merge into one wider identity-linked profile later?

### 9a. Relation System Rollout

- Current repo fact:
  - runtime now persists scoped relation records (`aion_relation`) with
    confidence/source/evidence fields and reflection-driven updates.
  - runtime now loads high-confidence relations and applies relation cues in
    context, role, planning, and expression paths.
- Decision needed:
  - which additional behavior layers should relations influence next (for
    example proactive delivery, interruption cost, and attention gating)?
  - what decay/revalidation policy should govern stale relation records?

### 10. Preference Influence Scope

- Current repo fact:
- stable `response_style` conclusions now influence context, planning, and expression.
- stable `preferred_role` conclusions can now influence role selection on ambiguous turns.
- stable `collaboration_preference` conclusions can now influence context, role selection, motivation, planning, and expression on ambiguous turns, and explicit user phrases like `step by step` or `do it for me` are now captured as episodic collaboration markers for reflection.
- reflected theta now provides a softer runtime bias toward support, analysis, or execution behavior without hard-overriding explicit signals, and that bias can now shape role selection, motivation mode, planning stance, and expression tone on ambiguous turns.
- Decision needed:
  - which preference types should remain expression-only, and which should be allowed to shape higher-level planning or role selection as the architecture grows?

### 10a. Action Intent Ownership

- Current repo fact:
  - planning now emits explicit typed `domain_intents` for goal/task/task-status
    and preference updates, plus `noop` when no domain write should occur.
  - action now executes only explicit intents and no longer reparses raw user
    text for durable domain writes.
- Decision needed:
  - should additional future writes (for example relation updates or proactive
    scheduling state) also be blocked behind explicit typed intents from
    planning?

### 10b. Adaptive Signal Governance

- Current repo fact:
  - reflection now requires outcome evidence and user-visible cues for
    adaptive updates (`preferred_role`, `theta`, collaboration fallback) to
    reduce feedback loops from role-only traces.
- Decision needed:
  - what evidence threshold should be required before adaptive signals can
    influence future role, motivation, planning, or expression?
  - which adaptive signals are valuable enough to keep as first-class runtime
    inputs, and which should remain descriptive-only until stronger evidence is
    available?

### 11. Theta Scope And Durability

- Current repo fact:
  - reflection now updates a lightweight `aion_theta` state from repeated recent role patterns, and runtime can use that state as a soft bias for role selection, motivation, planning, and expression on ambiguous turns.
- Decision needed:
  - should theta stay as a lightweight behavioral bias derived from recent runtime patterns, or evolve into a broader long-term identity state with stronger influence over planning, motivation, expression, and proactive behavior?

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
- Decision needed:
  - should reflection/maintenance scheduler cadence remain app-local, or move
    to a dedicated external scheduler/worker path?
  - should proactive guardrails remain plan-local and event-context driven, or
    move toward a dedicated attention-inbox gate shared with burst handling?
  - should scheduled reflection stay in-process first, or move directly toward
    dedicated worker execution?

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
- Decision needed:
  - what should be the canonical ownership of turn assembly, pending-turn
    state, and burst-message coalescing?
  - how long should the runtime wait before treating a rapid message burst as
    one conscious turn instead of many independent replies?

### 12b. Conscious vs Subconscious Coordination Boundary

- Current repo fact:
  - the architecture already states that subconscious processing does not
    communicate directly with the user, and runtime contracts now model a
    first-class proposal handoff surface between subconscious and conscious
    paths.
  - proposal persistence/promotion behavior is still not implemented end to end
    in live runtime execution.
  - planning now includes explicit proposal persistence, conscious promotion
    rules, read-only subconscious tool policy, and separate wakeup/cadence
    slices (`PRJ-088..PRJ-091`).
- Decision needed:
  - which subconscious outputs should become durable proposals rather than
    immediate behavior?
  - which proposal types should conscious runtime be allowed to merge, defer,
    discard, or escalate into user-visible action?
  - should subconscious research stay read-only forever, or ever gain more
    than retrieval-only authority?

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
