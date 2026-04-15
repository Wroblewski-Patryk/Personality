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
