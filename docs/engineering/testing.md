# Testing Strategy

## Current Automated Coverage

The repository currently contains lightweight backend-focused tests for:

- event normalization
- expression behavior
- end-to-end runtime pipeline composition with fake dependencies
- deployment-trigger and release-smoke script regressions

Canonical behavior-validation expectations now also live in:

- `docs/architecture/29_runtime_behavior_testing.md`

That architecture file defines when passing unit and integration tests are
still insufficient because the runtime has not yet proven memory influence,
continuity, or decision integrity across time.

Primary command:

```powershell
Push-Location .\backend
..\.venv\Scripts\python -m pytest -q
Pop-Location
```

Web build command:

```powershell
Push-Location .\web
npm run build
Pop-Location
```

Behavior-validation command (system-debug + scenario harness baseline):

```powershell
.\backend\scripts\run_behavior_validation.ps1 -GateMode operator
```

CI gate behavior-validation command (artifact + fail-fast gate posture):

```powershell
.\backend\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json
```

Artifact-input gate evaluation command (CI split-stage, no pytest rerun):

```powershell
.\backend\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactInputPath artifacts/behavior_validation/report.json -ArtifactPath artifacts/behavior_validation/report.gate.json
```

Incident-evidence bundle export helper:

```powershell
.\.venv\Scripts\python .\backend\scripts\export_incident_evidence_bundle.py --base-url http://localhost:8000
```

## Testing Layers For This Repo

- Unit tests:
  - heuristic agent logic
  - config validation
  - event normalization
  - repository helpers that can be exercised without a live service
- Integration tests:
  - FastAPI endpoints
  - database-backed memory persistence
  - Telegram/OpenAI adapter boundaries using mocks or fakes
- Manual smoke checks:
  - Docker startup
  - health endpoint
  - API roundtrip through `POST /event`
  - Telegram webhook flow in a non-production environment
- Behavior-driven system checks:
  - internal debug-mode validation of perception/context/motivation/role/plan
    and retrieved memory (`system_debug` contract surface)
  - relation-source optional-family posture checks across
    `/health.memory_retrieval`, `system_debug.adaptive_state`, and release
    smoke evidence
  - user-simulation scenarios without debug payloads
  - persistence, continuity, and failure-mode scenarios across time

## Required Checks By Change Type

- Runtime stage changes:
  - update or add tests around changed stage outputs
  - run the full pytest suite
  - when the change touches foreground-awareness, also run:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_identity_service.py tests/test_openai_prompting.py tests/test_context_agent.py tests/test_expression_agent.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py; Pop-Location`
- API contract changes:
  - add endpoint-level coverage
  - confirm the returned serialized shape still matches expectations
- Web client shell changes:
  - keep `web/` as a thin client over backend-owned contracts
  - require at least one successful production build
  - when the shell route topology changes, confirm release smoke still proves
    `"/"`, `"/chat"`, `"/settings"`, `"/tools"`, and `"/personality"` all
    resolve to the same deployed web revision
  - when the change touches tools or channels truth, run focused backend route
    coverage for `/app/tools/overview`, `/app/tools/preferences`, and
    Telegram link-state transitions
  - when deploy parity is affected, extend release smoke or deployment-script coverage
  - when the change touches account reset UX or destructive settings posture:
    - pin backend route coverage for `POST /app/me/reset-data`
    - pin repository cleanup coverage for preserved-versus-cleared state
    - verify the web shell build after wiring the destructive confirmation flow
- Memory or database changes:
  - add repository or integration coverage
  - verify startup table creation or migration behavior
  - when migration files change, validate the Alembic path explicitly
- Integration changes:
  - mock external providers
  - verify fallback behavior when providers are unavailable
- Release/deployment script changes:
  - add or update script-level regressions for evidence artifacts, failure
    posture, and smoke compatibility behavior
  - verify Windows PowerShell execution path in this workspace
  - keep bash logic symmetric and document when live bash execution is blocked
- Migration/schema parity changes:
  - require one regression that exercises fresh `alembic upgrade head`
    against a new database
  - verify new durable tables or named constraints through inspector-level
    assertions, not only `Base.metadata`
- Health/governance snapshot changes:
  - extend endpoint-level coverage for new policy or alignment fields
  - pin both baseline and customized-override posture when the contract is
    rollout-sensitive

## Risk Areas To Keep Honest

- placeholder values presented as real runtime facts
- hidden side effects outside `ActionExecutor`
- changes that break Telegram-specific payload handling
- changes that silently disable memory persistence
- changes that rely on live OpenAI responses in automated tests

## Evidence Preference

For meaningful repo changes, leave behind:

- the exact test command used
- pass/fail result
- a short note if coverage is still missing for a known edge case
- a scenario-level behavior note when the touched subsystem is memory,
  reflection, planning, language continuity, relation influence, or proactive
  behavior
- for release-readiness-sensitive slices, behavior validation evidence from:
  - `.\scripts\run_behavior_validation.ps1 -GateMode operator`
  - `./scripts/run_behavior_validation.sh --gate-mode operator`
- for deployment-trigger or release-smoke changes, script regression evidence
  from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py`
  - `.\web\npm run build`
