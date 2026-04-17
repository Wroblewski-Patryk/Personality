# Agent System

## Purpose

This document defines the agent layer in AION.

Agents are not the system.  
Agents are components used by the system.

AION = architecture  
Agents = tools inside that architecture

---

## Core Rule

Agents are NOT personalities.

Agents are processors.

They perform specific tasks such as:

- interpreting input  
- analyzing context  
- generating plans  
- formatting responses  
- extracting patterns  

---

## Why Agents Exist

Agents allow:

- modular design  
- clear responsibilities  
- easier debugging  
- better scalability  
- structured outputs  

Instead of one large prompt, AION uses multiple focused components.

---

## Core Agents

### Perception Agent

- identifies event type  
- detects intent  
- extracts basic meaning  

---

### Context Agent

- builds situation understanding  
- connects event with memory and goals  

---

### Motivation Agent

- evaluates importance  
- determines urgency  
- sets action tendency  

---

### Role Selection Agent

- selects behavior mode  
- determines how AION should act  

---

### Planning Agent

- decides what to do  
- creates structured plan  

---

### Expression Agent

- formats output  
- adjusts tone and style  

---

### Reflection Agent

- analyzes past memory  
- generates conclusions  
- updates system behavior  

---

## Optional Agents (Future)

- simulation agent  
- strategy agent  
- business agent  
- relation agent  
- ecosystem agent  

Not required for MVP.

---

## Agent Rules

Each agent must:

- have one responsibility  
- receive structured input  
- return structured output  

---

## No Side Effects Rule

Agents must NOT:

- write to database  
- call APIs  
- send messages  

Agents only think.

---

## Exception

Action layer executes:

- database operations  
- API calls  
- communication  

---

## Agent Inputs

Agents receive:

- event  
- context  
- memory  
- motivation  
- identity  
- theta  

Only relevant parts should be passed.

---

## Agent Outputs

Agents must return structured data.

Example:

{
  "plan": {
    "goal": "...",
    "steps": [...]
  }
}

No unstructured chaos.

---

## Design Principles

1. Single responsibility  
2. Clear input/output  
3. Replaceable  
4. Minimal complexity  
5. Structured communication  

---

## Agents vs Roles

Agent = processing unit  
Role = behavior mode  

Example:

Planning agent can work in:

- advisor role  
- executor role  

Same logic, different expression.

---

## Agents vs Skills

Skill = capability  
Agent = processor  

Example:

Skill:
- research  

Agent:
- decides when to use it  

---

## Implementation

Agents can be:

- LangGraph nodes  
- Python functions  
- LLM calls  
- hybrid logic  

Not every agent needs LLM.

---

## Error Handling

Agents must support:

- validation  
- retry  
- fallback  

---

## Model Strategy

Different agents can use different models.

Example:

- small model → classification  
- large model → planning  

---

## Core Flow

event → perception → context → motivation → role → planning → action → expression → memory → reflection

---

## When NOT to Create Agent

Do not create agent if:

- logic is simple  
- no clear responsibility  
- adds unnecessary complexity  

---

## Final Principle

Agents are internal tools.

They help AION think in a structured way.

They are not independent systems.