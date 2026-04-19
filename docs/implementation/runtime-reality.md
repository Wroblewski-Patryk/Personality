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

## Current Runtime Contracts

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

### Event API behavior

`POST /event` currently returns:

- a compact public response by default
- an optional debug payload when `debug=true` and debug exposure is enabled by policy
- when API payload metadata omits `meta.user_id`, runtime can use
  `X-AION-User-Id` as a fallback identity key before defaulting to `anonymous`

### Health behavior

`GET /health` currently exposes:

- app status
- reflection worker queue snapshot
- non-secret runtime policy flags

---

## Current Persisted Runtime State

The codebase currently persists these concrete tables:

- `aion_memory`
- `aion_profile`
- `aion_conclusion`
- `aion_theta`
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

This is more advanced than a purely conceptual background loop, but still lighter than the long-term architecture could become.

---

## Planned Coordination Direction (Not Yet Live)

The current repository does not yet implement the next coordination layer that
recent planning now describes.

The intended supplemental direction is:

- one explicit attention inbox for user turns, scheduler wakeups, and
  subconscious proposals
- turn assembly for bursty chat traffic so multiple rapid user messages can be
  answered as one conscious turn instead of one reply per raw message
- subconscious-to-conscious proposal handoff instead of direct subconscious
  messaging
- explicit attention gating before proactive delivery
- conscious wakeups and subconscious cadence treated as separate runtime
  concerns

Important non-live notes:

- subconscious runtime is still not allowed to communicate with the user
  directly
- subconscious runtime may eventually use read-only research or retrieval tools
  without gaining direct side-effect authority
- conscious runtime remains the only owner of user-visible delivery and other
  external side effects

This coordination model is planned through `PRJ-085..PRJ-092`.

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

This boundary is planned through `PRJ-087` and `PRJ-093..PRJ-097`.

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
