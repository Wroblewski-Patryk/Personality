# TASK_BOARD

Last updated: 2026-04-17

## READY

- [ ] PRJ-014 Add a reusable stage-level structured logging scaffold
  - Status: READY
  - Group: Observability And Runtime Honesty
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P2
  - Files:
    - `app/core/runtime.py`
    - `app/core/logging.py`
  - Done when:
    - each runtime stage logs success/failure with `event_id`, `trace_id`, stage, and duration
    - stage logs include short summaries instead of raw payload dumps
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`

## BACKLOG

- [ ] PRJ-011 Extract shared goal/task selection helpers
  - Status: BACKLOG
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P1

- [ ] PRJ-012 Extract shared goal-progress and milestone-history signal helpers
  - Status: BACKLOG
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: PRJ-011
  - Priority: P1

- [ ] PRJ-013 Split oversized heuristic modules after helper extraction
  - Status: BACKLOG
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: PRJ-011, PRJ-012
  - Priority: P2

- [ ] PRJ-015 Tighten the event normalization and public API boundary
  - Status: BACKLOG
  - Group: Observability And Runtime Honesty
  - Owner: Planner
  - Depends on: none
  - Priority: P2

- [ ] PRJ-016 Move startup toward migration-first schema ownership
  - Status: BACKLOG
  - Group: Observability And Runtime Honesty
  - Owner: DB/Migrations
  - Depends on: none
  - Priority: P2

## IN_PROGRESS

- [ ] (none)

## BLOCKED

- [ ] (none)

## DONE

- [x] PRJ-000 Establish Personality-specific agent workflow scaffolding
  - Status: DONE
  - Owner: Product Docs
  - Depends on: none
  - Priority: P1
  - Done when:
    - `AGENTS.md`, `.agents/`, `.claude/`, `.codex/`, `.githooks/`, and `.github/` exist in project-specific form
    - workflow rules mention the real stack and docs
    - validation commands match the repo

- [x] PRJ-001 Align runtime-facing docs with current reflection, language, role, and preference behavior
  - Status: DONE
  - Owner: Product Docs
  - Depends on: none
  - Priority: P1
  - Done when:
    - `docs/overview.md`, `docs/planning/open-decisions.md`, and any needed assumptions or basics docs reflect the current implemented runtime
    - current vs planned behavior is explicit
    - follow-up gaps remain captured rather than hidden

- [x] PRJ-002 Add endpoint-level coverage for reflection-related runtime contracts
  - Status: DONE
  - Owner: QA/Test
  - Depends on: none
  - Priority: P1
  - Done when:
    - `GET /health` reflection snapshot or related runtime contract is covered where applicable
    - `/event` reflection-trigger behavior is validated by tests if that contract is exposed
    - any brittle assumptions are documented

- [x] PRJ-003 Decide migration baseline and either document deferral or scaffold the first formal migration path
  - Status: DONE
  - Owner: DB/Migrations
  - Depends on: none
  - Priority: P1
  - Done when:
    - the schema strategy is explicit
    - rollback risk is documented
    - local bootstrap behavior remains understood

- [x] PRJ-004 Revisit the public `/event` response contract
  - Status: DONE
  - Owner: Planner
  - Depends on: PRJ-001
  - Priority: P1
  - Done when:
    - the owner and purpose of the response shape are explicit
    - tests and docs match the chosen contract
    - debug-only fields are intentional rather than accidental

- [x] PRJ-005 Harden release and deployment confidence for the Coolify path
  - Status: DONE
  - Owner: Ops/Release
  - Depends on: none
  - Priority: P2
  - Done when:
    - deployment smoke steps are explicit
    - webhook or manual-release fallback is documented
    - release verification is repeatable

- [x] PRJ-006 Introduce structured episodic memory payload alongside the human-readable summary
  - Status: DONE
  - Group: Runtime Contract Foundation
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P1
  - Done when:
    - episodic memory rows keep a typed machine-readable payload
    - the human-readable summary remains available
    - old rows are not broken
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_memory_repository.py tests/test_schema_baseline.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

- [x] PRJ-007 Move context and reflection to payload-first episodic-memory readers
  - Status: DONE
  - Group: Runtime Contract Foundation
  - Owner: Backend Builder
  - Depends on: PRJ-006
  - Priority: P1
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- [x] PRJ-008 Lock the episodic memory contract with regression coverage
  - Status: DONE
  - Group: Runtime Contract Foundation
  - Owner: QA/Test
  - Depends on: PRJ-006, PRJ-007
  - Priority: P1
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_memory_repository.py tests/test_context_agent.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_schema_baseline.py`

- [x] PRJ-009 Normalize motivation mode contract to the documented set
  - Status: DONE
  - Group: Motivation And Runtime Contract Alignment
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P1
  - Done when:
    - emotional-turn behavior no longer depends on undocumented `support`
    - supportive behavior still remains visible through documented runtime contracts
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-010 Add explicit emotional-turn contract tests after motivation normalization
  - Status: DONE
  - Group: Motivation And Runtime Contract Alignment
  - Owner: QA/Test
  - Depends on: PRJ-009
  - Priority: P1
  - Files:
    - `tests/test_motivation_engine.py`
    - `tests/test_planning_agent.py`
    - `tests/test_expression_agent.py`
    - `tests/test_runtime_pipeline.py`
  - Done when:
    - tests describe how emotional support flows through the documented contract
    - the expected behavior is readable without inspecting implementation details
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`
