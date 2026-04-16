# Open Decisions

## Why This File Exists

The current repo already works as an MVP slice, but several architecture-level docs describe systems that are not implemented yet. This file keeps the next real decisions visible and tied to the current codebase.

## Active Decisions

### 1. Reflection Placeholder vs Real Reflection

- Current repo fact:
  - runtime now has a lightweight background reflection worker backed by a durable `aion_reflection_task` queue in Postgres.
  - `RuntimeResult.reflection_triggered` is returned as `True` when reflection was successfully persisted and queued after episode persistence.
  - failed reflection tasks now retry with bounded backoff inside the app process.
  - `GET /health` now exposes a lightweight reflection snapshot with worker state and queue/task counts.
- Decision needed:
  - should this app-local durable worker stay as the MVP baseline, or should reflection move into a separate external worker or scheduler before more complex consolidation is added?

### 2. Migration Strategy

- Current repo fact:
  - database tables are created automatically on startup.
- Decision needed:
  - keep bootstrap simplicity for MVP, or introduce explicit migrations before schema complexity grows?

### 3. Public API Shape

- Current repo fact:
  - `POST /event` returns the full serialized runtime result, including per-stage `stage_timings_ms` for the conscious loop.
- Decision needed:
  - should this remain a debugging-friendly internal API, or should a smaller stable public response contract be introduced?

### 4. Role Selection

- Current repo fact:
  - runtime role now uses lightweight heuristic selection (`friend`, `analyst`, `executor`, `mentor`, `advisor`), can use a reflected `preferred_role` as a tie-breaker for more ambiguous turns, and can also fall back to lightweight reflected theta bias when explicit heuristics do not decide the turn.
- Decision needed:
  - when should role selection move from heuristics into a richer module with user-state, memory, and goal-aware logic?

### 5. Memory Retrieval Depth

- Current repo fact:
  - only the latest five user memory rows are loaded.
  - persisted episodes now include lightweight `memory_kind` and `memory_topics` metadata inside the stored summary.
  - perception now emits lightweight `topic_tags`, and memory persistence reuses them before falling back to raw lexical tokens.
  - context now prefers memories tagged with the same response language as the current turn before falling back to untagged older context.
  - within that pool, context now distinguishes between `continuity` and `semantic` memory and prefers topically overlapping memories before falling back to lower-signal items.
  - for more specific requests, context now skips unrelated memory entirely instead of forcing a weak fallback; ambiguous short follow-ups can still reuse continuity memory.
  - context also now receives lightweight semantic conclusions and can include stable user preferences alongside episodic recall.
- Decision needed:
  - when to add filtering, ranking, summarization, or episodic/semantic split memory?

### 5a. Goal And Task Scope

- Current repo fact:
  - runtime now loads active goals and active tasks, includes them in the runtime result, refreshes them after Action-layer writes, lets context/motivation/planning react to them, can seed lightweight goals/tasks from explicit user phrases such as `My goal is to ...` and `I need to ...`, can update task status from explicit progress phrases such as `I fixed ...`, and reflection can now derive a lightweight semantic `goal_execution_state` like `blocked`, `recovering`, `advancing`, `progressing`, or `stagnating`, plus a lightweight `goal_progress_score` and `goal_progress_trend`; it also persists a short goal-level progress history in `aion_goal_progress`.
- Decision needed:
  - should goal and task creation stay limited to explicit user declarations for MVP, or should the system begin inferring and creating them from plans and repeated execution patterns?

### 6. Deployment Path After Coolify

- Current repo fact:
  - docs and compose files already support local Docker and Coolify.
- Decision needed:
  - is Coolify the intended production baseline, or only a temporary path until a different hosting standard is chosen?

### 7. Deployment Trigger Reliability

- Current repo fact:
  - after pushing `main`, production required a manual redeploy from Coolify before the latest commit became live.
  - a manually sent, correctly signed GitHub-style webhook request to the configured Coolify endpoint successfully queued a deployment on 2026-04-15.
- Decision needed:
  - should deploys rely on GitHub webhooks, polling, or an explicit manual release step until automation is trustworthy?
  - until GitHub-side webhook delivery is verified, should manual redeploy remain the explicit release fallback?

### 8. Language Handling Strategy

- Current repo fact:
  - runtime now makes an explicit per-event language decision, propagates it through perception and expression, stores response-language hints in episodic memory for short follow-up turns, and keeps a lightweight `aion_profile` preferred language for ambiguous turns when recent memory is not enough.
- Decision needed:
  - should language handling stay heuristic-plus-profile for the MVP, or should it move to a richer user preference model and broader multilingual support once more channels are added?

### 9. Lightweight Profile Scope

- Current repo fact:
  - runtime now persists a lightweight language preference in `aion_profile`, keeps semantic preferences in `aion_conclusion`, and builds a lightweight runtime `IdentitySnapshot` from that state plus theta.
- Decision needed:
  - should `aion_profile` remain limited to durable interaction preferences such as language, while `aion_conclusion` carries generalized learned preferences, or should those concerns merge into one wider identity-linked profile later?

### 10. Preference Influence Scope

- Current repo fact:
- stable `response_style` conclusions now influence context, planning, and expression.
- stable `preferred_role` conclusions can now influence role selection on ambiguous turns.
- stable `collaboration_preference` conclusions can now influence context, role selection, motivation, planning, and expression on ambiguous turns, and explicit user phrases like `step by step` or `do it for me` are now captured as episodic collaboration markers for reflection.
- reflected theta now provides a softer runtime bias toward support, analysis, or execution behavior without hard-overriding explicit signals, and that bias can now shape role selection, motivation mode, planning stance, and expression tone on ambiguous turns.
- Decision needed:
  - which preference types should remain expression-only, and which should be allowed to shape higher-level planning or role selection as the architecture grows?

### 11. Theta Scope And Durability

- Current repo fact:
  - reflection now updates a lightweight `aion_theta` state from repeated recent role patterns, and runtime can use that state as a soft bias for role selection, motivation, planning, and expression on ambiguous turns.
- Decision needed:
  - should theta stay as a lightweight behavioral bias derived from recent runtime patterns, or evolve into a broader long-term identity state with stronger influence over planning, motivation, expression, and proactive behavior?
