# Overview

## What This Project Is

Personality is a backend-first AION runtime implemented as a FastAPI service with PostgreSQL-backed state, an optional OpenAI reply layer, and Telegram integration.

The repository now also carries the first `v2` product baseline:

- the runtime lives under `backend/`
- `web/` exists as a real React + TypeScript + daisyUI workspace
- the backend runtime image now builds and serves the browser client for production parity
- `mobile/` exists as a reserved product surface
- backend now exposes first-party auth/session and app-facing endpoints for
  `me`, settings, chat, and personality overview

The repository already ships a real multi-stage runtime, not just a skeleton:

- `POST /event`
- `GET /health`
- `POST /telegram/set-webhook`
- `POST /app/auth/register`
- `POST /app/auth/login`
- `POST /app/auth/logout`
- `GET /app/me`
- `PATCH /app/me/settings`
- `GET /app/chat/history`
- `POST /app/chat/message`
- `GET /app/personality/overview`
- `GET /app/tools/overview`
- `PATCH /app/tools/preferences`
- `POST /app/tools/telegram/link/start`
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

For canonical stage ordering and ownership boundaries, treat
`docs/architecture/02_architecture.md`,
`docs/architecture/15_runtime_flow.md`, and
`docs/architecture/16_agent_contracts.md` as the source of truth. Older
numbered architecture docs should elaborate on that contract, not contradict
it.

## Current Runtime Shape

The implemented foreground path is:

`event -> state load -> identity -> perception -> context -> motivation -> role -> planning -> expression -> action -> memory -> reflection enqueue`

Important current-runtime notes:

- identity, profile, conclusions, theta, goals, tasks, milestones, and recent histories are loaded before deeper reasoning
- foreground stage execution from `perception` through `action` now runs through
  LangGraph while preserving current stage contracts
- role selection is dynamic and can use heuristics, reflected preferences, and theta bias
- identity continuity now keeps explicit owners: `aion_profile` is the durable
  owner for preferred language, while response/collaboration preferences remain
  conclusion-owned runtime inputs
- language is chosen per event with explicit precedence (current-turn request or
  signal first, then recent-memory/profile continuity for ambiguous turns)
- API identity fallback is request-scoped (`meta.user_id` ->
  `X-AION-User-Id` -> `anonymous`) to reduce cross-user language/profile drift
- reflection runs through a durable Postgres-backed queue and updates conclusions, theta, and lightweight goal-manager signals in the background
- `POST /event` returns a compact public response by default;
  `POST /internal/event/debug` is the primary internal debug ingress, while
  `POST /event/debug` and compatibility `POST /event?debug=true` remain
  policy-gated transitional surfaces
- first-party product clients now authenticate through backend-owned sessions
  instead of relying on `X-AION-User-Id` as their primary identity boundary
- the `web` tools screen is now a thin client over backend-owned tools truth:
  - integral capabilities such as internal chat, web search, and web browser
    are exposed as always-on product posture
  - user-owned toggles exist only where backend contracts support them
  - Telegram linking uses a backend-issued short code and Telegram-side
    confirmation instead of browser-managed provider secrets
  - once linked, normal Telegram ingress now resolves to the same backend auth
    identity owner as first-party `/app/*` traffic, so memory continuity no
    longer splits between linked web and Telegram conversations

## Runtime Stage Ownership

This map is the fast architecture-to-code traceability surface for the live runtime:

| Stage | Main code owner | Primary validation surface |
| --- | --- | --- |
| Event normalization | `app/core/events.py`, `app/api/routes.py` | `tests/test_event_normalization.py`, `tests/test_api_routes.py` |
| State load and identity | `app/core/runtime.py`, `app/identity/service.py` | `tests/test_runtime_pipeline.py` |
| Foreground graph orchestration | `app/core/runtime_graph.py`, `app/core/graph_adapters.py` | `tests/test_runtime_pipeline.py`, `tests/test_graph_stage_adapters.py`, `tests/test_graph_state_contract.py` |
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

- dynamic language-aware replies with continuity precedence across current turn,
  recent memory, and profile
- lightweight identity snapshot with explicit profile-versus-conclusion
  ownership boundary
- heuristic but state-aware role selection
- semantic preference memory
- semantic embedding contract plus pgvector-ready storage scaffolding
- hybrid memory retrieval across episodic, semantic, and affective layers
- relation persistence and reflection-driven relation updates
- relation lifecycle governance (refresh, value-shift reset, decay/revalidation,
  expiration) with trust-aware proactive/planning/expression behavior
- durable reflection with retry and health observability
- lightweight goal, task, progress, and milestone management
- migration-first startup by default with explicit compatibility fallback
- explicit expression-to-action delivery handoff in the runtime implementation
- explicit graph-compatibility boundary (`GraphRuntimeState` and stage adapters)
  around current stage modules, preparing incremental LangGraph migration
- LangGraph foreground orchestration now active for `perception -> ... -> action`
- scheduler event normalization/cadence contracts in runtime and config
- owner-aware scheduler cadence posture (`in_process|externalized`) with
  maintenance/proactive owner and dispatch visibility in `/health.scheduler`
- proactive scheduler decision engine with interruption-cost guardrails and
  typed proactive planning/motivation outputs
- proactive delivery guardrails with opt-in, throttle limits, and delivery-target
  checks before outreach
- explicit attention inbox and proposal-handoff runtime-state contracts
- attention coordination owner posture (`in_process|durable_inbox`) with
  readiness/blocker visibility in `/health.attention`
- subconscious proposal persistence with conscious handoff resolution and
  read-only research/tool policy boundaries
- proactive scheduler attention-gate checks before delivery planning
- connector capability and permission-gate planning contracts with typed
  calendar/task/drive synchronization intents

What is still planned or intentionally deferred:

- provider-owned embedding strategy and retrieval tuning beyond deterministic fallback
- finishing migration leftovers around orchestration boundaries
- separate reflection worker process
- provider-backed execution adapters for calendar/task/drive connectors
- connector capability-expansion proposals

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
