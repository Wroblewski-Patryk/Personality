# Task

## Header
- ID: PRJ-944
- Title: Tools Pipeline Reference
- Task Type: research
- Current Stage: verification
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-937, PRJ-938, PRJ-939
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 944
- Operation Mode: BUILDER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context

The documentation system map already has a pipeline registry and dedicated
docs for foreground runtime, app chat, deferred reflection, and
scheduler/proactive flows. The tools/connectors flow remained compressed in
`docs/pipelines/index.md`, which made preference writes, connector readiness,
Telegram link-code start, and backend-owned permission gates too easy to miss.

## Goal

Create a dedicated tools pipeline reference grounded in the current codebase
and link it from the system map, traceability matrix, registry, and drift
report.

## Scope

- `docs/pipelines/tools.md`
- `docs/pipelines/index.md`
- `docs/index.md`
- `docs/analysis/documentation-drift.md`
- `docs/architecture/traceability-matrix.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Success Signal
- User or operator problem: the tools/connectors behavior is not hidden inside
  a short registry row.
- Expected product or reliability outcome: future connector/tool changes can
  trace UI, API, policy, data, tests, and known provider gaps.
- How success will be observed: docs link to a dedicated tools pipeline and
  validation confirms the important route/policy terms are present.
- Post-launch learning needed: no

## Deliverable For This Stage

A completed documentation slice with validation evidence.

## Constraints

- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it
- repository docs must remain in English

## Implementation Plan

1. Inspect the current tools routes, API client calls, app tools policy,
   connector execution baseline, connector policy, and existing docs.
2. Create `docs/pipelines/tools.md` with trigger paths, runtime flow, data,
   failure points, tests, related modules, docs, and gaps.
3. Update pipeline registry, documentation index, traceability matrix, and
   drift report to point to the dedicated doc.
4. Update `.codex/context/TASK_BOARD.md` and
   `.codex/context/PROJECT_STATE.md`.
5. Validate coverage terms, markdown links, and whitespace.

## Acceptance Criteria

- [x] `docs/pipelines/tools.md` exists and is code-grounded.
- [x] The tools traceability row points to the dedicated pipeline doc.
- [x] Pipeline registry and documentation index link the dedicated doc.
- [x] Drift report records that the compressed registry-only coverage was
  fixed.
- [x] Validation evidence is recorded.

## Definition of Done

- [x] Documentation maps the real code paths instead of invented architecture.
- [x] Missing or unverified areas are marked as gaps.
- [x] Relevant source-of-truth context files are updated.
- [x] No code behavior changed.
- [x] Validation commands passed.

## Stage Exit Criteria
- [x] The output matches the declared `Current Stage`.
- [x] Work from later stages was not mixed in without explicit approval.
- [x] Risks and assumptions for this stage are stated clearly.

## Forbidden

- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval
- implicit stage skipping

## Validation Evidence
- Tests:
  - tools pipeline coverage check passed
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-944-tools-pipeline-reference.md`
- Manual checks:
  - inspected `backend/app/api/routes.py`
  - inspected `backend/app/core/app_tools_policy.py`
  - inspected `backend/app/core/capability_catalog.py`
  - inspected `backend/app/core/connector_execution.py`
  - inspected `backend/app/core/connector_policy.py`
  - inspected `web/src/lib/api.ts`
- Screenshots/logs: not applicable
- High-risk checks: documentation-only; no runtime logic changed
- Coverage ledger updated: not applicable
- Coverage rows closed or changed: none

## Architecture Evidence
- Architecture source reviewed:
  - `docs/architecture/20_action_system.md`
  - `docs/operations/runtime-ops-runbook.md`
  - existing system map docs
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: not applicable
- Follow-up architecture doc updates: none

## UX/UI Evidence
- Design source type: not applicable
- Design source reference: not applicable
- Canonical visual target: not applicable
- Fidelity target: not applicable
- Stitch used: no
- Experience-quality bar reviewed: not applicable
- Visual-direction brief reviewed: not applicable
- Existing shared pattern reused: not applicable
- New shared pattern introduced: no
- Design-memory entry reused: not applicable
- Design-memory update required: no
- Visual gap audit completed: not applicable
- Background or decorative asset strategy: not applicable
- Canonical asset extraction required: no
- Screenshot comparison pass completed: not applicable
- Remaining mismatches: none
- State checks: not applicable
- Feedback locality checked: not applicable
- Raw technical errors hidden from end users: not applicable
- Responsive checks: not applicable
- Input-mode checks: not applicable
- Accessibility checks: not applicable
- Parity evidence: not applicable

