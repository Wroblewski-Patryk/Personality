# TASK_BOARD

Last updated: 2026-04-21

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
- The convergence queue is complete through `PRJ-299`; reflection lane is now
  complete through `PRJ-304`, and post-reflection hardening plus runtime
  behavior-validation queue is complete through `PRJ-317`.
- Runtime behavior-validation lane is now complete through `PRJ-317`
  (`PRJ-310..PRJ-317`).
- Next architecture-to-code queue is now seeded through `PRJ-342`.
- Subsequent slices should follow the grouped execution order for foreground
  runtime convergence, background topology, production retrieval rollout,
  adaptive governance, dual-loop execution boundaries, and operational
  hardening.
- Memory, continuity, and failure handling are now validated as
  living-system behavior rather than only contract correctness.
- Next queue turns remaining architecture decisions into implementation lanes
  for internal debug ingress, scheduler ownership, identity continuity,
  relation lifecycle, and internal planning growth.
- Additional architecture-alignment work should be appended after that queue so
  the backlog stays explicitly open for later discovery instead of pretending
  the plan is complete.

## READY

- [ ] PRJ-332 Add relation lifecycle and trust-influence regressions
  - Status: READY
  - Group: Relation Lifecycle And Trust Influence
  - Owner: QA/Test
  - Depends on: PRJ-331
  - Priority: P1
  - Result:
    - decay, refresh, and trust-driven behavior expectations are pinned end to
      end
    - relation drift becomes test-visible before it affects production behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_expression_agent.py`

## BACKLOG

- [ ] (none)

## FUTURE

- [ ] PRJ-333 Sync docs/context for relation lifecycle and trust influence
  - Status: FUTURE
  - Group: Relation Lifecycle And Trust Influence
  - Owner: Product Docs
  - Depends on: PRJ-332
  - Priority: P1
  - Result:
    - docs, planning, and project state align on how relations evolve and where
      they influence behavior
    - future relational capability work starts from one explicit baseline
  - Validation:
    - doc-and-context sync plus targeted relation-lifecycle cross-doc review
      recorded in this slice

- [ ] PRJ-334 Add inferred goal/task promotion rules to planning
  - Status: FUTURE
  - Group: Goal/Task Inference And Typed-Intent Expansion
  - Owner: Backend Builder
  - Depends on: PRJ-333
  - Priority: P1
  - Result:
    - planning can propose bounded inferred goals/tasks from repeated evidence
      instead of relying only on explicit user declarations
    - internal planning growth becomes a deliberate coded behavior rather than a
      future aspiration
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`

- [ ] PRJ-335 Expand typed domain intents for inferred planning state and controlled maintenance writes
  - Status: FUTURE
  - Group: Goal/Task Inference And Typed-Intent Expansion
  - Owner: Backend Builder
  - Depends on: PRJ-334
  - Priority: P1
  - Result:
    - inferred goal/task promotion and related maintenance writes stay blocked
      behind explicit typed intents
    - action remains the sole owner of durable planning-state side effects
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [ ] PRJ-336 Add regressions for inferred planning growth and no-duplicate/no-unsafe promotion behavior
  - Status: FUTURE
  - Group: Goal/Task Inference And Typed-Intent Expansion
  - Owner: QA/Test
  - Depends on: PRJ-335
  - Priority: P1
  - Result:
    - inferred planning growth is pinned against duplicate, unsafe, or weakly
      evidenced promotions
    - architecture drift on internal planning autonomy fails fast
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py`

- [ ] PRJ-337 Sync docs/context for goal/task inference and typed-intent expansion
  - Status: FUTURE
  - Group: Goal/Task Inference And Typed-Intent Expansion
  - Owner: Product Docs
  - Depends on: PRJ-336
  - Priority: P1
  - Result:
    - docs, planning, and project state align on how internal planning can grow
      while staying subordinate to typed intent ownership
    - later autonomy work can build on explicit internal planning rules
  - Validation:
    - doc-and-context sync plus targeted planning-autonomy cross-doc review
      recorded in this slice

- [ ] PRJ-339 Enforce structured affective-classifier output parsing and fallback diagnostics
  - Status: FUTURE
  - Group: Manual Runtime Reliability Fixes
  - Owner: Backend Builder
  - Depends on: PRJ-338
  - Priority: P1
  - Result:
    - affective classifier prompt/client path requires deterministic structured
      JSON output contract (or equivalent schema gate), reducing
      `openai_affective_parse_failed` fallback churn
    - fallback posture remains explicit with traceable error reasons and no
      silent behavior drift in affect-sensitive turns
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_perception_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
    - targeted manual emotional-turn debug validation through
      `POST /internal/event/debug` with `system_debug.perception.affective`
      evidence notes

- [ ] PRJ-340 Expand goal/task signal detection beyond prefix-only phrasing
  - Status: FUTURE
  - Group: Manual Runtime Reliability Fixes
  - Owner: Backend Builder
  - Depends on: PRJ-339
  - Priority: P1
  - Result:
    - planning intent detection handles natural inline phrasing
      (for example `utworz cel ...`, `dodaj zadanie ...`) in addition to strict
      prefix forms (`cel:`, `zadanie:`)
    - domain-intent extraction remains deterministic and keeps false-positive
      guardrails across Polish and English patterns
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
    - targeted manual debug checks confirm `upsert_goal|upsert_task` intent
      extraction for both strict-prefix and natural-phrase variants

- [ ] PRJ-341 Add Telegram integration smoke workflow for webhook/listen mode switching
  - Status: FUTURE
  - Group: Manual Runtime Reliability Fixes
  - Owner: QA/Test
  - Depends on: PRJ-340
  - Priority: P1
  - Result:
    - operator-facing smoke workflow now validates both Telegram modes:
      webhook-driven ingress and temporary `deleteWebhook -> getUpdates`
      listen diagnostics
    - end-to-end evidence checklist includes real chat delivery preconditions
      (`chat_id` availability, bot-start handshake) to reduce false-negative
      Telegram delivery triage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_event_normalization.py tests/test_delivery_router.py`
    - runbook-aligned manual smoke evidence recorded for
      `getWebhookInfo/getUpdates/setWebhook`

- [ ] PRJ-342 Sync docs/context for manual runtime reliability fix lane
  - Status: FUTURE
  - Group: Manual Runtime Reliability Fixes
  - Owner: Product Docs
  - Depends on: PRJ-341
  - Priority: P1
  - Result:
    - planning docs, runbook guidance, and context truth reflect the new
      manual-runtime fix lane and updated Telegram reliability baseline
    - queue and project-state continuity stay explicit after manual validation
      findings
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`, and
      `docs/operations/` with targeted cross-reference checks

## IN_PROGRESS

- [ ] (none)

## BLOCKED

- [ ] (none)

## REVIEW

- [ ] (none)

## DONE

- [x] PRJ-338 Harden Telegram delivery failure boundary to prevent 500 runtime crashes
  - Status: DONE
  - Group: Manual Runtime Reliability Fixes
  - Owner: Backend Builder
  - Depends on: PRJ-331
  - Priority: P0
  - Result:
    - Telegram delivery failures (`4xx/5xx`, transport errors, timeout) are
      now degraded at the integration boundary to controlled
      `ActionResult(status=fail)` responses, preventing uncaught action-stage
      exceptions from bubbling into runtime endpoint 500s.
    - runtime persistence and reflection follow-up remain deterministic on
      failed Telegram sends (`action=fail` persisted, reflection enqueue still
      evaluated) instead of short-circuiting on delivery exceptions.
    - debug-ingress API behavior now explicitly covers fail-action delivery
      posture so `/internal/event/debug` returns a structured fail response
      instead of crashing.
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`160 passed`)
    - Negative debug-ingress boundary coverage is pinned in
      `tests/test_api_routes.py::test_internal_event_debug_endpoint_returns_fail_action_result_without_500`
      and `tests/test_runtime_pipeline.py::test_runtime_pipeline_degrades_telegram_delivery_exception_to_fail_action_result`.
    - App-lifespan manual smoke attempt through `POST /internal/event/debug`
      was blocked in this workspace by unresolved external DB host at startup;
      pitfall and guardrail were captured in `.codex/context/LEARNING_JOURNAL.md`.

- [x] PRJ-331 Extend planning, motivation, and proactive logic with governed trust signals
  - Status: DONE
  - Group: Relation Lifecycle And Trust Influence
  - Owner: Backend Builder
  - Depends on: PRJ-330
  - Priority: P1
  - Result:
    - proactive trust governance now calibrates outreach behavior through
      delivery-reliability-aware interruption cost adjustments, relevance
      penalties/bonuses, and trust-shaped output-type posture for
      low-trust/high-trust paths
    - motivation now uses delivery-reliability tie-breaks on ambiguous turns
      (`high_trust -> execute`, `low_trust -> analyze`) without overriding
      explicit execution/analysis/emotional signals
    - planning now encodes explicit trust confidence posture steps
      (`plan_with_confident_next_step|plan_with_cautious_validation`) and
      trust-aware proactive outreach tone steps
      (`use_confident_outreach_tone|use_low_pressure_outreach_tone`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_adaptive_policy.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
      (`172 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`247 passed`)

- [x] PRJ-330 Implement relation decay and confidence revalidation policy
  - Status: DONE
  - Group: Relation Lifecycle And Trust Influence
  - Owner: Backend Builder
  - Depends on: PRJ-329
  - Priority: P1
  - Result:
    - relation reads now apply age-aware confidence revalidation with
      evidence-sensitive decay, so stale relation signals weaken over time and
      expire from retrieval once confidence falls below expiration posture
    - relation upserts now refresh confidence and evidence through
      quality-weighted blending for repeated same-value signals, while
      value-shift updates reset relation posture for revalidation
    - reflection now persists relation-only updates (including
      `delivery_reliability=low_trust`) instead of treating those turns as noop
      when no conclusion/theta update is produced
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
      (`155 passed`)

- [x] PRJ-329 Sync docs/context for identity, language, and profile boundary hardening
  - Status: DONE
  - Group: Identity, Language, And Profile Boundary Hardening
  - Owner: Product Docs
  - Depends on: PRJ-328
  - Priority: P1
  - Result:
    - canonical docs, implementation reality, planning notes, and project
      context now describe the same identity continuity baseline
    - identity ownership boundaries are now explicit across docs:
      profile-language ownership in `aion_profile`, conclusion-owned
      response/collaboration preferences, and request-scoped API identity
      fallback precedence
  - Validation:
    - targeted identity-boundary cross-doc review recorded across
      `docs/overview.md`, `docs/implementation/runtime-reality.md`,
      `docs/planning/open-decisions.md`,
      `docs/planning/next-iteration-plan.md`,
      `.codex/context/TASK_BOARD.md`, and
      `.codex/context/PROJECT_STATE.md`

- [x] PRJ-328 Add identity and language continuity regressions across session and API fallback boundaries
  - Status: DONE
  - Group: Identity, Language, And Profile Boundary Hardening
  - Owner: QA/Test
  - Depends on: PRJ-327
  - Priority: P1
  - Result:
    - language continuity regressions now pin ambiguous-turn behavior for
      durable profile continuity across runtime session restarts
    - API fallback regressions now pin per-request user-id boundary semantics
      so header-based identity fallback does not leak across subsequent requests
      without explicit identity input
    - continuity drift between profile state and observable response language
      behavior is now test-visible across runtime and API boundaries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`141 passed`)

- [x] PRJ-327 Add richer language continuity policy across profile, memory, and current turn context
  - Status: DONE
  - Group: Identity, Language, And Profile Boundary Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-326
  - Priority: P1
  - Result:
    - language decision logic now follows explicit precedence across
      current-turn signals, recent memory continuity, and durable profile
      preference signals
    - continuity heuristics now ingest structured episodic payload language
      hints (`payload.response_language`) and ignore unsupported language codes
      instead of inheriting arbitrary two-letter values
    - ambiguous follow-up tie-breaks now allow explicit durable profile
      preference to win against conflicting memory continuity without changing
      non-ambiguous turn behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_context_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`
      (`140 passed`)

- [x] PRJ-326 Refactor identity loading around explicit profile-versus-conclusion ownership
  - Status: DONE
  - Group: Identity, Language, And Profile Boundary Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-325
  - Priority: P1
  - Result:
    - runtime identity load now applies explicit owner boundaries:
      `aion_profile` remains the durable owner for profile language while
      identity response/collaboration preferences are conclusion-owned inputs
      only
    - relation fallback cues continue to support runtime planning/expression,
      but identity continuity no longer inherits relation-derived
      collaboration fallback as if it were a durable identity preference
    - runtime pipeline regression coverage now pins this owner boundary so
      profile-versus-conclusion identity continuity cannot silently drift
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`136 passed`)

- [x] PRJ-325 Sync docs/context/runbook for scheduler externalization and attention ownership
  - Status: DONE
  - Group: Scheduler Externalization And Attention Ownership
  - Owner: Product Docs + Ops/Release
  - Depends on: PRJ-324
  - Priority: P1
  - Result:
    - canonical docs, implementation reality, planning notes, and ops runbook
      now align with owner-aware scheduler cadence posture
      (`SCHEDULER_EXECUTION_MODE`, cadence owner/readiness fields) and attention
      owner posture (`ATTENTION_COORDINATION_MODE`, deployment-readiness fields)
    - group handoff is explicit and queue progression is synchronized so
      identity/language hardening starts from `PRJ-326` without drift
  - Validation:
    - doc-and-context sync plus targeted scheduler/attention cross-doc review
      across `docs/overview.md`,
      `docs/architecture/26_env_and_config.md`,
      `docs/operations/runtime-ops-runbook.md`,
      `docs/implementation/runtime-reality.md`,
      `docs/planning/open-decisions.md`,
      `docs/planning/next-iteration-plan.md`,
      `.codex/context/TASK_BOARD.md`, and
      `.codex/context/PROJECT_STATE.md`

- [x] PRJ-324 Add attention-inbox ownership posture for future durable coordination rollout
  - Status: DONE
  - Group: Scheduler Externalization And Attention Ownership
  - Owner: Backend Builder
  - Depends on: PRJ-323
  - Priority: P1
  - Result:
    - attention coordination now exposes explicit owner posture
      (`in_process|durable_inbox`) with machine-visible ownership fields in
      `/health.attention`
    - attention boundary now has explicit deployment-readiness semantics and
      durable-owner blockers, creating a clean seam for future durable inbox
      rollout
    - in durable-owner posture, in-process turn assembly is explicitly bypassed
      so future durable coordination can replace local coalescing without
      hidden coupling
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_scheduler_contracts.py tests/test_config.py`

