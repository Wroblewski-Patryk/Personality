# Pipeline Registry

Last updated: 2026-05-03

Each pipeline entry links real code paths and declares known gaps. This file is
the registry; future slices can split high-risk pipelines into dedicated files
when they need more detail.

## Foreground Runtime

- Dedicated reference: [Foreground Runtime Pipeline](foreground-runtime.md).
- Trigger: authenticated chat, generic event ingress, debug ingress, Telegram
  handoff, or another approved event source.
- User/system action: a normalized event enters the AION runtime.
- Frontend files: `web/src/App.tsx`, `web/src/lib/api.ts` for app chat;
  external callers for `/event`.
- Backend files:
  - `backend/app/api/routes.py`
  - `backend/app/core/runtime.py`
  - `backend/app/core/runtime_graph.py`
  - `backend/app/core/graph_adapters.py`
  - `backend/app/core/contracts.py`
  - `backend/app/agents/perception.py`
  - `backend/app/affective/assessor.py`
  - `backend/app/agents/context.py`
  - `backend/app/motivation/engine.py`
  - `backend/app/agents/role.py`
  - `backend/app/agents/planning.py`
  - `backend/app/expression/generator.py`
  - `backend/app/core/action.py`
- Data read/write: reads profile, memory, scoped conclusions, relations, goals,
  tasks, proposals; writes episodic memory and reflection queue records.
- Failure points: event normalization, user scoping, graph stage context,
  action boundary, memory persistence, reflection enqueue, provider failures.
- Tests: `backend/tests/test_runtime_pipeline.py`,
  `backend/tests/test_graph_stage_adapters.py`,
  `backend/tests/test_graph_state_contract.py`,
  stage-specific tests.
- Related docs: `docs/architecture/15_runtime_flow.md`,
  `docs/architecture/16_agent_contracts.md`,
  `docs/implementation/runtime-reality.md`.

## App Auth Session

- Trigger: registration, login, logout, or session refresh from the web shell.
- User/system action: user creates or uses a first-party app session.
- Frontend files: `web/src/App.tsx`, `web/src/lib/api.ts`.
- Backend files: `backend/app/api/routes.py`, `backend/app/api/schemas.py`,
  `backend/app/core/config.py`.
- Data read/write: `AionAuthUser`, `AionAuthSession`, selected profile fields.
- Failure points: password validation, cookie settings, expired/revoked
  sessions, duplicate email, missing auth on app routes.
- Tests: `backend/tests/test_api_routes.py`, `backend/tests/test_config.py`.
- Related docs: `docs/architecture/26_env_and_config.md`,
  `docs/engineering/local-development.md`.

## Profile Settings

- Trigger: settings screen load or update.
- User/system action: user changes display name, preferred language, UI
  language, UTC offset, or proactive opt-in posture.
- Frontend files: `web/src/App.tsx`, `web/src/lib/api.ts`.
- Backend files: `backend/app/api/routes.py`,
  `backend/app/memory/repository.py`, `backend/app/utils/utc_offset.py`,
  `backend/app/utils/preferences.py`.
- Data read/write: `AionProfile`, profile/preference conclusions as applicable.
- Failure points: invalid locale/UTC offset, missing auth, profile persistence
  drift.
- Tests: `backend/tests/test_api_routes.py`, `backend/tests/test_preferences.py`.
- Related docs: `docs/overview.md`, `docs/architecture/26_env_and_config.md`.

## App Chat Turn

- Dedicated reference: [App Chat Pipeline](app-chat.md).
- Trigger: web user sends a chat message.
- User/system action: web shell renders an optimistic local turn, then calls
  backend runtime and refreshes durable history.
- Frontend files: `web/src/App.tsx`, `web/src/lib/api.ts`,
  `web/src/index.css`.
- Backend files: `backend/app/api/routes.py`,
  `backend/app/core/runtime.py`, `backend/app/integrations/delivery_router.py`,
  `backend/app/memory/repository.py`.
- Data read/write: `AionMemory`, `AionProfile`, `AionReflectionTask`, scoped
  conclusions/relations.
- Failure points: auth expiry, runtime exception, local/durable transcript
  reconciliation, assistant delivery failure, reflection enqueue failure.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_runtime_pipeline.py`,
  `backend/tests/test_expression_agent.py`,
  `backend/tests/test_delivery_router.py`.
- Related docs: `docs/architecture/15_runtime_flow.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/internal-chat-and-telegram-message-quality-plan.md`.

## External Event Ingress

- Trigger: `POST /event` from API or transport.
- User/system action: route normalizes an event and either queues/coordinates
  attention or runs foreground runtime.
- Frontend files: none required.
- Backend files: `backend/app/api/routes.py`,
  `backend/app/core/events.py`, `backend/app/core/attention.py`,
  `backend/app/core/runtime.py`.
- Data read/write: `AionAttentionTurn`, `AionMemory`, `AionReflectionTask`.
- Failure points: missing user scope, attention coordination mode, transport
  identity mapping, debug compatibility policy.
- Tests: `backend/tests/test_event_normalization.py`,
  `backend/tests/test_api_routes.py`, `backend/tests/test_runtime_pipeline.py`.
- Related docs: `docs/architecture/11_event_contact.md`,
  `docs/architecture/15_runtime_flow.md`.

## Telegram Linking And Transport

- Trigger: web link-code start, Telegram command/link message, webhook setup,
  or Telegram delivery.
- User/system action: user links Telegram to app profile; transport may deliver
  runtime replies through Telegram.
- Frontend files: `web/src/App.tsx`, `web/src/lib/api.ts`.
- Backend files: `backend/app/api/routes.py`,
  `backend/app/integrations/telegram/client.py`,
  `backend/app/integrations/telegram/telemetry.py`,
  `backend/app/integrations/delivery_router.py`.
- Data read/write: `AionProfile`, `AionMemory`, `AionAttentionTurn`.
- Failure points: missing credentials, wrong chat/user mapping, webhook secret,
  delivery segmentation/formatting, provider API failure.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_telegram_client.py`,
  `backend/tests/test_delivery_router.py`.
