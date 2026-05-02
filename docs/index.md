# AION Documentation Index

This is the engineering entrypoint for the repository. Use it as the first stop
when tracing behavior across architecture, code, runtime, tests, and release
evidence.

## Read First

- [Docs README](README.md) - existing documentation model and canonical source
  ordering.
- [Project Overview](overview.md) - current product/runtime summary.
- [Architecture Source Of Truth](architecture/architecture-source-of-truth.md)
  - how canonical architecture authority is assigned.
- [Canonical Architecture](architecture/02_architecture.md) - intended AION
  cognitive architecture.
- [Runtime Flow](architecture/15_runtime_flow.md) - canonical stage order:
  `event -> perception -> context -> motivation -> role -> planning -> action -> expression -> memory -> reflection`.
- [Agent Contracts](architecture/16_agent_contracts.md) - stage ownership and
  data boundaries.
- [Runtime Reality](implementation/runtime-reality.md) - live implementation and
  transitional details.

## Engineering System Map

- [Documentation Inventory](analysis/documentation-inventory.md) - known docs,
  purpose, related code areas, suspected drift, and missing areas.
- [Codebase Map](architecture/codebase-map.md) - backend, frontend, data,
  integrations, workers, scripts, deployment, and tests.
- [Traceability Matrix](architecture/traceability-matrix.md) - core features
  mapped across frontend, API, services, models, pipelines, tests, and docs.
- [API Reference](api/index.md) - endpoint purpose, auth posture, schemas,
  side effects, frontend callers, tests, and related pipelines.
- [Data Model Reference](data/index.md) - ORM tables, migrations, repository
  capability groups, feature usage, tests, and data-change checklist.
- [Pipeline Registry](pipelines/index.md) - runtime and product flow registry.
- [Foreground Runtime Pipeline](pipelines/foreground-runtime.md) - dedicated
  stage-order, data, side-effect, failure-point, and test map for the central
  runtime flow.
- [App Chat Pipeline](pipelines/app-chat.md) - dedicated browser chat,
  runtime handoff, optimistic UI, durable transcript, and reconciliation map.
- [Deferred Reflection Pipeline](pipelines/deferred-reflection.md) - dedicated
  queue, signal, durable-write, supervision, and test map for background
  reflection.
- [Scheduler And Proactive Pipeline](pipelines/scheduler-proactive.md) -
  dedicated cadence-owner, planned-work, proactive, observer, evidence, and
  test map.
- [Tools Pipeline](pipelines/tools.md) - dedicated app tools, connector
  readiness, preference, Telegram link, permission-gate, and test map.
- [Module Registry](modules/index.md) - module responsibilities, dependencies,
  used pipelines, related routes, models, tests, and known gaps.
- [Documentation Drift Report](analysis/documentation-drift.md) - verified
  disconnects and explicit follow-up gaps.
- [Documentation Maintenance Rules](CONTRIBUTING-DOCS.md) - required updates
  when features, routes, modules, models, pipelines, tests, or deployment
  behavior change.
- [Documentation Gap Repair Plan](planning/documentation-system-gap-repair-plan.md)
  - queued repairs for generated OpenAPI, ERD/columns, test ownership IDs,
  frontend mapping, and provider-specific docs.

## Operations And Validation

- [Local Development](engineering/local-development.md)
- [Testing](engineering/testing.md)
- [Runtime Ops Runbook](operations/runtime-ops-runbook.md)
- [Service Reliability And Observability](operations/service-reliability-and-observability.md)
- [Environment And Config](architecture/26_env_and_config.md)
- [Runtime Behavior Testing](architecture/29_runtime_behavior_testing.md)

## Governance

- [Autonomous Engineering Loop](governance/autonomous-engineering-loop.md)
- [Working Agreements](governance/working-agreements.md)
- [Repository Structure Policy](governance/repository-structure-policy.md)
- [Function Coverage Ledger Standard](governance/function-coverage-ledger-standard.md)
- [World-Class Product Engineering Standard](governance/world-class-product-engineering-standard.md)
- [Secure Development Lifecycle](security/secure-development-lifecycle.md)

## UX Sources

- [Visual Direction Brief](ux/visual-direction-brief.md)
- [Experience Quality Bar](ux/experience-quality-bar.md)
- [Design Memory](ux/design-memory.md)
- [Screen Quality Checklist](ux/screen-quality-checklist.md)
- [Canonical Visual Implementation Workflow](ux/canonical-visual-implementation-workflow.md)
- [Background And Decorative Asset Strategy](ux/background-and-decorative-asset-strategy.md)

## Current Workspace Topology

- `backend/` - FastAPI runtime, AION orchestration, persistence, workers,
  scripts, migrations, and tests.
- `web/` - React/Vite browser product shell and API client.
- `mobile/` - reserved mobile surface.
- `docs/` - canonical docs, implementation reality, operations, governance,
  planning, UX, and system-map documentation.
- `.codex/` - task contracts, project state, task board, learning journal, and
  agent handoff context.
- `.agents/` - agent prompts and workflow instructions.

## If Something Conflicts

Use this precedence:

1. `docs/architecture/02_architecture.md`,
   `docs/architecture/15_runtime_flow.md`, and
   `docs/architecture/16_agent_contracts.md` for canonical architecture.
2. `docs/implementation/runtime-reality.md`, `docs/operations/`, and live code
   for current implementation reality.
3. `.codex/context/PROJECT_STATE.md` and `.codex/context/TASK_BOARD.md` for
   latest task and release state.

When implementation and architecture disagree, record the mismatch and ask for
a decision instead of inventing a workaround.
