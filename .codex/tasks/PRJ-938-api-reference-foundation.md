# Task

## Header
- ID: PRJ-938
- Title: API Reference Foundation
- Task Type: research
- Current Stage: verification
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-937
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 938
- Operation Mode: BUILDER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
PRJ-937 created the documentation system-map foundation and identified the
missing dedicated API reference as the next smallest useful task.

## Goal
Create a first-pass API reference grounded in real FastAPI routes, Pydantic
schemas, and the web API client so route ownership and frontend/backend
contract drift are easier to detect.

## Scope
- `docs/api/index.md`
- `docs/index.md`
- `docs/README.md`
- `docs/architecture/codebase-map.md`
- `docs/architecture/traceability-matrix.md`
- `docs/analysis/documentation-drift.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- this task file

## Implementation Plan
1. Inspect `backend/app/api/routes.py`, `backend/app/api/schemas.py`, and
   `web/src/lib/api.ts`.
2. Create `docs/api/index.md` with endpoint purpose, auth posture, request and
   response schemas, side effects, frontend callers, tests, and related
   pipelines.
3. Link the API reference from existing documentation map entrypoints and
   traceability docs.
4. Update drift/context to mark the API-reference foundation complete and leave
   deeper OpenAPI/schema-generation gaps explicit.
5. Validate docs paths, local markdown links, and whitespace.

## Acceptance Criteria
- Every route verified in `backend/app/api/routes.py` appears in the API
  reference.
- App-facing routes name their web client caller where one exists.
- Debug/internal/operator routes describe access posture without exposing
  secrets.
- Remaining API documentation gaps are explicit.

## Definition of Done
- [x] API reference exists and is linked from docs entrypoints.
- [x] Every verified endpoint is represented.
- [x] Validation evidence is recorded.
- [x] Context files are updated.

## Deliverable For This Stage
Implementation-stage API reference foundation and system-map updates.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Forbidden
- invented endpoints, schemas, or auth behavior
- documenting secret values
- changing runtime code
- presenting inferred behavior as verified

## Validation Evidence
- Tests: not applicable for docs-only change
- Manual checks:
  - endpoint coverage check passed for 18 routes including dynamic constants
  - local markdown link check passed
  - forbidden-template-reference scan passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-938-api-reference-foundation.md` passed
- Screenshots/logs: not applicable
- High-risk checks: route/schema/client paths reviewed
- Coverage ledger updated: not applicable
- Coverage rows closed or changed: not applicable

## Architecture Evidence
- Architecture source reviewed:
  - `docs/architecture/codebase-map.md`
  - `docs/architecture/traceability-matrix.md`
  - `docs/pipelines/index.md`
  - `docs/CONTRIBUTING-DOCS.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: not applicable
- Follow-up architecture doc updates: API reference links only.

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
- Remaining mismatches: not applicable
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
- Smoke steps updated: no runtime smoke change
- Rollback note: revert docs/context changes if superseded
- Observability or alerting impact: none
- Staged rollout or feature flag: not applicable

## Production-Grade Required Contract
- Goal: create a verified first-pass API reference.
- Scope: docs and context files listed above.
- Implementation Plan: see above.
- Acceptance Criteria: see above.
- Definition of Done: use documentation-only applicability.
- Result Report: complete.

## Integration Evidence
- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: documentation-only inspection of real code paths
- Endpoint and client contract match: documentation-only check
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: not applicable
- Regression check performed: pending

## Product / Discovery Evidence
- Problem validated: yes
- User or operator affected: maintainers and future agents
- Existing workaround or pain: endpoint behavior had to be inferred from route
  code and web client calls
- Smallest useful slice: one API reference index before deeper generated
  schema work
- Success metric or signal: all verified routes are listed with schemas,
  callers, side effects, and tests
- Feature flag, staged rollout, or disable path: not applicable
- Post-launch feedback or metric check: yes

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: not applicable
- Critical user journey: documentation handoff
- SLI: not applicable
- SLO: not applicable
- Error budget posture: not applicable
- Health/readiness check: API reference includes `/health`
- Logs, dashboard, or alert route: not applicable
- Smoke command or manual smoke: docs sanity checks passed
- Rollback or disable path: revert docs/context changes

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: not applicable
- Data classification: repository documentation; no secrets
- Trust boundaries: app auth, debug access, and operator-only posture are
  documented at a high level
- Permission or ownership checks: no runtime change
- Abuse cases: avoid exposing secret/token values
- Secret handling: no secrets included
- Security tests or scans: not applicable
- Fail-closed behavior: not applicable
- Residual risk: deeper OpenAPI/schema sync remains manual

## AI Testing Evidence
- `AI_TESTING_PROTOCOL.md` reviewed: not applicable
- Memory consistency scenarios: not applicable
- Multi-step context scenarios: not applicable
- Adversarial or role-break scenarios: not applicable
- Prompt injection checks: not applicable
- Data leakage and unauthorized access checks: not applicable
- Result: not applicable

## Result Report
- Task summary: created the first dedicated API reference grounded in FastAPI
  routes, Pydantic schemas, and the web API client.
- Files changed:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/tasks/PRJ-938-api-reference-foundation.md`
  - `docs/README.md`
  - `docs/index.md`
  - `docs/api/index.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/codebase-map.md`
  - `docs/architecture/traceability-matrix.md`
