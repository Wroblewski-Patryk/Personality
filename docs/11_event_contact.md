# Event Contract

## Purpose

This document defines the standard structure for all inputs in AION.

Every stimulus must be converted into a unified event format before processing.

This ensures:

- consistency  
- scalability  
- predictable behavior  

---

## Core Principle

Everything is an event.

Sources may vary:

- Telegram  
- system triggers  
- scheduler  
- API calls  

But all must be normalized.

---

## Event Structure

{
  "event_id": "uuid",
  "source": "telegram|system|scheduler|api",
  "subsource": "user_message|ritual|alert",
  "timestamp": "ISO-8601",
  "payload": {},
  "meta": {
    "user_id": "uuid",
    "trace_id": "uuid"
  }
}

---

## Field Definitions

event_id  
Unique identifier for event  

source  
High-level origin  

subsource  
Specific type  

timestamp  
Time of occurrence  

payload  
Event data  

meta  
Operational metadata  

---

## Example – Telegram Message

{
  "event_id": "evt_001",
  "source": "telegram",
  "subsource": "user_message",
  "timestamp": "2026-01-01T10:00:00Z",
  "payload": {
    "text": "Pomóż mi zaplanować dzień"
  },
  "meta": {
    "user_id": "user_1",
    "trace_id": "trace_1"
  }
}

---

## Example – Scheduled Event

{
  "event_id": "evt_002",
  "source": "scheduler",
  "subsource": "morning_check",
  "timestamp": "2026-01-01T07:00:00Z",
  "payload": {},
  "meta": {
    "user_id": "user_1",
    "trace_id": "trace_2"
  }
}

---

## Runtime State

After normalization, event becomes runtime state.

{
  "event": {},
  "context": {},
  "memory": {},
  "motivation": {},
  "role": null,
  "plan": null,
  "result": null
}

---

## Rules

- every input must follow event structure  
- no direct raw input processing  
- no exceptions  

---

## Benefits

- unified pipeline  
- easier debugging  
- easier scaling  
- predictable system behavior  

---

## Final Principle

If something enters AION,
it must become an event first.

Without this rule,
architecture breaks.