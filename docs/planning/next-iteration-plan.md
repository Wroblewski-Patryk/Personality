# Next Iteration Plan

## Purpose

This plan translates the repo analysis into an execution roadmap that brings the code closer to `docs/architecture/` without rewriting the canonical architecture docs around temporary runtime shortcuts.

The goal is not to add more features first.
The goal is to make the current AION runtime more correct, more inspectable, and easier to extend without architectural drift.

## Repo Analysis Snapshot

Confirmed on 2026-04-19:

- `.\.venv\Scripts\python -m pytest -q` passes with `425 passed`
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

Historical planning note (2026-04-22):

- after Group 49 closed, the repo seeded a seven-lane convergence queue
  through `PRJ-442` covering runtime topology finalization,
  production-boundary hardening, retrieval and affective-memory
  productionization, adaptive identity governance, goal/task and proposal
  governance, scheduler-plus-connector capability convergence, and deployment
  standard plus release-reliability closure.
- that queue has since been completed and is kept here only as architecture
  history for how Groups 50 through 56 were organized.

Completed on 2026-04-22:

- `PRJ-415..PRJ-418` are complete: runtime now exposes one explicit topology
  switch policy for reflection and durable attention, plus a machine-visible
  graph/proposal baseline through `/health.runtime_topology`.
- `PRJ-419..PRJ-422` are complete: runtime policy now exposes concrete
  enforcement/removal windows, and production defaults shared debug ingress to
  break-glass-only posture when not explicitly overridden.
- `PRJ-423..PRJ-426` are complete: retrieval depth policy now exposes explicit
  production defaults, and embeddings now support a local provider-owned
  `local_hybrid` execution path instead of only deterministic fallback
  posture.
- `PRJ-427..PRJ-430` are complete: health/runtime debug now expose one bounded
  adaptive identity governance snapshot for role horizon, affective rollout,
  preference authority, theta authority, and multilingual/profile posture.
- `PRJ-431..PRJ-434` are complete: planning governance is now explicit through
  one machine-visible snapshot for inferred goal/task growth and fixed
  proposal-decision posture.
- `PRJ-435..PRJ-438` are complete: connector authorization matrix and
  capability-proposal boundary are now explicit runtime surfaces alongside the
  existing shared connector policy owner.
- `PRJ-439..PRJ-442` are complete: deployment health and release smoke now
  expose the selected hosting baseline plus deployment-trigger SLO posture, and
  planning/context truth are synchronized through Group 56.
- after Group 56 closed, no seeded `READY` task remains; the next queue should
  again be derived from any newly discovered post-convergence follow-up.
- `PRJ-443` is complete: top-level planning/context surfaces now use one shared
  post-convergence stance instead of repeating stale queue-seeding notes from
  earlier convergence waves.
- `PRJ-444..PRJ-447` are complete: shared debug-ingress posture vocabulary now
  uses final route-owned labels across runtime policy, headers, release smoke,
  and docs.
- `PRJ-448..PRJ-451` are complete: affective visibility now distinguishes
  heuristic input ownership from final assessment resolution through `/health`
  and `system_debug`.
- `PRJ-452..PRJ-453` are complete: embedding posture now exposes one explicit
  execution class for deterministic baseline, local provider ownership, and
  fallback-to-deterministic paths.
- `PRJ-454` is complete: top-level planning/context surfaces now treat
  post-`PRJ-453` follow-up discovery as the only active planning posture and
  no longer mix it with stale queue-seeding notes from the earlier
  `PRJ-415..PRJ-442` convergence wave.
- `PRJ-455..PRJ-457` are complete: durable attention contract-store
  documentation now converges across canonical contracts, implementation
  reality, env/config guidance, ops runbook notes, and planning/context
  surfaces.
- `PRJ-458..PRJ-460` are complete: runtime reality and operator docs now
  converge on persisted subconscious proposal inventory plus the concrete
  meaning of post-convergence health surfaces used during release and triage.
- `PRJ-461..PRJ-463` are complete: operator docs and planning/context now
  converge on affective health visibility plus retrieval execution-class
  diagnostics as first-class post-convergence triage surfaces.
- `PRJ-464..PRJ-467` are complete: migration parity is now restored for the
  full live model set, Alembic head creates durable attention and subconscious
  proposal tables, and schema-baseline regressions now prove fresh
  migration-first bootstrap against the current metadata baseline.
- `PRJ-468..PRJ-471` are complete: canonical architecture docs no longer carry
  a conflicting `plan -> action -> expression` flow, action docs now separate
  action-owned side effects from runtime follow-ups, and reader-entry docs now
  restate `02/15/16` as the canonical ownership set.

Planned on 2026-04-22 after full architecture-conformance analysis:

- the next queue is now seeded through `PRJ-491`.
- unlike the earlier convergence waves, this queue is driven by verified
  post-convergence gaps between canonical architecture, live runtime code,
  migration truth, and release-readiness evidence.
- the execution order intentionally starts with schema/migration truth, then
  canonical architecture-document consistency, then subsystem
  productionization and behavior-proof expansion.

New groups:

- `PRJ-464..PRJ-467` Migration parity and schema governance
- `PRJ-468..PRJ-471` Canonical docs consistency sweep
- `PRJ-472..PRJ-475` Connector execution productionization
- `PRJ-476..PRJ-479` Retrieval provider completion
- `PRJ-480..PRJ-483` Background worker externalization
- `PRJ-484..PRJ-487` Proactive runtime activation - complete
- `PRJ-488..PRJ-491` Role/skill maturity and behavior-validation expansion - complete

Why this order:

- migration parity is the biggest runtime-versus-deployment truth gap and must
  be fixed before any deeper productionization work
- canonical docs consistency comes next so later work does not amplify stale
  architecture wording
- connector, retrieval, background, and proactive groups each move one
  rollout-shaped subsystem toward the documented target-state
- the last group turns the remaining capability and behavior-proof gaps into
  explicit contracts and release evidence instead of aspirational docs

Detailed queue:

## Group 63 - Migration Parity And Schema Governance

Completed on 2026-04-22:

- `PRJ-464` audited model-vs-migration parity and confirmed the missing Alembic
  delta set was limited to `aion_attention_turn` and
  `aion_subconscious_proposal`, while earlier revisions already covered memory
  payload, scoped conclusions, semantic embeddings, and relation storage.
- `PRJ-465` added the missing Alembic revision for durable attention and
  subconscious proposal persistence, including indexes and named attention
  uniqueness constraint parity.
- `PRJ-466` expanded schema-baseline coverage so tests now exercise a fresh
  `alembic upgrade head` and inspect the resulting schema instead of checking
  `Base.metadata` only.
- `PRJ-467` synchronized planning/context and docs so migration-first schema
  ownership now describes the full live model set.

- `PRJ-464` Audit model-vs-migration parity and define the missing Alembic delta set.
  - Result:
    - one explicit inventory maps every live SQLAlchemy model/table and current
      column family to existing Alembic revisions
    - missing migration deltas are recorded before implementation starts
  - Validation:
    - targeted review across `app/memory/models.py`, `migrations/versions/`,
      and current schema docs

- `PRJ-465` Add Alembic revisions for durable attention and subconscious proposal persistence.
  - Result:
    - the migration chain creates `aion_attention_turn` and
      `aion_subconscious_proposal` with the same ownership assumptions as the
      live repository/runtime
  - Validation:
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_memory_repository.py`

- `PRJ-466` Add schema-parity regressions for migration-first startup against the current model baseline.
  - Result:
    - tests pin that migration-first environments can reach the current runtime
      schema without relying on `create_tables`
    - schema drift becomes release-visible instead of operator-discovered
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_main_lifespan_policy.py tests/test_main_runtime_policy.py`

- `PRJ-467` Sync docs/context for migration parity and schema governance.
  - Result:
    - planning, ops, implementation reality, testing guidance, and context
      truth all align on migration-first schema ownership for the actual live
      model set
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/implementation/`, `docs/operations/`, and `docs/engineering/`

## Group 64 - Canonical Docs Consistency Sweep

Completed on 2026-04-22:

- `PRJ-468` audit identified the concrete drift surface: older architecture
  docs in `05_conscious_subconscious.md` and `20_action_system.md`, plus
  reader-entry ambiguity in `docs/README.md` and `docs/overview.md`.
- `PRJ-469` rewrote those stale architecture docs to match the current
  canonical foreground order and post-action ownership split.
- `PRJ-470` aligned `docs/README.md` and `docs/overview.md` so readers are
  redirected to `02`, `15`, and `16` whenever numbered docs differ.
- `PRJ-471` synchronized planning/context truth so the completed docs sweep is
  recorded and the next lane can move on to connector execution.

- `PRJ-468` Audit canonical architecture docs for flow/order drift against `02`, `15`, and `16`.
  - Result:
    - one explicit inventory identifies stale files that still contradict the
      canonical `expression -> action` boundary, dual-loop ownership, or
      target-state wording
  - Validation:
    - targeted cross-review across `docs/architecture/`

- `PRJ-469` Rewrite stale architecture docs to match the current canonical contract set.
  - Result:
    - older architecture files stop contradicting `02_architecture.md`,
      `15_runtime_flow.md`, and `16_agent_contracts.md`
  - Validation:
    - cross-doc consistency review plus targeted wording regression note

- `PRJ-470` Align overview and docs index with the corrected canonical architecture narrative.
  - Result:
    - `docs/README.md` and `docs/overview.md` no longer inherit stale wording
      from pre-convergence phases
  - Validation:
    - doc sync across top-level docs surfaces

- `PRJ-471` Sync planning/context for canonical docs consistency.
  - Result:
    - context truth and planning surfaces record the architecture-doc sweep as
      complete and keep later slices grounded in one consistent target-state
  - Validation:
    - doc-and-context sync across `.codex/context/` and `docs/planning/`

## Group 65 - Connector Execution Productionization

Completed on 2026-04-22:

- `PRJ-472` fixed the MVP boundary explicitly: the first live provider-backed
  connector path is ClickUp task creation, while calendar, cloud-drive, and
  remaining task-system operations stay policy-only on purpose.
- `PRJ-473` implemented that path through a dedicated ClickUp task adapter and
  action-side execution behind the existing connector policy and action
  envelope guardrails.
- `PRJ-474` exposed machine-visible readiness posture through
  `/health.connectors.execution_baseline`, including configured vs
  credentials-missing state for the ClickUp path.
- `PRJ-475` synchronized contracts, runtime-reality, config, ops, testing, and
  planning/context truth around that narrow live baseline so the next lane can
  move on to retrieval-provider completion.

- `PRJ-472` Decide the MVP production boundary for connector execution adapters.
  - Result:
    - the repo explicitly records which connector families will gain real
      provider-backed execution now, and which remain proposal/suggestion-only
      on purpose
  - Validation:
    - cross-review across `open-decisions`, `16_agent_contracts.md`, and ops docs

- `PRJ-473` Implement the first provider-backed connector execution path behind existing policy gates.
  - Result:
    - at least one connector family moves from typed intent only to real
      guarded execution via integration adapters without breaking the action
      boundary
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- `PRJ-474` Add health/debug visibility and failure posture for provider-backed connector execution.
  - Result:
    - operators can distinguish proposal-only posture, authorized execution
      posture, and provider failure posture through runtime-visible surfaces
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- `PRJ-475` Sync docs/context for connector execution productionization.
  - Result:
    - architecture, runtime reality, ops, testing guidance, and context truth
      all describe the selected connector execution baseline
  - Validation:
    - doc-and-context sync across canonical docs, runtime reality, ops, and planning

## Group 66 - Retrieval Provider Completion

Completed on 2026-04-22:

- `PRJ-476` fixed the target provider-owned retrieval baseline explicitly:
  `openai_api_embeddings` is the intended production owner when
  `OPENAI_API_KEY` is configured, `local_hybrid` remains a local transition
  path, and deterministic remains the explicit compatibility fallback.
- `PRJ-477` implemented provider-owned OpenAI embedding materialization behind
  one shared repository/action owner path while preserving deterministic and
  local-hybrid fallback behavior.
- `PRJ-478` exposed machine-visible readiness posture through
  `/health.memory_retrieval` and startup warning behavior, including explicit
  production-baseline state/hint fields.
- `PRJ-479` synchronized contracts, runtime reality, env/config guidance, ops,
  testing, and planning/context truth around that retrieval baseline so the
  next lane can move on to background worker externalization.

- `PRJ-476` Define the target provider-owned retrieval baseline beyond deterministic fallback.
  - Result:
    - one explicit decision records the intended provider, execution mode,
      fallback posture, and operational baseline for production retrieval
  - Validation:
    - cross-review across retrieval docs, env/config, and open decisions

- `PRJ-477` Implement provider-owned semantic embedding execution for the selected baseline.
  - Result:
    - retrieval can run through a real provider-backed embedding path instead
      of only deterministic fallback or local placeholder execution
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-478` Add rollout/readiness evidence for provider-owned retrieval execution.
  - Result:
    - `/health`, startup policy, and release evidence clearly distinguish
      provider-owned steady state from fallback posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_runtime_policy.py`

- `PRJ-479` Sync docs/context for retrieval provider completion.
  - Result:
    - docs, planning, ops, and context truth all align on the real retrieval
      production baseline
  - Validation:
    - doc-and-context sync across implementation, ops, planning, and engineering docs

## Group 67 - Background Worker Externalization

Completed on 2026-04-22:

- `PRJ-480` fixed the deferred reflection external-worker baseline explicitly:
  the repo now treats a shared external-driver policy plus one canonical
  queue-drain entrypoint as the target production posture.
- `PRJ-481` implemented that path through
  `scripts/run_reflection_queue_once.py` with PowerShell/bash wrappers and
  startup policy logging.
- `PRJ-482` exposed machine-visible external-driver posture through
  `/health.reflection.external_driver_policy` and release-smoke validation.
- `PRJ-483` synchronized contracts, runtime reality, ops guidance, testing,
  and planning/context truth so the next lane can move on to proactive
  runtime activation.

- `PRJ-480` Define the production external-worker baseline for deferred reflection.
  - Result:
    - one explicit operating model records when `deferred` reflection becomes
      a true production baseline rather than a monitored rollout posture
  - Validation:
    - reflection topology and ops cross-review

- `PRJ-481` Implement the external-driver-ready reflection execution path and ownership checks.
  - Result:
    - deferred reflection path is complete enough to run without app-local
      worker ownership assumptions leaking back in
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- `PRJ-482` Add release-smoke and health evidence for external worker posture.
  - Result:
    - release validation can prove the selected background execution owner path
      instead of inferring it from logs
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- `PRJ-483` Sync docs/context for background worker externalization.
  - Result:
    - architecture, runtime reality, ops, and planning all describe the same
      background execution baseline
  - Validation:
    - doc-and-context sync across canonical docs, runtime reality, ops, and planning

## Group 68 - Proactive Runtime Activation

Completed on 2026-04-22:

- `PRJ-484` fixed the true MVP proactive runtime baseline explicitly:
  scheduler-owned cadence, opted-in candidate selection, Telegram delivery
  target fallback, and anti-spam thresholds now live behind one shared policy
  owner.
- `PRJ-485` made proactive cadence actually live in the in-process scheduler by
  selecting repository-backed candidates, emitting bounded scheduler events,
  and exposing tick summaries plus proactive policy posture through `/health`.
- `PRJ-486` expanded behavior validation so proactive runtime is proven through
  delivery-ready and anti-spam-blocked scenarios rather than helper contracts
  alone.
- `PRJ-487` synchronized planning/context, runtime reality, ops guidance, and
  testing guidance around the same proactive baseline so the next lane can
  move on to role/skill maturity and behavior-validation expansion.

- `PRJ-484` Define the true MVP proactive runtime baseline and anti-spam contract.
  - Result:
    - one explicit contract records what “live proactive” means for cadence,
      delivery target, unanswered throttles, cooldowns, and feedback loops
  - Validation:
    - cross-review across proactive architecture, guardrails, and runtime reality

- `PRJ-485` Implement live proactive cadence ownership beyond passive scheduler plumbing.
  - Result:
    - the system can actually emit bounded proactive wakeups under governed
      scheduler ownership instead of only holding engine/guard primitives
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-486` Add scenario-level behavior validation for proactive outreach quality and anti-spam posture.
  - Result:
    - proactive runtime is proven by behavior scenarios, not only by contracts
      and helper tests
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode operator`
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-487` Sync docs/context for proactive runtime activation.
  - Result:
    - planning, runtime reality, ops, testing guidance, and context truth all
      describe the same proactive baseline
  - Validation:
    - doc-and-context sync across implementation, ops, planning, and engineering docs

