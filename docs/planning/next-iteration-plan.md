# Next Iteration Plan

## Purpose

This plan translates the repo analysis into an execution roadmap that brings the code closer to `docs/architecture/` without rewriting the canonical architecture docs around temporary runtime shortcuts.

The goal is not to add more features first.
The goal is to make the current AION runtime more correct, more inspectable, and easier to extend without architectural drift.

## Repo Analysis Snapshot

Confirmed on 2026-04-19:

- `.\.venv\Scripts\python -m pytest -q` passes with `342 passed`
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
- `PRJ-015` made API-boundary normalization explicit in runtime code and tests, including source/subsource hardening and normalized payload shaping.
- `PRJ-016` moved startup to migration-first by default and kept `create_tables()` behind an explicit compatibility mode.
- `PRJ-017` introduced an explicit `ActionDelivery` handoff contract between expression and action and pinned that boundary with runtime and action regression tests.
- `PRJ-019` added explicit runtime stage ownership and architecture-to-code traceability across overview and canonical architecture contract docs.
- `PRJ-018` moved delivery-channel dispatch behind an integration-level router so action consumes explicit handoff contracts without runtime-local delivery assumptions.
- `PRJ-020` added contract-level runtime flow smoke tests that pin stage order, action-boundary behavior, public API response shape, and stage-log payload invariants.
- `PRJ-021` added an explicit config gate for `/event?debug=true` payload exposure and test coverage for enabled/disabled debug paths.
- `PRJ-022` exposed non-secret runtime policy flags in `/health` for operator traceability and synchronized API tests and ops docs.
- `PRJ-023` added explicit startup warning visibility for production runs with debug payload exposure enabled.
- `PRJ-024` added explicit startup warning visibility for production runs with schema compatibility mode enabled.
- `PRJ-025` hardened production defaults for debug payload exposure, including explicit policy-source visibility in `/health`.
- `PRJ-026` added production policy enforcement mode (`warn|strict`) so startup can either emit warnings or fail fast on production policy mismatches, with health visibility and regression coverage.
- `PRJ-027` added a lifespan-level strict-policy regression test that verifies fail-fast startup happens before database initialization side effects.
- `PRJ-028` extended strict-policy lifespan regression coverage to schema compatibility mismatch (`STARTUP_SCHEMA_MODE=create_tables`) with the same block-before-side-effects guarantee.
- `PRJ-029` unified runtime-policy mismatch detection under a shared helper and exposed mismatch preview (`production_policy_mismatches`) in `/health`.
- `PRJ-030..PRJ-039` added strict-rollout readiness helpers and health contract fields (`production_policy_mismatch_count`, `strict_startup_blocked`, `strict_rollout_ready`), plus aligned startup/API tests and context/docs sync.
- `PRJ-040..PRJ-045` added strict-rollout recommendation helpers and health contract fields (`recommended_production_policy_enforcement`, `strict_rollout_hint`), plus startup rollout hints and aligned startup/API/policy tests.
- `PRJ-046..PRJ-051` added optional debug-token-gated debug payload access (`EVENT_DEBUG_TOKEN`, `X-AION-Debug-Token`), policy visibility (`event_debug_token_required`), startup warning alignment, and regression/docs/context sync.
- `PRJ-052` added API user-id header fallback (`X-AION-User-Id`) with explicit precedence over `meta.user_id`, reducing shared-anonymous language/profile drift for multi-user API traffic.
- `PRJ-053` added a first-class affective assessment contract and runtime placeholder slot (`affect_label`, `intensity`, `needs_support`, `confidence`, `source`, `evidence`) emitted by perception for follow-up empathy slices.
- `PRJ-054` added an AI-assisted affective assessor stage with deterministic fallback, including normalized LLM output handling and runtime log traceability of affective source (`ai_classifier|fallback`).
- `PRJ-055` wired motivation, role, and expression to consume `perception.affective` as the shared support signal owner, replacing local emotional keyword ladders and adding affective-driven regression coverage.
- `PRJ-056` added empathy-oriented shared fixtures for emotionally heavy, ambiguous, and mixed-intent turns, and expanded support-quality regressions across motivation, expression, and runtime integration.
- `PRJ-057` introduced scoped conclusions for `global|goal|task` context, including schema/repository support and goal-scoped reflection writes.
- `PRJ-058` refactored runtime consumers to use goal-scoped reflection state with global fallback, closing cross-goal leakage in context/motivation/planning paths.
- `PRJ-059` added an affective memory layer in episodic payloads plus reflection-derived affective conclusions reusable across turns.
- `PRJ-060` expanded runtime retrieval depth and affective-aware ranking/compression beyond the previous latest-five loading strategy.
- `PRJ-061` formalized memory-layer contracts (`episodic`, `semantic`,
  `affective`, `operational`) in canonical docs and repository APIs.
