# AGENTS.md - Personality / AION

## Purpose

This repository uses a project-specific multi-agent workflow so Codex and
related agents can evolve AION without drifting away from the current Python
runtime, contracts, docs, deployment reality, or product-shell UX direction.

## Canonical Context

Read these before starting non-trivial work:

- `.codex/context/PROJECT_STATE.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/LEARNING_JOURNAL.md`
- `.agents/workflows/general.md`
- `.agents/workflows/documentation-governance.md`
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
- `docs/architecture/architecture-source-of-truth.md`
- `docs/engineering/local-development.md`
- `docs/engineering/testing.md`
- `docs/planning/next-iteration-plan.md`
- `docs/planning/open-decisions.md`
- `docs/operations/runtime-ops-runbook.md`
- `docs/governance/working-agreements.md`
- `docs/governance/repository-structure-policy.md`
- `docs/governance/function-coverage-ledger-standard.md`
- `docs/governance/function-coverage-ledger-template.csv`
- `docs/ux/visual-direction-brief.md`
- `docs/ux/experience-quality-bar.md`
- `docs/ux/design-memory.md`
- `docs/ux/screen-quality-checklist.md`
- `docs/ux/anti-patterns.md`
- `docs/ux/brand-personality-tokens.md`
- `docs/ux/canonical-visual-implementation-workflow.md`
- `docs/ux/background-and-decorative-asset-strategy.md`

## Core Rules

### 1. Architecture Is Source Of Truth

- `docs/architecture/` is the single architecture authority for this repo.
- Implementation must stay aligned with approved architecture docs.
- If implementation does not fit architecture, stop and report the mismatch
  instead of forcing a workaround.

### 2. Critical Prohibitions

- Do not create new systems without explicit approval.
- Do not introduce workaround paths or temporary bypasses.
- Do not duplicate logic already covered by existing mechanisms.
- Always reuse existing approved systems first.

### 3. Decision Mode For Mismatches

When architecture and implementation clash:

1. describe the problem
2. propose 2 to 3 valid options
3. wait for explicit user decision

### 4. Mandatory Task Structure

Each task must use `.codex/templates/task-template.md`, including:

- `Context`
- `Goal`
- `Constraints`
- `Definition of Done`
- `Forbidden`

### 5. Stage-Based Delivery Workflow

Every task must declare its current delivery stage and the output expected from
that stage.

Supported stages:
- `intake`
- `analysis`
- `planning`
- `implementation`
- `verification`
- `release`
- `post-release`

Rules:
- Do not skip stages implicitly.
- Do not implement during `analysis` or `planning` unless explicitly requested.
- Do not declare a task complete without `verification` evidence.
- If missing information materially affects quality or risk, stop at the
  current stage and surface the gap.

### 6. Mandatory Review And Refactor

After implementation, verify:

- architecture alignment
- reuse of existing systems
- no workaround introduced
- no logic duplication introduced

If any check fails, fix before closure.

### 7. Repository Guardrails

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
- When active work is unclear, a release or handoff needs confidence, or the
  queue goes stale, use the function coverage ledger standard to turn AION
  runtime/module confidence gaps into explicit evidence, blocker, fix, or
  scope-decision tasks before inventing new feature work.
- If a coverage ledger exists, derive follow-up tasks in this order: release
  blockers, implementation-review rows, `P0` evidence rows, `P0/P1` unverified
  rows, then lower-priority scope decisions.
- Do not turn every `PARTIAL` or evidence-missing ledger row into feature work.
  Plan verification first, then create a narrow fix only when proof or code
  inspection finds a real defect.
- For runtime, memory, reflection, language, or preference changes, leave
  behind focused tests and docs or context updates.
- For UX/UI work, require explicit design source, state coverage, responsive
  evidence, accessibility checks, and parity notes.
- For flagship screenshot-driven UX/UI work, close one surface at a time:
  - finish `layout` before `sidebar`
  - finish shared shell pieces before route modules that depend on them
  - do not polish `dashboard`, `chat`, or `personality` in parallel when the
    current target surface is still below the acceptance threshold
- Reuse shared UI patterns before introducing screen-local style inventions.
- When a new pattern is approved, record it in `docs/ux/design-memory.md`.
- When a canonical web screen reference exists, treat it as a specification
  and close the task with screenshot-comparison evidence.
- For canonical screenshot work, require an explicit `95%` parity gate before
  moving to the next dependent surface.
- When the user adds explicit notes on top of a canonical screenshot, treat the
  screenshot plus those notes as the active merged spec.