- for app-facing tools and channels slices, regression and deploy-readiness
  evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "tools_overview or tools_preferences or telegram_link"`
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "release_smoke"`
  - `.\web\npm run build`
- coverage should pin:
    - authenticated `GET /app/tools/overview` grouped payload truth
    - user-owned toggle persistence through `PATCH /app/tools/preferences`
    - web-shell route proof for:
      - `/`
      - `/chat`
      - `/settings`
      - `/tools`
      - `/personality`
    - Telegram link-state transitions:
      - `not_linked`
      - `pending_confirmation`
      - `linked`
      - invalid or expired link code rejection
    - provider-blocked posture when Telegram is not configured
    - web build success for the tools screen consuming only backend-owned
      contract fields
- for destructive reset and runtime-cleanup slices, regression and release
  evidence from:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py; Pop-Location`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - `Push-Location .\web; npm run build; Pop-Location`
  - coverage should pin:
    - authenticated `POST /app/me/reset-data` confirmation guard and logout posture
    - preservation of auth identity, profile state, linked integrations, and
      user-managed operational preferences
    - clearing of runtime continuity, planning state, queue/proposal state,
      and relation/theta state
    - operator-script confirmation guards for:
      - `single_user_runtime_reset`
      - `runtime_only_preserve_auth`
    - product-shell success path returning the user to `/login` after reset
- for observability-export and incident-evidence slices, regression and gate
  evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_deployment_trigger_scripts.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - `.\.venv\Scripts\python .\scripts\export_incident_evidence_bundle.py --base-url http://localhost:8000`
  - coverage should pin:
    - `/health.observability` export-readiness posture
    - debug-response `incident_evidence` export contract
    - smoke-mode validation of exported incident evidence and full bundle
      directories
    - optional behavior-artifact ingestion of exported incident evidence
- for durable-attention production-baseline slices, regression and evidence
  checks from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`
  - coverage should pin:
    - public `/health.attention` durable owner plus repository-backed
      contract-store posture
    - public `/health.runtime_topology.attention_switch` selected durable mode
      and readiness posture
    - exported `incident_evidence.policy_posture["attention"]`
    - exported `incident_evidence.policy_posture["runtime_topology.attention_switch"]`
    - behavior-level burst-coalescing proof for the live `durable_inbox`
      baseline
- for `v1` conversation-reliability slices, regression and smoke evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_delivery_router.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_runtime_pipeline.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`
  - coverage should pin:
    - `/health.conversation_channels.telegram` readiness and last-event posture
    - ingress rejection versus processed-turn telemetry for Telegram webhook
      traffic
    - delivery success/failure telemetry in the shared delivery boundary
    - incident-evidence and smoke validation of
      `conversation_channels.telegram`
