# Open Decisions

## Why This File Exists

The current repo already works as an MVP slice, but several architecture-level docs describe systems that are not implemented yet. This file keeps the next real decisions visible and tied to the current codebase.

## V2 Product Surface And Repository Topology (2026-04-25)

Fresh user approval now resolves the top-level `v2` product topology.

1. approved repository direction
   - the repository should move toward product-facing top-level directories:
     - `backend/`
     - `web/`
     - `mobile/`
   - only repo-wide and deployment-wide files should remain in the root
2. approved backend direction
   - the current Python + FastAPI AION runtime remains the backend owner
   - `backend/` is the correct product-facing name even though it contains
     more than just raw API handlers
3. approved client direction
   - `web/` is the first dedicated UI surface
   - `mobile/` is part of the approved product topology now, even if its first
     implementation lands after `web`
4. approved auth direction
   - first-party auth/session should be backend-owned
   - product clients should not rely on raw `user_id` headers or internal
     debug surfaces as their trust boundary
5. still-open bounded follow-ups
   - the exact production serving topology for `web` versus `backend` routes
     should be frozen together with the deploy task, not guessed ad hoc during
     the initial folder move

## Mobile Stack Baseline (2026-04-25)

The previously deferred mobile-stack choice is now resolved for the first
mobile foundation lane.

1. approved stack
   - Expo-managed React Native
   - TypeScript
   - Expo Router
2. approved client-contract posture
   - `mobile/` must remain a thin client over backend-owned `/app/*`
     resources
   - `mobile/` must not consume internal debug or admin endpoints
   - `mobile/` must not become a provider-secret entry surface
3. still-open bounded follow-up
   - the exact native auth transport adapter remains an explicit follow-up
     after the shared resource baseline, not a hidden assumption inside the
     stack choice
4. current execution direction
   - user direction on 2026-04-25 freezes the mobile lane after this stack
     decision
   - near-term implementation should stay on `web + backend`
   - the mobile scaffold should restart later using this frozen baseline

## First-Party UI Language Boundary (2026-04-25)

Fresh product direction now resolves one UX-sensitive language split for the
first-party web and future mobile clients.

1. approved UI-language direction
   - the product may expose one explicit GUI language selector for the
     first-party shell
   - that selector controls interface copy only
   - the selector should use language label plus flag icon in the user-facing
     UI pattern
2. approved conversation-language direction
   - the language used when talking with the personality remains runtime-owned
   - it continues to be chosen live from current interaction, continuity, and
     learned signals instead of a manual UI setting
3. required architecture constraint
   - do not overload the current conversation-language continuity field as the
     new GUI language field
   - if implementation needs a persisted UI locale, it should use a separate
     backend-owned app-facing setting
4. approved settings cleanup direction
   - `response_style` and `collaboration_preference` should leave the
     product-facing settings form
   - those behaviors remain runtime-shaped from history, time, and interaction
     context rather than user-managed static controls
5. current execution direction
   - the next UX/UI planning lane should freeze this split before route-level
     settings redesign

## Multimodal Telegram And App Boundary (2026-04-25)

Fresh user-driven analysis now highlights a real product gap just below the
current text-first Telegram baseline.

1. current repo fact
   - canonical contracts describe text-first event ingestion and text-first
     response delivery through Telegram or API
   - project truth still records Telegram delivery as single-message and
     plain-text without richer channel-aware policy
   - user-reported Telegram behavior suggests photo-plus-caption input is not
     yet a trustworthy foreground path and should not be treated as random
     transport noise
2. decision still open
   - the repo does not yet freeze one explicit multimodal event and delivery
     boundary for:
     - photo context
     - voice-note-to-text intake
     - generated image reply plus caption
3. required architecture constraints
   - multimodal ingress must still normalize into one shared event contract
   - action must remain the only owner of provider media fetch, upload, and
     outbound media send methods
   - Telegram and a later first-party app should share one transport-neutral
     cognitive contract rather than separate reasoning paths
   - raw media payloads must not bypass the existing normalization or
     planning -> expression -> action boundary
4. likely next doc or implementation slice after the current readiness-truth
   and channel-aware delivery work
   - freeze a bounded multimodal payload shape for normalized event input
   - freeze a bounded multimodal response-execution handoff
   - decide whether photo understanding is direct model input, action-owned
     preprocessing, or both under explicit permission and evidence rules
   - decide what operator-visible health or incident surfaces prove the media
     path is working instead of silently falling back to text-only behavior

## Core V1 Time-Aware Planning Revision (2026-04-24)

The approved product and architecture revision now treats core no-UI `v1` as:

- stable Telegram or API conversation
- bounded web search and page reading
- tool-grounded learning
- internal time-aware planned work

Organizer-tool activation remains valuable but moves out of the core `v1`
closure gate and into a later extension or sync lane.

Key consequences:

1. future work should be modeled as internal planned work, not a standalone
   reminder subsystem
2. scheduler cadence should wake reevaluation, not become a second planner
3. if planned work becomes due, it still crosses the normal
   attention -> planning -> expression -> action boundary
4. bounded autonomous research should later build on the same planned-work
   model instead of inventing a separate autonomy engine

Queue seeded from this revision:

- `PRJ-635..PRJ-640` Core V1 Time-Aware Planned Work
- `PRJ-641..PRJ-642` Bounded Autonomous Research Windows

Current execution note:

- `PRJ-635` is now complete:
  - canonical architecture now freezes one explicit time-aware planned-work
    baseline for core no-UI `v1`
  - reminders, check-ins, routines, and future follow-ups now share one
    internal planned-work model instead of implying a separate reminder lane
  - organizer-tool activation remains a later extension or sync lane, not a
    hidden blocker for core `v1` closure
  - due planned work is now explicitly required to cross the existing
    `attention -> planning -> expression -> action` path for user-visible
    delivery
- `PRJ-636..PRJ-639` are now complete:
  - the repo now has one durable planned-work entity plus action-owned
    persistence, scheduler reevaluation, foreground due delivery, bounded
    recurrence rules, and context-aware delay-versus-skip handling
- `PRJ-640` is now complete:
  - behavior validation, `/health.v1_readiness`, exported incident evidence,
    and release smoke now prove the same time-aware planned-work contract
- `PRJ-641` is now complete:
  - bounded autonomous research windows are now frozen as `planned_work`
    variants with explicit trigger, read-only tool, and tool-grounded-learning
    guardrails
- `PRJ-642` is now complete:
  - architecture, testing, ops, planning, and context truth now describe the
    same core no-UI `v1` boundary and later organizer-tool extension
- the seeded queue through `PRJ-642` is now complete:
  - no seeded `READY`, `BACKLOG`, or `FUTURE` slice remains in this lane
  - future delivery or organizer follow-up should come from fresh analysis,
    not leftover backlog residue
- `PRJ-632..PRJ-633` are superseded by this revision:
  - they assumed organizer daily-use should stay part of the final core `v1`
    gate
  - that is no longer the approved product boundary
Future note after this lane:

- Telegram length and formatting still look like a likely next analysis topic,
  but they are no longer kept as a pre-seeded backlog after `PRJ-642`

## Fully Convincing No-UI V1 Analysis (2026-04-25)

Fresh comparison of canonical docs, runtime surfaces, regression proof, and
high-level repo truth now shows that core no-UI `v1` is implemented, but a
smaller set of truthfulness and delivery gaps remains before the product story
feels fully convincing.

1. truthful `v1_readiness`
   - not yet fully resolved
   - the approved product boundary now treats organizer tooling as a later
     extension, but some runtime and regression surfaces still mix organizer
     daily-use posture into the final no-UI `v1` acceptance story
   - some gate fields also remain static or surface-validity-oriented instead
     of being derived from live owner surfaces
2. channel-aware Telegram delivery
   - not yet resolved
   - the delivery layer still sends one raw Telegram message without explicit
     segmentation or formatting policy
   - this is now the clearest user-facing quality gap after the core-v1
     planning lane
3. high-level docs drift
   - partially resolved
   - canonical architecture is in better shape, but `docs/overview.md` and
     some runtime-reality wording still imply planned/deferred capability
     slices that are already live
4. organizer full provider activation and richer empathy rollout
   - intentionally not first in this queue
   - both remain useful later lanes, but fresh analysis says they are not the
     highest-signal blockers right now

Queue seeded from this analysis:

- `PRJ-647..PRJ-650` V1 Readiness Truth And Acceptance Boundary
- `PRJ-651..PRJ-654` Foreground Capability And Time Awareness
- `PRJ-643..PRJ-646` Channel-Aware Delivery Baseline

Current execution note:

- `PRJ-647` is now complete:
  - canonical architecture, planning truth, testing guidance, and runtime
    reality now explicitly separate core no-UI `v1` gates from mirrored
    extension posture
  - organizer daily-use posture is now described as extension readiness rather
    than as a hidden blocker inside the post-`PRJ-642` core boundary
- `PRJ-648` is now the first `READY` slice:
  - the next remaining gap is to make `/health.v1_readiness` reflect that
    clarified boundary truthfully
- fresh code analysis now also records a narrower follow-up gap after
  `PRJ-650`:
  - planning, planned work, bounded web search, page reading, and
    tool-grounded learning are implemented and tested
  - but current-time awareness and capability awareness remain only partially
    explicit in the foreground turn contract and reply-prompt surfaces
  - the next post-`PRJ-650` lane should therefore make these capabilities
    explicitly knowable to the active turn before channel-delivery polish
- dormant `PRJ-643..PRJ-646` stay useful:
  - they are now explicitly sequenced after `PRJ-654`, not discarded
  - the topic was real, but fresh analysis says readiness truth should come
    first, followed by foreground awareness of already-implemented capability
    posture

## Final Operational V1 Closure Analysis (2026-04-24)

Fresh comparison of canonical docs, repository truth, and live production
health now shows that the remaining work is no longer "make the runtime
exist". It is "make the personality truly daily-usable through Telegram/API
with bounded external knowledge and organizer tools".

1. production truth and deploy automation
   - not yet fully resolved
   - live production can be healthy, but repo truth and deployed truth can
     still drift
   - user-observed Coolify behavior still shows that auto-deploy is not yet a
     trusted primary path
   - the repo now needs one explicit final operator baseline for:
     - which surfaces must match between repo and live production
     - how deploy provenance is verified
     - when manual redeploy remains an exception rather than routine behavior
2. live web-knowledge workflows
   - partially resolved
   - bounded search/browser slices already exist and are behavior-proven at the
     contract level
   - but the repo still lacks one explicit production workflow baseline for:
     - asking the personality to inspect a website
     - reading bounded page content
     - turning that into a useful answer
     - optionally retaining bounded learned knowledge through the existing
       action -> memory path
3. durable role/skill/tool-authorization catalog
   - partially resolved
   - canonical architecture now allows durable role presets, durable skill
     descriptions, and per-user tool authorization records
   - backend capability catalog now exists, but runtime still lacks the fuller
     operator-facing catalog of:
     - approved role presets
     - skill-description metadata
     - per-user tool authorization posture
     - what is merely described versus actually executable
4. organizer-tool provider activation
   - partially resolved
   - organizer-tool stack and activation snapshot already exist
   - the missing step is to make this stack feel production-real for the user:
     - provider credentials and opt-in posture must be visible and actionable
     - acceptance must cover actual daily-use flows, not only abstract provider
       readiness
5. final no-UI `v1` closure
   - not yet explicitly resolved
   - canonical `v1` is backend-first and no-UI, but still should feel like a
     usable personality:
     - stable conversation
     - reminder/planning/follow-up continuity
     - bounded internet reading
     - live organizer/tool posture
     - truthful learned-state and capability introspection

Queue seeded from this analysis:

- `PRJ-614..PRJ-617` Production Truth And Deploy Automation Closure
- `PRJ-618..PRJ-621` Live Web-Knowledge Workflow Activation
- `PRJ-622..PRJ-625` Durable Role/Skill/Tool-Authorization Catalog
- `PRJ-626..PRJ-629` Organizer-Tool Daily-Use Activation
- `PRJ-630..PRJ-633` Final No-UI V1 Acceptance Closure

Current execution note:

- `PRJ-613` is complete:
  - the remaining queue is now explicitly about final operational `v1`
    closure, not generic hardening
  - the personality is already architecturally coherent, but the next slices
    must close the remaining gap between healthy backend contracts and actual
    daily use through Telegram/API plus authorized external reads/tools

## Post-V1 Tool Activation And Deployment Automation Analysis (2026-04-24)

Fresh comparison of canonical docs, runtime reality, live production release
smoke, and operator observations now shows a new class of remaining gaps.
Core runtime topology is healthy, but the system is not yet fully ready for
real-world tool onboarding and tool-grounded learning.

1. Coolify deployment automation reliability
   - baseline now frozen through `PRJ-597`
   - production can be healthy after a deploy, but user-observed behavior
     shows that pushes do not always trigger an automatic deploy on Coolify
   - the repo now has one explicit baseline for what "repo-driven deploy"
     means:
     - push `main`
     - Coolify source automation should enqueue deployment for the canonical
       app
     - operator verifies target commit in Coolify deployment history
     - operator verifies production with release smoke
   - remaining work is evidence and enforcement:
     - machine-visible proof that primary automation fired
     - explicit distinction between primary automation, webhook fallback, and
       UI redeploy fallback
2. organizer-tool credential activation
   - not yet resolved
   - `/health.connectors.organizer_tool_stack` is machine-visible and
     behavior-proven, but live production still reports
     `provider_credentials_missing`
   - the repo needs one explicit baseline for when the first ClickUp +
     Calendar + Drive stack becomes actually provider-ready
   - `PRJ-601` now exposes a shared `activation_snapshot` with
     provider-specific missing settings and next actions
   - `PRJ-602` now proves the same activation posture through release smoke,
     incident evidence, and incident-evidence bundles
3. tool-grounded learning capture
   - not yet resolved
   - bounded search, browser, and connector reads already exist, but there is
     still no explicit contract for how approved external reads become durable
     learned knowledge without creating a second tool-execution path
   - any solution must keep learning inside memory/reflection ownership and
     must not imply self-modifying executable skill learning
   - `PRJ-604` now freezes the bounded architecture contract for this lane
   - `PRJ-605` now makes that contract live through action-owned capture and
     memory-owned persistence of tool-grounded semantic conclusions
