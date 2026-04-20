# LEARNING_JOURNAL

Purpose: keep a compact memory of recurring execution pitfalls and verified
fixes for this repository.

## Update Rules

- Add or update an entry when a failure pattern is reproducible or documented.
- Prefer updating an existing entry over creating duplicates.
- Keep entries in English and free of secrets.
- Apply the new guardrail in the same task where the learning is captured.

## Entry Template

```markdown
### YYYY-MM-DD - Short Title
- Context:
- Symptom:
- Root cause:
- Guardrail:
- Preferred pattern:
- Avoid:
- Evidence:
```

## Entries

### 2026-04-21 - App-lifespan debug smoke can fail early when external DB DNS is unreachable
- Context:
  - validating manual `/internal/event/debug` behavior against full app
    lifespan startup in this workspace.
- Symptom:
  - app startup fails before request handling with
    `socket.gaierror: [Errno 11001] getaddrinfo failed`.
- Root cause:
  - current runtime DB target resolves through an external host that is not
    reachable/resolvable from this execution environment.
- Guardrail:
  - for endpoint-boundary validation slices, use route/runtime harness tests as
    the primary evidence path when full app lifespan depends on unavailable
    external DB DNS.
- Preferred pattern:
  - keep fail-boundary checks in focused API/runtime tests
  - run app-lifespan smoke only when DB host resolution is confirmed or
    `DATABASE_URL` is explicitly pointed to a reachable local target
  - record blocked manual smoke attempts explicitly in task evidence
- Avoid:
  - treating blocked full-app startup as proof that endpoint behavior regressed
  - claiming manual ingress smoke as passed when startup never reaches request
    handling
- Evidence:
  - `.\.venv\Scripts\python -` app-lifespan TestClient smoke attempt during
    `PRJ-338` failed at startup with `socket.gaierror [Errno 11001]`.
  - `tests/test_api_routes.py::test_internal_event_debug_endpoint_returns_fail_action_result_without_500`
  - `tests/test_runtime_pipeline.py::test_runtime_pipeline_degrades_telegram_delivery_exception_to_fail_action_result`

### 2026-04-20 - Memory is not validated if persistence never changes later behavior
- Context:
  - architectural memory work can look complete in contracts, repository
    writes, and health/debug surfaces while still failing to influence later
    turns in practice.
- Symptom:
  - the system appears to "have memory" in implementation terms, but follow-up
    responses remain generic and do not reuse the earlier stored context.
- Root cause:
  - coverage focused on write/read mechanics and contract shape without enough
    scenario-level validation that retrieved memory changes context, planning,
    or expression over time.
- Guardrail:
  - for memory-sensitive work, require behavior-driven tests that prove
    `write -> retrieve -> influence -> delayed recall`, not just persistence or
    retrieval in isolation.
- Preferred pattern:
  - validate through internal debug mode plus user-simulation scenarios
  - record whether retrieved memory appears in context and changes the later
    response
  - treat missing behavioral influence as a real failure even when storage
    mechanics pass
- Avoid:
  - calling memory "done" because DB rows, summaries, or retrieval counts exist
  - relying only on unit/contract tests for cognitive correctness
- Evidence:
  - `docs/architecture/29_runtime_behavior_testing.md`
  - `docs/engineering/testing.md`
  - `docs/planning/open-decisions.md`
  - `.codex/context/TASK_BOARD.md`

### 2026-04-20 - Windows runtime may not provide bash for shell-script smoke checks
- Context:
  - validating release smoke script alignment on Windows-first execution
    slices.
- Symptom:
  - running `./scripts/run_release_smoke.sh` fails immediately with
    `/bin/bash` not found in this environment.
- Root cause:
  - this workspace runtime does not guarantee WSL/Git-Bash availability even
    when `.sh` tooling is present in the repository.
- Guardrail:
  - treat `.ps1` as the executable validation path in this runtime and record
    when `.sh` execution is blocked by missing bash.
- Preferred pattern:
  - validate behavior through `scripts/run_release_smoke.ps1`
  - keep `.sh` changes symmetric with `.ps1` logic
  - document inability to execute bash path in task evidence
- Avoid:
  - assuming `.sh` scripts are runnable on every Windows-hosted Codex session
  - marking bash-path runtime verification as passed without executable shell
    support
