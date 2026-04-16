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
- a lightweight reflection worker now consolidates some conclusions asynchronously after episode writes
- reflection jobs are now also stored in `aion_reflection_task`, so pending background work survives app restarts and can be recovered on startup
- failed reflection jobs now retry with lightweight backoff and a bounded attempt limit, so transient worker errors do not immediately drop background consolidation
- runtime health now exposes a lightweight reflection snapshot so pending, failed, retryable, exhausted, and stuck background tasks are visible operationally
- episodic summaries now also capture motivation mode and plan steps, so background reflection can learn not only output style but also the user's preferred collaboration shape
- episodic summaries now also capture the role used, so reflection can infer lightweight `preferred_role` tendencies over time
- reflection now also maintains a lightweight `aion_theta` state with soft support, analysis, and execution biases derived from repeated recent role patterns
- runtime still prefers explicit heuristics and reflected `preferred_role`, but can now also use theta as a softer bias on ambiguous turns for role selection, motivation mode selection, lightweight planning stance, and expression tone selection
- semantic conclusions can now also infer `collaboration_preference`, for example whether the user tends to prefer guided step-by-step help or more hands-on concrete execution help
- episodic summaries now also capture explicit `collaboration_update` markers from direct requests like `step by step` or `do it for me`, so reflection can honor those signals without waiting only for repeated-pattern learning
- collaboration preference now influences role selection, motivation, planning, and expression, so the runtime can lean more guiding or more action-oriented even when the request itself is short or ambiguous
- semantic conclusions can now also infer lightweight goal-execution momentum, including `blocked`, `recovering`, `advancing`, `progressing`, and an early `stagnating` pattern derived from active task state plus repeated plan-vs-execution patterns
- reflection can now also derive a lightweight `goal_progress_score`, so runtime can tell not only whether the goal is moving, but also whether it is still early, mid-way, or entering the final stretch
- reflection can now also derive a lightweight `goal_progress_trend`, so runtime can tell whether goal progress is improving, steady, or slipping compared with the previous reflected score
- reflection now also persists lightweight `aion_goal_progress` snapshots for the primary active goal, so runtime can retrieve a short goal-level history instead of relying only on the latest reflected hint
- reflection can now also compress short goal-history patterns into a semantic `goal_progress_arc`, for example distinguishing traction in recovery from unstable or falling-behind progress
- reflection can now also maintain a lightweight `goal_milestone_state`, so runtime can keep a stable sense of whether the goal is still early, in active execution, in recovery, or already in the completion window
- reflection can now also emit a lightweight `goal_milestone_transition`, so runtime can notice threshold crossings like entering active execution, entering the completion window, or slipping back out of it
- reflection now also materializes that milestone understanding into lightweight `aion_goal_milestone` objects, so runtime can load an active milestone focus instead of relying only on semantic conclusions
- reflection can now also derive lightweight milestone-operational signals such as `goal_milestone_risk` and `goal_completion_criteria`, and runtime now enriches the active milestone focus with those signals without needing a heavier milestone schema yet
- reflection now also persists lightweight `aion_goal_milestone_history` snapshots, so runtime can see short milestone-level movement over time instead of only the current milestone state
- reflection can now also compress short milestone histories into a semantic `goal_milestone_arc`, so runtime can distinguish closure momentum, re-entry into the completion window, recovery backslide, whiplash, or steadier closure patterns
- reflection can now also derive lightweight `goal_milestone_pressure`, so runtime can notice when a milestone is not just in a phase, but has started lingering too long in completion, recovery, execution, or setup
- reflection can now also derive lightweight `goal_milestone_dependency_state`, so runtime can tell whether the active milestone is blocked by a dependency, still depends on multiple remaining work items, is down to a single remaining dependency, or is operationally clear to close
- reflection can now also derive lightweight `goal_milestone_due_state`, so runtime can tell what is operationally due next for the active milestone, such as making the closure call, finishing the next dependency, restoring recovery momentum, or forcing the first execution move
- reflection can now also derive lightweight `goal_milestone_due_window`, so runtime can tell whether the current due window is fresh, actively in play, overdue, or reopened after recovery
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
- aion_reflection_task  
- aion_theta  
- aion_goal_progress  
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
