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
- The planning queue is complete through `PRJ-231`.
- No `READY` PRJ slice is currently registered; derive the next smallest slice
  from `docs/planning/open-decisions.md` and sync it with the board before
  implementation.
- Additional architecture-alignment work should be appended after that queue so
  the backlog stays explicitly open for later discovery instead of pretending
  the plan is complete.

## READY

- [ ] (none)

## BACKLOG

- [ ] (none)

## FUTURE

- [ ] (none)

## IN_PROGRESS

- [ ] (none)

## BLOCKED

- [ ] (none)

## REVIEW

- [ ] (none)

## DONE

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
