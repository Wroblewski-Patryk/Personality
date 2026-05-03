# Backend Architecture Quality Audit And Improvement Plan

## Header
- ID: PRJ-785
- Title: Backend Architecture Quality Audit And Improvement Plan
- Task Type: research
- Current Stage: release
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-783
- Priority: P1

## Context

The backend runtime now has a coherent canonical architecture, production health
is green, and the communication-boundary repair from `PRJ-778` plus `PRJ-783`
is deployed. The next backend improvement should therefore avoid inventing a
new memory or subconscious subsystem. It should audit the current
implementation against the approved architecture and turn remaining quality
risks into small, reversible backend slices.

Reviewed source-of-truth:

- `docs/architecture/02_architecture.md`
- `docs/architecture/15_runtime_flow.md`
- `docs/architecture/16_agent_contracts.md`
- `docs/architecture/29_runtime_behavior_testing.md`
- `docs/planning/next-iteration-plan.md`
- `docs/planning/open-decisions.md`
- `DEFINITION_OF_DONE.md`
- `AI_TESTING_PROTOCOL.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/context/TASK_BOARD.md`

Current production evidence on 2026-04-29:

- `GET https://aviary.luckysparrow.ch/health` returned `status=ok`
- deployed runtime build revision is `9f04a928f907afaa30d0bdeced6e21ce4b2dce53`
- `release_readiness.ready=true`
- `proactive.communication_boundary_contract` is present
- `conversation_channels.telegram.round_trip_state=provider_backed_ready`
- semantic retrieval is provider-backed by OpenAI and reports `ready`
- affective assessment remains policy-disabled and uses deterministic baseline

## Goal

Create a concrete backend improvement roadmap that keeps Aviary aligned with
the canonical pipeline:

`event -> perception -> context -> motivation -> role -> planning -> expression -> action -> memory -> reflection`

The plan must improve runtime quality without bypassing the action boundary,
duplicating persistence paths, or replacing relation/reflection/planning
contracts with exception handling.

## Scope

Planning-only audit over these backend areas:

- runtime orchestration and graph ownership
- memory repository and retrieval lifecycle
- planning typed-intent ownership
- action boundary and delivery handoff
- reflection, proposal, and subconscious handoff
- proactive cadence and communication-boundary governance
- API route and health surface ownership
- behavior validation and AI safety evidence
- production runbook and operator scripts

No source-code implementation is included in this task.

## Implementation Plan

1. Close the deployed communication-boundary lane operationally:
   - run the production communication-boundary backfill dry-run
   - run the bounded write pass if dry-run evidence is sane
   - record health and operator evidence
2. Expand behavior validation before deeper refactors:
   - add multi-turn scenarios for memory influence, communication boundaries,
     proactive silence, linked-channel continuity, and prompt injection
   - ensure behavior validation proves stored state changes later behavior
3. Split large backend owners behavior-neutrally:
   - first health composition out of `backend/app/api/routes.py`
   - then domain repository interfaces out of `backend/app/memory/repository.py`
   - then planning intent builders out of `backend/app/agents/planning.py`
   - finally action executors by domain family out of `backend/app/core/action.py`
4. Harden subconscious and proactive observability:
   - expose why proactive candidates were delivered, deferred, or suppressed
   - include communication-boundary and planned-work evidence in incident
     bundles
5. Move affective assessment from deterministic baseline to governed rollout:
   - enable only behind explicit policy, confidence, fallback, and safety gates
   - add red-team scenarios before production enablement
6. Standardize runtime scripts and release proof:
   - verify direct script entrypoints from the documented backend working
     directory
   - align runbook, health, and release smoke for any changed operator path

## Acceptance Criteria

- Each follow-up is small enough to ship with focused tests and full backend
  regression when runtime behavior changes.
- Refactors are behavior-neutral unless the task explicitly declares a behavior
  change.
- No follow-up introduces a parallel memory, reminder, proactive, or
  communication-preference subsystem.
- AI-affect or memory changes include reproducible multi-turn scenarios from
  `AI_TESTING_PROTOCOL.md`.
- Runtime and ops changes include health or smoke evidence.

## Definition of Done

- [x] Current architecture source-of-truth was reviewed.
- [x] Current backend code shape was sampled for ownership and file-size risk.
- [x] Production health posture was checked.
- [x] Improvement lanes are ordered by risk and dependency.
- [x] Follow-up implementation tasks are executed and validated separately.

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

## Proposed Follow-Up Queue

### PRJ-786 Production Communication-Boundary Backfill Closure

- Stage: release
- Priority: P0
- Owner: Ops/Release
- Scope:
  - production Coolify shell
  - `backend/scripts/run_communication_boundary_backfill_once.py`
  - `/health.proactive.communication_boundary_contract`
