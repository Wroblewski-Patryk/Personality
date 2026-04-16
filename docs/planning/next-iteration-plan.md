# Next Iteration Plan

## Purpose

This document turns the current repo state into an executable next-step plan.

It is intentionally narrower than the long-term architecture docs and focuses on the next meaningful improvement to the live MVP runtime.

## Current Baseline

As of 2026-04-15, the repo already provides:

- `POST /event`, `GET /health`, and `POST /telegram/set-webhook`
- event normalization with `event_id` and `trace_id`
- an in-process runtime pipeline
- PostgreSQL-backed memory persistence
- lightweight recent-memory loading before context construction
- local Docker and documented Coolify deployment path

Important implementation limits that shape this plan:

- memory retrieval is still heuristic and bounded to a small recent window plus lightweight semantic conclusions
- role selection is still heuristic rather than user-state or goal-aware
- reflection now exists as a lightweight in-process worker, not yet as a durable external subsystem
- startup schema creation exists, but migrations do not

## Iteration Goal

Deliver a more memory-aware and operationally honest runtime without jumping ahead to full autonomous systems.

The target outcome is:

- memory affects context in a useful way
- runtime output stops claiming behavior that is not real
- deployment verification is ready for Coolify once access is available

## Primary Scope

### 1. Make Memory Retrieval Actually Useful

Goal:
- move from "memory count" to "memory-informed context"

Tasks:
- review the current `MemoryRepository.get_recent_for_user()` contract
- decide the minimum useful memory payload for context, for example summaries, timestamps, and importance
- update `ContextAgent` so it turns recent memory into a short contextual summary instead of only reporting the count
- keep the first version heuristic and deterministic; do not add semantic search yet
- add tests that prove memory changes the produced context

Success criteria:
- runtime context contains meaningful memory-derived signal
- behavior is deterministic and covered by tests

### 2. Make Runtime Contracts More Honest

Goal:
- align runtime fields with implemented behavior

Tasks:
- resolve the `reflection_triggered` placeholder by either setting it truthfully, making it optional, or removing it from the public result
- confirm whether `POST /event` should remain a debug-heavy internal response or move toward a smaller stable response contract
- document the chosen direction in `docs/planning/open-decisions.md` or promote the decision into a more stable doc once implemented

Success criteria:
- API no longer implies reflection exists when it does not
- response shape has a deliberate owner and rationale

### 3. Strengthen Change Safety Around Runtime And Memory

Goal:
- reduce the chance of silent regressions while the runtime grows

Tasks:
- add focused tests for memory-aware context behavior
- add or extend endpoint-level tests if the `/event` response contract changes
- keep the lightweight full-suite `pytest` run as the baseline gate for each runtime change

Success criteria:
- runtime and API changes leave behind direct automated evidence

## Explicit Non-Goals For This Iteration

Do not pull these into the same implementation slice unless something unexpectedly depends on them:

- full role selection logic
- subconscious loop or background worker system
- semantic memory retrieval or embeddings
- proactive behavior
- full migration framework rollout
- frontend or admin console work

## Recommended Execution Order

1. Implement memory-aware context shaping in the smallest useful form.
2. Add or update tests that lock in the new behavior.
3. Resolve the misleading `reflection_triggered` contract.
4. Re-check whether the `/event` response should stay verbose after the runtime contract cleanup.
5. Prepare deployment verification steps for the already-documented Coolify path.

## Definition Of Done

This iteration is done when:

- recent memory changes `ContextOutput.summary` in a way that is actually informative
- tests cover the new behavior and pass locally
- runtime result fields do not claim non-existent reflection behavior
- docs reflect the new contract and current repo truth
- deployment smoke-test tasks are ready to execute once infrastructure access is available

## Follow-Ups Discovered During Production Verification

These are small but real issues observed after the production rollout and smoke tests.

### 1. Memory Summary Truncation Quality

- current repo behavior now clips recent-memory summaries on sentence or word boundaries
- next improvement:
  - watch production behavior and decide whether memory summaries should also rank fields by usefulness or importance

### 2. Coolify Auto-Deploy Reliability

- current production behavior required a manual Coolify redeploy after pushing `main`
- next improvement:
  - verify GitHub repository webhook presence and recent deliveries
  - confirm the configured secret on GitHub matches the Coolify secret `codex-webhook-2026`
  - note: a manually sent, correctly signed GitHub-style `push` event to the Coolify endpoint successfully queued a deployment on 2026-04-15, so the remaining issue appears to be on the GitHub webhook configuration or delivery side

### 3. Runtime Language Coverage

- current repo behavior selects a response language per event, carries it through runtime, persists language hints in memory for ambiguous follow-up turns, and now stores a lightweight preferred language in `aion_profile` for ambiguous turns without useful recent memory
- next improvement:
  - expand beyond keyword heuristics if real traffic shows mixed-language or multilingual false positives
  - decide whether language preference should remain event-driven plus profile fallback, or become a stronger user-level contract once more channels are added

### 4. Memory Retrieval Ranking

- current repo behavior stores lightweight `memory_kind` and `memory_topics` markers, perception emits lightweight `topic_tags`, retrieval prefers memories tagged with the same response language as the current turn before ranking them by mode match, topical overlap, importance, and recency, and context now also adds stable semantic preference conclusions when they are available
- next improvement:
  - decide whether lightweight in-summary metadata is enough for MVP, or whether `memory_kind` and topic fields should become explicit columns before retrieval grows further
  - decide whether `topic_tags` should stay heuristic or become a richer perception artifact with explicit entities/intents
  - consider splitting "conversation continuity" memory from "semantic recall" memory more formally once retrieval grows beyond the latest five rows
  - watch production behavior around short acknowledgements versus specific requests, so continuity memory helps only when it adds signal instead of noise
  - decide when semantic conclusions should be ranked or filtered by topical relevance instead of being injected as always-on stable preferences

