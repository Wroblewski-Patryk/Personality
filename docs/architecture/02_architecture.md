# Architecture

## Purpose

This document defines the canonical AION architecture.

It describes the intended cognitive model of the system:

- how AION receives a stimulus
- how it forms understanding
- how it prepares expression
- how it performs action
- how it learns over time

Temporary implementation details belong outside `docs/architecture/`.

---

## Core Model

AION is a stateful event-driven cognitive runtime.

It does not start from zero on each turn.
Every new event is processed through existing identity, memory, and adaptive state.

The canonical loop is:

`state -> event -> interpretation -> expression -> action -> memory -> reflection -> updated state`

---

## Main Components

1. Identity
2. Memory System
3. Conscious Loop
4. Subconscious Loop
5. Motivation Engine
6. Role and Skill Layer
7. Planning Layer
8. Expression Layer
9. Action Layer
10. Infrastructure

---

## Execution Model

AION operates through two cooperating loops.

The conscious loop handles real-time turns:

- receives an event
- interprets it
- selects a role
- prepares a response or action
- executes the required side effects
- writes memory

The subconscious loop handles delayed cognition:

- analyzes stored episodes
- detects recurring patterns
- updates conclusions
- adjusts theta and relation state
- reevaluates time-aware planned work during scheduler-owned cadence windows

---

## Unified Cognitive Pipeline

The canonical foreground pipeline is:

`event -> perception -> context -> motivation -> role -> planning -> expression -> action -> memory -> reflection`

Each stage has one responsibility:

- perception identifies what happened
- context explains what it means now
- motivation scores importance and urgency
- role selects behavioral stance
- planning decides what should happen next
- expression shapes outward communication
- action executes side effects
- memory stores the episode
- reflection improves future behavior

---

## Stage Responsibilities

### Perception

Recognize the event.

Questions answered:

- what happened?
- what kind of event is this?
- what is the likely intent?

### Context

Build situational understanding.

Questions answered:

- what does this event mean?
- what background matters now?
- what memories or goals are relevant?

### Motivation

Determine how strongly the system should care.

Questions answered:

- how important is this?
- how urgent is this?
- should AION respond, clarify, analyze, execute, or ignore?

### Role

Select the behavioral mode for this turn.

Questions answered:

- what stance best fits the situation?
- how should identity be expressed here?

Role selection may read from a durable role registry that stores approved
role presets, prompt variants, and runtime selection hints.
Those role records shape expression and planning posture, but they do not
replace runtime ownership of role selection.

### Skill

Select reusable capability guidance for the turn.

Questions answered:

- which capabilities fit this situation?
- which stored skill descriptions or usage notes should guide planning?
- which approved tool families may be considered?

Skills may evolve as durable descriptions over time, but they remain guidance
for planning rather than direct execution authority.

### Planning

Turn understanding into intended next steps.

Questions answered:

- what should happen next?
- what needs response?
- what needs action?
- what future work should be scheduled, updated, or cancelled?

### Expression

Form the outward message or communicative structure.

Questions answered:

- what should be said?
- in what tone?
- in what structure or language?

### Action

Perform side effects in the system or outside world.

Questions answered:

- what must be written, sent, updated, or triggered?
- did execution succeed?

Approved external reads may inform later cognition only when Action reduces
their results into bounded summaries for Memory.

Raw provider payloads must not become a second memory-ingestion path outside
the existing action -> memory boundary.

### Memory

Store the finished episode for future retrieval and learning.

### Reflection

Analyze patterns across episodes and update future behavior.

---

## Time-Aware Planned Work

AION should not treat reminders as a standalone subsystem.

Instead, future-facing behavior belongs to one shared planned-work model that
extends existing planning, goals, tasks, proactive cadence, and scheduler
ownership.

Examples of planned work:

- one-time follow-up
- morning check-in
- recurring routine
- delayed research pass
- time-bound action window

The core rule is:

- "reminder" is only one possible outward expression of planned work
- planned work stays internal until runtime decides it is due or newly relevant
- user-visible delivery still goes through the normal foreground pipeline
- externally planned contact, care, or outreach is planned work or a
  subconscious proposal; it is not an always-on duty embedded in scheduler code

