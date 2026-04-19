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

- perception populates this slot with deterministic placeholder signals
- motivation, role, and expression still rely on existing heuristics for
  behavior decisions until the follow-up slices wire this slot through

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
