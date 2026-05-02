# Task

## Header
- ID: PRJ-941
- Title: App Chat Pipeline Reference
- Task Type: research
- Current Stage: verification
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-940
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 941
- Operation Mode: BUILDER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
PRJ-940 split the central foreground runtime pipeline into a dedicated doc. App
chat is the main product-facing path that exercises that runtime and durable
transcript projection.

## Goal
Create a dedicated app chat pipeline reference covering frontend optimistic
state, backend routes, runtime handoff, durable transcript projection, failure
points, and tests.

## Scope
- `docs/pipelines/app-chat.md`
- `docs/pipelines/index.md`
- `docs/index.md`
- `docs/architecture/traceability-matrix.md`
- `docs/analysis/documentation-drift.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- this task file

## Implementation Plan
1. Inspect `web/src/App.tsx`, `web/src/lib/api.ts`,
   `backend/app/api/routes.py`, `backend/app/memory/repository.py`, and
   chat/transcript tests.
2. Add a dedicated app chat pipeline doc.
3. Link it from the pipeline registry, docs index, traceability matrix, and
   drift report.
4. Validate required endpoint/client/transcript references, links, and
   whitespace.
5. Sync task board and project state.

## Acceptance Criteria
- Dedicated app chat doc exists and is linked.
- The doc covers send, history refresh, optimistic local items, reconciliation,
  runtime handoff, transcript projection, tests, and gaps.
- Validation evidence is recorded.
- Context files are updated.

## Definition of Done
- [x] App chat pipeline doc exists and is linked.
- [x] Key frontend/API/repository/test references are present.
- [x] Validation evidence is recorded.
- [x] Context files are updated.

## Deliverable For This Stage
Implementation-stage dedicated app chat pipeline reference.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Forbidden
- changing runtime or frontend code
- inventing transcript behavior
- hiding failure or test gaps

## Validation Evidence
- Tests: not applicable for docs-only change
- Manual checks:
  - app chat reference coverage check passed for 8 key terms
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-941-app-chat-pipeline-reference.md` passed

## Result Report
- Task summary: created the dedicated app chat pipeline reference grounded in
  frontend chat state, app API routes, runtime handoff, repository transcript
  projection, and tests.
- Files changed:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/tasks/PRJ-941-app-chat-pipeline-reference.md`
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/pipelines/app-chat.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- How tested:
  - app chat reference coverage check
  - local markdown link check
  - `git diff --check`
- What is incomplete:
  - dedicated frontend e2e tests for chat send/history UI
  - app chat sequence diagram
  - dedicated docs for long-message/markdown rendering behavior
- Next steps: create a dedicated deferred reflection pipeline doc.
- Decisions made: document-only split; no frontend, API, runtime, or repository
  behavior changed.

## Autonomous Loop Evidence

### 1. Analyze Current State
- Issues:
  - App chat is product-critical and only had a compact registry entry.
- Gaps:
  - no dedicated flow doc for optimistic UI and durable transcript truth.
- Inconsistencies:
  - none found before implementation.
- Architecture constraints:
  - durable transcript truth remains backend-owned; local UI items are
    transient.

### 2. Select One Priority Task
- Selected task: PRJ-941 App Chat Pipeline Reference.
- Priority rationale: app chat is the main frontend path through foreground
  runtime and transcript persistence.
- Why other candidates were deferred: reflection/scheduler/tools can follow
  after the primary product chat path.

### 3. Plan Implementation
- Files or surfaces to modify: docs/context files listed in Scope.
- Logic: document frontend local state, API routes, runtime handoff,
  repository transcript projection, failures, and tests.
- Edge cases:
  - distinguish transient local transcript items from durable backend truth.

### 4. Execute Implementation
- Implementation notes:
  - added `docs/pipelines/app-chat.md`
  - linked it from the pipeline registry, docs index, traceability matrix, and
    drift report
  - explicitly separated transient local UI transcript items from backend-owned
    durable transcript truth

### 5. Verify and Test
- Validation performed:
  - app chat reference coverage check
  - local markdown link check
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-941-app-chat-pipeline-reference.md`
- Result: passed.

### 6. Self-Review
- Simpler option considered: leave foreground runtime doc only; rejected
  because chat-specific UI reconciliation is a separate source of drift.
- Technical debt introduced: no
- Scalability assessment: doc can later be expanded with screenshots or e2e
  frontend checks.
- Refinements made:
  - kept frontend e2e tests and sequence diagram as explicit gaps
  - documented role-aware reconciliation as a key drift guardrail

### 7. Update Documentation and Knowledge
- Docs updated:
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/pipelines/app-chat.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- Context updated:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
- Learning journal updated: not applicable.