- `PRJ-062..PRJ-063` introduced explicit planning-owned `domain_intents` and
  moved durable goal/task/task-status/preference writes away from action-side
  raw-text parsing.
- `PRJ-064` added contract regressions that pin planning-owned intent and
  action-owned execution boundaries in planning/action/runtime tests.

## Highest-Risk Gaps

### 1. Episodic memory is still a machine-readable string contract

Current behavior:

- `ActionExecutor.persist_episode()` now writes a typed payload and a readable summary
- context and reflection now prefer payload-first reads with fallback for old summary-only rows

Why it matters:

- this removed a high-risk contract gap between runtime and `docs/architecture/16_agent_contracts.md`
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

### 6. Startup schema ownership still carries a compatibility fallback

Current behavior:

- Alembic baseline exists and startup now defaults to migration-first behavior
- `create_tables()` is now explicit compatibility fallback, enabled only through startup config

Why it matters:

- migration-first behavior is now explicit for normal runtime and deploy flows
- compatibility fallback should stay intentional and eventually be removed

## Delivery Principle

- Keep `docs/architecture/` fixed as the architecture source.
- Move code toward architecture intent, not architecture intent toward temporary runtime shortcuts.
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

- `PRJ-015` is complete.
  - Result:
    - input normalization rules are explicit and test-covered
    - public `/event` boundary is intentionally small (`source=api`, `subsource=event_endpoint`, normalized payload)
    - debug behavior remains clearly internal
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_api_routes.py`

- `PRJ-016` is complete.
  - Result:
    - migration-first ownership is explicit
    - startup `create_tables()` is now guarded behind deliberate compatibility mode
    - deployment and local-development expectations are documented
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_config.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

## Post-Current Queue Expansion

The current recommended execution queue through `PRJ-020` is complete.

The groups below are intentionally appended after that queue so the repo keeps
an explicit architecture-alignment backlog instead of implying that current
tasks fully close the gap between docs and code.

These groups are a later wave, not a replacement for the active queue.

## Group 5 - Stage Boundary Alignment

This group makes the documented action boundary more visible in code without
forcing a risky broad rewrite first.

- `PRJ-017` Make the expression-to-action handoff explicit and test-covered.
  - Result:
    - runtime now builds an explicit `ActionDelivery` handoff from expression
      output and event routing metadata
    - action side effects consume that explicit contract for API/Telegram
      delivery behavior
    - user-facing behavior remains unchanged while stage coupling is reduced
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_expression_agent.py`

- `PRJ-018` Reduce expression/action integration coupling without changing behavior.
  - Result:
    - channel delivery now flows through integration-level `DeliveryRouter`
      using explicit `ActionDelivery` contract fields
    - side effects remain isolated inside action-triggered integration calls
    - runtime behavior stayed equivalent for API and Telegram paths under
      regression tests
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_action_executor.py tests/test_delivery_router.py`

## Group 6 - Architecture Traceability And Contract Tests

This group makes the implemented architecture easier to audit and harder to let
drift silently.

- `PRJ-019` is complete.
  - Result:
    - each documented runtime stage now has explicit code ownership and
      validation mapping
    - current-runtime contract differences are explicit across overview, runtime
      flow, and contract docs
    - architecture traceability now has a faster audit surface in canonical docs
  - Validation:
    - doc-only change, no automated validation required

- `PRJ-020` is complete.
  - Result:
    - contract smoke tests now pin documented stage order and action-boundary
      invariants in runtime pipeline tests
    - API tests now pin compact public `/event` response shape and debug gating
    - logging tests now pin `RuntimeStageLogger` payload and traceability fields
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py`