- Evidence:
  - `PRJ-303` smoke alignment checks in this workspace showed
    `/bin/bash` missing while the PowerShell smoke script executed.

### 2026-04-19 - Keep compat sunset decision separate from activity posture
- Context:
  - compat telemetry now exposes both strict sunset-ready outputs and
    migration-window activity posture outputs.
- Symptom:
  - operators can lose clear go/no-go semantics when stale-vs-recent traffic
    diagnostics overwrite strict sunset readiness fields.
- Root cause:
  - mixing decision fields and monitoring posture fields into one contract
    surface.
- Guardrail:
  - keep sunset decision contract stable
    (`event_debug_query_compat_sunset_ready|reason`) and expose activity as
    separate posture fields
    (`event_debug_query_compat_activity_state|hint`).
- Preferred pattern:
  - decision fields for automation gates
  - activity posture fields for migration-window triage
- Avoid:
  - deriving strict disable readiness directly from fresh/stale posture fields.
- Evidence:
  - `app/core/debug_compat.py`
  - `app/api/routes.py`
  - `tests/test_debug_compat_telemetry.py`
  - `tests/test_api_routes.py`

### 2026-04-19 - Avoid `or` fallbacks when numeric config values can be zero
- Context:
  - request-level compat telemetry fallback reads configured rolling-window size
    from app settings.
- Symptom:
  - invalid numeric config can be silently replaced by default and skip expected
    validation failure paths.
- Root cause:
  - using `value or default` on numeric values treats `0` as missing.
- Guardrail:
  - read numeric config with explicit default at source (`getattr(..., default)`)
    and pass value through validation logic without boolean coercion.
- Preferred pattern:
  - use explicit `int(getattr(settings, "field", default))`
  - keep validation centralized in settings/model constructors
- Avoid:
  - `or default` for numeric config fallback paths.
- Evidence:
  - `app/api/routes.py`
  - `app/core/config.py`
  - `tests/test_config.py`

### 2026-04-19 - Keep sunset readiness and rolling trend signals separate
- Context:
  - health policy now exposes both all-time compat sunset posture and
    rolling-window compat trend diagnostics.
- Symptom:
  - rollout decisions can drift when rolling trend state is treated as
    equivalent to sunset readiness.
- Root cause:
  - trend metrics describe recent behavior only, while readiness depends on
    stricter migration posture rules.
- Guardrail:
  - keep separate fields for all-time sunset decision
    (`event_debug_query_compat_sunset_ready|reason`) and rolling trend
    diagnostics (`event_debug_query_compat_recent_*`).
- Preferred pattern:
  - use rolling trend for monitoring release windows
  - use sunset readiness fields for go/no-go automation
- Avoid:
  - deriving disable decisions from recent trend state alone.
- Evidence:
  - `app/core/debug_compat.py`
  - `app/api/routes.py`
  - `tests/test_debug_compat_telemetry.py`
  - `tests/test_api_routes.py`

### 2026-04-19 - Compat sunset recommendations should be based on attempts, not successful responses
- Context:
  - runtime now uses compat-route telemetry to guide whether
    `POST /event?debug=true` can be safely disabled.
- Symptom:
  - recommendation can incorrectly report "no compat traffic" when all observed
    compat attempts were blocked (for example token/policy failures).
- Root cause:
  - recommendation logic depended on `allowed_total` instead of total attempts.
- Guardrail:
  - compatibility sunset recommendation must treat any observed compat attempts
    as migration-needed, even if those attempts are blocked.
- Preferred pattern:
  - derive recommendation from `attempts_total` and compat-enabled posture;
    keep allow/block rates as supporting diagnostics.
- Avoid:
  - using successful compat responses as the only signal of active compat usage.
- Evidence:
  - `app/core/debug_compat.py`
  - `tests/test_debug_compat_telemetry.py`
  - `tests/test_api_routes.py`

### 2026-04-19 - Compat telemetry must record outcome after debug access validation
- Context:
  - `POST /event?debug=true` telemetry now tracks compat-route sunset readiness
    through allowed/blocked counters.
- Symptom:
  - blocked debug calls (for example missing/invalid token) can be counted as
    allowed if telemetry is updated before access checks finish.
- Root cause:
  - counter mutation happened before `_handle_event_request()` completed and
    before debug-access HTTP exceptions were resolved.