- [x] PRJ-323 Route maintenance and proactive cadence through the shared owner-aware dispatch boundary
  - Status: DONE
  - Group: Scheduler Externalization And Attention Ownership
  - Owner: Backend Builder
  - Depends on: PRJ-322
  - Priority: P1
  - Result:
    - maintenance/proactive cadence now use shared owner-aware dispatch
      decisions (`in_process_owner_mode|externalized_owner_mode`) instead of
      reflection-only ownership assumptions
    - scheduler maintenance execution now honors cadence ownership mode and
      explicitly no-ops under externalized ownership posture
    - scheduler health/snapshot posture now exposes cadence dispatch reasons for
      maintenance and proactive paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_api_routes.py`

- [x] PRJ-322 Implement owner-aware scheduler execution mode and health snapshot
  - Status: DONE
  - Group: Scheduler Externalization And Attention Ownership
  - Owner: Backend Builder + Ops/Release
  - Depends on: PRJ-321
  - Priority: P1
  - Result:
    - scheduler/runtime now expose explicit cadence execution mode
      (`in_process|externalized`) through shared scheduler contracts and health
      snapshot posture
    - `/health.scheduler` now exposes explicit maintenance/proactive cadence
      owner signals (`in_process_scheduler|external_scheduler`) plus
      readiness/blocker posture so operators no longer infer ownership from
      scattered runtime flags
    - scheduler worker snapshot now carries owner-aware cadence execution
      posture (`execution_mode`, `configured_enabled`, proactive posture, and
      readiness signals)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_config.py`

- [x] PRJ-321 Sync docs/context/runbook for internal debug ingress migration
  - Status: DONE
  - Group: Internal Debug Ingress Migration
  - Owner: Product Docs + Ops/Release
  - Depends on: PRJ-320
  - Priority: P1
  - Result:
    - canonical docs, planning, and runbook now align on primary internal
      debug ingress (`POST /internal/event/debug`) plus transitional shared
      posture (`POST /event/debug`)
    - architecture, operations, and planning docs now include shared
      break-glass posture controls and updated compatibility-header migration
      semantics
    - planning pointer is synchronized so next execution slice starts from
      `PRJ-322` without queue drift
  - Validation:
    - doc-and-context sync plus targeted debug-ingress cross-doc review recorded in this slice

- [x] PRJ-320 Add debug-ingress migration regressions and smoke coverage
  - Status: DONE
  - Group: Internal Debug Ingress Migration
  - Owner: QA/Test + Ops/Release
  - Depends on: PRJ-319
  - Priority: P1
  - Result:
    - API regressions now pin shared-ingress break-glass posture and health
      migration visibility in addition to internal-ingress ownership
    - release smoke scripts now fail fast when internal/shared debug-ingress
      path or break-glass posture contracts drift from runtime policy baseline
  - Validation:
    - `.\scripts\run_release_smoke.ps1` (not run in this slice: no live target URL in this environment)
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`

- [x] PRJ-319 Add break-glass override and shared-endpoint sunset posture for debug access
  - Status: DONE
  - Group: Internal Debug Ingress Migration
  - Owner: Backend Builder
  - Depends on: PRJ-318
  - Priority: P1
  - Result:
    - shared endpoint `POST /event/debug` now supports explicit posture modes
      (`compatibility|break_glass_only`) and enforces break-glass override
      header in break-glass-only mode
    - runtime policy now exposes shared-ingress break-glass posture fields
      (`event_debug_shared_ingress_mode`,
      `event_debug_shared_ingress_break_glass_required`,
      `event_debug_shared_ingress_posture`) for release visibility
    - API/config/runtime-policy regression coverage now pins shared-ingress
      break-glass behavior and runtime posture signals
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-318 Implement a dedicated internal debug ingress boundary and shared guard path
  - Status: DONE
  - Group: Internal Debug Ingress Migration
  - Owner: Backend Builder
  - Depends on: PRJ-317
  - Priority: P1
  - Result:
    - runtime now exposes `POST /internal/event/debug` as the explicit primary
      internal debug ingress that owns `system_debug` access semantics
    - shared `POST /event/debug` now acts as compatibility ingress with
      migration headers, while `POST /event?debug=true` compatibility headers
      point to the internal ingress path
    - runtime policy snapshot now surfaces explicit debug-ingress ownership and
      path posture fields for operator visibility
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`

- [x] PRJ-317 Make runtime behavior validation part of release-readiness and sync docs/context/runbook
  - Status: DONE
  - Group: Memory, Continuity, And Failure Validation
  - Owner: Product Docs + Ops/Release + QA/Test
  - Depends on: PRJ-316
  - Priority: P1
  - Result:
    - release readiness now includes behavior-validation evidence through
      `scripts/run_behavior_validation.{ps1,sh}` plus full regression checks
    - runbook, planning, and project state are synchronized with the
      living-system validation baseline
  - Validation:
    - `.\scripts\run_behavior_validation.ps1`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-316 Add contradiction, missing-data, and noisy-input behavior scenarios
  - Status: DONE
  - Group: Memory, Continuity, And Failure Validation
  - Owner: QA/Test + Backend Builder
  - Depends on: PRJ-315
  - Priority: P1
  - Result:
    - failure-mode scenarios now validate contradiction, missing-data, and
      noisy-input handling through structured behavior-harness outputs
    - fallback quality is now explicitly regression-covered
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_motivation_engine.py tests/test_expression_agent.py`

- [x] PRJ-315 Add multi-session continuity and personality-stability simulation scenarios
  - Status: DONE
  - Group: Memory, Continuity, And Failure Validation
  - Owner: QA/Test
  - Depends on: PRJ-314
  - Priority: P1
  - Result:
    - continuity scenarios now pin identity/tone/language stability across
      session restart boundaries
    - context reuse across turns is now behavior-tested through scenario output
      contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_expression_agent.py tests/test_planning_agent.py tests/test_language_runtime.py`

- [x] PRJ-314 Add memory behavior scenarios for write, retrieval, influence, and delayed recall
  - Status: DONE
  - Group: Memory, Continuity, And Failure Validation
  - Owner: QA/Test + Backend Builder
  - Depends on: PRJ-313
  - Priority: P1
  - Result:
    - memory scenarios now pin `write -> retrieve -> influence -> delayed
      recall` through repeatable harness execution
    - memory cannot be considered complete when retrieval does not influence
      later context behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_memory_repository.py tests/test_api_routes.py`

- [x] PRJ-313 Sync docs/context for runtime behavior testing architecture and internal validation contract
  - Status: DONE
  - Group: Runtime Behavior Testing Architecture
  - Owner: Product Docs + QA/Test
  - Depends on: PRJ-312
  - Priority: P1
  - Result:
    - canonical docs, engineering guidance, and context now align around one
      behavior-validation baseline
    - open decisions now record runtime behavior-validation posture as resolved
      baseline
  - Validation:
    - doc-and-context sync plus targeted cross-doc consistency review recorded
      in this slice

- [x] PRJ-312 Add structured behavior-harness output and scenario execution helpers
  - Status: DONE
  - Group: Runtime Behavior Testing Architecture
  - Owner: QA/Test
  - Depends on: PRJ-311
  - Priority: P1
  - Result:
    - behavior-harness helpers now provide structured scenario result contract
      (`test_id/status/reason/trace_id/notes`)
    - dedicated behavior-validation scripts now make scenario execution
      repeatable across local/release workflows
  - Validation:
    - `.\scripts\run_behavior_validation.ps1`
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_scheduler_contracts.py`

- [x] PRJ-311 Implement the internal system-debug validation surface for behavior checks
  - Status: DONE
  - Group: Runtime Behavior Testing Architecture
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-310
  - Priority: P1
  - Result:
    - internal debug responses now expose canonical `system_debug` fields for
      event normalization, memory bundle, context, motivation, role, plan
      intents, expression, and action traces
    - behavior debugging no longer depends on scattered endpoint payloads
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_logging.py`

- [x] PRJ-310 Define the canonical runtime behavior testing contract and required system-debug surface
  - Status: DONE
  - Group: Runtime Behavior Testing Architecture
  - Owner: Planner + QA/Test
  - Depends on: PRJ-309
  - Priority: P1
  - Result:
    - architecture now explicitly defines required behavior-validation modes
      (`system_debug`, `user_simulation`) and minimum internal debug fields
    - future cognitive slices can use one shared behavior contract baseline
  - Validation:
    - doc-and-context sync plus targeted behavior-testing architecture review
      recorded in this slice

- [x] PRJ-309 Sync docs/context/runbook for post-reflection hardening queue decisions
  - Status: DONE
  - Group: Post-Reflection Hardening Queue
  - Owner: Product Docs + Ops/Release
  - Depends on: PRJ-308
  - Priority: P1
  - Result:
    - planning, project state, and ops runbook remain synchronized after
      post-reflection decision closure slices
    - release-readiness and runtime-governance docs stay aligned with the next
      hardening lane
  - Validation:
    - doc-and-context sync plus targeted cross-doc consistency review recorded
      in this slice

- [x] PRJ-308 Define long-term scheduler externalization boundary for maintenance/proactive cadence ownership
  - Status: DONE
  - Group: Post-Reflection Hardening Queue
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-307
  - Priority: P1
  - Result:
    - scheduler/proactive follow-up now has one explicit target posture for
      app-local vs external cadence ownership after reflection rollout
    - later implementation slices can converge on one cadence owner model
      instead of reopening decision `12` every cycle
  - Validation:
    - doc-and-context sync plus targeted scheduler-boundary review recorded in
      this slice

- [x] PRJ-307 Define target internal debug ingress boundary and migration posture away from shared public API service endpoint
  - Status: DONE
  - Group: Post-Reflection Hardening Queue
  - Owner: Planner + Product Docs
  - Depends on: PRJ-306
  - Priority: P1
  - Result:
    - public-api follow-up decision now has explicit target-state ingress
      contract and migration ownership boundaries
    - debug-surface hardening can proceed without redefining runtime-policy
      baselines each slice
  - Validation:
    - doc-and-context sync plus targeted public-api boundary review recorded in
      this slice

- [x] PRJ-306 Define criteria and migration guardrails for removing `create_tables` compatibility startup path
  - Status: DONE
  - Group: Post-Reflection Hardening Queue
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-305
  - Priority: P1
  - Result:
    - migration-strategy follow-up now has explicit guardrails and removal
      criteria for retiring `create_tables` compatibility startup path
    - removal rollout order is codified to keep future implementation slices
      reversible and auditable
  - Validation:
    - doc-and-context sync plus targeted migration-strategy review recorded in
      this slice

- [x] PRJ-305 Derive and record the next execution queue after reflection lane closure
  - Status: DONE
  - Group: Post-Reflection Planning Baseline
  - Owner: Planner + Product Docs
  - Depends on: PRJ-304
  - Priority: P1
  - Result:
    - post-reflection hardening queue is now seeded through `PRJ-309` from
      remaining open decisions
    - execution continuity is preserved after `PRJ-304` without ad-hoc queue
      selection
  - Validation:
    - doc-and-context sync plus targeted planning coherence review recorded in
      this slice

- [x] PRJ-304 Sync docs/context/runbook for reflection deployment baseline and readiness contract
  - Status: DONE
  - Group: Reflection Deployment Baseline
  - Owner: Product Docs + Ops/Release
  - Depends on: PRJ-303
  - Priority: P1
  - Result:
    - planning, project state, and runbook truth are now synchronized after the
      post-convergence reflection implementation slices
    - release and rollback guidance now consistently include the reflection
      readiness gate
  - Validation:
    - doc-and-context sync plus targeted ops-runbook review recorded in this
      slice

- [x] PRJ-303 Add reflection deployment-readiness regressions and smoke script alignment
  - Status: DONE
  - Group: Reflection Deployment Baseline
  - Owner: Backend Builder + Ops/Release
  - Depends on: PRJ-302
  - Priority: P1
  - Result:
    - regression coverage now pins reflection deployment-readiness blocker
      signals in shared scheduler contracts and `/health` integration paths
    - release smoke scripts now fail fast on reflection deployment-readiness
      blockers with explicit fallback checks for older runtimes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_scheduler_contracts.py`

