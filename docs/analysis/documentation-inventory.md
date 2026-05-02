# Documentation Inventory

Last updated: 2026-05-03

This inventory is grounded in the repository tree inspected during PRJ-937. It
does not claim that every document is current; suspected drift is marked
explicitly.

## Existing Documentation Areas

| Area | Paths | Purpose | Related Code Areas | Status |
| --- | --- | --- | --- | --- |
| Root guidance | `README.md`, `AGENTS.md`, `DEFINITION_OF_DONE.md`, `INTEGRATION_CHECKLIST.md`, `NO_TEMPORARY_SOLUTIONS.md`, `DEPLOYMENT_GATE.md`, `AI_TESTING_PROTOCOL.md` | Repo overview, task rules, production gates, AI/security/testing guardrails | Whole repo | Active |
| Docs entrypoints | `docs/README.md`, `docs/index.md`, `docs/overview.md` | Human and engineering entrypoints | Whole repo | `docs/index.md` added by PRJ-937 |
| API reference | `docs/api/index.md` | Endpoint purpose, auth posture, schemas, side effects, frontend callers, tests, and related pipelines | `backend/app/api/routes.py`, `backend/app/api/schemas.py`, `web/src/lib/api.ts` | Added by PRJ-938 |
| Data/model reference | `docs/data/index.md` | ORM tables, migrations, repository capability groups, feature usage, tests, and data-change checklist | `backend/app/memory/models.py`, `backend/migrations/versions/`, `backend/app/memory/repository.py`, data tests | Added by PRJ-939 |
| Canonical architecture | `docs/architecture/*.md` | Intended architecture, runtime flow, contracts, data model, env, behavior testing | `backend/app/core`, `backend/app/agents`, `backend/app/memory`, `backend/app/reflection`, `backend/app/integrations` | Active; older numbered docs may need periodic drift checks |
| Implementation reality | `docs/implementation/runtime-reality.md`, `docs/implementation/dual-loop-coordination.md` | Live/transitional runtime notes | `backend/app/core/runtime.py`, `backend/app/core/runtime_graph.py`, workers, integrations | Active |
| Engineering | `docs/engineering/local-development.md`, `docs/engineering/testing.md` | Local commands and test strategy | `backend/tests`, `web`, `backend/scripts` | Active |
| Operations | `docs/operations/runtime-ops-runbook.md`, `docs/operations/service-reliability-and-observability.md` | Coolify/runtime operations, smoke, reliability posture | `docker-compose*.yml`, `backend/scripts`, `/health` | Active |
| Governance | `docs/governance/*.md` | Autonomous loop, repository structure, working agreements, coverage ledger | `.codex/tasks`, `.codex/context`, docs maintenance | Active |
| Planning | `docs/planning/*.md` | Sequenced work, release gates, UX plans, open decisions | Whole repo; many docs are historical task plans | Mixed: active plus historical |
| UX | `docs/ux/*.md`, `docs/ux/assets/*` | Visual direction, parity workflow, screenshots/assets | `web/src/App.tsx`, `web/src/index.css`, public assets | Active for web shell work |
| Security | `docs/security/secure-development-lifecycle.md` | Secure delivery guidance | Auth, AI, integrations, secrets | Active |
| Agent workflows | `.agents/workflows/*.md`, `.agents/prompts/*.md`, `.codex/agents/*.md` | Agent roles and workflow behavior | `.codex/tasks`, docs, code changes | Active |
| Task evidence | `.codex/tasks/*.md`, `.codex/context/*.md` | Task contracts, project state, task board, learning journal | Whole repo | Active, large, latest-state source |
| Workspace READMEs | `backend/README.md`, `mobile/README.md` | Workspace-specific entrypoints | `backend/`, `mobile/` | Active |

## Related Code Areas

- Backend API and route contracts: `backend/app/api/routes.py`,
  `backend/app/api/schemas.py`.
- Runtime orchestration: `backend/app/core/runtime.py`,
  `backend/app/core/runtime_graph.py`, `backend/app/core/graph_adapters.py`.
- Stage agents: `backend/app/agents/`, `backend/app/affective/`,
  `backend/app/motivation/`, `backend/app/expression/`.
- Persistence: `backend/app/memory/models.py`,
  `backend/app/memory/repository.py`, `backend/migrations/versions/`.
- Background work: `backend/app/workers/scheduler.py`,
  `backend/app/reflection/worker.py`.
- Integrations: `backend/app/integrations/`.
- Web client: `web/src/App.tsx`, `web/src/lib/api.ts`,
  `web/src/index.css`.
- Validation: `backend/tests/`, `backend/scripts/run_behavior_validation.py`,
  `backend/scripts/run_release_smoke.ps1`.

## Suspected Outdated Or Noisy Files

- `docs/README.md` contained repeated `Governance Addendum` headings before
  PRJ-937 cleanup.
- Historical `docs/planning/*.md` files are not all active plans. Treat them as
  task evidence unless linked from current state or task board.
- Some older architecture files may describe earlier implementation phases.
  The local rule remains: if they conflict with `02`, `15`, or `16`, update the
  older file instead of carrying two architecture narratives.
- Any command examples that point to root-level `scripts/` should be checked
  against the current backend-owned script layout under `backend/scripts/`.

## Missing Documentation Areas

- Generated OpenAPI export or richer per-endpoint examples.
- Generated ERD or column-by-column data/model reference.
- Per-module docs for every `backend/app/*` package beyond the registry index.
- Per-pipeline deep dives for every core runtime and app-facing flow.
- Test-to-feature ownership metadata inside tests. Current mapping is inferred
  from test filenames and assertions.
- Frontend component/module map below the monolithic `web/src/App.tsx` level.

## Maintenance Note

When a new feature, route, model, module, pipeline, deployment behavior, or test
is added, update [Documentation Maintenance Rules](../CONTRIBUTING-DOCS.md)
and the relevant registry or traceability row in the same task.