4. capability catalog for future UI/admin work
   - not yet resolved
   - learned-state and API-readiness surfaces exist, but future UI or admin
     work still lacks one clearer backend catalog that combines approved tools,
     provider readiness, selected role posture, and metadata-only skills

Queue seeded from this analysis:

- `PRJ-597..PRJ-599` Coolify Deployment Automation Reliability
- `PRJ-600..PRJ-603` Organizer-Tool Credential Activation
- `PRJ-604..PRJ-607` Tool-Grounded Learning Capture
- `PRJ-608..PRJ-611` Capability Catalog And Future-UI Bootstrap

Current execution note:

- `PRJ-614` is complete:
  - the repo now has one explicit final operational no-UI `v1` closure
    baseline
  - daily-use `v1` is defined as live production where conversation
    reliability, bounded life-assistant behavior, truthful learned-state
    inspection, bounded web-knowledge posture, organizer daily-use posture,
    and deploy parity are green at the same time
  - rollback posture is now explicit: if deploy parity drifts or live external
    tool posture stops being production-real, the repo falls back to "no-UI
    `v1` baseline achieved in repo" rather than claiming final operational
    closure
- `PRJ-615` is now complete:
  - `/health.deployment`, exported incident evidence, repo-driven Coolify
    env/build args, and release smoke now expose one shared repo-vs-production
    parity contract
  - live release smoke now fails explicitly when production is still behind
    repo truth instead of silently passing without deploy-parity proof
- `PRJ-616` is now complete:
  - the canonical Coolify production app was corrected from `Public GitHub` to
    the GitHub App source `vps-luckysparrow`
  - the source repository path was corrected from the pre-rename
    `Wroblewski-Patryk/LuckySparrow` to `Wroblewski-Patryk/Personality`
  - local `origin` now matches the renamed repository, so repo push target and
    deploy-source truth no longer drift
- `PRJ-617` is now complete:
  - planning/context and ops truth now treat `Public GitHub` on the canonical
    production app as deployment drift instead of an acceptable source posture
- `PRJ-634` is now complete:
  - full deploy parity is now green in live production
  - the repo-owned compose contract uses `${APP_BUILD_REVISION:-unknown}`
  - the canonical Coolify app maps `APP_BUILD_REVISION=$SOURCE_COMMIT` as a
    runtime-only variable
  - shadowing `SOURCE_COMMIT=unknown` variables were removed from the app
    environment
  - live `runtime_build_revision` now matches local repo `HEAD` through release
    smoke
- `PRJ-618` is now complete:
  - the first live website-reading workflow is frozen as one bounded no-UI
    `v1` behavior baseline
  - direct URL review and search-first review now share the same canonical
    planning -> permission-gate -> action -> tool-grounded-learning path
  - bounded outputs, safety boundaries, and durable-learning posture are now
    explicit in architecture truth instead of inferred from existing tests
- `PRJ-619` is now complete:
  - backend truth now exposes one shared `website_reading_workflow` posture in
    `/health.connectors.web_knowledge_tools` and runtime
    `system_debug.adaptive_state["web_knowledge_tools"]`
  - that posture distinguishes direct URL review, search-first page review,
    selected provider path, bounded read semantics, and blockers or next
    actions without introducing a new browsing subsystem
- `PRJ-620` is now complete:
  - release smoke, debug incident evidence, and incident-evidence bundles now
    require the same bounded website-reading contract that `/health` exposes
  - bounded behavior proof continues to reuse `T14.1`, `T14.2`, and `T17.1`
    instead of inventing a second acceptance harness
- `PRJ-621` is now complete:
  - runtime reality, testing guidance, ops notes, and planning/context now all
    describe the same bounded website-reading proof path
- `PRJ-622` is now complete:
  - one explicit durable capability-record contract now freezes the boundary
    between:
    - description of role presets and skill records
    - runtime selection of a role or skill guidance for the current turn
    - per-user authorization of approved tools or bounded operations
  - that truth model explicitly rejects turning skill growth into hidden
    executable authority or turning authorization records into a second action
    engine
- `PRJ-623` is now the next active slice:
  - the next gap is to expose a fuller runtime-backed catalog for those
    durable records without inventing a parallel capability system
- `PRJ-623` is now complete:
  - `/health.capability_catalog` and internal inspection now expose a fuller
    durable capability-record catalog that separates described role or skill
    metadata from runtime selection surfaces and from tool authorization
    posture
  - authorization truth remains bound to existing connector permission gates
    and provider-readiness posture instead of becoming a second action engine
- `PRJ-624` is now complete:
  - release smoke now validates the capability-record truth model and the
    distinction between public read operations versus confirmation-gated
    organizer mutations
  - runtime behavior coverage now proves that selected work-partner skill
    metadata does not imply unrelated organizer write authority during bounded
    website-reading
- `PRJ-625` is now complete:
  - runtime reality, testing guidance, ops notes, planning, and context now
    all describe the same capability-record truth model and evidence path
  - no remaining docs wording in this lane should imply self-modifying
    executable skill learning or hidden tool authorization
- `PRJ-626` is now complete:
  - the first practical daily-use organizer workflows are now frozen on top of
    the existing ClickUp, Calendar, and Drive production stack
  - role or skill selection still does not imply organizer execution authority
  - internal planning remains primary while external organizer tools remain
    action-owned helpers
- `PRJ-627` is now complete:
  - runtime now exposes one clearer daily-use organizer readiness summary per
    workflow instead of only provider activation details
  - `v1_readiness` now reflects that same organizer readiness truth in a more
    product-facing form
- `PRJ-628` is now complete:
  - release smoke, incident-evidence bundles, and behavior validation now
    prove the first organizer daily-use baseline end to end
- `PRJ-629` is now complete:
  - runtime reality, testing guidance, ops, planning, and repository context
    now describe the same organizer daily-use proof path and its parity with
    `/health.v1_readiness`
- `PRJ-630` is now complete:
  - `/health.v1_readiness` now exposes the final no-UI `v1` acceptance bundle
    contract with named gate states and canonical runtime surfaces
- `PRJ-631` is now complete:
  - final `T18.1..T18.2` scenarios now prove website-reading recall and
    organizer follow-up inside the no-UI `v1` acceptance lane
- `PRJ-632` is now the next active slice:
  - the next gap is to capture live production evidence for that final
    acceptance contract
- `PRJ-598` is complete in repo truth: deployment provenance is now
  machine-visible in `/health.deployment`, deploy webhook evidence, exported
  incident evidence, and release smoke.
- `PRJ-599` is complete as the docs/context sync slice for deployment
  provenance.
- `PRJ-600..PRJ-602` are complete:
  - the production organizer-tool credential baseline is frozen
  - `/health.connectors.organizer_tool_stack` now exposes one actionable
    activation snapshot
  - release smoke plus incident evidence now validate the same activation
    snapshot and next-action posture
- `PRJ-603` is complete:
  - runtime reality, testing guidance, ops notes, planning truth, and
    repository context now describe the richer organizer-tool activation
    snapshot and provider-specific next-action posture consistently
- `PRJ-604..PRJ-605` are complete:
  - the bounded tool-grounded learning contract is frozen
  - approved external reads now persist bounded tool-grounded semantic
    conclusions
- `PRJ-606..PRJ-607` are complete:
  - behavior validation and release evidence now prove the same bounded
    tool-grounded learning contract
  - runtime reality, testing guidance, ops notes, and context truth now
    describe that proof path consistently
- `PRJ-608` is complete:
  - canonical architecture now freezes one bounded backend
    capability-catalog contract
  - the catalog is defined as an aggregation over existing backend truth from
    `/health.api_readiness`, `/health.learned_state`, `/health.role_skill`,
    `/health.connectors`, and bounded internal inspection/debug surfaces
  - the catalog is explicitly not a new execution owner, a second
    authorization matrix, or a self-modifying skill-learning path
- `PRJ-609..PRJ-611` are now complete:
  - `/health.capability_catalog` and internal
    `GET /internal/state/inspect?user_id=...` expose one bounded backend
    capability-catalog payload for future UI/admin bootstrap
  - release smoke and incident-evidence bundle validation now pin the same
    bounded capability-catalog contract
  - runtime reality, testing guidance, ops notes, planning truth, and
    repository context now describe the same capability-catalog baseline
- the queue seeded through `PRJ-611` is complete and no seeded execution slice
  remains in this lane.

## Post-V1 Architecture Gap Analysis (2026-04-23)

Fresh comparison of canonical docs, runtime reality, and live production
`/health` shows that the biggest remaining gaps are no longer basic runtime
survival. The next queue should focus on the following unresolved or only
partially resolved areas:

1. attention ownership
   - resolved through `PRJ-576..PRJ-579`
   - production now runs `coordination_mode=durable_inbox`
   - release, incident-evidence, and behavior-validation proof are now part of
     the live durable-attention baseline
2. proactive production posture
   - resolved through `PRJ-580..PRJ-583`
   - cadence ownership remains externalized and production now runs bounded
     opt-in follow-up
   - release smoke, exported `incident_evidence`, and behavior-validation proof
     now verify the same live proactive owner posture
3. retrieval provider baseline
   - resolved for planning posture through `PRJ-584`
   - steady-state production baseline remains `openai_api_embeddings`
   - `local_hybrid` remains the bounded transition owner and deterministic
     remains compatibility fallback only
   - runtime alignment and strict release proof completed in `PRJ-585..PRJ-586`
4. learned-state and personality-growth introspection
   - resolved through `PRJ-588..PRJ-591`
   - `/health.learned_state`, internal inspection, release smoke, and
     incident-evidence bundles now agree on one richer bounded contract for
     preference summaries, knowledge summaries, reflection growth summaries,
     role/skill visibility summaries, and planning continuity
   - learned growth remains bounded to backend-owned metadata and summaries,
     not self-modifying executable skill learning
5. organizer-tool production posture
   - now resolved through `PRJ-592..PRJ-595`
   - the first bounded production organizer-tool stack is now frozen as:
     - ClickUp `create_task`, `list_tasks`, `update_task`
     - Google Calendar `read_availability`
     - Google Drive `list_files`
   - `PRJ-593` exposed one shared readiness surface through
     `/health.connectors.organizer_tool_stack`
   - `PRJ-594` added smoke, incident-evidence, incident-bundle, and behavior
     proof for that frozen baseline
   - `PRJ-595` synchronized canonical docs and repository context for the same
     agreed posture

Queue seeded from this analysis:

- `PRJ-576..PRJ-579` Durable Attention Production Cutover
- `PRJ-580..PRJ-583` Proactive Opt-In Production Activation
- `PRJ-584..PRJ-587` Retrieval Provider Baseline Alignment
- `PRJ-588..PRJ-591` Learned-State And Personality-Growth Introspection
- `PRJ-592..PRJ-595` Production Organizer-Tool Readiness

Resolved retrieval-baseline decision in `PRJ-584` (2026-04-23):

- production retrieval keeps `openai_api_embeddings` as the steady-state target
  baseline
- `local_hybrid` remains a bounded transition owner, not the final production
  owner
- deterministic execution remains the explicit compatibility fallback posture
- provider, model, and source-rollout enforcement stays `warn` during
  `PRJ-585` so live runtime alignment could land before `PRJ-586` makes drift
  release-blocking

Resolved proactive production-policy decision in `PRJ-580` (2026-04-23):

- production proactive is now frozen as bounded opt-in follow-up
- cadence ownership remains `external_scheduler`
- candidate selection remains limited to opted-in users with active work or
  time-checkin triggers
- delivery target remains bounded to Telegram direct message via recent chat id
  or numeric user-id fallback
- rollback posture remains explicit:
  - return production to `PROACTIVE_ENABLED=false`

Resolved first cutover-decision in `PRJ-576` (2026-04-23):

- durable inbox is now frozen as the target production attention owner
- production switch proof must be read from:
  - `/health.attention`
  - `/health.runtime_topology`
  - `/health.conversation_channels.telegram`
  - release smoke
- rollback posture remains explicit:
  - return to `ATTENTION_COORDINATION_MODE=in_process` until burst-assembly,
    cleanup, and reply-order semantics are stable again

Durable-attention lane completion update (`PRJ-577..PRJ-579`, 2026-04-23):

- production now runs the durable attention baseline:
  - `/health.attention.coordination_mode=durable_inbox`
  - `/health.attention.contract_store_mode=repository_backed`
  - `/health.runtime_topology.attention_switch.selected_mode=durable_inbox`
- release and incident proof now also includes:
  - exported `incident_evidence.policy_posture["attention"]`
  - exported `incident_evidence.policy_posture["runtime_topology.attention_switch"]`
  - release smoke
  - behavior-validation burst-coalescing regression coverage
- the next unresolved lane is retrieval-provider baseline alignment, not
  attention or proactive production posture

## V1 Productization Stance (2026-04-22)

- `v1` is now interpreted as a no-UI but production-usable life-assistant
  backend:
  - Telegram or API conversation must work reliably in production
  - reminders, planning, follow-up, and reflection-backed continuity must be
    behavior-level reality, not only contract-level truth
  - backend inspection surfaces must expose what the personality learned,
    selected, and planned so a later UI can be built on top of real runtime
    truth
- `v2` begins when a dedicated UI or admin product layer is added on top of
  those stable backend surfaces.
- work-partner is treated as a role of the same personality, not as a second
  persona or a UI-only feature.
- skills remain metadata-only capability hints unless a later approved
  architecture change explicitly expands their authority.
- tool execution remains action-owned:
  - learned knowledge belongs to memory and reflection outputs
  - selected skill metadata may explain capability posture
  - external tools such as search, browser, calendar, ClickUp, or drive must
    stay behind explicit planning and action boundaries
- user-reported Telegram no-response posture is treated as a real `v1`
  blocker and should be addressed before broader capability expansion is
  considered done.
- `PRJ-541..PRJ-542` now turn that blocker into explicit runtime truth:
  - `/health.conversation_channels.telegram` is the canonical operator surface
    for Telegram round-trip posture
  - exported `incident_evidence` and release smoke now require
    `conversation_channels.telegram` posture instead of treating Telegram
    reliability as log-only evidence
