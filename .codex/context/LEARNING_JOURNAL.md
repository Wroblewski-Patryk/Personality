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

### 2026-04-25 - Product-facing web shells need mobile-first screenshot proof, not only desktop coherence
- Context:
  - fresh browser audit of the first-party `web/` shell reviewed `login`,
    `chat`, `settings`, `tools`, and `personality` across mobile, tablet, and
    desktop before seeding the next UX/UI implementation lane.
- Symptom:
  - a route can look visually coherent on desktop while still behaving like a
    compressed inspector on mobile, with route chrome, technical wording, raw
    payload detail, or wide content dominating the screen.
- Root cause:
  - the current web shell is still implemented as one large inspection-oriented
    surface in `web/src/App.tsx`, so desktop-shaped cards and backend-truth
    language leak directly into product-facing mobile screens.
- Guardrail:
  - before calling any first-party web surface product-ready, capture
    mobile, tablet, and desktop screenshots for every main route and verify
    that the route is product-first rather than inspector-first.
- Preferred pattern:
  - freeze one mobile-first authenticated shell baseline first
  - prioritize the primary route action above account or hero chrome
  - hide raw payload detail behind an explicit inspect action or separate admin
    posture
  - translate backend truth into simple user-facing states and next actions
- Avoid:
  - treating desktop visual coherence as sufficient proof of mobile quality
  - exposing raw JSON, capability ids, or backend status phrasing as the main
    content of product routes
- Evidence:
  - `.codex/artifacts/ux-audit-2026-04-25/`
  - `web/src/App.tsx`

### 2026-04-25 - Linked channels must change runtime identity resolution, not only profile status
- Context:
  - fresh analysis of the first Telegram linking lane showed a user-visible
    `linked` state in the app tools screen while later memory continuity still
    appeared split between first-party web and Telegram conversations.
- Symptom:
  - the personality can remember a fact through `/app/chat/message`, but after
    linking Telegram the same user may still not get that recall from a normal
    Telegram turn.
- Root cause:
  - the linking flow persists channel linkage on the authenticated profile, but
    normal ingress can still normalize runtime `user_id` from the raw channel
    sender instead of resolving the linked backend identity owner.
- Guardrail:
  - when a product flow claims that an external channel is linked to a backend
    user identity, ordinary runtime ingress for that channel must resolve
    memory and continuity through that same backend identity owner.
- Preferred pattern:
  - keep linking truth in the existing profile-owned fields
  - resolve linked backend identity before foreground runtime state load
  - preserve explicit fallback for unlinked traffic
  - prove the outcome with cross-channel continuity tests, not only link-state
    tests
- Avoid:
  - treating `linked` UI state as sufficient proof that runtime memory owners
    are merged
  - validating only code-generation, confirmation, or tools-overview status
    without a later ordinary channel turn
- Evidence:
  - 2026-04-25 repo analysis across `backend/app/api/routes.py`,
    `backend/app/core/events.py`, `backend/app/memory/repository.py`, and
    `backend/tests/test_api_routes.py`

### 2026-04-25 - App-facing web clients must not assume every backend error is JSON
- Context:
  - live production testing of the first `v2` web shell showed that some
    authenticated `/app/*` routes can still fail with plain-text
    `Internal Server Error` responses during early rollout hardening.
- Symptom:
  - the browser UI shows `Unexpected token 'I'... is not valid JSON` instead
    of surfacing the real backend failure, while affected screens may remain
    on loading or look unrelated to the true fault.
- Root cause:
  - the shared web API helper parses every non-empty response body with
    `JSON.parse(...)` before checking whether the response is successful or
    whether the payload is actually JSON.
- Guardrail:
  - shared client transport helpers must branch on HTTP status and content
    shape before parsing, and they must preserve backend failure detail
    truthfully for app-facing UI states.
- Preferred pattern:
  - read response text once
  - parse JSON only when the payload is expected or safely detectable
  - keep non-JSON error bodies as plain failure detail instead of turning
    them into parser noise
