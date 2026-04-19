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
- runtime materializes an `ActionDelivery` object after expression
- `ActionExecutor` consumes that delivery object
- `DeliveryRouter` owns the channel-specific dispatch behavior

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
- when LLM classification is unavailable or invalid, the stage falls back to
  deterministic baseline signals and marks source as `fallback`
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

Current limitation:

- deterministic fallback embeddings are live; provider-owned embedding lifecycle
  and tuning are still planned follow-up work.

### Event API behavior

`POST /event` currently returns:

- a compact public response by default
- an optional debug payload when `debug=true`, debug exposure is enabled by
  policy, and compatibility query route is enabled
- explicit internal debug route `POST /event/debug` remains available when
  debug exposure is enabled
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
- scheduler cadence posture and latest tick summaries
- attention turn-assembly posture (`burst_window_ms`, turn TTLs, pending /
  claimed / answered counters)

Production debug access now also supports explicit token-requirement policy via
`PRODUCTION_DEBUG_TOKEN_REQUIRED` (default `true`).
Compatibility `POST /event?debug=true` route now supports explicit
environment-aware policy via `EVENT_DEBUG_QUERY_COMPAT_ENABLED`
(default `true` outside production, `false` in production).
Runtime policy health output now also includes `debug_access_posture` and
`debug_token_policy_hint` plus compat-route posture markers
(`event_debug_query_compat_enabled`, `event_debug_query_compat_source`) and
compat-route usage telemetry (`event_debug_query_compat_telemetry`) for
operator-visible debug access hardening posture.
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

Current limitation:

- proactive and scheduler-aware relation usage is still not implemented.

---

## Scheduler Contract Reality

Scheduler-facing runtime contracts are now explicit:

- scheduler events are normalized through dedicated contract helpers
- source/subsource and payload shape checks are centralized in
  `app/core/scheduler_contracts.py`
- runtime config includes scheduler and cadence boundaries:
  `SCHEDULER_ENABLED`, `REFLECTION_INTERVAL`, `MAINTENANCE_INTERVAL`,
  `PROACTIVE_ENABLED`, `PROACTIVE_INTERVAL`
- in-process scheduler cadence is now implemented through
  `app/workers/scheduler.py` for reflection and maintenance routines
- proactive ticks now have a live decision and delivery-guard path when a
  scheduler proactive event is received
- scheduler runtime posture and latest tick summaries are visible through
  `GET /health`

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
- update task status from explicit progress signals
- refresh returned goal and task state after action-layer writes

Current intent-ownership boundary:

- planning emits explicit `domain_intents` (goal/task/task-status plus
  preference intents, or `noop`)
- action executes those typed intents and no longer reparses raw user text for
  durable domain writes

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
- failed tasks can be retried with bounded backoff
- queue visibility is exposed through health reporting
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

This is more advanced than a purely conceptual background loop, but still lighter than the long-term architecture could become.

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
- `POST /event` applies Telegram burst coalescing through one in-memory
  attention-turn coordinator; rapid pending messages can assemble into one turn
  and duplicate/non-owner burst events return queued metadata instead of
  triggering duplicate runtime runs
- attention turn timing is now runtime-configurable through
  `ATTENTION_BURST_WINDOW_MS`, `ATTENTION_ANSWERED_TTL_SECONDS`, and
  `ATTENTION_STALE_TURN_SECONDS`
- reflection now derives and persists subconscious proposals with explicit
  proposal lifecycle state (`pending|accepted|deferred|discarded`)
- conscious planning/runtime now records proposal handoff decisions and resolves
  persisted proposals only after conscious acceptance/defer/discard decisions
- subconscious research proposals now carry explicit read-only policy/tool
  bounds (`research_policy`, `allowed_tools`)
- proactive scheduler events now pass through an explicit attention gate
  (quiet-hours, cooldown, unanswered-backlog) before delivery planning
- planning/action contracts now include connector permission-gate outputs plus
  typed calendar/task/drive connector intents without direct provider side
  effects

Important non-live notes:

- subconscious runtime is still not allowed to communicate with the user
  directly
- conscious runtime remains the only owner of user-visible delivery and other
  external side effects

This coordination model baseline is now implemented through `PRJ-092`.

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