- `PRJ-548..PRJ-550` now freeze and stabilize learned-state introspection:
  - `/health.learned_state` is the canonical health-level readiness surface
  - `GET /internal/state/inspect?user_id=...` is the bounded internal
    inspection surface for future UI or admin callers
  - exported `incident_evidence.policy_posture["learned_state"]` now carries
    the same owner and internal-path contract for release or incident review
- `PRJ-552` now freezes the architecture choice for web knowledge tools:
  - web search and browser access extend the existing action-owned external
    capability family
  - they are not "skills that execute tools" and not a second browsing
    subsystem outside planning/action validation
  - the next implementation slices should therefore reuse shared
    permission-gate and health/debug visibility patterns
- `PRJ-553..PRJ-554` now make that baseline runtime-visible:
  - shared typed intents and permission gates exist for `knowledge_search` and
    `web_browser`
  - `/health.connectors.web_knowledge_tools` and
    `system_debug.adaptive_state["web_knowledge_tools"]` now expose the same
    selected provider-backed posture for the approved first live slices
- `PRJ-556` now freezes the first provider-backed expansion choices:
  - `duckduckgo_html` for bounded web search
  - `generic_http` for bounded page-read browsing
  - `clickup:update_task` as the next organization mutation path
- `PRJ-557..PRJ-558` now make those slices execution- and behavior-real:
  - DuckDuckGo web search, generic HTTP page reads, and ClickUp task updates
    execute through the existing planning -> permission-gate -> action path
  - behavior validation now proves the same boundary through `T14.1..T14.3`
    instead of relying only on unit or integration regressions
- `PRJ-560` now freezes the backend work-partner baseline:
  - work-partner is a role of the same personality, not a second persona
  - it may combine bounded metadata-only skills with already approved tools
  - it remains inside the same role-selection, planning, permission-gate, and
    action boundary as every other role
- `PRJ-561..PRJ-562` now make that baseline backend-real:
  - explicit `work_partner` turns can be selected through the shared
    role-selection owner
  - the role carries a bounded skill mix and machine-visible role-skill
    policy posture
  - behavior validation proves work-partner organization and decision support
    through `T15.1..T15.2`
- `PRJ-564` now freezes the no-UI `v1` release gate:
  - conversation reliability
  - life-assistant workflow proof
  - learned-state inspection readiness
  - approved tooling and work-partner posture
  must be readable from one backend-facing acceptance bundle before `v1` is
  treated as closed
- `PRJ-565..PRJ-567` now close that lane:
  - `/health.v1_readiness` is the explicit no-UI `v1` acceptance surface
  - `/health.api_readiness` and internal
    `GET /internal/state/inspect?user_id=...` are the backend-owned starting
    point for later `v2` UI integration
  - the seeded `v1` queue is complete; any next queue should come from fresh
    production/runtime analysis rather than from unfinished `v1` backlog
- `PRJ-571` now seeds that next queue from live production truth:
  - Telegram and migration-first startup are repaired
  - the clearest remaining production drift was still operational:
    - reflection queue drain remained `in_process`
    - scheduler cadence ownership remained `in_process`
  - the next execution queue therefore externalized those owners before
    widening capability growth again
- `PRJ-572..PRJ-574` are now complete:
  - Coolify production reflection ownership is now aligned with the deferred
    external-driver baseline
  - Coolify production cadence ownership is now aligned with the external
    scheduler baseline
  - production `/health` and release smoke are now the canonical proof path
    for both owner cutovers
  - no seeded post-v1 production-hardening task remains open
- the completed `v1` execution queue prioritized:
  - production conversation reliability
  - life-assistant workflow activation
  - learned-state inspection surfaces
  - architecture-first web search and browser tooling
  - work-partner role orchestration
  - final `v1` release closure plus `v2` backend API readiness

## Target-State Convergence Stance (2026-04-20)

- For the next execution queue, prefer slices that reduce transitional wiring
  and move code toward the canonical architecture even when the current
  implementation can support temporary shortcuts.
- Treat `docs/architecture/02_architecture.md`,
  `docs/architecture/15_runtime_flow.md`, and
  `docs/architecture/16_agent_contracts.md` as the target shape for new work.
  Use `docs/implementation/runtime-reality.md` to describe current constraints
  and rollout guardrails, not to redefine the architecture.
- Resolve the currently open decision clusters through the queued groups in
  `docs/planning/next-iteration-plan.md` and
  `.codex/context/TASK_BOARD.md`:
  - `PRJ-276..PRJ-279`: foreground runtime convergence (`3a`, `3b`)
  - `PRJ-280..PRJ-283`: background reflection topology (`1`, `12`)
  - `PRJ-284..PRJ-287`: production memory retrieval rollout (`5`, `5d`,
    `5e`, `9a`)
  - `PRJ-288..PRJ-291`: adaptive cognition governance (`4`, `4a`, `10`,
    `10a`, `10b`, `11`)
  - `PRJ-292..PRJ-295`: attention/proposal execution boundary (`12a`, `12b`,
    `12c`)
  - `PRJ-296..PRJ-299`: operational hardening and release truth (`2`, `3`,
    `6`, `7`)
  - `PRJ-301..PRJ-304`: reflection deployment baseline and readiness rollout
    (`1`, `12` follow-up)
  - `PRJ-306..PRJ-309`: post-reflection hardening decisions (`2` follow-up,
    `3` follow-up, `12` follow-up)
  - `PRJ-310..PRJ-313`: runtime behavior testing architecture and internal
    validation surface (`3`, `5`, `12`) - complete
  - `PRJ-314..PRJ-317`: memory/continuity/failure validation scenarios and
    release gating (`5`, `8`, `9`, `12`) - complete
  - `PRJ-318..PRJ-321`: internal debug ingress migration
    (`3` implementation follow-up) - complete
  - `PRJ-322..PRJ-325`: scheduler externalization and attention ownership
    (`1`, `12`, `12a` implementation follow-up) - complete
  - `PRJ-326..PRJ-329`: identity, language, and profile boundary hardening
    (`8`, `9`) - complete
  - `PRJ-330..PRJ-333`: relation lifecycle and trust influence rollout
    (`9a`, `10`, `12`) - complete
  - `PRJ-334..PRJ-337`: goal/task inference and typed-intent expansion
    (`5a`, `10a`, `12c`) - complete
  - `PRJ-339..PRJ-342`: manual runtime reliability fixes
    (`3`, `13`) - complete
  - `PRJ-343..PRJ-346`: relation-aware inferred promotion governance
    (`9a`, `10a`) - complete
  - `PRJ-347..PRJ-350`: behavior-validation CI-ingestion follow-up
    (`13`) - complete
  - `PRJ-351..PRJ-354`: behavior-validation artifact governance
    (`13`) - complete
  - `PRJ-355..PRJ-358`: deployment-trigger SLO instrumentation
    (`7`) - complete
  - `PRJ-359..PRJ-360`: behavior-validation artifact compatibility governance
    (`13`) - complete
  - `PRJ-361..PRJ-362`: attention timing baseline governance (`12a`) - complete
  - `PRJ-363..PRJ-366`: connector boundary execution policy
    (`12c`) - complete
  - `PRJ-367..PRJ-370`: typed-intent coverage for future writes
    (`10a`) - complete
  - `PRJ-371..PRJ-374`: action-delivery extensibility (`3a`) - complete
  - `PRJ-375..PRJ-378`: compatibility sunset readiness (`2`, `3`) - complete
  - `PRJ-379..PRJ-382`: background adaptive-output convergence
    (`1`, `5`, `9a`) - complete
  - `PRJ-383..PRJ-386`: durable attention-inbox rollout baseline
    (`12`, `12a`) - complete
  - `PRJ-387..PRJ-390`: role-and-skill capability convergence (`4`, `6`) - complete
  - `PRJ-391..PRJ-394`: retrieval-depth and theta-governance baseline
    (`5`, `5d`, `10b`) - complete
  - `PRJ-395..PRJ-398`: role-selection evidence baseline (`4`, `10b`) - complete
  - `PRJ-399..PRJ-402`: affective-assessment rollout policy (`4a`) - complete
  - `PRJ-403..PRJ-406`: reflection scope governance (`5c`) - complete
  - `PRJ-407..PRJ-410`: durable attention contract-store rollout (`12a`) - complete
  - `PRJ-411..PRJ-414`: identity/profile ownership and language continuity
    governance (`8`, `9`) - complete
  - `PRJ-415..PRJ-418`: runtime topology finalization
    (`1`, `3b`, `12`, `12a`, `12b`) - complete
  - `PRJ-419..PRJ-422`: production boundary hardening (`2`, `3`) - complete
  - `PRJ-423..PRJ-426`: retrieval and affective-memory productionization
    (`5`, `5b`, `5d`, `5e`) - complete
  - `PRJ-427..PRJ-430`: adaptive identity and role-governance evolution
    (`4`, `4a`, `8`, `9`, `10`, `11`) - complete
  - `PRJ-431..PRJ-434`: goal/task and proposal governance (`5a`, `12b`) - complete
  - `PRJ-435..PRJ-438`: scheduler and connector capability convergence
    (`12`, `12a`, `12c`) - complete
  - `PRJ-439..PRJ-442`: deployment standard and release-reliability closure
    (`6`, `7`) - complete
  - `PRJ-444..PRJ-447`: shared debug-ingress vocabulary convergence (`3`) - complete
  - `PRJ-448..PRJ-451`: affective diagnostics convergence (`4a`) - complete
  - `PRJ-452..PRJ-453`: embedding execution-class diagnostics (`5d`, `5e`) - complete
  - `PRJ-455..PRJ-457`: attention contract-store docs convergence (`12a`) - complete
  - `PRJ-458..PRJ-460`: proposal inventory and operator health docs convergence (`3`, `12b`) - complete
  - `PRJ-461..PRJ-463`: affective and retrieval health visibility docs convergence (`4a`, `5d`) - complete
- post-`PRJ-453` state has no remaining seeded `READY`; the next architecture
  slice should again be derived from any newly discovered post-convergence
  follow-up instead of inventing a new queue without a concrete runtime or
  operational driver.
- historical queue-seeding notes for Groups 41 through 56 are intentionally
  omitted from this header now that those groups are complete; the decisions
  below remain as architecture history plus future reference unless a new
  follow-up reopens them explicitly.
- `PRJ-454` cleaned the remaining top-level planning drift after Groups 57
  through 59 so this file, the task board, project state, and the next
  iteration plan all describe the same post-convergence follow-up stance.
- `PRJ-457` closes the remaining durable-attention docs drift so canonical
  contracts, runtime reality, ops guidance, and planning surfaces all describe
  the same repository-backed contract-store baseline.
- `PRJ-460` closes the remaining docs drift around persisted subconscious
  proposal inventory and the operator-facing meaning of post-convergence health
  surfaces used in release checks and triage.
- `PRJ-463` closes the remaining runbook/planning drift around `/health.affective`
  and `semantic_embedding_execution_class`, so empathy triage and retrieval
  execution posture are explicit operator surfaces in the same way as other
  post-convergence health diagnostics.
- architecture-conformance analysis on 2026-04-22 identified seven new
  post-convergence lanes that should be handled before another broad planning
  pass:
  - `PRJ-464..PRJ-467`: migration parity and schema governance - complete
  - `PRJ-468..PRJ-471`: canonical docs consistency sweep - complete
  - `PRJ-472..PRJ-475`: connector execution productionization
  - `PRJ-476..PRJ-479`: retrieval provider completion - complete
  - `PRJ-480..PRJ-483`: background worker externalization - complete
  - `PRJ-484..PRJ-487`: proactive runtime activation - complete
  - `PRJ-488..PRJ-491`: role/skill maturity and behavior-validation expansion - complete
- this queue is intentionally ordered by architectural risk:
  deployment/schema truth first, then canonical docs consistency, then
  productionization of still-rollout subsystems, and finally behavior-proof
  expansion.
- `PRJ-464..PRJ-467` are now complete:
  - Alembic head matches the full live durable-table baseline again
  - migration parity is regression-tested through fresh `upgrade head`
    instead of inferred only from metadata or runtime docs
  - the next active lane is canonical architecture-doc consistency
- `PRJ-468..PRJ-471` are now complete:
  - older canonical docs no longer contradict the `planning -> expression ->
    action` boundary or the runtime-owned post-action follow-up split
  - `docs/README.md` and `docs/overview.md` now explicitly direct readers to
    `02/15/16` as the canonical contract set
  - the next active lane is connector execution productionization
- `PRJ-472..PRJ-475` are now complete:
  - the first live provider-backed connector path is now explicit and narrow:
    `task_system:create_task` for ClickUp when both `CLICKUP_API_TOKEN` and
    `CLICKUP_LIST_ID` are configured
  - `calendar`, `cloud_drive`, and other task-system operations remain
    policy-only on purpose until the architecture grows a bounded pre-action
    read posture and more provider adapters
  - `/health.connectors.execution_baseline` now exposes whether the selected
    live connector path is configured or still in `credentials_missing` posture
  - the next active lane is retrieval provider completion
- `PRJ-476..PRJ-479` are now complete:
  - the target provider-owned retrieval baseline is now explicit:
    `openai_api_embeddings` is the intended production owner when
    `OPENAI_API_KEY` is configured
  - `local_hybrid` remains a local transition owner and deterministic remains
    the explicit compatibility fallback baseline
  - `/health.memory_retrieval` now exposes machine-readable
    `semantic_embedding_production_baseline`,
    `semantic_embedding_production_baseline_state`, and
    `semantic_embedding_production_baseline_hint` fields for rollout triage
  - the next active lane is background worker externalization
- `PRJ-480..PRJ-483` are now complete:
  - deferred reflection externalization now has one explicit policy owner and
    one canonical queue-drain entrypoint (`scripts/run_reflection_queue_once.py`)
  - `/health.reflection.external_driver_policy` and release smoke now expose
    machine-visible external-driver baseline posture
  - `in_process` reflection remains explicit compatibility posture, not the
    target deferred external-worker baseline
  - the next active lane is proactive runtime activation
