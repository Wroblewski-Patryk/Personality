# Architecture

## Core Model

AION operates as a continuous loop:

STATE → PROCESS → ACTION → MEMORY → UPDATE → LOOP

The system never starts from zero.  
Every action is based on an existing state.

---

## Main Components

1. Identity  
2. Memory System  
3. Conscious Loop  
4. Subconscious Loop  
5. Motivation Engine  
6. Role / Skill System  
7. Agent Layer  
8. Action Layer  
9. Expression Layer  
10. Infrastructure  

---

## Execution Model

AION is a continuously running backend system.

It:

- receives events  
- processes them through a cognitive pipeline  
- performs actions when required  
- stores results  
- evolves over time  

---

## Two Main Loops

### Conscious Loop

Responsible for real-time behavior.

- interprets input  
- makes decisions  
- executes actions  
- communicates  
- writes episodic memory  

---

### Subconscious Loop

Responsible for background cognition.

- analyzes memory  
- detects patterns  
- generates conclusions  
- updates theta  
- refines behavior  

---

## Unified Cognitive Pipeline

All processing follows one pipeline:

Trigger → Perception → Context → Motivation → Planning → Action → Expression → Memory → Reflection

Each stage:

- has one responsibility  
- receives structured input  
- returns structured output  
- does not perform other stages' responsibilities  

---

## Stage Responsibilities

### Perception
What happened?

### Context
What does it mean?

### Motivation
How important is it?

### Planning
What should be done?

### Action
Execute changes in the system or outside world.

### Expression
Communicate result.

### Memory
Store the experience.

### Reflection
Learn from it (subconscious loop).

---

## Node Contract

Every processing unit must follow structure.

### Input

{
  "event": {},
  "context": {},
  "memory": {},
  "motivation": {},
  "identity": {},
  "theta": {}
}

### Output

{
  "result": {}
}

---

## Event Contract

All inputs must follow a unified format:

{
  "event_id": "uuid",
  "source": "telegram|system|scheduler|api",
  "subsource": "...",
  "timestamp": "ISO-8601",
  "payload": {},
  "meta": {
    "user_id": "...",
    "trace_id": "..."
  }
}

---

## Action Boundary

Only the Action layer can:

- write to database  
- call external APIs  
- send messages  
- modify system state  

Agents and reasoning layers must NOT perform side effects.

---

## Expression Layer

Responsible for output formatting.

Examples:

- Telegram messages  
- future UI responses  
- logs  

Expression is separate from logic.

---

## Performance Constraints

Target latency:

- simple response: 2–5s  
- normal response: 5–10s  
- complex response: max 15s  

Optimization strategies:

- minimize LLM calls  
- cache context  
- reduce unnecessary memory retrieval  
- keep subconscious processing async  

---

## Failure Handling

Each stage must support:

- validation  
- retry  
- fallback  
- logging  

Failures must not break the entire system.

---

## Observability

System should track:

- event_id  
- trace_id  
- stage  
- execution time  
- errors  
- model usage  

Without observability, debugging becomes impossible.

---

## Deployment Model

Recommended architecture:

- FastAPI (API layer)  
- LangGraph (orchestration)  
- PostgreSQL (data)  
- pgvector (semantic memory)  
- Docker (deployment)  
- VPS (hosting)  

---

## Architectural Principles

- Separation of responsibilities  
- Structured data flow  
- Controlled side effects  
- Persistent state  
- Event-driven processing  
- Scalable design  

---

## Final Principle

AION must remain:

- understandable  
- structured  
- debuggable  
- extensible  

Architecture is more important than intelligence.  
If architecture breaks, the system becomes chaos.