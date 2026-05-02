# Codebase Map

Last updated: 2026-05-03

This map describes the current repository structure verified from code. It is a
navigation aid, not a replacement for the canonical architecture.

## Topology

| Area | Path | Responsibility |
| --- | --- | --- |
| Backend runtime | `backend/app/` | FastAPI app, AION runtime stages, policies, persistence, integrations, workers |
| Backend tests | `backend/tests/` | Unit, integration, route, policy, runtime, schema, and script tests |
| Backend migrations | `backend/migrations/` | Alembic migration environment and versioned schema changes |
| Backend scripts | `backend/scripts/` | Operator and validation entrypoints |
| Web shell | `web/src/` | React/Vite browser client, route rendering, API client, styling |
| Mobile | `mobile/` | Reserved product surface |
| Deployment | `docker-compose.yml`, `docker-compose.coolify.yml`, `docker/` | Local and Coolify/container deployment shape |
| Docs and context | `docs/`, `.codex/`, `.agents/` | Source of truth, task contracts, workflows, handoffs |

## Backend Modules

| Module | Verified Files | Responsibility |
| --- | --- | --- |
| API | `backend/app/api/routes.py`, `backend/app/api/schemas.py`, `backend/app/api/health_response.py` | HTTP endpoints, app auth/session routes, debug/event ingress, Telegram webhook setup, response schemas |
| Core runtime | `backend/app/core/runtime.py`, `backend/app/core/runtime_graph.py`, `backend/app/core/contracts.py`, `backend/app/core/graph_state.py`, `backend/app/core/graph_adapters.py` | Foreground runtime orchestration and stage contract flow |
| Core policies | `backend/app/core/*_policy.py`, `backend/app/core/*_governance.py`, `backend/app/core/*_catalog.py` | Machine-visible runtime policy, readiness, deployment, connector, retrieval, proactive, observability, and authorization truth |
| Agents | `backend/app/agents/perception.py`, `context.py`, `planning.py`, `role.py` | Stage-specific reasoning and planning owners |
| Affective | `backend/app/affective/assessor.py` | Affective assessment with deterministic fallback and optional AI classification |
| Motivation | `backend/app/motivation/engine.py` | Motivation mode and support/execution weighting |
| Expression | `backend/app/expression/generator.py` | User-facing response generation and communication preference handling |
| Action | `backend/app/core/action.py`, `backend/app/core/action_delivery.py` | Side-effect boundary and delivery result shaping |
| Memory | `backend/app/memory/models.py`, `repository.py`, `episodic.py`, `embeddings.py`, `openai_embedding_client.py`, `vector_types.py` | SQLAlchemy models, repository API, episodic payloads, retrieval/embedding support |
| Reflection | `backend/app/reflection/*.py` | Deferred reflection, relation/affective/adaptive signals, proposals, goal conclusions |
| Proactive | `backend/app/proactive/engine.py` | Proactive candidate generation and delivery rules |
| Communication | `backend/app/communication/*.py` | Communication boundary and behavior feedback interpretation |
| Identity | `backend/app/identity/service.py` | Identity facts and foreground capability truth |
| Integrations | `backend/app/integrations/**` | Telegram, ClickUp, Google Calendar, Google Drive, OpenAI, DuckDuckGo, generic HTTP/web browser, delivery router |
| Workers | `backend/app/workers/scheduler.py` | Scheduler-owned maintenance/proactive execution entrypoints |
| Utils | `backend/app/utils/*.py` | Shared language, preferences, UTC offset, goal/task ranking and progress helpers |

## Routes And Endpoints

Verified in `backend/app/api/routes.py`.
See [API Reference](../api/index.md) for endpoint auth posture, schemas, side
effects, frontend callers, tests, and related pipelines.

| Endpoint | Purpose | Primary Consumers |
| --- | --- | --- |
| `GET /health` | Runtime, release, deployment, connector, Telegram, retrieval, observability, and readiness snapshot | Operators, release smoke, web shell health panels |
| `POST /app/auth/register` | First-party app registration | `web/src/lib/api.ts` |
| `POST /app/auth/login` | First-party app login | `web/src/lib/api.ts` |
| `POST /app/auth/logout` | Session logout | `web/src/lib/api.ts` |
| `GET /app/me` | Current app user and settings | `web/src/lib/api.ts` |
| `PATCH /app/me/settings` | Profile, UI language, UTC offset, proactive settings | `web/src/lib/api.ts` |
| `POST /app/me/reset-data` | User-owned data reset | `web/src/lib/api.ts` |
| `GET /app/chat/history` | Durable app transcript projection | `web/src/lib/api.ts` |
| `POST /app/chat/message` | Authenticated app chat ingress | `web/src/lib/api.ts` |
| `GET /app/personality/overview` | Learned-state/personality overview and recent activity | `web/src/lib/api.ts` |
| `GET /app/tools/overview` | Tool/channel readiness and user controls | `web/src/lib/api.ts` |
| `PATCH /app/tools/preferences` | Tool enablement preferences | `web/src/lib/api.ts` |
| `POST /app/tools/telegram/link/start` | Telegram linking code start | `web/src/lib/api.ts` |
| `GET /internal/state/inspect` | Internal learned-state inspection | Operator/internal use |
| `POST /event` | General event ingress | API clients and transports |
| `POST /event/debug` | Shared debug event ingress | Debug/compat users |
| `POST /internal/event/debug` | Dedicated internal debug ingress | Operator/debug tooling |
| `POST /telegram/set-webhook` | Telegram webhook registration | Operator tooling |

## Database Models

Verified in `backend/app/memory/models.py`.
See [Data Model Reference](../data/index.md) for table ownership, migration
timeline, repository capability groups, feature usage, and validation ownership.

