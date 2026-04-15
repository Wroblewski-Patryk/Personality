# Codex Instructions

## Purpose

This document defines how AI coding agents (e.g. Codex) must behave when working on AION.

It ensures:

- architectural consistency  
- correct implementation  
- avoidance of shortcuts  
- long-term scalability  

This file is mandatory for AI-assisted development.

---

## Core Principle

Follow architecture. Do not simplify it.

Even if a shortcut seems easier,
it must not break system design.

---

## System Understanding

Before writing code, you must understand:

- AION is event-driven  
- AION is stateful  
- AION separates cognition and action  
- AION uses structured data between components  

Do not treat it as a simple chatbot.

---

## Strict Rules

### Rule 1 – Do NOT Skip Event System

All input must:

- be normalized into event structure  
- include event_id and trace_id  

Never process raw input directly.

---

### Rule 2 – Respect Pipeline

All logic must follow:

event → perception → context → motivation → planning → action → expression → memory

Do not merge steps.

---

### Rule 3 – No Side Effects Outside Action Layer

Only Action System can:

- write to database  
- call APIs  
- send messages  

No exceptions.

---

### Rule 4 – Use Structured Data

All components must communicate using structured objects.

Do NOT:

- pass raw text  
- rely on implicit state  
- skip fields  

---

### Rule 5 – Keep Modules Separate

Do not mix:

- memory logic with planning  
- expression with reasoning  
- API with business logic  

Each module must have one responsibility.

---

### Rule 6 – No Hardcoding

Do not hardcode:

- API keys  
- DB connections  
- configuration values  

Use environment config.

---

### Rule 7 – Implement Minimal First

When building:

- start with simplest working version  
- do not implement full architecture at once  
- follow iteration plan  

---

### Rule 8 – Avoid Overengineering

Do not:

- create unnecessary abstractions  
- add layers without purpose  
- introduce complexity too early  

---

### Rule 9 – Logging Required

Every major step must log:

- event_id  
- trace_id  
- stage  
- result  

---

### Rule 10 – Memory Must Be Used

If memory is stored, it must be retrievable later.

Do not implement write-only memory.

---

## Coding Style

- clear and readable  
- explicit over implicit  
- small functions  
- simple logic  
- structured outputs  

---

## File Organization

Follow repository structure strictly.

Do not:

- create random folders  
- mix unrelated code  
- duplicate logic  

---

## API Rules

FastAPI must:

- only receive requests  
- call internal logic  
- return structured response  

Do not place business logic inside endpoints.

---

## Database Rules

- use clear models  
- validate data before write  
- handle errors  
- log operations  

---

## Error Handling

Never:

- crash silently  
- ignore exceptions  

Always:

- log error  
- return safe fallback  

---

## When Unsure

If unclear:

- follow architecture docs  
- prefer simpler implementation  
- do not invent new patterns  

---

## Anti-Patterns

Do NOT:

- merge multiple stages into one function  
- skip event normalization  
- call DB inside planning  
- send messages outside Action System  
- ignore config system  

---

## Development Approach

Always:

- implement small part  
- test it  
- verify behavior  
- continue  

---

## Final Principle

You are building a system, not just code.

Every line must respect:

- structure  
- flow  
- separation  
- clarity  

If code breaks architecture,
it is wrong even if it works.