- Avoid:
  - treating every non-empty body from `/app/*` as JSON by default
- Evidence:
  - production test artifacts in `.codex/artifacts/ui-prod-test-2026-04-25/`
  - `web/src/lib/api.ts`

### 2026-04-25 - Vite HTML revision placeholders should have a repo default even when Docker injects the real value
- Context:
  - `web/` now injects the deployed build revision into the browser shell so
    release smoke can prove backend and web ship from the same repository
    commit.
- Symptom:
  - local `npm run build` can stay green but still emit noisy warnings when an
    HTML `%VITE_*%` placeholder is only defined by the Docker build
    environment.
- Root cause:
  - Vite replaces HTML placeholders during build time, so relying only on
    Docker-provided environment values leaves plain local builds without a
    default.
- Guardrail:
  - whenever a Vite HTML placeholder becomes part of release proof, commit a
    safe local default in `web/.env` and let Docker override it with the real
    revision.
- Preferred pattern:
  - use a committed non-secret default such as `dev-local`
  - override it in Docker with the production build arg
  - keep release smoke validating the final deployed value
- Avoid:
  - adding build-proof placeholders to `index.html` without a local fallback
- Evidence:
  - `PRJ-665..PRJ-666`
  - `web/index.html`
  - `web/.env`
  - `docker/Dockerfile`

### 2026-04-25 - Implemented capabilities stay underused when runtime awareness is implicit
- Context:
  - fresh code-level analysis after the core no-UI `v1` planning lane showed
    that planned work, bounded web search, page reading, and tool-grounded
    learning are implemented and tested, but the foreground cognition path
    still exposes those abilities only indirectly in several places.
- Symptom:
  - the personality can execute capability-specific paths when the user uses
    explicit trigger phrasing like `search the web`, `read page`, or `remind
    me tomorrow`, yet it may fail to act like it clearly knows about current
    time, available tools, or its own bounded future-work posture on more
    implicit turns.
- Root cause:
  - runtime capability truth exists mainly in health/debug or planner-side
    heuristics, while prompt and foreground-context surfaces do not always
    carry an explicit, reusable awareness contract for the active turn.
- Guardrail:
  - when a capability becomes part of the product baseline, add an explicit
    foreground awareness contract for it instead of relying only on hidden
    heuristics, event timestamps, or operator-visible health surfaces.
- Preferred pattern:
  - keep execution authority in planning and action
  - add bounded turn-level awareness for time and approved tools
  - prove the behavior with indirect, non-keyword-trigger scenarios
- Avoid:
  - assuming "implemented and green in tests" automatically means the
    personality can recognize and use the capability naturally
- Evidence:
  - 2026-04-25 repo analysis across `app/core/runtime.py`,
    `app/agents/planning.py`, `app/integrations/openai/prompting.py`, and
    `tests/test_runtime_pipeline.py`

### 2026-04-25 - Acceptance surfaces can drift semantically even when parity tests stay green
- Context:
  - after the core no-UI `v1` boundary was revised around conversation,
    website reading, tool-grounded learning, and internal planned work, fresh
    analysis still found old organizer-gate assumptions and surface-only
    readiness wording in some repo truth.
- Symptom:
  - `/health.v1_readiness`, tests, and high-level docs can all look mutually
    consistent while still overstating what is core `v1`, what is extension
    posture, and which gates are truly derived from live runtime conditions.
- Root cause:
  - parity coverage was stronger than semantic-boundary coverage, so stale
    acceptance meaning survived even though serialization and smoke checks were
    already green.
- Guardrail:
  - whenever product boundary changes, review not only field presence and
    parity, but also whether each readiness field is still a truthful summary
    of the approved acceptance boundary.
- Preferred pattern:
  - freeze the acceptance boundary first
  - derive readiness summaries from live owner surfaces
  - keep extension posture visible, but separate from core-release blockers