## Group 69 - Role/Skill Maturity And Behavior-Validation Expansion

Completed on 2026-04-22:

- `PRJ-488` fixed the long-term role-versus-skill boundary explicitly:
  skills remain metadata-only capability hints that inform role and planning,
  but never gain tool or side-effect ownership on their own.
- `PRJ-489` applied that boundary in runtime surfaces and contracts through one
  shared policy owner plus `/health.role_skill` and runtime debug visibility.
- `PRJ-490` expanded behavior validation so CI now proves role/skill boundary
  posture, connector execution posture, proactive cadence posture, and
  deferred reflection enqueue expectations in one artifact flow.
- `PRJ-491` synchronized planning/context, runtime reality, canonical
  contracts, behavior-testing guidance, and ops notes so the seeded
  post-convergence queue can close cleanly.

- `PRJ-488` Decide the long-term role-versus-skill execution boundary.
  - Result:
    - one explicit governance statement records whether skills remain
      metadata-only capability hints or grow into a fuller execution-assist
      layer
  - Validation:
    - architecture/planning cross-review across role/skill docs and runtime contracts

- `PRJ-489` Apply the selected role/skill maturity baseline in runtime surfaces and contracts.
  - Result:
    - runtime outputs, contracts, and health/debug surfaces reflect the chosen
      role/skill boundary instead of a partially transitional posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-490` Expand behavior-validation coverage for post-convergence architecture lanes.
  - Result:
    - behavior validation now covers connector execution posture, proactive
      cadence behavior, deferred/background execution expectations, and the
      strongest remaining continuity risks
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`

- `PRJ-491` Sync docs/context for role/skill maturity and behavior-validation expansion.
  - Result:
    - architecture, runtime reality, testing guidance, ops notes, and context
      truth all align on the final queue outcome
  - Validation:
    - doc-and-context sync across canonical docs, implementation docs, ops, testing, and planning

## Post-Queue Status

Completed on 2026-04-22:

- the seeded post-convergence queue through `PRJ-491` is now fully complete
- no seeded `READY` task remains on the task board
- the next slice should come only from new architecture analysis, runtime
  drift, release evidence, or operator-facing gaps

Planned on 2026-04-22 after post-queue architecture review:

- the next queue is now seeded through `PRJ-515`
- this queue no longer targets broad convergence; it targets the remaining
  transitional surfaces that still keep runtime reality slightly behind the
  canonical architecture or release-hardening intent

New groups:

- `PRJ-492..PRJ-495` Debug ingress retirement and admin boundary closure
- `PRJ-496..PRJ-499` External scheduler ownership rollout
- `PRJ-500..PRJ-503` Connector read posture and provider expansion baseline
- `PRJ-504..PRJ-507` Retrieval lifecycle and source-rollout closure
- `PRJ-508..PRJ-511` Reflection worker supervision and durability closure
- `PRJ-512..PRJ-515` Observability export and incident-evidence baseline

Why this order:

- debug ingress is still the most visible transitional boundary and should be
  frozen before further runtime expansion
- external scheduler ownership is the biggest remaining runtime-topology gap
  after proactive activation and deferred reflection external-driver baseline
- connector expansion should happen only after scheduler/debug boundaries are
  less transitional
- retrieval lifecycle closure comes after execution-boundary work so provider
  ownership and source rollout can harden without also moving operator surface
  assumptions
- reflection supervision and observability close the remaining operational gaps
  that still keep the architecture more inspectable locally than operationally

Detailed queue:

## Group 70 - Debug Ingress Retirement And Admin Boundary Closure

- `PRJ-492` Freeze the dedicated-admin debug ingress target and compatibility-retirement checklist.
  - Result:
    - one explicit contract records the long-term admin/debug ingress owner,
      which shared compatibility paths remain temporary, and which conditions
      allow shared-endpoint retirement
  - Validation:
    - architecture/planning cross-review across runtime policy, ops, and debug contracts

- `PRJ-493` Expose machine-visible admin-ingress posture and shared-ingress retirement blockers.
  - Result:
    - `/health.runtime_policy` and release evidence can show whether runtime is
      still on transitional shared ingress or aligned with the dedicated-admin
      target posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`

- `PRJ-494` Add release-smoke and operator guidance for dedicated-admin debug posture.
  - Result:
    - smoke and runbook flows can prove debug posture without relying on
      operator memory or shared-route assumptions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`

- `PRJ-495` Sync docs/context for debug ingress retirement and admin boundary closure.
  - Result:
    - canonical docs, implementation notes, ops guidance, testing guidance,
      and planning/context truth all describe the same admin-only debug target
  - Validation:
    - doc-and-context sync across planning, ops, implementation, architecture, and context

## Group 71 - External Scheduler Ownership Rollout

- `PRJ-496` Define the production external-scheduler owner baseline for maintenance and proactive cadence.
  - Result:
    - one explicit contract records when `externalized` scheduler ownership is
      considered production-aligned and what remains local fallback only
  - Validation:
    - scheduler/attention/planning cross-review across architecture, runtime reality, and ops

- `PRJ-497` Implement canonical external cadence entrypoints and ownership checks.
  - Result:
    - the repo provides explicit operator or automation entrypoints for
      maintenance and proactive cadence execution under external owner mode,
      without leaking app-local scheduling assumptions back into runtime
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-498` Add release and health evidence for external scheduler ownership posture.
  - Result:
    - `/health.scheduler` and smoke flows can distinguish in-process fallback
      from externalized production owner posture with machine-visible blockers
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py`

- `PRJ-499` Sync docs/context for external scheduler ownership rollout.
  - Result:
    - planning, implementation notes, ops guidance, and context truth align on
      the same cadence-owner production baseline
  - Validation:
    - doc-and-context sync across planning, ops, implementation, and context

Completed on 2026-04-22:

- `PRJ-496..PRJ-499` are complete: the repo now has one explicit external
  cadence-owner baseline with canonical maintenance/proactive entrypoints,
  machine-visible `/health.scheduler.external_owner_policy`, startup and
  release-smoke evidence, and synchronized docs/context truth around
  `externalized` target ownership plus in-process fallback posture.

## Group 72 - Connector Read Posture And Provider Expansion Baseline

- `PRJ-500` Decide the first live read-capable connector baseline beyond ClickUp task creation.
  - Result:
    - the repo records which read-oriented connector capability should become
      the next live provider-backed path and which families remain policy-only
  - Validation:
    - connector policy and architecture cross-review

Completed on 2026-04-22:

- `PRJ-500` is complete: the selected next live read-capable expansion path is
  `task_system:list_tasks` for `provider_hint=clickup`, while `calendar` and
  `cloud_drive` remain policy-only until their narrower read boundaries are
  designed explicitly.
- `PRJ-501` is complete: the repo now executes
  `external_task_sync_intent(operation="list_tasks", provider_hint="clickup",
  mode="read_only")` through the existing ClickUp adapter before delivery,
  keeping the planning and action boundary intact.
- `PRJ-502` is complete: `/health.connectors.execution_baseline` now
  distinguishes ClickUp mutation and read-capable live paths from the
  remaining policy-only families in one machine-visible baseline.
- `PRJ-503` is complete: contracts, runtime reality, ops notes, testing
  guidance, and planning/context truth now describe the same expanded
  task-system baseline (`clickup_create_task` plus `clickup_list_tasks`) while
  calendar and cloud-drive remain policy-only.

- `PRJ-501` Implement the selected read-capable connector adapter behind existing permission gates.
  - Result:
    - at least one connector read path becomes genuinely provider-backed while
      preserving existing planning and action boundaries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- `PRJ-502` Expose provider-read readiness and failure posture for the expanded connector baseline.
  - Result:
    - `/health.connectors.execution_baseline` can distinguish mutation-only,
      read-capable, and still-policy-only connector families in one view
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- `PRJ-503` Sync docs/context for connector read posture and provider expansion baseline.
  - Result:
    - contracts, runtime reality, ops notes, and planning/context truth all
      describe the same expanded connector execution boundary
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing, and context

## Group 73 - Retrieval Lifecycle And Source-Rollout Closure

- `PRJ-504` is complete: the repo now has one explicit retrieval lifecycle
  owner that freezes OpenAI as the target provider baseline, `local_hybrid` as
  transition owner, deterministic as compatibility fallback, `on_write` as the
  steady-state refresh owner, and semantic+affective coverage as the
  foreground rollout completion baseline.
- `PRJ-505` is complete: `/health.memory_retrieval` now exposes the retrieval
  lifecycle owner, provider drift posture, pending lifecycle gaps, and
  alignment state in one machine-visible surface instead of scattering that
  information across independent rollout hints.
- `PRJ-506` is complete: release smoke now verifies retrieval lifecycle policy
  owner plus alignment/drift posture from `/health.memory_retrieval`, and
  runtime regression coverage pins that the local-hybrid transition owner
  still exercises the active hybrid retrieval path.
- `PRJ-507` is complete: implementation reality, ops guidance, testing
  guidance, planning, and context truth now describe the same retrieval
  steady-state lifecycle owner, pending-gap posture, and release evidence
  contract.

- `PRJ-504` Define the production retrieval lifecycle baseline beyond current provider-owned materialization.
  - Result:
    - one explicit contract records the steady-state owner for refresh,
      source-family rollout completion, and fallback retirement posture
  - Validation:
    - retrieval architecture/planning cross-review

- `PRJ-505` Implement lifecycle visibility for refresh, pending source families, and provider fallback drift.
  - Result:
    - runtime and `/health.memory_retrieval` expose the remaining lifecycle
      gaps as first-class machine-readable posture instead of scattered hints
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_runtime_policy.py tests/test_api_routes.py`

- `PRJ-506` Add behavior and release evidence for retrieval lifecycle alignment.
  - Result:
    - behavior validation or smoke evidence can prove retrieval lifecycle
      alignment rather than only provider selection
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_runtime_pipeline.py`

- `PRJ-507` Sync docs/context for retrieval lifecycle and source-rollout closure.
  - Result:
    - planning, implementation, ops, and testing surfaces all describe the
      same retrieval steady-state lifecycle baseline
  - Validation:
    - doc-and-context sync across implementation, ops, testing, planning, and context

## Group 74 - Reflection Worker Supervision And Durability Closure

- `PRJ-508` is complete: the repo now has one explicit supervision policy owner
  for deferred reflection operations, freezing target runtime mode, external
  queue-drain owner, durable retry owner, queue-health states, and recovery
  actions before those signals are surfaced through runtime health.
- `PRJ-509` is complete: `/health.reflection` now exposes one shared
  supervision snapshot with queue-health state, blocking signals, and recovery
  actions, so deferred reflection backlog pressure no longer requires manual
  interpretation across task counters and topology fields.
- `PRJ-510` is complete: startup logs and release smoke now consume the same
  reflection supervision contract, so queue pressure and recovery posture are
  visible in both release evidence and runtime startup traces.

- `PRJ-508` Define the production supervision baseline for deferred reflection workers.
  - Result:
    - one explicit contract records queue-drain supervision, failure ownership,
      and what counts as production-ready deferred reflection operations
  - Validation:
    - reflection topology and ops cross-review

- `PRJ-509` Implement machine-visible supervision posture for deferred reflection execution.
  - Result:
    - runtime health and worker-facing scripts expose supervision posture,
      backlog pressure, and recovery guidance beyond one-shot queue drain
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_api_routes.py`

- `PRJ-510` Add release evidence for deferred reflection supervision and recovery posture.
  - Result:
    - smoke and ops flows can prove reflection durability posture across queue
      drain, backlog pressure, and recovery expectations
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`

- `PRJ-511` Sync docs/context for reflection worker supervision and durability closure.
  - Result:
    - architecture notes, runtime reality, ops guidance, and planning/context
      truth align on the same supervised deferred-worker baseline
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, planning, and context

## Group 75 - Observability Export And Incident-Evidence Baseline

- `PRJ-512` Define the minimum exportable observability baseline beyond local logs and `/health`.
  - Result:
    - one explicit contract records which runtime evidence must be exportable
      for incidents and releases instead of remaining console-only
  - Validation:
    - observability cross-review across architecture, ops, and logging docs

- `PRJ-513` Implement exportable runtime evidence for stage timings and policy posture.
  - Result:
    - the repo can produce machine-readable incident or release evidence for
      stage timings, policy posture, and key owner-mode surfaces without
      depending on ad hoc operator capture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`

- `PRJ-514` Extend behavior or smoke flows to consume the exported incident-evidence baseline.
  - Result:
    - behavior validation or smoke tooling can consume exported evidence
      directly, making observability part of done-state rather than optional
      local debugging
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_deployment_trigger_scripts.py`

- `PRJ-515` Sync docs/context for observability export and incident-evidence baseline.
  - Result:
    - planning, architecture, ops, testing guidance, and context truth all
      describe the same exportable observability baseline
  - Validation:
    - doc-and-context sync across architecture, ops, testing, planning, and context

## Post-Convergence Operating Mode

After `PRJ-453`, the repo no longer has a pre-seeded architecture queue.

Execution should now prefer:

- newly discovered drift between runtime truth, `/health`, `system_debug`, and
  canonical docs
- operator-facing hardening where release smoke, deployment evidence, or
  runtime policy still leave ambiguous posture
- focused behavioral gaps where existing architecture is documented but live
  runtime influence is not yet convincingly test-visible

Execution should now avoid:

- inventing placeholder queue groups only to preserve numbering momentum
- keeping stale historical queue-seeding notes at the top of canonical backlog
  files once those queues are already complete
- reopening resolved architecture decisions without a concrete runtime or
  operational trigger

Completed on 2026-04-21:

- `PRJ-329` is complete: canonical docs, runtime-reality notes, and context
  records now share the same identity/language/profile continuity baseline
  (explicit profile-versus-conclusion identity ownership, language continuity
  precedence, and request-scoped API user-id fallback boundary).
- `PRJ-330..PRJ-333` are complete: relation lifecycle is now explicit
  (refresh, value-shift reset, age-aware revalidation, expiration), trust
  influence now governs proactive/planning confidence posture through shared
  policy owners, and relation-lifecycle regressions plus docs/context sync are
  now in place.
- `PRJ-334..PRJ-337` are complete: bounded inferred goal/task promotion is now
  implemented with typed inferred/maintenance intents, no-duplicate/no-unsafe
  regressions, and synchronized docs/context ownership for internal planning
  growth.
- `PRJ-339..PRJ-342` are complete: affective fallback diagnostics are now
  structured and traceable, goal/task signal detection now includes guarded
  natural inline phrasing, Telegram webhook/listen smoke workflow is now
  operator-facing, and planning/context/ops docs are synchronized for this
  reliability lane.
- `PRJ-343..PRJ-346` are complete: inferred planning promotion now has
  delivery-reliability-aware trust gates, machine-visible gate diagnostics in
  planning/runtime debug surfaces, regression coverage, and synchronized
  docs/context truth.
- `PRJ-347..PRJ-350` are complete: behavior-validation CI-ingestion now has a
  machine-readable artifact contract, explicit `operator|ci` gate posture, and
  regression coverage for gate semantics.
- `PRJ-351..PRJ-354` are complete: artifact schema-version/taxonomy governance
  is now explicit, artifact-input gate evaluation is available, and regression
  coverage plus docs/context sync are complete for this lane.
- `PRJ-355..PRJ-358` are complete: deployment-trigger evidence capture,
  optional release-smoke evidence verification, dedicated script regressions,
  and synchronized docs/context are now in place for the Coolify-trigger
  reliability lane.
- `PRJ-359..PRJ-360` are complete: behavior-validation artifact-input
  evaluation now enforces schema-major compatibility in CI mode while
  preserving operator-mode compatibility, with synchronized docs/context for
  the new governance posture.
- `PRJ-361..PRJ-362` are complete: attention timing now has an explicit
  production baseline (`120ms` burst window, `5s` answered TTL, `30s` stale
  cleanup) with health-visible alignment posture and synchronized docs/context.
