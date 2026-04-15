# Quickstart – AION

## Purpose

This document is the entry point for building AION.

It is written for:

- developers  
- AI coding agents (e.g. Codex)  

It defines:

- what to build first  
- how to structure the project  
- how to run the system  
- what MVP means in practice  

This file should be enough to start implementation without guessing.

---

## Core Goal

Build a minimal working AION system that:

- receives events  
- processes them through a pipeline  
- generates responses  
- stores memory  
- runs in Docker  
- communicates via Telegram  

---

## MVP Definition

The first working version must include:

- FastAPI server  
- event endpoint  
- basic runtime pipeline  
- simple memory write  
- Telegram integration  
- PostgreSQL connection  

Do NOT build full system immediately.

---

## Tech Stack (Required)

- Python 3.11+
- FastAPI
- PostgreSQL
- Docker + Docker Compose
- OpenAI API
- Telegram Bot API

---

## Project Setup

### 1. Create project

Create folder:

aion/

---

### 2. Basic structure

aion/
- app/
- docs/
- tests/
- docker/
- docker-compose.yml
- pyproject.toml
- .env

---

### 3. Install dependencies

Use:

- fastapi  
- uvicorn  
- psycopg2 or asyncpg  
- sqlalchemy (optional)  
- openai  

---

## Docker Setup

Create docker-compose.yml with:

- app (FastAPI)
- db (PostgreSQL)

Example services:

- app → Python service  
- db → postgres:15  

Expose:

- API port (e.g. 8000)  
- DB port (optional)  

---

## Environment Variables

Create `.env` file:

OPENAI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
DATABASE_URL=postgresql://user:password@db:5432/aion

---

## Step 1 – Run API

Create FastAPI app.

Basic endpoint:

POST /event

Input:
- raw event or Telegram message

Output:
- response message

Test:

- API must run  
- endpoint must accept request  

---

## Step 2 – Event Normalization

Inside endpoint:

- convert input into event structure  
- assign event_id  
- assign trace_id  
- add timestamp  

Return normalized event.

---

## Step 3 – Minimal Runtime Pipeline

Implement simple pipeline:

event → perception → context → planning → expression

Keep it simple.

Do NOT implement full system yet.

---

## Step 4 – Expression (MVP)

Return simple response:

- echo  
- or basic LLM response  

No need for full role system yet.

---

## Step 5 – Memory (MVP)

Create table:

aion_memory

Store:

- event_id  
- timestamp  
- summary  

Write memory after each request.

---

## Step 6 – Telegram Integration

Create bot.

Set webhook to:

POST /event

Flow:

Telegram → webhook → event → pipeline → response → Telegram

---

## Step 7 – Database Connection

Connect to PostgreSQL.

Test:

- insert memory  
- read memory  

---

## Step 8 – Basic Logging

Log:

- event_id  
- trace_id  
- endpoint hit  
- response status  

---

## Minimal Working Flow

1. receive Telegram message  
2. convert to event  
3. run simple pipeline  
4. generate response  
5. send response  
6. store memory  

---

## What NOT to Build Yet

Do NOT implement:

- subconscious loop  
- full motivation system  
- theta updates  
- relation system  
- advanced agents  
- multi-user  

Focus only on core loop.

---

## First Success Criteria

System is working if:

- Telegram message returns response  
- memory is stored  
- system runs in Docker  
- API is stable  

---

## Development Strategy

Build in small steps:

- implement  
- test  
- verify  
- move forward  

Do not skip steps.

---

## Debug Tips

If something breaks:

- check logs  
- check event structure  
- check DB connection  
- check API response  

---

## Next Steps After MVP

After working MVP:

1. improve memory retrieval  
2. add motivation layer  
3. add role selection  
4. add subconscious loop  
5. improve planning  

---

## Final Principle

Do not try to build AION fully at once.

Build a working loop first.

Then evolve it.

AION is a system that grows, not something built in one step.