This keeps AION closer to human-like time reasoning:

- context plus current time shape what should happen now
- the system may defer, advance, skip, or deliver a planned action
- the scheduler only wakes reevaluation; it does not become a second planner
- a lightweight due-work observer may check whether any planned action is due
  before a full conscious foreground run is started

---

## Trigger Model

The architecture keeps one explicit split between triggers for conscious
foreground processing and triggers for subconscious or background processing.

Conscious foreground triggers:

- direct user events from Telegram or API
- due planned-work items that cross the attention boundary
- accepted subconscious proposals that require user-visible handling
- explicit admin or system requests that enter the foreground event contract

Subconscious or background triggers:

- reflection enqueue after completed turns
- scheduler or cron cadence ticks
- maintenance windows
- passive proactive or relationship reevaluation windows
- planned-work reevaluation windows

Background processing may decide that something is due.
It must not bypass the action boundary.

If a due item should reach the user, background ownership may only:

- emit an attention item
- create a bounded proposal
- update durable planned-work state

Foreground runtime remains the owner of any later user-visible response.

Scheduler cadence must not wake the conscious loop merely because time passed.
It may first run a cheap observer over planned work, proposal state, and
relation-backed external planning signals. If nothing is due, actionable, or
newly relevant, no foreground event should be emitted.

This distinction applies only to external future-facing planning. Once a real
foreground stimulus has been admitted, the internal execution loop still
completes the current path through planning, expression, action, memory, and
reflection evidence.

---

## Event Contract

All inputs must be normalized into a shared event shape before deeper cognition.

Minimum canonical structure:

```json
{
  "event_id": "uuid",
  "source": "telegram|api|system|scheduler",
  "subsource": "...",
  "timestamp": "ISO-8601",
  "payload": {},
  "meta": {
    "user_id": "...",
    "trace_id": "..."
  }
}
```

---

## Runtime Node Contract

Each processing node must:

- receive structured input
- return structured output
- avoid hidden side effects
- avoid doing another stage's work

Canonical shared runtime state can include:

```json
{
  "event": {},
  "identity": {},
  "memory": {},
  "theta": {},
  "perception": {},
  "context": {},
  "motivation": {},
  "role": {},
  "skills": [],
  "plan": {},
  "expression": {},
  "action_result": {}
}
```

Not every stage uses every field.

---

## Action Boundary

The action boundary is a non-negotiable architectural rule.

Only the Action layer may:

- write to persistent storage
- call external APIs
- send outbound messages
- modify system state outside the local reasoning object
- trigger external or background execution

This remains true even when roles or skills reference prompts, heuristics,
tool families, or user-authorized providers.

Reasoning stages may prepare intent, but they may not perform side effects.

---

## Expression Layer

Expression is distinct from action.

Expression decides:

- wording
- tone
- structure
- channel adaptation

Action decides:

- what is executed
- where it is delivered
- what is persisted or triggered

This mirrors the intended human-like flow from stimulus to expression and then to action.

---

## Observability

Architecture must remain inspectable.

Core observability expectations:

- event and trace identifiers
- per-stage timing
- structured stage outcomes
- failure visibility
- runtime policy visibility

Future UI or admin surfaces should consume one backend capability catalog that
is composed from existing health and internal-inspection truth.

That catalog must summarize role posture, metadata-only skills, approved tool
families, and provider readiness without creating a parallel execution or
authorization system outside planning and action.

Without observability, architecture degrades into guesswork.

---

## Deployment Model

The long-term deployment shape remains:

- FastAPI as API boundary
- PostgreSQL as durable state
- background reflection execution
- containerized deployment

Supporting technologies may evolve, but the cognitive architecture should remain stable.

---

## Architectural Principles

- keep stage responsibilities explicit
- keep side effects controlled
- preserve identity continuity
- let memory influence future behavior
- keep reflection asynchronous to foreground interaction
- prefer small, inspectable runtime contracts

---

## Final Principle

Architecture is the system's cognitive spine.

If the architectural order is clear:

- implementation can evolve safely
- debugging stays possible
- future capability can grow without chaos

If the architectural order drifts, the system stops being coherent.