- Guardrail:
  - for compat-route telemetry, increment `allowed_total` only after successful
    handler completion; increment `blocked_total` for policy-denied and
    access-denied exceptions.
- Preferred pattern:
  - wrap debug compat handler in `try/except HTTPException` and record outcome
    in one place around the call.
- Avoid:
  - treating route admission as success before downstream debug policy gates.
- Evidence:
  - `app/api/routes.py`
  - `tests/test_api_routes.py`

### 2026-04-19 - Production debug compat-route policy can mask token-gate regressions
- Context:
  - API tests validate both production token-gate behavior and compatibility
    debug query route behavior for `POST /event?debug=true`.
- Symptom:
  - token-related production assertions fail with compat-route denial message
    before token policy checks run.
- Root cause:
  - production default now disables compatibility route unless
    `EVENT_DEBUG_QUERY_COMPAT_ENABLED=true`, so tests expecting token-policy
    outcomes must explicitly enable compat route.
- Guardrail:
  - for token-gate tests on `POST /event?debug=true` in production, set
    `event_debug_query_compat_enabled=True` in fixtures.
  - keep dedicated regressions for default compat-route denial and explicit
    production opt-in behavior.
- Preferred pattern:
  - separate tests by responsibility:
    compat-route access policy first, token-gate policy second.
- Avoid:
  - asserting production token-policy errors through compatibility route
    fixtures that rely on default compat posture.
- Evidence:
  - `tests/test_api_routes.py`
  - `tests/test_main_runtime_policy.py`
  - `tests/test_runtime_policy.py`

### 2026-04-19 - Graph-state list fields can contain raw dicts after model_copy updates
- Context:
  - runtime seeds graph state via `model_copy(update=...)` while loading
    repository-backed proposal payloads.
- Symptom:
  - planning stage crashed with `'dict' object has no attribute 'model_dump'`
    when adapter code assumed every subconscious proposal was a Pydantic model.
- Root cause:
  - `model_copy(update=...)` can keep nested list items as raw dict values
    instead of coercing them into typed nested models.
- Guardrail:
  - graph adapters must defensively normalize list items and accept either
    typed models or plain dict payloads for transitional/runtime-fed state.
- Preferred pattern:
  - check `hasattr(item, "model_dump")` first
  - otherwise accept `dict` items with an explicit copy
  - avoid hard assumptions about nested coercion after graph-state updates
- Avoid:
  - assuming typed list fields always contain model instances after
    `model_copy(update=...)`
- Evidence:
  - `app/core/graph_adapters.py`
  - `tests/test_runtime_pipeline.py`

### 2026-04-19 - LangGraph nodes must re-emit auxiliary runtime keys
- Context: foreground runtime migration to LangGraph while carrying stage logger
  and timing objects as auxiliary execution context.
- Symptom: only the first graph node worked; downstream nodes failed with
  missing runtime context despite successful initial invocation.
- Root cause: auxiliary keys not re-emitted by node outputs were dropped from
  subsequent LangGraph state transitions.
- Guardrail: when graph state includes non-domain auxiliary keys (for example
  logger/timing context), each node must explicitly return those keys again or
  encode them inside the persisted graph state contract.
- Preferred pattern:
  - keep domain state in `GraphRuntimeState`
  - keep runtime-only helper context minimal
  - re-emit runtime helper context in every node output when needed
- Avoid:
  - assuming initial invocation payload keys automatically persist through all
    graph node transitions
- Evidence:
  - `app/core/runtime_graph.py`
  - `tests/test_runtime_pipeline.py`

### 2026-04-19 - Prefer Select-String fallback when `rg` is unavailable in this shell
- Context: execution slices that require fast test/file pattern scans in the
  Windows PowerShell runtime.
- Symptom: `rg` invocation can fail with access-denied runtime errors even
  though repository files are readable.
- Root cause: local shell environment can block `rg.exe` execution in this
  workspace context.
- Guardrail: when `rg` fails, immediately switch to
  `Select-String`/`Get-ChildItem` for pattern discovery and continue without
  blocking the slice.
- Preferred pattern:
  - attempt `rg` first for speed
  - on failure, use `Select-String -Path ... -Pattern ...` with line numbers
  - keep validation and context sync work moving in the same cycle
