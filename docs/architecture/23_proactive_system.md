# Proactive System

## Purpose

This document defines how AION initiates actions without explicit user input.

The Proactive System enables AION to:

- suggest actions  
- remind  
- check progress  
- initiate conversations  
- support goals actively  

Without it:

- system is purely reactive  
- value is limited to responses  
- long-term support is weak  

Proactivity is what turns AION into an active partner.

---

## Core Principle

Proactivity must be justified.

AION must NOT act randomly.

Every proactive action must be based on:

- goals  
- tasks  
- memory patterns  
- relation signals  
- time context  

Scheduler or subconscious wakeups may trigger analysis without forcing a
visible message.

If conscious evaluation finds no grounded reason to interrupt the user, the
tick should stay silent and complete as internal runtime work.

Proactivity is external future-facing planning, not the internal execution
loop for a turn that has already started. A scheduler cadence may support
passive reevaluation, but it should not wake the conscious loop unless a cheap
planned-action observer finds due planned work or an actionable relation-backed
proposal. If no such item exists, the cadence should end as a no-op and avoid
spending a full foreground run.

Relationship-based care, such as noticing unusual silence after an established
communication rhythm, should be inferred into planned work or a subconscious
proposal. It must not be encoded as a fixed code-level obligation to contact
the user every N hours.

---

## What Counts as Proactive Behavior

Examples:

- reminding about a task  
- suggesting next step  
- checking progress on a goal  
- proposing optimization  
- asking clarification  
- initiating reflection  

---

## What Is NOT Proactive Behavior

- random messages  
- unnecessary interruptions  
- repeating known information  
- irrelevant suggestions  

---

## Proactive Triggers

Proactive system activates when specific conditions are met.

---

### 1. Time-Based Triggers

Examples:

- morning check-in  
- evening reflection  
- weekly planning  
- deadline approaching  

Time alone is not sufficient for user-visible outreach. It only makes
planned-work and proposal reevaluation eligible.

---

### 2. Goal-Based Triggers

Examples:

- important goal has no progress  
- goal is near deadline  
- goal is repeatedly ignored  

---

### 3. Task-Based Triggers

Examples:

- task overdue  
- task blocked  
- recurring task missed  
- task requires follow-up  

---

### 4. Memory-Based Triggers

Examples:

- repeated pattern detected  
- recurring problem  
- past behavior suggests intervention  

---

### 5. Relation-Based Triggers

Examples:

- user prefers reminders  
- user responds well to check-ins  
- user tends to forget certain tasks  

---

### 6. Event-Based Triggers

Examples:

- external alert  
- system condition met  
- threshold exceeded  

---

## Proactive Decision Model

Before acting, AION must evaluate:

- importance  
- urgency  
- relevance  
- interruption cost  
- user context  

---

## Proactive Output Types

AION may produce:

- suggestion  
- reminder  
- question  
- warning  
- encouragement  
- insight  

---

## Proactive Modes

### Soft Mode

- suggestion  
- optional  
- low interruption  

---

### Medium Mode

- reminder  
- contextual  
- moderate importance  

---

### Strong Mode

- urgent alert  
- high importance  
- immediate attention  

---

## Proactive Frequency Control

System must limit frequency.

Rules:

- avoid spamming  
- avoid repetition  
- respect user tolerance  
- adapt based on response  

---

## Cooldown Mechanism

After proactive action:

- wait before next similar action  
- adjust based on user reaction  

---

## User Feedback Loop

System should observe:

- user response  
- user ignoring  
- user engagement  

This updates:

- relation system  
- theta  
- proactive behavior frequency  

---

## Example Flow

1. detect overdue task  
2. evaluate importance  
3. check recent reminders  
4. decide to act  
5. generate message  
6. send via Action System  
7. log proactive event  

---

## Proactive Message Structure

A good proactive message should:

- be relevant  
- be short  
- explain why it matters  
- suggest action  

Example:

"Masz task X, który jest opóźniony. Chcesz go zamknąć teraz czy przeplanować?"

---

## Anti-Spam Rules

AION must NOT:

- repeat same reminder frequently  
- send multiple messages without response  
- escalate without reason  
- interrupt during low-relevance moments  
- treat an internal scheduler prompt as if the user had authored a message  

---

## Context Awareness

Proactivity must consider:

- time of day  
- user activity patterns  
- current context  
- recent interactions  
- likely sleep windows  
- preferred conversation channel  
- inferred response cadence and relation tolerance  

## Multi-Channel Relational Outreach Baseline

The canonical app chat remains the primary conversation owner.

Linked channels such as Telegram may also receive proactive outreach when
runtime judges that propagation improves the chance of constructive contact.

Rules:

- no fixed global silence window is required for every user
- silence interpretation may adapt from relation evidence, habits, and explicit
  preference cues
- night-time silence should not be treated as a delivery problem by default
- a user message on any linked channel counts as contact and should reset
  silence posture
- if there is no grounded value in speaking, the system should stay silent
- if there is grounded value, outreach may happen on the app alone or on the
  app plus linked channels depending on inferred channel fit

---

## Proactive Logging

Each proactive action should log:

- trigger type  
- reason  
- importance  
- user response  
- outcome  

---

## MVP Requirements

For MVP:

- simple time-based trigger  
- basic task reminder  
- one proactive message per cycle  
- basic cooldown  

---

## Future Extensions

- adaptive frequency control  
- smart scheduling  
- multi-channel notifications  
- predictive suggestions  
- behavior-aware timing  

---

## Safety Rules

Proactivity must:

- remain helpful  
- remain controlled  
- avoid annoyance  
- respect user autonomy  

---

## Final Principle

Proactivity must feel like help, not noise.

If done correctly:

- AION becomes valuable even without user input  

If done poorly:

- AION becomes annoying and ignored