- `PRJ-484..PRJ-487` are now complete:
  - proactive runtime now has one explicit policy owner for cadence owner,
    delivery-target baseline, opted-in candidate selection, and anti-spam
    thresholds
  - in-process scheduler ownership can now emit bounded proactive wakeups
    through repository-backed candidate selection and runtime execution
  - `/health.proactive` plus scheduler proactive tick summaries now expose
    live proactive posture for operator triage
  - behavior validation now covers delivery-ready versus anti-spam-blocked
    proactive outcomes
  - the next active lane is role/skill maturity and behavior-validation
    expansion
- `PRJ-488..PRJ-491` are now complete:
  - skills remain an explicit metadata-only capability layer that can inform
    role and planning but cannot execute tools or side effects on their own
  - `/health.role_skill` and runtime debug now expose the same shared
    role/skill boundary policy
  - behavior validation now covers role/skill boundary posture, connector
    execution posture, proactive cadence behavior, and deferred reflection
    enqueue expectations in one CI gate flow
- post-queue architecture review on 2026-04-22 identifies six new hardening
  lanes that should be handled before the next broad analysis pass:
  - `PRJ-492..PRJ-495`: debug ingress retirement and admin boundary closure
  - `PRJ-496..PRJ-499`: external scheduler ownership rollout
  - `PRJ-500..PRJ-503`: connector read posture and provider expansion baseline
  - `PRJ-504..PRJ-507`: retrieval lifecycle and source-rollout closure
  - `PRJ-508..PRJ-511`: reflection worker supervision and durability closure
  - `PRJ-512..PRJ-515`: observability export and incident-evidence baseline
- this queue is intentionally ordered around the most visible transitional
  runtime surfaces still left in implementation reality and release posture:
  shared debug ingress, app-local cadence ownership, partial connector live
  coverage, incomplete retrieval lifecycle closure, lightweight reflection
  supervision, and local-only observability evidence.
- `PRJ-492` is now complete:
  - debug ingress has one explicit shared policy owner with
    `/internal/event/debug` as the target dedicated-admin route
  - `/event/debug` and `/event?debug=true` remain temporary compatibility
    surfaces only, with retirement blockers frozen before any further runtime
    hardening
- `PRJ-493..PRJ-494` are now complete:
  - `/health.runtime_policy` exposes the dedicated-admin debug target posture
    plus machine-visible retirement blockers for remaining shared compat routes
  - startup logs and release smoke now consume the same dedicated-admin debug
    policy instead of inferring posture from partial fields
- `PRJ-496` is now complete:
  - maintenance and proactive cadence now have one explicit policy owner for
    the target `externalized` scheduler posture
  - app-local scheduler ownership remains a fallback-only compatibility posture,
    not the long-term production target
- `PRJ-496..PRJ-499` are now complete:
  - the repo now has one shared external cadence-owner baseline with canonical
    entrypoints (`scripts/run_maintenance_tick_once.py`,
    `scripts/run_proactive_tick_once.py`)
  - `/health.scheduler.external_owner_policy`, startup logs, and release smoke
    now expose the same target-vs-fallback posture for maintenance and
    proactive cadence ownership
- `PRJ-500` is now complete:
  - the next live read-capable connector expansion path is explicitly selected
    as `task_system:list_tasks` for ClickUp
  - calendar and cloud-drive reads remain policy-only until their read-scope
    and safe-output boundaries are narrowed further
- `PRJ-501..PRJ-503` are now complete:
  - ClickUp now has both the first live provider-backed mutation path
    (`task_system:create_task`) and the first live provider-backed read path
    (`task_system:list_tasks`)
  - `/health.connectors.execution_baseline` now distinguishes mutation and
    read-capable task-system paths from remaining policy-only connector
    families
- `PRJ-504` is now complete:
  - retrieval lifecycle now has one explicit owner for provider target,
    transition owner, compatibility fallback, steady-state refresh, and
    rollout completion posture
  - semantic+affective coverage is frozen as the foreground steady-state
    baseline, while relation remains an optional follow-on source family
- `PRJ-505..PRJ-507` are now complete:
  - `/health.memory_retrieval` now exposes one shared retrieval lifecycle
    owner together with provider drift posture, alignment state, and pending
    lifecycle gaps
  - release smoke now consumes the same lifecycle fields directly instead of
    inferring retrieval steady-state posture only from embedding-provider
    rollout diagnostics
  - implementation reality, ops guidance, testing guidance, planning, and
    context truth now describe the same steady-state retrieval lifecycle
    baseline
- `PRJ-508` is now complete:
  - deferred reflection supervision now has one explicit policy owner for
    target runtime mode, queue-drain owner, durable retry owner, queue-health
    states, and recovery actions before health/export surfaces consume those
    semantics
- `PRJ-509` is now complete:
  - `/health.reflection` now exposes that shared supervision snapshot directly,
    including backlog-pressure state, blocking signals, and recovery actions
  - deferred reflection supervision is now machine-visible in one surface
    instead of being reconstructed from task counts plus topology posture
- `PRJ-510` is now complete:
  - startup logs and release smoke now consume the same deferred-reflection
    supervision contract, so queue-pressure and recovery posture are visible in
    both runtime-startup and operator-smoke evidence
- `PRJ-511` is now complete:
  - canonical contracts, runtime reality, ops guidance, testing guidance,
    planning, and context truth now describe the same supervised deferred
    reflection baseline
- `PRJ-512` is now complete:
  - the repo now has one explicit observability export policy owner for the
    minimum incident-evidence contract beyond local logs and `/health`
  - `/health.observability` now exposes the required runtime evidence fields,
    required policy-posture surfaces, and the remaining machine-readable
    export gaps before artifact-based evidence is implemented
- `PRJ-513` is now complete:
  - debug responses now expose shared-owner `incident_evidence` for stage
    timings and machine-readable policy-posture snapshots
  - `/health.observability` now marks incident export as ready, and release
    smoke can verify exported incident evidence directly during debug-mode
    smoke runs
- `PRJ-514` is now complete:
  - behavior-validation artifacts can now optionally ingest exported runtime
    incident-evidence JSON through the same machine-readable gate flow
  - release smoke now consumes exported `incident_evidence` directly during
    debug-mode smoke runs, making observability evidence part of repeatable
    done-state
- `PRJ-515` is now complete:
  - architecture, runtime reality, ops guidance, testing guidance, planning,
    and context truth now describe the same observability export baseline
  - no seeded `READY` task remains after Group 75; the next slice should be
    derived from new runtime or operational analysis
- post-`PRJ-515` follow-up analysis on 2026-04-22 identifies six new
  production-facing lanes that should be handled before the next broad
  architecture review:
  - `PRJ-516..PRJ-519`: incident evidence bundle and retention
  - `PRJ-520..PRJ-523`: dedicated debug ingress compatibility retirement
  - `PRJ-524..PRJ-527`: calendar read connector baseline
  - `PRJ-528..PRJ-531`: cloud-drive metadata read baseline
  - `PRJ-532..PRJ-535`: external cadence cutover proof
  - `PRJ-536..PRJ-539`: relation retrieval source completion
- this queue is intentionally ordered around the remaining seams between
  explicit runtime policy surfaces and actual production operation:
  operator-grade evidence first, then real debug-route retirement, then
  bounded connector read expansion, then external cadence cutover proof, and
  finally the remaining relation-source retrieval decision.
- `PRJ-516` is now the first `READY` task and freezes the operator-facing
  incident-evidence artifact baseline before later retirement and cutover
  lanes depend on it.
- `PRJ-516` is now complete:
  - the operator-facing incident-evidence bundle is frozen as
    `manifest.json`, `incident_evidence.json`, `health_snapshot.json`, plus
    optional `behavior_validation_report.json`
  - naming posture and retention expectations are now explicit before helper
    implementation begins
- `PRJ-517` is now complete:
  - the canonical producer path is now `scripts/export_incident_evidence_bundle.py`
  - `/health.observability` exposes bundle-helper availability and entrypoint
    visibility through the existing observability owner
- `PRJ-518` is now complete:
  - release smoke can now validate a full bundle through
    `-IncidentEvidenceBundlePath`
  - regression coverage now pins both bundle success and partial-bundle
    failure posture
- `PRJ-519` is now complete:
  - canonical docs, runtime reality, testing guidance, ops guidance,
    planning, and context truth all describe the same bundle helper and smoke
    verification path
  - Group 76 is now complete and `PRJ-520` is now the next active task
- `PRJ-520` is now complete:
  - shared debug retirement now has one explicit cutover posture
    (`dedicated_internal_admin_route_primary_shared_routes_break_glass_then_remove`)
    plus one fixed checklist for operator path adoption, break-glass posture,
    query-compat shutdown, release-smoke proof, and rollback-note coverage
  - `/health.runtime_policy` now exposes retirement target, cutover posture,
    gate checklist, and gate state so later enforcement no longer depends on
    reconstructing posture from loose blocker fields alone
- `PRJ-521` is now complete:
  - dedicated-admin debug ingress is now the default runtime posture across
    environments
  - shared `/event/debug` now defaults to `break_glass_only`, and query compat
    `POST /event?debug=true` now defaults to disabled unless explicitly
    re-enabled for bounded rollback or migration handling
- `PRJ-522` is now complete:
  - release smoke now validates dedicated-admin-only debug posture directly
    from live `incident_evidence` and bundle-attached
    `incident_evidence.json`, not only from `/health.runtime_policy`
  - behavior-validation gates now fail when incident evidence drifts away from
    dedicated-admin-only debug posture or omits an explicit rollback-exception
    state (`shared_debug_break_glass_only|shared_debug_disabled`)
- `PRJ-523` is now complete:
  - canonical docs, runtime reality, testing guidance, ops notes, and context
    truth now all describe debug retirement proof through incident-evidence
    posture plus `/health.runtime_policy`
- `PRJ-524` is now complete:
  - the first bounded calendar read slice is frozen as
    `calendar:read_availability` with `provider_hint=google_calendar`
  - safe output posture is limited to action-owned availability evidence
    rather than raw event titles, attendees, or descriptions
- `PRJ-525` is now complete:
  - planner emits `calendar:read_availability` with
    `provider_hint=google_calendar` as the selected live-read baseline
  - action executes that intent through a bounded Google Calendar availability
    adapter and returns only normalized window evidence, busy-window counts,
    and free-slot preview notes
- `PRJ-526` is now complete:
  - `/health.connectors.execution_baseline` exposes
    `calendar.google_calendar_read_availability` as the bounded live-read
    posture for operators
  - readiness is now machine-visible as `credentials_missing` or
    `provider_backed_ready` without widening the existing connector boundary
- `PRJ-527` is now complete:
  - canonical contracts, runtime reality, testing guidance, ops notes, and
    context truth now describe the same bounded Google Calendar live-read
    baseline
- `PRJ-528` is now complete:
  - the first bounded cloud-drive metadata live-read slice is frozen as
    `cloud_drive:list_files` with `provider_hint=google_drive`
  - safe output posture is limited to file metadata evidence rather than
    document content, downloads, or write semantics
- `PRJ-529` is now complete:
  - planner emits `cloud_drive:list_files` with `provider_hint=google_drive`
    as the bounded metadata-read baseline
  - action executes that intent through a bounded Google Drive metadata adapter
    and returns only file metadata previews before normal delivery
- `PRJ-530` is now complete:
  - `/health.connectors.execution_baseline.cloud_drive.google_drive_list_files`
    exposes the bounded metadata-read path under one shared
    `provider_backed_when_configured` contract
  - operator posture now distinguishes `credentials_missing` from
    `provider_backed_ready` instead of leaving cloud-drive under one generic
    policy-only hint
- `PRJ-531` is now complete:
  - canonical contracts, runtime reality, testing guidance, ops notes,
    planning, and context truth all describe the same bounded Google Drive
    metadata-read baseline
- `PRJ-532` is now complete:
  - canonical contracts now freeze one external cadence cutover-proof
    baseline before runtime fields are added for recent last-run or
    duplicate-protection evidence
  - runtime reality and ops guidance now explicitly describe
    `/health.scheduler.external_owner_policy` as target-policy posture until
    those proof items become machine-visible
- `PRJ-533` is now complete:
  - `/health.scheduler.external_owner_policy` exposes maintenance and
    proactive run-evidence posture plus bounded duplicate-protection evidence
  - external cadence target-mode selection is now distinct from proven cutover
    readiness through `cutover_proof_ready`
- `PRJ-534` is now complete:
  - release smoke validates the new external cadence proof fields directly
    from `/health.scheduler.external_owner_policy`
  - behavior-validation gate logic validates the same proof surface from
    exported incident evidence and now fails on incomplete scheduler cutover
    payloads
- `PRJ-535` is now complete:
  - runtime reality, testing guidance, ops notes, planning, and context truth
    all describe the same external cadence cutover proof surface
  - Group 80 is complete and the next active slice is `PRJ-536` for relation
    retrieval source completion
- `PRJ-536` is now complete:
  - semantic plus affective are frozen as the steady-state retrieval
    completion baseline
  - relation embeddings remain an explicit optional follow-on source family,
    while relation records stay live adaptive inputs for foreground behavior
- `PRJ-537` is now complete:
  - retrieval code and `/health.memory_retrieval` now treat
    semantic+affective as the foreground rollout-completion baseline instead
    of implying relation is still a pending required source
  - relation source posture now has one explicit shared owner-level surface
    with machine-visible optional-family state, hint, recommendation, and
    enabled/alignment visibility
- `PRJ-538` is now complete:
  - runtime `system_debug.adaptive_state` and release smoke now require the
    same relation-source policy owner/state/enabled evidence as `/health`
  - focused regressions now pin both the green path and the missing-evidence
    smoke failure posture
- `PRJ-539` is now complete:
  - architecture, runtime reality, runtime behavior testing, ops guidance,
    testing guidance, and context truth now describe the same optional-family
    relation-source posture and its `/health`, `system_debug`, plus
    release-smoke evidence surfaces
  - Group 81 is complete and no seeded `READY` items remain in the current
    queue
- Introduce new feature surface only when it advances one of those convergence
  lanes or removes a documented transitional shortcut.

## Active Decisions

### 1. Reflection Placeholder vs Real Reflection

