# Task

## Header
- ID: PRJ-956
- Title: Release Reality Audit Script
- Task Type: feature
- Current Stage: verification
- Status: DONE
- Owner: Ops/Release
- Depends on: PRJ-951
- Priority: P0
- Coverage Ledger Rows: not applicable
- Iteration: 956
- Operation Mode: TESTER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
PRJ-938 showed that release reality checks are spread across git commands,
production `/health`, production web meta revision, and release smoke. PRJ-951
made the gap explicit. The repo needs one local operator command that prints
the current release reality before anyone claims v1 is deployed.

## Goal
Add a small script that compares local Git HEAD, `origin/main`, production
backend revision, production web revision, `/health.release_readiness`, and
`/health.v1_readiness` in one repeatable command.

## Scope
- `backend/scripts/`
- `backend/tests/test_deployment_trigger_scripts.py` or a focused new script
  test file if needed
- `docs/operations/runtime-ops-runbook.md`
- `docs/planning/v1-reality-audit-and-roadmap.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-956-release-reality-audit-script.md`

## Implementation Plan
1. Reuse existing release-smoke and deployment-policy conventions.
2. Add a read-only script with PowerShell and/or Python entrypoint consistent
   with existing script patterns.
3. Report:
   - local `HEAD`
   - `origin/main`
   - production backend runtime revision
   - production web meta revision
   - release readiness ready/violations
   - v1 final acceptance state/gates
   - final verdict: `GO_FOR_SELECTED_SHA`, `HOLD_REVISION_DRIFT`, or
     `HOLD_HEALTH_OR_READINESS`
4. Add tests for parsing, verdict selection, and help output.
5. Document the command in ops/release docs.

## Acceptance Criteria
- Script runs without secrets.
- Script is read-only and safe against production.
- Script returns non-zero when production does not match the selected SHA.
- Tests cover revision-drift verdict behavior.
- Docs show when to run it before release smoke or tagging.

## Definition of Done
- [x] `DEFINITION_OF_DONE.md` relevant checks are satisfied.
- [x] Script and tests are implemented.
- [x] Docs/context are updated.
- [x] Relevant validation passes.

## Stage Exit Criteria
- [x] The output matches the declared `Current Stage`.
- [x] Work from later stages was not mixed in.
- [x] Risks and assumptions for this stage are stated clearly.

## Forbidden
- triggering deployment
- reading or writing secrets
- creating release markers
- replacing release smoke

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "release_reality_audit or backend_operator_scripts_expose_help"; Pop-Location`
  - result: `11 passed, 44 deselected`
- Manual checks:
  - `Push-Location .\backend; ..\.venv\Scripts\python .\scripts\audit_release_reality.py --base-url "https://aviary.luckysparrow.ch"; Pop-Location`
  - result: exited non-zero with `HOLD_REVISION_DRIFT`, selected SHA
    `0011d5c932700531d2a617fae18aeb57c1b3695f`, production backend/web SHA
    `c7c3db639443df7ba5c26edacaf1e5ca368dd3f5`
- Screenshots/logs:
  - not applicable
- High-risk checks:
  - script must be read-only
- Coverage ledger updated: not applicable
- Coverage rows closed or changed: none

## Architecture Evidence
- Architecture source reviewed:
  - `docs/operations/runtime-ops-runbook.md`
  - `docs/planning/v1-reality-audit-and-roadmap.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: not applicable
- Follow-up architecture doc updates:
  - ops command docs

## Deployment / Ops Evidence
- Deploy impact: none
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: yes, documentation only
- Rollback note: not applicable
- Observability or alerting impact: improves release preflight visibility
- Staged rollout or feature flag: not applicable

## Result Report
- Task summary:
  - added a read-only release reality audit script that blocks release marker
    claims when production backend/web revisions drift from the selected SHA
- Files changed:
  - `backend/scripts/audit_release_reality.py`
  - `backend/scripts/audit_release_reality.ps1`
  - `backend/tests/test_deployment_trigger_scripts.py`
  - `docs/operations/runtime-ops-runbook.md`
  - `docs/planning/v1-reality-audit-and-roadmap.md`
  - context files
- How tested:
  - focused pytest and live production audit command
- What is incomplete:
  - none for script implementation
- Next steps:
  - `PRJ-957` revision-aware production health monitor
- Decisions made:
  - the audit script is read-only and returns non-zero for all `HOLD_*` states

## Autonomous Loop Evidence

### 1. Analyze Current State
- Issues:
  - release reality is checked through multiple commands
- Gaps:
  - no single preflight verdict command
- Inconsistencies:
  - health gates can be green for an older SHA while current candidate is not
    deployed
- Architecture constraints:
  - release marker follows green evidence

### 2. Select One Priority Task
- Selected task:
  - PRJ-956 Release Reality Audit Script
- Priority rationale:
  - local, unblocked, and directly addresses the PRJ-938 failure mode
- Why other candidates were deferred:
  - deploy recovery needs operator/Coolify access

### 3. Plan Implementation
- Files or surfaces to modify:
  - backend scripts, script tests, ops docs, context
- Logic:
  - read-only revision/readiness comparison
- Edge cases:
  - web meta missing
  - health unavailable
  - no origin/main ref

### 4. Execute Implementation
- Implementation notes:
  - added Python and PowerShell entrypoints
  - added verdict states for revision drift, missing revision, readiness hold,
    v1 acceptance hold, and selected-SHA GO

### 5. Verify And Test
- Validation performed:
  - focused pytest and live production audit command
- Result:
  - script works and blocks release marker on revision drift

### 6. Self-Review
- Simpler option considered:
  - documenting manual commands only, rejected because PRJ-938 showed manual
    release checks are too easy to scatter
- Technical debt introduced: no
- Scalability assessment:
  - script can later feed PRJ-970 go/no-go wrapper
- Refinements made:
  - kept it separate from release smoke so it remains a fast preflight

### 7. Update Documentation And Knowledge
- Docs updated:
  - runtime ops runbook and roadmap
- Context updated:
  - task board and project state
- Learning journal updated: not applicable
