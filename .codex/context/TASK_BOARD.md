# TASK_BOARD

Last updated: 2026-04-19

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
- The planning queue now extends through `PRJ-097`.
- The next executable slice is `PRJ-069`.
- Additional architecture-alignment work should be appended after that queue so
  the backlog stays explicitly open for later discovery instead of pretending
  the plan is complete.

## READY

- [ ] PRJ-069 Define the LangGraph migration boundary and compatibility contract
  - Status: READY
  - Group: Graph Orchestration Adoption
  - Owner: Planner
  - Depends on: PRJ-068
  - Priority: P1
  - Result:
    - docs and runtime contracts define an explicit state/compatibility boundary
      between the current orchestrator and target LangGraph graph state
    - migration can proceed incrementally with contract-pinned adapters instead
      of a big-bang rewrite
  - Validation:
    - doc-and-contract sync plus targeted runtime-state model tests

## BACKLOG

- [ ] PRJ-069 Define the LangGraph migration boundary and compatibility contract
- [ ] PRJ-070 Introduce graph-compatible state adapters around current stage modules
- [ ] PRJ-071 Migrate the foreground runtime orchestration to LangGraph
- [ ] PRJ-072 Add optional LangChain utility wrappers only where they reduce code
- [ ] PRJ-073 Define the embedding and semantic retrieval contract
- [ ] PRJ-074 Add pgvector-backed storage and migration scaffolding
- [ ] PRJ-075 Implement hybrid retrieval across episodic, semantic, and affective memory
- [ ] PRJ-076 Add semantic retrieval evaluation and observability
- [ ] PRJ-077 Define the relation data model, scopes, and repository surface
- [ ] PRJ-078 Extend reflection to derive and maintain relation updates
- [ ] PRJ-079 Make runtime relation-aware in retrieval, context, role, planning, and expression
- [ ] PRJ-080 Define scheduler events, cadence rules, and runtime boundaries
- [ ] PRJ-081 Make the reflection runtime ready for scheduled and out-of-process execution
- [ ] PRJ-082 Add scheduled reflection and maintenance cadence
- [ ] PRJ-083 Add a proactive decision engine with interruption guardrails
- [ ] PRJ-084 Add proactive delivery controls, throttling, and regression coverage
- [ ] PRJ-085 Define the attention inbox, turn-assembly contract, and proposal handoff model
- [ ] PRJ-086 Implement message burst coalescing and pending-turn ownership
- [ ] PRJ-087 Define internal planning-state ownership and external productivity boundaries
- [ ] PRJ-088 Add subconscious proposal persistence and conscious promotion rules
- [ ] PRJ-089 Add read-only tool and research policy for subconscious execution
- [ ] PRJ-090 Add an attention gate for proactive delivery
- [ ] PRJ-091 Separate conscious wakeups from subconscious cadence
- [ ] PRJ-092 Add regression coverage for dual-loop coordination and batched conversation handling
- [ ] PRJ-093 Define the external connector contract, capability model, and permission gates
- [ ] PRJ-094 Add calendar integration boundary and scheduling-intent contract
- [ ] PRJ-095 Add external task-system adapter contracts for connected task apps
- [ ] PRJ-096 Add connected-drive access contracts for cloud files and documents
- [ ] PRJ-097 Add connector expansion and capability-discovery proposals

## FUTURE

- [ ] (none)

## IN_PROGRESS

- [ ] (none)

## BLOCKED

- [ ] (none)

## REVIEW

- [ ] (none)

## DONE

