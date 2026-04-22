# Logging and Debugging

## Purpose

This document defines how to observe, debug, and understand AION during runtime.

Without proper logging:

- system behavior becomes invisible  
- debugging becomes guesswork  
- errors become hard to trace  
- development slows down  

Logging is not optional.  
It is part of the architecture.

---

## Core Principle

Everything important must be observable.

If you cannot see:

- what happened  
- why it happened  
- what the system decided  

then you cannot trust or improve the system.

---

## What Must Be Logged

Every runtime cycle should log:

- event_id  
- trace_id  
- source  
- timestamp  
- selected role  
- motivation state  
- action result  
- memory write status  
- total execution time  

---

## Stage-Level Logging

Each stage should log:

- stage name  
- input summary  
- output summary  
- duration  
- errors (if any)  

---

## Example Runtime Log

{
  "trace_id": "trace_123",
  "event_id": "evt_456",
  "stage": "planning",
  "duration_ms": 120,
  "status": "success"
}

---

## Trace Concept

Every event should have a trace_id.

trace_id connects:

- all stages  
- all logs  
- all actions  

This allows full tracking of a single runtime cycle.

---

## Log Levels

### INFO

Normal operation:

- event received  
- stage completed  
- action executed  

---

### WARNING

Potential issues:

- missing data  
- fallback used  
- partial failure  

---

### ERROR

Failures:

- stage failure  
- API failure  
- DB failure  

---

### DEBUG

Detailed internal data:

- intermediate values  
- internal state  
- raw outputs  

Used during development.

---

## Logging Strategy

- log at every stage  
- keep logs structured  
- avoid excessive noise  
- focus on important signals  

---

## Structured Logging

Logs should be structured, not plain text.

Example:

{
  "stage": "context",
  "status": "success",
  "duration": 80,
  "summary": "context built"
}

---

## Error Handling Strategy

When error occurs:

1. catch error  
2. log error  
3. return safe fallback  
4. continue system if possible  

System must not crash silently.

---

## Debugging Workflow

When something breaks:

1. find trace_id  
2. follow logs step by step  
3. identify failing stage  
4. inspect input/output  
5. fix issue  
6. retest  

---

## Common Debug Problems

### Missing Context

- memory not retrieved  
- wrong event structure  

---

### Wrong Role Selection

- motivation incorrect  
- context incomplete  

---

### Bad Responses

- expression layer issue  
- incorrect planning  

---

### Memory Issues

- not stored  
- not retrieved  
- wrong importance  

---

## Observability Goals

You should be able to answer:

- what happened?  
- why did it happen?  
- what did system decide?  
- what changed after?  

---

## Tools

Basic:

- console logs  
- file logs  

Advanced (future):

- dashboards  
- log aggregation  
- tracing systems  

---

## Performance Logging

Track:

- response time  
- stage duration  
- memory retrieval time  
- LLM call time  

This helps optimization.

---

## Debug Mode

System should support debug mode:

- more logs  
- detailed outputs  
- no silent failures  

Runtime behavior-validation baseline requires two explicit modes:

- `system_debug`: internal payload surface with normalized event metadata,
  perception, retrieved memory bundle, context, motivation, role, plan intents,
  expression, and action result
- `user_simulation`: natural conversation checks without debug payload exposure

Behavior-driven scenario outcomes should be recorded in the canonical format:

```json
{
  "test_id": "T2.4",
  "status": "pass|fail|skip",
  "reason": "...",
  "trace_id": "...",
  "notes": "..."
}
```

Current post-convergence diagnostics also require:

- `/health.affective` to expose heuristic affective-input ownership separately
  from assessment rollout posture
- `system_debug.adaptive_state.affective_input_policy` and
  `system_debug.adaptive_state.affective_resolution` to show how the live turn
  moved from heuristic input to final affective result
- `/health.observability` to expose the shared export-policy owner and whether
  machine-readable incident evidence is actually available beyond local logs
- debug-mode runtime responses to expose `incident_evidence` with:
  - `trace_id`, `event_id`, `duration_ms`, and `stage_timings_ms`
  - machine-readable posture snapshots for runtime policy, retrieval,
    scheduler external ownership, reflection supervision, and connector
    execution baseline

---

## Final Principle

If you cannot observe the system,
you cannot control or improve it.

Logging turns AION from a black box into a transparent system.
