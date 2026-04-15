# System Guardrails

## Purpose

This document defines the rules that protect AION from architectural decay.

As the system grows, complexity increases.

Without guardrails:

- architecture breaks  
- behavior becomes inconsistent  
- system becomes unpredictable  
- development slows down  

Guardrails ensure long-term stability.

---

## Core Principle

Do not sacrifice structure for speed.

Short-term hacks destroy long-term systems.

---

## Rule 1 – Separation of Concerns

Each layer must have one responsibility.

Never mix:

- planning with execution  
- expression with reasoning  
- memory with decision logic  
- agents with side effects  

If layers mix, system becomes impossible to debug.

---

## Rule 2 – Action Isolation

Only Action System may perform side effects.

No exceptions.

Violations lead to:

- hidden bugs  
- duplicated actions  
- unpredictable behavior  

---

## Rule 3 – Structured Data Only

All internal communication must be structured.

No:

- raw text passing  
- implicit assumptions  
- hidden state  

Everything must be explicit.

---

## Rule 4 – No Hidden State

All important state must be:

- stored  
- traceable  
- observable  

If something affects behavior, it must exist in data.

---

## Rule 5 – Memory Must Influence Behavior

If memory is not used:

- remove it  
- or fix retrieval  

Memory without effect is dead weight.

---

## Rule 6 – Slow Adaptation

Theta and relations must evolve slowly.

Never allow:

- instant personality shifts  
- reaction to single event  
- unstable behavior  

---

## Rule 7 – Identity Stability

Identity must remain stable.

It can evolve only when:

- strong patterns exist  
- reflection confirms change  

Identity drift = system collapse.

---

## Rule 8 – No Overengineering

Do not add:

- agents without need  
- layers without purpose  
- abstractions without usage  

Complexity must be earned.

---

## Rule 9 – MVP First

Before adding features:

- check if MVP is stable  
- check if core loops work  
- check if system behaves coherently  

Do not scale broken foundations.

---

## Rule 10 – Observability Required

Every important action must be:

- logged  
- traceable  
- debuggable  

If you cannot see it, you cannot fix it.

---

## Rule 11 – Deterministic Core

Where possible:

- use deterministic logic  
- limit LLM randomness  
- keep outputs predictable  

LLM should assist, not dominate.

---

## Rule 12 – Controlled Proactivity

Proactivity must be:

- justified  
- limited  
- adaptive  

Uncontrolled proactivity = user churn.

---

## Rule 13 – Fail Gracefully

System must never:

- crash silently  
- lose data  
- stop responding  

Failures must:

- be logged  
- be handled  
- be recoverable  

---

## Rule 14 – One Source of Truth

Each type of data must have one owner:

- memory → memory system  
- goals → goal system  
- relation → relation system  

No duplication of truth.

---

## Rule 15 – Explicit Flow

Every flow must be:

- understandable  
- traceable  
- predictable  

If you cannot explain a flow,
it is too complex.

---

## Rule 16 – No Implicit Magic

Avoid:

- hidden automation  
- implicit triggers  
- unclear dependencies  

Everything must be visible in architecture.

---

## Rule 17 – Incremental Development

Build in steps:

- small changes  
- test  
- validate  
- expand  

Do not build large untested systems.

---

## Rule 18 – System Over Features

Always ask:

Does this improve the system?

Not:

Is this a cool feature?

---

## Rule 19 – Remove Before Adding

Before adding new component:

- check if existing one can handle it  
- simplify instead of expanding  

---

## Rule 20 – Clarity Over Cleverness

Prefer:

- simple  
- readable  
- explicit  

Over:

- clever  
- complex  
- implicit  

---

## Final Principle

AION must remain:

- structured  
- understandable  
- controllable  
- extensible  

Guardrails are what keep it that way.

Without them, the system will slowly turn into chaos.