- after Group 40 closed, the next architecture-convergence queue is now seeded
  through `PRJ-394`, with new groups focused on background adaptive outputs,
  durable attention ownership, role/skill capability separation, and
  retrieval/theta governance.
- `PRJ-379..PRJ-382` are complete: background adaptive outputs now have an
  explicit summary contract, reflection snapshots surface that summary, and
  health/runtime debug make background-owned adaptive posture visible.
- `PRJ-383..PRJ-386` are complete: durable attention owner posture now exposes
  parity semantics (`persistence_owner`, `parity_state`) and
  `durable_inbox` mode preserves current turn-assembly baseline behavior.
- `PRJ-387..PRJ-390` are complete: role selection now emits bounded
  `selected_skills` metadata from a shared capability registry, and planning
  carries the same metadata without turning skills into side-effect owners.
- `PRJ-391..PRJ-394` are complete: runtime and `/health` now expose shared
  retrieval-depth policy snapshots plus bounded theta-influence diagnostics
  across foreground stages.
- after Group 44 closed, the next architecture-convergence queue is now seeded
  through `PRJ-410`, with new groups focused on role-selection evidence,
  affective rollout policy, reflection scope governance, and durable attention
  contract-store rollout.
- `PRJ-395..PRJ-398` are complete: role selection now has one shared policy
  owner with explicit selection reasons/evidence and bounded active-goal
  planning diagnostics through runtime debug surfaces.
- `PRJ-399..PRJ-402` are complete: affective assessment now has explicit
  rollout ownership, health/debug visibility, and deterministic fallback
  gating for policy-disabled versus classifier-unavailable posture.
- after Group 48 closed, the next architecture-convergence queue is now seeded
  through `PRJ-414`, with a new group focused on identity/profile ownership
  visibility and the next language-continuity governance follow-up.

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
- `PRJ-065..PRJ-068` completed adaptive-governance hardening by splitting
  reflection into concern-owned modules, adding anti-self-reinforcement guards,
  pruning low-leverage milestone pressure drift heuristics, and extending
  multi-goal reflection/planning coverage.
- `PRJ-069..PRJ-070` established the LangGraph migration boundary with explicit
  graph-compatible runtime state contracts and stage adapters around current
  modules, so migration can proceed incrementally without changing foreground
  behavior first.
- `PRJ-071` migrated foreground stage orchestration onto LangGraph while
  preserving stage-level contracts, logging visibility, and runtime pipeline
  behavior under regression coverage.
- `PRJ-072..PRJ-080` are complete: optional LangChain prompt wrappers landed,
  semantic retrieval contracts plus pgvector scaffold are now in place, hybrid
  retrieval diagnostics are observable, relation memory/reflection/runtime
  influence is implemented, and scheduler event/cadence contracts are now
  explicit in runtime/config surfaces.
- `PRJ-081` is complete: reflection enqueue is now durable even without active
  in-process worker ownership, reflection runtime mode is explicit
  (`in_process|deferred`), and reflection worker now supports one-shot pending
  queue execution for external scheduler/worker integration.
- `PRJ-087..PRJ-095` are complete: internal planning-state ownership is now
  explicitly separated from external connector projections; subconscious
  proposals are persisted with conscious handoff decisions and read-only
  research policy boundaries; proactive scheduler flow now applies an explicit
  attention gate; and connector contracts now include permission gates plus
  typed calendar/task synchronization intents.
- `PRJ-096` is complete: connected-drive access now has explicit planning and
  action contracts (`connected_drive_access_intent`), cloud-drive permission
  gates, and action-layer payload traceability without direct provider side
  effects.
- `PRJ-097` is complete: reflection now derives repeated unmet-connector
  expansion proposals, planning promotes accepted proposals into explicit
  capability-discovery intents, and action persists bounded
  `connector_expansion_update` traces with no self-authorized external access.
- `PRJ-098` is complete: runtime now exposes explicit `POST /event/debug` for
  internal full-runtime payload inspection with the same debug policy/token
  guardrails as `POST /event?debug=true`, while public `POST /event` responses
  remain compact by default.
- `PRJ-099..PRJ-110` are complete: debug compatibility hints are explicit on
  `POST /event?debug=true`, `/health` exposes attention posture, attention
  timing controls are now first-class runtime settings, and docs/context are
  synchronized for attention observability hardening.
- `PRJ-111..PRJ-120` are complete: production debug-token requirement is now an
  explicit policy surface (`PRODUCTION_DEBUG_TOKEN_REQUIRED`) with route-level
  enforcement, runtime-policy visibility, regression coverage, and
  synchronized ops/config docs.
- `PRJ-121..PRJ-130` are complete: runtime policy now emits explicit
  `debug_access_posture` and `debug_token_policy_hint` signals, startup logs
  include relaxed-token-requirement warnings for production debug mode, and
  health/runtime docs are synchronized with the new posture semantics.
- `PRJ-131..PRJ-140` are complete: strict rollout mismatch handling now includes
  `event_debug_token_missing=true` when production debug token policy requires
  a configured token, with aligned tests and synchronized ops/architecture/docs
  posture.
- `PRJ-141..PRJ-150` are complete: production debug query-compat hardening now
  has explicit shared mismatch ownership, stricter startup/API regression
  coverage, and synchronized env/ops/planning/runtime-reality docs for
  `EVENT_DEBUG_QUERY_COMPAT_ENABLED` posture.
- `PRJ-151..PRJ-160` are complete: compat-route sunset readiness now includes
  in-process usage telemetry (`event_debug_query_compat_telemetry`),
  explicit deprecation response header contract, and synchronized canonical
  docs/context coverage.
- `PRJ-161..PRJ-170` are complete: compat-route sunset recommendation signals
  (`event_debug_query_compat_allow_rate`,
  `event_debug_query_compat_block_rate`,
  `event_debug_query_compat_recommendation`) are now explicit in health
  contracts with aligned tests/docs/context.
- `PRJ-171..PRJ-180` are complete: compat-route sunset now exposes explicit
  machine-readable readiness fields
  (`event_debug_query_compat_sunset_ready`,
  `event_debug_query_compat_sunset_reason`), and recommendation logic now
  treats any observed compat attempts as migration-needed.
- `PRJ-181..PRJ-190` are complete: compat telemetry now includes rolling-window
  counters and health policy now exposes recent compat trend fields
  (`event_debug_query_compat_recent_attempts_total`,
  `event_debug_query_compat_recent_allow_rate`,
  `event_debug_query_compat_recent_block_rate`,
  `event_debug_query_compat_recent_state`).
- `PRJ-191..PRJ-200` are complete: compat rolling-trend refinement is now
  synchronized across health contracts, tests, and docs/context with explicit
  release-window trend semantics and attempt-based migration posture.
- `PRJ-201..PRJ-210` are complete: compat telemetry rolling-window size is now
  configurable (`EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW`) with bounded config
  validation and lifecycle/API wiring coverage.
- `PRJ-211..PRJ-220` are complete: `/health.runtime_policy` now exposes
  compat-route freshness posture (stale threshold, last-attempt age, and
  freshness state) with config-driven stale threshold
  (`EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`) and synchronized
  config/telemetry/API/docs context coverage.
- `PRJ-221..PRJ-230` are complete: `/health.runtime_policy` now exposes
  compat-route activity posture (`event_debug_query_compat_activity_state`,
  `event_debug_query_compat_activity_hint`) to separate
  disabled/no-attempt/stale-history/recent-traffic migration states while
  preserving existing sunset-ready contract semantics.
- `PRJ-231` is complete: semantic retrieval activation posture is now explicit
  through config/runtime (`SEMANTIC_VECTOR_ENABLED`) and `/health` operator
  visibility (`memory_retrieval.semantic_vector_enabled`,
  `memory_retrieval.semantic_retrieval_mode`), with regression coverage for
  config, action, runtime, and API health behavior.