- Goal:
  - finish the only remaining production follow-up after `PRJ-783`
- Acceptance:
  - dry-run evidence captured
  - write-run executed or explicitly skipped with reason
  - health still green after run

### PRJ-787 Behavior Validation Expansion For Backend Continuity

- Stage: implementation
- Priority: P1
- Owner: QA/Test
- Scope:
  - `backend/scripts/run_behavior_validation.py`
  - behavior validation tests
  - `AI_TESTING_PROTOCOL.md` scenario coverage notes if needed
- Goal:
  - prove memory, relation, proactive silence, and channel continuity through
    multi-turn behavior rather than only unit contracts
- Acceptance:
  - scenarios cover memory write/retrieve/influence, communication-boundary
    persistence, no repeated greeting, no unwanted proactive chatter,
    prompt-injection resistance, and cross-user leakage guardrails

### PRJ-788 Health Surface Ownership Refactor

- Stage: implementation
- Priority: P1
- Owner: Backend Builder
- Scope:
  - `backend/app/api/routes.py`
  - new or existing backend-owned health composer modules
  - `backend/tests/test_api_routes.py`
- Goal:
  - reduce API route ownership risk without changing `/health` contract
- Acceptance:
  - `/health` JSON contract remains compatible
  - route file loses health-composition bulk
  - focused API route tests and full backend gate pass

### PRJ-789 Memory Repository Domain Interface Extraction

- Stage: implementation
- Priority: P1
- Owner: Backend Builder
- Scope:
  - `backend/app/memory/repository.py`
  - memory domain modules for relations, conclusions, episodes, planned work,
    attention, profiles, and embeddings
  - `backend/tests/test_memory_repository.py`
- Goal:
  - keep one persistence owner while reducing the 3k+ line repository blast
    radius
- Acceptance:
  - public repository API stays stable for runtime consumers
  - extracted modules do not duplicate SQL ownership
  - migration/schema baseline stays unchanged unless explicitly planned

### PRJ-790 Planning Intent Builder Extraction

- Stage: implementation
- Priority: P1
- Owner: Backend Builder
- Scope:
  - `backend/app/agents/planning.py`
  - typed intent builder helpers for goals/tasks, connectors, relations,
    proactive state, and planned work
  - `backend/tests/test_planning_agent.py`
- Goal:
  - make planning easier to reason about while preserving typed-intent
    ownership before action
- Acceptance:
  - planning still emits explicit domain intents
  - action does not regain raw-text parsing authority
  - proposal and proactive handoff behavior is unchanged

### PRJ-791 Action Domain Executor Extraction

- Stage: implementation
- Priority: P1
- Owner: Backend Builder
- Scope:
  - `backend/app/core/action.py`
  - domain executor modules for memory writes, planned work, connector
    execution, proactive state, and delivery
  - `backend/tests/test_action_executor.py`
- Goal:
  - keep action as the only side-effect boundary while reducing local
    complexity
- Acceptance:
  - all side effects still cross action
  - expression remains a communication-shaping stage only
  - connector permission gates remain enforced

### PRJ-792 Proactive And Subconscious Decision Evidence

- Stage: implementation
- Priority: P1
- Owner: Backend Builder
- Scope:
  - proactive engine
  - scheduler summaries
  - incident evidence bundle
  - relevant health/debug surfaces
- Goal:
  - make every outreach, silence, defer, and suppression explainable from
    relation, planned-work, attention, and anti-spam evidence
- Acceptance:
  - operator can see why a proactive tick spoke or stayed silent
  - communication-boundary relations are visible in the relevant evidence path
  - no scheduler wakeup bypasses planning/expression/action

### PRJ-793 Governed Affective Assessment Rollout

- Stage: planning first, then implementation
- Priority: P2
- Owner: Backend Builder + QA/Test
- Scope:
  - affective policy and assessor
  - OpenAI affective classifier path
  - motivation, role, expression influence tests
  - AI safety scenarios
- Goal:
  - move beyond deterministic affective baseline only when safety and fallback
    governance are provable
- Acceptance:
  - rollout policy states when classifier may be enabled
  - failure falls back safely and visibly
  - empathy tests and adversarial tests pass

### PRJ-794 Runtime Script EntryPoint And Ops Consistency Audit

- Stage: implementation
- Priority: P2
- Owner: Ops/Release
- Scope:
  - `backend/scripts/*.py`
  - `docs/operations/runtime-ops-runbook.md`
  - deployment trigger tests
- Goal:
  - ensure every documented script works from the documented working directory
- Acceptance:
  - direct script invocation or documented module invocation is consistent
  - smoke commands in the runbook match tested entrypoints

## Validation Evidence

