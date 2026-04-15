# Data Model

## Purpose

This document defines the core data structure for AION.

The goal is to support:

- memory  
- identity  
- adaptation  
- decision making  

Without proper data structure, AION cannot function as a persistent system.

---

## Core Principle

Data must reflect cognition.

If the system:

- remembers  
- learns  
- adapts  

then the database must support those operations.

---

## Core Tables

### users

Stores system owner.

Fields:

- id  
- created_at  
- updated_at  
- name  

---

### aion_identity

Stores identity definition.

Fields:

- id  
- user_id  
- mission  
- values  
- behavior_rules  
- created_at  
- updated_at  

---

### aion_theta

Stores adaptive parameters.

Fields:

- id  
- user_id  
- emotional  
- display  
- learning  
- cognitive  
- updated_at  

---

### aion_memory

Stores episodic memory.

Fields:

- id  
- user_id  
- event_id  
- timestamp  
- summary  
- context  
- role  
- plan  
- result  
- importance  

---

### aion_conclusions

Stores learned patterns.

Fields:

- id  
- user_id  
- type  
- content  
- confidence  
- created_at  
- updated_at  

---

### goals

Stores goals.

Fields:

- id  
- user_id  
- name  
- description  
- priority  
- status  

---

### tasks

Stores tasks.

Fields:

- id  
- user_id  
- goal_id  
- name  
- status  
- priority  

---

### metrics

Stores measurable data.

Fields:

- id  
- user_id  
- name  
- value  
- timestamp  

---

## Relationships

- user → identity (1:1)  
- user → theta (1:1)  
- user → memory (1:N)  
- user → conclusions (1:N)  
- user → goals (1:N)  
- goals → tasks (1:N)  

---

## Storage

- PostgreSQL for structured data  
- pgvector for semantic search  

---

## Memory Priority

Not all data is equal.

Each memory should have:

- importance  
- relevance  
- recency  

This controls retrieval.

---

## Minimal MVP Tables

- users  
- identity  
- theta  
- memory  
- conclusions  

---

## Optional Tables (Future)

- relation_notes  
- event_logs  
- memory_links  
- theta_history  

---

## Final Principle

Database is not storage.

Database is the memory system of AION.

If data model is weak,
system cannot become intelligent.