- `PRJ-232` is complete: embedding strategy posture is now explicit through
  runtime config (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`,
  `EMBEDDING_DIMENSIONS`) and `/health.memory_retrieval` requested/effective
  provider-model visibility with deterministic-fallback hints.
- `PRJ-233` is complete: embedding provider readiness posture is now explicit
  in `/health.memory_retrieval` (`semantic_embedding_provider_ready`,
  `semantic_embedding_posture`) and startup now warns when requested embedding
  provider falls back to deterministic execution.
- `PRJ-234` is complete: conclusion embedding shells now align with configured
  embedding strategy posture (`provider/model/dimensions`) and persist
  requested-vs-effective provider metadata with explicit
  `pending_vector_materialization` status.
- `PRJ-235` is complete: embedding warning-state semantics are now shared
  between startup logging and `/health.memory_retrieval`, with explicit
  warning posture fields (`semantic_embedding_warning_state`,
  `semantic_embedding_warning_hint`) for operator diagnostics.
- `PRJ-236` is complete: embedding source-family scope is now explicit through
  `EMBEDDING_SOURCE_KINDS`, runtime embedding writes respect enabled families,
  and `/health.memory_retrieval` exposes effective configured source kinds.
- `PRJ-237` is complete: embedding source-coverage posture is now explicit in
  `/health.memory_retrieval` and startup warning logs share the same
  coverage-state semantics, reducing drift between operator diagnostics and
  startup guardrail signals.
- `PRJ-238` is complete: embedding refresh-cadence posture is now explicit
  through runtime config (`EMBEDDING_REFRESH_MODE`,
  `EMBEDDING_REFRESH_INTERVAL_SECONDS`), `/health.memory_retrieval` visibility
  (`semantic_embedding_refresh_mode`,
  `semantic_embedding_refresh_interval_seconds`), and startup warning coverage
  for manual refresh mode.
- `PRJ-239` is complete: embedding refresh posture semantics are now owned by
  the shared embedding strategy helper, including derived diagnostics
  (`semantic_embedding_refresh_state`,
  `semantic_embedding_refresh_hint`) reused by `/health.memory_retrieval` and
  startup refresh warning flow.
- `PRJ-240` is complete: embedding model-governance posture diagnostics are now
  explicit through shared helper semantics
  (`semantic_embedding_model_governance_state`,
  `semantic_embedding_model_governance_hint`) and startup warning alignment
  (`embedding_model_governance_warning`) for deterministic custom-model-name
  posture.
- `PRJ-241` is complete: embedding provider-ownership posture diagnostics are
  now explicit through shared helper semantics
  (`semantic_embedding_provider_ownership_state`,
  `semantic_embedding_provider_ownership_hint`), and startup fallback warnings
  now include shared ownership posture diagnostics.
- `PRJ-242` is complete: embedding provider-ownership enforcement posture is
  now explicit through runtime config
  (`EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT`) and shared helper diagnostics
  (`semantic_embedding_provider_ownership_enforcement`,
  `semantic_embedding_provider_ownership_enforcement_state`,
  `semantic_embedding_provider_ownership_enforcement_hint`), including strict
  startup block behavior for unresolved provider fallback ownership.
- `PRJ-243` is complete: embedding model-governance enforcement posture is now
  explicit through runtime config
  (`EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT`) and shared helper diagnostics
  (`semantic_embedding_model_governance_enforcement`,
  `semantic_embedding_model_governance_enforcement_state`,
  `semantic_embedding_model_governance_enforcement_hint`), including strict
  startup block behavior for deterministic custom-model-name governance posture.
- `PRJ-244` is complete: embedding owner-strategy recommendation posture is now
  explicit through shared helper diagnostics
  (`semantic_embedding_owner_strategy_state`,
  `semantic_embedding_owner_strategy_hint`,
  `semantic_embedding_owner_strategy_recommendation`) and startup fallback
  warning enrichment.
- `PRJ-245` is complete: embedding source-rollout recommendation posture is now
  explicit through shared helper diagnostics
  (`semantic_embedding_source_rollout_state`,
  `semantic_embedding_source_rollout_hint`,
  `semantic_embedding_source_rollout_recommendation`) and startup
  source-coverage warning enrichment.
- `PRJ-246` is complete: embedding strict-rollout preflight posture is now
  explicit through shared diagnostics
  (`semantic_embedding_strict_rollout_violations`,
  `semantic_embedding_strict_rollout_violation_count`,
  `semantic_embedding_strict_rollout_ready`,
  `semantic_embedding_strict_rollout_state`,
  `semantic_embedding_strict_rollout_hint`).
- `PRJ-247` is complete: embedding strict-rollout recommendations are now
  explicit through shared diagnostics
  (`semantic_embedding_strict_rollout_recommendation`,
  `semantic_embedding_recommended_provider_ownership_enforcement`,
  `semantic_embedding_recommended_model_governance_enforcement`).
- `PRJ-248` is complete: embedding enforcement-alignment posture is now
  explicit through shared diagnostics
  (`semantic_embedding_provider_ownership_enforcement_alignment`,
  `semantic_embedding_model_governance_enforcement_alignment`,
  `semantic_embedding_enforcement_alignment_state`,
  `semantic_embedding_enforcement_alignment_hint`).
- `PRJ-249` is complete: startup now emits `embedding_strategy_hint` with
  strict-rollout readiness, recommendations, and enforcement-alignment
  diagnostics from the same shared helper used by `/health`.
- `PRJ-250` is complete: planning/docs/context are synchronized through
  `PRJ-250` with targeted regression coverage for embedding strategy posture.
- `PRJ-251` is complete: source-rollout relation-aware completion posture is now
  explicit in shared diagnostics (`all_vector_sources_enabled`,
  `semantic_embedding_source_rollout_completion_state`,
  `semantic_embedding_source_rollout_next_source_kind`).
- `PRJ-252` is complete: source-rollout sequencing diagnostics are now explicit
  in shared helper outputs (`semantic_embedding_source_rollout_order`,
  `semantic_embedding_source_rollout_enabled_sources`,
  `semantic_embedding_source_rollout_missing_sources`).
- `PRJ-253` is complete: source-rollout progress diagnostics are now explicit
  (`semantic_embedding_source_rollout_phase_index`,
  `semantic_embedding_source_rollout_phase_total`,
  `semantic_embedding_source_rollout_progress_percent`).
- `PRJ-254` is complete: startup now emits `embedding_source_rollout_hint`
  while vectors are enabled and rollout still has pending source kinds.
- `PRJ-255` is complete: planning/docs/context are synchronized through
  `PRJ-255` with targeted regression coverage for source-rollout sequencing
  diagnostics.
- `PRJ-256` is complete: refresh cadence posture is now explicit in shared
  diagnostics (`semantic_embedding_refresh_cadence_state`,
  `semantic_embedding_refresh_cadence_hint`) for vectors-disabled, on-write,
  and manual high/moderate/low frequency modes.
- `PRJ-257` is complete: refresh strategy recommendation posture is now explicit
  in shared diagnostics (`semantic_embedding_recommended_refresh_mode`) with
  rollout-aware recommendation semantics.
- `PRJ-258` is complete: refresh recommendation alignment posture is now
  explicit through shared diagnostics
  (`semantic_embedding_refresh_alignment_state`,
  `semantic_embedding_refresh_alignment_hint`).
- `PRJ-259` is complete: startup now emits `embedding_refresh_hint` whenever
  refresh posture deviates from rollout recommendation, and refresh warning logs
  now include cadence diagnostics.
- `PRJ-260` is complete: planning/docs/context are synchronized through
  `PRJ-260` with targeted regression coverage for refresh strategy diagnostics.
- `PRJ-261` is complete: runtime config now exposes
  `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` (`warn|strict`) with defaults and
  validation.
- `PRJ-262` is complete: shared embedding strategy snapshot now exposes
  source-rollout enforcement diagnostics
  (`semantic_embedding_source_rollout_enforcement`,
  `semantic_embedding_source_rollout_enforcement_state`,
  `semantic_embedding_source_rollout_enforcement_hint`).
- `PRJ-263` is complete: `/health.memory_retrieval` now surfaces
  source-rollout enforcement posture for vectors-disabled, pending, and
  complete rollout states.
- `PRJ-264` is complete: startup now emits
  `embedding_source_rollout_warning` in warn mode and
  `embedding_source_rollout_block` in strict mode for pending source rollout.
- `PRJ-265` is complete: planning/docs/context are synchronized through
  `PRJ-265` with targeted regression coverage for source-rollout enforcement.
- `PRJ-266` is complete: source-rollout enforcement recommendation posture is
  now explicit through shared diagnostics
  (`semantic_embedding_recommended_source_rollout_enforcement`).
- `PRJ-267` is complete: source-rollout enforcement alignment primitive is now
  explicit through shared diagnostics
  (`semantic_embedding_source_rollout_enforcement_alignment`).
- `PRJ-268` is complete: source-rollout enforcement alignment state/hint are
  now explicit through shared diagnostics
  (`semantic_embedding_source_rollout_enforcement_alignment_state`,
  `semantic_embedding_source_rollout_enforcement_alignment_hint`).
- `PRJ-269` is complete: `/health.memory_retrieval` now surfaces source-rollout
  enforcement recommendation/alignment posture.
- `PRJ-270` is complete: startup source-rollout warning/block logs now include
  recommendation/alignment diagnostics from the shared snapshot.
- `PRJ-271` is complete: startup now emits
  `embedding_source_rollout_enforcement_hint` with current enforcement,
  recommendation, and alignment posture.
- `PRJ-272` is complete: snapshot regressions now pin source-rollout
  recommendation/alignment semantics across disabled, pending, complete, and
  strict aligned/blocked rollout states.
- `PRJ-273` is complete: `/health` API regressions now pin source-rollout
  recommendation/alignment fields across key rollout states.
- `PRJ-274` is complete: startup logging regressions now pin source-rollout
  enforcement hint posture plus warning/block recommendation/alignment fields.
- `PRJ-275` is complete: planning/docs/context are synchronized through
  `PRJ-275` with targeted regression coverage for source-rollout enforcement
  recommendation/alignment diagnostics.
- `PRJ-276` is complete: canonical runtime-flow and agent-contract docs now
  define one explicit foreground ownership split (runtime pre/post graph vs
  graph stage spine) plus migration invariants for stable stage contracts and
  ordering while convergence continues.
- `PRJ-277` is complete: expression now emits an explicit response-execution
  handoff contract consumed by action, preserving wording/tone ownership in
  expression while keeping execution ownership in action.
- `PRJ-278` is complete: runtime orchestration boundaries are now explicit in
  code through pre-graph seed ownership, graph-stage execution, and post-graph
  follow-up segments (`memory_persist`, `reflection_enqueue`, `state_refresh`).
- `PRJ-279` is complete: foreground architecture-parity regressions now pin
  API-stage ordering and logging-stage ownership surfaces, and planning/context
  docs are synchronized to the converged foreground boundary.
- `PRJ-280` is complete: reflection topology and worker-mode ownership contract
  is now explicit across canonical architecture, runtime reality, and runtime
  operations docs.
- `PRJ-281` is complete: runtime and scheduler now consume one shared
  enqueue/dispatch boundary contract for reflection ownership, keeping durable
  enqueue semantics while making dispatch intent explicitly mode-aware.
- `PRJ-282` is complete: `/health` and scheduler logs now expose explicit
  worker-mode handoff posture (`in_process|deferred`) for queue drain and retry
  ownership without changing reflection execution semantics.
- `PRJ-283` is complete: regression coverage now pins background-topology
  handoff guarantees across health topology, scheduler log posture, and
  exhausted-retry skip semantics.
- `PRJ-284` is complete: one production retrieval baseline now defines provider
  ownership, refresh ownership, default vector posture, and family rollout
  order (`episodic+semantic -> affective -> relation`) across planning,
  architecture, runtime-reality, and operations docs.
- `PRJ-285` is complete: semantic conclusions now materialize embeddings on
  write (with deterministic fallback posture when provider execution is not yet
  implemented), and episodic embedding writes now honor explicit refresh
  ownership (`materialized_on_write` vs `pending_manual_refresh`).
- `PRJ-286` is complete: affective and relation embedding families now
  participate in source-gated rollout with explicit refresh ownership metadata,
  and hybrid vector retrieval now includes relation source-family queries.
- `PRJ-287` is complete: production retrieval rollout posture is now
  regression-pinned across embedding strategy, health API contracts, context
  summaries, and runtime hybrid-loading defaults.

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

- `PRJ-065` is complete.
  - Result:
    - reflection logic is separated into preference, progress, affective, and
      adaptive-state concern owners
    - `app/reflection/worker.py` stops being the single home for unrelated
      inference logic
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-066` is complete.
  - Result:
    - `preferred_role`, `theta`, and `collaboration_preference` require
      stronger evidence and outcome-aware updates
    - the runtime stops learning mainly from its own previous guesses and
      instead prefers user-visible signals or durable success evidence
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_expression_agent.py`

- `PRJ-067` is complete.
  - Result:
    - milestone arc/pressure/due-window heuristics are reviewed for actual
      downstream effect
    - low-value signals are removed, merged, or gated behind clearer evidence
      thresholds
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py`

- `PRJ-068` is complete.
  - Result:
    - regression coverage explicitly proves that one active goal does not leak
      reflected state into another
    - runtime behavior is pinned for users with more than one live objective
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_context_agent.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

## Group 11 - Graph Orchestration Adoption

This group aligns the runtime with the architecture-level stack direction
without forcing a big-bang rewrite of the current working orchestrator.

- `PRJ-069` is complete.
  - Result:
    - docs and runtime contracts describe which current orchestrator fields map
      directly into graph state
    - migration can proceed incrementally instead of rewriting all stages at
      once
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_state_contract.py tests/test_runtime_pipeline.py`

- `PRJ-070` is complete.
  - Result:
    - current perception, context, motivation, role, planning, expression, and
      action modules can be called through graph-ready adapters
    - repo preserves current behavior while preparing the LangGraph runtime
      shape
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_stage_adapters.py tests/test_runtime_pipeline.py`

- `PRJ-071` is complete.
  - Result:
    - the main foreground pipeline runs through LangGraph while preserving
      existing stage boundaries, logs, and response contracts
    - current runtime behavior stays regression-covered during the migration
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py tests/test_graph_state_contract.py tests/test_graph_stage_adapters.py`

- `PRJ-072` is complete.
  - Result:
    - LangChain is used narrowly for prompt templates, retrievers, or parsing
      where it materially reduces boilerplate
    - the repo avoids turning LangChain into the architectural core
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_openai_prompting.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

## Group 12 - Semantic Retrieval Infrastructure

This group upgrades memory retrieval from heuristics-only ranking to a hybrid
system that can use embeddings and pgvector where that improves relevance.

- `PRJ-073` is complete.
  - Result:
    - repo has one explicit contract for embeddings, vectorized records, and
      similarity retrieval inputs/outputs
    - semantic retrieval can evolve without leaking provider-specific details
      into stage logic
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_semantic_contracts.py tests/test_memory_repository.py tests/test_schema_baseline.py`

- `PRJ-074` is complete.
  - Result:
    - PostgreSQL gains pgvector-compatible schema and indexes for semantic
      retrieval
    - deploy and migration docs explicitly cover the new dependency
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_memory_repository.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

- `PRJ-075` is complete.
  - Result:
    - runtime can rank memory using recency, explicit scope, lexical overlap,
      and vector similarity
    - semantic retrieval complements rather than replaces current deterministic
      retrieval behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`

- `PRJ-076` is complete.
  - Result:
    - logs and tests show when vector retrieval helps, misses, or conflicts
      with lexical ranking
    - retrieval quality becomes measurable instead of anecdotal
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_logging.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`

## Group 13 - Relation System

This group adds the user-specific relation layer described in architecture so
the personality can accumulate durable interpersonal understanding, not only
generic conclusions and task state.

- `PRJ-077` is complete.
  - Result:
    - repo gets an explicit relation model with confidence, scope, and decay
      semantics
    - relation storage is separated from generic conclusions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_schema_baseline.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

- `PRJ-078` is complete.
  - Result:
    - subconscious processing can derive relation hypotheses from repeated
      interactions and update them gradually
    - relation updates follow explicit confidence and safety rules
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-079` is complete.
  - Result:
    - runtime can retrieve relevant high-confidence relations per turn
    - relation signals influence behavior in a controlled, testable way
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_role_agent.py tests/test_planning_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

## Group 14 - Scheduled And Proactive Runtime

This group adds the missing background cadence and proactive behavior described
in architecture so the personality can initiate helpful, bounded actions over
time rather than only react to incoming events.

- `PRJ-080` is complete.
  - Result:
    - scheduler-originated events become a first-class documented input source
    - reflection cadence, maintenance cadence, and proactive cadence have one
      contract owner
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_event_normalization.py tests/test_scheduler_contracts.py`

- `PRJ-081` is complete.
  - Result:
    - reflection ownership no longer assumes only in-process wakeups
    - runtime can move toward a dedicated worker or scheduled execution without
      rewriting reflection logic again
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

- `PRJ-082` is complete.
  - Result:
    - in-process scheduler cadence now executes reflection and maintenance
      routines without requiring user-event turns
    - reflection cadence dispatch is mode-aware (`in_process|deferred`) to
      avoid duplicate in-process worker ownership while still supporting
      deferred queue draining
    - `/health` now exposes scheduler runtime posture and latest tick summaries
      for operator-visible cadence wiring
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_scheduler_contracts.py tests/test_api_routes.py tests/test_config.py tests/test_reflection_worker.py tests/test_main_lifespan_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- `PRJ-083` is complete.
  - Result:
    - proactive suggestions, reminders, warnings, or encouragement can be
      selected from explicit triggers and bounded decision rules
    - interruption cost and user context are part of the decision model
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- `PRJ-084` is complete.
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

- `PRJ-085` is complete.
  - Result:
    - architecture and runtime contracts define one explicit inbox for
      user-originated events, scheduler ticks, and subconscious proposals
    - conversational turn assembly has one contract owner instead of ad hoc
      per-message handling
    - subconscious outputs are modeled as proposals for conscious evaluation,
      not direct user-visible actions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_state_contract.py`

- `PRJ-086` is complete.
  - Result:
    - Telegram burst messages now coalesce into one assembled conscious turn
      through shared pending-turn ownership in the API ingress path
    - pending/claimed/answered state now prevents duplicate runtime runs during
      short burst windows by returning queued no-op metadata for non-owner
      events
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

- `PRJ-097` is complete.
  - Result:
    - the personality can notice repeated unmet needs and propose connector or
      capability expansion without self-authorizing new external access
    - user-facing extension suggestions become explicit, bounded outputs of the
      runtime instead of hidden side effects
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_reflection_worker.py`
    - `.\.venv\Scripts\python -m pytest -q`

## Group 17 - Foreground Runtime Convergence

This group closes the remaining ambiguity in the foreground execution spine so
the live runtime can keep moving toward the canonical architecture without
reopening basic stage-ownership questions on every slice.

- `PRJ-276` Define target-state foreground ownership and graph boundary invariants.
  - Result:
    - one explicit target-state ownership contract defines which foreground
      segments stay graph-owned versus runtime-owned (`baseline load`, stage
      graph, episodic memory write, reflection trigger)
    - migration invariants make it explicit which stage contracts and ordering
      guarantees must remain stable while the orchestration boundary evolves
  - Validation:
    - doc-and-context sync plus targeted contract diff review recorded in this
      slice

- `PRJ-277` Introduce an explicit response-execution contract for expression-to-action handoff.
  - Result:
    - expression produces a handoff that preserves wording/tone ownership while
      action remains the sole execution owner
    - the repo no longer depends on implicit delivery coupling to keep
      expression-before-action behavior working
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py`

- `PRJ-278` Align graph/runtime orchestration boundaries for baseline load, memory write, and reflection trigger.
  - Result:
    - graph-owned and runtime-owned segments are explicit in code rather than
      hidden in orchestration shortcuts
    - foreground flow can evolve toward the canonical architecture without
      losing traceability or breaking the action boundary
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_graph_state_contract.py tests/test_graph_stage_adapters.py tests/test_main_lifespan_policy.py`

- `PRJ-279` Add foreground architecture-parity regressions and sync docs/context.
  - Result:
    - regression coverage now fails quickly when foreground ordering or stage
      ownership drifts away from the agreed target-state contract
    - architecture, planning, and context docs describe the same foreground
      boundary truth
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py tests/test_graph_state_contract.py`

## Group 18 - Background Reflection Topology

This group turns reflection from a "current app-local behavior plus future
intent" story into an explicit topology contract that can support either
in-process or external execution without rewriting the cognitive boundary.

- `PRJ-280` Define target-state reflection topology and worker-mode contract.
  - Result:
    - reflection ownership becomes explicit across in-process scheduler mode,
      external worker mode, queue semantics, and operator health posture
    - the repo records which background concerns are durable architecture and
      which are temporary execution choices
  - Validation:
    - doc-and-context sync plus targeted topology review recorded in this slice

- `PRJ-281` Extract the reflection enqueue/dispatch boundary from app-local scheduler ownership.
  - Result:
    - reflection enqueue and dispatch stop assuming one in-process owner
    - scheduler and runtime can share one explicit dispatch boundary instead of
      duplicating reflection ownership rules
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_main_lifespan_policy.py`

- `PRJ-282` Add worker-mode health, queue-drain, and retry handoff contract.
  - Result:
    - `/health` and runtime logs expose the worker-mode posture needed for
      in-process and external-driver operation
    - queue-drain and retry behavior can be safely handed to an external driver
      without changing reflection semantics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_api_routes.py tests/test_scheduler_worker.py tests/test_logging.py`

- `PRJ-283` Add background-topology regressions and sync docs/context.
  - Result:
    - background execution ownership, retry posture, and worker-mode guarantees
      are pinned by tests
    - planning, project state, and operations docs stay aligned with the new
      reflection topology contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

## Group 19 - Production Memory Retrieval Rollout

This group moves retrieval from "contracts plus diagnostics" toward a planned
production baseline that is explicit about provider ownership, refresh
semantics, and family-by-family rollout.

- `PRJ-284` is complete.
  - Result:
    - the repo records one target production baseline for embedding provider,
      refresh strategy, default vector posture, and memory-family rollout order
    - later retrieval work can implement toward a stable target instead of
      reopening rollout strategy on each slice
  - Validation:
    - doc-and-context sync plus targeted retrieval-baseline review recorded in
      this slice

- `PRJ-285` is complete.
  - Result:
    - semantic and episodic records can materialize provider-backed vectors with
      explicit fallback and refresh ownership
    - retrieval stops treating semantic vectors as mostly diagnostic shells
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py`

- `PRJ-286` is complete.
  - Result:
    - affective and relation memory families join the rollout behind explicit
      source-family gates and completion semantics
    - retrieval posture can distinguish baseline semantic rollout from full
      target-state memory coverage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-287` is complete.
  - Result:
    - health diagnostics, runtime defaults, and retrieval behavior are pinned
      against the agreed production rollout posture
    - planning, context, and operations docs now describe the same retrieval
      baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_context_agent.py tests/test_runtime_pipeline.py`

- `PRJ-288` is complete.
  - Result:
    - canonical architecture now defines one adaptive influence governance
      baseline for affective, relation, preference, and theta signals
    - evidence thresholds, precedence order, and tie-break boundaries are now
      explicit so adaptive influence no longer expands through undocumented
      heuristics
  - Validation:
    - doc-and-context sync plus targeted adaptive-policy review recorded in this
      slice
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

## Group 20 - Adaptive Cognition Governance

This group keeps richer cognition aligned with the architecture by making
evidence thresholds and influence scope explicit before adaptive signals spread
further through runtime behavior.

- `PRJ-288` is complete.
  - Result:
    - the repo has one explicit policy for how affective, relation, preference,
      and theta signals may influence future runtime behavior
    - adaptive signals stop expanding through undocumented tie-breakers
  - Validation:
    - doc-and-context sync plus targeted adaptive-policy review recorded in
      this slice
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- `PRJ-289` is complete.
  - Result:
    - core cognition stages consume one governed adaptive-policy owner instead
      of ad hoc signal checks
    - role and planning behavior remain explainable as the architecture grows
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_adaptive_policy.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- `PRJ-290` is complete.
  - Result:
    - proactive and attention behavior can use relation/theta context only
      through explicit policy surfaces
    - adaptive cues do not silently bypass attention or anti-spam guardrails
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_adaptive_policy.py`

- `PRJ-291` is complete.
  - Result:
    - anti-feedback-loop, cross-goal-leakage, and adaptive influence scope
      expectations are pinned by regression coverage
    - docs and context describe the same adaptive governance rules
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

## Group 21 - Attention And Proposal Execution Boundary

This group finishes the dual-loop execution boundary so subconscious proposals,
turn assembly, proactive delivery, and external permission gates all pass
through one explicit conscious ownership path.

- `PRJ-292` is complete.
  - Result:
    - proposal persistence, handoff decisions, and pending-turn ownership have
      one explicit contract owner
    - future dual-loop changes no longer need to infer whether attention or
      planning owns a boundary
  - Validation:
    - doc-and-context sync plus targeted dual-loop contract review recorded in
      this slice

- `PRJ-293` is complete.
  - Result:
    - subconscious proposals can persist durably and re-enter conscious runtime
      through explicit handoff decisions
    - user-visible actions remain blocked until conscious runtime accepts or
      merges a proposal
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_planning_agent.py`

- `PRJ-294` is complete.
  - Result:
    - proactive delivery and external-connector permission outcomes now share
      one conscious execution boundary
    - connector suggestions and outreach plans stop bypassing the same gating
      model used for batched conversation handling
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_planning_agent.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- `PRJ-295` is complete.
  - Result:
    - turn assembly, proposal handoff, proactive delivery, and permission-gated
      external intent flows are pinned end to end
    - docs and context now describe one coherent dual-loop execution model
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py tests/test_action_executor.py tests/test_planning_agent.py`

## Group 22 - Operational Hardening And Release Truth

This group turns the remaining production and release posture questions into an
explicit target baseline so the repo can be built toward the intended system,
not around temporary convenience defaults.

- `PRJ-296` is complete.
  - Result:
    - one target production baseline defines migration-only startup posture,
      strict policy defaults, and the intended internal-versus-public debug
      boundary
    - later hardening slices can remove temporary rollout ambiguity instead of
      creating more diagnostic layers
  - Validation:
    - doc-and-context sync plus targeted production-baseline review recorded in
      this slice

- `PRJ-297` is complete.
  - Result:
    - runtime and config boundaries reflect the agreed production target while
      keeping any temporary escape hatches explicit and reviewable
    - startup and API policy posture move closer to the final deployment shape
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

- `PRJ-298` is complete.
  - Result:
    - deployment automation, manual fallback, and release smoke ownership are
      documented as one coherent operational path
    - execution work stops assuming deploy behavior that operations cannot yet
      prove
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`

- `PRJ-299` is complete.
  - Result:
    - `/health` now exposes a compact `release_readiness` gate snapshot and
      release smoke scripts fail fast when production-policy drift is detected
    - release-readiness regressions and operational docs now match the
      target-state production baseline
    - planning, project state, and runbook truth remain synchronized at the end
      of the convergence queue
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`

- `PRJ-300` is complete.
  - Result:
    - first post-convergence execution queue is now seeded through
      `PRJ-304`, focused on reflection runtime-mode deployment posture and
      external dispatch readiness decisions
    - task board and planning docs now expose one explicit next lane instead of
      stopping at the end of `PRJ-299`
  - Validation:
    - doc-and-context sync plus targeted planning coherence review recorded in
      this slice

- `PRJ-301` is complete.
  - Result:
    - production reflection deployment baseline is now explicit:
      `REFLECTION_RUNTIME_MODE=in_process` remains default posture
    - deferred reflection dispatch now has explicit external-readiness criteria
      instead of implicit operator interpretation
  - Validation:
    - doc-and-context sync plus targeted reflection-topology contract review
      recorded in this slice

- `PRJ-302` is complete.
  - Result:
    - `/health.reflection` now includes deployment-readiness posture
      (`ready`, `blocking_signals`, baseline/selected runtime mode)
    - reflection mode migration can now be verified through health contract
      signals instead of log-only interpretation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_reflection_worker.py`

- `PRJ-303` is complete.
  - Result:
    - reflection deployment-readiness regressions now pin runtime-mode,
      handoff, and task-health blocker signals through shared contract helpers
      and `/health` integration
    - release smoke scripts now fail fast when reflection deployment-readiness
      blockers are present (with fallback checks for older runtimes)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_scheduler_contracts.py`

- `PRJ-304` is complete.
  - Result:
    - reflection deployment baseline/readiness docs are now synchronized across
      planning, runtime-reality, and ops runbook surfaces
    - release and rollback guidance now consistently treats reflection
      deployment-readiness blockers as release-gating signals
  - Validation:
    - doc-and-context sync plus targeted ops-runbook review recorded in this
      slice

- `PRJ-305` is complete.
  - Result:
    - next post-reflection execution queue is now seeded through `PRJ-309`
      from remaining open decisions
    - queue continuity is preserved after `PRJ-304` with explicit
      decision-linked slices instead of ad-hoc backlog picks
  - Validation:
    - doc-and-context sync plus targeted planning coherence review recorded in
      this slice

- `PRJ-306` is complete.
  - Result:
    - migration-strategy follow-up now has explicit guardrails and removal
      criteria for retiring `create_tables` compatibility startup path
    - removal rollout order is now codified (freeze usage -> remove code path
      -> clean compatibility references/tests)
  - Validation:
    - doc-and-context sync plus targeted migration-strategy review recorded in
      this slice

- `PRJ-307` is complete.
  - Result:
    - public-api follow-up decision now has explicit target-state ingress
      contract and migration ownership boundaries
    - debug-surface hardening can proceed without redefining runtime-policy
      baselines each slice
  - Validation:
    - doc-and-context sync plus targeted public-api boundary review recorded in
      this slice

## Group 23 - Runtime Behavior Testing Architecture

This group makes behavior validation a first-class architectural concern so the
repo can prove that cognition works across time, not only that contracts and
unit paths look correct in isolation.

- `PRJ-310` is complete.
  - Result:
    - architecture explicitly defines required behavior-testing modes
      (`system_debug`, `user_simulation`) plus minimum internal debug fields
    - future cognitive work can be validated against one shared behavior
      contract instead of ad-hoc debug expectations
  - Validation:
    - doc-and-context sync plus targeted behavior-testing architecture review
      recorded in this slice

- `PRJ-311` is complete.
  - Result:
    - internal debug responses now expose explicit `system_debug` fields for
      normalized event metadata, memory bundle visibility, context,
      motivation, role, plan intents, expression, and action traces
    - behavior debugging no longer depends on scattered endpoint-specific
      payloads or log-only interpretation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_logging.py`

- `PRJ-312` is complete.
  - Result:
    - behavior scenarios now emit structured pass/fail/skip outputs with
      `test_id`, `status`, `reason`, `trace_id`, and notes
    - scenario execution becomes repeatable for Codex agents, operators, and
      release workflows
  - Validation:
    - `.\scripts\run_behavior_validation.ps1`
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_scheduler_contracts.py`

- `PRJ-313` is complete.
  - Result:
    - canonical docs, engineering guidance, and project context all describe
      the same behavior-validation baseline
    - future slices can rely on one documented contract for behavior testing
  - Validation:
    - doc-and-context sync plus targeted cross-doc consistency review recorded
      in this slice

## Group 24 - Memory, Continuity, And Failure Validation

This group turns the new behavior-testing contract into concrete scenarios that
can prove whether AION feels alive rather than only structurally compliant.

- `PRJ-314` is complete.
  - Result:
    - scenario suite now proves `write -> retrieve -> influence -> delayed
      recall` instead of only memory persistence mechanics
    - memory can no longer be treated as complete when it fails to shape later
      turns
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_memory_repository.py tests/test_api_routes.py`

- `PRJ-315` is complete.
  - Result:
    - scenario coverage now validates identity continuity, tone stability, and
      goal/context reuse across session gaps
    - continuity regressions become visible before they reach user-facing
      runtime behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_expression_agent.py tests/test_planning_agent.py tests/test_language_runtime.py`

- `PRJ-316` is complete.
  - Result:
    - failure-mode scenarios now verify that the runtime stays explainable and
      stable under contradiction, incomplete context, and chaotic input
    - fallback quality becomes part of architecture validation instead of an
      untested assumption
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_motivation_engine.py tests/test_expression_agent.py`

- `PRJ-317` is complete.
  - Result:
    - release readiness now considers behavior-driven validation for memory,
      continuity, and failure handling, not only subsystem health
    - runbook, planning, and project state remain aligned on the living-system
      validation baseline
  - Validation:
    - `.\scripts\run_behavior_validation.ps1`
    - `.\.venv\Scripts\python -m pytest -q`

## Group 25 - Internal Debug Ingress Migration

This group turns the resolved internal-debug boundary decision into live code so
system-debug behavior stops depending on the shared public service endpoint as a
long-term posture.

Status update (2026-04-20): `PRJ-318..PRJ-321` are complete.

- `PRJ-318` Implement a dedicated internal debug ingress boundary and shared guard path.
  - Result:
    - runtime exposes one explicit internal debug ingress boundary that owns
      `system_debug` access semantics
    - shared-endpoint debug access stops being the primary long-term owner of
      internal cognitive inspection
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`

- `PRJ-319` Add break-glass override and shared-endpoint sunset posture for debug access.
  - Result:
    - public debug access can be explicitly downgraded to break-glass-only
      posture while preserving controlled emergency access
    - release posture makes it clear when shared-endpoint debug is transitional
      instead of baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- `PRJ-320` Add debug-ingress migration regressions and smoke coverage.
  - Result:
    - API regressions and smoke checks now pin internal-ingress ownership plus
      shared-endpoint sunset behavior
    - architecture drift around debug exposure fails quickly
  - Validation:
    - `.\scripts\run_release_smoke.ps1`
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`

- `PRJ-321` Sync docs/context/runbook for internal debug ingress migration.
  - Result:
    - docs, planning, project state, and runbook truth stay aligned with the
      new internal debug ingress baseline
    - later release-window decisions can be made without reopening the same API
      boundary ambiguity
  - Validation:
    - doc-and-context sync plus targeted debug-ingress cross-doc review
      recorded in this slice

## Group 26 - Scheduler Externalization And Attention Ownership

This group moves scheduler and attention ownership closer to the intended
architecture by making cadence execution mode explicit in code rather than only
in planning decisions.

- `PRJ-322` Implement owner-aware scheduler execution mode and health snapshot. (complete)
  - Result:
    - scheduler runtime exposes one explicit owner mode for cadence execution
      (`in_process|externalized`)
    - operators can see whether maintenance/proactive cadence is app-local or
      externally owned without inferring from scattered signals
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_config.py`

- `PRJ-323` Route maintenance and proactive cadence through the shared owner-aware dispatch boundary. (complete)
  - Result:
    - cadence ownership becomes explicit in scheduler/runtime dispatch instead
      of hidden behind in-process assumptions
    - externalization groundwork no longer depends on reflection-only
      ownership paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_api_routes.py`

- `PRJ-324` Add attention-inbox ownership posture for future durable coordination rollout. (complete)
  - Result:
    - attention coordination now exposes one explicit owner posture for
      in-process versus durable inbox evolution
    - future durable attention work gets a clean implementation seam instead of
      ad-hoc migration
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_scheduler_contracts.py`

- `PRJ-325` Sync docs/context/runbook for scheduler externalization and attention ownership.
  - Result:
    - docs, planning, and ops truth remain aligned with owner-aware cadence and
      attention posture
    - later rollout slices can build on explicit scheduler ownership instead of
      re-planning it
  - Validation:
    - doc-and-context sync plus targeted scheduler/attention cross-doc review
      recorded in this slice

## Group 27 - Identity, Language, And Profile Boundary Hardening

This group makes identity continuity more explicit in code by tightening the
boundary between profile state, conclusions, and language behavior.

- `PRJ-326` Refactor identity loading around explicit profile-versus-conclusion ownership.
  - Result:
    - runtime identity loading uses one clear owner for durable profile fields
      versus learned conclusions
    - identity continuity stops relying on fuzzy fallback chains
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-327` Add richer language continuity policy across profile, memory, and current turn context.
  - Result:
    - language choice can use a clearer precedence model across current turn,
      recent memory, and durable preference state
    - multilingual continuity becomes more architecture-aligned and less
      heuristic-only
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_context_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

- `PRJ-328` Add identity and language continuity regressions across session and API fallback boundaries.
  - Result:
    - identity/language continuity is pinned across multi-session behavior,
      ambiguous turns, and API user-id fallback paths
    - drift between profile state and response behavior becomes visible quickly
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- `PRJ-329` Sync docs/context for identity, language, and profile boundary hardening.
  - Result:
    - canonical docs, implementation reality, and project context describe the
      same identity continuity baseline
    - future identity work can build on explicit ownership boundaries
  - Validation:
    - doc-and-context sync plus targeted identity-boundary cross-doc review
      recorded in this slice

## Group 28 - Relation Lifecycle And Trust Influence

This group closes the gap between relation storage and relation-driven behavior
by making decay, revalidation, and trust influence explicit in code.

- `PRJ-330` Implement relation decay and confidence revalidation policy.
  - Result:
    - relation records can weaken, refresh, or expire based on evidence age and
      repeated interaction quality
    - relation memory becomes lifecycle-aware instead of purely additive
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-331` Extend planning, motivation, and proactive logic with governed trust signals.
  - Result:
    - relation cues can shape interruption cost, planning confidence, and
      outreach tone through explicit trust rules
    - trust influence becomes a coded behavior path instead of a future note
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-332` Add relation lifecycle and trust-influence regressions.
  - Result:
    - decay, refresh, and trust-driven behavior expectations are pinned end to
      end
    - relation drift becomes test-visible before it affects production behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_expression_agent.py`

- `PRJ-333` Sync docs/context for relation lifecycle and trust influence.
  - Result:
    - docs, planning, and project state align on how relations evolve and where
      they influence behavior
    - future relational capability work starts from one explicit baseline
  - Validation:
    - doc-and-context sync plus targeted relation-lifecycle cross-doc review
      recorded in this slice

## Group 29 - Goal/Task Inference And Typed-Intent Expansion

This group grows internal planning capability in code while preserving explicit
intent ownership and action-layer control.

- `PRJ-334` Add inferred goal/task promotion rules to planning.
  - Result:
    - planning can propose bounded inferred goals/tasks from repeated evidence
      instead of relying only on explicit user declarations
    - internal planning growth becomes a deliberate coded behavior rather than a
      future aspiration
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`

- `PRJ-335` Expand typed domain intents for inferred planning state and controlled maintenance writes.
  - Result:
    - inferred goal/task promotion and related maintenance writes stay blocked
      behind explicit typed intents
    - action remains the sole owner of durable planning-state side effects
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- `PRJ-336` Add regressions for inferred planning growth and no-duplicate/no-unsafe promotion behavior.
  - Result:
    - inferred planning growth is pinned against duplicate, unsafe, or weakly
      evidenced promotions
    - architecture drift on internal planning autonomy fails fast
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py`

- `PRJ-337` Sync docs/context for goal/task inference and typed-intent expansion.
  - Result:
    - docs, planning, and project state align on how internal planning can grow
      while staying subordinate to typed intent ownership
    - later autonomy work can build on explicit internal planning rules
  - Validation:
    - doc-and-context sync plus targeted planning-autonomy cross-doc review
      recorded in this slice

- `PRJ-308` is complete.
  - Result:
    - scheduler/proactive follow-up now has one explicit target posture for
      app-local vs external cadence ownership after reflection rollout
    - later implementation slices can converge on one cadence owner model
      instead of reopening decision `12` every cycle
  - Validation:
    - doc-and-context sync plus targeted scheduler-boundary review recorded in
      this slice

- `PRJ-309` is complete.
  - Result:
    - planning, project state, and ops runbook are synchronized after
      post-reflection decision closure slices
    - release-readiness and runtime-governance docs stay aligned with the next
      hardening lane
  - Validation:
    - doc-and-context sync plus targeted cross-doc consistency review recorded
      in this slice

## Group 30 - Manual Runtime Reliability Fixes

Status update (2026-04-21): `PRJ-339..PRJ-342` are complete.

- `PRJ-339` enforces structured affective parse/schema fallback diagnostics and
  runtime fallback reason observability.
- `PRJ-340` expands goal/task signal detection to guarded natural inline
  command phrasing while preserving deterministic intent extraction.
- `PRJ-341` adds operator-facing Telegram mode smoke helpers for
  webhook/listen switching diagnostics and safe webhook restore posture.
- `PRJ-342` synchronizes planning, operations guidance, and context truth for
  this reliability lane.

## Group 31 - Relation-Aware Inferred Promotion Governance

This group applies the open relation/trust follow-up to inferred planning
promotion thresholds so inferred goal/task growth remains bounded by trust
posture without weakening explicit intent ownership.

Status update (2026-04-21): `PRJ-343..PRJ-346` are complete.

- `PRJ-343` Add delivery-reliability-aware inferred promotion thresholds in planning. (complete)
- `PRJ-344` Add planning diagnostics for inferred-promotion gate decisions. (complete)
- `PRJ-345` Add planning/runtime/API regressions for trust-aware inferred promotion gates and diagnostics. (complete)
- `PRJ-346` Sync docs/context for relation-aware inferred promotion governance. (complete)

## Group 32 - Behavior Validation CI-Ingestion Follow-up

This group converts behavior-validation outcomes from command-and-evidence-only
release posture into machine-ingestable CI artifacts without weakening the
current local/operator workflow.

Status update (2026-04-21): `PRJ-347..PRJ-350` are complete.

- `PRJ-347` Add machine-readable behavior-validation artifact output for CI consumers. (complete)
- `PRJ-348` Add release/ops script support for behavior-validation CI gate posture. (complete)
- `PRJ-349` Add regressions for behavior-validation artifact and gate semantics. (complete)
- `PRJ-350` Sync docs/context for behavior-validation CI-ingestion lane. (complete)

## Group 33 - Behavior Validation Artifact Governance

This group hardens artifact lifecycle and CI consumption posture so release
evidence can be validated consistently across operator and automation paths.

Status update (2026-04-21): `PRJ-351..PRJ-354` are complete.

- `PRJ-351` Add explicit artifact schema versioning and gate reason taxonomy. (complete)
- `PRJ-352` Add local artifact gate-evaluation mode for CI consumers without rerunning pytest. (complete)
- `PRJ-353` Add regressions for artifact schema-version and local gate-evaluation semantics. (complete)
- `PRJ-354` Sync docs/context for behavior-validation artifact-governance lane. (complete)

## Group 34 - Deployment Trigger SLO Instrumentation

This group turns deployment-trigger reliability from an anecdotal signal into
explicit machine-readable evidence tied to release operations.

Status update (2026-04-21): `PRJ-355..PRJ-358` are complete.

- `PRJ-355` Add deployment-trigger evidence capture script for Coolify webhook invocations. (complete)
- `PRJ-356` Add release-smoke support for optional deployment-trigger evidence verification. (complete)
- `PRJ-357` Add regressions for deployment-trigger evidence and release-smoke verification posture. (complete)
- `PRJ-358` Sync docs/context for deployment-trigger SLO instrumentation lane. (complete)

## Group 35 - Behavior Validation Artifact Compatibility Governance

This group turns artifact schema-version metadata into an explicit CI
compatibility policy without weakening local operator inspection workflows.

Status update (2026-04-21): `PRJ-359..PRJ-360` are complete.

- `PRJ-359` Enforce schema-major compatibility gate for behavior-validation artifact input in CI mode. (complete)
- `PRJ-360` Sync docs/context for behavior-validation schema-major compatibility posture. (complete)

## Group 36 - Attention Timing Baseline Governance

This group turns attention timing defaults into an explicit production
governance surface instead of leaving rollout posture implicit in config-only
values.

Status update (2026-04-21): `PRJ-361..PRJ-362` are complete.

- `PRJ-361` Expose attention timing baseline and alignment posture through `/health`. (complete)
- `PRJ-362` Sync docs/context for attention timing baseline governance. (complete)

## Next Derived Slice

Runtime behavior-validation queue is now complete through `PRJ-317`.
Next implementation queue is now seeded through `PRJ-378`.
Before the next implementation slice:

- derive the next smallest useful task from `.codex/context/TASK_BOARD.md`,
  `docs/planning/next-iteration-plan.md`, and `docs/planning/open-decisions.md`
- keep the implementation scope bounded to one reversible slice
- preserve target-state architecture bias when resolving local runtime choices

Post-reflection hardening queue:

- `PRJ-306..PRJ-309` are complete.
- Runtime behavior validation lane (`PRJ-310..PRJ-317`) is complete.

Runtime behavior validation queue:

- `PRJ-310` is complete: define the canonical runtime behavior testing contract and required
  system-debug surface.
- `PRJ-311` is complete: implement the internal system-debug validation surface for
  behavior checks.
- `PRJ-312` is complete: add structured behavior-harness output and scenario execution
  helpers.
- `PRJ-313` is complete: sync docs/context for runtime behavior testing architecture and
  internal validation contract.
- `PRJ-314` is complete: add memory behavior scenarios for write, retrieval, influence, and
  delayed recall.
- `PRJ-315` is complete: add multi-session continuity and personality-stability simulation
  scenarios.
- `PRJ-316` is complete: add contradiction, missing-data, and noisy-input behavior
  scenarios.
- `PRJ-317` is complete: make runtime behavior validation part of release-readiness and
  sync docs/context/runbook.

Next architecture-to-code queue:

- `PRJ-318..PRJ-321` Internal debug ingress migration
- `PRJ-322..PRJ-325` Scheduler externalization and attention ownership
- `PRJ-326..PRJ-329` Identity, language, and profile boundary hardening
- `PRJ-330..PRJ-333` Relation lifecycle and trust influence
- `PRJ-334..PRJ-337` Goal/task inference and typed-intent expansion
- `PRJ-339..PRJ-342` Manual runtime reliability fixes
- `PRJ-343..PRJ-346` Relation-aware inferred promotion governance
- `PRJ-347..PRJ-350` Behavior-validation CI-ingestion follow-up
- `PRJ-351..PRJ-354` Behavior-validation artifact governance
- `PRJ-355..PRJ-358` Deployment-trigger SLO instrumentation
- `PRJ-359..PRJ-360` Behavior-validation artifact compatibility governance
- `PRJ-361..PRJ-362` Attention timing baseline governance
- `PRJ-363..PRJ-366` Connector boundary execution policy
- `PRJ-367..PRJ-370` Typed-intent coverage for future writes
- `PRJ-371..PRJ-374` Action-delivery extensibility
- `PRJ-375..PRJ-378` Compatibility sunset readiness
- `PRJ-379..PRJ-382` Background adaptive-output convergence
- `PRJ-383..PRJ-386` Durable attention-inbox rollout baseline
- `PRJ-387..PRJ-390` Role-and-skill capability convergence
- `PRJ-391..PRJ-394` Retrieval-depth and theta-governance baseline

## Group 37 - Connector Boundary Execution Policy

This group closes the still-open internal-versus-external boundary by turning
connector permission posture into one shared execution policy instead of
scattered connector-family heuristics.

Status update (2026-04-21): `PRJ-363..PRJ-366` are complete.

- `PRJ-363` Define shared connector operation policy for internal planning versus external systems.
  - Result: (complete)
    - one policy owner defines which connector operations default to
      `read_only`, `suggestion_only`, or `mutate_with_confirmation`
    - architecture-aligned connector posture becomes executable without
      introducing provider-specific integrations first
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-364` Apply shared connector execution policy to planning permission gates and action guardrails. (complete)
  - Result:
    - planning and action share one connector execution baseline for calendar,
      task-system, and cloud-drive flows
    - internal planning state stays bounded until user-authorized external
      execution posture is explicit
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-365` Add regressions for connector execution posture and no-self-authorization rules. (complete)
  - Result:
    - connector execution boundaries are pinned across intent shaping,
      permission gates, and action outcomes
    - capability-expansion proposals remain suggestion-only and cannot
      self-authorize external access
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-366` Sync docs/context for connector execution policy baseline. (complete)
  - Result:
    - architecture, implementation reality, planning docs, and context truth
      now describe the same connector execution boundary
    - later provider-backed connector work can reuse one explicit policy owner
  - Validation:
    - doc-and-context sync plus targeted connector-boundary cross-doc review
      recorded in this slice

## Group 38 - Typed-Intent Coverage For Future Writes

This group extends the typed-intent rule from current goal/task/preference
mutations to the next class of durable writes so action ownership keeps
growing without slipping back into generic mutation paths.

Status update (2026-04-21): `PRJ-367..PRJ-370` are complete.

- `PRJ-367` Add dedicated typed intents for relation-maintenance and proactive-state writes. (complete)
  - Result:
    - relation lifecycle and proactive follow-up state are now represented as
      explicit future-write intents (`maintain_relation`,
      `update_proactive_state`) instead of generic side-effect payloads
    - typed intent ownership expands without weakening current planning/action
      boundaries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py`

- `PRJ-368` Route future durable writes through typed-intent-only action execution. (complete)
  - Result:
    - action now executes relation-maintenance and proactive follow-up state
      only from explicit typed intents
    - proactive planning paths stop depending on generic `noop` placeholders
      when durable proactive state should still be recorded
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_scheduler_worker.py tests/test_reflection_worker.py`

- `PRJ-369` Add regressions for typed future-write boundaries and no-raw-text durable mutation posture. (complete)
  - Result:
    - typed future-write boundaries are pinned in planning/action/runtime
      suites
    - durable mutation drift back to raw-text or generic fallbacks becomes
      test-visible
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_scheduler_worker.py tests/test_reflection_worker.py`

- `PRJ-370` Sync docs/context for expanded typed-intent ownership. (complete)
  - Result:
    - architecture, implementation reality, planning docs, and context truth
      now align on the expanded typed-intent boundary for proactive follow-up
      state and relation-maintenance writes
    - later autonomy work can add new write families without reopening action
      ownership drift
  - Validation:
    - doc-and-context sync plus targeted typed-intent boundary review recorded
      in this slice

## Group 39 - Action-Delivery Extensibility

This group resolves the remaining expression-versus-action follow-up by keeping
one shared handoff owner while making the contract extensible enough for
connector-heavy execution paths.

Status update (2026-04-21): `PRJ-371..PRJ-374` are complete.

- `PRJ-371` Extend the shared `ActionDelivery` contract with connector-safe execution envelopes. (complete)
  - Result:
    - one shared expression-to-action handoff now carries bounded
      connector-oriented execution metadata without splitting into
      connector-specific handoff owners
    - stage ordering stays architecture-aligned (`expression -> action`)
  - Validation:
    - Group 39 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
      (`138 passed`)

- `PRJ-372` Consume `ActionDelivery` execution envelopes in action and integration routing without expression leakage. (complete)
  - Result:
    - action now validates extension-envelope parity against planning while
      delivery routing consumes bounded envelope notes
    - connector-aware routing metadata no longer depends on ad-hoc payload
      coupling
  - Validation:
    - Group 39 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
      (`138 passed`)

- `PRJ-373` Add regressions for shared handoff stability and connector-extension compatibility. (complete)
  - Result:
    - backward-compatible handoff behavior is pinned for standard responses,
      graph-runtime parity, and extension-ready connector flows
    - stage-boundary drift between expression, action, and delivery routing
      becomes test-visible
  - Validation:
    - Group 39 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
      (`138 passed`)

- `PRJ-374` Sync docs/context for `ActionDelivery` extensibility baseline. (complete)
  - Result:
    - architecture, implementation reality, planning docs, and context truth
      align on one extensible shared handoff contract
    - future connector/provider work can enrich delivery semantics without
      re-opening the stage-ordering decision
  - Validation:
    - doc-and-context sync plus targeted expression/action boundary review
      recorded in this slice

## Group 40 - Compatibility Sunset Readiness

This group turns the remaining production-hardening follow-ups into explicit
readiness evidence so the repo can schedule actual compatibility removals from
observable runtime posture instead of only from planning notes.

Status update (2026-04-21): `PRJ-375..PRJ-378` are complete.

- `PRJ-375` Add compatibility-sunset readiness diagnostics for migration-only bootstrap and internal-only debug ingress. (complete)
  - Result:
    - runtime health now exposes machine-readable readiness posture for
      removing `create_tables` compatibility and retiring shared debug ingress
      from normal production use
    - release-window decisions now have explicit runtime evidence instead of
      living only in planning notes
  - Validation:
    - Group 40 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
      (`127 passed`)

- `PRJ-376` Extend release smoke and runtime-policy gates for compatibility-sunset readiness evidence. (complete)
  - Result:
    - release smoke now verifies migration-only bootstrap posture and
      dedicated-internal-ingress debug posture as explicit release evidence
    - compatibility-removal planning now has a repeatable operator workflow
      for checking evidence presence and coherence
  - Validation:
    - Group 40 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
      (`127 passed`)

- `PRJ-377` Add regressions for compatibility-sunset readiness and release-gate semantics. (complete)
  - Result:
    - readiness posture and release-gate semantics are pinned for
      `create_tables` removal and shared-debug-ingress retirement
    - remaining compatibility paths stay observable until explicit removal
  - Validation:
    - Group 40 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
      (`127 passed`)

- `PRJ-378` Sync docs/context for compatibility-sunset readiness governance. (complete)
  - Result:
    - architecture, operations guidance, planning docs, testing guidance, and
      context truth now align on how transitional compatibility paths become
      retirement-ready
    - the next queue can choose actual removal windows from runtime evidence
      instead of re-planning the baseline
  - Validation:
    - doc-and-context sync plus targeted compatibility-sunset cross-doc review
      recorded in this slice

## Group 41 - Background Adaptive-Output Convergence

This group turns the background runtime from a lightweight reflection worker
into a more explicit owner of adaptive outputs, so theta/relation/progress
changes follow one durable contract instead of scattered side effects.

Status update (2026-04-21): `PRJ-379..PRJ-382` are complete.

- `PRJ-379` Define a shared background adaptive-output contract for reflection results. (complete)
  - Result:
    - reflection outputs gain one explicit contract for conclusion updates,
      relation updates, theta updates, and progress signals
    - foreground/runtime consumers can depend on typed adaptive outputs instead
      of implicit repository-side behavior
  - Validation:
    - Group 41 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-380` Expose reflection adaptive-output summaries through runtime health and debug surfaces. (complete)
  - Result:
    - operators can see whether background runtime is producing adaptive state
      updates and what kinds of outputs are currently active
    - background-runtime evidence stops living only in logs and repository rows
  - Validation:
    - Group 41 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-381` Add regressions for adaptive-output ownership and no-foreground-theta-mutation posture. (complete)
  - Result:
    - theta/relation/progress updates are pinned as background-owned outputs
      with no drift back into foreground side effects
    - adaptive-output visibility stays stable across reflection, runtime, and
      health surfaces
  - Validation:
    - Group 41 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-382` Sync docs/context for background adaptive-output convergence. (complete)
  - Result:
    - architecture, runtime-reality, planning docs, and context truth align on
      the background runtime as the durable owner of adaptive outputs
    - later subconscious-loop work can extend adaptive state without reopening
      ownership boundaries
  - Validation:
    - doc-and-context sync plus targeted background-runtime cross-doc review

## Group 42 - Durable Attention-Inbox Rollout Baseline

This group starts the migration from in-memory attention coordination toward
the canonical durable inbox boundary without forcing an immediate production
default switch.

Status update (2026-04-21): `PRJ-383..PRJ-386` are complete.

- `PRJ-383` Define the durable attention-inbox persistence contract and repository boundary. (complete)
  - Result:
    - attention inbox items and pending-turn assembly gain an explicit durable
      owner contract instead of existing only as in-process coordinator state
    - future owner-mode rollout becomes implementable without redefining the
      turn-assembly model
  - Validation:
    - Group 42 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-384` Add runtime-owner adapter for `durable_inbox` mode with health-visible parity semantics. (complete)
  - Result:
    - runtime can route attention ownership through a durable-inbox adapter
      while preserving current `in_process` baseline behavior
    - `/health.attention` shows mode-consistent readiness and owner posture for
      both baselines
  - Validation:
    - Group 42 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-385` Add regressions for in-process versus durable attention-owner parity. (complete)
  - Result:
    - burst coalescing, claimed-turn protection, and answered/deferred state
      semantics stay aligned across owner modes
    - durable-inbox rollout drift becomes test-visible before production switch
  - Validation:
    - Group 42 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-386` Sync docs/context for durable attention-inbox rollout baseline. (complete)
  - Result:
    - canonical docs, implementation reality, planning docs, and context truth
      align on the staged path from in-process coordination to durable inbox
      ownership
    - production default can later change without reopening the contract model
  - Validation:
    - doc-and-context sync plus targeted attention-boundary cross-doc review

## Group 43 - Role-And-Skill Capability Convergence

This group closes the gap between the documented role/skill architecture and
the current role-only heuristic runtime by adding an explicit capability layer
without letting skills bypass action ownership.

Status update (2026-04-21): `PRJ-387..PRJ-390` are complete.

- `PRJ-387` Define a shared skill-registry contract and role-to-skill capability model. (complete)
  - Result:
    - roles stay behavioral stances while skills become explicit reusable
      capabilities with limitations
    - planning/expression/action can refer to one capability surface instead of
      ad-hoc implicit ability assumptions
  - Validation:
    - Group 43 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-388` Extend foreground outputs with bounded selected-skill metadata without tool leakage. (complete)
  - Result:
    - role selection and planning can expose which skills are relevant for the
      turn without turning skills into tools or direct actions
    - expression/action keep current side-effect boundaries while capability
      choice becomes explicit
  - Validation:
    - Group 43 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-389` Add regressions for role/skill separation and no-skill-side-effect posture. (complete)
  - Result:
    - the repo pins `role != skill != action` across runtime tests and contract
      surfaces
    - future capability growth can extend behavior without reintroducing layer
      confusion
  - Validation:
    - Group 43 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-390` Sync docs/context for role-and-skill capability convergence. (complete)
  - Result:
    - architecture, runtime-reality, planning docs, and context truth align on
      explicit capability semantics between role selection and action
    - the runtime moves closer to the documented role/skill layer instead of a
      role-only heuristic implementation
  - Validation:
    - doc-and-context sync plus targeted role/skill cross-doc review

## Group 44 - Retrieval-Depth And Theta-Governance Baseline

This group makes production retrieval depth and theta influence more explicit,
so adaptive behavior is observable and bounded instead of depending on
implementation-local heuristics.

Status update (2026-04-21): `PRJ-391..PRJ-394` are complete.

- `PRJ-391` Define a shared retrieval-depth policy snapshot for hybrid memory loading. (complete)
  - Result:
    - runtime exposes one explicit owner for retrieval depth, source limits, and
      hybrid bundle posture
    - production load-depth decisions stop living only inside orchestrator code
  - Validation:
    - Group 44 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-392` Expose theta-influence posture diagnostics across role, motivation, planning, and expression. (complete)
  - Result:
    - adaptive tie-break influence becomes machine-visible instead of implicit
      in stage heuristics
    - theta remains bounded to documented precedence and tie-break semantics
  - Validation:
    - Group 44 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-393` Add regressions for retrieval-depth governance and bounded theta influence. (complete)
  - Result:
    - retrieval-depth drift and over-broad theta influence become visible in
      regression coverage
    - production rollout of richer retrieval/adaptive logic stays constrained by
      explicit contracts
  - Validation:
    - Group 44 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- `PRJ-394` Sync docs/context for retrieval-depth and theta-governance baseline. (complete)
  - Result:
    - architecture, implementation reality, planning docs, and context truth
      align on production retrieval-depth posture and bounded theta influence
    - later multilingual/retrieval improvements can extend the runtime without
      reopening adaptive-governance ownership
  - Validation:
    - doc-and-context sync plus targeted adaptive-governance cross-doc review

## Group 45 - Role-Selection Evidence Baseline

This group moves role selection from a bare heuristic result toward an
evidence-driven policy owner, while keeping the role layer bounded and
side-effect-free.

Status update (2026-04-21): `PRJ-395..PRJ-398` are complete.

- `PRJ-395` Define a shared role-selection evidence contract and baseline policy owner. (complete)
  - Result:
    - role outputs now expose machine-readable selection reason/evidence fields
      instead of only a selected string plus confidence
    - richer role-selection work can extend one policy owner instead of
      growing ad-hoc heuristics in the agent directly
  - Validation:
    - Group 45 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`729 passed`)

