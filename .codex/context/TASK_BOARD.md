# TASK_BOARD

Last updated: 2026-04-18

## Agent Workflow Refresh (2026-04-18)

- This board is the canonical execution queue for Personality / AION.
- If no task is `READY`, the Planning Agent should derive the next smallest
  executable task from:
  - `docs/planning/next-iteration-plan.md`
  - `docs/planning/open-decisions.md`
- Default delivery loop for every execution slice:
  - plan
  - implement
  - run relevant tests and validations
  - capture architecture follow-up if discovered
  - sync task state, project state, and learning journal when needed
- The current active queue remains `PRJ-015` through `PRJ-016`.
- Additional architecture-alignment work should be appended after that queue so
  the backlog stays explicitly open for later discovery instead of pretending
  the plan is complete.

## READY

- [ ] PRJ-015 Tighten the event normalization and public API boundary
  - Status: READY
  - Group: Observability And Runtime Honesty
  - Owner: Planner
  - Depends on: none
  - Priority: P2
  - Files:
    - `app/core/events.py`
    - `app/api/routes.py`
    - `app/api/schemas.py`
    - `tests/test_event_normalization.py`
    - `tests/test_api_routes.py`
  - Done when:
    - input normalization rules are explicit and test-covered
    - the public `/event` contract stays small and intentional
    - debug behavior remains clearly internal
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_api_routes.py`

## BACKLOG

- [ ] PRJ-016 Move startup toward migration-first schema ownership
  - Status: BACKLOG
  - Group: Observability And Runtime Honesty
  - Owner: DB/Migrations
  - Depends on: none
  - Priority: P2

## FUTURE

- [ ] PRJ-017 Make the expression-to-action handoff explicit and test-covered
  - Status: FUTURE
  - Group: Stage Boundary Alignment
  - Owner: Backend Builder
  - Depends on: PRJ-016
  - Priority: P2
  - Files:
    - `app/core/runtime.py`
    - `app/action/`
    - `app/expression/`
    - `docs/architecture/15_runtime_flow.md`
    - `docs/architecture/16_agent_contracts.md`
  - Done when:
    - the runtime passes an explicit delivery contract from expression into
      action instead of relying on hidden stage coupling
    - action inputs and outputs stay aligned with the documented action
      boundary
    - regression tests pin the handoff contract without changing current
      user-facing behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_expression_agent.py`

- [ ] PRJ-018 Reduce expression/action integration coupling without changing behavior
  - Status: FUTURE
  - Group: Stage Boundary Alignment
  - Owner: Backend Builder
  - Depends on: PRJ-017
  - Priority: P2
  - Files:
    - `app/action/`
    - `app/integrations/`
    - `app/core/runtime.py`
    - related tests
  - Done when:
    - integrations consume the explicit handoff contract instead of stage-local
      assumptions
    - side effects remain isolated inside action
    - behavior stays equivalent from the public runtime point of view
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_telegram_webhook.py`

- [ ] PRJ-019 Add runtime stage ownership and architecture-to-code traceability
  - Status: FUTURE
  - Group: Architecture Traceability And Contract Tests
  - Owner: Product Docs
  - Depends on: PRJ-016
  - Priority: P3
  - Files:
    - `docs/overview.md`
    - `docs/architecture/02_architecture.md`
    - `docs/architecture/15_runtime_flow.md`
    - `docs/architecture/16_agent_contracts.md`
    - `.codex/context/PROJECT_STATE.md`
  - Done when:
    - each documented runtime stage points to its implementation owner in code
      and its primary validation surface
    - current implementation notes versus intended architecture remain explicit
    - the repo truth is easier to audit without reading large modules first
  - Validation:
    - doc-only change, no automated validation required

- [ ] PRJ-020 Add contract-level runtime flow smoke tests for architecture invariants
  - Status: FUTURE
  - Group: Architecture Traceability And Contract Tests
  - Owner: QA/Test
  - Depends on: PRJ-017, PRJ-019
  - Priority: P2
  - Files:
    - `tests/test_runtime_pipeline.py`
    - `tests/test_api_routes.py`
    - `tests/test_logging.py`
    - related helper fixtures
  - Done when:
    - tests pin the documented stage presence, action-boundary rules, and
      traceable runtime result/log invariants
    - future refactors fail loudly when code drifts away from the documented
      runtime flow
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py`

## IN_PROGRESS

- [ ] (none)

## BLOCKED

- [ ] (none)

## REVIEW

- [ ] (none)

## DONE

- [x] PRJ-000 Establish Personality-specific agent workflow scaffolding
- [x] PRJ-001..PRJ-010 Runtime contract, release-smoke, memory, and motivation alignment slices completed and captured in docs and tests
- [x] PRJ-014 Add a reusable stage-level structured logging scaffold
  - Status: DONE
  - Group: Observability And Runtime Honesty
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P2
  - Files:
    - `app/core/runtime.py`
    - `app/core/logging.py`
  - Done when:
    - each runtime stage logs success or failure with `event_id`, `trace_id`, stage, and duration
    - stage logs include short summaries instead of raw payload dumps
    - related docs or project state mention the new observability surface if it changes repo truth
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
- [x] PRJ-011 Extract shared goal/task selection helpers
  - Status: DONE
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P1
  - Done when:
    - tokenization, priority ranking, task-status ranking, and related-goal selection no longer live in multiple copies
    - behavior stays unchanged
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
- [x] PRJ-012 Extract shared goal-progress and milestone-history signal helpers
  - Status: DONE
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: PRJ-011
  - Priority: P1
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
- [x] PRJ-013 Split oversized heuristic modules after helper extraction
  - Status: DONE
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: PRJ-011, PRJ-012
  - Priority: P2
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`