## Group 7 - Affective Understanding And Empathy

This group replaces brittle emotional keyword ladders with an explicit affective
assessment contract that can evolve toward AI-assisted classification while
keeping deterministic fallback behavior.

- `PRJ-053` Define the affective assessment contract and runtime placeholders.
  - Result:
    - runtime contracts explicitly describe affective interpretation output
      (`affect_label`, `intensity`, `needs_support`, `confidence`,
      `source`, `evidence`)
    - runtime state and docs gain a first-class affective slot instead of
      hiding emotion handling inside role and valence heuristics
    - the next implementation slices can evolve affective logic without mixing
      it into unrelated perception or motivation contracts
  - Validation:
    - doc-and-contract sync plus targeted schema tests for runtime models

- `PRJ-054` Add an AI-assisted affective assessor with deterministic fallback.
  - Result:
    - perception or a dedicated affective module can call an LLM with strict
      structured output for emotion/support detection
    - deterministic keyword fallback remains available for offline or degraded
      runtime paths
    - runtime logs expose whether affective classification came from AI or
      fallback rules
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_perception_agent.py tests/test_runtime_pipeline.py tests/test_expression_agent.py`

- `PRJ-055` is complete.
  - Result:
    - motivation, role, and expression consume the explicit affective contract
      instead of re-deriving emotion separately
    - supportive behavior becomes traceable from one affective owner instead of
      repeated local heuristics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_role_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

- `PRJ-056` is complete.
  - Result:
    - emotionally heavy, ambiguous, and mixed-intent turns have explicit
      contract fixtures
    - repo behavior is pinned around support quality, not only around internal
      heuristic labels
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_expression_agent.py tests/test_motivation_engine.py`

## Group 8 - Scoped Memory And Retrieval Depth

This group makes memory richer and less misleading by separating memory layers,
introducing affective memory, and removing the current user-global leakage of
goal-specific reflection signals.

- `PRJ-057` is complete.
  - Result:
    - conclusions such as progress, milestone, and completion state are no
      longer stored as one flat user-global bag
    - repository APIs can query conclusions by scope instead of forcing one
      latest value across all active goals
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-058` is complete.
  - Result:
    - context, motivation, planning, and milestone enrichment consume
      goal-scoped state when a goal is relevant
    - unrelated goals stop leaking pressure, risk, or completion heuristics
      into the current turn
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- `PRJ-059` is complete.
  - Result:
    - episodes can persist lightweight affective tags or summaries
    - reflection can derive slower-moving affective patterns such as recurring
      stress, confidence recovery, or support sensitivity
    - affective state becomes reusable across turns without overloading
      `response_style` or generic conclusions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-060` is complete.
  - Result:
    - runtime retrieval can rank across recency, topical relevance, memory
      layer, and affective relevance
    - runtime stops depending on a fixed shallow fetch as the only memory depth
      strategy
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_runtime_pipeline.py`

- `PRJ-061` is complete.
  - Result:
    - docs explicitly distinguish episodic, semantic, affective, and
      operational memory views
    - repository now exposes layer-aware APIs and classification helpers for
      episodic retrieval, conclusion-layer filtering, and operational reads
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py`

## Group 9 - Planning And Action Intent Hardening

This group restores the architectural rule that planning proposes domain
changes and action executes explicit intents instead of reparsing user text
inside the action layer.