- `PRJ-396` Apply a shared role-selection policy owner with evidence-driven diagnostics. (complete)
  - Result:
    - `app/core/role_selection_policy.py` now owns selection precedence and
      bounded diagnostics for affective, preference, relation, theta, and
      active-goal planning context
    - role debug surfaces now stay architecture-visible without turning role
      metadata into action authority
  - Validation:
    - Group 45 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`729 passed`)

- `PRJ-397` Add regressions for role-selection evidence precedence and bounded diagnostics. (complete)
  - Result:
    - regressions now pin preferred-role tie breaks, active-goal planning
      reinforcement, and system-debug visibility of role-selection evidence
    - richer role-selection work can extend from pinned precedence instead of
      implicit heuristics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`160 passed`)
    - `.\.venv\Scripts\python -m pytest -q`
      (`729 passed`)

- `PRJ-398` Sync docs/context for role-selection evidence baseline. (complete)
  - Result:
    - architecture, runtime-reality, planning docs, and context truth align on
      one shared role-selection policy owner with bounded evidence metadata
    - the next group can now treat affective rollout policy as a separate
      concern instead of mixing it into role-selection ownership
  - Validation:
    - doc-and-context sync plus targeted role-selection cross-doc review

## Group 46 - Affective Assessment Rollout Policy