- for learned-state and skill-introspection slices, regression and evidence
  checks from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - coverage should pin:
    - `/health.learned_state` owner, internal inspection path, and bounded
      section-contract metadata
    - `/health.api_readiness` owner and stable backend-surface contract for
      later `v2` UI callers
    - internal `GET /internal/state/inspect?user_id=...` access and bounded
      payload shape, including `api_readiness`, preference summary,
      knowledge summary, reflection growth summary, role/skill visibility
      summary, and planning continuity summary
    - exported `incident_evidence.policy_posture["learned_state"]` with the
      same bounded section-contract metadata
    - release-smoke and behavior-validation rejection when learned-state
      posture is missing or carries the wrong bounded contract
- for bounded search, browser, and organization tooling slices, regression and
  behavior evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
- coverage should pin:
    - shared typed-intent and permission-gate policy for `knowledge_search`
      and `web_browser`
    - `/health.connectors.web_knowledge_tools` readiness plus fallback posture
    - `/health.connectors.web_knowledge_tools.website_reading_workflow` direct
      versus search-first review contract, selected provider path, bounded read
      semantics, and memory-capture boundary
    - matching incident-evidence and incident-bundle proof for
      `connectors.web_knowledge_tools.website_reading_workflow`
    - live execution-baseline entries for:
      - `knowledge_search.search_web`
      - `web_browser.read_page`
      - `task_system.clickup_update_task`
    - runtime `system_debug.adaptive_state["web_knowledge_tools"]` parity with
      the health-level posture
    - scenario-level proof that role and planning use the approved tool slices
      only through the action-owned boundary:
      - `T14.1` analyst-driven DuckDuckGo search
      - `T14.2` analyst-driven generic HTTP page read
      - `T14.3` executor-aligned ClickUp task update
- for foreground-awareness repair slices, regression evidence from:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_identity_service.py tests/test_openai_prompting.py tests/test_context_agent.py tests/test_expression_agent.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py; Pop-Location`
- coverage should pin:
    - foreground context fields for current-turn awareness
    - linked-name recall from auth/profile-owned identity facts
    - current-turn time answers grounded in `event.timestamp`
    - implicit weather lookup through bounded search
    - implicit website-content lookup from explicit URL or bare domain
    - rejection of false capability-denial wording when foreground truth is present
- for backend work-partner orchestration slices, regression and behavior
  evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - coverage should pin:
    - explicit `work_partner` role selection and bounded skill mix
    - machine-visible role-skill policy posture for `work_partner`
    - work-partner orchestration of approved tool slices through typed intents
      and action results
    - scenario-level proof through:
      - `T15.1` work-partner organization with bounded search plus ClickUp
        update
      - `T15.2` work-partner decision support with bounded page-read browsing
      - `T16.1` work-partner ClickUp task listing
      - `T16.2` work-partner Google Calendar availability reads
      - `T16.3` work-partner Google Drive metadata listing
- for organizer-tool production-readiness slices, regression and release-proof
  evidence from:
- `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py`
- `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
- `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`
- coverage should pin the shared `/health.connectors.organizer_tool_stack`
  contract plus matching incident-evidence and bundle proof
- organizer daily-use coverage should also pin:
  - `daily_use_workflows`
  - `daily_use_ready_workflow_count` versus `daily_use_total_workflow_count`
  - `daily_use_ready_workflows`
  - `daily_use_blocked_workflows`
  - parity with `/health.v1_readiness.organizer_daily_use_*`