- [x] PRJ-302 Add explicit `/health.reflection` deployment-readiness summary for chosen runtime-mode baseline
  - Status: DONE
  - Group: Reflection Deployment Baseline
  - Owner: Backend Builder + Ops/Release
  - Depends on: PRJ-301
  - Priority: P1
  - Result:
    - `/health.reflection` now exposes deployment-readiness posture
      (`ready`, `blocking_signals`, baseline/selected runtime mode)
    - reflection-mode migration can now be verified through health contract
      signals instead of log-only interpretation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_reflection_worker.py`

- [x] PRJ-301 Define production reflection runtime-mode deployment baseline and external-dispatch readiness criteria
  - Status: DONE
  - Group: Reflection Deployment Baseline
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-300
  - Priority: P1
  - Result:
    - production baseline now keeps `REFLECTION_RUNTIME_MODE=in_process` as
      default posture
    - deferred reflection dispatch now has explicit rollout-readiness criteria
      instead of implicit operator judgment
  - Validation:
    - doc-and-context sync plus targeted reflection-topology contract review
      recorded in this slice

- [x] PRJ-300 Derive and record the first post-convergence execution queue
  - Status: DONE
  - Group: Post-Convergence Planning Baseline
  - Owner: Planner + Product Docs
  - Depends on: PRJ-299
  - Priority: P1
  - Result:
    - first post-convergence execution queue is now seeded through `PRJ-304`
      from remaining open decisions and reflected in planning docs plus task
      board state
    - execution does not stall after `PRJ-299` because the next lane is
      explicitly scoped into small reversible slices
  - Validation:
    - doc-and-context sync plus targeted planning coherence review recorded in
      this slice

- [x] PRJ-299 Add release-readiness regressions and sync docs/context/runbook
  - Status: DONE
  - Group: Operational Hardening And Release Truth
  - Owner: QA/Test + Product Docs + Ops/Release
  - Depends on: PRJ-298
  - Priority: P1
  - Result:
    - `/health` now exposes release-readiness gate posture and smoke scripts
      fail fast on production-policy drift
    - release-readiness regressions and operational docs now match the
      target-state production baseline
    - planning, project state, and runbook truth remain synchronized at the
      end of the convergence queue
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-298 Finalize deployment and release truth for Coolify/manual fallback and smoke ownership
  - Status: DONE
  - Group: Operational Hardening And Release Truth
  - Owner: Ops/Release
  - Depends on: PRJ-297
  - Priority: P1
  - Result:
    - deployment automation, manual fallback, and release smoke ownership are
      documented as one coherent operational path
    - execution work stops assuming deploy behavior that operations cannot yet
      prove
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-297 Enforce migration-first and internal-debug posture through explicit runtime gates
  - Status: DONE
  - Group: Operational Hardening And Release Truth
  - Owner: Backend Builder
  - Depends on: PRJ-296
  - Priority: P1
  - Result:
    - runtime and config boundaries reflect the agreed production target while
      keeping any temporary escape hatches explicit and reviewable
    - startup and API policy posture move closer to the final deployment shape
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

- [x] PRJ-296 Define the target production posture for migration-only startup, strict defaults, and the internal debug boundary
  - Status: DONE
  - Group: Operational Hardening And Release Truth
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-295
  - Priority: P1
  - Result:
    - one target production baseline defines migration-only startup posture,
      strict policy defaults, and the intended internal-versus-public debug
      boundary
    - later hardening slices can remove temporary rollout ambiguity instead of
      creating more diagnostic layers
  - Validation:
    - doc-and-context sync plus targeted production-baseline review recorded in
      this slice

- [x] PRJ-295 Add dual-loop execution-boundary regressions and sync docs/context
  - Status: DONE
  - Group: Attention And Proposal Execution Boundary
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-294
  - Priority: P1
  - Result:
    - turn assembly, proposal handoff, proactive delivery, and permission-gated
      external intent flows are pinned end to end
    - docs and context now describe one coherent dual-loop execution model
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py tests/test_action_executor.py tests/test_planning_agent.py`

- [x] PRJ-294 Route proactive outreach and connector permission gates through the shared attention/proposal boundary
  - Status: DONE
  - Group: Attention And Proposal Execution Boundary
  - Owner: Backend Builder
  - Depends on: PRJ-293
  - Priority: P1
  - Result:
    - proactive delivery and external-connector permission outcomes now share
      one conscious execution boundary
    - connector suggestions and outreach plans stop bypassing the same gating
      model used for batched conversation handling
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_planning_agent.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- [x] PRJ-293 Implement end-to-end proposal persistence and conscious handoff decisions
  - Status: DONE
  - Group: Attention And Proposal Execution Boundary
  - Owner: Backend Builder
  - Depends on: PRJ-292
  - Priority: P1
  - Result:
    - subconscious proposals can persist durably and re-enter conscious runtime
      through explicit handoff decisions
    - user-visible actions remain blocked until conscious runtime accepts or
      merges a proposal
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_planning_agent.py`

- [x] PRJ-292 Define a durable proposal lifecycle and canonical turn-assembly ownership contract
  - Status: DONE
  - Group: Attention And Proposal Execution Boundary
  - Owner: Planner
  - Depends on: PRJ-291
  - Priority: P1
  - Result:
    - proposal persistence, handoff decisions, and pending-turn ownership have
      one explicit contract owner
    - future dual-loop changes no longer need to infer whether attention or
      planning owns a boundary
  - Validation:
    - doc-and-context sync plus targeted dual-loop contract review recorded in
      this slice

- [x] PRJ-291 Add adaptive-governance regressions and sync docs/context
  - Status: DONE
  - Group: Adaptive Cognition Governance
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-290
  - Priority: P1
  - Result:
    - anti-feedback-loop, cross-goal-leakage, and adaptive influence scope
      expectations are pinned by regression coverage
    - docs and context describe the same adaptive governance rules
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-288 Define evidence thresholds and influence policy for adaptive signals
  - Status: DONE
  - Group: Adaptive Cognition Governance
  - Owner: Planner
  - Depends on: PRJ-287
  - Priority: P1
  - Result:
    - canonical contracts now define one explicit adaptive influence policy for
      affective, relation, preference, and theta signals
    - adaptive influence now has documented evidence gates, precedence, and
      tie-break boundaries instead of undocumented expansion
  - Validation:
    - doc-and-context sync plus targeted adaptive-policy review recorded in
      this slice
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-287 Add production retrieval rollout regressions and sync docs/context
  - Status: DONE
  - Group: Production Memory Retrieval Rollout
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-286
  - Priority: P1
  - Result:
    - production retrieval diagnostics are now regression-pinned for hybrid
      query defaults in runtime integration tests and rollout posture in health
      contract tests
    - planning, project state, runtime-reality, and open-decisions docs are
      synchronized to the rollout state after semantic+affective+relation
      source-family enablement support
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_context_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-286 Extend vector rollout to affective and relation families with explicit gating
  - Status: DONE
  - Group: Production Memory Retrieval Rollout
  - Owner: Backend Builder
  - Depends on: PRJ-285
  - Priority: P1
  - Result:
    - affective conclusion embeddings now materialize vectors with explicit
      refresh ownership metadata (`materialized_on_write` vs
      `pending_manual_refresh`) under source-family gates
    - relation embedding writes are now source-gated and materialize vectors
      with the same refresh ownership contract when `relation` rollout is
      enabled
    - hybrid retrieval vector queries now include relation source family so
      rollout can progress from semantic baseline toward full source coverage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-285 Implement the provider-owned semantic and episodic vector materialization path
  - Status: DONE
  - Group: Production Memory Retrieval Rollout
  - Owner: Backend Builder
  - Depends on: PRJ-284
  - Priority: P1
  - Result:
    - semantic conclusion embeddings now materialize vectors on write when
      refresh ownership is `on_write`, including deterministic fallback when
      non-implemented providers are requested
    - episodic embedding writes now explicitly honor refresh ownership
      (`materialized_on_write` vs `pending_manual_refresh`) with provider/model
      fallback metadata for retrieval diagnostics
    - retrieval no longer treats semantic embeddings as primarily diagnostic
      shells during the baseline rollout
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_memory_repository.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-284 Define the production retrieval baseline for provider, refresh ownership, and family rollout order
  - Status: DONE
  - Group: Production Memory Retrieval Rollout
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-283
  - Priority: P1
  - Result:
    - one target production baseline now defines provider ownership, refresh
      ownership, default vector posture, and family rollout order
      (`episodic+semantic -> affective -> relation`)
    - retrieval implementation slices can now converge on one stable baseline
      instead of reopening rollout strategy each cycle
  - Validation:
    - doc-and-context sync plus targeted retrieval-baseline review recorded
      across `docs/planning/open-decisions.md`,
      `docs/architecture/26_env_and_config.md`,
      `docs/implementation/runtime-reality.md`, and
      `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-283 Add background-topology regressions and sync docs/context
  - Status: DONE
  - Group: Background Reflection Topology
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-282
  - Priority: P1
  - Result:
    - regression coverage now pins worker-mode handoff behavior in
      `in_process|deferred` operation across reflection retry posture,
      scheduler runtime logs, and `/health.reflection.topology`
    - planning, project state, and runtime-ops docs are synchronized to the
      converged background-topology contract through `PRJ-283`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

- [x] PRJ-282 Add worker-mode health, queue-drain, and retry handoff contract
  - Status: DONE
  - Group: Background Reflection Topology
  - Owner: Backend Builder + Ops/Release
  - Depends on: PRJ-281
  - Priority: P1
  - Result:
    - `/health.reflection.topology` now exposes explicit handoff posture for
      in-process and deferred operation (`queue_drain_owner`,
      `external_driver_expected`, enqueue/scheduler dispatch decisions, and
      retry ownership metadata)
    - scheduler reflection tick logs now emit mode-aware handoff fields so
      queue-drain/retry ownership remains observable when external dispatch is
      expected
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_api_routes.py tests/test_scheduler_worker.py tests/test_logging.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py`

- [x] PRJ-281 Extract the reflection enqueue/dispatch boundary from app-local scheduler ownership
  - Status: DONE
  - Group: Background Reflection Topology
  - Owner: Backend Builder
  - Depends on: PRJ-280
  - Priority: P1
  - Result:
    - runtime and scheduler now consume one shared reflection dispatch-boundary
      contract (`reflection_enqueue_dispatch_decision` and
      `reflection_scheduler_dispatch_decision`) instead of duplicating
      mode/worker ownership rules
    - runtime enqueue behavior now keeps durable enqueue ownership while
      dispatch intent is explicitly mode-aware (`in_process|deferred`) even when
      a reflection worker instance is attached
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_main_lifespan_policy.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py`

- [x] PRJ-280 Define target-state reflection topology and worker-mode contract
  - Status: DONE
  - Group: Background Reflection Topology
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-279
  - Priority: P1
  - Result:
    - canonical contracts now define reflection topology ownership across
      `in_process|deferred` runtime modes, durable queue semantics, and
      mode-independent enqueue ownership
    - runtime-reality and ops docs now describe operator-visible posture and
      topology invariants without redefining architecture
  - Validation:
    - doc-and-context sync completed; targeted topology review recorded across
      `docs/architecture/15_runtime_flow.md`,
      `docs/architecture/16_agent_contracts.md`,
      `docs/implementation/runtime-reality.md`, and
      `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-279 Add foreground architecture-parity regressions and sync docs/context
  - Status: DONE
  - Group: Foreground Runtime Convergence
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-278
  - Priority: P1
  - Result:
    - architecture-parity regressions now pin foreground boundary ordering in
      runtime, API debug payload, and logging test surfaces
    - docs, planning, and context are synchronized to the converged foreground
      ownership boundary through `PRJ-279`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py tests/test_graph_state_contract.py`

- [x] PRJ-278 Align graph/runtime orchestration boundaries for baseline load, memory write, and reflection trigger
  - Status: DONE
  - Group: Foreground Runtime Convergence
  - Owner: Backend Builder
  - Depends on: PRJ-277
  - Priority: P1
  - Result:
    - runtime now exposes explicit pre-graph seed ownership, graph-stage
      execution boundary, and post-graph follow-up ownership in
      `RuntimeOrchestrator`
    - foreground flow keeps target-state traceability without breaking the
      action boundary
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_graph_state_contract.py tests/test_graph_stage_adapters.py tests/test_main_lifespan_policy.py`

- [x] PRJ-277 Introduce an explicit response-execution contract for expression-to-action handoff
  - Status: DONE
  - Group: Foreground Runtime Convergence
  - Owner: Backend Builder
  - Depends on: PRJ-276
  - Priority: P1
  - Result:
    - expression now emits explicit response-execution handoff data consumed by
      action as the execution contract boundary
    - action execution no longer depends on implicit expression coupling for
      delivery preparation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`