This group makes AI-assisted affective classification rollout posture explicit
so runtime behavior can stay architecture-aligned whether the assessor is
enabled broadly or kept behind stricter rollout controls.

Status update (2026-04-21): `PRJ-399..PRJ-402` are complete.

- `PRJ-399` Define rollout policy ownership for AI-assisted affective assessment. (complete)
  - Result:
    - affective-assessment enablement/default posture gains one explicit
      policy owner instead of living only in implementation assumptions
    - non-production and production rollout choices become machine-visible
  - Validation:
    - Group 46 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`734 passed`)

- `PRJ-400` Expose affective-assessment rollout posture through runtime policy and debug surfaces. (complete)
  - Result:
    - `/health` and runtime debug surfaces expose whether AI-assisted affective
      classification is enabled, gated, or falling back deterministically
    - operator/debug visibility no longer depends on inference from logs
  - Validation:
    - Group 46 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`734 passed`)

- `PRJ-401` Add regressions for affective rollout defaults and deterministic fallback gating. (complete)
  - Result:
    - rollout defaults, fallback posture, and debug visibility become
      regression-pinned for both enabled and disabled classifier modes
    - affective rollout changes stay test-visible before broader deployment
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_config.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`199 passed`)
    - `.\.venv\Scripts\python -m pytest -q`
      (`734 passed`)

