# Agent Contracts

## Purpose

This document defines the canonical contracts between AION stages.

It exists to keep:

- stage boundaries explicit
- data flow predictable
- implementation aligned with architecture

These contracts describe cognitive responsibilities.
Transport- or endpoint-specific envelopes belong outside `docs/architecture/`.

---

## Core Principle

Every stage must:

- receive structured input
- return structured output
- own one responsibility
- avoid hidden side effects

No stage should absorb the responsibilities of another stage.

---

## Shared Runtime State

Stages receive only the subset of state they need.

Canonical shared runtime state may include:

```json
{
  "event": {},
  "identity": {},
  "memory": {},
  "conclusions": [],
  "theta": {},
  "affective": {},
  "goals": [],
  "tasks": [],
  "perception": {},
  "context": {},
  "motivation": {},
  "role": {},
  "plan": {},
  "expression": {},
  "action_result": {}
}
```

---

## Perception Agent

### Purpose

Identify what happened.

### Input

```json
{
  "event": {}
}
```

### Output

```json
{
  "perception": {
    "event_type": "...",
    "topic": "...",
    "intent": "...",
    "language": "en",
    "ambiguity": 0.0,
    "initial_salience": 0.0,
    "affective": {
      "affect_label": "neutral|support_distress|urgent_pressure|positive_engagement",
      "intensity": 0.0,
      "needs_support": false,
      "confidence": 0.0,
      "source": "deterministic_placeholder|ai_classifier|fallback",
      "evidence": []
    }
  }
}
```

---

## Context Agent

### Purpose

Build situational understanding for the current turn.

### Input

```json
{
  "event": {},
  "perception": {},
  "memory": {},
  "conclusions": [],
  "goals": [],
  "tasks": [],
  "identity": {},
  "theta": {}
}
```

### Output

```json
{
  "context": {
    "summary": "...",
    "related_goals": [],
    "related_tags": [],
    "risk_level": 0.0
  }
}
```

---

## Motivation Agent

### Purpose

Determine how strongly the system should care.

### Input

```json
{
  "event": {},
  "context": {},
  "goals": [],
  "tasks": [],
  "theta": {},
  "identity": {}
}
```

### Output

```json
{
  "motivation": {
    "importance": 0.0,
    "urgency": 0.0,
    "valence": 0.0,
    "arousal": 0.0,
    "mode": "respond|ignore|analyze|execute|clarify"
  }
}
```

---

## Role Selection Agent

### Purpose

Select the behavioral stance for the turn.

### Input

```json
{
  "event": {},
  "context": {},
  "motivation": {},
  "identity": {},
  "theta": {}
}
```

### Output

```json
{
  "role": {
    "selected": "advisor|analyst|mentor|executor|friend",
    "confidence": 0.0
  }
}
```

---

## Planning Agent

### Purpose

Decide what should happen next.

### Input

```json
{
  "context": {},
  "motivation": {},
  "role": {},
  "goals": [],
  "tasks": [],
  "theta": {}
}
```

### Output

```json
{
  "plan": {
    "goal": "...",
    "steps": [],
    "needs_action": true,
    "needs_response": true
  }
}
```

---

## Expression Agent

### Purpose

Form the outward communication of the turn.

### Input

```json
{
  "event": {},
  "context": {},
  "motivation": {},
  "role": {},
  "plan": {},
  "identity": {},
  "theta": {}
}
```

### Output

```json
{
  "expression": {
    "message": "...",
    "tone": "...",
    "channel": "api|telegram",
    "language": "en"
  }
}
```

---

## Action Layer Contract

### Purpose

Execute the required side effects.

### Input

```json
{
  "event": {},
  "plan": {},
  "expression": {}
}
```

### Output

```json
{
  "action_result": {
    "status": "success|partial|fail|noop",
    "actions": [],
    "notes": "..."
  }
}
```

---

## Memory Write Contract

### Purpose

Persist the finished episode after the turn.

### Input

```json
{
  "event": {},
  "context": {},
  "role": {},
  "motivation": {},
  "plan": {},
  "expression": {},
  "action_result": {}
}
```

### Output

```json
{
  "memory_record": {
    "summary": "...",
    "importance": 0.0
  }
}
```

---

## Reflection Agent

### Purpose

Analyze patterns across memory and update slower-moving state.

### Input

```json
{
  "recent_memory": [],
  "existing_conclusions": [],
  "theta": {},
  "goals": [],
  "tasks": []
}
```

### Output

```json
{
  "reflection": {
    "new_conclusions": [],
    "updated_conclusions": [],
    "theta_update": {},
    "relation_update": {},
    "progress_update": {}
  }
}
```

---

## Contract Rules

1. every stage returns only its own output field
2. no stage returns the full system state as its main output
3. no stage except Action performs side effects
4. expression shapes communication before action executes it
5. reflection updates future state asynchronously

---

## Validation

Each contract should be:

- schema-valid
- minimal
- explicit
- testable

---

## Common Mistakes

- mixing cognition with side effects
- returning too much state from one stage
- letting action decide message content
- letting expression mutate durable state
- letting reflection silently rewrite identity

---

## Final Principle

Contracts are what keep AION coherent while the implementation evolves.

If contracts are clear:

- the runtime is predictable
- testing is straightforward
- refactors stay safe

If contracts are unclear, architectural drift becomes invisible.
