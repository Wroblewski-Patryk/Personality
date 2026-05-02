# Task

## Header
- ID: PRJ-940
- Title: Foreground Runtime Pipeline Reference
- Task Type: research
- Current Stage: verification
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-939
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 940
- Operation Mode: TESTER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
The pipeline registry now exists, and PRJ-939 left the next smallest useful
task as splitting high-risk pipeline entries into dedicated docs, starting with
foreground runtime.

## Goal
Create a dedicated foreground runtime pipeline reference that shows trigger
paths, stage order, stage contracts, data dependencies, side-effect boundaries,
failure points, tests, and known gaps.

## Scope
- `docs/pipelines/foreground-runtime.md`
- `docs/pipelines/index.md`
- `docs/index.md`
- `docs/architecture/traceability-matrix.md`
- `docs/analysis/documentation-drift.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- this task file

## Implementation Plan
1. Inspect `backend/app/core/runtime.py`, `backend/app/core/runtime_graph.py`,
   `backend/app/core/contracts.py`, and runtime graph tests.
2. Add a dedicated foreground runtime pipeline doc.
3. Link it from the pipeline registry, docs index, traceability matrix, and
   drift report.
4. Validate links, expected stage names, and whitespace.
5. Sync task board and project state.

## Acceptance Criteria
- Dedicated foreground runtime doc exists and is linked from registry/index.
- Stage order matches `runtime_graph.py`.
- Side-effect boundary and post-graph followups are explicit.
- Tests and known gaps are explicit.

## Definition of Done
- [x] Foreground runtime pipeline doc exists and is linked.
- [x] Stage order and key contracts match inspected code.
- [x] Validation evidence is recorded.
- [x] Context files are updated.

## Deliverable For This Stage
Implementation-stage dedicated foreground runtime pipeline reference.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Forbidden
- changing runtime behavior
- inventing stages or side effects
- hiding unverified gaps
- weakening the action boundary

## Validation Evidence
- Tests: not applicable for docs-only change
- Manual checks:
  - stage-order coverage check passed for `perception -> affective_assessment -> context -> motivation -> role -> planning -> expression -> action`
  - local markdown link check passed
  - forbidden-template-reference scan passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-940-foreground-runtime-pipeline-reference.md` passed
- Screenshots/logs: not applicable
- High-risk checks: runtime stage order and side-effect boundary reviewed
- Coverage ledger updated: not applicable
- Coverage rows closed or changed: not applicable

## Architecture Evidence
- Architecture source reviewed:
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/pipelines/index.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: not applicable
- Follow-up architecture doc updates: pipeline reference links only.

## Result Report
- Task summary: created the dedicated foreground runtime pipeline reference
  grounded in runtime orchestration, graph stage order, contracts, and tests.
- Files changed:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/tasks/PRJ-940-foreground-runtime-pipeline-reference.md`
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/pipelines/foreground-runtime.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- How tested:
  - stage-order coverage check
  - local markdown link check
  - forbidden-template-reference scan
  - `git diff --check`
- What is incomplete:
  - rendered sequence diagram
  - generated stage contract table from `backend/app/core/contracts.py`
  - dedicated app chat, reflection, scheduler/proactive, and tools pipeline docs
  - stable feature or pipeline IDs in tests
- Next steps: create a dedicated app chat pipeline doc.
- Decisions made: document-only split; no runtime behavior changed.

## Autonomous Loop Evidence

### 1. Analyze Current State
- Issues:
  - Foreground runtime is the highest-risk central pipeline and currently only
    has a registry entry.
- Gaps:
  - no dedicated pipeline doc with stage contracts and failure points.
- Inconsistencies:
  - none found before implementation.
- Architecture constraints:
  - preserve canonical runtime order and action boundary.

### 2. Select One Priority Task
- Selected task: PRJ-940 Foreground Runtime Pipeline Reference.
- Priority rationale: it is the highest-risk pipeline and first explicit
  follow-up after the data reference.
- Why other candidates were deferred: app chat/reflection/scheduler docs should
  build on the foreground runtime reference.

### 3. Plan Implementation
- Files or surfaces to modify: docs/context files listed in Scope.
- Logic: document stage order, contracts, data dependencies, side effects,
  failure points, tests, and gaps from inspected code.
- Edge cases:
  - runtime graph stage order differs from the broader architecture sequence
    because memory/reflection are post-graph followups; document that clearly.

### 4. Execute Implementation
- Implementation notes:
  - added `docs/pipelines/foreground-runtime.md`
  - linked it from the pipeline registry, docs index, traceability matrix, and
    drift report
  - documented graph stage order separately from post-graph memory/reflection
    followups

### 5. Verify and Test
- Validation performed:
  - stage-order coverage check
  - local markdown link check
  - forbidden-template-reference scan
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-940-foreground-runtime-pipeline-reference.md`
- Result: passed.

### 6. Self-Review
- Simpler option considered: leave registry entry only; rejected because it
  keeps the central pipeline too compressed.
- Technical debt introduced: no
- Scalability assessment: dedicated file can be expanded with diagrams later.
- Refinements made:
  - kept Telegram/durable inbox and due planned-work as related trigger paths
    that still need dedicated docs
  - marked generated contract tables and test pipeline IDs as gaps

### 7. Update Documentation and Knowledge
- Docs updated:
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/pipelines/foreground-runtime.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- Context updated:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
- Learning journal updated: not applicable.
