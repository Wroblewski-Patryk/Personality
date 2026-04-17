# Agent Contracts

## Purpose

This document captures the structured contracts used by the current AION runtime modules.

It focuses on the contracts that are implemented today, not the larger future agent society described elsewhere in the architecture docs.

## Shared Runtime State

The foreground runtime currently passes structured state between stages. Depending on the stage, inputs can include:

```json
{
  "event": {},
  "identity": {},
  "recent_memory": [],
  "user_profile": {},
  "user_preferences": {},
  "user_conclusions": [],
  "theta": {},
  "active_goals": [],
  "active_tasks": [],
  "active_goal_milestones": [],
  "goal_milestone_history": [],
  "goal_progress_history": [],
  "perception": {},
  "context": {},
  "motivation": {},
  "role": {},
  "plan": {}
}
```

Not every stage receives every field.

## Perception Agent

### Purpose

Interpret the raw normalized event.

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
    "topic_tags": [],
    "intent": "...",
    "language": "en",
    "language_source": "explicit_request|message_heuristic|recent_memory|profile",
    "language_confidence": 0.0,
    "ambiguity": 0.0,
    "initial_salience": 0.0
  }
}
```

## Context Agent

### Purpose

Compress the current situation into a usable runtime summary.

### Input

```json
{
  "event": {},
  "perception": {},
  "recent_memory": [],
  "conclusions": [],
  "identity": {},
  "active_goals": [],
  "active_tasks": [],
  "active_goal_milestones": [],
  "goal_milestone_history": [],
  "goal_progress_history": []
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

## Motivation Engine

### Purpose

Score how much the system should care and how urgently it should respond.

### Input

```json
{
  "event": {},
  "perception": {},
  "context": {},
  "user_preferences": {},
  "theta": {},
  "active_goals": [],
  "active_tasks": [],
  "goal_milestone_history": [],
  "goal_progress_history": []
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

## Role Agent

### Purpose

Choose the current behavioral stance.

### Input

```json
{
  "event": {},
  "perception": {},
  "context": {},
  "user_preferences": {},
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

## Planning Agent

### Purpose

Turn the current turn into a response or action plan.

### Input

```json
{
  "event": {},
  "context": {},
  "motivation": {},
  "role": {},
  "user_preferences": {},
  "theta": {},
  "active_goals": [],
  "active_tasks": [],
  "active_goal_milestones": [],
  "goal_milestone_history": [],
  "goal_progress_history": []
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

## Expression Agent

### Purpose

Prepare the user-visible reply before the action layer delivers it.

### Input

```json
{
  "event": {},
  "perception": {},
  "context": {},
  "plan": {},
  "role": {},
  "motivation": {},
  "identity": {},
  "user_preferences": {},
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

## Action Layer

### Purpose

Perform side effects and runtime persistence only after planning has been decided.

### Input

```json
{
  "plan": {},
  "event": {},
  "expression": {}
}
```

### Output

```json
{
  "action_result": {
    "status": "success|fail|noop",
    "actions": [],
    "notes": "..."
  }
}
```

## Memory Persistence Contract

### Purpose

Persist the completed episode and lightweight explicit user-state updates.

### Input

```json
{
  "event": {},
  "perception": {},
  "context": {},
  "motivation": {},
  "role": {},
  "plan": {},
  "action_result": {},
  "expression": {}
}
```

### Output

```json
{
  "memory_record": {
    "id": 0,
    "event_id": "...",
    "timestamp": "ISO-8601",
    "summary": "...",
    "importance": 0.0
  }
}
```

## Reflection Worker

### Purpose

Consolidate lightweight semantic state asynchronously after foreground completion.

### Durable trigger input

```json
{
  "user_id": "...",
  "event_id": "..."
}
```

### Reflection scope inputs

```json
{
  "recent_memory": [],
  "existing_conclusions": [],
  "theta": {},
  "active_goals": [],
  "active_tasks": [],
  "goal_progress_history": [],
  "goal_milestone_history": []
}
```

### Effective outputs

Reflection currently persists lightweight updates such as:

- semantic conclusions in `aion_conclusion`
- theta updates in `aion_theta`
- goal progress snapshots in `aion_goal_progress`
- milestone objects in `aion_goal_milestone`
- milestone history in `aion_goal_milestone_history`

## Runtime Result Contract

`POST /event` currently returns the full `RuntimeResult`, which includes:

```json
{
  "event": {},
  "identity": {},
  "active_goals": [],
  "active_tasks": [],
  "active_goal_milestones": [],
  "goal_milestone_history": [],
  "goal_progress_history": [],
  "perception": {},
  "context": {},
  "motivation": {},
  "role": {},
  "plan": {},
  "action_result": {},
  "expression": {},
  "memory_record": {},
  "reflection_triggered": true,
  "stage_timings_ms": {},
  "duration_ms": 0
}
```

This is intentionally verbose today and is still treated as an internal debugging-friendly API contract rather than a final public DTO.