- How tested:
  - endpoint coverage check for 18 routes including dynamic route constants
  - local markdown link check
  - forbidden-template-reference scan
  - `git diff --check`
- What is incomplete:
  - generated OpenAPI artifact or richer per-endpoint examples
  - deeper shape docs for flexible `extra="allow"` overview responses
  - dedicated event/debug payload contract reference
  - test endpoint IDs or ownership metadata
- Next steps: create `docs/data/index.md` with model/table/migration/repository
  mapping.
- Decisions made: the API reference remains documentation-only and does not
  alter runtime code or route contracts.

## Autonomous Loop Evidence

### 1. Analyze Current State
- Issues:
  - PRJ-937 explicitly left the API reference as the next gap.
  - Routes, schemas, and frontend calls exist but were not documented in one
    API reference.
- Gaps:
  - no `docs/api/index.md`
  - no endpoint-by-endpoint auth/schema/side-effect map
- Inconsistencies:
  - none found before implementation.
- Architecture constraints:
  - documentation must reflect real route code and avoid changing runtime
    architecture.

### 2. Select One Priority Task
- Selected task: PRJ-938 API Reference Foundation.
- Priority rationale: it is the first explicit follow-up from PRJ-937 and
  reduces route/client drift risk.
- Why other candidates were deferred: data/model reference is next, but API
  reference was the documented immediate follow-up.

### 3. Plan Implementation
- Files or surfaces to modify: docs/context files listed in Scope.
- Logic: create route reference from inspected backend routes, schemas, and web
  client methods.
- Edge cases:
  - internal/debug routes must not reveal secrets
  - dynamic debug internal path is documented by canonical path name
  - broad extra-allow overview schemas remain marked as shape-flexible

### 4. Execute Implementation
- Implementation notes:
  - added `docs/api/index.md`
  - linked it from docs entrypoints, codebase map, traceability matrix,
    inventory, and drift report
  - marked deeper API contract gaps explicitly instead of treating the first
    reference as full generated OpenAPI coverage

### 5. Verify and Test
- Validation performed:
  - endpoint coverage check
  - local markdown link check
  - forbidden-template-reference scan
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-938-api-reference-foundation.md`
- Result: passed.

### 6. Self-Review
- Simpler option considered: only add a route list; rejected because it would
  not capture auth, callers, side effects, and tests.
- Technical debt introduced: no
- Scalability assessment: single index can later be split or generated.
- Refinements made:
  - documented the dynamic `DEBUG_INTERNAL_INGRESS_PATH` route explicitly as
    `/internal/event/debug`
  - kept flexible response schemas marked as shape-flexible rather than
    inventing unverified nested fields

### 7. Update Documentation and Knowledge
- Docs updated:
  - `docs/README.md`
  - `docs/index.md`
  - `docs/api/index.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/codebase-map.md`
  - `docs/architecture/traceability-matrix.md`
- Context updated:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
- Learning journal updated: not applicable.