- `PRJ-062` is complete.
  - Result:
    - plans can carry typed intents for goal creation, task creation, task
      status update, preference update, or no-op
    - planning now explicitly owns the domain-change contract passed to action
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- `PRJ-063` is complete.
  - Result:
    - `ActionExecutor` executes structured intents instead of re-running
      keyword extraction over the original event text
    - side effects follow the documented plan -> action ownership boundary
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`

- `PRJ-064` is complete.
  - Result:
    - architectural regressions on domain side-effect ownership fail quickly
    - runtime smoke tests prove that message delivery and durable writes both
      happen only from explicit action inputs
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

## Group 10 - Adaptive Signal Governance And Heuristic Reduction

This group reduces code growth by splitting oversized modules, pruning
low-leverage heuristics, and adding anti-feedback-loop rules for adaptive
signals such as theta, role preference, and collaboration preference.

- `PRJ-065` Split reflection into smaller concern-owned modules.
  - Result:
    - reflection logic is separated into preference, progress, affective, and
      adaptive-state concern owners
    - `app/reflection/worker.py` stops being the single home for unrelated
      inference logic
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-066` Add anti-self-reinforcement rules for adaptive signals.
  - Result:
    - `preferred_role`, `theta`, and `collaboration_preference` require
      stronger evidence and outcome-aware updates
    - the runtime stops learning mainly from its own previous guesses and
      instead prefers user-visible signals or durable success evidence
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_expression_agent.py`

- `PRJ-067` Audit and prune low-leverage milestone heuristics.
  - Result:
    - milestone arc/pressure/due-window heuristics are reviewed for actual
      downstream effect
    - low-value signals are removed, merged, or gated behind clearer evidence
      thresholds
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py`

- `PRJ-068` Add multi-goal-aware reflection and planning tests.
  - Result:
    - regression coverage explicitly proves that one active goal does not leak
      reflected state into another
    - runtime behavior is pinned for users with more than one live objective
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_context_agent.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

## Group 11 - Graph Orchestration Adoption

This group aligns the runtime with the architecture-level stack direction
without forcing a big-bang rewrite of the current working orchestrator.

- `PRJ-069` Define the LangGraph migration boundary and compatibility contract.
  - Result:
    - docs and runtime contracts describe which current orchestrator fields map
      directly into graph state
    - migration can proceed incrementally instead of rewriting all stages at
      once
  - Validation:
    - doc-and-contract sync plus targeted runtime-state model tests

- `PRJ-070` Introduce graph-compatible state adapters around current stage modules.
  - Result:
    - current perception, context, motivation, role, planning, expression, and
      action modules can be called through graph-ready adapters
    - repo preserves current behavior while preparing the LangGraph runtime
      shape
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_logging.py`

- `PRJ-071` Migrate the foreground runtime orchestration to LangGraph.
  - Result:
    - the main foreground pipeline runs through LangGraph while preserving
      existing stage boundaries, logs, and response contracts
    - current runtime behavior stays regression-covered during the migration
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py`

- `PRJ-072` Add optional LangChain utility wrappers only where they reduce code.
  - Result:
    - LangChain is used narrowly for prompt templates, retrievers, or parsing
      where it materially reduces boilerplate
    - the repo avoids turning LangChain into the architectural core
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_runtime_pipeline.py`

## Group 12 - Semantic Retrieval Infrastructure

This group upgrades memory retrieval from heuristics-only ranking to a hybrid
system that can use embeddings and pgvector where that improves relevance.

- `PRJ-073` Define the embedding and semantic retrieval contract.
  - Result:
    - repo has one explicit contract for embeddings, vectorized records, and
      similarity retrieval inputs/outputs
    - semantic retrieval can evolve without leaking provider-specific details
      into stage logic
  - Validation:
    - doc-and-contract sync plus targeted repository model tests

- `PRJ-074` Add pgvector-backed storage and migration scaffolding.
  - Result:
    - PostgreSQL gains pgvector-compatible schema and indexes for semantic
      retrieval
    - deploy and migration docs explicitly cover the new dependency
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_memory_repository.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

- `PRJ-075` Implement hybrid retrieval across episodic, semantic, and affective memory.
  - Result:
    - runtime can rank memory using recency, explicit scope, lexical overlap,
      and vector similarity
    - semantic retrieval complements rather than replaces current deterministic
      retrieval behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`

- `PRJ-076` Add semantic retrieval evaluation and observability.
  - Result:
    - logs and tests show when vector retrieval helps, misses, or conflicts
      with lexical ranking
    - retrieval quality becomes measurable instead of anecdotal
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_logging.py tests/test_runtime_pipeline.py`

## Group 13 - Relation System

This group adds the user-specific relation layer described in architecture so
the personality can accumulate durable interpersonal understanding, not only
generic conclusions and task state.

- `PRJ-077` Define the relation data model, scopes, and repository surface.
  - Result:
    - repo gets an explicit relation model with confidence, scope, and decay
      semantics
    - relation storage is separated from generic conclusions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_schema_baseline.py`