- Avoid:
  - treating "field exists and matches incident evidence" as sufficient proof
    that the field still means the right thing
- Evidence:
  - `PRJ-647` planning analysis
  - `app/core/v1_readiness_policy.py`
  - `docs/architecture/10_future_vision.md`

### 2026-04-24 - Coolify Docker Compose apps must not reference `SOURCE_COMMIT` directly in compose values
- Context:
  - deploy parity was repaired up to automatic source automation, but live
    production still reported `runtime_build_revision=unknown` even after the
    canonical app auto-deployed the latest commits.
- Symptom:
  - the Coolify environment-variable UI showed `SOURCE_COMMIT=unknown`, and
    runtime build revision stayed missing despite healthy source automation and
    successful deploy history.
- Root cause:
  - referencing `SOURCE_COMMIT` directly inside `docker-compose.coolify.yml`
    caused Coolify to materialize `SOURCE_COMMIT` as a user-managed environment
    variable, which shadowed the predefined magic variable and persisted the
    value `unknown`.
- Guardrail:
  - for Docker Compose deployments, let the compose file reference an
    application-owned variable such as `${APP_BUILD_REVISION:-unknown}`, then
    set `APP_BUILD_REVISION=$SOURCE_COMMIT` in Coolify as a runtime variable.
- Preferred pattern:
  - keep `APP_BUILD_REVISION` as the repo-owned compose contract
  - keep `$SOURCE_COMMIT` only in Coolify's environment-variable value, not as
    a compose placeholder
  - remove any user-created `SOURCE_COMMIT` variable if it appears with the
    value `unknown`
- Avoid:
  - using `$SOURCE_COMMIT` or `${SOURCE_COMMIT:-...}` directly in compose
    service environment values for the canonical Coolify app
- Evidence:
  - `PRJ-634`
  - production `/health.deployment.runtime_build_revision`
  - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`

### 2026-04-25 - Frontend build revision parity should not depend on Coolify passing runtime variables into the web bundler
- Context:
  - the first `v2` browser stabilization lane added release-smoke proof that
    `/`, `/chat`, `/settings`, `/tools`, and `/personality` all expose the
    same deployed web-shell revision as the backend runtime.
- Symptom:
  - production `/health` reported the correct `runtime_build_revision`, but
    the served SPA HTML still exposed `aion-web-build-revision=unknown`, so
    release smoke failed even after the new backend commit was live.
- Root cause:
  - Coolify runtime environment mapping kept `APP_BUILD_REVISION` correct for
    the Python service, but the frontend bundler artifact could still be built
    with the fallback value, leaving the revision meta stale inside static
    `web/dist/index.html`.
- Guardrail:
  - when FastAPI is the owner serving the SPA shell, inject the runtime
    `APP_BUILD_REVISION` into the served HTML response instead of trusting the
    static build artifact to carry the final deploy revision.
- Preferred pattern:
  - keep the web-shell revision meta tag in `web/index.html`
  - preserve the Docker build arg for local and image-level parity
  - have backend-owned SPA serving rewrite the meta tag to the runtime
    revision before responding
- Avoid:
  - treating a static `unknown` web revision as acceptable once backend
    runtime parity is already machine-visible
- Evidence:
  - `PRJ-679`
  - `backend/tests/test_web_routes.py`
  - `.\backend\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`

### 2026-04-24 - Coolify source drift can silently break repo-driven deploy after a repository rename
- Context:
  - the final operational `v1` closure lane required proving that `push main`
    reaches the canonical Coolify production app without relying on manual
    redeploys.
- Symptom:
  - pushes to `main` did not trigger automatic deploys for `Personality`, even
    though a comparable app in the same Coolify instance still auto-deployed.
- Root cause:
  - the canonical Coolify app had drifted onto the `Public GitHub` source and
    still referenced the pre-rename repository path
    `Wroblewski-Patryk/LuckySparrow`; the intended GitHub App source
    `vps-luckysparrow` was no longer attached to the renamed
    `Wroblewski-Patryk/Personality` repository.
- Guardrail:
  - when production auto-deploy stops after a repository rename, verify both
    the local git remote and the Coolify `Source` page for the canonical app
    before debugging webhook/runtime behavior.
- Preferred pattern:
  - select the correct Coolify team scope first, then keep the canonical app on
    the GitHub App source `vps-luckysparrow` with repository
    `Wroblewski-Patryk/Personality` and branch `main`.
- Avoid:
  - treating `Public GitHub` on the canonical production app as an acceptable
    source variant
  - debugging webhook fallbacks before checking for source-type or repository
    drift
- Evidence:
  - `PRJ-616`
  - canonical app `jr1oehwlzl8tcn3h8gh2vvih`
  - source corrected from `Public GitHub` to `vps-luckysparrow`

### 2026-04-24 - Production can be healthy while deploy parity is still behind repo truth
- Context:
  - the final operational `v1` closure lane needed machine-visible proof that
    live production really matched the current repository baseline instead of
    only returning a healthy `/health` response.
- Symptom:
  - live production remained generally healthy, but release smoke failed on
    deployment parity because the deployed contract was missing the newer
    deployment provenance fields.
- Root cause:
  - repo truth had advanced beyond production truth, and the previous smoke
    path did not make that drift explicit enough.
- Guardrail:
  - whenever deployment or runtime-proof surfaces widen, make release smoke
    compare live runtime build revision against local repo HEAD and optional
    deployment evidence `after_sha`.
- Preferred pattern:
  - expose `runtime_build_revision`, trigger mode, and provenance state through
    `/health.deployment`
  - pass the same deployment posture through incident evidence
  - let release smoke fail loudly when production is still behind the checked
    out repo
- Avoid:
  - treating a healthy `/health.status=ok` as sufficient proof that production
    matches the current repository baseline
  - adding a second deploy-truth system outside the existing deployment and
    observability owners
- Evidence:
  - `PRJ-615`
  - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`