- [x] PRJ-276 Define target-state foreground ownership and graph boundary invariants
  - Status: DONE
  - Group: Foreground Runtime Convergence
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-275
  - Priority: P1
  - Result:
    - target-state ownership is now explicit for graph-owned versus
      runtime-owned foreground segments (`baseline load`, stage graph,
      episodic memory write, reflection trigger)
    - canonical contracts now include migration invariants that keep stage
      output keys, ordering, and side-effect ownership stable during
      orchestration convergence
  - Validation:
    - doc-and-context sync completed; targeted contract diff review recorded
      across `docs/architecture/15_runtime_flow.md`,
      `docs/architecture/16_agent_contracts.md`, and
      `docs/implementation/runtime-reality.md`

- [x] PRJ-275 Sync source-rollout enforcement recommendation/alignment slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-274
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-275`
    - canonical env/config and runtime ops docs now include source-rollout
      enforcement recommendation/alignment diagnostics
    - runtime reality docs now record startup source-rollout enforcement hint
      posture and shared alignment ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-274 Add startup regression coverage for source-rollout enforcement recommendation/alignment hints
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: QA/Test
  - Depends on: PRJ-273
  - Priority: P2
  - Result:
    - startup log regressions now pin `embedding_source_rollout_enforcement_hint`
      posture for aligned and below-recommendation scenarios
    - warning/block log regressions now pin recommendation and alignment fields
      for warn and strict startup paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-273 Expand `/health.memory_retrieval` contract regressions for source-rollout enforcement recommendation/alignment fields
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: QA/Test
  - Depends on: PRJ-272
  - Priority: P2
  - Result:
    - API health contract tests now pin source-rollout enforcement recommendation
      and alignment fields across vectors-disabled, pending-rollout, strict
      blocked, and rollout-complete states
    - `/health` regression coverage now includes aligned strict posture once
      rollout is complete
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-272 Add shared snapshot regression coverage for source-rollout enforcement recommendation/alignment diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: QA/Test
  - Depends on: PRJ-271
  - Priority: P2
  - Result:
    - embedding strategy unit regressions now pin recommendation/alignment
      semantics for vectors-disabled, pending-rollout, rollout-complete, strict
      blocked, and strict aligned states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-271 Add startup source-rollout enforcement alignment hint logs from shared diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-270
  - Priority: P2
  - Result:
    - startup now emits `embedding_source_rollout_enforcement_hint` with current
      enforcement, recommendation, alignment, and rollout completion context
    - hint log posture is shared across aligned, below-recommendation, and
      above-recommendation scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_embedding_strategy.py`