- Avoid:
  - repeatedly retrying blocked `rg` commands
  - treating tool unavailability as a reason to skip validation or docs sync
- Evidence:
  - `PRJ-055` execution logs in this workspace showed `rg.exe` access denied
    while `Select-String` worked normally

### 2026-04-19 - API events need explicit user scoping to avoid shared-language drift
- Context: language/profile memory is keyed by `user_id`, while API requests
  can arrive without explicit `meta.user_id`.
- Symptom: different API callers can unintentionally share `anonymous` memory
  and influence each other's language preference on ambiguous turns.
- Root cause: missing per-request identity signals on API traffic.
- Guardrail: for API clients, send either `meta.user_id` or
  `X-AION-User-Id`; keep precedence explicit (`meta.user_id` >
  `X-AION-User-Id` > `anonymous`).
- Preferred pattern:
  - preserve strict event normalization boundaries
  - allow route-level identity fallback for clients that cannot send structured
    `meta`
  - keep precedence pinned by tests
- Avoid:
  - relying on shared `anonymous` identity for multi-user API workloads
  - introducing language/profile behavior changes without user-scoping checks
- Evidence:
  - `app/core/events.py`
  - `app/api/routes.py`
  - `tests/test_event_normalization.py`
  - `tests/test_api_routes.py`

### 2026-04-19 - Canonical architecture docs must stay separate from runtime shortcuts
- Context: architecture documentation drifted when live runtime implementation
  details and transport-oriented shortcuts were mixed directly into canonical
  architecture files.
- Symptom: the same `docs/architecture/` files tried to describe both the
  intended human-oriented cognitive order and temporary implementation wiring,
  which made it unclear whether a statement was architectural intent or current
  repo behavior.
- Root cause: implementation reality was documented in the same layer as
  canonical design, so runtime convenience decisions could silently overwrite
  the architecture narrative.
- Guardrail: keep `docs/architecture/` for canonical design only, and place
  live or transitional runtime details in `docs/implementation/`,
  `docs/overview.md`, and operations docs.
- Preferred pattern:
  - update canonical architecture only when the intended design changed
  - record implementation shortcuts outside `docs/architecture/`
  - link both layers clearly from `docs/README.md`
  - sync `.codex/context/PROJECT_STATE.md` when the documentation model changes
- Avoid:
  - using canonical architecture files as a changelog of temporary runtime
    wiring
  - silently changing cognitive stage order just because the implementation
    currently uses a delivery shortcut
- Evidence:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/implementation/runtime-reality.md`

### 2026-04-18 - Schema work must validate both migration and startup paths
- Context: database and runtime tasks while the repository still carries both
  Alembic baseline ownership and a compatibility `create_tables()` startup path.
- Symptom: a schema change can appear correct in one path while still drifting
  in the other, which creates false confidence and hidden startup regressions.
- Root cause: schema ownership is temporarily split between formal migrations
  and MVP bootstrap convenience behavior.
- Guardrail: until migration-first ownership fully replaces startup bootstrap,
  every schema-affecting task must validate both the migration path and the
  current runtime startup assumptions, then sync docs and project state.
- Preferred pattern:
  - update Alembic or schema files
  - run targeted schema or runtime tests
  - verify startup assumptions still hold
  - record the dual-path impact in docs or project state
- Avoid:
  - treating Alembic success alone as sufficient proof that the runtime startup
    path is still safe
- Evidence:
  - migration-first default and compatibility-path decision trail recorded in
    `.codex/context/PROJECT_STATE.md` and `docs/planning/open-decisions.md`

### 2026-04-18 - Validation commands must match real test inventory
- Context: task-board validation commands during stage-boundary and contract-test
  slices.
- Symptom: a validation command can fail immediately with "file not found" even
  when code changes are correct.
- Root cause: task metadata drifted to a stale test path
  (`tests/test_telegram_webhook.py`) that no longer exists in the repository.
- Guardrail: before running or recording a task validation command, verify each
  referenced test path exists in `tests/`.
- Preferred pattern:
  - check planned test files against repository inventory
  - update task-board and planning validation commands when paths changed
  - run the corrected command and record the exact passing output scope
- Avoid:
  - copying historical validation snippets without path existence checks
- Evidence:
  - `PRJ-018` validation command corrected to existing tests in
    `.codex/context/TASK_BOARD.md`
  - full regression remained green after the correction
