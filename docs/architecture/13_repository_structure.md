# Repository Structure

## Purpose

This document defines the recommended project structure for AION.

The goal is:

- clarity  
- scalability  
- separation of responsibilities  

A good structure prevents chaos as the system grows.

---

## Core Structure

Target `v2` structure:

aion/
- backend/
- web/
- mobile/
- docs/
- docker/
- docker-compose.yml
- .env.example

Current transition note:

- today the runtime still lives in the repository root
- approved `v2` direction moves that runtime into `backend/`
- `web/` and `mobile/` become explicit product surfaces instead of being
  implied future additions

---

## Application Layer

backend/app/

- api/
- agents/
- core/
- memory/
- motivation/
- identity/
- expression/
- integrations/
- workers/
- utils/

---

## Folder Breakdown

### api/

- FastAPI endpoints  
- webhook handlers  
- external interfaces  

---

### agents/

- perception agent  
- context agent  
- planning agent  
- reflection agent  

Each agent should be isolated and reusable.

---

### core/

- main logic  
- orchestration  
- LangGraph pipelines  
- system flow  

---

### memory/

- memory models  
- retrieval logic  
- storage interface  

---

### motivation/

- scoring system  
- decision logic  
- priority evaluation  

---

### identity/

- identity definition  
- theta system  
- role logic  

---

### expression/

- response formatting  
- output generation  
- channel adaptation  

---

### integrations/

- telegram/
- future integrations  

External systems live here.

---

### workers/

- subconscious loop  
- scheduled jobs  
- background processing  

---

### utils/

- helper functions  
- shared utilities  
- common logic  

---

## Tests

backend/tests/

- unit tests  
- integration tests  
- system tests  

Testing ensures system stability.

---

## Docs

docs/

- architecture  
- system design  
- specifications  

Documentation is part of the system.

---

## Docker

docker/

- Dockerfiles  
- service configs  

---

## Configuration Files

- pyproject.toml → dependencies  
- docker-compose.yml → services  
- .env → environment variables  

---

## Principles

1. Separate concerns  
2. Keep modules small  
3. Avoid tight coupling  
4. Prefer clarity over cleverness  

---

## Growth Strategy

As system grows:

- add modules, not chaos  
- extend existing structure  
- keep architecture consistent  

---

## Final Principle

Structure defines maintainability.

If structure breaks,
development slows down or stops.
