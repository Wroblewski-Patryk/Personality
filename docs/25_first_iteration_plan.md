# First Iteration Plan

## Purpose

This document defines the exact first development iteration of AION.

It is a concrete execution plan for:

- developer  
- AI coding agent (Codex)  

Unlike roadmap, this file is:

- strict  
- ordered  
- minimal  
- executable  

---

## Core Goal

Deliver a working minimal AION system that:

- receives Telegram messages  
- processes them through a simple pipeline  
- responds  
- stores memory  

Nothing more.

---

## Iteration Scope

Included:

- FastAPI  
- event endpoint  
- Telegram webhook  
- basic pipeline  
- PostgreSQL connection  
- memory write  

Excluded:

- subconscious loop  
- advanced agents  
- motivation system  
- theta system  
- relation system  
- proactivity  

---

## Execution Order

Follow strictly in this order.

Do NOT skip steps.

---

## Step 1 – Project Initialization

Tasks:

- create repository  
- create project structure  
- add pyproject.toml  
- create .env file  
- create docker-compose.yml  

Success criteria:

- project builds  
- docker runs  

---

## Step 2 – FastAPI Setup

Tasks:

- create FastAPI app  
- create /event endpoint  
- return static response  

Success criteria:

- server runs  
- endpoint responds  

---

## Step 3 – Event System

Tasks:

- create event schema  
- generate event_id  
- generate trace_id  
- normalize input  

Success criteria:

- every request returns structured event  

---

## Step 4 – Telegram Integration

Tasks:

- create Telegram bot  
- set webhook to /event  
- map Telegram message → event  

Success criteria:

- message from Telegram hits API  

---

## Step 5 – Basic Pipeline

Tasks:

- implement simple pipeline:

event → simple processing → response  

Minimal behavior:

- extract text  
- generate response (echo or LLM)  

Success criteria:

- system responds to Telegram  

---

## Step 6 – Database Setup

Tasks:

- connect PostgreSQL  
- create aion_memory table  

Table fields:

- id  
- event_id  
- timestamp  
- summary  

Success criteria:

- can insert memory  

---

## Step 7 – Memory Write

Tasks:

- store event after processing  
- store summary  
- log result  

Success criteria:

- every message creates DB entry  

---

## Step 8 – Logging

Tasks:

- log event_id  
- log trace_id  
- log request start/end  

Success criteria:

- logs show full flow  

---

## Step 9 – Docker Integration

Tasks:

- run app in container  
- connect DB container  
- test full flow  

Success criteria:

- full system works in Docker  

---

## Step 10 – Basic Stability

Tasks:

- handle errors  
- validate input  
- avoid crashes  

Success criteria:

- system does not crash on bad input  

---

## Minimal Pipeline Definition

At this stage pipeline =

1. receive event  
2. extract message  
3. generate simple response  
4. send response  
5. store memory  

No advanced logic required.

---

## Allowed Simplifications

- no agent system yet  
- no role system  
- no motivation  
- no context building  
- no memory retrieval  

Keep everything minimal.

---

## First Working Version

System should:

- respond to Telegram  
- store messages  
- log execution  
- run in Docker  

That is enough.

---

## Anti-Patterns

Do NOT:

- implement full architecture  
- add multiple agents  
- overuse LLM  
- build features ahead of plan  
- optimize too early  

---

## Development Loop

For each step:

- implement  
- test  
- verify  
- commit  

Repeat.

---

## Completion Criteria

Iteration is complete when:

- Telegram → response works  
- memory is stored  
- logs are visible  
- system runs reliably  

---

## Next Iteration Preview

After this:

- memory retrieval  
- context building  
- motivation system  
- role system  

---

## Final Principle

First iteration is not about intelligence.

It is about:

- working system  
- stable base  
- correct flow  

Everything else builds on top of it.