### 6. Lightweight Profile Memory

- current repo behavior keeps a small `aion_profile` table with preferred language updated only from explicit or higher-confidence language signals, so weak fallbacks do not reinforce themselves
- next improvement:
  - decide whether stable preferences such as tone or channel habits belong in the same profile state
  - decide when durable profile updates should move from synchronous action-time writes into a more reflective conclusion/consolidation path

### 7. Semantic Conclusion Memory

- current repo behavior now keeps lightweight `aion_conclusion` records for semantic preferences such as `response_style`, `preferred_role`, and `collaboration_preference`; expression uses response-style preferences in both fallback generation and OpenAI prompting, context retrieval includes stable preferences in the runtime summary, planning turns response-style preferences into explicit response-shaping steps such as `keep_response_concise` or `format_response_as_bullets`, role selection can use `preferred_role` as a tie-breaker on ambiguous turns, and `collaboration_preference` can now shape role selection, motivation, planning, and expression toward a more guided or more hands-on collaboration style
- current repo behavior also persists explicit collaboration markers in episodic memory when the user directly asks for guidance like `step by step` or for delegation like `do it for me`, so background reflection can learn `collaboration_preference` immediately instead of relying only on repeated-pattern heuristics
- next improvement:
  - widen conclusion memory beyond explicit requests into repeated-pattern learning once there is enough traffic signal
  - decide whether conclusions should start carrying supporting memory ids and richer provenance before the subconscious loop exists
  - decide which future preference types should be allowed to influence role selection versus staying lower in the stack
  - decide whether collaboration preference should also shape action selection more directly

### 8. Background Reflection Worker

- current repo behavior now has a lightweight reflection worker backed by durable `aion_reflection_task` rows; it runs after episode persistence, updates semantic conclusions asynchronously, recovers pending work on startup, retries failed jobs with bounded backoff, and sets `reflection_triggered=true` when the task is durably persisted and queued
- current repo behavior also exposes lightweight queue observability through `GET /health`, including worker status plus pending, failed, retryable, exhausted, and stuck-task counts
- next improvement:
  - move beyond explicit `preference_update` markers and infer stable conclusions from repeated behavioral patterns
  - decide whether the current app-local durable queue is enough for MVP or whether reflection should move into a separate worker process before more complex jobs exist
  - decide whether retry policy should become configurable beyond the current built-in worker defaults once reflection handles more than lightweight consolidation
  - decide whether health-level observability is enough, or whether a dedicated internal ops endpoint should expose richer reflection task detail
  - decide when reflection should stay limited to `aion_conclusion` plus lightweight `aion_theta`, versus growing into richer future artifacts like goals or stronger role heuristics

### 9. Theta Runtime Bias

- current repo behavior now stores lightweight theta state in `aion_theta`; reflection derives soft `support`, `analysis`, and `execution` biases from repeated recent role usage, and ambiguous runtime behavior can use theta after explicit heuristics and `preferred_role`, including role selection, motivation mode choice, lightweight planning stance, and expression tone
- next improvement:
  - decide whether theta should stay as a soft nudge, or start influencing downstream action selection more directly
  - decide whether theta should stay recency-driven or accumulate over a longer user history
  - decide when theta deserves richer provenance and decay rules instead of simple overwrite updates

### 5. UTF-8 Smoke Test Reliability

- current production behavior is fine, but a manual PowerShell smoke request on Windows mangled Polish diacritics in the submitted payload during verification on 2026-04-15
- next improvement:
  - harden local verification snippets and helper scripts so production smoke tests preserve UTF-8 payloads end to end

## Tasks Waiting For Coolify / VPS Access

These tasks do not block local development, but they do require actual infrastructure access.

### Coolify Application Setup

- create or verify the Coolify application that points at this repository
- select `docker-compose.coolify.yml` as the deployment definition
- verify the correct branch and auto-deploy behavior

### Production Environment Configuration

- set or verify production env vars in Coolify:
  - `APP_ENV`
  - `APP_PORT`
  - `LOG_LEVEL`
  - `DATABASE_URL` if an external database is used
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_WEBHOOK_SECRET`
- confirm whether Postgres is bundled in Coolify for this app or managed separately

### First Production Deploy

- trigger a deploy from Coolify
- inspect build logs and container health
- verify `GET /health` on the production domain
- confirm the app can connect to the configured database

### Telegram Production Verification

- configure the production webhook against the final domain
- verify the secret-token validation path
- send a real Telegram message and confirm:
  - request reaches `/event`
  - runtime completes successfully
  - reply is delivered
  - memory row is persisted

### Ops Validation

- inspect runtime logs for `event_id`, `trace_id`, action status, and errors
- verify fallback behavior if OpenAI is unavailable or rate-limited
- record any production-only gaps discovered during deploy or first live traffic

## Suggested Immediate Next Task

Start with the smallest high-value slice:

- upgrade `ContextAgent` so it summarizes recent memory into the context output
- add tests that prove the summary changes when memory exists

That gives the MVP its next real capability jump without violating the current roadmap.