### 2026-04-23 - Coolify env overrides can silently mask repo-driven defaults
- Context:
  - production proactive was expected to follow the repo-driven Coolify compose
    baseline after `PROACTIVE_ENABLED` defaulted to `true`, but live `/health`
    still reported `disabled_by_policy`.
- Symptom:
  - production runtime contradicted the repository-owned compose default even
    after the correct commit was pushed and deployed.
- Root cause:
  - the active Coolify application still had an explicit env override
    `PROACTIVE_ENABLED=false`, which took precedence over the compose default.
- Guardrail:
  - when production `/health` disagrees with a repo-driven compose default,
    check explicit Coolify env overrides before assuming deploy drift or a
    runtime bug.
- Preferred pattern:
  - keep the desired baseline in `docker-compose.coolify.yml`
  - use app-level env overrides only for deliberate exceptions
  - after changing an override, redeploy and verify the corresponding `/health`
    surface directly
- Avoid:
  - assuming a pushed compose default always wins over existing Coolify env
    values
  - debugging runtime logic before checking app-level overrides
- Evidence:
  - `PRJ-581`
  - production `/health.proactive`
  - Coolify production app env for `PROACTIVE_ENABLED`

### 2026-04-23 - Coolify production checks can silently target the wrong team scope
- Context:
  - production attention cutover verification needed direct Coolify UI
    interaction after the repo commit was already pushed to `main`.
- Symptom:
  - the panel showed an incomplete project view with empty resources, no
    sources, and no terminal access even though the real production app and
    public `/health` were both live.
- Root cause:
  - the active Coolify team scope remained on `luckysparrow's Team`, while the
    real production app lived under `Root Team`.
- Guardrail:
  - when Coolify UI evidence does not match public runtime truth, verify the
    selected team before assuming the deployment resource is gone or the panel
    is broken.
- Preferred pattern:
  - open `/projects`
  - switch to the expected team explicitly
  - then resolve the canonical project, environment, and application URLs
  - only after that inspect queued deployments or trigger redeploys