- [x] PRJ-065 Split reflection into smaller concern-owned modules
  - Status: DONE
  - Group: Adaptive Signal Governance And Heuristic Reduction
  - Owner: Backend Builder
  - Depends on: PRJ-064
  - Priority: P1
  - Result:
    - reflection logic was split into concern-owned modules:
      `app/reflection/goal_conclusions.py`,
      `app/reflection/adaptive_signals.py`,
      `app/reflection/affective_signals.py`
    - `app/reflection/worker.py` now focuses on orchestration and persistence
      flow instead of owning all inference details
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
- [x] PRJ-066 Add anti-self-reinforcement rules for adaptive signals
  - Status: DONE
  - Group: Adaptive Signal Governance And Heuristic Reduction
  - Owner: Backend Builder
  - Depends on: PRJ-065
  - Priority: P1
  - Result:
    - adaptive inference now requires outcome evidence (domain/preference update
      markers plus successful action), reducing self-reinforcement loops from
      role-only traces
    - collaboration-preference fallback now prefers explicit user-visible cues
      from recent events over plan-step self-feedback
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_expression_agent.py`
- [x] PRJ-067 Audit and prune low-leverage milestone heuristics
  - Status: DONE
  - Group: Adaptive Signal Governance And Heuristic Reduction
  - Owner: Backend Builder
  - Depends on: PRJ-066
  - Priority: P1
  - Result:
    - milestone pressure heuristics were pruned to phase-consistency signals and
      arc/transition evidence, removing low-leverage pure time-window drift
      triggers
    - regression now pins that stale time alone does not create lingering
      completion pressure
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py`
- [x] PRJ-068 Add multi-goal-aware reflection and planning tests
  - Status: DONE
  - Group: Adaptive Signal Governance And Heuristic Reduction
  - Owner: QA/Test
  - Depends on: PRJ-067
  - Priority: P1
  - Result:
    - reflection tests now pin goal-conclusion scope selection against recent
      turn hints when multiple active goals coexist
    - planning tests now pin event-to-goal matching across multiple active goals
      and task sets
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-061 Formalize memory-layer contracts in docs and repository APIs
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Product Docs
  - Depends on: PRJ-060
  - Priority: P1
  - Result:
    - docs and repository contracts now share explicit layer vocabulary
      (`episodic`, `semantic`, `affective`, `operational`)
    - repository now exposes layer-aware APIs and classification helpers for
      episodic retrieval, conclusion-layer reads, and operational view reads
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py`
- [x] PRJ-062 Add explicit domain action intents to the planning and action contract
  - Status: DONE
  - Group: Planning And Action Intent Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-061
  - Priority: P1
  - Result:
    - planning output now carries explicit typed `domain_intents` for
      goal/task/task-status and preference updates, plus `noop`
    - contracts/docs/runtime reality now define planning-owned intent and
      action-owned execution boundary explicitly
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
- [x] PRJ-063 Move durable domain writes from text parsing to explicit intents
  - Status: DONE
  - Group: Planning And Action Intent Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-062
  - Priority: P1
  - Result:
    - action no longer reparses raw event text for goal/task/task-status or
      preference durable updates
    - action executes only explicit `plan.domain_intents` and persists
      resulting intent outcomes in episodic payload metadata
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`
- [x] PRJ-064 Add contract tests for planning-owned intent and action-owned execution
  - Status: DONE
  - Group: Planning And Action Intent Hardening
  - Owner: QA/Test
  - Depends on: PRJ-063
  - Priority: P1
  - Result:
    - planning, action, and runtime tests now pin typed intent emission,
      no-intent no-write behavior, and end-to-end plan->action ownership
    - regressions that reintroduce action-side raw-text domain parsing now fail
      through contract-level tests
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-029 Split canonical architecture docs from transitional runtime reality
  - Status: DONE
  - Group: Documentation Integrity
  - Owner: Product Docs
  - Depends on: PRJ-028
  - Priority: P2
  - Result:
    - `docs/architecture/` now again describes the canonical AION architecture
      and human-oriented cognitive flow
    - transitional runtime details were moved into
      `docs/implementation/runtime-reality.md`
    - docs index and project context now describe the two-layer documentation
      model explicitly
  - Validation:
    - doc-only change, no automated validation required
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
- [x] PRJ-015 Tighten the event normalization and public API boundary
  - Status: DONE
  - Group: Observability And Runtime Honesty
  - Owner: Planner
  - Depends on: none
  - Priority: P2
  - Result:
    - API event normalization now enforces explicit source/subsource and a small payload boundary
    - text normalization and meta fallback rules are test-covered, including length caps aligned with persistence limits
    - `EventRuntimeResponse` now uses shared `MotivationMode` contract typing
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_api_routes.py`
- [x] PRJ-016 Move startup toward migration-first schema ownership
  - Status: DONE
  - Group: Observability And Runtime Honesty
  - Owner: DB/Migrations
  - Depends on: none
  - Priority: P2
  - Result:
    - app startup now defaults to migration-first behavior
    - startup `create_tables()` moved behind explicit compatibility mode (`STARTUP_SCHEMA_MODE=create_tables`)
    - migration and deployment expectations were synchronized in docs and context
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_config.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`
- [x] PRJ-017 Make the expression-to-action handoff explicit and test-covered
  - Status: DONE
  - Group: Stage Boundary Alignment
  - Owner: Backend Builder
  - Depends on: PRJ-016
  - Priority: P2
  - Result:
    - runtime now materializes an explicit `ActionDelivery` handoff between
      expression and action
    - action side effects consume the handoff contract instead of implicit
      expression/event coupling
    - runtime and action tests pin Telegram/API delivery behavior through the
      explicit contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_expression_agent.py`
- [x] PRJ-019 Add runtime stage ownership and architecture-to-code traceability
  - Status: DONE
  - Group: Architecture Traceability And Contract Tests
  - Owner: Product Docs
  - Depends on: PRJ-016
  - Priority: P3
  - Result:
    - runtime stage ownership and primary validation surfaces are now documented
      in overview and architecture docs
    - runtime-contract docs now explicitly distinguish public `/event` response
      from debug-only internal payload shape
    - current-runtime differences versus intended architecture are explicit and
      searchable in canonical docs
  - Validation:
    - doc-only change, no automated validation required
- [x] PRJ-018 Reduce expression/action integration coupling without changing behavior
  - Status: DONE
  - Group: Stage Boundary Alignment
  - Owner: Backend Builder
  - Depends on: PRJ-017
  - Priority: P2
  - Result:
    - action execution now delegates channel delivery to integration-level
      `DeliveryRouter`
    - integration delivery consumes explicit `ActionDelivery` contract instead
      of runtime-local channel assumptions
    - API and Telegram delivery behavior remains stable under regression tests
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_action_executor.py tests/test_delivery_router.py`
- [x] PRJ-020 Add contract-level runtime flow smoke tests for architecture invariants
  - Status: DONE
  - Group: Architecture Traceability And Contract Tests
  - Owner: QA/Test
  - Depends on: PRJ-017, PRJ-019
  - Priority: P2
  - Result:
    - runtime flow invariants now have dedicated contract smoke tests across
      runtime pipeline, API boundary shape, and stage-logger payload contract
    - architectural drift on stage order, action boundary, or trace/log payload
      keys now causes fast regression failures
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py`
- [x] PRJ-021 Add explicit debug payload exposure gate for `/event`
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P3
  - Result:
    - debug payload exposure for `POST /event?debug=true` is now controlled by
      explicit config (`EVENT_DEBUG_ENABLED`)
    - API behavior is test-covered for both debug-enabled and debug-disabled
      paths
    - environment and operations docs now describe the gate and policy surface
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py`
- [x] PRJ-022 Expose runtime policy flags in `/health` for operator traceability
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Ops/Release
  - Depends on: none
  - Priority: P3
  - Result:
    - `/health` now includes non-secret runtime policy flags (`startup_schema_mode`, `event_debug_enabled`)
    - API tests pin the added health payload contract
    - runtime ops and planning docs now describe the policy visibility surface
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- [x] PRJ-023 Add production visibility warning for debug payload policy
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P3
  - Result:
    - startup now emits an explicit warning when `APP_ENV=production` and
      `EVENT_DEBUG_ENABLED=true`
    - warning behavior is pinned with targeted startup policy tests
    - runtime ops and planning docs now explain how operators should interpret
      and clear this warning
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py tests/test_main_runtime_policy.py`
- [x] PRJ-024 Add production visibility warning for schema compatibility mode
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P3
  - Result:
    - startup now emits an explicit warning when `APP_ENV=production` and
      `STARTUP_SCHEMA_MODE=create_tables`
    - warning behavior is pinned with targeted startup policy tests
    - runtime ops and planning docs now explain why schema compatibility mode
      should remain temporary in production
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_config.py`
- [x] PRJ-025 Harden production default for debug payload exposure policy
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-023
  - Priority: P3
  - Result:
    - event debug exposure now uses environment-aware effective policy
      (enabled by default in non-production, disabled by default in production)
    - `/health` now exposes `event_debug_source` so operators can distinguish
      explicit config from environment-derived default behavior
    - startup warnings and docs were aligned with explicit-vs-default policy
      semantics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py tests/test_main_runtime_policy.py`
- [x] PRJ-026 Add optional strict production policy enforcement for startup
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-024, PRJ-025
  - Priority: P3
  - Result:
    - startup runtime-policy checks now support `PRODUCTION_POLICY_ENFORCEMENT=warn|strict`
    - production mismatch cases (`EVENT_DEBUG_ENABLED=true`, `STARTUP_SCHEMA_MODE=create_tables`) can now fail fast in strict mode
    - `/health` now exposes `production_policy_enforcement` so operators can verify active enforcement posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
- [x] PRJ-027 Add lifespan-level fail-fast regression test for strict policy mode
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-026
  - Priority: P3
  - Result:
    - startup strict-policy fail-fast behavior is now pinned at `lifespan` entry, not only in helper-level policy tests
    - regression test confirms mismatch block happens before database initialization side effects
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_api_routes.py`
- [x] PRJ-028 Add lifespan-level fail-fast regression coverage for strict schema mismatch
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-027
  - Priority: P3
  - Result:
    - startup strict-policy fail-fast behavior is now lifecycle-covered for both mismatch families
      (`EVENT_DEBUG_ENABLED=true` and `STARTUP_SCHEMA_MODE=create_tables`)
    - regression tests confirm strict-mode mismatch blocks runtime before database initialization in both cases
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_api_routes.py`
- [x] PRJ-029 Unify runtime policy mismatch detection and expose mismatch preview in `/health`
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-028
  - Priority: P3
  - Result:
    - runtime policy resolution now has one shared owner (`app/core/runtime_policy.py`) reused by startup warning/block checks and `/health`
    - `/health.runtime_policy` now includes `production_policy_mismatches` for operator-visible mismatch preview
    - regression coverage now pins shared policy snapshot semantics plus startup and API consumers
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py tests/test_api_routes.py`
- [x] PRJ-030 Add shared mismatch-count helper for runtime policy
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-029
  - Priority: P3
  - Result:
    - shared `production_policy_mismatch_count()` helper now exposes mismatch cardinality from one source of truth
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-031 Add shared strict-startup-block predicate helper
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-030
  - Priority: P3
  - Result:
    - shared `strict_startup_blocked()` helper now encodes strict enforcement block semantics in one place
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py`
- [x] PRJ-032 Add shared strict-rollout-readiness helper
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-031
  - Priority: P3
  - Result:
    - shared `strict_rollout_ready()` helper now reports whether strict-mode rollout has zero policy mismatches
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-033 Extend runtime policy snapshot with readiness fields
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-032
  - Priority: P3
  - Result:
    - `runtime_policy_snapshot` now includes `production_policy_mismatch_count`, `strict_startup_blocked`, and `strict_rollout_ready`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`