- If user notes conflict with each other or with an already-approved screen
  interpretation, stop and ask the user to choose before implementing.
- Do not silently downgrade decorative fidelity by replacing image-based
  backgrounds with gradient approximations.
- When a recurring environment or execution pitfall is discovered, record it in
  `.codex/context/LEARNING_JOURNAL.md` in the same task.
- Follow the default loop:
  - check architecture
  - create task
  - implement
  - review
  - fix or refactor
  - sync docs and context
  - repeat

## Project Validation Baseline

Primary automated gate for this repo:

- `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`

Add narrower commands when useful, for example:

- `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py; Pop-Location`
- `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py; Pop-Location`

Use Docker and HTTP smoke when deployment, runtime wiring, or integrations
change:

- `docker compose up --build`
- `curl http://localhost:8000/health`
- `curl -X POST http://localhost:8000/event ...`

## Autonomous Engineering Loop

Follow `docs/governance/autonomous-engineering-loop.md` for every autonomous iteration:

1. analyze current state
2. select exactly one priority task
3. plan implementation
4. execute implementation
5. verify and test
6. self-review
7. update documentation and knowledge

Before starting an iteration, perform the process self-audit from that document. Do not continue until all seven steps, one-task scope, and the correct operation mode are represented in the task contract.

Operation mode rotates by iteration number:

- `BUILDER`: default mode
- `ARCHITECT`: every third iteration, unless the iteration is also a tester iteration
- `TESTER`: every fifth iteration
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
   - `docs/governance/function-coverage-ledger-standard.md` and any active
     `docs/operations/*function-coverage*` artifacts when the queue is stale,
     release confidence is unclear, or a handoff/incident needs a module map
4. If planning docs and board drift, sync them before implementation.
5. Implement exactly one small slice.
6. Run relevant validation.
7. Update task, project state, and docs in the same cycle.
8. Return files changed, tests run, deployment impact, and the next tiny task.

## UX/UI Rule

This repository now has active browser-shell work. For UX/UI scope:

- require a design source or approved artifact
- check loading, empty, error, and success states
- check desktop, tablet, and mobile behavior
- check accessibility and input modes when relevant
- keep evidence in task notes or PR notes
- use `docs/ux/visual-direction-brief.md` before broad UI refresh work
- use `docs/ux/screen-quality-checklist.md` before calling a screen polished
- use `docs/ux/canonical-visual-implementation-workflow.md` for screenshot
  driven parity tasks
- use `docs/ux/background-and-decorative-asset-strategy.md` when route art
  direction depends on illustration or image-rich atmosphere
- require a quick screenshot check after each surface slice before proceeding
  to the next dependent surface

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

## Production Hardening Gate

Canonical hardening files:

- `DEFINITION_OF_DONE.md`
- `INTEGRATION_CHECKLIST.md`
- `NO_TEMPORARY_SOLUTIONS.md`
- `DEPLOYMENT_GATE.md`
- `AI_TESTING_PROTOCOL.md`
- `.codex/agents/ai-red-team-agent.md`

Every task must include Goal, Scope, Implementation Plan, Acceptance Criteria, Definition of Done, and Result Report. A task is `DONE` only after `DEFINITION_OF_DONE.md` is satisfied with evidence.

Runtime features must be vertical slices across UI, logic, API, DB, validation, error handling, and tests. Partial implementations, placeholders, mock-only behavior, fake data, temporary fixes, and hidden bypasses are forbidden.

AI systems must be tested against prompt injection, data leakage, and unauthorized access before deployment. AI features require reproducible multi-turn scenarios from `AI_TESTING_PROTOCOL.md` and red-team review when risk is meaningful.

## Template Sync: World-Class Delivery Addendum

Use these additional standards for substantial product, runtime, release, UX,
security, or AI work:

- `.agents/workflows/user-collaboration.md`
- `.agents/workflows/world-class-delivery.md`
- `docs/governance/world-class-product-engineering-standard.md`
- `docs/operations/service-reliability-and-observability.md`
- `docs/security/secure-development-lifecycle.md`
- `docs/ux/evidence-driven-ux-review.md`

For substantial changes, define why the work matters, the smallest safe slice,
the success signal, the main failure mode, and the rollback or recovery path.
For deployable services or important journeys, define SLIs/SLOs, health checks,
alert routes, and error-budget posture when appropriate. For auth, AI, money,
secrets, permissions, integrations, or user-data work, use the secure
development lifecycle and include threat-model or abuse-case evidence.
