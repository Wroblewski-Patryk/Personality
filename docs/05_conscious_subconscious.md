# Conscious vs Subconscious

## Purpose

This document defines the two main operating modes of AION:

- conscious loop  
- subconscious loop  

They are not separate personalities.  
They are two modes of the same system.

---

## Core Principle

AION operates in two temporal modes:

- Conscious → handles the present  
- Subconscious → processes the past to improve the future  

---

## Conscious Loop

### Definition

The conscious loop is the real-time processing layer.

It reacts to incoming events and produces immediate behavior.

---

### Responsibilities

- receive event  
- interpret input  
- build context  
- retrieve memory  
- evaluate importance  
- select role  
- create plan  
- execute actions  
- generate response  
- store episodic memory  

---

### Flow

input → perception → context → motivation → role → plan → action → expression → memory

---

### Characteristics

- fast  
- reactive  
- visible to user  
- action-oriented  

---

### Constraints

The conscious loop must NOT:

- update identity directly  
- perform deep learning  
- overfit on single events  
- perform heavy reflection  

Its job is to act, not to evolve the system.

---

## Subconscious Loop

### Definition

The subconscious loop is the background processing layer.

It runs independently of real-time interaction.

---

### Responsibilities

- analyze stored memory  
- detect patterns  
- generate conclusions  
- update theta  
- refine behavior  
- maintain consistency  

---

### Flow

memory → analysis → pattern detection → conclusions → theta update → storage

---

### Characteristics

- slow  
- reflective  
- not user-visible  
- pattern-oriented  

---

## Key Rule

Conscious loop = action  
Subconscious loop = adaptation  

This separation is critical.

---

## Why Separation Matters

Without separation:

- system becomes slow  
- learning becomes unstable  
- identity becomes chaotic  
- responses degrade  

With separation:

- real-time stays fast  
- learning stays stable  
- system evolves correctly  

---

## Shared State

Both loops operate on the same:

- identity  
- memory  
- theta  
- goals  
- context  

This ensures coherence.

---

## Communication Policy

### Conscious loop

- communicates directly with user  

### Subconscious loop

- does NOT communicate directly  
- produces internal updates  

If needed, subconscious insights are passed through conscious loop.

---

## Triggers

### Conscious triggers

- user message  
- API request  
- system event  

### Subconscious triggers

- time-based (cron)  
- batch processing  
- after N events  
- scheduled reflection  

---

## Temporal Dynamics

- conscious loop = immediate  
- subconscious loop = periodic  

Example:

- real-time: always active  
- reflection: every few hours  
- deep reflection: daily  

---

## Failure Isolation

If subconscious loop fails:

- conscious loop must still work  
- system must still respond  
- reflection can retry later  

---

## Implementation Split

### Conscious

- FastAPI endpoint  
- LangGraph pipeline  
- Telegram integration  
- memory writing  

### Subconscious

- background worker  
- scheduler  
- reflection pipeline  
- conclusion updates  

---

## Final Principle

AION works because:

- it acts in the present  
- it learns from the past  

Conscious loop lives.  
Subconscious loop understands.