- organizer-tool activation coverage should also pin
  `organizer_tool_stack.activation_snapshot`, including:
  - activation-state transitions
  - provider-specific missing settings
  - provider-specific next actions
  - parity between `/health`, incident evidence, and incident-evidence bundles
  - for tool-grounded learning capture slices, regression and release-proof
    evidence from:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - coverage should pin:
    - approved external reads persist only bounded tool-grounded conclusion
      kinds through action-owned capture and memory-owned conclusion writes
    - `/health.learned_state.tool_grounded_learning` and
      `incident_evidence.policy_posture["learned_state"].tool_grounded_learning`
      stay in parity
    - `v1_readiness.required_behavior_scenarios` includes the
      tool-grounded-learning recall anchors `T17.1..T17.2`
    - scenario-level proof that later cognition can recall tool-grounded
      semantic conclusions without re-running the external read path in the
      follow-up turn
  - for backend capability-catalog slices, regression and release-proof
    evidence from:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_deployment_trigger_scripts.py`
    - coverage should pin:
      - `/health.capability_catalog` bounded aggregation posture
      - internal `GET /internal/state/inspect?user_id=...` capability catalog
        parity with selection-visibility details
      - `capability_record_truth_model` distinction between:
        - described durable records
        - runtime selection surfaces
        - authorization posture
      - described role presets and described skill ids remain visible without
        implying executable authority
      - authorization evidence keeps public read operations separate from
        opt-in-bound reads and confirmation-gated organizer mutations
      - release-smoke and incident-evidence bundle failure when
        `capability_catalog` is missing or partial
      - scenario-level proof that selected work-partner skill metadata does not
        imply unrelated organizer mutation authority during bounded
        website-reading
  - for no-UI `v1` life-assistant workflow slices, regression and behavior
    evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_goal_task_signals.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode operator`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - coverage should pin:
    - explicit reminder phrasing creates a bounded internal task anchor
    - explicit reminder/check-in phrasing persists `proactive_opt_in` through
      the action-owned conclusion path
    - `T18.1` website-reading plus later recall without re-running the page
      read
    - `T18.2` organizer review plus later focus guidance without re-running
      the organizer read
    - `T19.1` due planned-work delivery stays inside the normal foreground
      runtime path
    - `T19.2` recurring planned work advances through scheduler-owned
      reevaluation instead of a second scheduling subsystem
    - `v1_readiness.required_behavior_scenarios` includes `T18.1..T19.2`
    - explicit planning phrasing creates the bounded task anchor
      `plan tomorrow`
    - scenario-level proof that reminder capture, planning continuity, and
      scheduler-owned proactive follow-up still compose into one end-to-end
      `v1` workflow (`T13.1`)
- for time-aware planned-work proof slices, regression and release evidence
  from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - coverage should pin:
    - `/health.v1_readiness.time_aware_planned_work_*`
    - exported `incident_evidence.policy_posture["v1_readiness"]` parity for
      the same planned-work posture
    - release-smoke failure when planned-work gate state drifts or disappears
    - required behavior scenarios `T19.1..T19.2`
- for runtime-topology, adaptive-governance, planning-governance, or
  deployment-policy surface changes, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
- for retrieval-provider rollout changes, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_main_runtime_policy.py tests/test_runtime_policy.py`
- for retrieval-lifecycle closure slices, regression and release evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_runtime_policy.py tests/test_api_routes.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_runtime_pipeline.py`
  - coverage should pin all three surfaces:
    - lifecycle owner, provider-drift posture, and pending-gap visibility in
      `/health.memory_retrieval`
    - runtime behavior that still exercises the declared transition owner when
      `local_hybrid` is active
    - release-smoke summary fields for retrieval lifecycle owner, drift, and
      alignment posture
  - when production baseline is frozen as OpenAI provider-owned embeddings,
    release-evidence coverage should also pin:
    - requested/effective provider `openai`
    - requested/effective model `text-embedding-3-small`
    - `semantic_embedding_execution_class=provider_owned_openai_api`
    - `semantic_embedding_production_baseline_state=aligned_openai_provider_owned`
    - `retrieval_lifecycle_provider_drift_state=aligned_target_provider`
    - `retrieval_lifecycle_alignment_state=aligned_with_defined_lifecycle_baseline`
    - empty `retrieval_lifecycle_pending_gaps`
  - CI behavior-validation gate coverage should fail when incident evidence no
    longer proves that aligned retrieval posture
- for background-worker externalization slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_reflection_worker.py`
- for reflection-supervision slices, regression and release evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_supervision_policy.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_api_routes.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
  - coverage should pin all four surfaces:
    - supervision baseline owner and queue-health classification
    - `/health.reflection.supervision` posture
    - startup log evidence for supervision posture
    - release-smoke summary fields for supervision readiness and recovery guidance
- for proactive-runtime activation slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode operator`
  - coverage should pin:
    - `/health.proactive` owner, enabled state, and production baseline posture
    - anti-spam guardrail outcomes through proactive runtime and scheduler paths
    - latest proactive tick summary together with scheduler-owned cadence
      evidence