- Avoid:
  - diagnosing empty Coolify resources before checking team scope
  - assuming the first visible project in Coolify is the active production
    stack
- Evidence:
  - `PRJ-577`
  - production app
    `project/icmgqml9uw3slzch9m9ok23z/environment/qxooi9coxat272krzjx221fv/application/jr1oehwlzl8tcn3h8gh2vvih`
  - deployment `amz31iyapwr3t9z9tanpe2jb`

### 2026-04-23 - External cadence sidecars must not sleep the full interval after migration-race failures
- Context:
  - Coolify production externalized maintenance and proactive cadence into
    dedicated sidecars while the repository still runs `python -m alembic
    upgrade head` as a post-deployment command after containers start.
- Symptom:
  - production `/health.scheduler.external_owner_policy` stayed on
    `missing_external_run_evidence` even though the external cadence containers
    were up and the selected execution mode was already `externalized`.
- Root cause:
  - cadence sidecars executed their first tick before the post-deploy migration
    created the new evidence table, then the shell loop slept for the full
    cadence interval (`3600s` or `1800s`) after that failure instead of
    retrying quickly once migrations finished.
- Guardrail:
  - external cadence loops must use a short failure backoff that is distinct
    from the normal cadence interval whenever startup ordering can race against
    post-deploy migrations.
- Preferred pattern:
  - keep the canonical cadence entrypoints unchanged
  - make the deployment loop retry quickly after a non-zero exit
  - keep the normal cadence sleep only for successful ticks
- Avoid:
  - assuming a successful container start means the first cadence tick also had
    the migrated schema available
  - sleeping for the full cadence interval after a migration-race failure
- Evidence:
  - `PRJ-573`
  - `docker-compose.coolify.yml`
  - production Coolify deployment `rbcv9u835f1d72w8z4pw0trc`

### 2026-04-23 - Coolify production Postgres must ship pgvector before migration-first deploys
- Context:
  - production Telegram traffic reached the service, but full Alembic repair on
    Coolify failed after baseline stamping because the production database image
    was still plain `postgres:15`.
- Symptom:
  - `alembic upgrade head` stopped on `CREATE EXTENSION IF NOT EXISTS vector`
    even though the application image and migration chain were otherwise ready.
- Root cause:
  - the repo-driven `docker-compose.coolify.yml` pinned the production `db`
    service to a vanilla PostgreSQL image that cannot satisfy the approved
    semantic-vector migration baseline.
- Guardrail:
  - when production PostgreSQL deploys use migration-first bootstrap and
    semantic vectors are enabled, the Coolify compose file must use a
    pgvector-capable image for the same PostgreSQL major version.
- Preferred pattern:
  - keep the production database image aligned with the semantic migration
    contract in repository-owned compose
  - verify both Python `pgvector` and PostgreSQL `vector` extension readiness
    before calling production healthy
- Avoid:
  - assuming a plain PostgreSQL image can remain valid once Alembic `head`
    includes `vector` extension setup
- Evidence:
  - `PRJ-570`
  - `docker-compose.coolify.yml`
  - production Coolify deployment logs on 2026-04-23
  - migration `20260419_0004_add_pgvector_semantic_embedding_scaffold.py`

### 2026-04-23 - PostgreSQL vector deploys must validate Python pgvector parity before startup
- Context:
  - production Telegram webhook traffic reached the service, but every
    foreground `/event` turn failed with
    `/health.conversation_channels.telegram.last_ingress.reason=runtime_exception:ProgrammingError`.
- Symptom:
  - `/health` looked healthy, while Telegram and direct API turns both returned
    `500 Internal Server Error` before any delivery attempt.
- Root cause:
  - PostgreSQL semantic-vector retrieval was live in the foreground pipeline,
    but the Python `pgvector` binding was not guaranteed by the default runtime
    dependency set, so deploys could boot into a broken vector-runtime state.