- `PRJ-078` Extend reflection to derive and maintain relation updates.
  - Result:
    - subconscious processing can derive relation hypotheses from repeated
      interactions and update them gradually
    - relation updates follow explicit confidence and safety rules
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-079` Make runtime relation-aware in retrieval, context, role, planning, and expression.
  - Result:
    - runtime can retrieve relevant high-confidence relations per turn
    - relation signals influence behavior in a controlled, testable way
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_role_agent.py tests/test_planning_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

## Group 14 - Scheduled And Proactive Runtime

This group adds the missing background cadence and proactive behavior described
in architecture so the personality can initiate helpful, bounded actions over
time rather than only react to incoming events.

- `PRJ-080` Define scheduler events, cadence rules, and runtime boundaries.
  - Result:
    - scheduler-originated events become a first-class documented input source
    - reflection cadence, maintenance cadence, and proactive cadence have one
      contract owner
  - Validation:
    - doc-and-contract sync plus targeted event normalization tests

- `PRJ-081` Make the reflection runtime ready for scheduled and out-of-process execution.
  - Result:
    - reflection ownership no longer assumes only in-process wakeups
    - runtime can move toward a dedicated worker or scheduled execution without
      rewriting reflection logic again
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-082` Add scheduled reflection and maintenance cadence.
  - Result:
    - scheduler can trigger periodic reflection, cleanup, or maintenance
      workflows
    - the background loop no longer depends only on post-event enqueue
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_api_routes.py tests/test_config.py`

- `PRJ-083` Add a proactive decision engine with interruption guardrails.
  - Result:
    - proactive suggestions, reminders, warnings, or encouragement can be
      selected from explicit triggers and bounded decision rules
    - interruption cost and user context are part of the decision model
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- `PRJ-084` Add proactive delivery controls, throttling, and regression coverage.
  - Result:
    - proactive outputs obey frequency limits, opt-in guards, and delivery
      constraints
    - proactive behavior is measurable and test-covered instead of ad hoc
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

## Group 15 - Attention Gating And Dual-Loop Coordination

This group clarifies how conscious and subconscious runtime cooperate without
collapsing their boundaries, while also preventing message-by-message reply
spam during bursty user conversations.

- `PRJ-085` Define the attention inbox, turn-assembly contract, and proposal handoff model.
  - Result:
    - architecture and runtime contracts define one explicit inbox for
      user-originated events, scheduler ticks, and subconscious proposals
    - conversational turn assembly has one contract owner instead of ad hoc
      per-message handling
    - subconscious outputs are modeled as proposals for conscious evaluation,
      not direct user-visible actions
  - Validation:
    - doc-and-contract sync plus targeted runtime-state model tests

- `PRJ-086` Implement message burst coalescing and pending-turn ownership.
  - Result:
    - rapid inbound user messages can be coalesced into one conscious turn
      instead of producing one reply per raw message
    - pending/claimed/answered turn state prevents duplicate foreground
      replies during short burst windows
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-087` Define internal planning-state ownership and external productivity boundaries.
  - Result:
    - architecture and repository vocabulary keep goals/tasks as integral
      internal planning state of the personality rather than a detached
      subsystem
    - docs define where internal planning ends and connected external systems
      (calendar, task apps, file drives) begin, so connector rollout does not
      blur cognitive ownership
  - Validation:
    - doc-and-contract sync plus targeted repository model tests

- `PRJ-088` Add subconscious proposal persistence and conscious promotion rules.
  - Result:
    - subconscious runtime can persist proposals such as `ask_user`,
      `research_topic`, `suggest_goal`, or `nudge_user` without executing them
      directly
    - conscious runtime becomes the only owner that can accept, defer, merge,
      or discard those proposals before action
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-089` Add read-only tool and research policy for subconscious execution.
  - Result:
    - subconscious runtime can use explicit read-only retrieval or research
      tools without gaining direct side-effect authority
    - tool boundaries are documented and testable so subconscious exploration
      cannot bypass conscious action ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_logging.py`

