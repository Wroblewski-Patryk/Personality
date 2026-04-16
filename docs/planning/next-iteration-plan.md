# Next Iteration Plan

## Purpose

This plan translates the 2026-04-17 repo analysis into an execution roadmap that brings the code closer to `docs/basics/` without rewriting `docs/basics/`.

The goal is not to add more features first.
The goal is to make the current AION runtime more correct, more inspectable, and easier to extend without architectural drift.

## Repo Analysis Snapshot

Confirmed on 2026-04-17:

- `.\.venv\Scripts\python -m pytest -q` passes with `246 passed`
- the live runtime already covers:
  - event normalization
  - state load
  - identity
  - perception
  - context
  - motivation
  - role
  - planning
  - expression
  - action
  - episodic persistence
  - durable reflection enqueue
- the current problems are mostly contract and maintainability problems, not missing endpoints

## Progress Update

Completed on 2026-04-17:

- `PRJ-006` introduced a structured episodic memory payload plus a readable summary and formal migration step.
- `PRJ-007` moved context retrieval and reflection to payload-first episodic readers with legacy-summary fallback.
- `PRJ-008` locked that episodic contract with regression tests across persistence, context, reflection, and runtime.
- `PRJ-009` normalized motivation to the documented shared mode set while keeping emotional support visible through role, valence, planning, and expression tone.
- `PRJ-010` added explicit emotional-turn contract tests that describe supportive behavior through the documented runtime surfaces instead of an extra motivation mode.

## Highest-Risk Gaps

### 1. Episodic memory is still a machine-readable string contract

Current behavior:

- `ActionExecutor.persist_episode()` now writes a typed payload and a readable summary
- context and reflection now prefer payload-first reads with fallback for old summary-only rows

Why it matters:

- this removed a high-risk contract gap between runtime and `docs/basics/16_agent_contracts.md`
- the remaining memory-contract risk is mainly regression prevention, not missing structure

### 2. Motivation contract drift exists

Current behavior:

- resolved in code by `PRJ-009`
- runtime now keeps emotional-turn behavior inside the documented shared mode set:
  - `respond|ignore|analyze|execute|clarify`

Why it matters:

- this removed one of the clearest runtime-vs-basics contract mismatches
- the remaining work is to keep that documented contract stable while other runtime slices evolve

### 3. Core heuristic modules are too large

Current file sizes on 2026-04-17:

- `app/reflection/worker.py`: 1365 lines
- `app/agents/context.py`: 806 lines
- `app/agents/planning.py`: 755 lines
- `app/motivation/engine.py`: 560 lines

Why it matters:

- these files are now difficult to change safely
- behavior is becoming hard to reason about
- every next feature increases regression risk

### 4. Signal logic is duplicated across stages

Examples found in code:

- duplicated token / priority helpers across context, planning, motivation, action, and repository layers
- duplicated `goal_history_signal` logic in planning and motivation
- duplicated `goal_milestone_arc_signal` logic in planning and motivation
- duplicated summary-field parsing in context and reflection

Why it matters:

- the same concept can drift across stages
- future changes will keep multiplying maintenance cost

### 5. Logging is still below the `docs/basics/17_logging_and_debugging.md` target

Current behavior:

- runtime start/end logs exist
- reflection logs exist
- per-stage timing exists in the returned result

Missing compared with basics:

- consistent stage-level input/output summaries
- consistent per-stage failure logging
- a reusable structured logging scaffold

### 6. Database bootstrap still uses a temporary dual path

Current behavior:

- Alembic baseline exists
- startup still calls `create_tables()`

Why it matters:

- schema ownership is still split
- runtime and deploy behavior can diverge

## Delivery Principle

- Keep `docs/basics/` fixed as the architecture source.
- Move code toward basics, not basics toward code.
- Stabilize contracts before adding richer behavior.
- Prefer extraction and consolidation over adding more heuristics into already-large files.
- Keep tasks small enough that an execution agent can finish them in one focused pass.

## Execution Groups

## Group 1 - Runtime Contract Foundation

This group removed the biggest architectural brittleness first.

- `PRJ-006`, `PRJ-007`, and `PRJ-008` are complete.
- Result:
  - episodic memory now has a typed machine-readable payload
  - a readable summary remains available for inspection and logs
  - context and reflection use payload-first reads with legacy fallback
  - regression tests now pin payload writing, payload reading, and old-row fallback

## Group 2 - Motivation And Runtime Contract Alignment

This group removes the clearest code-vs-basics mismatch.

