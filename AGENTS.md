# AGENTS.md - Personality / AION

## Purpose

This repository uses a project-specific multi-agent workflow so Codex and
related agents can evolve AION without drifting away from the current Python
runtime, contracts, docs, and deployment reality.

## Canonical Context

Read these before starting non-trivial work:

- `.codex/context/PROJECT_STATE.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/LEARNING_JOURNAL.md`
- `.agents/workflows/general.md`
- `.agents/workflows/subagent-orchestration.md`

## Canonical Docs

- `docs/README.md`
- `docs/overview.md`
- `docs/architecture/02_architecture.md`
- `docs/architecture/15_runtime_flow.md`
- `docs/architecture/16_agent_contracts.md`
- `docs/architecture/17_logging_and_debugging.md`
- `docs/architecture/29_runtime_behavior_testing.md`
- `docs/architecture/26_env_and_config.md`
- `docs/architecture/27_codex_instructions.md`
- `docs/engineering/local-development.md`
- `docs/engineering/testing.md`
- `docs/planning/next-iteration-plan.md`
- `docs/planning/open-decisions.md`
- `docs/operations/runtime-ops-runbook.md`
- `docs/governance/working-agreements.md`
- `docs/governance/repository-structure-policy.md`

## Core Rules

- Project state, task board, learning journal, and canonical docs are the
  source of truth.
- Keep repository artifacts in English.
- Communicate with the user in the user's language.
- Never reference sibling repositories or `!template` paths from project docs.
- Keep root minimal. Project documentation belongs in `docs/`.
- Every meaningful change updates at least one relevant source-of-truth file:
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/LEARNING_JOURNAL.md` when a recurring pitfall is confirmed
  - canonical docs when behavior, scope, or architecture changed
- Respect the AION pipeline:
  - `event -> perception -> context -> motivation -> role -> planning -> action -> expression -> memory -> reflection`
- Preserve the action boundary:
  - side effects belong in the action or integration layer, not in reasoning
    stages
- Keep changes tiny, testable, and reversible.
- Run relevant validation before creating a commit.
- Do not mark work done without test or evidence notes that match the changed
  scope.
- For runtime, memory, reflection, language, or preference changes, leave
  behind focused tests and docs or context updates.
- When a recurring environment or execution pitfall is discovered, record it in
  `.codex/context/LEARNING_JOURNAL.md` in the same task.
- Follow the default loop:
  - plan
  - implement
  - test
  - review risks and architecture follow-up
  - sync docs and context
  - repeat

## Project Validation Baseline

Primary automated gate for this repo:

- `.\.venv\Scripts\python -m pytest -q`

Add narrower commands when useful, for example:

- `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py`

Use Docker and HTTP smoke when deployment, runtime wiring, or integrations
change:

- `docker compose up --build`
- `curl http://localhost:8000/health`
- `curl -X POST http://localhost:8000/event ...`

## Agent Catalog

- Planner: `.agents/prompts/planner.md` or `.claude/agents/planner.agent.md`
- Product Docs: `.agents/prompts/product-docs.md` or
  `.claude/agents/product-docs.agent.md`
- Backend Builder: `.agents/prompts/backend-builder.md` or
  `.claude/agents/backend-builder.agent.md`
- Frontend Builder: `.agents/prompts/frontend-builder.md` or
  `.claude/agents/frontend-builder.agent.md`
- QA/Test: `.agents/prompts/qa-test.md` or `.claude/agents/qa-test.agent.md`
- Security: `.agents/prompts/security-auditor.md` or
  `.claude/agents/security-auditor.agent.md`
- DB/Migrations: `.agents/prompts/db-migrations.md` or
  `.claude/agents/db-migrations.agent.md`
- Ops/Release: `.agents/prompts/ops-release.md` or
  `.claude/agents/ops-release.agent.md`
- Code Review: `.agents/prompts/code-reviewer.md`
- Codex Documentation Agent: `.codex/agents/documentation-agent.md`
- Codex Planning Agent: `.codex/agents/planning-agent.md`
- Codex Execution Agent: `.codex/agents/execution-agent.md`
- Codex Review Agent: `.codex/agents/review-agent.md`

## Trigger Intent

If the user sends a short execution nudge such as `rob`, `dzialaj`, `start`,
`go`, `next`, or `lecimy`:

1. Read `.codex/context/TASK_BOARD.md`.
2. Take the first `READY` or `IN_PROGRESS` task.
3. If no task is `READY`, derive the next smallest useful task from:
   - `docs/planning/next-iteration-plan.md`
   - `docs/planning/open-decisions.md`
4. If planning docs and board drift, sync them before implementation.
5. Implement exactly one small slice.
6. Run relevant validation.
7. Update task, project state, and docs in the same cycle.
8. Return files changed, tests run, deployment impact, and the next tiny task.

## UX/UI Rule

This repo is backend-first today. If a future web or admin UI is introduced:

- require a design source or approved artifact,
- check loading, empty, error, and success states,
- check desktop and mobile behavior,
- keep evidence in task notes or PR notes.

## Deployment Rule

- Treat `docs/operations/runtime-ops-runbook.md` as the current deployment and
  release-readiness contract.
- For runtime or deployment changes, update smoke steps and rollback notes in
  the same task.

## Subagent Rule

- Delegate only bounded, non-overlapping work.
- Keep critical-path runtime changes local.
- Give delegated tasks explicit file ownership.
- Integrate and verify subagent output before closure.

## Commit Rule

Do not create a commit when the required checks for the touched scope are
failing, unless the user explicitly accepts the risk.