- Current repo fact:
  - runtime now has a lightweight background reflection worker backed by a durable `aion_reflection_task` queue in Postgres.
  - `RuntimeResult.reflection_triggered` is returned as `True` when reflection was successfully persisted and queued after episode persistence.
  - failed reflection tasks now retry with bounded backoff inside the app process.
  - `GET /health` now exposes a lightweight reflection snapshot with worker state and queue/task counts.
  - `PRJ-280` now defines explicit topology ownership across
    `in_process|deferred` modes, durable enqueue ownership, queue/retry
    semantics, and operator-visible health posture boundaries.
  - `PRJ-281` now extracts a shared enqueue/dispatch boundary contract consumed
    by both runtime follow-up and scheduler tick ownership paths.
  - `PRJ-282` now exposes worker-mode handoff posture through
    `/health.reflection.topology` and scheduler runtime logs so queue-drain and
    retry ownership are explicit for in-process and deferred operation.
  - `PRJ-283` now pins those ownership guarantees with regressions and keeps
    planning/context/ops docs aligned to the converged background topology.
  - `/health.reflection` now exposes deployment-readiness posture
    (`ready`, `blocking_signals`, baseline/selected runtime mode) so reflection
    mode migration no longer depends on log-only interpretation.
  - release smoke scripts now treat reflection deployment-readiness blockers as
    release-failing signals (with explicit fallback checks for older runtimes
    that do not yet expose the readiness snapshot).
- Decision (PRJ-301 reflection deployment baseline, 2026-04-20):
  - earlier production posture stayed on
    `REFLECTION_RUNTIME_MODE=in_process` while deferred dispatch matured.
  - `REFLECTION_RUNTIME_MODE=deferred` was initially a controlled rollout
    posture rather than the explicit baseline.
  - deferred rollout readiness requires all of:
    - explicit external dispatch owner runbook and on-call ownership
    - `/health.reflection.topology.external_driver_expected=true` and
      `queue_drain_owner=external_driver`
    - sustained queue stability in deferred posture (no recurring growth in
      pending backlog and no persistent `stuck_processing`/`exhausted_failed`)
    - scheduler/runtime logs proving mode-consistent dispatch handoff
      (`scheduler_tick_dispatch=false` with external-driver expectation)
    - release smoke and rollback steps updated to include reflection-mode
      readiness checks
- Resolved in `PRJ-415..PRJ-418` (2026-04-22):
  - production default switch from `in_process` to `deferred` is now gated by
    one explicit runtime-topology switch policy plus machine-visible readiness
    evidence instead of an open-ended operator judgment.
- Resolved follow-up in `PRJ-480..PRJ-483` (2026-04-22):
  - deferred reflection externalization now has one explicit policy owner,
    canonical queue-drain entrypoint, and release-smoke-visible health
    contract.
  - `in_process` reflection remains explicit compatibility posture, not the
    target external-worker production baseline.

### 2. Migration Strategy

- Current repo fact:
  - the repo now has an Alembic baseline rooted in the current SQLAlchemy metadata, with an initial revision under `migrations/versions/`.
  - startup now defaults to migration-first behavior and skips `create_tables()` unless `STARTUP_SCHEMA_MODE=create_tables` is explicitly enabled.
  - `GET /health` now exposes active non-secret runtime policy flags, including `startup_schema_mode` and `production_policy_enforcement`, so operators can verify migration policy posture on the live runtime.
  - `GET /health` now also exposes startup-policy mismatch preview, readiness, and guidance signals (`production_policy_mismatches`, `production_policy_mismatch_count`, `strict_startup_blocked`, `strict_rollout_ready`, `recommended_production_policy_enforcement`, `strict_rollout_hint`) for operator triage.
  - startup now emits a production warning when `STARTUP_SCHEMA_MODE=create_tables` to keep compatibility mode visible in runtime logs.
  - startup can now run in strict production-policy mode (`PRODUCTION_POLICY_ENFORCEMENT=strict`) and hard-fail on policy mismatch instead of warning-only behavior.
  - strict policy fail-fast behavior is pinned at lifespan entry by regression tests for both mismatch families (`EVENT_DEBUG_ENABLED=true` and `STARTUP_SCHEMA_MODE=create_tables`) to prevent startup-order drift.
  - runtime-policy mismatch detection now uses one shared helper owner so startup and `/health` stay aligned.
  - startup and `/health` now share the same strict-block semantics through shared readiness helpers (`strict_startup_blocked`, `strict_rollout_ready`).
  - startup now emits an informational strict-rollout hint when production runs in `warn` mode and strict rollout is ready.
  - production policy enforcement now resolves to `strict` by default in
    production when `PRODUCTION_POLICY_ENFORCEMENT` is unset, while explicit
    `warn` remains a controlled override.
  - `GET /health` now exposes `release_readiness` (`ready`, `violations`) so
    release smoke can fail fast when production-policy drift appears.
  - `scripts/run_release_smoke.{ps1,sh}` now enforce that release-readiness
    gate and stop the release when drift signals are present.
- Decision (PRJ-296 target production baseline, 2026-04-20):
  - target production startup posture is migration-only
    (`STARTUP_SCHEMA_MODE=migrate`); `create_tables` remains a temporary
    compatibility fallback path.
  - target production policy posture is strict
    (`PRODUCTION_POLICY_ENFORCEMENT=strict`) so mismatch conditions fail fast
    instead of staying warning-only.
  - release-readiness checks should treat non-empty
    `runtime_policy.production_policy_mismatches` as baseline drift.
- Decision (PRJ-306 migration compatibility removal criteria, 2026-04-20):
  - `create_tables` compatibility path can be removed only when all guardrails
    are true:
    - production and pre-production environments run with
      `STARTUP_SCHEMA_MODE=migrate` and no approved exceptions
    - release gates stay green with
      `runtime_policy.production_policy_mismatches` empty across at least two
      consecutive release windows
    - no operational rollback/runbook step depends on `create_tables` as a
      recovery path
    - migration smoke (`alembic upgrade` + app startup + release smoke)
      is validated as the sole bootstrap route for the same release windows
  - removal rollout order is:
    - freeze: disallow new `create_tables` usage outside local/test-only
      contexts
    - remove: delete compatibility startup branch and associated policy
      mismatch path
    - clean up: remove obsolete docs/config references and compatibility-only
      tests
- Resolved in `PRJ-419..PRJ-422` (2026-04-22):
  - runtime policy now exposes the scheduled removal window as
    `after_group_51_release_evidence_green`.
- Resolved follow-up in `PRJ-464..PRJ-467` (2026-04-22):
  - Alembic head now covers the full current live schema, including
    `aion_attention_turn` and `aion_subconscious_proposal`.
  - migration parity is now regression-pinned by exercising fresh
    `alembic upgrade head` instead of trusting metadata/docs parity alone.
- Planned implementation lane:
  - `PRJ-375..PRJ-378` will make migration-only removal readiness
    machine-visible before an actual release-window removal is scheduled.
- Resolved baseline (2026-04-21):
  - `/health.runtime_policy` now exposes machine-readable sunset-readiness
    posture for migration-only bootstrap
    (`startup_schema_compatibility_posture`,
    `startup_schema_compatibility_sunset_ready`,
    `startup_schema_compatibility_sunset_reason`).
  - release smoke now verifies that compatibility-sunset evidence is present
    and internally consistent before using it as release evidence.

### 3. Public API Shape

- Current repo fact:
  - `POST /event` now returns a smaller public response by default: event identifiers, reply payload, and a compact runtime summary.
  - the full serialized runtime result is exposed through primary internal
    route `POST /internal/event/debug`, plus transitional compatibility routes
    `POST /event/debug` (shared endpoint) and
    `POST /event?debug=true` (query compatibility path), guarded by explicit
    config (`EVENT_DEBUG_ENABLED`) with environment-aware defaults (enabled in
    non-production, disabled in production unless explicitly enabled).
  - `POST /event?debug=true` now emits explicit compatibility headers
    (`X-AION-Debug-Compat`, `Link`) that point operators to
    `POST /internal/event/debug` as the preferred internal debug route.
  - shared `POST /event/debug` now emits explicit compatibility headers
    (`X-AION-Debug-Shared-Compat`, `X-AION-Debug-Shared-Mode`,
    `X-AION-Debug-Shared-Posture`) and can run in
    `compatibility|break_glass_only` mode through
    `EVENT_DEBUG_SHARED_INGRESS_MODE`.
  - shared ingress posture vocabulary is now final and route-owned:
    `shared_route_compatibility|shared_route_break_glass_only`.
  - compat-route responses now also emit
    `X-AION-Debug-Compat-Deprecated=true` and runtime health now exposes
    `event_debug_query_compat_telemetry` counters plus derived compat sunset
    recommendation signals (`event_debug_query_compat_allow_rate`,
    `event_debug_query_compat_block_rate`,
    `event_debug_query_compat_recommendation`) plus explicit sunset posture
    signals (`event_debug_query_compat_sunset_ready`,
    `event_debug_query_compat_sunset_reason`) for migration tracking.
  - compat recommendation logic now treats any observed compat attempts as
    migration-needed (not only successful compat responses), so blocked
    attempts still count as active migration work.
  - health policy now also exposes rolling compat trend signals
    (`event_debug_query_compat_recent_attempts_total`,
    `event_debug_query_compat_recent_allow_rate`,
    `event_debug_query_compat_recent_block_rate`,
    `event_debug_query_compat_recent_state`) to support release-window
    migration monitoring.
  - rolling compat trend window size is now configurable via
    `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` (default `20`).
  - health policy now also exposes compat freshness posture
    (`event_debug_query_compat_stale_after_seconds`,
    `event_debug_query_compat_last_attempt_age_seconds`,
    `event_debug_query_compat_last_attempt_state`) so migration decisions can
    distinguish fresh usage from stale historical attempts.
  - health policy now also exposes compat activity posture
    (`event_debug_query_compat_activity_state`,
    `event_debug_query_compat_activity_hint`) so operators can separate
    disabled/no-attempt/stale-history/recent-traffic compatibility states
    without changing the stricter sunset-ready decision contract.
  - stale-age threshold for that freshness posture is configurable via
    `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS` (default `86400`).
  - compatibility `POST /event?debug=true` route now has an explicit
    environment-aware policy surface (`EVENT_DEBUG_QUERY_COMPAT_ENABLED`):
    enabled by default outside production and disabled by default in
    production unless explicitly enabled.
  - when `EVENT_DEBUG_TOKEN` is configured, `POST /event?debug=true` also requires `X-AION-Debug-Token`.
  - when `EVENT_DEBUG_TOKEN` is configured, both
    `POST /internal/event/debug` and `POST /event/debug` require
    `X-AION-Debug-Token`.
  - production can now enforce debug-token configuration through
    `PRODUCTION_DEBUG_TOKEN_REQUIRED` (default `true`); when enabled and
    production debug payload exposure is active without a configured token,
    debug endpoints reject access.
  - `GET /health` now exposes `event_debug_enabled`, `event_debug_token_required`,
    `production_debug_token_required`, `debug_access_posture`,
    `debug_token_policy_hint`, `event_debug_source`, and
    `production_policy_enforcement` so operators can verify effective policy,
    token-gate posture, policy source, and enforcement mode.
  - `/health` also exposes strict-rollout readiness and recommendation signals so operators can detect production-hardening mismatches before a strict-mode rollout and decide when to switch enforcement.
  - startup now emits a production warning when `EVENT_DEBUG_ENABLED=true` so the policy remains visible even before handling requests.
  - startup warns when production debug payload exposure is enabled without
    `EVENT_DEBUG_TOKEN` while `PRODUCTION_DEBUG_TOKEN_REQUIRED=true`.
  - startup also warns when production debug payload exposure is enabled with
    `PRODUCTION_DEBUG_TOKEN_REQUIRED=false`, making relaxed token-hardening
    posture explicit.
  - startup can now hard-fail in production when debug payload exposure is enabled and strict enforcement mode is active.
  - strict mismatch posture now also includes
      `event_debug_token_missing=true` when debug exposure is enabled in
      production, token requirement is enabled, and no debug token is
      configured.
  - strict mismatch posture also includes
    `event_debug_query_compat_enabled=true` when production debug exposure
    keeps compatibility query-debug route enabled.
  - strict-mode hard-fail behavior is test-covered at startup lifecycle level across both debug and schema mismatch paths, not only at helper-function level.
  - production now uses strict policy enforcement as the default when
    enforcement mode is unset, and explicit `warn` keeps temporary override
    ownership visible.
- Decision (PRJ-296 target production baseline, 2026-04-20):
  - production public API posture stays compact on `POST /event`; full runtime
    payload remains an internal diagnostics surface.
  - production baseline keeps debug exposure disabled by default
    (`EVENT_DEBUG_ENABLED=false`) and keeps compatibility query-debug route
    disabled (`EVENT_DEBUG_QUERY_COMPAT_ENABLED=false`).
  - when a temporary incident-debug window is explicitly enabled in production,
    debug payload access must stay token-gated
    (`EVENT_DEBUG_TOKEN` configured and
    `PRODUCTION_DEBUG_TOKEN_REQUIRED=true`).
  - strict production policy enforcement should treat debug-exposure mismatch
    states as release-blocking drift.
- Decision (PRJ-307 internal debug ingress boundary, 2026-04-20):
  - target ingress contract is:
    - public API ingress keeps `POST /event` compact and must not expose full
      runtime payloads
    - full runtime debug payload access belongs to a dedicated internal/admin
      ingress boundary (not a shared public API service endpoint)
  - migration posture is:
    - current primary debug ingress path is `POST /internal/event/debug`
    - current `POST /event/debug` on shared API service endpoint is a
      transitional compatibility posture
    - shared endpoint posture can be tightened to break-glass-only mode
      (`EVENT_DEBUG_SHARED_INGRESS_MODE=break_glass_only`) while preserving
      explicit emergency override via `X-AION-Debug-Break-Glass: true`
    - deprecated compatibility `POST /event?debug=true` remains migration-only
      and should stay disabled in production baseline
    - production incident-debug usage should migrate to dedicated internal
      ingress first, then shared-endpoint debug exposure should be retired as
      default posture
  - ownership boundaries are:
    - runtime/API owners keep debug payload schema and policy telemetry
      semantics (`debug_access_posture`, compat telemetry, strict mismatch
      previews)
    - Ops/Release owns ingress routing, network/auth controls, and
      release/rollback evidence for the dedicated debug ingress path
- Resolved in `PRJ-419..PRJ-422` (2026-04-22):
  - runtime policy now exposes the shared-debug enforcement window as
    `after_group_51_release_evidence_green`, and production default posture is
    break-glass-only when no explicit override is configured.