- Guardrail:
  - when PostgreSQL plus semantic vectors are enabled, startup must block
    before database initialization unless the Python `pgvector` package is
    available in the runtime image.
- Preferred pattern:
  - ship `pgvector` as a normal deploy dependency
  - fail fast at startup on missing vector-runtime bindings
  - use `/health.conversation_channels.telegram.last_ingress.reason` to confirm
    whether production silence is a foreground runtime crash instead of a
    webhook or delivery outage
- Avoid:
  - treating healthy `/health` as proof that foreground turn processing is
    safe when semantic retrieval dependencies may still be missing
- Evidence:
  - `PRJ-569`
  - `pyproject.toml`
  - `app/main.py`
  - `tests/test_main_lifespan_policy.py`

### 2026-04-22 - Connector-action tests must carry the same delivery envelope as the plan
- Context:
  - adding provider-backed connector execution to `ActionExecutor` while the
    runtime already enforced `ActionDelivery.execution_envelope` parity.
- Symptom:
  - new connector execution tests failed with generic action `fail` posture
    before the provider client was even exercised.
- Root cause:
  - the tests reused `_delivery()` defaults with an empty envelope, but
    connector-aware plans now require the matching bounded envelope built from
    planning output.
- Guardrail:
  - whenever action tests exercise connector intents, build the delivery
    envelope from the same `PlanOutput` using
    `build_action_delivery_execution_envelope(plan)`.
- Preferred pattern:
  - create the plan once
  - derive the delivery envelope from that exact plan
  - assert provider-backed execution behavior only after envelope parity is
    satisfied
- Avoid:
  - treating empty delivery envelopes as valid defaults for connector-aware
    action tests
- Evidence:
  - `PRJ-472..PRJ-475`
  - `tests/test_action_executor.py`

### 2026-04-22 - Runtime table additions must ship with Alembic parity proof
- Context:
  - post-convergence slices had already introduced durable attention and
    subconscious proposal tables in runtime code and docs.
- Symptom:
  - `Base.metadata` and runtime-reality inventory looked current, but the
    Alembic chain still lagged behind the actual live schema surface.
- Root cause:
  - durable-table work was validated through runtime behavior and docs sync
    before migration parity was explicitly exercised from a fresh database.
- Guardrail:
  - every new persisted table or named constraint family must ship with:
    - an Alembic revision
    - a regression that runs fresh `alembic upgrade head`
    - docs/context sync only after migration parity is proven
- Preferred pattern:
  - treat migration-first bootstrap as the release truth for schema changes
  - inspect the migrated schema with tests instead of trusting metadata alone
- Avoid:
  - assuming runtime behavior plus `Base.metadata` means deploy/bootstrap truth
    is already aligned
- Evidence:
  - `PRJ-464..PRJ-467`
  - `tests/test_schema_baseline.py`
  - `migrations/versions/20260422_0006_add_attention_and_subconscious_tables.py`

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

### 2026-04-23 - Startup wiring can drift from route-level durable inbox tests
- Context:
  - production Telegram reply handling depended on `ATTENTION_COORDINATION_MODE=durable_inbox`
    while route-level tests already injected a repository-backed attention
    coordinator manually.
- Symptom:
  - Telegram messages reached production, but no reply was observed after a
    recent change set even though route-level durable inbox tests still passed.
- Root cause:
  - app startup instantiated `AttentionTurnCoordinator` without the shared
    `memory_repository`, so the production coordinator could not activate the
    repository-backed durable inbox path even when the mode was configured.
- Guardrail:
  - add lifespan-level regression coverage for any production-only startup
    wiring that differs from route test harness setup.
- Preferred pattern:
  - when runtime state depends on a repository-backed coordinator or worker,
    assert that `app.state` wiring in `app.main` carries the same dependency as
    route-level test factories.
- Avoid:
  - assuming route tests that build app state manually also prove main-lifespan
    wiring for the same feature flags.
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