- Related docs: `docs/operations/runtime-ops-runbook.md`,
  `docs/planning/shared-chat-transcript-and-telegram-continuity-plan.md`.

## Learned State Overview

- Trigger: web personality/dashboard/memory-style surfaces load overview data
  or internal operator asks for state inspection.
- User/system action: backend builds a safe learned-state snapshot.
- Frontend files: `web/src/App.tsx`, `web/src/lib/api.ts`.
- Backend files: `backend/app/api/routes.py`,
  `backend/app/core/learned_state_policy.py`,
  `backend/app/memory/repository.py`.
- Data read/write: reads `AionMemory`, `AionProfile`, `AionConclusion`,
  `AionRelation`, `AionTheta`, goals/tasks; no route-owned writes expected.
- Failure points: exposing raw memory payloads, stale overview projection,
  missing recent activity, user-scope leaks.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_memory_repository.py`.
- Related docs: `docs/architecture/04_memory_system.md`,
  `docs/architecture/22_relation_system.md`.

## Tools Overview

- Dedicated reference: [Tools Pipeline](tools.md).
- Trigger: tools route load or preference change.
- User/system action: user inspects tool/channel readiness and toggles
  approved tool preferences.
- Frontend files: `web/src/App.tsx`, `web/src/lib/api.ts`.
- Backend files: `backend/app/api/routes.py`,
  `backend/app/core/capability_catalog.py`,
  `backend/app/core/connector_execution.py`,
  `backend/app/core/connector_policy.py`,
  `backend/app/core/app_tools_policy.py`.
- Data read/write: profile/preferences; exact storage split for all toggles is
  `AionConclusion` for supported preference keys and `AionProfile` for
  Telegram link/profile state.
- Failure points: provider config drift, presenting policy-only connectors as
  provider-backed, preference persistence mismatch.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_connector_policy.py`,
  `backend/tests/test_action_executor.py`.
- Related docs: `docs/architecture/20_action_system.md`,
  `docs/operations/runtime-ops-runbook.md`.

## Deferred Reflection

- Dedicated reference: [Deferred Reflection Pipeline](deferred-reflection.md).
- Trigger: foreground runtime enqueue or queue-drain script/worker.
- User/system action: background worker converts episodic evidence into slower
  conclusions, relations, proposals, progress, and affective/adaptive signals.
- Frontend files: none directly.
- Backend files: `backend/app/reflection/worker.py`,
  `backend/app/reflection/*.py`,
  `backend/app/core/reflection_supervision_policy.py`,
  `backend/scripts/run_reflection_queue_once.*`.
- Data read/write: `AionReflectionTask`, `AionMemory`, `AionConclusion`,
  `AionRelation`, `AionGoalProgress`, `AionGoalMilestone*`,
  `AionSubconsciousProposal`.
- Failure points: stuck queue, retry exhaustion, malformed episodic payload,
  duplicated signal logic, scope leakage.
- Tests: `backend/tests/test_reflection_worker.py`,
  `backend/tests/test_reflection_supervision_policy.py`,
  `backend/tests/test_memory_repository.py`.
- Related docs: `docs/architecture/04_memory_system.md`,
  `docs/architecture/22_relation_system.md`.

## Scheduler And Proactive Cadence

- Dedicated reference: [Scheduler And Proactive Pipeline](scheduler-proactive.md).
- Trigger: external maintenance/proactive tick or in-process fallback.
- User/system action: scheduler evaluates maintenance, planned work, proactive
  candidates, and delivery boundaries.
- Frontend files: web health/status panels only, no direct scheduler UI.
- Backend files: `backend/app/workers/scheduler.py`,
  `backend/app/proactive/engine.py`,
  `backend/app/core/planned_action_observer.py`,
  `backend/app/core/external_scheduler_policy.py`,
  `backend/scripts/run_maintenance_tick_once.*`,
  `backend/scripts/run_proactive_tick_once.*`.
- Data read/write: `AionSchedulerCadenceEvidence`,
  `AionPlannedWorkItem`, `AionSubconsciousProposal`, `AionMemory`.
