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

### 2. Semantic (Conclusion) Memory

Stores generalized knowledge extracted from experience.

Examples:

- user prefers short answers
- certain patterns repeat
- specific behaviors work better

This memory is more stable than raw episodes.

### 3. Working Memory

Temporary runtime state.

Contains:

- current event
- context
- selected role
- current plan

This memory is not persistent.

### 4. Temporal Memory

Recent time-based context.

Examples:

- last 24 hours
- last week
- recent actions

Helps maintain short-term continuity.

### 5. Identity-Linked Memory

Stores longer-lived user and system knowledge:

- preferences
- goals
- recurring patterns
- relation context

---

## Storage Model

AION needs durable structured storage for:

- episodes
- conclusions
- identity-linked state
- adaptive state
- goals and tasks

Vector or embedding-based retrieval may be added later, but it is not required for the canonical model.

## Runtime Memory Layer Vocabulary

To keep runtime and repository boundaries explicit, memory retrieval should use one shared vocabulary:

- `episodic`: turn-level event traces and payload snapshots
- `semantic`: generalized conclusions derived from episodes
- `affective`: emotionally relevant support patterns and continuity signals
- `operational`: active runtime state used to execute work (preferences, goals, tasks, milestone signals)

The same layer names should be used in:

- repository retrieval APIs
- runtime memory-load orchestration
- architecture and operations docs

---

## Memory Lifecycle

`event -> episode -> retrieval -> reflection -> conclusion -> update`

Detailed flow:

1. an event occurs
2. an episode is stored
3. a future event retrieves relevant memory
4. the subconscious loop analyzes patterns
5. conclusions are created or updated
6. adaptive state evolves
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

Typical order:

1. fetch operational state needed for active execution
2. fetch episodic memory for near-turn continuity
3. fetch semantic and affective conclusions
4. combine, rank, and filter for current context

---

## Importance (Salience)

Each memory should have an importance score.

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

The subconscious loop should:

- group similar events
- detect patterns
- generate conclusions
- reduce noise

This prevents memory overload.

---

## Memory Decay

Not all memories stay equally relevant.

The system should support:

- decay of importance
- archival of old data
- confidence updates

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
- overfit on a single event
- treat all data equally
- leak sensitive data

---

## Suggested Persistent Stores

- episodic_memory
- conclusions
- identity_profile
- theta_state
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
