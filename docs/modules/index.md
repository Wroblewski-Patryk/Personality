# Module Registry

Last updated: 2026-05-03

This registry gives each major module an engineering ownership summary. It is
not exhaustive API documentation; use it to find the right code owner and
traceable pipeline.

## Backend Modules

| Module | Responsibility | Public Interface | Key Dependencies | Used By Pipelines | Related Routes | Related Models | Related Tests | Known Gaps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `backend/app/api` | HTTP boundary, app auth, event/debug ingress, health, app-facing schemas | FastAPI router in `routes.py`, Pydantic schemas in `schemas.py` | Runtime, memory repository, settings, Telegram, workers, policies | Auth, settings, chat, event ingress, tools, health, debug | All routes in codebase map | Many, via repository | `test_api_routes.py`, `test_web_routes.py` | Dedicated API reference missing |
| `backend/app/core/runtime.py` | Runtime orchestrator and post-graph followups | `RuntimeOrchestrator.run(event)` | Stage agents, graph runner, repository, workers, policies | Foreground runtime, app chat, event ingress | `/event`, `/app/chat/message`, debug ingress | Memory, profile, conclusions, relations, tasks, reflection queue | `test_runtime_pipeline.py` | Deep sequence diagram missing |
| `backend/app/core/runtime_graph.py` | Foreground stage graph execution | `ForegroundLangGraphRunner.run(...)` | Graph adapters/state, stage agents | Foreground runtime | Runtime-owned routes only | Runtime state models/contracts | `test_graph_stage_adapters.py`, `test_graph_state_contract.py` | Per-node input/output doc missing |
| `backend/app/core/contracts.py` | Shared runtime domain contracts | Pydantic/domain models | Stage modules | Foreground runtime, API schemas | Event/debug responses indirectly | None directly | `test_semantic_contracts.py`, runtime tests | Contract reference missing |
| `backend/app/core/*_policy.py` | Runtime/deployment/connector/retrieval/proactive/debug/readiness policy owners | Snapshot functions and constants | Settings, health, runtime state | Health, release smoke, debug evidence | `/health`, debug routes | Usually read-only | Policy-specific tests | Policy index missing |
| `backend/app/agents` | Perception, context, role, planning stages | Stage classes/functions | Contracts, utilities, memory bundles | Foreground runtime | Runtime-owned routes only | Reads runtime-loaded state | `test_context_agent.py`, `test_planning_agent.py`, `test_role_agent.py` | Individual stage docs missing |
| `backend/app/affective` | Affective assessment | `AffectiveAssessor` | OpenAI client optional fallback | Foreground runtime | Runtime-owned routes only | Episodic affective fields | `test_affective_assessor.py`, `test_affective_contract.py` | Classifier prompt/config doc missing |
| `backend/app/motivation` | Motivation scoring and mode | Motivation engine | Affective/context state | Foreground runtime | Runtime-owned routes only | Reads conclusions/relations indirectly | `test_motivation_engine.py` | None for first map |
| `backend/app/expression` | User-facing response generation | Expression generator | Role, motivation, planning, memory/preferences | Foreground runtime, chat, Telegram delivery | Runtime-owned routes only | Memory/preferences indirectly | `test_expression_agent.py` | Prompt contract details are distributed |
| `backend/app/memory` | SQLAlchemy models, repository, episodic memory, embeddings | `MemoryRepository`, ORM models | SQLAlchemy, config, vector type, OpenAI embeddings optional | Runtime, reflection, retrieval, app overview, auth/settings | Many app/runtime routes | All `Aion*` tables | `test_memory_repository.py`, `test_schema_baseline.py`, `test_embedding_strategy.py` | Data/model reference missing |
| `backend/app/reflection` | Deferred reflection and signal extraction | `ReflectionWorker`, signal modules | Memory repository, policies, episodic payloads | Deferred reflection | Worker/script triggered | Reflection queue, memory, conclusions, relations, progress, proposals | `test_reflection_worker.py`, supervision tests | Per-signal docs missing |
| `backend/app/workers` | Scheduler execution | `SchedulerWorker` | Memory repository, proactive engine, policies | Scheduler/proactive cadence | Health/script paths | Scheduler evidence, planned work, memory | `test_scheduler_worker.py` | External scheduler runbook depth lives in ops docs |
| `backend/app/proactive` | Proactive candidate and delivery decisions | Proactive engine | Memory, communication boundary, policies | Scheduler/proactive cadence | Indirect through runtime/delivery | Memory, planned work, proposals | `test_scheduler_worker.py`, runtime tests | Dedicated proactive pipeline doc missing |
| `backend/app/communication` | Communication boundary and behavior feedback | Boundary/feedback helpers | Memory/reflection/expression consumers | Runtime, reflection, proactive | Indirect | Relations, memory payloads | `test_communication_boundary.py` | State family reference missing |
| `backend/app/identity` | Identity facts and foreground capability truth | Identity service | Memory/preferences/runtime state | Foreground runtime | Indirect | Profile/conclusions | `test_identity_service.py` | None for first map |
| `backend/app/integrations` | External providers and delivery router | Provider clients, delivery router | Settings, HTTP clients, provider APIs | Tools, action delivery, Telegram, retrieval, web reading | `/telegram/set-webhook`, runtime action paths | Profile/memory depending on flow | `test_telegram_client.py`, `test_delivery_router.py`, `test_connector_policy.py` | Provider-specific docs incomplete |
| `backend/app/utils` | Shared helpers | Language, preference, UTC, goal/task ranking helpers | Standard library, contracts | Runtime, settings, reflection | Indirect | None directly | `test_goal_task_signals.py`, `test_preferences.py` | Helper docs not needed unless API expands |

