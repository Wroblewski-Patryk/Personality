# Open Decisions

## Why This File Exists

The current repo already works as an MVP slice, but several architecture-level docs describe systems that are not implemented yet. This file keeps the next real decisions visible and tied to the current codebase.

## Active Decisions

### 1. Reflection Placeholder vs Real Reflection

- Current repo fact:
  - `RuntimeResult.reflection_triggered` is now returned as `False`.
- Decision needed:
  - should reflection become a real stage, a background worker, or should the field be removed until it becomes real behavior?

### 2. Migration Strategy

- Current repo fact:
  - database tables are created automatically on startup.
- Decision needed:
  - keep bootstrap simplicity for MVP, or introduce explicit migrations before schema complexity grows?

### 3. Public API Shape

- Current repo fact:
  - `POST /event` returns the full serialized runtime result.
- Decision needed:
  - should this remain a debugging-friendly internal API, or should a smaller stable public response contract be introduced?

### 4. Role Selection

- Current repo fact:
  - runtime role now uses lightweight heuristic selection (`friend`, `analyst`, `executor`, `mentor`, `advisor`) instead of a hardcoded `advisor`.
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
- Decision needed:
  - when to add filtering, ranking, summarization, or episodic/semantic split memory?

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
  - runtime now persists a lightweight language preference in `aion_profile`, but no broader stable user preferences or semantic conclusions are stored yet.
- Decision needed:
  - should `aion_profile` remain limited to durable interaction preferences such as language and response style, or should it evolve into a wider identity-linked profile alongside future `aion_conclusions`?