- [x] PRJ-270 Enrich startup source-rollout enforcement warning/block logs with recommendation/alignment diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-269
  - Priority: P2
  - Result:
    - `embedding_source_rollout_warning` now includes recommended enforcement and
      alignment diagnostics from shared snapshot ownership
    - `embedding_source_rollout_block` now includes recommendation/alignment
      diagnostics for strict pending-rollout fail-fast posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-269 Expose source-rollout enforcement recommendation/alignment diagnostics through `/health.memory_retrieval`
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-268
  - Priority: P2
  - Result:
    - `/health.memory_retrieval` now surfaces source-rollout enforcement
      recommendation/alignment fields
      (`semantic_embedding_recommended_source_rollout_enforcement`,
      `semantic_embedding_source_rollout_enforcement_alignment`,
      `semantic_embedding_source_rollout_enforcement_alignment_state`,
      `semantic_embedding_source_rollout_enforcement_alignment_hint`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_embedding_strategy.py`

- [x] PRJ-268 Add source-rollout enforcement alignment state/hint diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-267
  - Priority: P2
  - Result:
    - shared snapshot now exposes source-rollout enforcement alignment state/hint
      (`semantic_embedding_source_rollout_enforcement_alignment_state`,
      `semantic_embedding_source_rollout_enforcement_alignment_hint`)
    - alignment state semantics now distinguish aligned, below-recommendation,
      above-recommendation, and vectors-disabled posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-267 Add source-rollout enforcement alignment primitive diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-266
  - Priority: P2
  - Result:
    - shared snapshot now exposes source-rollout enforcement alignment primitive
      (`semantic_embedding_source_rollout_enforcement_alignment`) against
      rollout-aware recommendation posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-266 Add source-rollout enforcement recommendation diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-265
  - Priority: P2
  - Result:
    - shared snapshot now exposes rollout-aware source-rollout enforcement
      recommendation (`semantic_embedding_recommended_source_rollout_enforcement`)
      with `warn` while rollout is pending and `strict` when rollout is complete
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-265 Sync embedding source-rollout enforcement slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-264
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-265`
    - canonical env/config and runtime ops docs now include source-rollout
      enforcement controls and diagnostics
    - runtime reality docs now record startup source-rollout enforcement
      warning/block posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-264 Add startup source-rollout enforcement warning/block logs from shared diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-263
  - Priority: P2
  - Result:
    - startup now emits `embedding_source_rollout_warning` when rollout is
      pending and enforcement stays in `warn`
    - startup now emits `embedding_source_rollout_block` and fails fast when
      rollout is pending and `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT=strict`
    - runtime policy regressions now pin both warn-mode visibility and strict
      startup block behavior for pending rollout posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_embedding_strategy.py`

- [x] PRJ-263 Expose source-rollout enforcement diagnostics through `/health.memory_retrieval`
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-262
  - Priority: P2
  - Result:
    - `/health.memory_retrieval` now surfaces source-rollout enforcement fields
      (`semantic_embedding_source_rollout_enforcement`,
      `semantic_embedding_source_rollout_enforcement_state`,
      `semantic_embedding_source_rollout_enforcement_hint`)
    - health contract regressions now pin vectors-disabled, pending-rollout,
      and fully-enabled rollout enforcement posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_embedding_strategy.py`

- [x] PRJ-262 Add source-rollout enforcement diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-261
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes source-rollout enforcement
      diagnostics
      (`semantic_embedding_source_rollout_enforcement`,
      `semantic_embedding_source_rollout_enforcement_state`,
      `semantic_embedding_source_rollout_enforcement_hint`)
    - rollout enforcement posture is now machine-readable for vectors-disabled,
      pending-rollout, and fully-enabled rollout states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-261 Add source-rollout enforcement runtime setting contract
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-260
  - Priority: P2
  - Result:
    - runtime settings now expose
      `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` (`warn|strict`) with `warn`
      default
    - config regressions now pin defaults, strict mode acceptance, and invalid
      mode rejection
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-260 Sync embedding refresh-strategy guidance slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-259
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-260`
    - canonical env/config and runtime ops docs now include refresh
      cadence/recommendation/alignment diagnostics
    - runtime reality docs now record startup refresh-hint posture and shared
      refresh strategy ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-259 Add startup refresh-strategy hint logs from shared diagnostics
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-258
  - Priority: P2
  - Result:
    - startup refresh warning logs now include cadence diagnostics for manual
      posture visibility
    - startup now emits `embedding_refresh_hint` when refresh mode is not
      aligned with rollout recommendation posture
    - runtime log regressions now pin manual-override and
      on-write-before-manual-recommendation hint paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_embedding_strategy.py`

- [x] PRJ-258 Add refresh recommendation-alignment diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-257
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes refresh alignment posture
      (`semantic_embedding_refresh_alignment_state`,
      `semantic_embedding_refresh_alignment_hint`) against rollout-aware
      refresh recommendation
    - `/health.memory_retrieval` now surfaces refresh alignment posture across
      vectors-disabled, active rollout, and fully-enabled rollout states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-257 Add refresh strategy recommendation diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-256
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes recommended refresh mode
      (`semantic_embedding_recommended_refresh_mode`) using rollout-aware
      semantics (`on_write` during active rollout, `manual` for mature/full
      source rollout)
    - `/health.memory_retrieval` now surfaces recommended refresh posture for
      baseline and full-source rollout states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-256 Add refresh cadence diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-255
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes refresh cadence diagnostics
      (`semantic_embedding_refresh_cadence_state`,
      `semantic_embedding_refresh_cadence_hint`) for vectors-disabled, on-write,
      and manual high/moderate/low-frequency modes
    - `/health.memory_retrieval` now surfaces refresh cadence posture in all
      tested retrieval configurations
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-255 Sync embedding source-rollout sequencing slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-254
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-255`
    - canonical env/config and runtime ops docs now include source-rollout
      sequencing and progress diagnostics
    - runtime reality docs now record startup source-rollout hint behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-254 Add startup source-rollout hint logs from shared sequencing diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-253
  - Priority: P2
  - Result:
    - startup source-coverage warnings now include rollout completion and
      progress context from one shared snapshot owner
    - startup now emits `embedding_source_rollout_hint` when vectors are
      enabled and rollout still has a pending next source kind
    - runtime log regressions now pin rollout hint behavior for pending and
      all-sources-enabled states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-253 Add source-rollout progress diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-252
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes source-rollout progress
      fields (`semantic_embedding_source_rollout_phase_index`,
      `semantic_embedding_source_rollout_phase_total`,
      `semantic_embedding_source_rollout_progress_percent`)
    - `/health.memory_retrieval` now surfaces rollout progress posture across
      vectors-disabled, partial, baseline, and full-source states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-252 Add source-rollout sequencing diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-251
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes explicit source sequencing
      diagnostics (`semantic_embedding_source_rollout_order`,
      `semantic_embedding_source_rollout_enabled_sources`,
      `semantic_embedding_source_rollout_missing_sources`,
      `semantic_embedding_source_rollout_next_source_kind`)
    - `/health.memory_retrieval` now exposes machine-readable next-source
      guidance for rollout operations
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-251 Add relation-aware source-rollout completion posture in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-250
  - Priority: P2
  - Result:
    - source-rollout state now distinguishes full vector-source activation
      (`all_vector_sources_enabled`) from semantic+affective baseline
    - shared diagnostics now expose explicit completion posture through
      `semantic_embedding_source_rollout_completion_state`
    - `/health.memory_retrieval` and unit tests now pin relation-inclusive
      full rollout behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-250 Sync embedding strict-rollout guidance slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-249
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-250`
    - canonical env/config and runtime ops docs now include strict-rollout
      preflight/recommendation/alignment fields and startup
      `embedding_strategy_hint` posture
    - implementation reality docs now record shared strict-rollout ownership
      across `/health` and startup diagnostics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-249 Add startup embedding strategy rollout hints from shared strict-rollout diagnostics
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-248
  - Priority: P2
  - Result:
    - startup now emits `embedding_strategy_hint` when vectors are enabled and
      enforcement alignment is visible (`below|aligned|mixed|above`)
    - hint logs now include strict-rollout readiness, violation summary,
      recommendation, and recommended enforcement posture from one shared
      snapshot owner
    - runtime policy log regressions now pin hint behavior for
      below-recommendation and aligned strict posture cases
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_embedding_strategy.py`

- [x] PRJ-248 Add embedding enforcement-alignment diagnostics in shared strategy snapshot
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-247
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes per-control alignment
      fields (`semantic_embedding_provider_ownership_enforcement_alignment`,
      `semantic_embedding_model_governance_enforcement_alignment`) plus
      combined alignment posture
      (`semantic_embedding_enforcement_alignment_state`,
      `semantic_embedding_enforcement_alignment_hint`)
    - `/health.memory_retrieval` now surfaces alignment posture in baseline,
      vectors-disabled, fallback, and strict scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-247 Add embedding strict-rollout recommendation diagnostics in shared strategy snapshot
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-246
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes strict-rollout
      recommendation fields
      (`semantic_embedding_strict_rollout_recommendation`,
      `semantic_embedding_recommended_provider_ownership_enforcement`,
      `semantic_embedding_recommended_model_governance_enforcement`)
    - recommendation posture is now visible in `/health.memory_retrieval` for
      deterministic baseline, provider fallback, deterministic custom-model, and
      vectors-disabled states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-246 Add embedding strict-rollout preflight diagnostics in shared strategy snapshot
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-245
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes strict-rollout preflight
      diagnostics
      (`semantic_embedding_strict_rollout_violations`,
      `semantic_embedding_strict_rollout_violation_count`,
      `semantic_embedding_strict_rollout_ready`,
      `semantic_embedding_strict_rollout_state`,
      `semantic_embedding_strict_rollout_hint`)
    - strict rollout now has one machine-readable readiness owner across
      `/health.memory_retrieval` and startup logging pathways
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-245 Add embedding source-rollout recommendation posture in shared diagnostics
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-244
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes source-rollout recommendation
      posture through
      `semantic_embedding_source_rollout_state`,
      `semantic_embedding_source_rollout_hint`, and
      `semantic_embedding_source_rollout_recommendation`
    - `/health.memory_retrieval` now surfaces source-rollout posture for
      vectors-disabled, semantic+affective baseline, semantic-only,
      affective-only, and foundational-only source sets
    - startup source-coverage warning now includes shared source-rollout
      diagnostics for operator rollout guidance
    - docs/context/planning are synchronized through `PRJ-245`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-244 Add embedding owner-strategy recommendation posture in shared diagnostics
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-243
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes explicit owner-strategy
      recommendation posture through
      `semantic_embedding_owner_strategy_state`,
      `semantic_embedding_owner_strategy_hint`, and
      `semantic_embedding_owner_strategy_recommendation`
    - `/health.memory_retrieval` now surfaces owner-strategy recommendation
      posture for vectors-disabled, deterministic baseline/manual, and fallback
      provider ownership states
    - startup fallback warning now includes shared owner-strategy diagnostics
      for operator visibility
    - docs/context/planning are synchronized through `PRJ-244`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-243 Add embedding model-governance enforcement posture and strict startup block option
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-242
  - Priority: P2
  - Result:
    - runtime config now exposes explicit model-governance enforcement posture
      through `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` (`warn|strict`)
    - shared embedding strategy helper now exposes
      `semantic_embedding_model_governance_enforcement`,
      `semantic_embedding_model_governance_enforcement_state`, and
      `semantic_embedding_model_governance_enforcement_hint`
    - startup now supports strict model-governance block mode for
      deterministic custom-model-name posture, while warn mode remains
      warning-only
    - docs/context/planning are synchronized through `PRJ-243`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-242 Add embedding provider-ownership enforcement posture and strict startup block option
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-241
  - Priority: P2
  - Result:
    - runtime config now exposes explicit provider-ownership enforcement posture
      through `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` (`warn|strict`)
    - shared embedding strategy helper now exposes
      `semantic_embedding_provider_ownership_enforcement`,
      `semantic_embedding_provider_ownership_enforcement_state`, and
      `semantic_embedding_provider_ownership_enforcement_hint`
    - startup now supports strict provider-ownership block mode for fallback
      ownership posture, while warn mode remains warning-only
    - docs/context/planning are synchronized through `PRJ-242`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-241 Add embedding provider-ownership posture diagnostics and startup warning enrichment
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-240
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes provider-ownership posture
      diagnostics
      (`semantic_embedding_provider_ownership_state`,
      `semantic_embedding_provider_ownership_hint`) so ownership visibility is
      explicit for deterministic baseline, fallback, and vectors-disabled modes
    - `/health.memory_retrieval` now surfaces provider-ownership diagnostics
      through the same shared embedding strategy helper
    - startup `embedding_strategy_warning` now includes provider-ownership
      diagnostics when fallback posture is active
    - docs/context/planning are synchronized through `PRJ-241`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-240 Add embedding model-governance posture diagnostics and startup warning alignment
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-239
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes model-governance posture
      diagnostics
      (`semantic_embedding_model_governance_state`,
      `semantic_embedding_model_governance_hint`) alongside provider/model and
      refresh/source posture
    - `/health.memory_retrieval` now surfaces model-governance diagnostics from
      the same shared helper semantics
    - startup warning flow now emits
      `embedding_model_governance_warning` for deterministic custom-model-name
      posture so potentially misleading model config is operator-visible
    - docs/context/planning are synchronized through `PRJ-240`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-239 Unify embedding refresh posture semantics in shared strategy helper
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-238
  - Priority: P2
  - Result:
    - shared embedding strategy helper now owns refresh posture fields
      (`semantic_embedding_refresh_mode`,
      `semantic_embedding_refresh_interval_seconds`) and derived refresh
      diagnostics (`semantic_embedding_refresh_state`,
      `semantic_embedding_refresh_hint`)
    - `/health.memory_retrieval` and startup refresh warning flow now consume
      one shared refresh-posture owner, reducing drift risk
    - docs/context/planning are synchronized through `PRJ-239`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-238 Add explicit embedding refresh-cadence posture visibility and startup warning coverage
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-237
  - Priority: P2
  - Result:
    - runtime config now exposes explicit embedding refresh-cadence posture
      through `EMBEDDING_REFRESH_MODE` (`on_write|manual`) and
      `EMBEDDING_REFRESH_INTERVAL_SECONDS`
    - `/health.memory_retrieval` now exposes
      `semantic_embedding_refresh_mode` and
      `semantic_embedding_refresh_interval_seconds` for operator visibility
    - startup embedding strategy warnings now include
      `embedding_refresh_warning` when semantic vectors are enabled with manual
      refresh posture
    - docs/context/planning are synchronized through `PRJ-238`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-237 Add embedding source-coverage posture diagnostics and startup warning alignment
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-236
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes source-coverage posture for
      current vector retrieval path
      (`semantic_embedding_source_coverage_state`,
      `semantic_embedding_source_coverage_hint`)
    - `/health.memory_retrieval` now exposes those source-coverage diagnostics
      alongside provider/model/source configuration posture
    - startup now emits `embedding_source_coverage_warning` when vectors are
      enabled but semantic/affective source coverage is partial or missing,
      using the same shared coverage-state semantics as health
    - docs/context/planning are synchronized through `PRJ-237`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`

- [x] PRJ-236 Add explicit embedding source-family scope configuration and runtime gating
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-235
  - Priority: P2
  - Result:
    - runtime config now exposes `EMBEDDING_SOURCE_KINDS` with validation and
      explicit allowed family set (`episodic|semantic|affective|relation`)
    - action and memory repository embedding writes now respect enabled source
      families, so embedding persistence scope is explicit instead of implicit
    - `/health.memory_retrieval` now exposes effective configured embedding
      source kinds for operator visibility
    - docs/context/planning are synchronized through `PRJ-236`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`

- [x] PRJ-235 Unify embedding warning posture semantics across health and startup logging
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-234
  - Priority: P2
  - Result:
    - one shared helper now owns embedding strategy posture and warning state
      semantics used by both `/health.memory_retrieval` and startup warning
      logging
    - `memory_retrieval` now exposes explicit warning posture fields
      (`semantic_embedding_warning_state`, `semantic_embedding_warning_hint`)
      in addition to provider/model readiness posture
    - startup warning behavior is now tied to the same shared warning state
      (`provider_fallback_active`) used by health diagnostics
    - docs/context/planning are synchronized through `PRJ-235`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-234 Align conclusion embedding shell metadata with configured embedding strategy posture
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-233
  - Priority: P2
  - Result:
    - `MemoryRepository` now owns embedding strategy posture
      (`provider/model/dimensions`) so conclusion-driven semantic/affective
      embedding shells no longer use hardcoded `pending/0` values
    - conclusion embedding shells now persist effective model/dimensions plus
      requested-vs-effective provider metadata and explicit
      `pending_vector_materialization` status
    - app startup wiring now passes embedding strategy settings into
      `MemoryRepository`
    - docs/context/planning are synchronized through `PRJ-234`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`

- [x] PRJ-233 Add embedding provider readiness posture and startup fallback warning
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-232
  - Priority: P2
  - Result:
    - `/health.memory_retrieval` now exposes provider readiness posture through
      `semantic_embedding_provider_ready` and
      `semantic_embedding_posture` (`ready|fallback_deterministic`)
    - startup now emits `embedding_strategy_warning` whenever semantic vectors
      are enabled but requested embedding provider/model posture falls back to
      deterministic execution
    - planning/docs/context are synchronized through `PRJ-233`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-232 Add embedding strategy config posture and deterministic fallback visibility
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-231
  - Priority: P2
  - Result:
    - runtime settings now expose explicit embedding strategy controls
      (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`) with
      bounded validation
    - action/runtime now consume configured embedding dimensions and deterministic
      fallback posture when non-implemented providers are requested
    - `GET /health.memory_retrieval` now exposes requested vs effective
      embedding provider/model posture plus fallback hint and dimensions
    - task board, project state, and planning/docs artifacts are synchronized
      through `PRJ-232`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-231 Add semantic vector retrieval feature gate and health posture visibility
  - Status: DONE
  - Group: Semantic Retrieval Activation Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-230
  - Priority: P2
  - Result:
    - runtime now supports explicit `SEMANTIC_VECTOR_ENABLED` posture, so
      hybrid retrieval can run in `hybrid_vector_lexical` (default) or
      `lexical_only` mode without hidden behavior
    - action now skips episodic embedding writes when semantic vectors are
      disabled
    - `GET /health` now exposes `memory_retrieval` posture fields
      (`semantic_vector_enabled`, `semantic_retrieval_mode`) for operator
      visibility
    - task board, project state, and planning docs are now synchronized through
      `PRJ-231` with no hidden `READY` work
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-230 Sync compat activity posture slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-229
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat
      activity posture as complete through `PRJ-230`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_config.py`

- [x] PRJ-229 Record compat activity posture completion and validation evidence in project state
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Product Docs
  - Depends on: PRJ-228
  - Priority: P3
  - Result:
    - project state now records activity posture decision and latest validation
      evidence for this slice
  - Validation:
    - context sync review

- [x] PRJ-228 Sync planning docs for compat activity posture slice closure
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Product Docs
  - Depends on: PRJ-227
  - Priority: P3
  - Result:
    - next-iteration plan now records activity posture slice completion and
      queue advancement through `PRJ-230`
  - Validation:
    - docs sync review

- [x] PRJ-227 Document compat activity posture fields in architecture and operations docs
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Product Docs
  - Depends on: PRJ-226
  - Priority: P3
  - Result:
    - architecture, operations runbook, runtime-reality, and open-decisions
      docs now include compat activity posture fields and semantics
  - Validation:
    - docs sync review

- [x] PRJ-226 Add API regression for stale historical compat activity posture
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: QA/Test
  - Depends on: PRJ-225
  - Priority: P2
  - Result:
    - API tests now pin `stale_historical_attempts` posture when configured
      stale threshold is crossed after an observed compat attempt
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-225 Extend API regressions for compat activity posture fields
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: QA/Test
  - Depends on: PRJ-224
  - Priority: P2
  - Result:
    - API health contract tests now pin activity posture fields across
      no-attempt, compat-disabled, and recent-attempt scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-224 Add telemetry unit regressions for compat activity posture helper states
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: QA/Test
  - Depends on: PRJ-223
  - Priority: P2
  - Result:
    - telemetry tests now pin activity posture helper states and hints for
      disabled/no-attempt/stale/recent compat usage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-223 Expose compat activity posture through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Backend Builder
  - Depends on: PRJ-222
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now exposes
      `event_debug_query_compat_activity_state` and
      `event_debug_query_compat_activity_hint`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-222 Add shared compat activity posture helper from telemetry/freshness snapshots
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Backend Builder
  - Depends on: PRJ-221
  - Priority: P2
  - Result:
    - debug compat core now derives migration activity posture that separates
      disabled, no-attempt, stale-historical, and recent-attempt states while
      keeping sunset readiness contract unchanged
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-221 Derive compat activity posture slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-220
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on activity posture
      visibility for compat-route migration windows
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-220 Sync compat freshness signal slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-219
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat
      freshness signaling as complete through `PRJ-220`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_config.py`

- [x] PRJ-219 Document compat freshness threshold and fields in architecture/ops/local/runtime docs
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Product Docs
  - Depends on: PRJ-218
  - Priority: P3
  - Result:
    - architecture, local-development, ops runbook, runtime-reality, and
      open-decisions docs now include compat freshness fields and
      `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`
  - Validation:
    - docs sync review

- [x] PRJ-218 Extend config regressions for compat freshness threshold defaults and bounds
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: QA/Test
  - Depends on: PRJ-217
  - Priority: P2
  - Result:
    - config tests now pin default freshness threshold, explicit override, and
      too-low validation rejection for
      `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-217 Extend API regressions for compat freshness policy fields
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: QA/Test
  - Depends on: PRJ-216
  - Priority: P2
  - Result:
    - API health contract tests now pin freshness fields across no-attempt and
      attempted compat-route paths, including configured stale-threshold
      visibility
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-216 Add telemetry unit regressions for compat freshness helper states
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: QA/Test
  - Depends on: PRJ-215
  - Priority: P2
  - Result:
    - telemetry tests now pin freshness helper states
      (`no_attempts_recorded|fresh|stale`) and threshold validation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-215 Keep test fixture and request-level health wiring aligned with configurable freshness threshold
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-214
  - Priority: P2
  - Result:
    - API test settings fixture now exposes
      `event_debug_query_compat_stale_after_seconds` and health coverage pins
      configured threshold behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-214 Add explicit compat freshness-threshold setting to runtime config
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-213
  - Priority: P2
  - Result:
    - runtime settings now expose
      `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS` with default `86400` and
      bounded validation (`>=1`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-213 Expose compat freshness helper output through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-212
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now exposes stale-threshold, last-attempt age,
      and freshness state fields derived from compat telemetry snapshot
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-212 Add shared compat freshness helper from telemetry snapshot
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-211
  - Priority: P2
  - Result:
    - debug compat core now derives freshness posture from
      `last_attempt_at` with explicit stale threshold and state mapping
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-211 Derive compat freshness signal slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-210
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on explicit compat-route
      freshness posture for migration-window interpretation
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-210 Sync compat recent-window configurability slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-209
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat recent
      window configurability as complete through `PRJ-210`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-209 Document compat recent-window setting in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Product Docs
  - Depends on: PRJ-208
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now include
      `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` semantics
  - Validation:
    - docs sync review

- [x] PRJ-208 Document compat recent-window setting in architecture and ops/local docs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Product Docs
  - Depends on: PRJ-207
  - Priority: P3
  - Result:
    - architecture, local-development, and ops docs now include
      `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` defaults and purpose
  - Validation:
    - docs sync review

- [x] PRJ-207 Extend API regressions for configured compat recent-window behavior
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: QA/Test
  - Depends on: PRJ-206
  - Priority: P2
  - Result:
    - API tests now pin that configured recent window size bounds rolling
      compat counters and trend rates/state outputs
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-206 Extend config regressions for compat recent-window defaults and bounds
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: QA/Test
  - Depends on: PRJ-205
  - Priority: P2
  - Result:
    - config tests now pin default value, explicit override, and too-low
      validation failure for compat recent-window setting
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-205 Extend telemetry unit regressions for configurable recent-window size
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: QA/Test
  - Depends on: PRJ-204
  - Priority: P2
  - Result:
    - telemetry unit tests now pin custom recent-window behavior and reject
      non-positive window values
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-204 Add explicit compat recent-window setting to runtime config
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Backend Builder
  - Depends on: PRJ-203
  - Priority: P2
  - Result:
    - runtime settings now expose `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW`
      with default `20` and bounded validation (`>=1`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-203 Wire compat recent-window setting into lifespan telemetry initialization
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Backend Builder
  - Depends on: PRJ-202
  - Priority: P2
  - Result:
    - app lifespan now initializes debug compat telemetry with configured
      recent-window size
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-202 Keep request-level telemetry fallback aligned with configured recent-window setting
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Backend Builder
  - Depends on: PRJ-201
  - Priority: P2
  - Result:
    - request-level telemetry fallback now respects configured recent-window
      size from app settings
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_debug_compat_telemetry.py`

- [x] PRJ-201 Derive compat recent-window configurability slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-200
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on configurable rolling
      window size for compat telemetry trends
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-200 Sync compat rolling-trend refinement slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-199
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat
      rolling-trend refinement as complete through `PRJ-200`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-199 Document rolling-trend refinement semantics in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Product Docs
  - Depends on: PRJ-198
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now describe rolling trend as
      release-window signal and attempt-based migration posture semantics
  - Validation:
    - docs sync review

- [x] PRJ-198 Document rolling-trend fields and states in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Product Docs
  - Depends on: PRJ-197
  - Priority: P3
  - Result:
    - architecture and ops docs now include recent trend fields/states and
      operator interpretation guidance
  - Validation:
    - docs sync review

- [x] PRJ-197 Extend API regressions for rolling-trend mixed/disabled states
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: QA/Test
  - Depends on: PRJ-196
  - Priority: P2
  - Result:
    - API tests now pin rolling trend state outputs across mixed and disabled
      compat-route scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-196 Extend health contract regressions for rolling-window telemetry fields
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: QA/Test
  - Depends on: PRJ-195
  - Priority: P2
  - Result:
    - health endpoint policy tests now pin rolling telemetry counters and
      recent trend outputs
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-195 Add telemetry unit regressions for rolling-trend helper states
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: QA/Test
  - Depends on: PRJ-194
  - Priority: P2
  - Result:
    - telemetry unit tests now pin rolling trend helper behavior for
      `no_recent_attempts|mixed|compat_disabled` states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-194 Extend compat telemetry snapshot with rolling-window counters
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Backend Builder
  - Depends on: PRJ-193
  - Priority: P2
  - Result:
    - compat telemetry snapshot now exposes recent window size and
      recent allowed/blocked counters for trend derivation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py`

- [x] PRJ-193 Expose rolling-trend helper output through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Backend Builder
  - Depends on: PRJ-192
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now exposes recent attempts/rates/state fields
      from one shared helper
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-192 Add shared rolling-trend helper for compat telemetry snapshots
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Backend Builder
  - Depends on: PRJ-191
  - Priority: P2
  - Result:
    - debug compat core now provides a reusable rolling-trend helper that maps
      recent rates into operator states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-191 Derive compat rolling-trend refinement slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-190
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on rolling-window compat
      trend visibility for migration monitoring
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-190 Sync compat recent-trend slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-189
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat
      recent-trend signaling as complete through `PRJ-190`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-189 Document compat recent-trend fields in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Product Docs
  - Depends on: PRJ-188
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now describe rolling-window compat
      trend fields exposed by health policy
  - Validation:
    - docs sync review

- [x] PRJ-188 Document compat recent-trend fields in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Product Docs
  - Depends on: PRJ-187
  - Priority: P3
  - Result:
    - architecture and ops docs now include
      `event_debug_query_compat_recent_attempts_total`,
      `event_debug_query_compat_recent_allow_rate`,
      `event_debug_query_compat_recent_block_rate`, and
      `event_debug_query_compat_recent_state`
  - Validation:
    - docs sync review

- [x] PRJ-187 Extend API regressions for compat recent-trend state outputs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: QA/Test
  - Depends on: PRJ-186
  - Priority: P2
  - Result:
    - API tests now pin recent-trend state behavior in disabled and mixed
      compat attempt scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-186 Extend health contract regressions for recent-trend fields
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: QA/Test
  - Depends on: PRJ-185
  - Priority: P2
  - Result:
    - health endpoint policy tests now pin recent attempts/rates/state fields
      in default and production snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-185 Add telemetry unit regressions for recent-trend helper states
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: QA/Test
  - Depends on: PRJ-184
  - Priority: P2
  - Result:
    - telemetry unit tests now pin `no_recent_attempts`, `mixed`, and
      `compat_disabled` recent-state mapping
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-184 Extend telemetry snapshot with rolling-window counters
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Backend Builder
  - Depends on: PRJ-183
  - Priority: P2
  - Result:
    - compat telemetry snapshots now include rolling-window counters
      (`recent_window_size`, `recent_attempts_total`, `recent_allowed_total`,
      `recent_blocked_total`) for trend derivation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py`

- [x] PRJ-183 Expose compat recent-trend helper output through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Backend Builder
  - Depends on: PRJ-182
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now exposes recent attempts/rates/state via
      one shared recent-trend helper
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-182 Add shared compat recent-trend helper from telemetry snapshot
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Backend Builder
  - Depends on: PRJ-181
  - Priority: P2
  - Result:
    - debug compat core now derives rolling-window attempts/rates/state from
      telemetry snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-181 Derive compat recent-trend slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-180
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on rolling-window compat
      trend visibility for release-window migration monitoring
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-180 Sync compat-sunset readiness-boolean slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-179
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat sunset
      readiness boolean/reason signaling as complete through `PRJ-180`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-179 Document compat sunset readiness boolean/reason in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Product Docs
  - Depends on: PRJ-178
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now include explicit
      `event_debug_query_compat_sunset_ready` and
      `event_debug_query_compat_sunset_reason` semantics
  - Validation:
    - docs sync review

- [x] PRJ-178 Document compat sunset readiness boolean/reason in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Product Docs
  - Depends on: PRJ-177
  - Priority: P3
  - Result:
    - architecture and ops docs now describe machine-readable compat sunset
      readiness fields and reasons
  - Validation:
    - docs sync review

- [x] PRJ-177 Extend mixed allowed/blocked compat-route regressions for sunset readiness fields
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: QA/Test
  - Depends on: PRJ-176
  - Priority: P2
  - Result:
    - compat-route API regressions now pin readiness=false and migration-needed
      reason when compat attempts are observed
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-176 Extend health contract regressions for sunset readiness boolean/reason
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: QA/Test
  - Depends on: PRJ-175
  - Priority: P2
  - Result:
    - health endpoint policy regressions now pin
      `event_debug_query_compat_sunset_ready` and
      `event_debug_query_compat_sunset_reason` across default and production
      policy postures
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-175 Add unit regressions for compat attempts with zero allows
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: QA/Test
  - Depends on: PRJ-174
  - Priority: P2
  - Result:
    - telemetry unit tests now pin that compat attempts (even fully blocked)
      still require migration before disabling compatibility route
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-174 Align compat recommendation logic with observed attempt presence
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-173
  - Priority: P2
  - Result:
    - recommendation now treats any observed compat attempts as migration-needed
      instead of relying on allowed-count only
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py`

- [x] PRJ-173 Add shared compat sunset readiness boolean/reason helper outputs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-172
  - Priority: P2
  - Result:
    - debug compat core now emits machine-readable sunset decision fields based
      on recommendation state
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-172 Expose compat sunset readiness boolean/reason through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-171
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now includes
      `event_debug_query_compat_sunset_ready` and
      `event_debug_query_compat_sunset_reason`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-171 Derive compat sunset readiness-boolean slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-170
  - Priority: P2
  - Result:
    - next architecture-alignment slice now adds explicit machine-readable
      go/no-go sunset signal for compatibility debug route
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-170 Sync compat-sunset recommendation slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-169
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat-sunset
      recommendation signals as complete through `PRJ-170`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-169 Document compat-sunset recommendation signals in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Product Docs
  - Depends on: PRJ-168
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now describe compat allow/block
      rates and recommendation guidance fields exposed via `/health`
  - Validation:
    - docs sync review

- [x] PRJ-168 Document compat-sunset recommendation signals in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Product Docs
  - Depends on: PRJ-167
  - Priority: P3
  - Result:
    - architecture and ops docs now include
      `event_debug_query_compat_allow_rate`,
      `event_debug_query_compat_block_rate`, and
      `event_debug_query_compat_recommendation`
  - Validation:
    - docs sync review

- [x] PRJ-167 Extend compat-route blocked-path regressions for recommendation signals
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: QA/Test
  - Depends on: PRJ-166
  - Priority: P2
  - Result:
    - compat-route tests now pin blocked-path telemetry and recommendation
      posture when production keeps compat route disabled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-166 Extend health contract regressions for compat-sunset recommendation fields
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: QA/Test
  - Depends on: PRJ-165
  - Priority: P2
  - Result:
    - health endpoint tests now pin allow/block rates and recommendation output
      in default and production policy snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-165 Add unit regressions for compat-sunset recommendation helper behavior
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: QA/Test
  - Depends on: PRJ-164
  - Priority: P2
  - Result:
    - telemetry unit tests now pin recommendation behavior for disabled,
      no-traffic, and active-migration compat-route states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-164 Keep compat-route telemetry outcome classification aligned with debug access checks
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Backend Builder
  - Depends on: PRJ-163
  - Priority: P2
  - Result:
    - compat-route telemetry continues to classify allowed vs blocked outcomes
      after access checks, so recommendation inputs remain trustworthy
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-163 Expose compat-sunset rates and recommendation through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Backend Builder
  - Depends on: PRJ-162
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now includes
      `event_debug_query_compat_allow_rate`,
      `event_debug_query_compat_block_rate`, and
      `event_debug_query_compat_recommendation`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-162 Add shared compat-sunset recommendation helper from telemetry snapshots
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Backend Builder
  - Depends on: PRJ-161
  - Priority: P2
  - Result:
    - debug compat core now derives allow/block rates and recommendation from
      one shared helper fed by telemetry snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-161 Derive compat-sunset recommendation slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-160
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on decision-ready compat
      sunset guidance based on observable route usage signals
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-160 Sync query-compat sunset-readiness slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-159
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record query-compat
      sunset-readiness as complete through `PRJ-160`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-159 Document query-compat deprecation telemetry and headers in canonical docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Product Docs
  - Depends on: PRJ-158
  - Priority: P3
  - Result:
    - architecture, ops, local-dev, runtime-reality, and planning docs now
      describe compat-route deprecation headers and health telemetry surface
  - Validation:
    - docs sync review

- [x] PRJ-158 Add API regressions for compat-route telemetry tracking
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: QA/Test
  - Depends on: PRJ-157
  - Priority: P2
  - Result:
    - API tests now pin compat-route health telemetry counters for allowed and
      blocked attempts
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-157 Add API regressions for compat-route deprecation header contract
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: QA/Test
  - Depends on: PRJ-156
  - Priority: P2
  - Result:
    - API tests now pin `X-AION-Debug-Compat-Deprecated=true` on accepted
      compatibility route responses
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-156 Add unit regressions for debug query-compat telemetry contract
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: QA/Test
  - Depends on: PRJ-155
  - Priority: P2
  - Result:
    - dedicated telemetry unit tests now pin default and mutation behavior for
      compat-route counters and timestamp fields
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-155 Expose compat-route telemetry through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-154
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now includes
      `event_debug_query_compat_telemetry` with attempt/allow/block counters
      plus last-attempt timestamps
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-154 Track blocked compat-route attempts across policy and token rejections
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-153
  - Priority: P2
  - Result:
    - compat-route telemetry now records blocked attempts for policy-denied and
      debug-access-denied request outcomes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-153 Track successful compat-route debug responses
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-152
  - Priority: P2
  - Result:
    - compat-route telemetry now records allowed attempts only after successful
      debug response generation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-152 Add explicit in-process telemetry contract for debug query-compat usage
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-151
  - Priority: P2
  - Result:
    - `DebugQueryCompatTelemetry` now owns compat-route usage counters and
      timestamp snapshots for migration sunset observability
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-151 Derive query-compat sunset-readiness slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-150
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on measurable compat-route
      sunset readiness (deprecation signaling and usage telemetry)
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-150 Sync query-compat hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-149
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record query-compat
      hardening as complete through `PRJ-150`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`

- [x] PRJ-149 Document query-compat policy posture in architecture, ops, and planning docs
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Product Docs
  - Depends on: PRJ-148
  - Priority: P3
  - Result:
    - env/config, local-dev, ops, runtime-reality, and open-decisions docs now
      describe `EVENT_DEBUG_QUERY_COMPAT_ENABLED`, production-default disabled
      compat route posture, and strict mismatch visibility for
      `event_debug_query_compat_enabled=true`
  - Validation:
    - docs sync review

- [x] PRJ-148 Add production API regression for explicit query-compat opt-in behavior
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-147
  - Priority: P2
  - Result:
    - API tests now pin that production `POST /event?debug=true` works only
      when compat route is explicitly enabled and token policy is satisfied
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-147 Add production API regression for default query-compat route denial
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-146
  - Priority: P2
  - Result:
    - API tests now pin production default behavior where compatibility
      `POST /event?debug=true` is blocked unless explicitly enabled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-146 Extend health-policy regressions for query-compat mismatch visibility
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-145
  - Priority: P2
  - Result:
    - health endpoint tests now pin explicit compat-route mismatch list/count
      behavior in production policy snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-145 Extend startup strict-block regressions for query-compat mismatch posture
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-144
  - Priority: P2
  - Result:
    - startup strict-policy tests now pin violation payloads that include
      `event_debug_query_compat_enabled=true` in multi-mismatch production
      scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-144 Extend runtime-policy regressions for query-compat and token-missing combined posture
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-143
  - Priority: P2
  - Result:
    - runtime-policy tests now pin combined mismatch list/count when production
      debug route keeps query-compat enabled and token policy is unmet
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-143 Route production query-compat mismatch detection through shared helper
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-142
  - Priority: P2
  - Result:
    - production mismatch detection now calls one helper for compat-route
      posture so mismatch semantics remain centralized
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-142 Add shared helper for production query-compat mismatch ownership
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-141
  - Priority: P2
  - Result:
    - runtime policy now includes explicit helper ownership for production
      query-compat mismatch detection
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-141 Derive production query-compat hardening slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-140
  - Priority: P2
  - Result:
    - next architecture-alignment slice now resolves policy-observability and
      test-coverage gaps for production debug query-compat route posture
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-140 Sync strict-token-mismatch hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-139
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record strict token
      mismatch hardening as complete through `PRJ-140`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`

- [x] PRJ-139 Update open decisions and runtime reality for strict token-missing mismatch posture
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Product Docs
  - Depends on: PRJ-138
  - Priority: P3
  - Result:
    - planning and runtime-reality docs now explicitly capture
      `event_debug_token_missing=true` strict mismatch behavior and posture
  - Validation:
    - docs sync review

- [x] PRJ-138 Document strict token-missing mismatch semantics in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Product Docs
  - Depends on: PRJ-137
  - Priority: P3
  - Result:
    - architecture and ops docs now include strict mismatch examples that cover
      missing debug-token policy posture in production
  - Validation:
    - docs sync review

- [x] PRJ-137 Extend health mismatch regressions for strict token-missing policy
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-136
  - Priority: P2
  - Result:
    - API health tests now pin production mismatch list/count with
      `event_debug_token_missing=true` where applicable
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-136 Extend startup strict-block regressions for token-missing mismatch
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-135
  - Priority: P2
  - Result:
    - startup strict-policy tests now pin error/log violation payloads that
      include `event_debug_token_missing=true` in multi-mismatch scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-135 Extend runtime-policy mismatch regressions for token-missing cases
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-134
  - Priority: P2
  - Result:
    - runtime-policy tests now pin mismatch list/count behavior when production
      debug token is required but not configured
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-134 Include production token-missing state in policy mismatch count helpers
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-133
  - Priority: P2
  - Result:
    - mismatch count and strict readiness now include token-missing production
      posture through one shared mismatch owner
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-133 Add explicit production token-missing mismatch entry
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-132
  - Priority: P2
  - Result:
    - production policy mismatch output now emits
      `event_debug_token_missing=true` when debug exposure is enabled in
      production and token requirement mode is active without a configured token
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-132 Add shared helper for production debug token-missing detection
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-131
  - Priority: P2
  - Result:
    - runtime policy now has explicit helper ownership for
      token-missing detection in production debug posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-131 Derive strict-rollout token-missing hardening slice from open decisions
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-130
  - Priority: P2
  - Result:
    - next architecture-alignment slice now resolves strict-rollout gap where
      production debug token-missing posture was visible but not part of policy
      mismatch counts
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-130 Sync production debug posture hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-129
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record production debug
      posture hardening as complete through `PRJ-130`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`

- [x] PRJ-129 Update open decisions and implementation reality for debug posture signals
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Product Docs
  - Depends on: PRJ-128
  - Priority: P3
  - Result:
    - planning and implementation docs now reflect `debug_access_posture` and
      `debug_token_policy_hint`, including startup warning behavior for relaxed
      token requirement mode
  - Validation:
    - docs sync review

- [x] PRJ-128 Document debug posture signals in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Product Docs
  - Depends on: PRJ-127
  - Priority: P3
  - Result:
    - architecture and operations docs now include
      `debug_access_posture|debug_token_policy_hint` as operator-visible
      runtime policy signals
  - Validation:
    - docs sync review

- [x] PRJ-127 Add startup warning regression for relaxed production token requirement
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: QA/Test
  - Depends on: PRJ-126
  - Priority: P2
  - Result:
    - startup policy tests now pin warning behavior when production debug is
      enabled and `PRODUCTION_DEBUG_TOKEN_REQUIRED=false`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-126 Add runtime-policy snapshot regressions for debug posture and hints
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: QA/Test
  - Depends on: PRJ-125
  - Priority: P2
  - Result:
    - runtime-policy tests now pin `debug_access_posture` and
      `debug_token_policy_hint` across disabled, token-gated, missing-token,
      and open-no-token states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-125 Extend health endpoint regressions for debug posture signals
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: QA/Test
  - Depends on: PRJ-124
  - Priority: P2
  - Result:
    - `/health.runtime_policy` tests now pin
      `debug_access_posture|debug_token_policy_hint` and production token
      requirement modes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-124 Add relaxed-mode production debug warning in startup policy logs
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Backend Builder
  - Depends on: PRJ-123
  - Priority: P2
  - Result:
    - startup logging now emits explicit warning when production debug is
      enabled with token requirement mode disabled and no configured token
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-123 Expose debug posture and hint fields in runtime policy snapshot
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Backend Builder
  - Depends on: PRJ-122
  - Priority: P2
  - Result:
    - runtime policy snapshot now emits `debug_access_posture` and
      `debug_token_policy_hint` for operator-visible debug hardening posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-122 Add shared debug token policy hint helper
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Backend Builder
  - Depends on: PRJ-121
  - Priority: P2
  - Result:
    - runtime policy now exposes one shared helper for concise debug token
      hardening guidance (`debug_token_policy_hint`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-121 Add shared debug access posture helper
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Backend Builder
  - Depends on: PRJ-120
  - Priority: P2
  - Result:
    - runtime policy now models explicit debug access posture
      (`disabled|token_gated|production_token_required_missing|open_no_token`)
      for debug route policy diagnostics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-120 Sync production-debug-token hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-119
  - Priority: P2
  - Result:
    - task board, project state, and iteration planning now record completion
      through `PRJ-120` for production debug-token hardening
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-119 Document production debug-token policy in operations and local docs
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Product Docs
  - Depends on: PRJ-118
  - Priority: P3
  - Result:
    - runtime ops and local development docs now describe
      `PRODUCTION_DEBUG_TOKEN_REQUIRED` and its production behavior
  - Validation:
    - docs sync review

- [x] PRJ-118 Document production debug-token env contract in architecture docs
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Product Docs
  - Depends on: PRJ-117
  - Priority: P3
  - Result:
    - canonical env/config docs now include `PRODUCTION_DEBUG_TOKEN_REQUIRED`
      and related `/health.runtime_policy` visibility
  - Validation:
    - docs sync review

- [x] PRJ-117 Add startup-policy logging regression for disabled token-requirement mode
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-116
  - Priority: P2
  - Result:
    - runtime-policy startup logging tests now pin behavior when production
      token requirement is explicitly disabled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-116 Extend runtime-policy snapshot regressions for production token policy signal
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-115
  - Priority: P2
  - Result:
    - runtime-policy tests now pin `production_debug_token_required` snapshot
      behavior across production and non-production cases
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-115 Add API-route regressions for production debug-token enforcement
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-114
  - Priority: P2
  - Result:
    - API tests now pin production behavior for debug endpoints when no debug
      token is configured and requirement mode is enabled/disabled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-114 Enforce production debug-token requirement in debug route access guard
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-113
  - Priority: P2
  - Result:
    - debug access guard now rejects production debug payload access when debug
      exposure is enabled and token requirement mode is enabled without a
      configured token
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-113 Expose production debug-token policy signal in runtime policy snapshot
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-112
  - Priority: P2
  - Result:
    - runtime policy snapshot now reports
      `production_debug_token_required` for operator-visible policy posture
      through `/health`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-112 Add production debug-token requirement helper to runtime policy core
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-111
  - Priority: P2
  - Result:
    - runtime policy now has an explicit shared helper for production
      debug-token requirement mode with safe defaults
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-111 Add explicit production debug-token requirement setting
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-110
  - Priority: P2
  - Result:
    - runtime config now exposes `PRODUCTION_DEBUG_TOKEN_REQUIRED` (default
      `true`) as a first-class policy switch
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-110 Sync attention-config hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-109
  - Priority: P2
  - Result:
    - task board, project state, and iteration planning now record the
      attention-config hardening slice as completed through `PRJ-110`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_main_lifespan_policy.py tests/test_api_routes.py`

- [x] PRJ-109 Document attention tuning env vars in runtime ops runbook
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Product Docs
  - Depends on: PRJ-108
  - Priority: P3
  - Result:
    - runbook now documents optional attention tuning env vars for burst window
      and turn lifecycle cleanup thresholds
  - Validation:
    - docs sync review

- [x] PRJ-108 Document attention timing env contract in architecture config docs
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Product Docs
  - Depends on: PRJ-107
  - Priority: P3
  - Result:
    - canonical env/config doc now includes `ATTENTION_BURST_WINDOW_MS`,
      `ATTENTION_ANSWERED_TTL_SECONDS`, and `ATTENTION_STALE_TURN_SECONDS`
      including boundary semantics
  - Validation:
    - docs sync review

- [x] PRJ-107 Keep strict-lifespan regression fixtures compatible with attention settings
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: QA/Test
  - Depends on: PRJ-106
  - Priority: P2
  - Result:
    - strict-policy lifespan fixtures include explicit attention setting fields,
      preventing fixture drift after config-surface expansion
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py`

- [x] PRJ-106 Add attention-threshold validation regressions in config tests
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: QA/Test
  - Depends on: PRJ-105
  - Priority: P2
  - Result:
    - config tests now pin invalid attention threshold behavior (negative burst
      window, too-low answered TTL, stale threshold below answered TTL)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-105 Add default attention-config regression coverage
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: QA/Test
  - Depends on: PRJ-104
  - Priority: P2
  - Result:
    - default settings coverage now pins attention defaults:
      `burst_window_ms=120`, `answered_ttl=5.0`, `stale_turn=30.0`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-104 Make `/health` attention posture fully config-driven
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-103
  - Priority: P2
  - Result:
    - `/health.attention` now reflects live coordinator thresholds that are
      wired from runtime settings rather than startup defaults only
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-103 Wire attention timing settings into app lifespan coordinator setup
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-102
  - Priority: P2
  - Result:
    - app startup now initializes `AttentionTurnCoordinator` from settings
      values for burst window and TTL/stale thresholds
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py tests/test_api_routes.py`

- [x] PRJ-102 Add bounded validation for attention timing config
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-101
  - Priority: P2
  - Result:
    - settings validation now enforces non-negative burst window, minimum
      answered TTL, and stale threshold ordering vs answered TTL
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-101 Add explicit attention timing settings to runtime config
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-100
  - Priority: P2
  - Result:
    - runtime config now exposes first-class attention timing controls for
      burst coalescing and turn lifecycle cleanup
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_api_routes.py`

- [x] PRJ-100 Expose attention turn-assembly posture via `/health`
  - Status: DONE
  - Group: Attention Observability
  - Owner: Backend Builder
  - Depends on: PRJ-099
  - Priority: P2
  - Result:
    - `/health` now exposes an explicit `attention` snapshot with
      `burst_window_ms`, turn TTLs, and pending/claimed/answered counters so
      burst-coalescing posture is operator-visible
    - runtime turn-assembly behavior stays unchanged; this slice adds
      observability-only diagnostics and regression coverage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-099 Add explicit compatibility hint headers for `POST /event?debug=true`
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-098
  - Priority: P2
  - Result:
    - `POST /event?debug=true` now emits explicit compatibility headers
      (`X-AION-Debug-Compat`, `Link`) that point operators to
      `POST /event/debug` as the preferred internal debug route
    - compatibility behavior stays intact while migration intent is now
      machine-visible in API responses and route-level tests
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-098 Add explicit internal debug endpoint while preserving `/event?debug=true`
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-097
  - Priority: P2
  - Result:
    - runtime now exposes explicit `POST /event/debug` for internal full-runtime
      debug payload access, guarded by the same debug policy/token checks as
      `POST /event?debug=true`
    - public `POST /event` contract remains compact by default, while debug
      behavior is now available through a clear internal route
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-097 Add connector expansion and capability-discovery proposals
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-096
  - Priority: P1
  - Result:
    - reflection now derives explicit `suggest_connector_expansion` proposals
      from repeated unmet connector needs, and planning promotes accepted
      proposals into bounded `connector_capability_discovery_intent` outputs
    - connector capability-discovery outputs now remain suggestion-only through
      permission gates (`proposal_only_no_external_access`) and episode payload
      traces (`connector_expansion_update`) without self-authorized side effects
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_reflection_worker.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-096 Add connected-drive access contracts for cloud files and documents
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-095
  - Priority: P1
  - Result:
    - runtime now exposes explicit connected-drive domain intents with guarded
      read/suggest/mutate operation modes
    - planning and action contracts now include cloud-drive permission gates
      and non-side-effect connector payload traces (`drive_connector_update`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`

- [x] PRJ-095 Add external task-system adapter contracts for connected task apps
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Backend Builder
  - Depends on: PRJ-094
  - Priority: P1
  - Result:
    - planning and action contracts now expose explicit external task-system
      sync intents (`external_task_sync`) without provider-specific coupling
    - runtime now carries connector permission gate outputs so external task
      adapters stay authorization-bound and action-layer controlled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-094 Add calendar integration boundary and scheduling-intent contract
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Backend Builder
  - Depends on: PRJ-093
  - Priority: P1
  - Result:
    - planning and action contracts now expose explicit calendar scheduling
      intents (`calendar_scheduling`) with mutate/read permission semantics
    - calendar connector suggestions remain proposal/intention outputs until
      action-layer permission gates allow execution
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-093 Define the external connector contract, capability model, and permission gates
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-092
  - Priority: P1
  - Result:
    - runtime contracts now include connector capability and permission-gate
      outputs with explicit read/suggest/mutate operation modes
    - planning outputs now carry connector permission gates as first-class
      contracts instead of ad hoc integration assumptions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-092 Add regression coverage for dual-loop coordination and batched conversation handling
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-091
  - Priority: P1
  - Result:
    - regression coverage now pins subconscious proposal persistence/handoff,
      proactive attention gating, and burst-turn runtime behavior
    - contract-level tests now fail fast when conscious/subconscious ownership
      or connector permission boundaries drift
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-091 Separate conscious wakeups from subconscious cadence
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-090
  - Priority: P1
  - Result:
    - subconscious reflection now persists proposal candidates while conscious
      planning/runtime explicitly accepts, defers, or discards them
    - proactive scheduler wakeups now pass through explicit attention-gate
      checks, keeping subconscious cadence non-user-facing
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-090 Add an attention gate for proactive delivery
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-089
  - Priority: P1
  - Result:
    - proactive scheduler events now evaluate an explicit attention gate
      (quiet hours, cooldown, unanswered backlog) before delivery planning
    - planning/runtime now defer proactive delivery through a typed
      `respect_attention_gate` branch when gate constraints block outreach
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-089 Add read-only tool and research policy for subconscious execution
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-088
  - Priority: P1
  - Result:
    - subconscious proposal records now carry explicit `research_policy` and
      `allowed_tools` fields with `read_only` as the normalized default
    - reflection/runtime proposal flow now preserves read-only tool boundaries
      so subconscious research cannot bypass conscious action ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-088 Add subconscious proposal persistence and conscious promotion rules
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-087
  - Priority: P1
  - Result:
    - repository now persists subconscious proposals in a dedicated
      `aion_subconscious_proposal` table with pending/accepted/deferred/discarded
      status tracking
    - planning/runtime now record conscious proposal handoff decisions and
      resolve pending proposals only through conscious stage ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-087 Define internal planning-state ownership and external productivity boundaries
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-086
  - Priority: P1
  - Result:
    - architecture/runtime contracts now keep internal goals/tasks as core
      planning state while external systems are treated as permissioned
      connector projections
    - docs and graph-state contracts now separate internal planning ownership
      from external connector capability and permission boundaries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-086 Implement message burst coalescing and pending-turn ownership
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-085
  - Priority: P1
  - Result:
    - Telegram burst events now pass through an attention-turn coordinator that
      coalesces rapid pending messages into one assembled turn payload before
      foreground runtime execution
    - pending/claimed/answered ownership now gates duplicate webhook events so
      duplicate updates and already-claimed turn events return queued no-op
      responses instead of triggering duplicate runtime replies
    - `/event` now returns explicit queue metadata for non-owner burst events,
      while owner events keep the existing public runtime response contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-085 Define the attention inbox, turn-assembly contract, and proposal handoff model
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-084
  - Priority: P1
  - Result:
    - runtime graph-state contracts now define explicit attention inbox,
      turn-assembly, subconscious proposal, and proposal-handoff model surfaces
      for conscious/subconscious coordination
    - architecture and implementation docs now align on one contract vocabulary
      for attention items, pending turn ownership, and conscious proposal
      decisions
    - the contract boundary now exists without introducing hidden side effects
      or bypassing conscious action ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_state_contract.py`

- [x] PRJ-084 Add proactive delivery controls, throttling, and regression coverage
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-083
  - Priority: P1
  - Result:
    - proactive planning now applies explicit delivery guardrails for user opt-in,
      recent outbound limits, unanswered proactive limits, and delivery-target
      presence before any outreach is executed
    - action execution now enforces proactive delivery guard outputs as a
      defensive boundary, preventing proactive delivery when guardrails defer
      outreach
    - proactive scheduler events can now preserve `chat_id` delivery targets,
      and proactive scheduler replies route through Telegram when a delivery
      target is available
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- [x] PRJ-083 Add a proactive decision engine with interruption guardrails
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-082
  - Priority: P1
  - Result:
    - scheduler proactive payloads now normalize explicit trigger/importance/urgency
      and user-context guardrail fields in one shared contract owner
    - proactive decision scoring now runs through a dedicated engine with bounded
      interruption cost evaluation, returning typed proactive decision output
    - motivation and planning now consume proactive decisions to either defer
      outreach or build typed proactive warning/reminder/insight-style plans
      without bypassing existing action boundaries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-082 Add scheduled reflection and maintenance cadence
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-081
  - Priority: P1
  - Result:
    - scheduler worker now runs reflection and maintenance cadence independently
      from user-event turns, with explicit runtime guardrails for
      `in_process|deferred` reflection modes
    - `/health` now exposes scheduler runtime posture (`enabled`, `running`,
      cadence intervals, and latest tick summaries) so cadence wiring is
      observable during operations
    - cadence intervals are now clamped through scheduler contract rules so
      runtime configuration stays bounded by shared scheduler limits
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_scheduler_contracts.py tests/test_api_routes.py tests/test_config.py tests/test_reflection_worker.py tests/test_main_lifespan_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-081 Make the reflection runtime ready for scheduled and out-of-process execution
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-080
  - Priority: P1
  - Result:
    - runtime now persists reflection tasks even when no in-process worker is attached,
      so deferred/scheduler/out-of-process reflection execution remains durable
    - reflection runtime mode is now explicit (`in_process|deferred`) and health
      semantics respect mode-aware worker expectations
    - reflection worker now exposes one-shot pending-task drain execution
      (`run_pending_once`) so external schedulers/workers can process queue state
      without long-running in-process loop ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

- [x] PRJ-080 Define scheduler events, cadence rules, and runtime boundaries
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-079
  - Priority: P1
  - Result:
    - scheduler-originated events now have explicit runtime normalization contracts
      (`source=scheduler`, scoped subsource rules, payload normalization)
    - runtime configuration now exposes explicit cadence boundaries for scheduler,
      reflection, maintenance, and proactive loops
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_event_normalization.py tests/test_scheduler_contracts.py`

- [x] PRJ-079 Make runtime relation-aware in retrieval, context, role, planning, and expression
  - Status: DONE
  - Group: Relation System
  - Owner: Backend Builder
  - Depends on: PRJ-078
  - Priority: P1
  - Result:
    - runtime now loads high-confidence relation records into graph/runtime state
      and maps relation cues into context, role, planning, and expression behavior
    - relation cues now influence collaboration/support stance in a bounded,
      test-covered way
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_role_agent.py tests/test_planning_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-078 Extend reflection to derive and maintain relation updates
  - Status: DONE
  - Group: Relation System
  - Owner: Backend Builder
  - Depends on: PRJ-077
  - Priority: P1
  - Result:
    - reflection now derives relation signals from episodic interaction evidence
      and persists scoped relation updates with confidence and provenance metadata
    - relation update events are observable through dedicated reflection log entries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- [x] PRJ-077 Define the relation data model, scopes, and repository surface
  - Status: DONE
  - Group: Relation System
  - Owner: Backend Builder
  - Depends on: PRJ-076
  - Priority: P1
  - Result:
    - repository now has a dedicated scoped relation model (`aion_relation`) with
      confidence, evidence count, decay rate, and source metadata
    - repository APIs now support upsert and retrieval of relations independently
      from generic conclusions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_schema_baseline.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

- [x] PRJ-076 Add semantic retrieval evaluation and observability
  - Status: DONE
  - Group: Semantic Retrieval Infrastructure
  - Owner: Backend Builder
  - Depends on: PRJ-075
  - Priority: P1
  - Result:
    - hybrid retrieval diagnostics now expose lexical/vector candidate counts
      and similarity/overlap scoring signals for runtime observability
    - runtime memory-load logging now surfaces hybrid retrieval summaries
      (`hybrid_vector_hits`, `hybrid_lexical_hits`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_logging.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`

- [x] PRJ-075 Implement hybrid retrieval across episodic, semantic, and affective memory
  - Status: DONE
  - Group: Semantic Retrieval Infrastructure
  - Owner: Backend Builder
  - Depends on: PRJ-074
  - Priority: P1
  - Result:
    - repository now exposes hybrid retrieval that blends episodic, semantic,
      and affective memory candidates using lexical overlap and vector similarity
    - runtime memory-load now consumes the hybrid bundle with deterministic
      embedding fallback when provider embeddings are unavailable
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`

- [x] PRJ-074 Add pgvector-backed storage and migration scaffolding
  - Status: DONE
  - Group: Semantic Retrieval Infrastructure
  - Owner: DB/Migrations
  - Depends on: PRJ-073
  - Priority: P1
  - Result:
    - schema now includes `aion_semantic_embedding` with PostgreSQL `vector`
      extension scaffolding and non-Postgres JSON fallback compatibility
    - migration path now includes pgvector extension creation and semantic index baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_memory_repository.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

- [x] PRJ-073 Define the embedding and semantic retrieval contract
  - Status: DONE
  - Group: Semantic Retrieval Infrastructure
  - Owner: Backend Builder
  - Depends on: PRJ-072
  - Priority: P1
  - Result:
    - shared contracts now define semantic source kinds, embedding records,
      retrieval query shape, and similarity hit/result payloads
    - deterministic embedding and cosine helper modules now provide a stable
      fallback baseline for retrieval tests and offline environments
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_semantic_contracts.py tests/test_memory_repository.py tests/test_schema_baseline.py`

- [x] PRJ-072 Add optional LangChain utility wrappers only where they reduce code
  - Status: DONE
  - Group: Graph Orchestration Adoption
  - Owner: Backend Builder
  - Depends on: PRJ-071
  - Priority: P1
  - Result:
    - OpenAI prompt construction now uses optional LangChain prompt templates
      behind a compatibility wrapper and remains fully functional without LangChain
    - LangChain support is now opt-in utility surface, not orchestration core
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_openai_prompting.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-071 Migrate the foreground runtime orchestration to LangGraph
  - Status: DONE
  - Group: Graph Orchestration Adoption
  - Owner: Backend Builder
  - Depends on: PRJ-070
  - Priority: P1
  - Result:
    - foreground cognitive stages now run through LangGraph (`StateGraph`)
      while preserving stage boundaries, stage-level logging, and public/runtime
      contracts
    - runtime still loads baseline state and performs memory/reflection follow-up
      outside graph execution, keeping migration incremental and regression-safe
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py tests/test_graph_state_contract.py tests/test_graph_stage_adapters.py`

- [x] PRJ-069 Define the LangGraph migration boundary and compatibility contract
  - Status: DONE
  - Group: Graph Orchestration Adoption
  - Owner: Planner
  - Depends on: PRJ-068
  - Priority: P1
  - Result:
    - runtime now exposes an explicit graph compatibility state contract
      (`GraphRuntimeState`) plus conversion helpers from/to foreground
      `RuntimeResult`
    - canonical/runtime docs now define a contract-pinned migration boundary
      so LangGraph rollout can proceed incrementally without a big-bang rewrite
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_state_contract.py`
- [x] PRJ-070 Introduce graph-compatible state adapters around current stage modules
  - Status: DONE
  - Group: Graph Orchestration Adoption
  - Owner: Backend Builder
  - Depends on: PRJ-069
  - Priority: P1
  - Result:
    - graph-compatible stage adapters now wrap perception, affective
      assessment, context, motivation, role, planning, expression, and action
      without changing the current orchestrator path
    - action-delivery shaping now uses one shared helper reusable by current
      orchestrator and future graph nodes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_stage_adapters.py tests/test_runtime_pipeline.py`

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