- `PRJ-090` Add an attention gate for proactive delivery.
  - Result:
    - proactive delivery evaluates quiet hours, interruption cost, cooldown,
      recent outbound count, and unanswered proactive count before messaging
    - user availability and anti-spam posture become explicit runtime inputs
      instead of implicit heuristics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- `PRJ-091` Separate conscious wakeups from subconscious cadence.
  - Result:
    - conscious runtime can wake on assembled conversation turns, scheduler
      attention events, or accepted subconscious proposals
    - subconscious cadence remains periodic and non-user-facing instead of
      acting as a second direct messaging loop
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_config.py`

- `PRJ-092` Add regression coverage for dual-loop coordination and batched conversation handling.
  - Result:
    - repo gains end-to-end regression coverage for burst-message coalescing,
      proposal handoff, and gated proactive delivery
    - architecture drift on conscious/subconscious separation or duplicate
      reply prevention fails quickly
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py tests/test_action_executor.py`

## Group 16 - External Productivity Connectors

This group lets the personality use connected user systems such as calendar,
task platforms, and cloud drives without turning those integrations into
implicit or uncontrolled side effects.

- `PRJ-093` Define the external connector contract, capability model, and permission gates.
  - Result:
    - runtime has one explicit connector contract for user-authorized external
      systems and their capabilities
    - permission, opt-in, and confirmation rules are documented for read,
      suggest, and mutate operations against connected tools
  - Validation:
    - doc-and-contract sync plus targeted runtime-state model tests

- `PRJ-094` Add calendar integration boundary and scheduling-intent contract.
  - Result:
    - runtime contracts define how internal planning can read availability,
      create scheduling suggestions, and execute calendar changes when the user
      authorized that behavior
    - calendar awareness becomes usable for productivity support without
      bypassing action ownership or proactive guardrails
  - Validation:
    - doc-and-contract sync plus targeted action/runtime tests

- `PRJ-095` Add external task-system adapter contracts for connected task apps.
  - Result:
    - repo gains a generic task-provider contract that can back ClickUp,
      Trello, or future task tools behind one internal planning surface
    - internal goals/tasks can synchronize with authorized external systems
      without making any one provider the architectural core
  - Validation:
    - doc-and-contract sync plus targeted repository/action tests

- `PRJ-096` Add connected-drive access contracts for cloud files and documents.
  - Result:
    - runtime defines guarded access patterns for Google Drive, OneDrive, and
      similar file providers
    - file and document access becomes an explicit capability that planning,
      context, and action can consume without ad hoc tool coupling
  - Validation:
    - doc-and-contract sync plus targeted runtime/action tests

- `PRJ-097` Add connector expansion and capability-discovery proposals.
  - Result:
    - the personality can notice repeated unmet needs and propose connector or
      capability expansion without self-authorizing new external access
    - user-facing extension suggestions become explicit, bounded outputs of the
      runtime instead of hidden side effects
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_planning_agent.py tests/test_action_executor.py`

## Next Derived Slice

The planning queue is now extended through `PRJ-097`.
The next execution-ready slice is `PRJ-065`, with later groups staying ordered
behind it.

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

- derive the next smallest architecture-alignment task from
  `docs/planning/open-decisions.md`
- register that task in `.codex/context/TASK_BOARD.md` before implementation

## Recommended Execution Order

1. `PRJ-065..PRJ-068` Adaptive signal governance and heuristic reduction
2. `PRJ-069..PRJ-072` Graph orchestration adoption
3. `PRJ-073..PRJ-076` Semantic retrieval infrastructure
4. `PRJ-077..PRJ-079` Relation system
5. `PRJ-080..PRJ-084` Scheduled and proactive runtime
6. `PRJ-085..PRJ-092` Attention gating and dual-loop coordination
7. `PRJ-093..PRJ-097` External productivity connectors

The queue should still be treated as intentionally open after those items.
Additional small architecture-alignment slices may still be discovered while
executing Groups 4 through 16.

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
