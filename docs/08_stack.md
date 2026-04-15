# Technology Stack

## Purpose

This document defines the technology stack for AION.

The goal is to build a real backend system, not a collection of workflows.

---

## Core Stack

### Language

- Python

Used for:

- system logic  
- agents  
- orchestration  
- API  
- background jobs  

---

### API Layer

- FastAPI

Used for:

- receiving events  
- exposing endpoints  
- Telegram webhook  
- system control  

---

### Orchestration

- LangGraph

Used for:

- cognitive pipelines  
- state flow  
- decision graphs  
- loop execution  

---

### Optional Support

- LangChain

Used only when needed:

- prompt templates  
- retrievers  
- parsing  

LangChain is NOT the core architecture.

---

## Memory Stack

### Database

- PostgreSQL

Stores:

- memory  
- identity  
- goals  
- tasks  
- system state  

---

### Vector Search

- pgvector

Used for:

- semantic memory retrieval  
- similarity search  

---

## Communication

### Telegram

- Telegram Bot API

Used for:

- input (messages)  
- output (responses)  

Telegram is an interface, not core logic.

---

## AI Layer

### LLM Provider

- OpenAI API

Used for:

- reasoning  
- planning  
- interpretation  
- expression  

---

### Optional Local Models

- Ollama  
- vLLM  

Used for:

- offline testing  
- cost reduction  
- simple tasks  

Not required for MVP.

---

## Runtime Components

### Main App

- FastAPI service  
- LangGraph runtime  

Handles:

- conscious loop  
- API  
- event processing  

---

### Worker

- background process  

Handles:

- subconscious loop  
- reflection  
- scheduled tasks  

---

### Scheduler

Options:

- APScheduler  
- cron  

Used for:

- periodic reflection  
- daily routines  
- system maintenance  

---

### Cache (Optional)

- Redis

Used for:

- caching  
- queues  
- temporary state  

Add only if needed.

---

## Infrastructure

### Containerization

- Docker  
- Docker Compose  

All services should run in containers.

---

### Hosting

- VPS (e.g. OVH)

Used for:

- running containers  
- hosting backend  

---

### Reverse Proxy

- Nginx or Caddy  

Used for:

- routing  
- HTTPS  
- public access  

---

## Observability

### Logging

- Python logging  

Track:

- events  
- errors  
- execution flow  

---

### Metrics (Optional)

- Prometheus  

Track:

- latency  
- usage  
- failures  

---

## Configuration

- environment variables  
- .env files  

Store:

- API keys  
- DB credentials  
- system settings  

---

## Repository Structure (High-Level)

aion/
- app/
- agents/
- memory/
- api/
- workers/
- tests/
- docs/
- docker/

---

## MVP Stack

Minimum required:

- Python  
- FastAPI  
- LangGraph  
- PostgreSQL  
- pgvector  
- Docker  
- Telegram API  
- OpenAI API  

---

## What Is NOT Required

- n8n  
- complex orchestration tools  
- multiple databases  
- heavy frontend  

---

## Final Principle

Stack must serve architecture.

If technology adds complexity without value,
it should not be used.