- [x] PRJ-034 Keep startup strict-block checks aligned with shared policy helper
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-033
  - Priority: P3
  - Result:
    - startup now consumes shared strict-block predicate so startup and `/health` policy semantics remain aligned
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`
- [x] PRJ-035 Expose strict-rollout readiness fields through `/health`
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Ops/Release
  - Depends on: PRJ-033
  - Priority: P3
  - Result:
    - `/health.runtime_policy` now exposes mismatch count and strict readiness/block state for operator triage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- [x] PRJ-036 Add runtime-policy unit regression coverage for readiness helpers
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-032
  - Priority: P3
  - Result:
    - runtime-policy unit tests now pin mismatch count and strict rollout/block helper behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-037 Expand `/health` API contract tests for strict readiness fields
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-035
  - Priority: P3
  - Result:
    - API tests now pin mismatch count and strict readiness/block outputs for multiple policy combinations
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- [x] PRJ-038 Add startup regression for warn-mode multi-mismatch non-block behavior
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-034
  - Priority: P3
  - Result:
    - startup tests now explicitly pin that `warn` mode logs warnings without strict startup block even under multiple mismatches
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`
- [x] PRJ-039 Sync planning/context/docs for strict rollout readiness contract
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Product Docs
  - Depends on: PRJ-035
  - Priority: P3
  - Result:
    - planning, context, architecture, and ops docs now describe strict rollout readiness fields and current runtime truth
  - Validation:
    - doc-and-context sync plus regression evidence recorded in this slice
