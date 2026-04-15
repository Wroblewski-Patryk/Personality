# Memory System

## Purpose

Memory is the persistence layer that gives AION continuity over time.

Without memory:

- there is no identity continuity  
- there is no learning  
- there is no adaptation  

Memory is not storage.  
Memory is a core cognitive component.

---

## Core Principle

Memory must influence behavior.

If stored information does not change future decisions, it is useless.

Memory exists to:

- support cognition  
- improve decisions  
- maintain continuity  
- enable adaptation  

---

## Types of Memory

### 1. Episodic Memory

Stores events and experiences.

Examples:

- conversations  
- system actions  
- user interactions  
- outcomes  

This is the raw history of the system.

---

### 2. Semantic (Conclusion) Memory

Stores generalized knowledge extracted from experience.

Examples:

- user prefers short answers  
- certain patterns repeat  
- specific behaviors work better  

This memory is more important than raw episodes.

---

### 3. Working Memory

Temporary runtime state.

Contains:

- current event  
- context  
- selected role  
- current plan  

This memory is not persistent.

---

### 4. Temporal Memory

Recent time-based context.

Examples:

- last 24 hours  
- last week  
- recent actions  

Helps maintain short-term continuity.

---

### 5. Identity-Linked Memory

Stores long-term stable information:

- preferences  
- goals  
- patterns  
- relation context  

---

## Storage Model

AION uses:

- PostgreSQL for structured data  
- pgvector for semantic retrieval  

Current MVP status:

- episodic memory is stored in PostgreSQL
- lightweight identity-linked preferences are stored in `aion_profile`
- first semantic preference conclusions are stored in `aion_conclusion`
- runtime retrieval now combines recent episodes with stable semantic preferences during context construction
- a lightweight in-process reflection worker now consolidates some conclusions asynchronously after episode writes
- episodic summaries now also capture the role used, so reflection can infer lightweight `preferred_role` tendencies over time
- reflection now also maintains a lightweight `aion_theta` state with soft support, analysis, and execution biases derived from repeated recent role patterns
- runtime still prefers explicit heuristics and reflected `preferred_role`, but can now also use theta as a softer bias on ambiguous turns for role selection, motivation mode selection, lightweight planning stance, and expression tone selection
- vector retrieval is still planned, not live

---

## Memory Lifecycle

event → episode → retrieval → reflection → conclusion → update

Detailed:

1. event occurs  
2. episode is stored  
3. future event retrieves relevant memory  
4. subconscious loop analyzes patterns  
5. conclusions are created  
6. theta is updated  
7. future behavior improves  

---

## Episodic Memory Structure

Each record should contain:

- event_id  
- timestamp  
- summary  
- context  
- role used  
- motivation snapshot  
- plan  
- action result  
- expression summary  
- importance score  

---

## Conclusion Memory Structure

Each conclusion should contain:

- type  
- content  
- confidence  
- supporting memories  
- created_at  
- updated_at  

---

## Retrieval Strategy

Memory retrieval must be:

- relevant  
- limited  
- structured  

Steps:

1. fetch goals and identity  
2. fetch recent memory  
3. fetch semantic matches  
4. combine and filter  

---

## Importance (Salience)

Each memory should have importance score.

Factors:

- emotional weight  
- goal relevance  
- repetition  
- outcome impact  

This controls:

- what is stored  
- what is retrieved  
- what is ignored  

---

## Consolidation

Raw memory must be processed.

Subconscious loop should:

- group similar events  
- detect patterns  
- generate conclusions  
- reduce noise  

This prevents memory overload.

---

## Memory Decay

Not all memories stay relevant.

System should support:

- decay of importance  
- archival of old data  
- updating confidence  

---

## Memory and Identity

Rules:

- one event cannot change identity  
- repeated patterns may influence theta  
- identity changes are rare  

---

## Safety Rules

Memory must not:

- store everything blindly  
- overfit on single event  
- treat all data equally  
- leak sensitive data  

---

## Suggested Tables

- aion_memory  
- aion_conclusion  
- aion_profile  
- aion_theta  
- goals  
- tasks  

---

## Final Principle

Memory is not a log.

Memory is a system that:

- preserves meaning  
- influences behavior  
- enables adaptation  

Without it, AION is just a chatbot.
