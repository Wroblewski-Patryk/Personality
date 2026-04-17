# Runtime Flow

## Purpose

This document describes the runtime flow that is implemented today and highlights where the broader architecture is still ahead of the code.

## Core Principle

AION stays event-driven and stateful.

Every foreground cycle starts from an event plus stored state, produces a structured result, persists an episode, and can enqueue reflection work for later consolidation.

## Implemented Foreground Flow

The current orchestrator runs this sequence:

`event -> state load -> identity -> perception -> context -> motivation -> role -> planning -> expression -> action -> memory -> reflection enqueue`

The intended architecture still treats the action boundary as:

`event -> perception -> context -> motivation -> role -> planning -> action -> expression -> memory -> reflection`

Current implementation note:

- `expression` is currently produced just before `action`
- `action` remains the only stage that performs side effects
- this ordering exists so outbound integrations can reuse the already prepared channel-specific message

## Step-by-Step Foreground Runtime

### 1. Event normalization

Incoming API or Telegram payloads are converted into the canonical `Event` structure with:

- `event_id`
- `source`
- `subsource`
- `timestamp`
- `payload`
- `meta.user_id`
- `meta.trace_id`

### 2. State load

Before reasoning starts, runtime loads lightweight user-linked state:

- recent episodic memory
- user profile
- runtime preferences and semantic conclusions
- theta
- active goals
- active tasks
- active goal milestones
- recent goal milestone history
- recent goal progress history

### 3. Identity build

`IdentityService` builds a lightweight `IdentitySnapshot` from:

- stable product-level mission and values
- durable profile state
- semantic conclusions
- theta orientation

### 4. Perception

Perception classifies the event and emits:

- `event_type`
- `topic`
- `topic_tags`
- `intent`
- `language`
- `language_source`
- `language_confidence`
- `ambiguity`
- `initial_salience`

### 5. Context

Context combines the current event with:

- recent episodic memory
- stable semantic conclusions
- identity
- active goals and tasks
- milestone state and recent histories

The output is a compressed situational summary plus related tags and goals.

### 6. Motivation

Motivation scores:

- importance
- urgency
- valence
- arousal
- response mode

It can react to active goals, blocked work, milestone pressure, due state, due window, and goal-progress signals.

### 7. Role

Role selection is lightweight but real. It can use:

- event and context heuristics
- semantic user preferences
- collaboration preference
- reflected theta bias

### 8. Planning

Planning turns the current turn into:

- a response goal
- ordered plan steps
- `needs_action`
- `needs_response`

It is goal-aware and milestone-aware, but still heuristic rather than model-driven.

### 9. Expression

Expression prepares the user-visible reply:

- message
- tone
- channel
- language

It can use identity, role, motivation, preferences, and theta, and can optionally call OpenAI.

### 10. Action

Only the action layer performs side effects. Today that includes:

- Telegram send when applicable
- persistence of episodic memory and lightweight runtime state changes
- explicit goal/task updates triggered by user phrases

### 11. Memory and state refresh

After action execution, runtime persists the episode and refreshes returned goal/task/milestone state so the `/event` response reflects post-write state instead of only pre-write state.

### 12. Reflection enqueue

When episode persistence succeeds, runtime tries to persist and queue a reflection task.

`reflection_triggered=true` means the task was durably written and accepted by the in-app worker queue.

## Implemented Background Flow

Background reflection is now a real subsystem inside the app process.

### 1. Durable task persistence

Reflection work is first stored in `aion_reflection_task`.

### 2. Worker pickup and retry

The worker:

- claims pending or retryable tasks
- retries failed tasks with bounded backoff
- reports queue state through `GET /health`

### 3. Reflection scope load

Reflection loads recent memory and runtime state around the user, including:

- episodic summaries
- conclusions
- theta
- active goals and tasks
- goal progress history
- goal milestone history

### 4. Consolidation

Reflection updates lightweight semantic state such as:

- response style
- collaboration preference
- preferred role
- theta orientation
- goal execution state
- goal progress score, trend, and arc
- milestone state, transition, arc, pressure, dependency, due, due window, risk, and completion criteria

### 5. Persistence

Reflection writes back updated conclusions, theta, progress snapshots, milestone objects, and milestone history.

## Runtime Observability

The runtime is intentionally debuggable.

`POST /event` currently returns:

- the full `RuntimeResult`
- `reflection_triggered`
- `stage_timings_ms`
- `duration_ms`

`GET /health` currently returns:

- app health status
- reflection worker running status
- durable queue counts such as pending, processing, failed, retryable, exhausted, and stuck

## Runtime Invariants

The current implementation still aims to preserve these rules:

1. Every input becomes a normalized event before deeper reasoning.
2. Only the action layer performs side effects.
3. Every completed foreground cycle attempts episodic memory persistence.
4. Reflection never blocks the foreground reply path.
5. Identity remains more stable than theta.
6. Background reflection updates future behavior through stored state, not hidden in-memory mutation only.

## Still Planned

The following are still architectural targets rather than implemented runtime facts:

- formal migrations
- vector retrieval
- LangGraph or other external orchestration
- a separate reflection worker service
- richer relation systems and proactive loops