| Model | Table | Primary Use |
| --- | --- | --- |
| `AionMemory` | `aion_memory` | Episodic memory, transcript projection source, event summaries |
| `AionSemanticEmbedding` | `aion_semantic_embedding` | Retrieval materialization and vector-backed semantic search |
| `AionProfile` | `aion_profile` | User language, UI language, UTC offset, Telegram link/profile fields |
| `AionConclusion` | `aion_conclusion` | Scoped conclusions and runtime preferences |
| `AionAuthUser` | `aion_auth_user` | First-party app user account |
| `AionAuthSession` | `aion_auth_session` | First-party session token state |
| `AionRelation` | `aion_relation` | Durable relation/communication preference truth |
| `AionTheta` | `aion_theta` | Support/analysis/execution bias state |
| `AionGoal` | `aion_goal` | Goal state |
| `AionTask` | `aion_task` | Task state |
| `AionPlannedWorkItem` | `aion_planned_work_item` | Time-aware planned work and foreground handoff |
| `AionGoalProgress` | `aion_goal_progress` | Goal progress snapshots |
| `AionGoalMilestone` | `aion_goal_milestone` | Active milestone state |
| `AionGoalMilestoneHistory` | `aion_goal_milestone_history` | Milestone history/evidence |
| `AionAttentionTurn` | `aion_attention_turn` | Durable attention inbox/turn assembly |
| `AionReflectionTask` | `aion_reflection_task` | Deferred reflection queue |
| `AionSchedulerCadenceEvidence` | `aion_scheduler_cadence_evidence` | Scheduler cadence evidence |
| `AionSubconsciousProposal` | `aion_subconscious_proposal` | Subconscious proposal queue and decisions |

## Migrations

Migration ownership lives under `backend/migrations/versions/`. Current latest
verified revision in planning/context is `20260426_0012`.
See [Data Model Reference](../data/index.md#migration-timeline) for the current
first-pass migration timeline.

## Frontend Modules

| Path | Responsibility |
| --- | --- |
| `web/src/App.tsx` | Authenticated/public shell, routes, UI copy, route components, chat rendering, settings, tools, personality overview, health-derived panels |
| `web/src/lib/api.ts` | Typed fetch client for app auth, settings, reset, chat, personality, tools, Telegram link, and health endpoints |
| `web/src/index.css` | Shared visual system, layout, route styling, responsive behavior |
| `web/src/main.tsx` | React app bootstrap |

Frontend component ownership is currently mostly inside `web/src/App.tsx`.
Per-component docs below that level are a GAP.

## Background Jobs And Queues

| Area | Files | Data |
| --- | --- | --- |
| Deferred reflection | `backend/app/reflection/worker.py`, `backend/app/core/reflection_supervision_policy.py`, `backend/scripts/run_reflection_queue_once.*` | `AionReflectionTask`, memory/conclusion/relation tables |
| Scheduler cadence | `backend/app/workers/scheduler.py`, `backend/app/core/external_scheduler_policy.py`, `backend/scripts/run_maintenance_tick_once.*`, `backend/scripts/run_proactive_tick_once.*` | `AionSchedulerCadenceEvidence`, memory, planned work |
| Durable attention | `backend/app/core/attention.py`, `backend/app/core/attention_gate.py` | `AionAttentionTurn` |
| Planned work observer | `backend/app/core/planned_action_observer.py`, `backend/app/proactive/engine.py` | `AionPlannedWorkItem`, proposals, memory |

## Integrations

| Integration | Files | Status From Code Shape |
| --- | --- | --- |
| Telegram | `backend/app/integrations/telegram/client.py`, `telemetry.py`, `backend/app/integrations/delivery_router.py` | Provider-backed when env is configured |
| ClickUp | `backend/app/integrations/task_system/clickup_client.py` | Task-system create/list path when configured |
| Google Calendar | `backend/app/integrations/calendar/google_calendar_client.py` | Policy/client path exists; readiness depends on config and approved scope |
| Google Drive | `backend/app/integrations/cloud_drive/google_drive_client.py` | Policy/client path exists; readiness depends on config and approved scope |
| OpenAI | `backend/app/integrations/openai/client.py`, `prompting.py` | Optional model/embedding/classification support |
| Web/HTTP reading | `backend/app/integrations/web_browser/generic_http_client.py`, `backend/app/integrations/knowledge_search/duckduckgo_client.py` | Bounded read/search capability support |

## Deployment And Runtime

- App entrypoint: `backend/app/main.py`.
- Backend package config: `backend/pyproject.toml`.
- Alembic config: `backend/alembic.ini`.
- Local compose: `docker-compose.yml`.
- Coolify compose: `docker-compose.coolify.yml`.
- Primary operator scripts: `backend/scripts/*.ps1` and paired `.py`/`.sh`
  where available.

## Test Structure

Tests live under `backend/tests/` and map mostly by module name:

- API/routes: `test_api_routes.py`, `test_web_routes.py`.
- Runtime pipeline and graph: `test_runtime_pipeline.py`,
  `test_graph_stage_adapters.py`, `test_graph_state_contract.py`.
- Stage agents: `test_context_agent.py`, `test_planning_agent.py`,
  `test_role_agent.py`, `test_motivation_engine.py`,
  `test_expression_agent.py`, `test_affective_assessor.py`.
- Memory/data: `test_memory_repository.py`, `test_schema_baseline.py`,
  `test_embedding_strategy.py`.
- Workers/policies: `test_scheduler_worker.py`,
  `test_reflection_worker.py`, `test_reflection_supervision_policy.py`,
  `test_runtime_policy.py`.
- Integrations/scripts/ops: `test_telegram_client.py`,
  `test_connector_policy.py`, `test_deployment_trigger_scripts.py`,
  `test_incident_evidence_bundle_script.py`.