- Planned implementation lane:
  - `PRJ-375..PRJ-378` will turn shared-debug-ingress retirement into explicit
  readiness and release evidence before selecting the enforcement window.
- Resolved baseline (2026-04-21):
  - `/health.runtime_policy` now exposes machine-readable sunset-readiness
    posture for shared debug ingress retirement
    (`event_debug_shared_ingress_sunset_ready`,
    `event_debug_shared_ingress_sunset_reason`,
    `compatibility_sunset_ready`, `compatibility_sunset_blockers`).
  - release smoke now validates that shared-debug-ingress sunset evidence is
    present and coherent before treating it as release evidence.

### 3a. Expression vs Action Ordering

- Current repo fact:
  - canonical architecture describes `... -> planning -> expression -> action -> memory -> reflection`.
  - foreground runtime now materializes an explicit response-execution handoff
    (`ActionDelivery`) at expression output, and action consumes that handoff
    directly.
  - action still delegates channel delivery to integration-owned routing
    (`DeliveryRouter`), so integration dispatch consumes explicit handoff
    payload while side effects remain action-triggered.
- Resolved baseline (2026-04-21):
  - `PRJ-371..PRJ-374` completed the shared-contract path first by adding a
    bounded `execution_envelope` to `ActionDelivery` instead of introducing
    connector-specific handoff owners.
  - action now validates envelope parity against planning before side effects,
    and integration routing may surface bounded envelope notes without
    changing expression ownership.

### 3b. Graph Orchestration Adoption

- Current repo fact:
  - architecture docs describe `LangGraph` as the intended orchestration layer,
    and foreground stage execution now runs through LangGraph `StateGraph`.
  - foreground ownership convergence for Group 17 is now complete:
    - `PRJ-276` defined canonical ownership and migration invariants
    - `PRJ-277` made expression-to-action handoff explicit
    - `PRJ-278` made runtime-owned pre/post graph segments explicit in code
    - `PRJ-279` pinned parity regressions and synchronized docs/context
  - baseline-state load plus post-action persistence/reflection still run
    outside graph execution by design, with explicit ownership boundaries.
  - runtime keeps an explicit graph-compatibility boundary
    (`GraphRuntimeState`, conversion helpers, stage adapters) for incremental
    migration without contract drift.
  - `PRJ-276` now defines the target foreground ownership boundary and migration
    invariants in canonical docs:
    - runtime-owned: baseline load, episodic memory write, reflection trigger
    - graph-owned: cognitive stage graph (`perception -> ... -> action`)
  - `LangChain` is described as optional support, not the architectural core.
- Resolved in `PRJ-415..PRJ-418` (2026-04-22):
  - current pre/post graph ownership remains the canonical long-term baseline;
    future node expansion is bounded and optional rather than a default
    migration goal.

### 4. Role Selection

- Current repo fact:
  - runtime role now uses lightweight heuristic selection (`friend`, `analyst`, `executor`, `mentor`, `advisor`), can use a reflected `preferred_role` as a tie-breaker for more ambiguous turns, and can also fall back to lightweight reflected theta bias when explicit heuristics do not decide the turn.
  - role outputs now expose explicit `selection_reason` and
    `selection_evidence` metadata from one shared policy owner
    (`app/core/role_selection_policy.py`).
  - active-goal context can now reinforce analytical role selection on
    planning turns, while preferred-role/relation/theta tie breaks remain
    bounded metadata-backed decisions instead of hidden local heuristics.
- Follow-up implementation (resolved in `PRJ-395..PRJ-398`, 2026-04-21):
  - role selection now has a shared evidence-driven policy owner with
    machine-readable precedence diagnostics
  - runtime debug and role outputs expose bounded evidence metadata without
    changing action ownership
- Resolved in `PRJ-427..PRJ-430` (2026-04-22):
  - role selection remains a foreground policy with bounded history evidence
    rather than a broader long-horizon identity owner.

### 4a. Affective Assessment Strategy

- Current repo fact:
  - runtime now has a first-class affective contract slot
    (`affect_label`, `intensity`, `needs_support`, `confidence`, `source`,
    `evidence`) and a dedicated affective assessor stage.
  - when available, the assessor can consume LLM classification and normalize
    it to the shared contract; when unavailable or invalid, it falls back
    deterministically.
  - motivation, role, and expression now consume `perception.affective` as the
    shared support/emotion signal owner.
- Resolved in `PRJ-399..PRJ-402` and `PRJ-427..PRJ-430`:
  - AI-assisted affective classification remains enabled by default in
    non-production, disabled by default in production, and the first-class
    affective contract fields remain
    `label|intensity|needs_support|confidence|source|evidence`.
- Follow-up implementation (resolved in `PRJ-399..PRJ-402`, 2026-04-21):
  - affective assessment now has a shared rollout policy owner with
    environment-default enablement, explicit override support, and
    machine-visible health/debug posture
  - policy-disabled fallback and classifier-unavailable fallback are now
    separated in deterministic, test-visible runtime behavior
- Resolved in `PRJ-427..PRJ-430` (2026-04-22):
  - affective rollout remains enabled-by-default in non-production and
    disabled-by-default in production unless explicitly overridden.
- Resolved in `PRJ-448..PRJ-451` (2026-04-22):
  - `/health.affective` and runtime `system_debug.adaptive_state` now
    distinguish heuristic perception input from final affective assessment
    resolution, including fallback-reuse posture.

### 5. Memory Retrieval Depth

- Current repo fact:
  - runtime now loads up to 12 recent memory rows for context selection.
  - persisted episodes now keep lightweight structured runtime fields in a typed payload, while still keeping a readable summary.
  - perception now emits lightweight `topic_tags`, and memory persistence reuses them before falling back to raw lexical tokens.
  - context and reflection now read episodic memory payload-first and fall back to old summary-only rows only when needed.
  - context now prefers memories tagged with the same response language as the current turn before falling back to untagged older context.
  - within that pool, context now distinguishes between `continuity` and `semantic` memory, applies affective relevance scoring, and prefers topically overlapping memories before falling back to lower-signal items.
  - for more specific requests, context now skips unrelated memory entirely instead of forcing a weak fallback; ambiguous short follow-ups can still reuse continuity memory.
  - context also now receives lightweight semantic conclusions and can include stable user preferences alongside episodic recall.
- Resolved in `PRJ-423..PRJ-426` (2026-04-22):
  - retrieval now treats hybrid lexical plus vector as the production target
    path, with explicit production-default depth surfaced as
    `episodic_limit=12` and `conclusion_limit=8`.

### 5b. Affective Memory Model

- Current repo fact:
  - episodic payloads now persist lightweight affective tags
    (`affect_label`, `affect_intensity`, `affect_needs_support`,
    `affect_source`, `affect_evidence`).
  - reflection now derives slower-moving affective conclusions
    (`affective_support_pattern`, `affective_support_sensitivity`) from recent
    episodic traces.
- Resolved in `PRJ-423..PRJ-426` (2026-04-22):
  - affective memory remains an orthogonal layer across episodic and semantic
    records, while long-lived affective conclusions stay durable and current
    turn affect remains transient.

### 5c. Reflection Scope And Multi-Goal Leakage

- Current repo fact:
  - reflection now supports scoped conclusions (`scope_type`, `scope_key`) and
    persists goal-operational conclusions with goal scope.
  - runtime consumers now resolve a primary active goal and read scoped
    conclusions/preferences with global fallback, reducing cross-goal leakage in
    context, motivation, planning, and milestone enrichment.
- Decision (resolved in `PRJ-403..PRJ-406`, 2026-04-21):
  - reflection scope ownership now lives in one shared owner
    (`app/core/reflection_scope_policy.py`) reused by reflection writers and
    repository/runtime readers.
  - goal-progress and milestone reflection conclusions remain goal-scoped.
  - adaptive role/collaboration and affective reflection outputs remain
    user-global by default until a later architecture change explicitly narrows
    their ownership.
  - repository/runtime readers now ignore invalid scoped overrides for global
    reflection outputs, so cross-goal leakage is test-visible and bounded.

### 5d. Vector Retrieval Activation

- Current repo fact:
  - runtime now has a semantic embedding contract, deterministic embedding
    fallback helpers, pgvector-ready schema/migration scaffolding, and hybrid
    lexical-plus-vector retrieval APIs.
  - semantic vector retrieval now has an explicit runtime feature gate
    (`SEMANTIC_VECTOR_ENABLED`) and `/health` operator visibility through
    `memory_retrieval.semantic_vector_enabled` and
    `memory_retrieval.semantic_retrieval_mode`
    (`hybrid_vector_lexical|lexical_only`).
  - runtime memory load now consumes hybrid retrieval diagnostics with explicit
    rollout posture in `/health`.
- Decision (resolved in `PRJ-284`, 2026-04-20):
  - keep `SEMANTIC_VECTOR_ENABLED=true` as the target production baseline,
    while preserving explicit lexical-only behavior when vectors are disabled
  - keep vector retrieval as the default runtime retrieval path for enabled
    source families
  - keep deterministic fallback explicit until a provider-backed production
    owner is implemented and validated
- Resolved in `PRJ-423..PRJ-426` (2026-04-22):
  - provider-owned execution is now available through the local `local_hybrid`
  provider path; deterministic remains the fallback baseline.
  - `/health.memory_retrieval.semantic_embedding_execution_class` now exposes
    whether current execution is deterministic baseline, local provider-owned,
    or fallback-to-deterministic posture.
- Resolved follow-up in `PRJ-476..PRJ-479` (2026-04-22):
  - OpenAI API embeddings are now the target provider-owned production
    baseline when `OPENAI_API_KEY` is configured.
  - `/health.memory_retrieval.semantic_embedding_execution_class` now also
    exposes `provider_owned_openai_api`, and production-baseline posture is
    explicit through
    `semantic_embedding_production_baseline`,
    `semantic_embedding_production_baseline_state`, and
    `semantic_embedding_production_baseline_hint`.

### 5e. Embedding Strategy

