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

Completed on 2026-04-18:

- `PRJ-014` added a reusable structured runtime-stage logging scaffold with `start/success/failure` logs, short summaries, and regression coverage for both success and failure paths.
- `PRJ-011` extracted shared goal/task selection helpers used by context, planning, and motivation.
- `PRJ-012` extracted shared goal-progress and milestone-history signal helpers and wired reflection to the shared milestone-arc signal owner.
- `PRJ-013` completed the post-extraction module split by removing duplicated heuristic logic from oversized runtime modules while preserving behavior.

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

### 3. Core heuristic modules are still substantial even after extraction

Current file sizes on 2026-04-18:

- `app/reflection/worker.py`: 1318 lines
- `app/agents/context.py`: 751 lines
- `app/agents/planning.py`: 676 lines
- `app/motivation/engine.py`: 489 lines

Why it matters:

- the extraction lowered risk, but reflection and context are still large
- future behavior work should prefer focused modules and helper ownership

### 4. Signal logic is duplicated across stages

Examples found in code:

- this gap is largely resolved by the shared owners:
  - `app/utils/goal_task_selection.py`
  - `app/utils/progress_signals.py`
- remaining duplication risk now sits mainly in summary rendering/parsing details, not core selection/scoring logic

Why it matters:

- shared owners reduce drift and simplify future changes
- remaining cleanup can now be incremental instead of high-risk rewrites

### 5. Logging still needs to grow beyond the new stage scaffold

Current behavior:

- runtime start/end logs exist
- reflection logs exist
- per-stage timing exists in the returned result
- runtime stages now emit structured `start/success/failure` logs with short summaries

Missing compared with basics:

- richer cross-component summaries outside the orchestrator
- broader adoption of the scaffold in non-runtime services where useful

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

- `PRJ-011` is complete.
  - Result:
    - tokenization, ranking, and goal/task selection now use shared helpers with one owner
    - context, planning, and motivation consume the same selection primitives

- `PRJ-012` is complete.
  - Result:
    - goal-history and milestone-arc signal logic now has a shared utility owner
    - reflection milestone-arc derivation now reuses the shared signal helper instead of duplicating logic

- `PRJ-013` is complete.
  - Result:
    - oversized heuristic modules were reduced by extracting shared concerns to utility modules
    - behavior remained stable under targeted and full regression test runs

## Group 4 - Observability And Runtime Honesty

This group makes the system easier to operate and safer to evolve.

- `PRJ-014` is complete.
  - Result:
    - runtime stages now emit structured `start/success/failure` logs with `event_id`, `trace_id`, stage name, duration, and short summaries
    - regression tests cover both the happy path and a `memory_persist` failure path

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

## Post-Current Queue Expansion

The current recommended execution order stays unchanged through `PRJ-016`.

The groups below are intentionally appended after that queue so the repo keeps
an explicit architecture-alignment backlog instead of implying that current
tasks fully close the gap between docs and code.

These groups are a later wave, not a replacement for the active queue.

## Group 5 - Stage Boundary Alignment

This group makes the documented action boundary more visible in code without
forcing a risky broad rewrite first.

- `PRJ-017` Make the expression-to-action handoff explicit and test-covered.
  - Files: `app/core/runtime.py`, `app/action/`, `app/expression/`, related docs/tests
  - Depends on: `PRJ-016`
  - Done when:
    - expression hands action a deliberate delivery contract rather than an
      implicit payload shape
    - the action boundary stays explicit in code and docs
    - current user-facing behavior remains unchanged
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_expression_agent.py`

- `PRJ-018` Reduce expression/action integration coupling without changing behavior.
  - Files: `app/action/`, `app/integrations/`, `app/core/runtime.py`, related tests
  - Depends on: `PRJ-017`
  - Done when:
    - channel integrations consume the explicit contract instead of runtime-only
      assumptions
    - side effects still remain isolated inside action
    - the runtime is easier to evolve toward stricter stage parity later
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_telegram_webhook.py`

## Group 6 - Architecture Traceability And Contract Tests

This group makes the implemented architecture easier to audit and harder to let
drift silently.

- `PRJ-019` Add runtime stage ownership and architecture-to-code traceability.
  - Files: `docs/overview.md`, `docs/architecture/02_architecture.md`, `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`, `.codex/context/PROJECT_STATE.md`
  - Depends on: `PRJ-016`
  - Done when:
    - each documented stage names its code owner and main validation surface
    - current-runtime differences remain explicit and searchable
    - the repo truth can be audited faster during future refactors
  - Validation:
    - doc-only change, no automated validation required

- `PRJ-020` Add contract-level runtime flow smoke tests for architecture invariants.
  - Files: `tests/test_runtime_pipeline.py`, `tests/test_api_routes.py`, `tests/test_logging.py`, related helper fixtures
  - Depends on: `PRJ-017`, `PRJ-019`
  - Done when:
    - tests pin documented stage presence, action-boundary rules, and traceable
      runtime result/log invariants
    - future architectural drift causes fast, obvious failures
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py`

## Parallel-Ready Lanes

These tasks are intentionally chosen so different execution agents can work in parallel with minimal overlap:

- Completed lane examples:
  - `PRJ-006`
    - ownership: memory schema, repository, action persistence
  - `PRJ-009`
    - ownership: motivation/planning/expression contract alignment
  - `PRJ-014`
    - ownership: runtime logging scaffold

After those finished:

- run `PRJ-015`
- then run `PRJ-016`
- then run `PRJ-017`
- then run `PRJ-019`
- then run `PRJ-018`
- then run `PRJ-020`

## Recommended Execution Order

1. `PRJ-015`
2. `PRJ-016`
3. `PRJ-017`
4. `PRJ-019`
5. `PRJ-018`
6. `PRJ-020`

The queue should still be treated as intentionally open after those items.
Additional small architecture-alignment slices may still be discovered while
executing Groups 4 through 6.

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
- runtime stage ownership is traceable from docs to code and tests
- docs, code, and `.codex/context/` describe the same runtime truth