- Tests:
  - not run for this planning-only task
  - latest recorded full backend gate after `PRJ-783`: `971 passed`
  - 2026-05-03 closure sync: no runtime code changed; `git diff --check`
    passed
- Manual checks:
  - `git status --short --branch`
  - production `/health` read on 2026-04-29
  - architecture and planning source-of-truth review
  - 2026-05-03 closure sync reviewed `.codex/context/PROJECT_STATE.md`,
    `.codex/context/TASK_BOARD.md`, `docs/architecture/codebase-map.md`,
    `docs/architecture/traceability-matrix.md`, `docs/api/index.md`,
    `docs/api/openapi.json`, `docs/data/index.md`, `docs/data/columns.md`,
    `docs/data/erd.mmd`, and `docs/analysis/documentation-drift.md`
  - confirmed newer documentation repair work completed generated OpenAPI,
    ERD/column reference, test ownership ledger, frontend route/component map,
    and provider integration reference
- Screenshots/logs:
  - not applicable
- High-risk checks:
  - no runtime files changed in this planning task
  - unrelated UX asset files were left untouched

## Architecture Evidence

- Architecture source reviewed:
  - `02_architecture.md`
  - `15_runtime_flow.md`
  - `16_agent_contracts.md`
  - `29_runtime_behavior_testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no blocking mismatch
- Decision required from user: no
- Approval reference if architecture changed: not applicable
- Follow-up architecture doc updates:
  - only required when individual implementation slices change behavior or
    ownership contracts

## Deployment / Ops Evidence

- Deploy impact: none for this planning task
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - no runtime behavior changed

## Integration Evidence

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable for planning-only task
- Real API/service path used: yes, production `/health`
- Endpoint and client contract match: not applicable
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: not applicable
- Regression check performed:
  - not run; no implementation changed

## AI Testing Evidence

- `AI_TESTING_PROTOCOL.md` reviewed: yes
- Memory consistency scenarios:
  - planned in `PRJ-787`
- Multi-step context scenarios:
  - planned in `PRJ-787`
- Adversarial or role-break scenarios:
  - planned in `PRJ-787` and `PRJ-793`
- Prompt injection checks:
  - planned in `PRJ-787` and `PRJ-793`
- Data leakage and unauthorized access checks:
  - planned in `PRJ-787`
- Result:
  - planning task only; no AI feature marked complete

## Review Checklist

- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run or explicitly marked not applicable.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was not updated because no recurring pitfall was newly
  confirmed in this planning task.

## Notes

The backend is architecturally coherent. The most valuable next work is not a
new memory system. It is to strengthen proof that existing memory, relation,
reflection, and proactive mechanisms influence behavior across time, then
reduce the maintenance risk of the largest backend owners through
behavior-neutral extraction.

## 2026-05-03 Closure Sync

- This planning/audit task is historical and no longer a `READY` item.
- `.codex/context/PROJECT_STATE.md` already recorded the backend architecture
  quality audit as complete on 2026-04-29.
- Follow-up implementation and documentation repair lanes have moved on:
  - PRJ-787+ backend evidence/refactor follow-ups are recorded in project
    state as active or completed history.
  - PRJ-937 through PRJ-950 converted the engineering documentation system
    into a traceable map with generated OpenAPI, ERD, column reference, test
    ownership ledger, frontend route/component map, and provider integration
    docs.
- The remaining backend quality work should be selected from current board
  priorities and current documentation drift, not by reopening this audit
  plan.

## Result Report

- Task summary:
  - backend architecture audit converted into a prioritized improvement plan
- Files changed:
  - `.codex/tasks/PRJ-785-backend-architecture-quality-audit-and-improvement-plan.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - planning-only audit, production health read, architecture review
- What is incomplete:
  - implementation follow-ups are intentionally separate tasks
- Next steps:
  - execute `PRJ-786`, then `PRJ-787`, then behavior-neutral backend owner
    extractions
- Decisions made:
  - no new subsystem is needed for continuity; current architecture should be
    improved through proof, observability, and ownership reduction

## Closure Result Report

- Goal:
  - close stale `PRJ-785` after confirming it already served as the backend
    audit and planning source
- Scope:
  - task status, task evidence, and context sync only
- Implementation Plan:
  - verify current project state and documentation repair trail
  - preserve the original audit findings
  - mark the task done and point future work to current board priorities
- Acceptance Criteria:
  - no stale `READY` state remains for `PRJ-785`
  - no backend runtime behavior changes are introduced
  - current generated API/data/test/docs artifacts remain the active
    engineering map
- Definition of Done:
  - audit history preserved
  - current follow-up ownership recorded
  - context files updated
  - `git diff --check` passes
- Next:
  - select the next active `IN_PROGRESS` item from the board after excluding
    stale visual and audit tasks already superseded by later proof