## Deployment / Ops Evidence
- Deploy impact: none
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: no
- Rollback note: revert documentation-only changes
- Observability or alerting impact: none
- Staged rollout or feature flag: not applicable

## Review Checklist
- [x] Process self-audit completed before implementation.
- [x] Autonomous loop evidence covers all seven steps.
- [x] Exactly one priority task was completed in this iteration.
- [x] Operation mode was selected according to iteration rotation.
- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes

This is a documentation-only task. It records current behavior and marks
provider-specific docs, connector capability generation, frontend e2e coverage,
and live provider smoke as follow-up gaps.

## Production-Grade Required Contract

This task includes Goal, Scope, Implementation Plan, Acceptance Criteria,
Definition of Done, and Result Report. No runtime implementation was changed.

## Integration Evidence

## Product / Discovery Evidence
- Problem validated: yes
- User or operator affected: future maintainers and agents tracing tool
  readiness
- Existing workaround or pain: infer behavior from code and a compressed
  registry row
- Smallest useful slice: dedicated tools pipeline reference
- Success metric or signal: route/policy coverage terms and links validate
- Feature flag, staged rollout, or disable path: not applicable
- Post-launch feedback or metric check: not applicable

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: not applicable
- Critical user journey: tools readiness inspection and preference persistence
- SLI: not applicable
- SLO: not applicable
- Error budget posture: not applicable
- Health/readiness check: connector readiness surfaces documented
- Logs, dashboard, or alert route: `/health` connector sections documented
- Smoke command or manual smoke: not applicable
- Rollback or disable path: revert docs

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: yes
- Endpoint and client contract match: yes
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: not applicable
- Regression check performed: documentation link and coverage checks

## AI Testing Evidence

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: not applicable
- Data classification: docs-only reference to user preferences/profile link
  state
- Trust boundaries: backend-owned connector permission gates documented
- Permission or ownership checks: authenticated app routes documented
- Abuse cases: frontend must not reconstruct connector authorization
- Secret handling: no secrets read or written
- Security tests or scans: not applicable
- Fail-closed behavior: Telegram link start `409` when provider is not
  configured documented
- Residual risk: provider-specific docs remain incomplete

- `AI_TESTING_PROTOCOL.md` reviewed: not applicable
- Memory consistency scenarios: not applicable
- Multi-step context scenarios: not applicable
- Adversarial or role-break scenarios: not applicable
- Prompt injection checks: not applicable
- Data leakage and unauthorized access checks: not applicable
- Result: not applicable

## Result Report

- Task summary: created a dedicated tools pipeline reference and linked it into
  the documentation system map.
- Files changed:
  - `docs/pipelines/tools.md`
  - `docs/pipelines/index.md`
  - `docs/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/tasks/PRJ-944-tools-pipeline-reference.md`
- How tested: coverage term check, local markdown link check, and
  `git diff --check`.
- What is incomplete: provider-specific docs, generated connector matrix,
  frontend e2e for tools toggles/link start, and live provider smoke.
- Next steps: add stable feature/pipeline IDs to tests or create a test
  ownership ledger.
- Decisions made: documented the existing backend-owned readiness and
  permission model without changing architecture.

## Autonomous Loop Evidence

### 1. Analyze Current State
- Issues: tools/connectors had only compressed registry-level documentation.
- Gaps: preference writes, connector readiness, permission gates, and Telegram
  link start were not mapped in one place.
- Inconsistencies: no architecture mismatch found.
- Architecture constraints: action/connector authorization stays backend-owned.

### 2. Select One Priority Task
- Selected task: PRJ-944 Tools Pipeline Reference.
- Priority rationale: it was the next documented repair loop after PRJ-943.
- Why other candidates were deferred: test ownership metadata is a larger
  follow-up and should not be mixed into this documentation slice.

### 3. Plan Implementation
- Files or surfaces to modify: docs index, pipeline registry, traceability
  matrix, drift report, context files, task contract.
- Logic: documentation only.
- Edge cases: mark provider docs and live smoke gaps instead of inventing
  provider readiness.

### 4. Execute Implementation
- Implementation notes: created a dedicated pipeline doc and relinked the
  tools feature row from the registry anchor to the dedicated file.

### 5. Verify and Test
- Validation performed: coverage terms, local links, whitespace.
- Result: passed.

### 6. Self-Review
- Simpler option considered: leave the registry row as-is.
- Technical debt introduced: no
- Scalability assessment: the dedicated doc can absorb future provider-specific
  detail without bloating the registry.
- Refinements made: explicitly separated provider readiness, user preferences,
  and permission-gate ownership.

### 7. Update Documentation and Knowledge
- Docs updated: yes
- Context updated: yes
- Learning journal updated: not applicable.