## Frontend Modules

| Module | Responsibility | Public Interface | Key Dependencies | Used By Pipelines | Related Routes | Related Tests | Known Gaps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `web/src/App.tsx` | Public/authenticated shell, route rendering, UI copy, local state, chat markdown, settings/tools/personality surfaces | React default export | `web/src/lib/api.ts`, CSS, assets | Web shell, auth, settings, chat, tools, personality | Browser routes: `/`, `/login`, `/dashboard`, `/chat`, `/personality`, `/settings`, `/tools`, module routes | Build evidence in task records; backend `test_web_routes.py` | Large file; component-level docs/tests missing |
| `web/src/lib/api.ts` | Typed app API fetch client | exported `api` object and response types | Browser fetch | Auth, settings, chat, tools, health | App-facing backend routes | Build/type checks in task records | No generated OpenAPI/type sync |
| `web/src/index.css` | Visual system and responsive styling | CSS classes | App component markup/assets | Web shell route rendering | Browser routes | Screenshot/build task evidence | Existing local dirty change was not touched in PRJ-937 |
| `web/src/main.tsx` | React bootstrap | app mount | React/Vite | Web shell | All web routes | Build evidence | None |

## Data And Migration Modules

| Module | Responsibility | Public Interface | Dependencies | Tests | Known Gaps |
| --- | --- | --- | --- | --- | --- |
| `backend/app/memory/models.py` | ORM table definitions | SQLAlchemy models | SQLAlchemy, vector type | `test_schema_baseline.py`, repository tests | Column-by-column reference missing |
| `backend/migrations/versions` | Versioned schema changes | Alembic revisions | Alembic | `test_schema_baseline.py`, migration commands in task evidence | Migration-to-model traceability matrix missing |

## Script Modules

| Script Area | Files | Responsibility | Tests | Known Gaps |
| --- | --- | --- | --- | --- |
| Behavior validation | `backend/scripts/run_behavior_validation.*` | Scenario validation gate | `test_behavior_validation_script.py` | Scenario-to-feature matrix is partial |
| Release smoke | `backend/scripts/run_release_smoke.ps1`, `.sh` | Production/local release readiness smoke | `test_deployment_trigger_scripts.py` | Bash path may be unverified on Windows |
| Incident evidence | `backend/scripts/export_incident_evidence_bundle.py` | Production-safe evidence export | `test_incident_evidence_bundle_script.py` | None for first map |
| Worker entrypoints | `run_reflection_queue_once.*`, `run_maintenance_tick_once.*`, `run_proactive_tick_once.*` | Externalized queue/cadence execution | Worker and deployment script tests | Per-script operator examples live in ops docs |
| Deployment webhook | `trigger_coolify_deploy_webhook.*` | Coolify deploy trigger | `test_deployment_trigger_scripts.py` | Env-specific execution remains operator-owned |
