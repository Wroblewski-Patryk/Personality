# Overview

## What This Project Is

Personality is a backend-first AION runtime implemented as a FastAPI service with PostgreSQL-backed state, an optional OpenAI reply layer, and Telegram integration.

The repository already ships a real multi-stage runtime, not just a skeleton:

- `POST /event`
- `GET /health`
- `POST /telegram/set-webhook`
- event normalization for API and Telegram payloads
- conscious-loop orchestration with structured stage outputs
- episodic memory persistence plus lightweight semantic conclusions
- durable in-app reflection queue with health visibility
- lightweight goal, task, progress, and milestone state

## Canonical vs Implemented

The documentation is intentionally split into two layers:

- `docs/architecture/` defines the canonical AION architecture and human-oriented cognitive flow
- `docs/implementation/runtime-reality.md` describes the current implementation and transitional runtime wiring

When those layers differ, the difference must be explicit rather than hidden.

## Current Runtime Shape

The implemented foreground path is:

`event -> state load -> identity -> perception -> context -> motivation -> role -> planning -> expression -> action -> memory -> reflection enqueue`

Important current-runtime notes:

- identity, profile, conclusions, theta, goals, tasks, milestones, and recent histories are loaded before deeper reasoning
- role selection is dynamic and can use heuristics, reflected preferences, and theta bias
- language is chosen per event and can fall back to recent memory or profile state for ambiguous turns
- reflection runs through a durable Postgres-backed queue and updates conclusions, theta, and lightweight goal-manager signals in the background
- `POST /event` returns a compact public response by default; `debug=true` is policy-gated

## Runtime Stage Ownership

This map is the fast architecture-to-code traceability surface for the live runtime:

| Stage | Main code owner | Primary validation surface |
| --- | --- | --- |
| Event normalization | `app/core/events.py`, `app/api/routes.py` | `tests/test_event_normalization.py`, `tests/test_api_routes.py` |
| State load and identity | `app/core/runtime.py`, `app/identity/service.py` | `tests/test_runtime_pipeline.py` |
| Perception | `app/agents/perception.py` | `tests/test_perception_agent.py`, `tests/test_runtime_pipeline.py` |
| Context | `app/agents/context.py` | `tests/test_context_agent.py`, `tests/test_runtime_pipeline.py` |
| Motivation | `app/motivation/engine.py` | `tests/test_motivation_engine.py`, `tests/test_runtime_pipeline.py` |
| Role | `app/agents/role.py` | `tests/test_role_agent.py`, `tests/test_runtime_pipeline.py` |
| Planning | `app/agents/planning.py` | `tests/test_planning_agent.py`, `tests/test_runtime_pipeline.py` |
| Expression | `app/expression/generator.py` | `tests/test_expression_agent.py`, `tests/test_runtime_pipeline.py` |
| Action delivery and side effects | `app/core/runtime.py`, `app/core/action.py`, `app/integrations/delivery_router.py` | `tests/test_action_executor.py`, `tests/test_delivery_router.py`, `tests/test_runtime_pipeline.py`, `tests/test_api_routes.py` |
| Memory persistence | `app/core/action.py`, `app/memory/repository.py` | `tests/test_action_executor.py`, `tests/test_memory_repository.py` |
| Reflection enqueue and worker flow | `app/core/runtime.py`, `app/reflection/worker.py`, `app/memory/repository.py` | `tests/test_reflection_worker.py`, `tests/test_api_routes.py`, `tests/test_runtime_pipeline.py` |

## Current vs Planned

What is already live:

- dynamic language-aware replies
- lightweight identity snapshot
- heuristic but state-aware role selection
- semantic preference memory
- durable reflection with retry and health observability
- lightweight goal, task, progress, and milestone management
- migration-first startup by default with explicit compatibility fallback
- explicit expression-to-action delivery handoff in the runtime implementation

What is still planned or intentionally deferred:

- vector retrieval or embeddings
- external orchestration layer
- separate reflection worker process
- proactive loops, richer relation systems, and fuller autonomous behavior
- attention inbox and burst-message turn assembly for rapid conversation
  handling
- subconscious proposal handoff and explicit proactive attention gating
- user-authorized productivity connectors such as calendar, task systems, and
  cloud drives

Near-term planning now also makes two coordination boundaries explicit:

- internal goals/tasks remain integral planning state of the personality
- external productivity systems are future authorized connector surfaces rather
  than replacements for internal planning state

## Documentation Intent

Use the docs in layers:

- `docs/architecture/` for canonical design
- `docs/implementation/` for live runtime reality and transition notes
- `docs/operations/` for deployment and operator truth
- `docs/planning/` for next decisions and slices
- `.codex/context/` for execution queue and project-state truth

## Links

- Canonical architecture: `docs/architecture/02_architecture.md`
- Canonical runtime flow: `docs/architecture/15_runtime_flow.md`
- Canonical agent contracts: `docs/architecture/16_agent_contracts.md`
- Runtime reality: `docs/implementation/runtime-reality.md`
- Logging and debugging: `docs/architecture/17_logging_and_debugging.md`
- Environment/config: `docs/architecture/26_env_and_config.md`
- Runtime operations: `docs/operations/runtime-ops-runbook.md`
- Open decisions: `docs/planning/open-decisions.md`
- Next implementation slices: `docs/planning/next-iteration-plan.md`
