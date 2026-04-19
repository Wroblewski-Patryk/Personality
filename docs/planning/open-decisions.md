# Open Decisions

## Why This File Exists

The current repo already works as an MVP slice, but several architecture-level docs describe systems that are not implemented yet. This file keeps the next real decisions visible and tied to the current codebase.

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
  - the full serialized runtime result is exposed through `POST /event?debug=true` and is guarded by explicit config (`EVENT_DEBUG_ENABLED`) with environment-aware defaults (enabled in non-production, disabled in production unless explicitly enabled).
  - when `EVENT_DEBUG_TOKEN` is configured, `POST /event?debug=true` also requires `X-AION-Debug-Token`.
  - `GET /health` now exposes `event_debug_enabled`, `event_debug_token_required`, `event_debug_source`, and `production_policy_enforcement` so operators can verify effective policy, token-gate posture, policy source, and enforcement mode.
  - `/health` also exposes strict-rollout readiness and recommendation signals so operators can detect production-hardening mismatches before a strict-mode rollout and decide when to switch enforcement.
  - startup now emits a production warning when `EVENT_DEBUG_ENABLED=true` so the policy remains visible even before handling requests.
  - startup also warns when production debug payload exposure is enabled without `EVENT_DEBUG_TOKEN`.
  - startup can now hard-fail in production when debug payload exposure is enabled and strict enforcement mode is active.
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
  - the intended architecture still describes `... -> action -> expression -> memory -> reflection`.
  - the current orchestrator computes `expression` before `action`, then passes an explicit `ActionDelivery` handoff into the action layer.
  - action now delegates channel delivery to integration-owned routing (`DeliveryRouter`), so integration dispatch consumes the explicit handoff while side effects still remain action-triggered.
- Decision needed:
  - should runtime keep this expression-before-action implementation detail, or should action consume a lower-level response plan so final expression can move back after action in a stricter architecture-aligned pipeline?

### 3b. Graph Orchestration Adoption

- Current repo fact:
  - architecture docs describe `LangGraph` as the intended orchestration layer,
    but the current runtime still uses a hand-written Python orchestrator.
  - `LangChain` is described as optional support, not the architectural core.
- Decision needed:
  - when should the repo migrate the foreground runtime onto LangGraph?
  - which current stage contracts must stay stable during that migration?
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
  - architecture docs name `pgvector` and semantic retrieval as part of the
    target memory stack, but the current implementation does not yet use vector
    search or embeddings.
- Decision needed:
  - when should hybrid lexical plus vector retrieval become part of the live
    runtime?
  - should vector retrieval start as optional enrichment behind feature flags,
    or become part of the default retrieval path once it exists?

### 5e. Embedding Strategy

- Current repo fact:
  - architecture allows vector or embedding-based retrieval later, but current
    code does not define embedding ownership, refresh rules, or provider scope.
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
  - architecture docs define a relation system with scoped, confidence-bearing
    user-specific knowledge, but the current runtime does not yet persist or
    retrieve relations as a first-class subsystem.
- Decision needed:
  - when should relation storage and retrieval move from architecture intent
    into the live runtime?
  - which behavior layers should relations influence first: context,
    expression, planning, role selection, or proactive behavior?

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
  - reflected `preferred_role`, `theta`, and `collaboration_preference` can be
    learned partly from earlier runtime decisions, which risks feedback loops.
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
  - architecture docs define scheduler-driven events, periodic reflection, and
    proactive behavior, but the live runtime still depends mainly on reactive
    event handling plus post-event reflection enqueue.
  - config docs already reserve fields such as `REFLECTION_INTERVAL` and
    `PROACTIVE_ENABLED`, but those subsystems are not fully implemented yet.
- Decision needed:
  - when should scheduler-originated events become a real production runtime
    path?
  - should proactive behavior start with reminders and check-ins only, or
    include richer warnings, encouragement, and insights from the start?
  - should scheduled reflection stay in-process first, or move directly toward
    dedicated worker execution?

### 12a. Attention Inbox And Turn Assembly

- Current repo fact:
  - the live runtime still processes one normalized event at a time and does
    not yet expose an explicit attention inbox or burst-message coalescing
    layer.
  - planning now includes follow-up slices for attention inbox, proposal
    handoff, and batched conversation handling (`PRJ-085..PRJ-086`,
    `PRJ-092`).
- Decision needed:
  - what should be the canonical ownership of turn assembly, pending-turn
    state, and burst-message coalescing?
  - how long should the runtime wait before treating a rapid message burst as
    one conscious turn instead of many independent replies?

### 12b. Conscious vs Subconscious Coordination Boundary

- Current repo fact:
  - the architecture already states that subconscious processing does not
    communicate directly with the user, but the live runtime does not yet model
    a first-class proposal handoff between subconscious and conscious paths.
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