- for proactive production-evidence slices, regression and evidence checks from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`
  - coverage should pin:
    - exported `incident_evidence.policy_posture["proactive"]`
    - release-smoke failure when proactive health or incident-evidence posture
      is missing, disabled, or carries the wrong owner
    - behavior-validation rejection when proactive posture drifts from the live
      bounded production baseline
- for embedding execution-class diagnostics slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- for connector execution-policy slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
- for connector read-posture expansion slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  - coverage should pin both:
    - bounded provider-backed execution notes for the selected read path
    - `/health.connectors.execution_baseline` readiness posture
      (`credentials_missing|provider_backed_ready`) for the same path
  - current live bounded read paths that should remain pinned are:
    - `calendar.google_calendar_read_availability`
    - `cloud_drive.google_drive_list_files`
- for external-scheduler ownership slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`
  - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`
  - coverage should pin both:
    - `/health.scheduler.external_owner_policy` cutover-proof fields
      (`maintenance_run_evidence`, `proactive_run_evidence`,
      `duplicate_protection_posture`, `cutover_proof_ready`)
    - smoke and incident-evidence gate failures when that proof surface is
      incomplete
  - current production-baseline evidence should prove:
    - `selected_execution_mode=externalized`
    - `cutover_proof_ready=true`
    - `production_baseline_ready=true`
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py`
- for typed future-write ownership slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py tests/test_scheduler_worker.py`
- for `ActionDelivery` extensibility slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
- for compatibility-sunset readiness slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
- for shared debug-ingress vocabulary convergence slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
- for dedicated-admin debug-ingress retirement slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py`
- for affective input and resolution diagnostics slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
- for background adaptive-output convergence slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`
- for identity/profile ownership slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
- for durable attention parity slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_memory_repository.py tests/test_config.py`
- for role-and-skill capability slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_action_executor.py`
- for retrieval-depth and theta-governance slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_role_agent.py tests/test_planning_agent.py tests/test_memory_repository.py`
- for role-selection evidence slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
- for role/skill maturity slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
- for affective rollout-policy slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`
- for reflection-scope governance slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
  - coverage should pin all three surfaces:
    - reflection writer scope selection
    - repository canonicalization/filtering for scoped vs global conclusions
    - runtime no-cross-goal leakage when scoped rows coexist with global
      adaptive outputs
- for durable attention contract-store slices, regression evidence from:
  - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  - coverage should pin:
    - repository-backed attention turn persistence
    - durable-inbox route parity with burst coalescing semantics
    - cleanup-candidate visibility and answered/stale row cleanup
- for CI-sensitive slices, behavior gate evidence from:
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  - `./scripts/run_behavior_validation.sh --gate-mode ci --artifact-path artifacts/behavior_validation/report.json`
  - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactInputPath artifacts/behavior_validation/report.json -ArtifactPath artifacts/behavior_validation/report.gate.json`
  - `./scripts/run_behavior_validation.sh --gate-mode ci --artifact-input-path artifacts/behavior_validation/report.json --artifact-path artifacts/behavior_validation/report.gate.json`
- artifact contract notes for CI parsers:
  - `artifact_schema_version` identifies schema evolution
  - `gate_reason_taxonomy_version` identifies reason-code taxonomy
  - `gate.violation_context` carries machine-readable context for gate reasons
  - optional `incident_evidence` block records whether exported runtime
    incident evidence was checked, which schema/policy owner it used, and
    whether policy-surface coverage was complete
  - for dedicated-admin debug retirement, that same `incident_evidence` block
    must also prove dedicated-admin-only posture plus an explicit rollback
    exception state (`shared_debug_break_glass_only|shared_debug_disabled`)
  - CI artifact-input evaluation now blocks on incompatible
    `artifact_schema_version` major values, while operator mode remains
    backward-compatible for local inspection

Useful migration verification command:

```powershell
.\.venv\Scripts\python -m alembic upgrade head --sql
```