- `PRJ-402` Sync docs/context for affective-assessment rollout policy. (complete)
  - Result:
    - architecture, runtime-reality, planning docs, and context truth align on
      affective rollout ownership and fallback posture
    - later empathy/affective improvements can extend one rollout policy owner
  - Validation:
    - doc-and-context sync plus targeted affective-policy cross-doc review

## Group 47 - Reflection Scope Governance

This group resolves the remaining question of which reflection outputs should
stay global and which need scoped ownership as goal/task complexity grows.

- `PRJ-403` Define explicit scope policy for reflection outputs with multi-goal risk. (complete)
  - Result:
    - reflection outputs gain one explicit scope policy instead of relying on
      mixed historical conventions
    - future reflection additions can choose global versus goal/task scope from
      one documented rule set
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`

- `PRJ-404` Apply scope policy to remaining reflection outputs and runtime readers. (complete)
  - Result:
    - runtime readers and reflection writers align on which outputs must stay
      scoped to goal/task context versus user-global posture
    - multi-goal leakage risk decreases without broad architectural churn
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`

- `PRJ-405` Add regressions for no-cross-goal leakage in scoped reflection outputs. (complete)
  - Result:
    - scoped reflection leakage becomes test-visible across reflection,
      repository, and runtime integration paths
    - future scoped-output additions inherit pinned non-leakage behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`

- `PRJ-406` Sync docs/context for reflection scope governance. (complete)
  - Result:
    - architecture, runtime-reality, planning docs, and context truth align on
      reflection scope ownership and multi-goal guardrails
    - later adaptive/reflection work can extend scopes without reopening the
      baseline governance question
  - Validation:
    - doc-and-context sync plus targeted reflection-scope cross-doc review
    - Group 47 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
      (`172 passed`)

## Group 48 - Durable Attention Contract-Store Rollout

This group starts the move from parity-only durable attention posture to a real
repository-backed contract store while preserving current owner-mode rollout
guardrails.

- `PRJ-407` Define the durable attention contract-store shape and persistence responsibilities. (complete)
  - Result:
    - attention inbox persistence and cleanup responsibilities gain one
      explicit repository-backed contract shape
    - future durable owner rollout can proceed without redefining turn
      semantics again
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_graph_state_contract.py`

- `PRJ-408` Add repository-backed durable attention store primitives behind owner-mode rollout. (complete)
  - Result:
    - runtime gains the first real durable attention primitives behind the
      existing owner-mode boundary
    - in-process parity baseline remains available while storage-backed rollout
      starts becoming real
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- `PRJ-409` Add regressions for durable attention contract-store parity and cleanup behavior. (complete)
  - Result:
    - contract-store parity and stale/answered cleanup behavior become
      regression-pinned before any production default switch
    - durable attention rollout stays bounded and observable
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- `PRJ-410` Sync docs/context for durable attention contract-store rollout. (complete)
  - Result:
    - architecture, runtime-reality, planning docs, and context truth align on
      durable attention contract-store rollout posture
    - later production default changes can build on an explicit store owner
      instead of parity-only scaffolding
  - Validation:
    - doc-and-context sync plus targeted durable-attention cross-doc review
    - Group 48 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_graph_state_contract.py`
      (`122 passed`)
      `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py`
      (`79 passed`)

## Group 49 - Identity And Language Ownership Baseline

This group makes the identity/profile boundary explicit through one shared
policy owner, then follows it with more visible language-continuity posture
before any broader multilingual or profile-surface expansion.

Status update (2026-04-21): `PRJ-411..PRJ-414` are complete.

- `PRJ-411` Define a shared identity/profile ownership policy and baseline visibility. (complete)
  - Result:
    - runtime now has one shared owner for profile-versus-conclusion identity
      preferences in `app/core/identity_policy.py`
    - `/health.identity` and `system_debug.adaptive_state.identity_policy` now
      expose that baseline so the split is machine-visible instead of living
      only in scattered implementation details
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`149 passed`)

- `PRJ-412` Expose language-continuity posture diagnostics through health and runtime debug.
  - Result: (complete)
    - `/health.identity.language_continuity` now exposes precedence baseline,
      supported codes, and continuity source families for operators
    - runtime `system_debug.adaptive_state.language_continuity` now exposes
      selected source, candidate continuity inputs, and fallback posture for
      the current event
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`149 passed`)

- `PRJ-413` Add regressions for language-continuity posture and supported-language boundaries.
  - Result: (complete)
    - explicit-request posture, profile-only continuity posture, and
      unsupported-profile fallback are now regression-pinned across language
      utility, runtime, and API-visible diagnostics
    - the current MVP language boundary stays explicit at `en|pl` instead of
      silently accepting unsupported profile continuity inputs
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`165 passed`)

- `PRJ-414` Sync docs/context for identity and language ownership baseline.
  - Result: (complete)
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on the shared identity-policy owner plus
      language-continuity diagnostics baseline
    - Group 49 closes in a clean state, so later identity-profile changes can
      extend one explicit owner instead of reopening the split ad hoc
  - Validation:
    - doc-and-context sync plus targeted identity/language cross-doc review

## Detailed Functional Analysis And Remaining Work (2026-04-22)

### 1. Runtime Topology And Ownership

- Current state:
  - reflection has durable queue ownership and machine-visible readiness, but
    production still defaults to `REFLECTION_RUNTIME_MODE=in_process`
  - attention now has a real durable contract store, but the long-term owner
    decision between in-process coordination and durable-owner posture is not
    formally closed
  - graph-stage execution is explicit, but pre/post graph ownership versus
    future graph-node expansion is still an open architecture question
- Target state:
  - background reflection, durable attention, and graph ownership are explicit
    enough that production defaults can move without semantic drift or hidden
    framework coupling
- Gap:
  - the repo has the mechanics, but not the final switch criteria, release
    policy, or long-term ownership baseline
- Planned queue:
  - `PRJ-415..PRJ-418`

### 2. Production Boundary Hardening

- Current state:
  - startup is migration-first, but `create_tables()` compatibility still
    exists behind rollout guardrails
  - shared `/event?debug=true` posture is guarded and visible, but production
    has not yet enforced dedicated internal-ingress-only debug access as the
    default baseline
- Target state:
  - production runtime starts only through migration-owned schema control, and
    internal debug stays on a dedicated protected ingress with break-glass
    posture instead of a convenience default
- Gap:
  - release-window removal and enforcement timing are still planning-only
    decisions
- Planned queue:
  - `PRJ-419..PRJ-422`

### 3. Retrieval, Semantic Recall, And Affective Memory

- Current state:
  - retrieval is still heuristic-first with deeper load depth, policy
    visibility, and deterministic embedding/provider placeholders
  - affective memory exists as tags and conclusions, but the long-term split
    between transient turn-state and durable affective memory is not fully
    settled
- Target state:
  - retrieval should be a production-ready hybrid lexical-plus-vector system
    with explicit provider ownership, explicit default depth, and a stable
    affective-memory model
- Gap:
  - the current repo has contracts and deterministic baselines, but not the
    production retrieval owner or the final affective-memory boundaries
- Planned queue:
  - `PRJ-423..PRJ-426`

### 4. Adaptive Identity, Role, Language, And Preference Governance

- Current state:
  - identity/profile ownership, language continuity, role-selection evidence,
    affective rollout posture, and theta governance are all explicit and
    bounded
  - learned preferences and adaptive signals remain deliberately narrow
    tie-break inputs
- Target state:
  - the app should have a clearly documented long-horizon governance policy for
    how far role history, affective signals, language continuity, profile
    identity, preferences, and theta are allowed to shape later behavior
- Gap:
  - the baseline is safe and inspectable, but the future authority model is
    still unresolved
- Planned queue:
  - `PRJ-427..PRJ-430`

### 5. Goal/Task Growth And Proposal Governance

- Current state:
  - the runtime already supports explicit goal/task creation, scoped goal
    reflection state, inferred typed maintenance intents, and proposal
    promotion through the conscious boundary
- Target state:
  - the app should define exactly when inference is allowed to create or widen
    internal planning state and whether subconscious proposal handling needs a
    richer conscious decision set
- Gap:
  - the repo has bounded mechanics, but not the final policy for inferred
    planning growth or proposal-decision extensibility
- Planned queue:
  - `PRJ-431..PRJ-434`

### 6. Scheduler Ownership And Connector Capability Convergence

- Current state:
  - scheduler cadence, proactive dispatch, attention timing, and connector
    execution policy are explicit and test-visible
  - connector families already have a shared baseline policy owner
- Target state:
  - external scheduling, durable attention ownership, and connector capability
    expansion should converge on one explicit conscious-execution boundary with
    clear opt-in, authorization, and proposal rules
- Gap:
  - the repo still needs a final authority split between in-app coordination,
    external schedulers, and user-authorized connector execution
- Planned queue:
  - `PRJ-435..PRJ-438`

### 7. Deployment Standard And Release Reliability

- Current state:
  - Coolify remains the documented hosting baseline, deployment-trigger
    evidence exists, and release smoke now verifies deployment evidence
- Target state:
  - deployment ownership, trigger SLOs, rollback expectations, and release
    evidence should describe the intended long-term operating model instead of
    a transitional fallback-heavy posture
- Gap:
  - webhook reliability thresholds and any post-Coolify hosting standard are
    still unresolved
- Planned queue:
  - `PRJ-439..PRJ-442`

## Group 50 - Runtime Topology Finalization

This group closes the remaining topology questions around foreground graph
ownership, background reflection execution, and durable attention ownership
before any production-default switches.

- `PRJ-415` Define the production switch criteria for deferred reflection and durable attention ownership.
  - Result:
    - one explicit switch contract records when production may move from
      `REFLECTION_RUNTIME_MODE=in_process` to `deferred` and from
      `ATTENTION_COORDINATION_MODE=in_process` to `durable_inbox`
    - reflection readiness, attention contract-store readiness, and rollback
      criteria are described in one place instead of spread across docs
  - Validation:
    - targeted cross-doc review covering `open-decisions`, runtime ops, and
      architecture/runtime-reality ownership notes

- `PRJ-416` Add machine-visible readiness evidence for the selected topology owner path.
  - Result:
    - `/health` and release-smoke evidence expose the final readiness checklist
      for reflection-mode and attention-owner switches
    - operator-visible blockers become machine-readable before any default
      change is scheduled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`

