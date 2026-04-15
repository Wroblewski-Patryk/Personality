# Agent Contracts

## Purpose

This document defines the exact input and output structures for each agent in AION.

It is the bridge between:

- architecture  
- implementation  

Without this document:

- agents become inconsistent  
- data flow becomes unclear  
- debugging becomes difficult  

---

## Core Principle

Every agent must:

- receive structured input  
- return structured output  
- follow a strict contract  

No free-form chaos.

---

## Shared Input Structure

All agents receive a subset of the runtime state.

Base structure:

{
  "event": {},
  "perception": {},
  "context": {},
  "memory": {},
  "conclusions": [],
  "goals": [],
  "tasks": [],
  "identity": {},
  "theta": {},
  "motivation": {},
  "role": {},
  "plan": {}
}

Agents should only use relevant fields.

---

## Perception Agent

### Purpose

Understand what happened.

### Input

{
  "event": {}
}

### Output

{
  "perception": {
    "event_type": "...",
    "topic": "...",
    "intent": "...",
    "ambiguity": 0.0,
    "initial_salience": 0.0
  }
}

---

## Context Agent

### Purpose

Build situational understanding.

### Input

{
  "event": {},
  "perception": {},
  "memory": {},
  "goals": [],
  "tasks": [],
  "identity": {}
}

### Output

{
  "context": {
    "summary": "...",
    "related_goals": [],
    "related_tags": [],
    "risk_level": 0.0
  }
}

---

## Motivation Agent

### Purpose

Determine importance and urgency.

### Input

{
  "event": {},
  "context": {},
  "goals": [],
  "theta": {}
}

### Output

{
  "motivation": {
    "importance": 0.0,
    "urgency": 0.0,
    "valence": 0.0,
    "arousal": 0.0,
    "mode": "respond|ignore|investigate|act_now"
  }
}

---

## Role Selection Agent

### Purpose

Choose behavior mode.

### Input

{
  "event": {},
  "context": {},
  "motivation": {},
  "identity": {}
}

### Output

{
  "role": {
    "selected": "...",
    "confidence": 0.0
  }
}

---

## Planning Agent

### Purpose

Decide what to do.

### Input

{
  "context": {},
  "motivation": {},
  "role": {},
  "goals": []
}

### Output

{
  "plan": {
    "goal": "...",
    "steps": [],
    "needs_action": true,
    "needs_response": true
  }
}

---

## Action Layer Contract

### Purpose

Execute real-world effects.

### Input

{
  "plan": {},
  "event": {}
}

### Output

{
  "action_result": {
    "status": "success|fail|noop",
    "actions": [],
    "notes": "..."
  }
}

---

## Expression Agent

### Purpose

Generate output for user.

### Input

{
  "context": {},
  "role": {},
  "motivation": {},
  "plan": {},
  "action_result": {}
}

### Output

{
  "expression": {
    "message": "...",
    "tone": "...",
    "channel": "telegram"
  }
}

---

## Memory Write Contract

### Purpose

Store episode after processing.

### Input

{
  "event": {},
  "context": {},
  "role": {},
  "motivation": {},
  "plan": {},
  "action_result": {},
  "expression": {}
}

### Output

{
  "memory_record": {
    "summary": "...",
    "importance": 0.0
  }
}

---

## Reflection Agent

### Purpose

Analyze patterns and update system.

### Input

{
  "recent_memory": [],
  "existing_conclusions": [],
  "theta": {}
}

### Output

{
  "reflection": {
    "new_conclusions": [],
    "updated_conclusions": [],
    "theta_update": {}
  }
}

---

## Contract Rules

1. Every agent must return exactly its own field  
2. No agent returns full system state  
3. No agent modifies external systems  
4. No agent mixes responsibilities  

---

## Validation

Each output must be:

- JSON-valid  
- schema-consistent  
- minimal  

---

## Common Mistakes

- returning too much data  
- mixing multiple responsibilities  
- free-form text instead of structure  
- skipping fields  

---

## Final Principle

Agents communicate through contracts.

If contracts are clear:

- system is predictable  
- system is debuggable  
- system is scalable  

If contracts are unclear:

- system becomes chaos