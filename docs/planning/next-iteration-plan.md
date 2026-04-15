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

- memory retrieval only contributes a count-based hint to context
- role selection is still hardcoded to `advisor`
- `reflection_triggered` is returned as `True` even though reflection is not implemented
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
  - decide whether profile state should also remember response-style preferences once the runtime starts observing stronger user-specific patterns

### 4. Memory Retrieval Ranking

- current repo behavior stores lightweight `memory_kind` and `memory_topics` markers, perception emits lightweight `topic_tags`, and retrieval prefers memories tagged with the same response language as the current turn before ranking them by mode match, topical overlap, importance, and recency
- next improvement:
  - decide whether lightweight in-summary metadata is enough for MVP, or whether `memory_kind` and topic fields should become explicit columns before retrieval grows further
  - decide whether `topic_tags` should stay heuristic or become a richer perception artifact with explicit entities/intents
  - consider splitting "conversation continuity" memory from "semantic recall" memory more formally once retrieval grows beyond the latest five rows
  - watch production behavior around short acknowledgements versus specific requests, so continuity memory helps only when it adds signal instead of noise

### 6. Lightweight Profile Memory

- current repo behavior keeps a small `aion_profile` table with preferred language updated only from explicit or higher-confidence language signals, so weak fallbacks do not reinforce themselves
- next improvement:
  - decide whether stable preferences such as response length, tone, or channel habits belong in the same profile state
  - decide when durable profile updates should move from synchronous action-time writes into a more reflective conclusion/consolidation path

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