- `PRJ-417` Decide the long-term graph ownership boundary and proposal decision-set baseline.
  - Result:
    - the repo records whether current pre/post graph ownership remains the
      long-term baseline or whether selected non-stage segments should migrate
      into graph-owned nodes later
    - the conscious proposal-decision set is either explicitly frozen or a
      bounded extension path is documented
  - Validation:
    - architecture and planning cross-review plus targeted graph-contract test
      impact note

- `PRJ-418` Sync docs/context for runtime topology finalization.
  - Result:
    - task board, project state, open decisions, canonical architecture docs,
      runtime-reality notes, and ops guidance all align on the final topology
      stance
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`,
      `docs/operations/`, and `.codex/context/`

## Group 51 - Production Boundary Hardening

This group turns transitional production guardrails into an explicit path
toward migration-only startup and dedicated internal debug ingress.

- `PRJ-419` Schedule the actual `create_tables()` removal window and strict startup baseline.
  - Result:
    - a concrete release window and prerequisite checklist exists for removing
      compatibility-mode schema creation
    - startup policy docs, ops notes, and `/health.runtime_policy` all point to
      the same migration-only target baseline
  - Validation:
    - targeted runtime-policy and ops doc cross-review

- `PRJ-420` Enforce dedicated internal-ingress-only debug posture with break-glass override.
  - Result:
    - production debug access defaults to dedicated internal ingress only, with
      a narrow break-glass override path instead of shared-endpoint default
      exposure
    - release and rollback paths explicitly cover the selected debug posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py`

- `PRJ-421` Add release evidence for migration-only startup and debug-ingress enforcement.
  - Result:
    - release smoke and startup evidence prove the chosen production boundary
      instead of relying on manual interpretation
    - the repo gains one release-readiness story for schema ownership and debug
      ingress retirement
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`

- `PRJ-422` Sync docs/context for production boundary hardening.
  - Result:
    - planning docs, runtime ops, testing guidance, and context truth all align
      on migration-only startup plus dedicated debug-ingress enforcement
  - Validation:
    - doc-and-context sync across `docs/planning/`,
      `docs/operations/`, `docs/engineering/`, and `.codex/context/`

## Group 52 - Retrieval And Affective-Memory Productionization

This group upgrades retrieval from deterministic heuristic baseline toward the
production semantic-recall model described by the architecture.

- `PRJ-423` Define the production retrieval architecture and default depth policy.
  - Result:
    - one shared plan records the target hybrid lexical-plus-vector retrieval
      path, provider owner, fallback posture, and production default depth
    - retrieval and embedding strategy decisions stop being spread across
      multiple open-decision sections
  - Validation:
    - architecture/planning cross-review across decisions `5`, `5d`, and `5e`

- `PRJ-424` Implement provider-backed retrieval and embedding rollout behind explicit owner-mode policy.
  - Result:
    - retrieval and embedding providers move from deterministic placeholder
      contracts to a real rollout path with explicit owner-mode and fallback
      semantics
    - the repo can test production-like semantic recall without redefining the
      retrieval contract again
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-425` Separate durable affective-memory patterns from transient turn-state and pin their influence.
  - Result:
    - durable affective signals and transient turn affect are explicitly split
      so later retrieval/ranking work does not overfit recent emotion noise
    - context, motivation, and reflection influence from affective memory is
      regression-pinned under the new boundary
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_motivation_engine.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- `PRJ-426` Sync docs/context for retrieval and affective-memory productionization.
  - Result:
    - docs, planning truth, testing guidance, and context notes all describe
      the same retrieval owner, default depth, embedding posture, and
      affective-memory split
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`,
      `docs/engineering/`, and `.codex/context/`

## Group 53 - Adaptive Identity And Role-Governance Evolution

This group decides how far adaptive state is allowed to shape future behavior
without drifting into implicit identity ownership.

- `PRJ-427` Define the long-horizon role-selection and affective-rollout boundary.
  - Result:
    - the repo records whether role selection should remain a lightweight
      foreground policy or grow toward longer-horizon state/history reasoning
    - affective-assessment default posture is intentionally fixed for future
      environments instead of staying an open rollout assumption
  - Validation:
    - architecture/planning cross-review plus targeted role and affective test
      scope note

- `PRJ-428` Decide the future authority of learned preferences and theta signals.
  - Result:
    - one explicit governance statement defines whether preference signals and
      theta remain tie-break-only or gain any broader influence on proactive,
      attention, or identity behavior
    - expansion, if any, is bounded by stage ownership and evidence thresholds
  - Validation:
    - policy cross-review across `16_agent_contracts.md` and
      `open-decisions.md`

- `PRJ-429` Define the future profile and multilingual identity boundary.
  - Result:
    - the repo records whether conclusion-owned preferences should stay
      separate from profile identity long-term and when language continuity may
      evolve beyond the current `en|pl` heuristic-plus-profile baseline
    - future identity growth gets one explicit compatibility path instead of ad
      hoc profile widening
  - Validation:
    - identity/language cross-review across architecture, planning, and ops
      notes

- `PRJ-430` Sync docs/context for adaptive identity and role governance.
  - Result:
    - task board, project state, open decisions, and canonical docs all align
      on the bounded future authority of role history, affective posture,
      preferences, theta, and multilingual continuity
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/planning/`, `docs/implementation/`, and `.codex/context/`

## Group 54 - Goal/Task And Proposal Governance

This group decides how internal planning state is allowed to grow and how
subconscious proposals should evolve without bypassing the conscious boundary.

- `PRJ-431` Define the inference boundary for future goal and task creation.
  - Result:
    - one explicit policy records whether internal goals/tasks remain limited to
      explicit user declarations or may be inferred from repeated execution and
      plan patterns
    - inferred creation, if allowed, gains bounded triggers and rollback-safe
      guardrails
  - Validation:
    - planning/memory cross-review plus targeted goal/task test impact note

- `PRJ-432` Decide the long-term conscious decision set for subconscious proposals.
  - Result:
    - proposal handling either keeps the current `accept|merge|defer|discard`
      baseline or gains a bounded extension path with explicit status mapping
    - proposal-family growth stays inside conscious planning ownership
  - Validation:
    - planning/architecture cross-review for proposal lifecycle contracts

- `PRJ-433` Add machine-visible governance diagnostics for inferred planning growth and proposal handling.
  - Result:
    - runtime debug and/or health surfaces expose the chosen inferred-planning
      and proposal-governance posture so later rollout is observable
    - future inference expansion no longer depends on reading scattered code
      paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- `PRJ-434` Sync docs/context for goal/task and proposal governance.
  - Result:
    - canonical docs, planning truth, and context notes all align on internal
      planning growth limits plus proposal-decision baseline
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/planning/`, `docs/implementation/`, and `.codex/context/`

## Group 55 - Scheduler And Connector Capability Convergence

This group completes the conscious execution boundary across cadence ownership,
durable attention, and external productivity connectors.

- `PRJ-435` Define the final scheduler-versus-attention ownership split.
  - Result:
    - one explicit policy records where app-local scheduler ownership ends, how
      external cadence ownership interacts with durable attention, and which
      path becomes the intended production baseline
    - proactive and maintenance scheduling can move forward without reopening
      attention semantics
  - Validation:
    - scheduler/attention cross-review across architecture, runtime-reality,
      and ops docs

- `PRJ-436` Define the connector authorization matrix for read, suggestion, and direct execution.
  - Result:
    - connector families gain an explicit operation matrix that distinguishes
      read-only, suggestion-only, and safe direct-execution paths after user
      opt-in
    - future connector growth stays policy-owned instead of depending on local
      planner/action heuristics
  - Validation:
    - planning/action/connector policy cross-review and targeted permission
      regression note

- `PRJ-437` Define the capability-proposal workflow for new connectors without self-authorization.
  - Result:
    - the system gets one explicit proposal path for suggesting new connector
      capability or expansion without silently authorizing itself
    - runtime/debug visibility records when capability growth is merely
      suggested versus actually authorized
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- `PRJ-438` Sync docs/context for scheduler and connector capability convergence.
  - Result:
    - canonical docs, planning docs, ops guidance, and context truth all align
      on scheduler ownership, durable attention interaction, and connector
      authorization posture
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/planning/`, `docs/operations/`, and `.codex/context/`

## Group 56 - Deployment Standard And Release-Reliability Closure

This group converts the remaining deployment and release questions into one
explicit long-term operating model.

- `PRJ-439` Choose the post-Coolify hosting baseline and responsibility split.
  - Result:
    - the repo records whether Coolify remains the medium-term standard or a
      new hosting baseline should replace it, together with ownership for
      secrets, deploy orchestration, rollback, and operator visibility
    - future runtime work stops assuming an unspecified hosting transition
  - Validation:
    - ops/planning cross-review with updated deployment decision record

- `PRJ-440` Define the deployment-trigger SLO and manual-fallback retirement criteria.
  - Result:
    - one objective webhook delivery and deployment evidence target defines
      when manual redeploy becomes exception-only instead of routine fallback
    - release policy and smoke checks align with that SLO
  - Validation:
    - runbook and behavior-validation/release-smoke cross-review

- `PRJ-441` Align release evidence, smoke workflow, and rollback notes to the chosen deployment standard.
  - Result:
    - release readiness, smoke execution, and rollback documentation all point
      at the same long-term deployment baseline
    - deployment reliability is proved through repeatable evidence rather than
      ad hoc operator memory
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py`

- `PRJ-442` Sync docs/context for deployment standard and release reliability closure.
  - Result:
    - context truth, planning docs, runtime ops, and architecture notes all
      align on the chosen hosting baseline plus deployment-trigger SLO posture
  - Validation:
    - doc-and-context sync across `docs/planning/`,
      `docs/operations/`, `docs/implementation/`, and `.codex/context/`

## Parallel-Ready Lanes

The next three groups intentionally stay sequential because they define shared
runtime boundaries that later work depends on:

- `PRJ-276..PRJ-279`
- `PRJ-280..PRJ-283`
- `PRJ-284..PRJ-287`

After those groups are stable, the next two lanes can be worked with minimal
overlap:

- `PRJ-288..PRJ-291`
  - ownership: adaptive governance across role, motivation, planning, and
    reflection consumers
- `PRJ-292..PRJ-295`
  - ownership: attention inbox, proposal handoff, proactive gating, and
    connector execution boundary

`PRJ-296..PRJ-299` should start only after both lanes stabilize, because that
group locks the production and release baseline for the converged runtime.

## Recommended Execution Order

1. `PRJ-276..PRJ-279` Foreground runtime convergence
2. `PRJ-280..PRJ-283` Background reflection topology
3. `PRJ-284..PRJ-287` Production memory retrieval rollout
4. `PRJ-288..PRJ-291` Adaptive cognition governance
5. `PRJ-292..PRJ-295` Attention and proposal execution boundary
6. `PRJ-296..PRJ-299` Operational hardening and release truth
7. `PRJ-301..PRJ-304` Reflection deployment baseline and readiness rollout
8. `PRJ-306..PRJ-309` Post-reflection hardening decisions
9. `PRJ-310..PRJ-313` Runtime behavior testing architecture
10. `PRJ-314..PRJ-317` Memory, continuity, and failure validation
11. `PRJ-318..PRJ-321` Internal debug ingress migration
12. `PRJ-322..PRJ-325` Scheduler externalization and attention ownership
13. `PRJ-326..PRJ-329` Identity, language, and profile boundary hardening
14. `PRJ-330..PRJ-333` Relation lifecycle and trust influence
15. `PRJ-334..PRJ-337` Goal/task inference and typed-intent expansion
16. `PRJ-339..PRJ-342` Manual runtime reliability fixes
17. `PRJ-343..PRJ-346` Relation-aware inferred promotion governance
18. `PRJ-347..PRJ-350` Behavior-validation CI-ingestion follow-up
19. `PRJ-351..PRJ-354` Behavior-validation artifact governance
20. `PRJ-355..PRJ-358` Deployment-trigger SLO instrumentation
21. `PRJ-359..PRJ-360` Behavior-validation artifact compatibility governance
22. `PRJ-361..PRJ-362` Attention timing baseline governance
23. `PRJ-363..PRJ-366` Connector boundary execution policy
24. `PRJ-367..PRJ-370` Typed-intent coverage for future writes
25. `PRJ-371..PRJ-374` Action-delivery extensibility
26. `PRJ-375..PRJ-378` Compatibility sunset readiness
27. `PRJ-379..PRJ-382` Background adaptive-output convergence
28. `PRJ-383..PRJ-386` Durable attention-inbox rollout baseline
29. `PRJ-387..PRJ-390` Role-and-skill capability convergence
30. `PRJ-391..PRJ-394` Retrieval-depth and theta-governance baseline
31. `PRJ-395..PRJ-398` Role-selection evidence baseline
32. `PRJ-399..PRJ-402` Affective-assessment rollout policy
33. `PRJ-403..PRJ-406` Reflection scope governance
34. `PRJ-407..PRJ-410` Durable attention contract-store rollout
35. `PRJ-411..PRJ-414` Identity and language ownership baseline
36. `PRJ-415..PRJ-418` Runtime topology finalization
37. `PRJ-419..PRJ-422` Production boundary hardening
38. `PRJ-423..PRJ-426` Retrieval and affective-memory productionization
39. `PRJ-427..PRJ-430` Adaptive identity and role-governance evolution
40. `PRJ-431..PRJ-434` Goal/task and proposal governance
41. `PRJ-435..PRJ-438` Scheduler and connector capability convergence
42. `PRJ-439..PRJ-442` Deployment standard and release-reliability closure

The queue should still be treated as intentionally open after those items.
Additional small architecture-alignment slices may still be discovered while
executing Groups 17 through 56.

## Handoff Rules For Execution Agents

When taking the next task:

1. Touch only the files listed for that task unless a local refactor becomes necessary.
2. If scope expands, update `.codex/context/TASK_BOARD.md` before closing the task.
3. Do not mix Group 1 contract work with Group 3 refactors in the same change.
4. Keep behavior-neutral extraction separate from behavior-changing contract fixes.
5. Leave behind the exact validation command and pass result for the touched scope.

## Definition Of Done For This Phase

This phase is complete when:

- foreground runtime ownership is explicit across graph execution, baseline
  load, action handoff, episodic memory write, and reflection trigger
- background reflection topology is explicit, operator-visible, and ready for
  either in-process or external execution without semantic drift
- semantic retrieval has a production baseline with explicit provider,
  refresh-owner, and family-rollout semantics
- adaptive signals influence behavior only through documented, evidence-based
  policy surfaces
- attention, proposal handoff, proactive outreach, and connector permission
  gates share one conscious execution boundary
- production startup, debug posture, and release workflow describe the intended
  target-state baseline rather than temporary convenience defaults
- system-debug visibility and user-simulation scenarios are sufficient to prove
  whether memory, continuity, and decision-making work across time
- memory is considered correct only when stored state influences later context
  and response behavior
- internal debug, scheduler ownership, identity continuity, relation lifecycle,
  and internal planning growth are all reflected in code rather than only in
  planning decisions
- docs, code, and `.codex/context/` describe the same runtime truth
- `PRJ-492` is complete: the repo now records one explicit debug-ingress owner
  with the dedicated internal admin route as the target posture, shared routes
  as temporary compatibility-only surfaces, and a fixed retirement checklist
  for later runtime and release evidence.
- `PRJ-493..PRJ-494` are complete: runtime policy, startup logs, release smoke,
  and the ops runbook now expose the same dedicated-admin debug posture with
  machine-visible shared-retirement blockers.
- `PRJ-496` is complete: the repo now records one explicit production cadence
  owner baseline with `externalized` scheduler execution as the target posture
  for maintenance and proactive ticks.