- `PRJ-009` is complete.
  - Result:
    - shared runtime behavior no longer depends on undocumented `support`
    - emotional turns still produce supportive behavior through documented contracts such as role, tone, plan goal, or valence

- `PRJ-010` is complete.
  - Result:
    - emotional-turn behavior is now described at test level across motivation, planning, expression, and the full runtime pipeline
    - the documented contract is readable from regression tests without relying on implementation-only details

## Group 3 - Shared Signal Engine Extraction

This group reduces drift and prepares the runtime for future behavior changes.

- `PRJ-011` Extract shared goal/task selection helpers used by context, motivation, and planning.
  - Files: new shared helper module under `app/utils/` or `app/core/`, plus `app/agents/context.py`, `app/agents/planning.py`, `app/motivation/engine.py`
  - Depends on: none
  - Done when:
    - tokenization, priority ranking, task-status ranking, and related-goal selection no longer live in multiple copies
    - behavior stays unchanged
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- `PRJ-012` Extract shared goal-progress and milestone-history signal helpers.
  - Files: shared helper module plus `app/agents/planning.py`, `app/motivation/engine.py`, `app/reflection/worker.py`
  - Depends on: `PRJ-011`
  - Done when:
    - goal-history and milestone-arc logic have one owner
    - runtime and reflection stop reimplementing the same logic in separate files
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-013` Split oversized heuristic modules after helper extraction, without changing behavior.
  - Files: `app/agents/context.py`, `app/agents/planning.py`, `app/motivation/engine.py`, `app/reflection/worker.py`, new helper modules
  - Depends on: `PRJ-011`, `PRJ-012`
  - Done when:
    - no single runtime heuristic file remains the only place where too many concerns live
    - responsibilities are easier to test in isolation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`

## Group 4 - Observability And Runtime Honesty

This group makes the system easier to operate and safer to evolve.

- `PRJ-014` Add a reusable stage-level structured logging scaffold to the runtime.
  - Files: `app/core/runtime.py`, `app/core/logging.py`, stage modules only if minimal summaries are needed, related tests if added
  - Depends on: none
  - Done when:
    - each stage emits start/end or success/failure logs with `event_id`, `trace_id`, stage name, and duration
    - stage logs include short input/output summaries rather than raw payload dumps
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-015` Tighten the event normalization and public API boundary.
  - Files: `app/core/events.py`, `app/api/routes.py`, `app/api/schemas.py`, related tests
  - Depends on: none
  - Done when:
    - input normalization rules are explicit and test-covered
    - the public `/event` contract stays small and intentional
    - debug behavior remains clearly internal
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_api_routes.py`

- `PRJ-016` Move startup from temporary bootstrap toward migration-first behavior.
  - Files: `app/main.py`, `app/memory/repository.py`, migration helpers/docs/tests as needed
  - Depends on: none
  - Done when:
    - migration-first ownership is explicit
    - startup `create_tables()` is either removed or guarded behind a deliberate compatibility path
    - deploy expectations are documented
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

## Parallel-Ready Lanes

These tasks are intentionally chosen so different execution agents can work in parallel with minimal overlap:

- Lane A: `PRJ-006`
  - ownership: memory schema, repository, action persistence
- Lane B: `PRJ-009`
  - ownership: motivation/planning/expression contract alignment
- Lane C: `PRJ-014`
  - ownership: runtime logging scaffold

After those finish:

- run `PRJ-007`
- then run `PRJ-011` and `PRJ-015`
- then run `PRJ-012`
- then run `PRJ-013`
- finish with `PRJ-016`

## Recommended Execution Order

1. `PRJ-014`
2. `PRJ-011`
3. `PRJ-015`
4. `PRJ-012`
5. `PRJ-013`
6. `PRJ-016`

## Handoff Rules For Execution Agents

When taking the next task:

1. Touch only the files listed for that task unless a local refactor becomes necessary.
2. If scope expands, update `.codex/context/TASK_BOARD.md` before closing the task.
3. Do not mix Group 1 contract work with Group 3 refactors in the same change.
4. Keep behavior-neutral extraction separate from behavior-changing contract fixes.
5. Leave behind the exact validation command and pass result for the touched scope.

## Definition Of Done For This Phase

This phase is complete when:

- episodic memory uses a typed machine-readable contract instead of summary-string parsing as the primary path
- motivation uses only documented shared modes
- duplicated signal logic has one clear owner
- stage-level logging makes runtime decisions observable
- startup schema ownership is migration-first or explicitly guarded as temporary
- docs, code, and `.codex/context/` describe the same runtime truth