- Failure points: cadence ownership drift, anti-spam regression, passive/active
  boundary mistakes, provider delivery failure.
- Tests: `backend/tests/test_scheduler_worker.py`,
  `backend/tests/test_planned_action_observer.py`,
  `backend/tests/test_runtime_pipeline.py`.
- Related docs: `docs/architecture/23_proactive_system.md`,
  `docs/operations/runtime-ops-runbook.md`.

## Retrieval And Memory Context

- Trigger: runtime context load, retrieval materialization, health/readiness
  checks.
- User/system action: runtime selects relevant memory and optionally uses
  provider-backed embeddings.
- Frontend files: none directly.
- Backend files: `backend/app/memory/embeddings.py`,
  `backend/app/memory/openai_embedding_client.py`,
  `backend/app/memory/repository.py`,
  `backend/app/core/retrieval_policy.py`,
  `backend/app/core/retrieval_lifecycle_policy.py`.
- Data read/write: `AionSemanticEmbedding`, `AionMemory`, scoped conclusions.
- Failure points: provider config drift, deterministic fallback mismatch,
  stale embedding materialization, retrieval ranking regression.
- Tests: `backend/tests/test_embedding_strategy.py`,
  `backend/tests/test_memory_repository.py`,
  `backend/tests/test_runtime_pipeline.py`.
- Related docs: `docs/architecture/04_memory_system.md`,
  `docs/architecture/29_runtime_behavior_testing.md`.

## Debug And Incident Evidence

- Trigger: operator debug route, release smoke, incident evidence bundle export.
- User/system action: operator receives policy-safe debug or strict-mode
  incident evidence.
- Frontend files: health surfaces in `web/src/App.tsx` only.
- Backend files: `backend/app/api/routes.py`,
  `backend/app/core/debug_compat.py`,
  `backend/app/core/debug_ingress_policy.py`,
  `backend/app/core/observability_policy.py`,
  `backend/scripts/export_incident_evidence_bundle.py`.
- Data read/write: mostly reads health/runtime policy; debug event execution
  can write normal runtime memory.
- Failure points: debug policy exposure, token/config mismatch, production
  strict-mode evidence export, stale smoke expectations.
- Tests: `backend/tests/test_debug_compat_telemetry.py`,
  `backend/tests/test_runtime_policy.py`,
  `backend/tests/test_observability_policy.py`,
  `backend/tests/test_incident_evidence_bundle_script.py`.
- Related docs: `docs/architecture/17_logging_and_debugging.md`,
  `docs/operations/runtime-ops-runbook.md`.

## User Data Reset

- Trigger: settings reset confirmation or operator cleanup script.
- User/system action: user-owned data is deleted while preserved categories
  remain explicit.
- Frontend files: `web/src/App.tsx`, `web/src/lib/api.ts`.
- Backend files: `backend/app/api/routes.py`,
  `backend/scripts/run_user_data_cleanup.py`.
- Data read/write: deletes user-scoped rows across memory/profile/session and
  related state according to route/script policy.
- Failure points: insufficient confirmation, deleting preserved categories,
  session revocation mismatch, unlisted tables.
- Tests: `backend/tests/test_api_routes.py`.
- Related docs: `docs/planning/user-data-reset-and-production-cleanup-plan.md`,
  `docs/operations/runtime-ops-runbook.md`.

## Web Shell Route Rendering

- Trigger: browser navigation and authenticated route state changes.
- User/system action: React renders public home, login, dashboard, chat,
  personality, settings, tools, memory, reflections, plans, goals, insights,
  automations, and integrations.
- Frontend files: `web/src/App.tsx`, `web/src/index.css`,
  `web/src/lib/api.ts`.
- Backend files: app-facing API routes as used by each route.
- Data read/write: varies by route; auth/settings/chat/tools/personality are
  backend-backed, some module route content remains static or fallback-driven.
- Failure points: route-owned copy drift, localization drift, loading/error
  state gaps, frontend/backend contract mismatch, lack of dedicated frontend
  automated tests.
- Tests: `backend/tests/test_web_routes.py`, `npm run build` evidence in task
  records. `GAP`: no dedicated frontend unit/e2e test suite found in this pass.
- Related docs: `docs/ux/*`, `docs/planning/web-ux-ui-productization-plan.md`.

## Release And Deployment Smoke

- Trigger: operator release or production parity check.
- User/system action: smoke scripts check health, deploy revision, readiness,
  and selected production posture.
- Frontend files: none directly.
- Backend files: `backend/scripts/run_release_smoke.ps1`,
  `backend/scripts/trigger_coolify_deploy_webhook.py`,
  `backend/app/core/deployment_policy.py`,
  `backend/app/core/runtime_policy.py`.
- Data read/write: mostly read-only health and deployment state.
- Failure points: stale script paths, revision parity drift, missing production
  env, strict debug policy, migration drift.
- Tests: `backend/tests/test_deployment_trigger_scripts.py`,
  `backend/tests/test_main_runtime_policy.py`.
- Related docs: `docs/operations/runtime-ops-runbook.md`,
  `docs/architecture/28_local_windows_and_coolify_deploy.md`.