- [x] PRJ-040 Add strict-rollout recommendation helper for production policy
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-039
  - Priority: P3
  - Result:
    - shared helper now derives `recommended_production_policy_enforcement` from environment and mismatch readiness
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-041 Add strict-rollout action hint helper
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-040
  - Priority: P3
  - Result:
    - shared helper now emits concise rollout hints (`not_applicable_non_production`, `resolve_mismatches_before_strict`, `can_enable_strict`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-042 Expose strict-rollout recommendation fields through runtime policy snapshot and `/health`
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Ops/Release
  - Depends on: PRJ-041
  - Priority: P3
  - Result:
    - `/health.runtime_policy` now includes `recommended_production_policy_enforcement` and `strict_rollout_hint`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py`
- [x] PRJ-043 Add startup informational hint for strict-rollout readiness in production warn mode
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-042
  - Priority: P3
  - Result:
    - startup now logs `runtime_policy_hint` when production is in `warn` mode and strict rollout is ready
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`
- [x] PRJ-044 Expand runtime-policy and startup/API regression coverage for recommendation hints
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-043
  - Priority: P3
  - Result:
    - tests now pin recommendation/hint fields in snapshot and `/health`, plus startup info-hint behavior in production warn mode
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
- [x] PRJ-045 Sync docs/context for strict-rollout recommendation contract
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Product Docs
  - Depends on: PRJ-044
  - Priority: P3
  - Result:
    - planning, context, architecture, and ops docs now describe strict-rollout recommendation and hint fields
  - Validation:
    - doc-and-context sync plus regression evidence recorded in this slice
- [x] PRJ-046 Add optional debug-token runtime setting for event debug access
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-045
  - Priority: P3
  - Result:
    - settings now support optional `EVENT_DEBUG_TOKEN` for debug payload access control
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py`
- [x] PRJ-047 Add runtime-policy token-required signal for debug payload access
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-046
  - Priority: P3
  - Result:
    - runtime policy snapshot now exposes `event_debug_token_required`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`
- [x] PRJ-048 Enforce debug-token header for `POST /event?debug=true` when configured
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-047
  - Priority: P3
  - Result:
    - debug runtime payload endpoint now requires `X-AION-Debug-Token` when `EVENT_DEBUG_TOKEN` is configured
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- [x] PRJ-049 Add production warning for debug exposure without debug token
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-048
  - Priority: P3
  - Result:
    - startup now warns when production debug exposure is enabled and no debug token is configured
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`
- [x] PRJ-050 Expand config/runtime/API/startup regression coverage for debug token gate
  - Status: DONE
  - Group: Public API Shape
  - Owner: QA/Test
  - Depends on: PRJ-049
  - Priority: P3
  - Result:
    - tests now pin token-required health policy field, debug endpoint token rejection/acceptance, and startup token-warning behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_main_lifespan_policy.py`
- [x] PRJ-051 Sync docs/context for debug-token-gated debug payload contract
  - Status: DONE
  - Group: Public API Shape
  - Owner: Product Docs
  - Depends on: PRJ-050
  - Priority: P3
  - Result:
    - architecture, operations, local-dev, planning docs and context now describe optional debug-token-gated debug payload access
  - Validation:
    - doc-and-context sync plus regression evidence recorded in this slice
- [x] PRJ-052 Add API user-id header fallback to reduce shared anonymous language/profile drift
  - Status: DONE
  - Group: Language Handling Strategy
  - Owner: Backend Builder
  - Depends on: PRJ-051
  - Priority: P2
  - Result:
    - API event normalization now accepts a route-provided fallback user id
      and `POST /event` now passes `X-AION-User-Id` as fallback identity input
      when `meta.user_id` is not provided
    - API user identity precedence is now explicit and test-covered
      (`meta.user_id` first, then `X-AION-User-Id`, then `anonymous`)
    - runtime reality, local-dev, ops, planning, and context docs now describe
      the multi-user API identity guardrail
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_api_routes.py`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-053 Define the affective assessment contract and runtime placeholders
  - Status: DONE
  - Group: Affective Understanding And Empathy
  - Owner: Planner
  - Depends on: PRJ-052
  - Priority: P1
  - Result:
    - runtime contracts now define a first-class affective slot
      (`affect_label`, `intensity`, `needs_support`, `confidence`, `source`,
      `evidence`)
    - perception now emits deterministic affective placeholder data and runtime
      carries it as top-level `RuntimeResult.affective`
    - architecture/runtime-reality/planning/context docs now align around the
      explicit affective contract before AI-assisted behavior slices
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_affective_contract.py tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-054 Add an AI-assisted affective assessor with deterministic fallback
  - Status: DONE
  - Group: Affective Understanding And Empathy
  - Owner: Backend Builder
  - Depends on: PRJ-053
  - Priority: P1
  - Result:
    - runtime now runs a dedicated `AffectiveAssessor` stage that can consume
      LLM classification and normalize it to the explicit affective contract
    - deterministic fallback remains active when classifier client is missing,
      unavailable, or returns invalid payload
    - runtime stage logs now expose affective source (`ai_classifier` vs
      `fallback`) for operator traceability
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_expression_agent.py`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-055 Wire affective assessment through motivation, role, and expression
  - Status: DONE
  - Group: Affective Understanding And Empathy
  - Owner: Backend Builder
  - Depends on: PRJ-054
  - Priority: P1
  - Result:
    - motivation, role, and expression now consume `perception.affective` as
      the primary support/emotion signal instead of local emotional keyword
      ladders
    - supportive behavior remains traceable to one affective owner across
      runtime stages (`affective_assessment` -> `motivation`/`role`/`expression`)
    - targeted tests now encode affective-driven behavior in stage-level unit
      paths and runtime pipeline integration
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_role_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-056 Add empathy-oriented evaluation fixtures and regression tests
  - Status: DONE
  - Group: Affective Understanding And Empathy
  - Owner: QA/Test
  - Depends on: PRJ-055
  - Priority: P1
  - Result:
    - empathy-focused shared fixtures now cover emotionally heavy, ambiguous,
      and mixed-intent turns
    - motivation, expression, and runtime regression tests now parametrize these
      fixtures to pin support quality through the affective contract path
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_expression_agent.py tests/test_motivation_engine.py`
- [x] PRJ-057 Introduce scoped conclusions for global, goal, and task context
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Backend Builder
  - Depends on: PRJ-056
  - Priority: P1
  - Result:
    - `aion_conclusion` now supports scoped records (`scope_type`, `scope_key`)
      for `global|goal|task` context with scoped uniqueness guarantees
    - reflection now persists goal-operational conclusions with goal scope instead
      of forcing all operational state into one user-global slot
    - memory repository APIs now support scoped conclusion and runtime-preference
      queries, including scope-aware filtering with optional global fallback
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-058 Refactor runtime consumers to use scoped reflection state
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Backend Builder
  - Depends on: PRJ-057
  - Priority: P1
  - Result:
    - runtime state load now resolves a primary active goal and reads scoped
      runtime preferences and scoped conclusions with global fallback
    - context, motivation, planning, and milestone enrichment consume the
      scoped state for the active goal path
    - regression coverage now pins that unrelated goal conclusions do not leak
      into the current turn
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
- [x] PRJ-059 Add an affective memory layer and reflection outputs
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Backend Builder
  - Depends on: PRJ-058
  - Priority: P1
  - Result:
    - episodic payloads now persist lightweight affective tags
      (`affect_label`, `affect_intensity`, `affect_needs_support`,
      `affect_source`, `affect_evidence`)
    - reflection now derives slower-moving affective conclusions
      (`affective_support_pattern`, `affective_support_sensitivity`)
    - runtime preferences, context summaries, and motivation scoring now consume
      those affective reflection signals
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_context_agent.py tests/test_motivation_engine.py tests/test_runtime_pipeline.py`
- [x] PRJ-060 Add retrieval ranking and compression beyond the latest-five load
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Backend Builder
  - Depends on: PRJ-059
  - Priority: P1
  - Result:
    - runtime memory load depth now fetches beyond a fixed latest-five limit
      (`RuntimeOrchestrator.MEMORY_LOAD_LIMIT=12`)
    - context retrieval ranking now includes affective relevance in addition to
      language, layer mode, topical overlap, and importance
    - runtime integration tests pin that deeper history can surface ranked
      relevant memory instead of being cut off by shallow fetch depth
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_runtime_pipeline.py`
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