- Current repo fact:
  - code now defines embedding contracts and deterministic fallback vectors for
    episodic/semantic retrieval surfaces.
  - embedding strategy config posture is now explicit
    (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`) and
    `/health.memory_retrieval` now exposes requested/effective
    provider-model posture plus deterministic-fallback hint for
    non-implemented providers.
  - `/health.memory_retrieval` now also exposes explicit provider readiness
    posture (`semantic_embedding_provider_ready`,
    `semantic_embedding_posture`) and startup logs now emit
    `embedding_strategy_warning` when a requested provider falls back to
    deterministic execution.
  - semantic/affective conclusion embeddings, episodic embeddings, and relation
    embeddings now honor explicit refresh ownership with
    `materialized_on_write` versus `pending_manual_refresh` status.
  - source-family rollout remains explicitly gated by
    `EMBEDDING_SOURCE_KINDS`, allowing progressive enablement across
    `semantic|affective|relation` without implicit writes.
  - startup warnings and health diagnostics now share one embedding warning
    posture owner; `/health.memory_retrieval` exposes
    `semantic_embedding_warning_state` and
    `semantic_embedding_warning_hint` for machine-readable fallback posture.
  - embedding persistence scope is now explicit through
    `EMBEDDING_SOURCE_KINDS`, so runtime can limit which memory families
    (`episodic|semantic|affective|relation`) persist embedding records.
  - source-coverage posture for current vector retrieval path is now explicit
    through `semantic_embedding_source_coverage_state` and
    `semantic_embedding_source_coverage_hint`, with startup warnings using the
    same shared coverage-state semantics.
  - embedding refresh-cadence posture is now explicit through
    `EMBEDDING_REFRESH_MODE` (`on_write|manual`) and
    `EMBEDDING_REFRESH_INTERVAL_SECONDS`; `/health.memory_retrieval` now
    surfaces `semantic_embedding_refresh_mode` and
    `semantic_embedding_refresh_interval_seconds`; shared helper-owned refresh
    diagnostics (`semantic_embedding_refresh_state`,
    `semantic_embedding_refresh_hint`) now align startup and health semantics,
    and startup emits `embedding_refresh_warning` when vectors are enabled in
    manual mode.
  - model-governance posture is now explicit through shared diagnostics
    (`semantic_embedding_model_governance_state`,
    `semantic_embedding_model_governance_hint`) and startup warning visibility
    (`embedding_model_governance_warning`) for deterministic custom-model-name
    posture.
  - provider-ownership posture is now explicit through shared diagnostics
    (`semantic_embedding_provider_ownership_state`,
    `semantic_embedding_provider_ownership_hint`) and startup fallback warning
    enrichment.
  - provider-ownership enforcement posture is now explicit through
    `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` (`warn|strict`) and shared
    enforcement diagnostics
    (`semantic_embedding_provider_ownership_enforcement`,
    `semantic_embedding_provider_ownership_enforcement_state`,
    `semantic_embedding_provider_ownership_enforcement_hint`), including
    strict-mode startup block behavior for unresolved fallback ownership.
  - model-governance enforcement posture is now explicit through
    `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` (`warn|strict`) and shared
    enforcement diagnostics
    (`semantic_embedding_model_governance_enforcement`,
    `semantic_embedding_model_governance_enforcement_state`,
    `semantic_embedding_model_governance_enforcement_hint`), including
    strict-mode startup block behavior for deterministic custom-model-name
    governance posture.
  - owner-strategy recommendation posture is now explicit through shared
    diagnostics (`semantic_embedding_owner_strategy_state`,
    `semantic_embedding_owner_strategy_hint`,
    `semantic_embedding_owner_strategy_recommendation`) so provider+refresh
    ownership strategy is machine-visible in health and startup diagnostics.
  - source-rollout recommendation posture is now explicit through shared
    diagnostics (`semantic_embedding_source_rollout_state`,
    `semantic_embedding_source_rollout_hint`,
    `semantic_embedding_source_rollout_recommendation`) so next memory-family
    rollout step is machine-visible in health and startup diagnostics.
  - strict-rollout preflight posture is now explicit through shared diagnostics
    (`semantic_embedding_strict_rollout_violations`,
    `semantic_embedding_strict_rollout_violation_count`,
    `semantic_embedding_strict_rollout_ready`,
    `semantic_embedding_strict_rollout_state`,
    `semantic_embedding_strict_rollout_hint`,
    `semantic_embedding_strict_rollout_recommendation`) and enforcement
    recommendation/alignment fields
    (`semantic_embedding_recommended_provider_ownership_enforcement`,
    `semantic_embedding_recommended_model_governance_enforcement`,
    `semantic_embedding_provider_ownership_enforcement_alignment`,
    `semantic_embedding_model_governance_enforcement_alignment`,
    `semantic_embedding_enforcement_alignment_state`,
    `semantic_embedding_enforcement_alignment_hint`); startup now emits
    `embedding_strategy_hint` for rollout guidance.
  - source-rollout sequencing posture is now explicit through shared diagnostics
    (`semantic_embedding_source_rollout_order`,
    `semantic_embedding_source_rollout_enabled_sources`,
    `semantic_embedding_source_rollout_missing_sources`,
    `semantic_embedding_source_rollout_next_source_kind`,
    `semantic_embedding_source_rollout_completion_state`,
    `semantic_embedding_source_rollout_phase_index`,
    `semantic_embedding_source_rollout_phase_total`,
    `semantic_embedding_source_rollout_progress_percent`), and startup now
    emits `embedding_source_rollout_hint` while rollout remains in progress.
  - source-rollout enforcement posture is now explicit through
    `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` (`warn|strict`) plus shared
    diagnostics (`semantic_embedding_source_rollout_enforcement`,
    `semantic_embedding_source_rollout_enforcement_state`,
    `semantic_embedding_source_rollout_enforcement_hint`); startup now emits
    `embedding_source_rollout_warning` in warn mode and
    `embedding_source_rollout_block` with fail-fast behavior in strict mode
    while rollout is still pending.
  - source-rollout enforcement recommendation/alignment posture is now explicit
    through shared diagnostics
    (`semantic_embedding_recommended_source_rollout_enforcement`,
    `semantic_embedding_source_rollout_enforcement_alignment`,
    `semantic_embedding_source_rollout_enforcement_alignment_state`,
    `semantic_embedding_source_rollout_enforcement_alignment_hint`), and
    startup now emits `embedding_source_rollout_enforcement_hint` plus
    recommendation/alignment-enriched warning/block logs.
  - refresh cadence and rollout-alignment posture are now explicit through
    shared diagnostics (`semantic_embedding_refresh_cadence_state`,
    `semantic_embedding_refresh_cadence_hint`,
    `semantic_embedding_recommended_refresh_mode`,
    `semantic_embedding_refresh_alignment_state`,
    `semantic_embedding_refresh_alignment_hint`), and startup now emits
    `embedding_refresh_hint` when refresh posture deviates from recommendation.
- Decision (resolved in `PRJ-284`, 2026-04-20):
  - provider ownership baseline:
    - OpenAI API embeddings are the target provider-owned production baseline
      when configured
    - `local_hybrid` remains a bounded local transition owner
    - deterministic remains the explicit compatibility fallback owner;
      fallback diagnostics stay explicit
  - refresh ownership baseline:
    - `on_write` is the rollout baseline owner for vector materialization;
      `manual` stays an explicit operator override with documented process
      expectations
  - memory-family rollout order:
    - phase 1: episodic + semantic materialization baseline
    - phase 2: affective materialization rollout
    - phase 3: relation materialization rollout and full-source completion
  - enforcement rollout posture:
    - keep source-rollout enforcement aligned to `warn` while relation is
      pending; recommend `strict` after full rollout completion
- Resolved in `PRJ-423..PRJ-426` (2026-04-22):
  - provider-backed execution timing is now rollout-owned through explicit
    provider posture instead of a planning-only placeholder.
- Resolved follow-up in `PRJ-476..PRJ-479` (2026-04-22):
  - repository and action persistence now share a real OpenAI provider-owned
    embedding materialization path when `EMBEDDING_PROVIDER=openai` and
    `OPENAI_API_KEY` are configured
  - missing OpenAI credentials now produce explicit
    `openai_api_key_missing_fallback_deterministic` posture instead of a
    generic non-implemented-provider fallback

### 5a. Goal And Task Scope

- Current repo fact:
- runtime now loads active goals and active tasks, includes them in the runtime result, refreshes them after Action-layer writes, lets context/motivation/planning react to them, can seed lightweight goals/tasks from explicit user phrases such as `My goal is to ...` and `I need to ...`, can update task status from explicit progress phrases such as `I fixed ...`, and reflection can now derive a lightweight semantic `goal_execution_state` like `blocked`, `recovering`, `advancing`, `progressing`, or `stagnating`, plus a lightweight `goal_progress_score`, `goal_progress_trend`, `goal_progress_arc`, `goal_milestone_state`, `goal_milestone_transition`, `goal_milestone_arc`, `goal_milestone_pressure`, `goal_milestone_dependency_state`, `goal_milestone_due_state`, `goal_milestone_due_window`, `goal_milestone_risk`, and `goal_completion_criteria`; it also persists a short goal-level progress history in `aion_goal_progress`, syncs lightweight `aion_goal_milestone` objects for the active goal focus, persists short `aion_goal_milestone_history` snapshots, and runtime enriches those milestone objects with the current operational arc/pressure/dependency/due/due-window/risk/completion signals without introducing a heavier milestone schema yet.
- Resolved in `PRJ-431..PRJ-434` (2026-04-22):
  - goal/task growth stays bounded to repeated execution-blocker evidence
    through explicit typed intents instead of broad free-form inference.

### 6. Deployment Path After Coolify

- Current repo fact:
  - docs and compose files already support local Docker and Coolify.
- Decision (PRJ-298 operational baseline, 2026-04-20):
  - Coolify is the active production deployment baseline for this repository.
  - `docker-compose.coolify.yml` is the deployment source of truth for this
    baseline, while `docker-compose.yml` remains local-development oriented.
  - hosting-standard replacement is explicitly future work; runtime slices must
    not assume another deployment platform until operations records that change.
- Resolved in `PRJ-439..PRJ-442` (2026-04-22):
  - Coolify remains the medium-term hosting baseline, and no replacement
    transition is currently scheduled.

### 7. Deployment Trigger Reliability

- Current repo fact:
  - after pushing `main`, production required a manual redeploy from Coolify before the latest commit became live.
  - a manually sent, correctly signed GitHub-style webhook request to the configured Coolify endpoint successfully queued a deployment on 2026-04-15.
  - the repo now has a repeatable release smoke helper for `GET /health` plus `POST /event`, so manual verification no longer depends on hand-written curl snippets.
  - Coolify deploy trigger helpers now emit optional machine-readable webhook
    evidence (`coolify_deploy_webhook_evidence`) for response posture and
    timing metadata.
  - release-smoke helpers now optionally verify that deployment evidence is
    fresh and reflects a successful webhook response before the smoke
    roundtrip runs.
  - dedicated script regressions now pin evidence file shape, unsuccessful
    webhook failure posture, optional evidence omission, and freshness checks.
- Decision (PRJ-298 operational baseline, 2026-04-20):
  - deploy trigger posture is `automation_first_with_explicit_manual_fallback`:
    GitHub/Coolify webhook automation is preferred when it fires correctly.
  - manual fallback remains explicit and supported through
    `scripts/trigger_coolify_deploy_webhook.{ps1,sh}` or direct Coolify UI
    redeploy when automation is missing or delayed.
  - release completion requires running
    `scripts/run_release_smoke.{ps1,sh}` against the deployed URL and treating
    smoke failure as a release-blocking signal.
- Resolved in `PRJ-439..PRJ-442` (2026-04-22):
  - deployment trigger SLO is now explicit through release-health posture:
    `delivery_success_rate_percent=99.0` and
    `manual_redeploy_exception_rate_percent=5.0`.

### 8. Language Handling Strategy

- Current repo fact:
  - runtime now makes an explicit per-event language decision and uses
    precedence across current-turn signals, recent-memory continuity, and
    profile continuity.
  - continuity parsing now uses structured episodic payload hints
    (`payload.response_language` and `payload.language`) plus summary fallback,
    while ignoring unsupported language codes.
  - API identity fallback is now explicit and request-scoped
    (`meta.user_id` -> `X-AION-User-Id` -> `anonymous`), reducing accidental
    language/profile bleed from shared anonymous traffic.
  - `PRJ-411` now defines a shared `identity_policy` owner and exposes the
    current boundary through `/health.identity` and
    `system_debug.adaptive_state.identity_policy`.
  - `PRJ-412` now exposes `language_continuity` posture through
    `/health.identity` and runtime debug, including precedence baseline,
    supported codes, selected source, candidate continuity inputs, and
    fallback posture.
  - `PRJ-413` now regression-pins explicit-request posture, profile-only
    continuity posture, and unsupported-profile fallback against the current
    MVP language boundary (`en|pl`).
- Decision (interim baseline resolved in `PRJ-411`, 2026-04-21):
  - language handling stays heuristic-plus-profile for the MVP
  - multilingual posture remains explicitly bounded to supported runtime codes
    (`en|pl`) until a broader language model is intentionally added
- Resolved in `PRJ-427..PRJ-430` (2026-04-22):
  - multilingual expansion remains explicitly deferred until a new contract is
    introduced beyond the current supported runtime codes.

### 9. Lightweight Profile Scope

- Current repo fact:
  - runtime now persists lightweight language preference in `aion_profile`
    while semantic response/collaboration preferences stay conclusion-owned in
    `aion_conclusion`.
  - identity loading now keeps that owner boundary explicit: relation fallback
    cues may shape stage behavior but do not become durable profile identity
    fields.
  - runtime builds a lightweight `IdentitySnapshot` from profile language plus
    conclusion/theta inputs without merging those ownership surfaces.
  - `PRJ-411` now centralizes that boundary in `app/core/identity_policy.py`
    and exposes the same owner snapshot through `/health` and runtime debug.
- Decision (interim baseline resolved in `PRJ-411`, 2026-04-21):
  - `aion_profile` remains limited to durable interaction continuity such as
    language preference
  - generalized learned preferences stay conclusion-owned in
    `aion_conclusion`
  - relation fallback cues remain foreground tie-break inputs only, not
    durable profile identity writes
- Resolved in `PRJ-427..PRJ-430` (2026-04-22):
  - the split between profile-owned language continuity and
    conclusion-owned learned preferences remains the long-term baseline.

### 9a. Relation System Rollout

- Current repo fact:
  - runtime now persists scoped relation records (`aion_relation`) with
    confidence/source/evidence/decay fields and reflection-driven updates.
  - runtime now loads high-confidence relations and applies relation cues in
    context, role, planning, and expression paths.
- Decision (baseline resolved in `PRJ-330..PRJ-333`, 2026-04-21):
  - relation lifecycle is now explicit:
    - repeated same-value observations refresh confidence/evidence posture
    - value-shift observations reset evidence/decay posture
    - stale relation signals weaken via age-aware revalidation and expire when
      confidence drops below expiration threshold
  - trust influence is now explicit:
    - delivery reliability cues now shape motivation/planning confidence
      posture and proactive interruption/relevance behavior through shared
      adaptive policy owners
  - low-confidence relation cues remain descriptive-only and must not directly
    drive trust-sensitive planning/expression/proactive behavior.
- Follow-up implementation (resolved in `PRJ-343..PRJ-346`, 2026-04-21):
  - inferred goal/task promotion now applies delivery-reliability-aware trust
    thresholds (`low_trust|medium_trust|high_trust`) while explicit
    user-declared intent paths remain unaffected
  - inferred promotion gate diagnostics (`reason=...`, `result=...`) are now
    explicit in planning and runtime debug surfaces

### 10. Preference Influence Scope

- Current repo fact:
- stable `response_style` conclusions now influence context, planning, and expression.
- stable `preferred_role` conclusions can now influence role selection on ambiguous turns.
- stable `collaboration_preference` conclusions can now influence context, role selection, motivation, planning, and expression on ambiguous turns, and explicit user phrases like `step by step` or `do it for me` are now captured as episodic collaboration markers for reflection.
- reflected theta now provides a softer runtime bias toward support, analysis, or execution behavior without hard-overriding explicit signals, and that bias can now shape role selection, motivation mode, planning stance, and expression tone on ambiguous turns.
- Decision (baseline resolved in `PRJ-288`, 2026-04-20):
  - `response_style` remains formatting-oriented and may shape expression/planning structure, not execution ownership
  - `preferred_role` remains a role tie-break signal only, gated by confidence (`>= 0.72`) and ambiguous-turn posture
  - `collaboration_preference` may shape role/motivation/planning/expression only through ambiguous-turn tie-break paths
- Resolved in `PRJ-427..PRJ-430` (2026-04-22):
  - preference signals remain foreground tie-break inputs and do not gain
    proactive or attention-gate authority.

### 10a. Action Intent Ownership

- Current repo fact:
  - planning now emits explicit typed `domain_intents` for goal/task/task-status,
    inferred promotion (`promote_inferred_goal`, `promote_inferred_task`),
    maintenance status alignment (`maintain_task_status`), and preference
    updates, plus `noop` when no domain write should occur.
  - action now executes only explicit intents and no longer reparses raw user
    text for durable domain writes.
- Decision (baseline expanded in `PRJ-334..PRJ-336`, 2026-04-21):
  - inferred goal/task growth now remains subordinate to explicit typed-intent
    ownership in planning contracts
  - repeated-blocker maintenance writes now also require explicit typed
    intents before action can mutate durable task state
  - duplicate/no-unsafe inferred promotion behavior is now regression-pinned
    in planning and runtime suites.
- Follow-up implementation (resolved in `PRJ-367..PRJ-370`, 2026-04-21):
  - relation-maintenance writes now have an explicit typed owner
    (`maintain_relation`) that action can execute without falling back to
    generic payload interpretation
  - proactive planning now emits explicit durable state intents
    (`update_proactive_state`) for `delivery_ready`,
    `delivery_guard_blocked`, `interruption_deferred`, and
    `attention_gate_blocked` posture instead of hiding write semantics behind
    generic `noop`
  - action persists those relation/proactive writes only from explicit typed
    intents, and regression coverage now pins the boundary across planning,
    action, runtime, reflection, and scheduler paths

### 10b. Adaptive Signal Governance

- Current repo fact:
  - reflection now requires outcome evidence and user-visible cues for
    adaptive updates (`preferred_role`, `theta`, collaboration fallback) to
    reduce feedback loops from role-only traces.
- Decision (resolved in `PRJ-288`, 2026-04-20):
  - adaptive influence now has one explicit baseline policy contract in
    `docs/architecture/16_agent_contracts.md`
  - evidence thresholds are explicit:
    - relation cues require confidence `>= 0.68` (`>= 0.70` for role
      collaboration tie-break)
    - role preference tie-break requires `preferred_role_confidence >= 0.72`
    - theta influence requires dominant bias `>= 0.58`
  - signal precedence is explicit:
    - affective safety/support cues first
    - relation/preference cues next
    - theta last
  - below-threshold adaptive signals are descriptive-only and must not alter
    role, motivation mode, planning steps, or expression tone
- Resolved through `PRJ-289..PRJ-290` and the later convergence queue:
  - adaptive policy-owner adoption is now complete across foreground,
    proactive, attention, and health/debug policy surfaces.

### 11. Theta Scope And Durability

- Current repo fact:
  - reflection now updates a lightweight `aion_theta` state from repeated recent role patterns, and runtime can use that state as a soft bias for role selection, motivation, planning, and expression on ambiguous turns.
  - runtime and `/health` now expose a shared retrieval/theta governance
    snapshot so retrieval-depth posture and theta influence are machine-visible
    through one owner.
  - `system_debug.adaptive_state.theta_influence` now reports bounded posture
    per foreground stage (`role`, `motivation`, `planning`, `expression`) and
    explicitly marks theta as tie-break-only governance.
- Decision (interim baseline resolved in `PRJ-288`, 2026-04-20):
  - theta stays a lightweight adaptive tie-break signal, not a dominant
    identity owner
  - theta influence remains ambiguity-gated and threshold-gated
    (`dominant_bias >= 0.58`)
- Follow-up implementation (resolved in `PRJ-391..PRJ-394`, 2026-04-21):
  - retrieval-depth policy snapshot and theta-influence diagnostics are now
    explicit runtime surfaces
  - bounded theta posture is regression-pinned in runtime, role, planning, and
    health contract coverage
- Resolved in `PRJ-427..PRJ-430` (2026-04-22):
  - theta remains permanently bounded to tie-break posture in the current
    architecture convergence baseline.

### 12. Scheduler And Proactive Runtime

- Current repo fact:
  - scheduler event normalization contracts are now explicit, including cadence
    and source/subsource runtime boundaries.
  - runtime config now includes scheduler/reflection/maintenance/proactive
    interval controls.
  - an in-process scheduler worker can now run reflection, maintenance, and
    proactive cadence (`SCHEDULER_ENABLED`) and exposes scheduler
    posture/tick summaries through `GET /health`.
  - proactive scheduler ticks now run through a dedicated decision engine with
    interruption-cost guardrails and typed plan/motivation outputs.
  - proactive delivery now enforces baseline guardrails (user opt-in, outbound
    and unanswered throttle checks, delivery-target requirement) before outreach.
  - `/health.proactive` now exposes one shared proactive runtime policy owner,
    cadence owner posture, delivery-target baseline, candidate-selection
    baseline, and anti-spam threshold snapshot.
- Decision (PRJ-322 scheduler execution owner posture, 2026-04-20):
  - scheduler cadence execution mode is now explicit through
    `SCHEDULER_EXECUTION_MODE` (`in_process|externalized`)
  - `/health.scheduler` now exposes owner-mode and readiness posture
    (`execution_mode`, cadence owners, dispatch reasons, blocker list)
- Decision (PRJ-323 shared cadence dispatch boundary, 2026-04-20):
  - maintenance and proactive cadence now share one owner-aware dispatch
    boundary in runtime contracts
  - maintenance execution now explicitly no-ops under externalized owner posture
    instead of relying on implicit in-process assumptions
- Decision (PRJ-301 scheduler/reflection baseline, 2026-04-20):
  - scheduled reflection baseline stays in-process first
    (`REFLECTION_RUNTIME_MODE=in_process`) with durable enqueue semantics.
  - deferred reflection dispatch remains opt-in and requires the explicit
    readiness criteria recorded in decision `1`.
- Decision (PRJ-308 maintenance/proactive cadence ownership boundary, 2026-04-20):
  - long-term target posture:
    - cadence ownership for maintenance and proactive wakeups moves to a
      dedicated external scheduler path after reflection external-dispatch
      posture is stable
    - app-local scheduler ownership remains transitional and local-development
      friendly, not the final production ownership model
  - ownership boundaries:
    - runtime keeps event-contract normalization, guardrail evaluation, and
      conscious execution boundaries for scheduled events
    - external scheduler owner controls cadence triggering, retry/backoff
      operations, and production on-call ownership for scheduler availability
  - rollout guardrails:
    - move production cadence ownership only after explicit runbook ownership,
      idempotent scheduler-event contract checks, and release smoke coverage for
      selected owner path
    - keep app-local scheduler as explicit fallback while external ownership
      SLOs and rollback path are being proven
- Resolved in `PRJ-415..PRJ-418` and `PRJ-435..PRJ-438` (2026-04-22):
  - durable attention remains the rollout target owner, while current
    production-default switching is gated by explicit topology and scheduler
    ownership evidence.
- Resolved follow-up in `PRJ-484..PRJ-487` (2026-04-22):
  - proactive cadence now has one explicit live baseline under shared
    `proactive_runtime_policy` ownership
  - in-process scheduler ownership can emit bounded proactive wakeups through
    repository-backed candidate selection and normal runtime execution
  - anti-spam posture is explicit through cooldown plus outbound/unanswered
    thresholds, and behavior validation now proves both delivery-ready and
    attention-gate-blocked proactive scenarios

### 12a. Attention Inbox And Turn Assembly

- Current repo fact:
  - runtime contracts now expose explicit graph-state surfaces for
    `attention_inbox`, `pending_turn`, `subconscious_proposals`, and
    `proposal_handoffs`.
  - `POST /event` now executes baseline Telegram burst-message coalescing with
    `pending|claimed|answered` turn ownership; duplicate/non-owner burst events
    are returned as queued no-op responses instead of running duplicate
    foreground turns.
  - `GET /health` now exposes an explicit `attention` snapshot with
    `burst_window_ms`, turn TTL values, and `pending|claimed|answered`
    counters, making burst-coalescing posture operator-visible.
  - attention timing now has explicit runtime config controls:
    `ATTENTION_BURST_WINDOW_MS`, `ATTENTION_ANSWERED_TTL_SECONDS`,
    `ATTENTION_STALE_TURN_SECONDS`.
- Decision (PRJ-292 baseline):
  - attention boundary is the canonical owner of turn assembly, pending-turn
    state, and burst-message coalescing status transitions.
  - timing windows remain config-owned by the attention boundary through
    `ATTENTION_BURST_WINDOW_MS`, `ATTENTION_ANSWERED_TTL_SECONDS`, and
    `ATTENTION_STALE_TURN_SECONDS`.
- Decision (PRJ-324 attention owner posture, 2026-04-20):
  - attention coordination owner mode is now explicit through
    `ATTENTION_COORDINATION_MODE` (`in_process|durable_inbox`)
  - `/health.attention` now exposes owner-mode deployment readiness posture
    (`coordination_mode`, `turn_state_owner`, `deployment_readiness`) for
    durable-inbox rollout preparation
- Decision (resolved in `PRJ-361..PRJ-362`, 2026-04-21):
  - production-default attention timing baseline is now explicit:
    - `ATTENTION_BURST_WINDOW_MS=120`
    - `ATTENTION_ANSWERED_TTL_SECONDS=5.0`
    - `ATTENTION_STALE_TURN_SECONDS=30.0`
  - `/health.attention.timing_policy` now exposes both the production baseline
    and the current configured values together with alignment posture so
    operators can distinguish baseline deployment from local/rollout overrides.
- Follow-up implementation (resolved in `PRJ-383..PRJ-386`, 2026-04-21):
  - `ATTENTION_COORDINATION_MODE=durable_inbox` now keeps the same conscious
    turn-assembly semantics as `in_process` instead of reporting placeholder
    not-ready posture
  - `/health.attention` now exposes `persistence_owner` and `parity_state` so
    durable rollout parity is explicit and operator-visible
- Decision (resolved in `PRJ-407..PRJ-410`, 2026-04-21):
  - `durable_inbox` now uses a repository-backed `aion_attention_turn`
    contract store keyed by `(user_id, conversation_key)`.
  - attention boundary still owns burst coalescing, claim, answer, and cleanup
    timing semantics; repository code owns the durable storage primitives.
  - `/health.attention` now exposes contract-store posture and cleanup
    visibility so the rollout stays observable before any production-default
    switch.

### 12b. Conscious vs Subconscious Coordination Boundary

- Current repo fact:
  - the architecture already states that subconscious processing does not
    communicate directly with the user, and runtime contracts now model a
    first-class proposal handoff surface between subconscious and conscious
    paths.
  - proposal persistence/promotion now runs end to end in live runtime:
    reflection persists proposal records, runtime loads retriable proposal
    states (`pending|deferred`), planning emits conscious handoff decisions, and
    runtime resolves proposal lifecycle status from those decisions.
  - planning now includes explicit proposal persistence, conscious promotion
    rules, read-only subconscious tool policy, and separate wakeup/cadence
    slices (`PRJ-088..PRJ-091`).
- Decision (PRJ-292 baseline):
  - subconscious outputs become durable proposals in the explicit proposal
    contract surface (`ask_user`, `research_topic`, `suggest_goal`,
    `nudge_user`, `suggest_connector_expansion`), not immediate actions.
  - conscious planning is the canonical owner of proposal handoff decisions
    (`accept|merge|defer|discard`) and corresponding durable status mapping
    (`accepted|merged|deferred|discarded`).
  - subconscious research remains read-only by default (`research_policy=read_only`);
    any broader authority requires a future architecture-contract change.
- Resolved in `PRJ-415..PRJ-418` and `PRJ-431..PRJ-434` (2026-04-22):
  - proposal decision set stays fixed at
    `accept|merge|defer|discard` unless a future explicit contract introduces
    new decisions and durable status mapping.

### 12c. Internal Planning State And External Connector Boundary

- Current repo fact:
  - internal goals/tasks already influence cognition and action, but the repo
    does not yet define a connector contract for calendar, task-system, or
    cloud-drive integrations.
  - planning now includes explicit connector and permission-gate slices
    (`PRJ-087`, `PRJ-093..PRJ-097`).
  - `PRJ-363` now defines one shared connector execution-policy owner
    (`app/core/connector_policy.py`) for baseline operation posture across
    `calendar`, `task_system`, and `cloud_drive`.
  - planner connector intents now derive baseline
    `read_only|suggestion_only|mutate_with_confirmation` mode from that shared
    policy instead of local connector-family literals.
  - planning permission gates and action guardrails now both consume that
    shared policy owner, and action fails fast on inconsistent connector
    intent posture before delivery side effects.
- Resolved in `PRJ-435..PRJ-438` (2026-04-22):
  - connector authorization matrix is now explicit for read, suggestion, and
    mutate-with-confirmation posture, and new connector capabilities remain
    proposal-only until explicit user authorization exists.
- Follow-up implementation (resolved in `PRJ-472..PRJ-475`, 2026-04-22):
  - the first live provider-backed connector path is now
    `task_system:create_task` for `provider_hint=clickup`, executed only from
    explicit typed intents and only when ClickUp credentials are configured
  - `/health.connectors.execution_baseline` now exposes the selected live path
    and its readiness posture
  - `calendar`, `cloud_drive`, and remaining task-system operations stay
    policy-only until pre-action read semantics and additional providers are
    explicitly designed

### 13. Runtime Behavior Validation Surface

- Current repo fact:
  - the repository has broad unit and integration coverage plus runtime-policy,
    health, scheduler, and memory contract tests.
  - canonical behavior-validation contract now exists in
    `docs/architecture/29_runtime_behavior_testing.md`.
  - internal debug responses now expose an explicit `system_debug` payload with
    event normalization metadata, memory bundle visibility, context,
    motivation, role, plan intents, expression, and action result traces.
  - behavior-harness helpers now emit structured scenario outputs
    (`test_id`, `status`, `reason`, `trace_id`, `notes`) for repeatable
    execution and evidence capture.
  - practical testing has shown that a subsystem can look well implemented
    through contracts and still fail to influence later behavior in a useful
    way (for example memory that persists but does not shape future turns).
- Decision (resolved in `PRJ-310..PRJ-317`, 2026-04-20):
  - mandatory internal debug fields are now defined and implemented through the
    shared `system_debug` validation surface.
  - behavior-driven scenario checks are now part of release-readiness evidence
    through `scripts/run_behavior_validation.{ps1,sh}`.
  - required scenario families now include:
    - memory `write -> retrieve -> influence -> delayed recall`
    - multi-session continuity and personality stability
    - contradiction, missing-data, and noisy-input resilience
- Decision (resolved in `PRJ-347..PRJ-350`, 2026-04-21):
  - behavior validation now emits a machine-readable artifact contract with
    summary counts, per-test status, and explicit gate snapshot
    (`mode`, `status`, `violations`).
  - release/ops behavior-validation wrappers now support explicit
    `operator|ci` posture so local evidence mode and CI fail-fast mode share
    one command family.
  - regression coverage now pins artifact gate semantics, including CI
    fail-fast behavior for empty test collection when required.
- Decision (resolved in `PRJ-351..PRJ-354`, 2026-04-21):
  - behavior-validation artifacts now include explicit schema-version and
    gate-taxonomy metadata.
  - CI consumers can evaluate existing artifacts locally without rerunning
    pytest, while keeping one gate contract owner.
  - malformed artifact-input paths are now regression-pinned for
    `missing|summary_missing|summary_invalid` posture.
- Decision (resolved in `PRJ-359..PRJ-360`, 2026-04-21):
  - CI artifact-input evaluation now treats incompatible
    `artifact_schema_version` major values as strict blockers.
  - operator-mode artifact-input evaluation remains backward-compatible for
    local inspection even when schema-major mismatch is present.
  - gate violation context now records input-versus-expected schema-major
    posture for machine-visible CI triage.
