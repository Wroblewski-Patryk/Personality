# PROJECT_STATE

Last updated: 2026-04-29

## Product Snapshot

- 2026-04-29: `PRJ-778` captured a planning-grade analysis for the reported
  short-term memory / proactive cadence drift:
  - user evidence showed repeated proactive Telegram-style check-ins every
    ~30 minutes despite explicit instructions not to write that often and not
    to greet on every message
  - current runtime already loads more than one memory item
    (`RuntimeOrchestrator.MEMORY_LOAD_LIMIT=12`), so increasing the recent
    window to 25 may be a secondary tuning option but is not the core fix
  - likely root cause is preference propagation:
    - narrow explicit proactive preference phrase detection
    - older `proactive_opt_in=true` can remain the scheduler candidate driver
    - no durable greeting-style preference currently shapes expression
  - the approved repair path should reuse existing preference/conclusion,
    planning intent, action persistence, proactive guard, and expression
    owners rather than introducing a new short-term memory subsystem
  - plan artifact:
    - `.codex/tasks/PRJ-778-plan-short-term-memory-and-proactive-style-respect.md`

- 2026-04-29: `PRJ-779` pushed the dashboard into its next structural
  convergence pass:
  - the dashboard hero now ends with a dedicated bridge note so the cognition
    field reads more like one flagship scene
  - the right editorial column is calmer and more ordered:
    - guidance
    - intention
    - conversation channel
    - recent activity
  - the `cognitive flow` band no longer carries a competing sidecard; current
    phase meaning now lives inside the bridge itself
  - the lower row now separates:
    - active goals
    - current focus
    - memory growth
    - reflection highlights
  - the final closure now gives relatively more authority to the scenic summary
    and less to late-route stat density
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
    - `git diff --check -- web/src/App.tsx web/src/index.css`
  - highest-value next step:
    - fresh deploy screenshots and canonical parity review for `public home`
      and `dashboard`

- 2026-04-29: `PRJ-776` started the first real implementation slice from the
  layout/dashboard/public-home master audit:
  - unauthenticated entry is no longer structured as a standalone auth page
  - `web/src/App.tsx` now renders a landing-first public shell with:
    - browser-like top chrome
    - integrated public nav
    - embodied hero stage
    - feature strip
    - integrated auth module
    - trust closure band
  - authenticated routes now render inside a reusable shared `WindowChrome`
    frame before route-local content begins
  - `docs/ux/design-memory.md` now records:
    - window-chrome shell framing
    - landing-first public entry
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
    - `git diff --check -- web/src/App.tsx web/src/index.css`
  - the highest-value next lane is now narrower:
    - dashboard structural convergence on top of the new parent frame
    - then browser screenshot parity for public home and dashboard

- 2026-04-28: `PRJ-775` completed a planning-grade master audit for the next
  major flagship lane:
  - `docs/planning/layout-dashboard-public-home-canonical-master-audit.md`
  - focus narrowed to:
    - shared authenticated parent layout
    - public layout
    - public home / landing
    - dashboard
  - the audit concludes that the biggest remaining drift is still structural:
    - public home is still login-first instead of landing-first
    - the authenticated shell is still product-shell-first instead of
      flagship-frame-first
    - dashboard still reads as stacked sections instead of one composed
      overview tableau
  - recommended execution order is now:
    - parent layout contract freeze
    - public layout/home rebuild
    - dashboard structural convergence

- 2026-04-28: production deploy drift check is current:
  - `GET https://aviary.luckysparrow.ch/health` returned `status=ok`
  - `release_readiness.ready=true`
  - production runtime build revision:
    - `35727c8f0451d9c7f95f338c345e67021084c219`
  - local `HEAD`:
    - `38960d9555ea40359623d978f48bce4fa43b5f48`
  - `origin/main`:
    - `35727c8f0451d9c7f95f338c345e67021084c219`
  - conclusion:
    - production matches `origin/main`
    - production does not yet contain the latest local flagship/chat UI commits
    - deployed screenshot parity for `PRJ-743` should wait until the latest
      local web changes are pushed and deployed

- 2026-04-28: `PRJ-774` repaired internal app chat send responsiveness:
  - the issue was frontend-local timing rather than a backend transcript
    contract failure
  - before the fix, the web chat UI waited for `api.sendChatMessage(text)` and
    then added an assistant pending item, so the user-authored message only
    appeared after the `/app/chat/history` refresh
  - `web/src/App.tsx` now appends the user turn immediately as transient UI
    state with `delivery_state=sending`, updates that turn to
    `delivery_state=delivered` when the real `/app/chat/message` response
    arrives, appends the real assistant reply, and reconciles local items away
    once `/app/chat/history` contains the same event
  - `web/src/index.css` adds compact delivery-status indicators for sending,
    delivered, and failed local user turns
  - the durable chat source of truth remains `/app/chat/history`; no second
    chat store, backend route, schema, prompt, memory, or action-layer path was
    introduced
  - validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "chat"; Pop-Location`
      - `8 passed, 109 deselected`
    - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-774-fix-internal-chat-optimistic-turn-status.md`
  - in-app browser proof remains blocked in this local environment because the
    browser-client runtime requires Node `>= v22.22.0`, while the available
    runtime is `v22.13.0`

- 2026-04-28: production conversation-silence triage found that the current
  production host is up and the foreground runtime path answers normally:
  - `GET https://aviary.luckysparrow.ch/health` returned `status=ok`
  - `release_readiness.ready=true`
  - `POST https://aviary.luckysparrow.ch/event` returned a normal API reply
    with `runtime.action_status=success`
  - Telegram configuration posture is ready
    (`conversation_channels.telegram.round_trip_state=provider_backed_ready`),
    but observed Telegram ingress/delivery counters are all zero
    (`ingress_attempts=0`, `delivery_attempts=0`, `last_ingress={}`,
    `last_delivery={}`)
  - the current evidence points toward webhook/linking/transport visibility
    rather than a broken foreground runtime pipeline
  - `PRJ-770` is now complete locally:
    - dashboard now fetches `/health` and renders a conversation-channel status
      band from backend-owned Telegram ingress/delivery truth
    - the status distinguishes live delivery, configured-but-idle, rejected or
      failing webhook traffic, loading, and unavailable health states
    - focused validation passed:
      - `Push-Location .\web; npm run build; Pop-Location`
    - local dashboard smoke passed:
      - `http://127.0.0.1:5177/dashboard` returned HTTP `200`
- 2026-04-28: the flagship canonical convergence lane now has a detail-level
  final checklist in:
  - `docs/planning/final-flagship-canonical-detail-checklist.md`
  - `PRJ-772` is now complete as the bounded last-mile execution loop for
    `dashboard`, `chat`, and `personality`
  - the completed slice used rhythm, hierarchy, crop, and mobile compression
    passes instead of any new route topology changes
  - deeper verification then sent one synthetic Telegram-shaped request without
    the webhook secret and observed the expected production rejection:
    - `403 Invalid Telegram webhook secret token.`
    - `/health.conversation_channels.telegram.ingress_attempts=1`
    - `/health.conversation_channels.telegram.ingress_rejections=1`
    - `/health.conversation_channels.telegram.last_ingress.reason=invalid_webhook_secret`
  - this confirms the production `/event` route and Telegram telemetry work
    when Telegram-shaped traffic reaches the app
  - the remaining high-value check is secret-backed Telegram provider
    inspection (`getWebhookInfo`, listen probe, and restore), captured as
    `PRJ-773`
  - `PRJ-773` then reset the production Telegram webhook through the existing
    server-owned route:
    - `POST https://aviary.luckysparrow.ch/telegram/set-webhook`
    - response: `ok=true`, `result=true`, `description=Webhook was set`
  - post-repair production health confirmed real Telegram recovery:
    - `ingress_processed=1`
    - `delivery_attempts=1`
    - `delivery_successes=1`
    - `last_ingress.state=processed`
    - `last_delivery.state=sent`
  - focused Telegram regressions passed with `24 passed, 210 deselected`

- 2026-04-28: the active canonical `chat` screen target is now the supplied v4
  approved snapshot:
  - canonical asset:
    - `docs/ux/assets/aion-chat-canonical-reference-v4.png`
  - source image:
    - `C:\Users\wrobl\Desktop\UIUX\aion - chat - v4.png`
  - UX source-of-truth and active convergence plans now point future `chat`
    parity work at v4 instead of the previous v2 reference
  - this was a docs-and-asset target freeze only; no web implementation files
    were changed by this slice

- 2026-04-27: the first Aviary web-brand repair pass is now complete locally:
  - active user-facing `AION` product naming in the shell source has been
    replaced with `Aviary`
  - the reusable shell wordmark now renders the provided Aviary SVG alongside
    the visible `AVIARY` wordmark
  - the lockup typography has been tightened toward the approved premium
    `Cormorant Garamond` plus `Inter` baseline
  - browser screenshot parity is still pending because the in-app browser
    runtime could not execute in this environment
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`

- 2026-04-27: another canonical flagship calming pass is now complete locally:
  - dashboard closure now converges more tightly toward the canonical scenic
    lower band:
    - the separate reflection-plus-summary ending has been compressed into one
      premium summary band
    - the scenic closure side now carries more weight than the stat side
  - chat is now materially calmer and more conversation-first:
    - transcript metadata is time-first instead of role-plus-channel-heavy
    - raw payload detail drawers are removed from the flagship transcript
    - the extra `response path` support card is removed so the right column
      stays closer to the canonical support posture
    - route CSS now normalizes the headline emblem and send-button symbol
      rendering
  - personality is now shorter and closer to the canonical overview:
    - the extra `layer map` explainer section below the hero/timeline surface
      is removed
    - the route now centers the canonical trio more clearly:
      - figure stage
      - mind-layers timeline
      - editorial right-column panels
  - one proof constraint is now explicit:
    - in-app browser automation is locally blocked because the available
      `node_repl` runtime reports Node `v22.13.0`, while the browser runtime
      currently requires `>= v22.22.0`
    - until that runtime is upgraded, live parity loops should continue using
      manual deploy review and the stored production screenshot evidence
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`

- 2026-04-28: one more canonical flagship hero-stage pass is now complete
  locally:
  - dashboard hero now has:
    - stronger card-to-figure connective tension
    - a slightly larger center scene
    - a calmer desktop split that favors the embodied stage over the guidance
      column
  - chat portrait support now has:
    - a warmer crop
    - a lower planning inset
    - a slightly more transcript-first desktop balance
  - personality hero now has:
    - a taller figure stage
    - clearer connector endpoints
    - stronger callout visibility around the embodied map
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`

- 2026-04-26: the canonical first-party production host baseline is now:
  - `https://aviary.luckysparrow.ch`
  - the approved deployment posture remains same-origin:
    - the same host serves the web shell and backend routes
    - no separate API subdomain is part of the baseline
  - the Telegram webhook target should now be:
    - `https://aviary.luckysparrow.ch/event`

- Name: Personality / AION
- Goal: build a memory-aware AI runtime that receives events, reasons through a
  structured pipeline, replies through API or Telegram, and learns lightweight
  user preferences over time
- Commercial model: TBD
- Current phase: no-UI V1 baseline achieved in repo; core-V1 time-aware planning revision now active before later organizer-tool onboarding
- 2026-04-26: the canonical first-party product brand baseline is now frozen
  locally:
  - the app-shell brand is now explicitly:
    - `Aviary`
  - the approved web brand pair is now:
    - `Cormorant Garamond` for the `AVIARY` wordmark and flagship headers
    - `Inter` for operational UI and body copy
  - the canonical bird logomark assets are now stored in:
    - `docs/ux/assets/aviary-logomark.svg`
    - `docs/ux/assets/aviary-logomark-preview.png`
    - `web/public/aviary-logomark.svg`
    - `web/public/aviary-logomark-preview.png`
  - the embodied digital personality remains intentionally unnamed in the
    product shell
  - the web shell now uses the Aviary brand lockup in the authenticated rail
    and compact mobile header, while personality-facing copy no longer assigns
    a fixed proper name to the presence
  - UX source-of-truth docs are now updated in:
    - `docs/ux/brand-personality-tokens.md`
    - `docs/ux/aion-visual-motif-system.md`
    - `docs/ux/design-memory.md`
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-26: the repo now also freezes the next communication-expansion lane
  around canonical multi-channel conversation and relational outreach:
  - internal authenticated app chat remains the canonical conversation owner
  - linked Telegram is now explicitly treated as ingress/egress mirror over
    the same user continuity after account linking
  - long transport-limited replies may segment on Telegram, but the canonical
    app reply remains the semantic source of truth
  - proactive propagation is now approved as relation-sensitive and adaptive,
    not fixed to one global silence timeout
  - one execution-ready implementation plan now lives in:
    - `docs/planning/canonical-multi-channel-conversation-and-relational-outreach-plan.md`
  - the seeded execution queue is:
    - `PRJ-750` Freeze canonical multi-channel conversation contract
    - `PRJ-751` Freeze relational outreach governance contract
    - `PRJ-752` Add channel-affinity and response-cadence adaptive outputs
    - `PRJ-753` Add sleep and quiet-pattern inference boundary
    - `PRJ-754` Add explicit user channel-preference posture
    - `PRJ-755` Canonicalize linked-channel ingress into app-owned continuity
    - `PRJ-756` Mirror linked-channel replies from one canonical answer
    - `PRJ-757` Preserve canonical semantics during transport segmentation
    - `PRJ-758` Add channel-choice policy for proactive outreach
    - `PRJ-759` Add adaptive silence interpretation
    - `PRJ-760` Preserve mandatory reply posture for user-authored turns
    - `PRJ-761..PRJ-763` proof, observability, and rollout sync
- 2026-04-26: the proactive transcript-truth and conscious outbound
  governance repair lane is now complete locally:
  - scheduler-owned wakeups now persist bounded transcript visibility markers
    so internal prompt text no longer impersonates user-authored turns
  - `/app/chat/history` now keeps delivered scheduler outreach visible as
    assistant output while hiding internal scheduler prompts from the app
    transcript
  - plain `time_checkin` wakeups now default toward silent conscious analysis
    unless active-work or relation signals justify outreach
  - unanswered proactive counting now skips unrelated internal/system memory
    rows instead of resetting anti-spam posture prematurely
  - regression coverage now pins:
    - transcript truth
    - delivered-scheduler-assistant visibility
    - silent low-value time-checkin behavior
    - anti-spam continuity across internal memory rows
  - operator guidance is now updated in:
    - `docs/operations/runtime-ops-runbook.md`
  - one explicit decision gate still remains open before any cross-channel
    proactive escalation is implemented:
    - no escalation
    - delivery-failure-only escalation
    - silence-window escalation with explicit channel-priority ownership
- 2026-04-26: `PRJ-742` is now complete locally:
  - the authenticated shell now exposes `/dashboard` as a first-class route
    and the default post-login destination
  - `web/src/App.tsx` now reuses existing shell-owned data to render one new
    flagship overview surface with:
    - central embodied figure stage
    - flanking signal cards
    - insights and guidance column
    - cognitive-flow band
    - lower overview cards for goals, focus, memory, reflection, and module
      entry
  - `web/src/index.css` now carries one shared flagship overview pattern for
    future authenticated surfaces rather than introducing a parallel dashboard
    style family
  - design-memory is now updated with:
    - flagship overview stage
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-26: the first dashboard-specific convergence loop is now explicit:
  - production health and root HTML both confirm deploy parity on runtime build
    revision:
    - `ffd9401766e5219366feeed65804ce8585ed0aed`
  - one dashboard-only compare loop plan now lives in:
    - `docs/planning/dashboard-canonical-convergence-loop-plan.md`
  - the current remaining dashboard drift is explicitly frozen as:
    - hero-stage atmosphere and connective detail
    - stronger guidance-column hierarchy
    - more integrated cognitive-flow band
    - selective need for bespoke artwork where CSS-only treatment flattens the
      route
- 2026-04-26: one additional asset-backed dashboard pass is now complete
  locally:
  - new dashboard scenic assets now exist in:
    - `docs/ux/assets/aion-dashboard-intention-background-v1.png`
    - `docs/ux/assets/aion-dashboard-summary-band-reference-v1.png`
    - `web/public/aion-dashboard-intention-background-v1.png`
    - `web/public/aion-dashboard-summary-band-reference-v1.png`
  - the dashboard now uses those assets to strengthen:
    - the right-column intention card
    - the lower scenic summary closure
  - design memory is now updated with:
    - dashboard scenic closure
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-26: another flagship-shell convergence pass is now complete locally:
  - the shared shell utility bar now moves closer to the canonical route
    controls through:
    - memory continuity signal
    - conversation language signal
    - linked-channel signal
  - dashboard now has one dedicated hero-stage atmosphere asset in:
    - `docs/ux/assets/aion-dashboard-hero-atmosphere-reference-v1.png`
    - `web/public/aion-dashboard-hero-atmosphere-reference-v1.png`
  - `web/src/App.tsx` and `web/src/index.css` now use that asset to deepen:
    - the central cognition field
    - the embodied-figure stage
    - the perceived connection between flanking dashboard signals and the
      center stage
  - chat now has one softer ambient canvas overlay and personality now has
    explicit callout connectors so the three flagship routes read more like
    one family
  - design memory is now updated with:
    - dashboard cognition field
- 2026-04-26: one more route-family refinement pass is now complete locally:
  - dashboard cognitive flow now reads less like six separate cards and more
    like one calmer orchestration band
  - personality side insight panels now carry a more premium editorial surface
    treatment, improving parity with the canonical route without changing
    topology
- 2026-04-26: one logged-in production audit against the canonical flagship
  route set is now recorded and partially implemented locally:
  - audit evidence now exists in:
    - `.codex/artifacts/production-audit-2026-04-26/`
  - the bounded final convergence plan now lives in:
    - `docs/planning/flagship-production-audit-and-final-convergence-plan.md`
  - the latest local shell pass now responds to the highest-value audited
    drift through:
    - removing redundant route-hero banners from `dashboard` and
      `personality`
    - shortening the dashboard by removing the extra module-entry / route
      highlights row
    - adding a premium starter transcript for empty-history `chat`
    - moving the `chat` portrait support higher in the right column
    - removing the long payload-browser section from the flagship
      `personality` route
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-26: another proportion-tuning pass is now complete locally:
  - dashboard hero now gives more visual dominance to the central embodied
    stage while slightly reducing guidance-column weight
  - chat stage now leans a little more transcript-first on desktop
  - personality hero stage is now larger and more ceremonial, improving
    parity with the canonical preview composition
- 2026-04-26: `PRJ-733` is now complete:
  - the approved canonical web-screen set is now stored in:
    - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
    - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
    - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
    - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
  - route-level UX truth and the screenshot-parity workflow now live in:
    - `docs/ux/canonical-web-screen-reference-set.md`
    - `docs/ux/aion-visual-motif-system.md`
    - `docs/ux/design-memory.md`
  - future motif-led web changes should now capture post-deploy screenshot
    proof against these canonical route targets instead of relying on prompt
    history alone
- 2026-04-26: `PRJ-732` is now complete:
  - `aion_profile` now carries one profile-owned `utc_offset` setting for
    explicit local-time continuity
  - authenticated `/app/me/settings` and the web settings surface now persist
    bounded `UTC±HH:MM` values without adding a broader timezone subsystem
  - runtime now localizes current-turn timestamp truth from the stored offset
    before date/time-sensitive replies are generated
  - focused validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_memory_repository.py tests/test_expression_agent.py tests/test_schema_baseline.py; Pop-Location`
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-26: `PRJ-723` is now complete:
  - the repository now has one approved visual motif snapshot at
    `docs/ux/assets/aion-visual-motif-reference.png`
  - `docs/ux/aion-visual-motif-system.md` now freezes the embodied cognition
    design language for future web-first rollout
  - the visual lane is now expanded into a dashboard-first system plan:
    `docs/planning/dashboard-foundation-and-personality-visual-system-plan.md`
  - the visual implementation queue now runs through `PRJ-731`, starting with
    dashboard foundation and then `personality` on shared primitives
- 2026-04-26: `PRJ-724..PRJ-727` are now complete locally:
  - `web/src/index.css` now exposes one shared AION visual layer with warm
    background treatment, reusable glass surfaces, chips, flow rails, and
    motif-oriented decorative primitives
  - `web/src/App.tsx` now uses that shared system to turn `/chat` into a
    dashboard-first front door with:
    - motif-led hero
    - transcript-first continuity panel
    - cognitive-flow sidebar
    - reusable module-entry cards for `personality`, `tools`, and `settings`
  - `settings`, `tools`, and `personality` now inherit the same shared surface
    grammar instead of reading like older independent screens
  - the latest local shell pass extends that reuse further:
    - `settings` now opens with the same hero-and-chip posture as the dashboard
    - `tools` now uses the same route hero before grouped capability sections
    - `personality` now adds one richer embodied layer map plus pipeline rail
      on top of the backend-owned overview payload
    - mobile now has explicit route navigation inside the authenticated shell
    - the chat composer no longer obscures transcript reading order
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
      -> build passed
- 2026-04-26: `PRJ-728` remains the next UX verification slice:
  - initial mocked screenshot proof for the refreshed shell now exists in:
    - `.codex/artifacts/local-chat-desktop-mocked-v2.png`
    - `.codex/artifacts/local-chat-mobile-mocked-v2.png`
    - `.codex/artifacts/local-personality-desktop-mocked.png`
    - `.codex/artifacts/local-personality-mobile-mocked.png`
    - `.codex/artifacts/local-tools-desktop-mocked.png`
    - `.codex/artifacts/local-settings-desktop-mocked.png`
  - full `PRJ-728` closure still needs:
    - tablet capture
    - real loading/empty/error/success proof on live backend data
    - explicit accessibility and reduced-motion review notes
- 2026-04-26: chat shell reference pass is now complete locally:
  - `web/src/App.tsx` now turns `/chat` into a dedicated workspace closer to the
    approved visual target:
    - desktop left rail for module navigation and account posture
    - chat-specific top control bar with memory/language/channel/account pills
    - three-part workspace with transcript, cognitive flow rail, and embodied
      portrait panel
    - bottom feature strip mirroring the continuity / channels / memory /
      reflection / privacy framing from the approved mockup
  - `web/src/index.css` now carries the route-specific primitives needed for
    that workspace:
    - app rail
    - chat transcript cards
    - control pills
    - flow stages
    - portrait panel
    - feature strip
  - refreshed mocked proof now exists in:
    - `.codex/artifacts/chat-reference-pass-desktop.png`
    - `.codex/artifacts/chat-reference-pass-mobile-v2.png`
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-26: chat background art integration is now complete locally:
  - the generated premium chat artwork is now stored as:
    - `docs/ux/assets/aion-chat-background-reference-v1.png`
    - `web/public/aion-chat-background-reference-v1.png`
  - the chat portrait zone now uses that real art layer instead of relying only
    on CSS-built geometric illustration
  - updated mocked proof now exists in:
    - `.codex/artifacts/chat-background-asset-pass-desktop.png`
    - `.codex/artifacts/chat-background-asset-pass-mobile.png`
  - design guidance is now synced in:
    - `docs/ux/design-memory.md`
    - `docs/ux/aion-visual-motif-system.md`
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-26: chat premium polish pass is now complete locally:
  - the chat header now carries a clearer live-conversation accent state
  - the portrait zone now includes a planning overlay card, bringing the route
    closer to the approved premium-chat composition
  - the bottom feature strip now reads more like one editorial information band
    than a row of generic utility cards
  - refreshed proof now exists in:
    - `.codex/artifacts/chat-premium-polish-pass-desktop.png`
- 2026-04-26: canonical shell-and-chat convergence planning is now complete:
  - production and local screenshot review confirm the current drift is now
    compositional rather than directional:
    - shell still reads too heavy and too dashboard-like for canonical `chat`
    - `chat` still exposes too much process structure in the foreground
    - the right-side support area still needs a calmer, more ambient hierarchy
  - the execution-ready plan now lives in:
    - `docs/planning/canonical-authenticated-shell-and-chat-convergence-plan.md`
  - the next seeded convergence lane is:
    - `PRJ-735` Shared Authenticated Shell Spine And Chrome Reduction
    - `PRJ-736` Chat Transcript, Quick Actions, And Composer Convergence
    - `PRJ-737` Chat Support Column And Ambient Embodiment Convergence
    - `PRJ-738` Personality Convergence On The Shared Canonical Shell
    - `PRJ-739` Shared Route Art, Material, And Typography Polish
    - `PRJ-740` Responsive, State, And Accessibility Proof
    - `PRJ-741` Production Screenshot Parity And Baseline Freeze
- 2026-04-26: the first shell-convergence implementation slice is now complete locally:
  - `web/src/App.tsx` and `web/src/index.css` now reduce authenticated shell chrome and push `chat`
    toward a calmer premium posture:
    - narrower, lighter left rail
    - softer transcript cards
    - integrated composer zone
    - condensed right support column instead of a large explicit process rail
  - this slice closes part of the compositional gap to the canonical `chat`
    target, but does not yet claim parity
  - the next smallest remaining implementation gap is:
    - `PRJ-736` for transcript softness, top-control density, and tighter composer integration
- 2026-04-26: the second chat-convergence implementation slice is now complete locally:
  - `chat` top controls now read lighter and calmer through stacked pill treatment
  - transcript cards now foreground conversation copy more strongly than route mechanics
  - the quick-action row and composer now behave more like one shared premium action tray
  - the route is materially closer to the canonical `chat` target, but still needs:
    - final premium polish across route family consistency
    - `personality` convergence on the refined shell
    - explicit responsive and post-deploy screenshot parity proof
- 2026-04-26: flagship dashboard/chat/personality parity planning is now expanded:
  - one more detailed route-family convergence plan now lives in:
    - `docs/planning/dashboard-chat-personality-canonical-parity-plan.md`
  - the new plan narrows the remaining route-family work to:
    - dashboard-first shell framing
    - `chat`
    - `personality` preview
- 2026-04-26: the next flagship convergence implementation slices are now complete locally:
  - the shared authenticated shell now carries a richer dashboard-first utility bar
  - `personality` now uses one route-specific embodied figure asset stored in:
    - `docs/ux/assets/aion-personality-figure-reference-v1.png`
    - `web/public/aion-personality-figure-reference-v1.png`
  - the top `personality` preview now behaves much closer to the canonical route:
    - anchored callouts
    - mind-layer timeline
    - stronger conscious/subconscious/recent-activity side panels
  - the remaining route-family gap is now primarily:
    - cross-route premium polish
    - responsive proof
    - post-deploy screenshot parity
- 2026-04-26: one additional flagship-shell premium pass is now complete locally:
  - the shared authenticated frame now has calmer flagship chrome and stronger
    editorial posture through:
    - richer utility-bar context
    - softer left-rail storytelling
    - wider desktop shell proportions
  - `chat` now moves closer to the canonical route through:
    - lighter topbar hierarchy
    - removal of duplicate account chrome inside the route body
    - a more integrated composer tray with embedded support actions
  - `personality` now carries a more canonical preview posture through:
    - a dedicated preview-tab strip above the embodied overview
    - stronger visual continuity between the route hero and the main figure stage
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-25: `PRJ-707` is now complete:
  - the GUI-language selector now rests on one shared locale metadata model
    carrying value, native label, localized label, icon token, and explicit
    system fallback semantics
  - locale-icon posture no longer depends on emoji flags and is now explicit
    enough for later web-to-mobile reuse
- 2026-04-26: `PRJ-709` is now complete:
  - authenticated `chat`, `settings`, `tools`, and `personality` were reviewed
    across mobile, tablet, and desktop breakpoints after the second UX/UI lane
  - screenshot evidence and review notes now live in
    `.codex/artifacts/prj709-authenticated-route-sweep/`
  - the accepted shell baseline now points to polish-level follow-up only,
    rather than product-structure gaps
  - the `ui_language` boundary remains separate from runtime-owned
    conversation language
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
      -> build passed
- 2026-04-26: `PRJ-710` is now complete:
  - the second UX/UI lane is now closed with one accepted baseline across
    login posture, product copy, responsive shell rules, state semantics,
    locale metadata, hierarchy cleanup, and authenticated route proof
  - accepted evidence now points to
    `.codex/artifacts/prj705-responsive-proof/`,
    `.codex/artifacts/prj708-visual-hierarchy-proof/`, and
    `.codex/artifacts/prj709-authenticated-route-sweep/`
  - this closure handed the queue back to transcript continuity work, starting
    with `PRJ-712`
- 2026-04-26: `PRJ-712` is now complete:
  - `/app/chat/history` is now frozen as a transcript-oriented app-facing
    contract instead of a memory-entry surface
  - the frozen contract keeps one backend-owned continuity owner across app
    chat and linked Telegram, sets the default app-facing window to the latest
    `10` messages, and fixes chronological oldest-to-newest ordering
  - this freeze handed the execution queue to `PRJ-713` for backend transcript
    projection
- 2026-04-26: `PRJ-713` is now complete:
  - `/app/chat/history` now projects existing episodic turn memory into
    transcript items derived from `payload.event` and `payload.expression`
  - the endpoint now defaults to the latest `10` transcript items and returns
    them oldest-to-newest, with normalized `api|telegram` channel posture
  - focused backend validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_memory_repository.py; Pop-Location`
      -> 171 passed
- 2026-04-26: `PRJ-714` is now complete:
  - `web/src/lib/api.ts` now matches the backend transcript item shape instead
    of the old memory-entry interpretation
  - the web chat route now renders one backend-owned transcript thread and
    removes the separate continuity sidebar from `/chat`
  - initial transcript load now scrolls to the bottom, and new assistant
    replies are revealed from the top edge after send
  - focused web validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- 2026-04-26: `PRJ-715` is now complete:
  - route regressions now prove linked Telegram and app turns appear in the
    same authenticated `/app/chat/history` transcript
  - unlinked Telegram traffic now has explicit regression coverage proving it
    does not impersonate app-auth transcript continuity
  - runtime regression now proves one shared continuity owner can project both
    `api` and `telegram` turns into the same transcript
  - focused backend validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py; Pop-Location`
      -> `218 passed`
- 2026-04-26: `PRJ-716` is now complete:
  - `docs/planning/mobile-client-baseline.md` now defines
    `/app/chat/history` as a shared message transcript with latest-`10`
    posture, oldest-to-newest ordering, and one continuity owner across app
    chat and linked Telegram
  - `mobile/README.md` and `docs/overview.md` now point at the same
    transcript-safe first-party client contract
  - doc-and-context cross-review passed for the shared client baseline
- 2026-04-26: `PRJ-717` is now complete:
  - final validation passed:
    - backend full suite: `942 passed`
    - web build: passed
  - `.codex/context/LEARNING_JOURNAL.md` now records the scheduler
    quiet-hours test guardrail confirmed during full-suite validation
  - source-of-truth files now reflect the shared transcript continuity lane as
    complete through `PRJ-717`
- 2026-04-25: `PRJ-706` is now complete:
  - the shell now uses one shared product-state posture for loading, empty,
    success, and error feedback across public and authenticated surfaces
  - success and error feedback now leads with short product guidance, while
    operational detail remains available as secondary expandable detail
  - route states remain thin wrappers over the same backend-owned contracts
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
      -> build passed
- 2026-04-25: `PRJ-705` is now complete:
  - the authenticated shell now treats tablet as a distinct product tier:
    mobile keeps bottom navigation, tablet uses top navigation plus a richer
    route summary strip, and desktop keeps the wider two-column posture
  - chat, settings, tools, and personality now enter multi-column layouts
    earlier on larger tiers without duplicating shell logic per route
  - screenshot proof for the responsive posture now lives in
    `.codex/artifacts/prj705-responsive-proof/`
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
      -> build passed
- 2026-04-25: `PRJ-704` is now complete:
  - shared product copy across the shell now avoids backend, contract,
    endpoint, and payload framing on user-facing surfaces
  - route descriptions, settings labels, tools states, and personality
    summaries now read as product guidance instead of implementation posture
  - any remaining technical detail is demoted to secondary details rather than
    primary route messaging
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
      -> build passed
- 2026-04-25: `PRJ-703` is now complete:
  - the public `web` login route now leads with return-to-conversation value
    framing instead of architecture-first hero language
  - unauthenticated trust cards now explain fast workspace return, preference
    control, and runtime-reset ownership without surfacing backend or endpoint
    wording
  - the public build revision badge has been removed from the primary
    unauthenticated session-entry view
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
      -> build passed
- 2026-04-25: fresh product and ops analysis now seeds one bounded
  destructive-data lane through `PRJ-722`:
  - production-wide cleanup and per-user self-service reset are now explicitly
    treated as different contracts rather than one ambiguous "clear data"
    action
  - the approved architecture can support a self-service user reset by reusing
    backend-owned auth, profile, and per-user continuity ownership without
    creating a second settings or workspace subsystem
  - production-wide cleanup is now planned as an operator-only maintenance flow
    and must not be exposed through normal product UI
  - later user clarification now freezes the self-service reset boundary more
    tightly:
    - connected APIs, linked integrations, and user settings should remain
      unchanged
    - the reset should remove runtime continuity so the user can start "from
      new" without reconfiguration
  - the repo now contains one execution-ready plan in
    `docs/planning/user-data-reset-and-production-cleanup-plan.md`
  - the seeded implementation order is:
    - `PRJ-719` Reset Boundary Contract And Retention Policy Freeze
    - `PRJ-720` Shared Backend Cleanup Owner And Operator Script
    - `PRJ-721` Account Settings Reset UX And Confirmation Flow
    - `PRJ-722` Regression Proof, Ops Runbook, And Context Sync
  - `PRJ-719` is now complete:
    - canonical contract truth now freezes self-service reset as a
      runtime-continuity reset, not account deletion
    - auth identity, profile settings, linked integrations, linked channels,
      and user-managed operational preferences remain preserved
    - per-user runtime continuity, adaptive state, internal planning state,
      attention/reflection state, and proposal state are inside the destructive
      scope
    - the first implementation posture revokes all auth sessions, including
      the current session, after reset
  - `PRJ-720` is now complete:
    - backend now has one shared cleanup owner in
      `backend/app/memory/repository.py` for:
      - single-user runtime reset
      - runtime-only cleanup preserving auth/profile state
    - `POST /app/me/reset-data` now reuses that owner instead of duplicating
      per-table delete logic in the route layer
    - operator entrypoints now exist in
      `backend/scripts/run_user_data_cleanup.{py,ps1,sh}`
    - focused regression coverage now proves:
      - runtime continuity is cleared
      - managed settings and linked profile state are preserved
      - all auth sessions are revoked after reset
  - `PRJ-721` is now complete:
    - the web settings route now exposes a dedicated destructive reset card
      instead of hiding reset inside the normal settings save flow
    - the UI now explains the retention boundary explicitly:
      - clear runtime continuity and learned state
      - preserve account, profile, UI settings, proactive preference, and
        linked integrations
    - the reset CTA stays locked until the exact confirmation phrase is
      entered, then returns the user to `/login` after backend session
      revocation
  - `PRJ-722` is now complete:
    - runtime ops guidance now records the bounded operator cleanup commands
      and the preserved-versus-cleared destructive boundary
    - testing guidance now records the required evidence for reset and cleanup
      slices across repository, route, and web-shell surfaces
    - full-lane validation passed:
      - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
        -> `937 passed`
      - `Push-Location .\web; npm run build; Pop-Location`
        -> build passed
    - the destructive-data lane seeded through `PRJ-722` is now complete
- 2026-04-25: approved post-no-UI `v2` entry direction is now explicit:
  - the repository should evolve toward product-facing top-level folders
    `backend/`, `web/`, and `mobile/`
  - the current Python + FastAPI AION runtime remains the backend owner and is
    expected to move into `backend/`
  - `web/` is the first dedicated UI surface
  - `mobile/` is now part of the approved product topology, even if it lands
    after the first web release
  - first-party auth/session should be backend-owned
  - repo-driven production deploy after push must remain truthful through the
    topology change instead of becoming a manual or undocumented side path
- 2026-04-25: `PRJ-664..PRJ-666` are complete:
  - `web/` now contains the first functional product shell for login/register,
    user settings, chat, and personality inspection
  - the browser client remains a thin consumer of backend-owned `/app/*`
    contracts instead of recreating domain logic in the client
  - the production image now builds `web/`, FastAPI serves the built SPA, and
    release smoke validates that the served web revision matches backend
    runtime build truth after push
- 2026-04-25: a new `v2` follow-up planning lane is now seeded for
  tool-and-channel visibility in the first-party web client:
  - the next product-facing settings expansion should expose one dedicated
    backend-owned tools overview instead of asking the web client to infer
    connector truth from mixed inspection payloads
  - UI switches must distinguish:
    - integral product capabilities that are always on
    - user-owned enablement preferences
    - provider readiness blocked by environment configuration
  - Telegram should be planned as a user-linking flow between backend auth
    identity and an existing bot/channel, not as browser-managed secret entry
  - future third-party integrations such as Trello or a custom Nest app
    should enter through the same grouped tools model rather than ad hoc
    settings cards
- 2026-04-25: `PRJ-669..PRJ-670` are complete:
  - backend now exposes `GET /app/tools/overview` as the authenticated
    app-facing grouped tools and channels contract
  - the response is composed from connector execution truth, organizer-stack
    readiness, web knowledge tooling, Telegram channel telemetry, and current
    user preference state instead of duplicating connector logic in the client
  - integral first-party capabilities such as internal chat, web search, and
    web browser are now explicit app-facing states
  - Telegram is surfaced as provider-backed but link-required, while Trello
    and Nest remain truthful planned placeholders
- 2026-04-25: `PRJ-671` is complete:
  - `web/` now includes a dedicated `Tools` route backed by
    `GET /app/tools/overview`
  - the first browser tools screen renders grouped communication, task,
    knowledge, and organizer sections directly from backend truth
  - the UI is intentionally read-only where backend mutation or user linking
    is not implemented yet, avoiding false affordances for provider setup or
    user toggles
- 2026-04-25: `PRJ-672` is complete:
  - backend now persists user-owned tool and channel enablement through the
    existing conclusion-backed preference mechanism instead of a second
    settings subsystem
  - `PATCH /app/tools/preferences` now updates supported toggles for Telegram,
    ClickUp, Google Calendar, and Google Drive
  - `GET /app/tools/overview` now distinguishes provider readiness from
    user-requested enablement and effective enabled state
  - the web `Tools` route now renders working toggles only for supported
    preferences while keeping unsupported items read-only
- 2026-04-25: `PRJ-673` is complete:
  - backend now exposes `POST /app/tools/telegram/link/start` so an
    authenticated user can generate a bounded Telegram link code without
    browser-side secret entry
  - Telegram `/link CODE` commands now attach the confirmed Telegram chat to
    the backend auth identity through the existing profile model instead of a
    parallel linking subsystem
  - `GET /app/tools/overview` now reflects Telegram `not_linked`,
    `pending_confirmation`, and `linked` states separately from provider
    readiness and user enablement
  - the web `Tools` route now shows a real Telegram linking panel with code
    generation and confirmation instructions only when backend truth says the
    channel is enabled and still requires linking
- 2026-04-25: `PRJ-674` is complete:
  - tools/channels proof now includes focused backend regression coverage for
    grouped overview truth, toggle persistence, provider-blocked Telegram
    start posture, and expired Telegram link-code rejection
  - engineering testing guidance now defines the canonical validation commands
    and truth checks for app-facing tools/channels slices
  - overview, ops, and env/config docs now describe the same backend-owned
    tools boundary where provider secrets stay outside product UI and the web
    client remains a thin consumer of backend truth
- 2026-04-25: `PRJ-667` is complete:
  - the initial mobile stack is now frozen as Expo-managed React Native with
    TypeScript and Expo Router
  - the repository now records one shared first-party client-contract baseline
    where `mobile` reuses backend-owned `/app/*` resources instead of creating
    a second mobile-only domain model
  - the mobile baseline explicitly keeps provider-secret handling and internal
    debug surfaces out of the future app workspace
  - native auth transport details remain an explicit bounded follow-up instead
    of being falsely implied as already solved by the stack freeze
- 2026-04-25: user direction now freezes mobile execution after `PRJ-667`:
  - `mobile/` remains an approved future product surface
  - active implementation should stay on `web + backend`
  - the first mobile workspace scaffold is intentionally deferred until a later
    explicit restart of the mobile lane
- 2026-04-25: fresh production UI validation of
  `https://personality.luckysparrow.ch/` now seeds the next stabilization lane
  through `PRJ-680`:
  - register, login, logout, and `POST /app/chat/message` are working on the
    first-party web shell
  - `GET /app/chat/history` currently returns `500`, leaving the continuity
    panel empty even though live chat replies succeed
  - `PATCH /app/me/settings` currently returns `500`, so settings edits do not
    persist through the app-facing contract
  - `/app/tools/overview` and `/app/personality/overview` return `200`, but
    the `Tools` and `Personality` screens stay on loading because the current
    route lifecycle cancels its own request path
  - the shared web API helper currently tries to parse plain-text
    `Internal Server Error` responses as JSON, which surfaces misleading
    browser errors instead of truthful backend failure detail
  - the next queue should therefore repair backend contract health first, then
    the client-side loading and error boundary behavior, then add regression
    and smoke proof for the repaired baseline
- 2026-04-25: local implementation now covers the first repair slice of that
  stabilization lane:
  - `backend/app/memory/repository.py` now serializes chat-memory `source`
    for the app history route and keeps `proactive_opt_in` plus current tool
    toggles in the operational preference family
  - `web/src/lib/api.ts` now handles plain-text backend failures without
    surfacing misleading JSON parser exceptions
  - `web/src/App.tsx` now allows successful `Tools` and `Personality` loads to
    complete and clears stale route-level errors on navigation
  - `backend/scripts/run_release_smoke.ps1` now verifies that `/`, `/chat`,
    `/settings`, `/tools`, and `/personality` all resolve to the same deployed
    web build revision instead of proving only the root route
  - targeted backend route tests, web route tests, release-smoke regressions,
    and a production web build now pass locally
  - first live smoke against deployed commit `7ff715e` proved the backend
    runtime revision had updated, but also exposed one remaining parity gap:
    the served web-shell HTML still reported `aion-web-build-revision=unknown`
  - a follow-up local repair now makes FastAPI inject the runtime
    `APP_BUILD_REVISION` into served SPA HTML so deploy parity no longer
    depends on the frontend bundler receiving the same variable at build time
  - follow-up deploy on commit `ddb327f` is now live in production
  - release smoke now passes against production with matching backend and
    web-shell build revisions
  - authenticated production checks now confirm login, `/app/me`,
    `/app/chat/history`, `/app/me/settings`, `/app/tools/overview`,
    `/app/personality/overview`, chat send, and logout all succeed on the
    repaired baseline
  - the production stabilization lane seeded through `PRJ-680` is now
    complete
- 2026-04-25: fresh linked-account analysis now seeds the next identity
  continuity lane through `PRJ-684`:
  - the Telegram link flow appears to persist `telegram_chat_id` and
    `telegram_user_id` on the authenticated profile and the app-facing tools
    surface truthfully reports `linked`
  - but ordinary Telegram foreground events still appear to normalize under
    the raw Telegram sender identity instead of resolving to the linked
    backend auth `user_id`
  - this likely leaves chat memory, learned preferences, and later recall
    split across two identity owners even after the user completes the
    linking flow successfully
  - the next repair lane is therefore ordered as:
    - freeze the linked-identity resolution contract plus relink conflict rule
    - make Telegram event normalization/runtime identity resolution honor the
      linked backend auth identity
    - add end-to-end regression coverage for shared UI+Telegram memory
      continuity
    - sync task/context truth and record the pitfall in the learning journal
- 2026-04-25: `PRJ-681..PRJ-684` are complete:
  - linked Telegram ingress now resolves to the same backend auth `user_id`
    that first-party `/app/*` traffic uses after the user completes the
    linking flow
  - the runtime keeps the existing raw Telegram sender fallback only for
    unlinked traffic, preserving backward-compatible behavior for chats that
    were never linked
  - Telegram relinking now transfers `telegram_chat_id` and
    `telegram_user_id` ownership to the latest authenticated user instead of
    leaving multiple profiles attached to the same Telegram identity
  - targeted route, event-normalization, and repository regressions now prove
    the repaired linked-identity continuity contract
  - follow-up hardening on the same lane now also merges pre-link legacy raw
    Telegram memory state into the authenticated account during linking, so
    older Telegram-only recall survives the move to shared app+Telegram
    identity continuity instead of staying stranded under the old numeric
    sender bucket
- 2026-04-25: fresh browser UX/UI audit of the current first-party web shell
  now seeds the next product-facing lane through `PRJ-691`:
  - login is visually coherent, but the authenticated shell still repeats too
    much hero and account chrome above the real task area
  - `Chat` is the clearest product route, yet still does not prioritize the
    conversation and composer enough for mobile-first use
  - `Settings` duplicates editable preferences and backend snapshot detail
    instead of behaving like a concise task-focused preference flow
  - `Tools` remains truthful but too inspection-heavy, surfacing capability
    ids, provider posture, and status detail as primary user content
  - `Personality` currently behaves like a raw inspector because summary cards
    and raw JSON payloads share one product-facing route
  - `Tools` and `Personality` therefore are not yet ready to act as the
    interaction baseline for a later Expo mobile client
  - product direction now also freezes one explicit language split for this
    lane:
    - GUI language must become its own first-party shell setting
    - conversation language remains runtime-owned and selected live from
      interaction and continuity
    - the current conversation-language field must not be silently repurposed
      as UI locale
  - product-facing settings should also stop exposing `response style` and
    `collaboration preference` as manual user controls because those behaviors
    should remain runtime-shaped
  - the next queue is intentionally ordered as:
    - `PRJ-685` Mobile-First App Shell Baseline
    - `PRJ-686` UI Language Boundary And Locale Switcher Plan
    - `PRJ-687` Chat Experience And Composer Priority
    - `PRJ-688` Settings Simplification And Runtime-Shaped Preference Cleanup
    - `PRJ-689` Tools Information Architecture And Actionability
    - `PRJ-690` Personality Productization And Inspector Split
    - `PRJ-691` Visual System Hardening, Responsive Proof, And Context Sync
  - the canonical execution plan for this lane now lives in
    `docs/planning/web-ux-ui-productization-plan.md`
- 2026-04-25: `PRJ-685` is complete:
  - the authenticated web shell now uses a compact sticky top bar instead of
    route-level repeated hero chrome
  - desktop keeps route navigation in the top bar, while mobile now uses a
    fixed bottom navigation suitable for a later app-shell transfer
  - account access and sign-out now live in one toggleable account panel
    rather than a permanently expanded summary card
  - the next slice `PRJ-686` is now also complete:
    - canonical architecture now freezes `preferred_language` as
      conversation continuity only
    - the future first-party shell locale field is explicitly planned as
      `ui_language`
    - the planned first selector iteration is bounded to `system`, `en`,
      `pl`, and `de`, rendered as `flag + language label`
    - `response_style` and `collaboration_preference` remain runtime-shaped
      and should not return as manual product-facing settings controls
  - `PRJ-687..PRJ-691` are now complete:
    - `Chat` now prioritizes the thread and sticky composer on mobile while
      keeping continuity as supporting context
    - `Settings` now center on profile, `ui_language`, and proactive
      preferences, and the app-facing contract persists `ui_language`
      separately from conversation continuity
    - `Tools` now frame each capability around state, next step, and optional
      technical detail instead of inspection-heavy density
    - `Personality` now surfaces summary-first insights before raw payload
      inspection
    - the authenticated shell now shares one coherent copy and responsive
      posture across login, chat, settings, tools, and personality
  - the UX/UI lane seeded through `PRJ-691` is now complete; next work should
    come from fresh browser feedback or a new product direction
- 2026-04-25: `PRJ-692` is complete:
  - repository-driven Coolify deploys now include a one-shot `migrate`
    service in `docker-compose.coolify.yml`
  - the deployment graph now runs
    `python -m alembic -c /app/backend/alembic.ini upgrade head` after
    PostgreSQL health and before the long-lived runtime services start
  - `app`, `maintenance_cadence`, and `proactive_cadence` now wait on
    migration success instead of assuming schema changes were applied through
    an out-of-band hook
  - Coolify deployment guidance and the runtime ops runbook now describe the
    same migration-first operator path, which keeps push-driven deploys
    self-contained without paid GitHub automation
- 2026-04-25: `PRJ-693` is complete:
  - release smoke now supports opt-in deploy-parity waiting through
    `-WaitForDeployParity`, `-DeployParityMaxWaitSeconds`, and
    `-DeployParityPollSeconds`
  - live production evidence on 2026-04-25 showed that repo-driven source
    automation can still expose the previous deployed revision for at least
    45 seconds after push, even though the target commit arrives shortly after
  - immediate smoke after push observed deployed revision
    `00ae4eadcca0afe46ce13e88366ab2c744695a36`, while wait-mode smoke later
    passed on `b514a01c3b68d55edecfa247429e5db29867effe`
  - the deploy-proof baseline now distinguishes temporary Coolify propagation
    lag from a real deployment-trigger miss without weakening strict final
    parity checks
- 2026-04-25 to 2026-04-26: the second web UX/UI lane through `PRJ-710` is now
  complete:
  - `/login` now leads with trust, return-to-conversation value, and calmer
    first-viewport posture
  - shared shell copy now reads as product language instead of backend or
    contract framing
  - mobile, tablet, and desktop shell rules are explicit and evidence-backed
  - loading, empty, success, and error states now follow one shared
    product-facing posture
  - GUI language now uses separate app-facing locale metadata and remains
    distinct from runtime-owned conversation language
  - visual hierarchy now relies on headings, overlines, metric tiles, and
    status-bearing chips instead of repeated decorative badge chrome
  - authenticated route proof reduced the remaining UX deltas to polish-level
    follow-up rather than product-structure gaps
  - user direction can now return to the shared transcript continuity lane,
    starting with `PRJ-712`
- 2026-04-25: `PRJ-694` is complete:
  - release smoke now retries transient `/health` failures with bounded
    `HealthRetryMaxAttempts` and `HealthRetryDelaySeconds`
  - live production on 2026-04-25 briefly returned `503 Service Unavailable`
    during deploy convergence and then recovered, so the deploy-proof baseline
    now distinguishes short availability blips from sustained failure
- 2026-04-25: fresh runtime-behavior analysis now seeds the next foreground
  awareness repair lane through `PRJ-702`:
  - linked Telegram identity continuity is repaired, but the active answer path
    can still deny or miss existing capabilities around memory continuity,
    current turn time, bounded search, and bounded page reading
  - the repo already contains the needed foundations:
    - linked backend auth identity resolution for Telegram
    - `event.timestamp` on active turns
    - bounded search and page-read execution in the action layer
    - context and expression stages that can consume more explicit foreground
      runtime truth
  - the remaining gap is therefore a foreground-awareness contract and
    propagation problem, not a need for a second identity, memory, or tool
    subsystem
- 2026-04-25: `PRJ-695` is complete:
  - the repo now contains one detailed execution-ready repair plan in
    `docs/planning/foreground-memory-time-and-tool-awareness-repair-plan.md`
  - the next implementation order is intentionally frozen as:
    - `PRJ-696` Foreground Awareness Contract Freeze
    - `PRJ-697` Runtime Turn-Awareness Payload And Prompt Propagation
    - `PRJ-698` Identity Facts Flow And Truthful Capability Claims
    - `PRJ-699` Implicit Tool Invocation Heuristics For External Facts
    - `PRJ-700` Behavior Regression Proof For Memory, Time, And Tool Awareness
    - `PRJ-701` Canonical Docs And Testing Guidance Sync
    - `PRJ-702` Final Validation, Context Sync, And Learning Closure
- 2026-04-25: explicit user reprioritization resumed the foreground-awareness
  lane and `PRJ-696..PRJ-702` are now complete:
  - foreground runtime now carries one explicit bounded turn-awareness payload
    with current-turn timestamp, known user name, memory continuity posture,
    and bounded `search_web` / `read_page` readiness
  - auth-owned `display_name` now flows into identity/context outputs and can
    answer direct user name-recall turns without inventing a new identity
    subsystem
  - expression now answers direct current-time asks from `event.timestamp`,
    receives explicit foreground-awareness in prompt construction, and rejects
    false capability-denial wording when runtime truth already exposes memory
    continuity or bounded tools
  - planning now infers bounded weather/latest-fact search and page-read for
    URLs or bare domains without requiring literal trigger phrases
  - action-owned bounded external reads can now enrich same-turn delivery text
    while leaving side-effect execution inside the action layer
  - focused validation for the lane passed with `293 passed` across:
    - `tests/test_identity_service.py`
    - `tests/test_openai_prompting.py`
    - `tests/test_context_agent.py`
    - `tests/test_expression_agent.py`
    - `tests/test_planning_agent.py`
    - `tests/test_action_executor.py`
    - `tests/test_runtime_pipeline.py`
- 2026-04-25: fresh product analysis now seeds the next linked-channel chat UX
  lane through `PRJ-717`:
  - linked Telegram identity continuity is already repaired at the backend
    `user_id` owner level, so the next gap is no longer identity split
  - the remaining product gap is that `/app/chat/history` still exposes
    memory-oriented entries while the web shell renders local session messages
    separately from continuity, so the user does not see one shared
    cross-channel transcript
  - the next lane is therefore ordered as:
    - freeze one shared transcript contract for `/app/chat/history`
    - project existing episodic memory into transcript-safe message items
    - unify the web chat thread around backend transcript truth and required
      scroll behavior
    - add linked Telegram plus app-chat regression proof
    - sync mobile baseline and product docs to the shared transcript contract
    - close with final validation and context sync
- 2026-04-24: `PRJ-635` is complete: canonical architecture now freezes one
  explicit core-`v1` time-aware planned-work baseline. Reminders, check-ins,
  routines, and future follow-ups are variants of one internal planned-work
  model, due-item delivery still crosses
  `attention -> planning -> expression -> action`, and organizer-tool
  activation is no longer a hidden prerequisite for core no-UI `v1` closure.
- 2026-04-24: `PRJ-636` is complete: the repo now has one durable
  `planned_work` contract and storage shape, action-owned create/reschedule/
  cancel/complete persistence, and regression coverage without introducing a
  parallel reminder subsystem.
- 2026-04-24: `PRJ-637` is complete: maintenance cadence now reevaluates due
  planned work, marks it `due`, and hands it to the existing subconscious
  proposal boundary instead of sending user-visible delivery directly from the
  background scheduler.
- 2026-04-24: `PRJ-638` is complete: due planned-work handoffs now re-enter
  the normal foreground runtime path, are delivered only through the existing
  `planning -> expression -> action` boundary, and proposal resolution remains
  explicit for scheduler-origin follow-ups.
- 2026-04-24: `PRJ-639` is complete: recurring planned work now advances
  through bounded recurrence rules on the same durable entity, quiet-hours
  sensitive items snooze instead of bypassing delivery guardrails, and expired
  one-off items skip cleanly without creating a second scheduler.
- 2026-04-24: `PRJ-640` is complete: behavior validation now includes `T19.1`
  and `T19.2`, `/health.v1_readiness` and exported incident evidence expose
  the same time-aware planned-work posture, and release smoke now fails when
  that acceptance contract drifts.
- 2026-04-24: `PRJ-641` is complete: bounded autonomous research windows are
  now frozen as `planned_work` variants with explicit trigger, read-only tool,
  and tool-grounded-learning guardrails instead of a separate autonomy engine.
- 2026-04-24: `PRJ-642` is complete: architecture, runtime, testing, ops,
  planning, and context truth now describe the same core no-UI `v1` boundary
  and later organizer-tool extension.
- 2026-04-24: core no-UI `v1` is now explicitly reinterpreted around stable
  conversation, bounded internet reading, tool-grounded learning, and
  internal time-aware planned work. Organizer-tool activation remains prepared
  but is no longer the blocking core-`v1` gate.
- 2026-04-24: `PRJ-632..PRJ-633` are superseded by the approved architecture
  revision. The next queue is now seeded through `PRJ-642` and targets:
  - durable planned future work as an internal-first planning model
  - scheduler-owned reevaluation with foreground delivery through the existing
    action boundary
  - bounded autonomous research windows built on that same model
- 2026-04-24: the queue seeded through `PRJ-642` is now complete. No seeded
  `READY`, `BACKLOG`, or `FUTURE` slice remains for the core time-aware
  planning lane; any follow-up delivery-adaptation work should be derived from
  fresh analysis instead of backlog residue.
- 2026-04-25: fresh repo analysis now seeds the next queue through `PRJ-654`.
  The highest-signal remaining gaps before a fully convincing no-UI `v1`
  are:
  - `v1_readiness` still mixes core-v1 truth with later organizer-extension
    posture in some runtime and regression surfaces
  - some `v1_readiness` gate fields are still static or surface-validity
    summaries rather than live semantic readiness
  - the foreground runtime still lacks one explicit capability-awareness and
    time-awareness contract, so implemented planning, temporal, and bounded
    web capabilities may remain under-signaled to the active turn
  - Telegram delivery is still single-message and plain-text, with no
    channel-aware segmentation or formatting policy
  - high-level docs such as `docs/overview.md` still carry older
    "planned/deferred" wording that no longer matches the implemented runtime
- 2026-04-25: fresh user-driven product analysis now also records a likely
  post-text-delivery follow-up lane:
  - Telegram and later app interaction still need one explicit multimodal
    boundary for photo context, voice-note-to-text intake, and generated image
    reply plus caption
  - current architecture is still text-first at the normalized event and
    response-handoff level, so media behavior should not be treated as already
    covered by the stable no-UI `v1` contract
- 2026-04-25: the next queue is intentionally ordered as:
  - `PRJ-647..PRJ-650` V1 Readiness Truth And Acceptance Boundary
  - `PRJ-651..PRJ-654` Foreground Capability And Time Awareness
  - `PRJ-643..PRJ-646` Channel-Aware Delivery Baseline
- 2026-04-25: `PRJ-647` is complete: canonical architecture, planning truth,
  testing guidance, and runtime reality now explicitly distinguish:
  - core no-UI `v1` acceptance gates
  - mirrored extension posture such as organizer daily use
  - later delivery-quality work such as channel-aware Telegram formatting
- 2026-04-26: `PRJ-648` is now complete:
  - `/health.v1_readiness` now derives conversation, learned-state,
    tool-grounded-learning, and deploy-parity gate states from the live owner
    surfaces instead of treating weaker posture as green
  - organizer daily use remains mirrored for operator visibility, but it is no
    longer included inside the core final acceptance gate bundle
  - `final_acceptance_state` now reports whether the clarified core no-UI `v1`
    bundle is actually green
  - focused backend validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "v1_readiness or telegram_round_trip_readiness_state or deploy_parity_manual_fallback"; Pop-Location`
      -> `3 passed`
- 2026-04-26: `PRJ-649` is now complete:
  - release smoke now verifies that `v1_readiness` stays semantically aligned
    with conversation, learned-state, web-knowledge, organizer, and
    deployment owner surfaces
  - organizer extension posture now causes a smoke failure if it leaks back
    into the core final acceptance bundle
  - focused backend validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "v1_readiness"; Pop-Location`
      -> `4 passed`
- 2026-04-26: `PRJ-650` is now the active doc-sync slice:
  - high-level repo truth now mainly needs wording alignment, not further
    readiness implementation
  - the remaining work in this lane is to make overview, runtime-reality,
    testing, ops, and context tell the same core-v1-versus-extension story
- 2026-04-26: `PRJ-650` is now complete:
  - overview, runtime-reality, testing, ops, and context now tell the same
    core no-UI `v1` versus mirrored organizer-extension story
  - the next active lane is now `PRJ-651..PRJ-654` for explicit foreground
    capability and time awareness
- 2026-04-26: `PRJ-651` is now complete:
  - canonical contracts now freeze foreground awareness as bounded visibility
    of current turn time, active planned-work posture, and approved tool
    readiness
  - execution authority remains unchanged; this freeze only prepares the
    implementation slice in `PRJ-652`
- 2026-04-26: old backlog residue around `PRJ-652..PRJ-654` is now resolved:
  - those slices were already effectively completed by the later
    `PRJ-696..PRJ-702` foreground-awareness lane
  - task files and context now record that coverage instead of implying the
    same runtime, proof, and doc work is still waiting
  - the next true remaining lane is now `PRJ-643..PRJ-646` for channel-aware
    Telegram delivery
- 2026-04-26: `PRJ-643` is now complete:
  - canonical contracts now freeze channel-aware delivery as a delivery-layer
    concern below expression and inside action/integration ownership
  - `PRJ-644` is now the next active implementation slice for Telegram
    segmentation and formatting
- 2026-04-26: `PRJ-644` is now complete:
  - Telegram delivery now segments long outbound responses inside
    `DeliveryRouter` according to transport-owned limits instead of sending one
    raw message
  - Telegram formatting now uses one explicit delivery policy:
    - supported markdown (`**bold**`, inline code, fenced code) normalizes to
      Telegram HTML parse mode
    - structurally unsafe markdown falls back to plain text instead of
      accidental raw markup transport
  - targeted backend validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_telegram_client.py tests/test_action_executor.py -k "telegram or delivery_router" tests/test_api_routes.py -k "telegram_link or telegram_webhook or telegram" tests/test_runtime_pipeline.py -k "telegram"; Pop-Location`
      -> `27 passed`
- 2026-04-26: `PRJ-645` is now complete:
  - release smoke, health, and incident evidence now pin the same Telegram
    delivery-adaptation posture instead of treating channel shaping as hidden
    implementation detail
  - `conversation_channels.telegram` now exposes:
    - `delivery_adaptation_policy_owner`
    - `delivery_segmentation_state`
    - `delivery_formatting_state`
    - last-delivery segment and formatting hints
  - targeted backend validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_observability_policy.py; Pop-Location`
      -> `171 passed`
- 2026-04-26: `PRJ-646` is now complete:
  - runtime reality, testing guidance, ops notes, planning truth, and context
    now describe the same channel-aware Telegram delivery contract
  - the lane `PRJ-643..PRJ-646` is now complete end-to-end
- 2026-04-25: fresh code analysis now shows a narrower product gap after
  truthful readiness:
  - planning, planned work, bounded web search, page reading, and
    tool-grounded learning are implemented
  - but time/context/tool awareness is still only partially explicit in the
    foreground turn contract and reply prompt surfaces
  - the next follow-up lane after `PRJ-650` should therefore make those
    capabilities explicitly knowable to the active turn before delivery polish
    work continues
- 2026-04-25: organizer full provider activation and richer empathy rollout
  remain valuable later lanes, but they are not the first blockers in this
  fresh post-`PRJ-642` queue.
- 2026-04-24: `PRJ-628` is complete: organizer daily-use posture is now proven
  through release smoke, incident-evidence bundles, and behavior validation,
  not only through `/health` or provider-activation summaries.
- 2026-04-24: `PRJ-629` is complete: runtime reality, testing guidance, ops
  notes, planning, and repository context now describe the same organizer
  daily-use proof path and parity with `/health.v1_readiness`.
- 2026-04-24: `PRJ-630` is complete: `/health.v1_readiness` now carries the
  final no-UI `v1` acceptance-bundle contract with named gate states and
  canonical runtime surfaces.
- 2026-04-24: `PRJ-631` is complete: final `T18.1..T18.2` daily-use scenarios
  now prove website-reading recall and organizer follow-up as part of the
  no-UI `v1` acceptance bundle.
- 2026-04-24: `PRJ-627` is complete: organizer-tool runtime truth now exposes
  workflow-level daily-use readiness, and `v1_readiness` reuses that same
  backend truth to summarize whether ClickUp task review and mutation, Google
  Calendar availability inspection, and Google Drive file-space inspection
  are actually ready for daily use.
- 2026-04-24: `PRJ-626` is complete: no-UI `v1` now has one explicit
  daily-use organizer workflow baseline. ClickUp task review and mutation,
  Google Calendar availability inspection, and Google Drive metadata-only
  file inspection are now described as real daily helpers around
  internal-first planning state instead of just raw connector capability
  slices.
- 2026-04-24: `PRJ-625` is complete: runtime reality, testing guidance, ops
  notes, planning, and repository context now all describe the same durable
  capability-record truth model. Future callers no longer need to guess
  whether a capability is merely described, currently selected, or actually
  authorized to execute.
- 2026-04-24: `PRJ-624` is complete: release-smoke and runtime behavior
  coverage now prove that capability-record truth stays honest. The backend
  catalog distinguishes described records from authorization posture, and a
  work-partner website-reading turn now pins that selected skill metadata does
  not imply unrelated organizer mutation authority.
- 2026-04-24: `PRJ-623` is complete: backend `capability_catalog` now exposes
  the durable capability-record model through both `/health` and internal
  inspection. The catalog now distinguishes described role presets, described
  skill records, runtime selection surfaces, and authorization posture for
  approved tool families or operations without widening execution authority.
- 2026-04-24: `PRJ-622` is complete: canonical architecture now freezes one
  durable capability-record truth model for role presets, skill descriptions,
  and per-user tool authorization. Description, runtime selection, and
  authorization are now explicit separate concerns, and durable skill growth
  remains metadata-only rather than executable self-modification.
- 2026-04-24: `PRJ-621` is complete: runtime reality, testing guidance, ops
  notes, and planning truth now all describe the same bounded website-reading
  proof path across `/health.connectors.web_knowledge_tools.website_reading_workflow`,
  debug incident evidence, incident-evidence bundle `health_snapshot.json`, and
  bounded behavior scenarios `T14.1`, `T14.2`, and `T17.1`.
- 2026-04-24: `PRJ-620` is complete: release-smoke and incident-evidence proof
  now pin the same bounded website-reading workflow that health exposes. The
  runtime exports `connectors.web_knowledge_tools` through incident evidence,
  and release evidence now fails if website-reading guardrails drift out of
  parity with `/health`.
- 2026-04-24: `PRJ-619` is complete: `/health.connectors.web_knowledge_tools`
  and runtime `system_debug.adaptive_state["web_knowledge_tools"]` now expose
  one bounded `website_reading_workflow` contract with selected provider path,
  direct-versus-search-first readiness, bounded read semantics, and
  operator-visible blockers or next actions.
- 2026-04-24: `PRJ-618` is complete: the first live website-reading workflow
  is now frozen as an explicit no-UI `v1` product contract. The personality
  may either read a provided URL directly or search first and then inspect a
  selected page, but the workflow stays bounded to source-backed page
  summaries, read-only safety, and action-owned tool-grounded learning.
- 2026-04-24: `PRJ-634` is complete: deploy parity is now fully green on live
  production. The compose contract uses application-owned
  `${APP_BUILD_REVISION:-unknown}`, the canonical Coolify app maps
  `APP_BUILD_REVISION=$SOURCE_COMMIT` as a runtime-only variable, shadowing
  `SOURCE_COMMIT=unknown` variables were removed, and live production now
  reports a declared `runtime_build_revision` that matches local repo `HEAD`
  through release smoke.
- 2026-04-24: `PRJ-617` is complete: planning truth, ops guidance, and
  repository context now all record the same deploy-closure baseline after the
  Coolify source repair. The canonical production app must stay on the GitHub
  App source `vps-luckysparrow` and the renamed repository
  `Wroblewski-Patryk/Aviary`; `Public GitHub` on that app is now explicit
  operational drift, not an acceptable variant. The current Coolify UI path is
  project `Aviary` -> environment `production` -> application `aviary`.
- 2026-04-24: `PRJ-616` is complete: the root cause behind missing automatic
  deploys was operational source drift in Coolify, not runtime code. The
  canonical production app `jr1oehwlzl8tcn3h8gh2vvih` was corrected from
  `Public GitHub` to the GitHub App source `vps-luckysparrow`, the repository
  path was updated from `Wroblewski-Patryk/LuckySparrow` to
  `Wroblewski-Patryk/Aviary`, and local `origin` was aligned to the same
  renamed repository so repo truth and deploy-source truth match again.
- 2026-04-24: `PRJ-615` is complete: `/health.deployment`, exported incident
  evidence, repo-driven Coolify env/build args, and release smoke now expose
  one machine-visible repo-vs-production parity contract built around
  `runtime_build_revision`, `runtime_trigger_mode`, and explicit provenance
  state. Live production smoke is now failing loudly while production is still
  behind repo truth instead of silently passing without deploy-parity proof.
- 2026-04-24: `PRJ-614` is complete: one explicit final operational no-UI
  `v1` closure baseline is now frozen. Daily-use `v1` requires live production
  parity across conversation reliability, life-assistant behavior proof,
  learned-state inspection, bounded web-knowledge posture, organizer daily-use
  posture, and deploy provenance or parity. If any of those drift, the repo
  falls back to "no-UI `v1` baseline achieved in repo" instead of claiming
  final operational closure.
- 2026-04-24: `PRJ-613` is complete: fresh analysis now reframes the remaining
  work as final operational `v1` closure rather than another generic
  post-`v1` hardening wave. The next queue is seeded through `PRJ-633` and
  targets:
  - production truth and deploy-automation closure
  - live web-knowledge workflow activation
  - durable role/skill/tool-authorization catalog runtime
  - organizer-tool provider activation for daily use
  - final daily-use acceptance proof for no-UI `v1`
- 2026-04-24: the biggest remaining gap is no longer core cognition. It is the
  distance between healthy backend contracts and a production setup where the
  user can reliably talk to the personality, have it inspect bounded web
  content, and use authorized external tools in everyday life.
- 2026-04-24: architecture truth remains explicit for this lane:
  - external reads may become durable learned knowledge only through the
    existing action -> memory boundary
  - skills may evolve as metadata and guidance, but not as self-modifying
    executable tool logic
  - work-partner remains a role of the same personality, not a separate agent
    or persona
- 2026-04-24: `PRJ-609..PRJ-611` are complete: `/health.capability_catalog`,
  internal `GET /internal/state/inspect?user_id=...`, release smoke, and
  incident-evidence bundle validation now share one bounded backend
  capability-catalog contract for future UI/admin bootstrap, and the queue
  seeded through `PRJ-611` is complete.
- 2026-04-24: `PRJ-608` is complete: canonical architecture now freezes one
  bounded backend capability-catalog contract composed from existing health,
  internal-inspection, role-skill, and connector surfaces, keeping skills
  metadata-only and tools action-owned.
- 2026-04-22: product staging is now explicit:
  - `MVP` is already exceeded by the current runtime
  - `v1` means a no-UI but production-usable life assistant over Telegram or
    API
  - `v2` begins when a dedicated UI consumes stable backend inspection and
    orchestration surfaces
- 2026-04-22: work-partner is now explicitly treated as a role of the same
  personality that may use selected skills and authorized tools through the
  existing planning-to-action boundary; it is not a separate persona.
- 2026-04-22: user-reported Telegram no-response posture is now treated as the
  highest-priority blocker for making `v1` real and seeds the first group in
  the new queue.
- 2026-04-22: a new `v1` productization queue is now seeded through
  `PRJ-567`, focused on:
  - production conversation reliability
  - life-assistant workflow activation
  - learned-state and skill introspection
  - web knowledge and tooling architecture
  - bounded search, browser, and organization tool expansion
  - work-partner role orchestration
  - final `v1` release closure and `v2` backend API readiness
- 2026-04-22: `PRJ-540` is now the first `READY` task; it freezes the no-UI
  `v1` product contract and makes Telegram or API round-trip reliability a
  release-blocking baseline before broader capability work continues.
- 2026-04-22: `PRJ-540` is complete: canonical planning surfaces and
  `docs/architecture/10_future_vision.md` now align on one product
  interpretation where `v1` is backend-first and no-UI, `v2` begins with a
  dedicated UI or admin surface, and work-partner remains a role of the same
  personality rather than a separate persona.
- 2026-04-22: `PRJ-541` is now the first `READY` task; the next slice should
  repair and instrument the Telegram ingress-to-delivery path so production
  no-response incidents become machine-visible instead of log-only.
- 2026-04-22: `PRJ-541` is complete: Telegram ingress and delivery now share
  one bounded telemetry owner in `app/integrations/telegram/telemetry.py`,
  `/health.conversation_channels.telegram` exposes round-trip readiness plus
  latest ingress or delivery evidence, and wrong-secret versus missing-token
  posture is now machine-visible instead of log-only.
- 2026-04-22: `PRJ-542` is now the first `READY` task; the next slice should
  prove Telegram round-trip reliability through release smoke and
  incident-evidence coverage instead of relying only on route and delivery
  regressions.
- 2026-04-22: `PRJ-542` is complete: runtime incident evidence now requires
  Telegram conversation posture, release smoke validates
  `/health.conversation_channels.telegram` together with debug and bundle
  evidence, and behavior-validation gates now fail on missing or invalid
  Telegram conversation reliability posture.
- 2026-04-22: `PRJ-543` is now the first `READY` task; the next slice should
  synchronize the new `v1` conversation-reliability evidence across canonical
  docs, runtime reality, testing guidance, ops notes, and context truth.
- 2026-04-22: `PRJ-543` is complete: canonical logging/debugging docs, runtime
  reality, testing guidance, ops notes, planning truth, and context now all
  describe the same `v1` conversation-reliability baseline built around
  `/health.conversation_channels.telegram` and exported
  `incident_evidence.policy_posture["conversation_channels.telegram"]`.
- 2026-04-22: `PRJ-544` is now the first `READY` task; the next slice should
  freeze the exact no-UI `v1` life-assistant workflow set before expanding
  workflow execution or behavior scenarios.
- 2026-04-22: `PRJ-544` is complete: canonical product and contract docs now
  freeze one bounded no-UI `v1` workflow set built around reminder capture and
  follow-up, daily planning activation, task/goal check-ins, and
  reflection-backed continuity, while explicitly keeping full due-date or
  recurrence scheduling outside this lane.
- 2026-04-22: `PRJ-545` is now the first `READY` task; the next slice should
  wire the missing bounded execution pieces for reminder opt-in/capture and
  daily-support phrasing through the existing planning, action, task, and
  proactive boundaries.
- 2026-04-22: `PRJ-545` is complete: explicit reminder and check-in phrasing now
  persists `proactive_opt_in` through typed planning intents, action-owned
  conclusion writes, and runtime preferences, while reminder and daily-planning
  phrases create bounded task anchors (`send the release summary tomorrow`,
  `plan tomorrow`) without introducing a separate reminder subsystem.
- 2026-04-22: `PRJ-546` is now the first `READY` task; the next slice should
  prove the frozen `v1` workflow set with behavior-level scenarios for reminder
  capture, continuity, and follow-up posture across turns.
- 2026-04-22: `PRJ-546` is complete: behavior-level validation now proves that a
  no-UI `v1` assistant can capture reminder intent, persist proactive opt-in,
  add a daily-planning task anchor, and later execute a proactive follow-up
  through the scheduler path instead of only exposing correct internal payloads.
- 2026-04-22: `PRJ-547` is now the first `READY` task; the next slice should
  sync architecture, runtime reality, testing, ops, and planning/context around
  the newly proven `v1` workflow baseline and its validation evidence.
- 2026-04-22: `PRJ-547` is complete: architecture, runtime reality, testing,
  ops, and context truth now describe the same bounded no-UI `v1` workflow
  contract, including reminder capture, persisted `proactive_opt_in`, the
  `plan tomorrow` task anchor, and scenario-level proof through behavior
  validation `T13.1`.
- 2026-04-22: `PRJ-548` is now the first `READY` task; the next slice should
  freeze the learned-state introspection baseline for roles, skills, learned
  preferences, and other operator-visible growth surfaces needed before `v2`
  UI/API work.
- 2026-04-22: `PRJ-548` is complete: the canonical contract now separates
  learned knowledge, learned preferences, selected role, selected skill
  metadata, planning state, and adaptive-versus-identity ownership, while also
  freezing a truthfulness rule that `v1` may expose selected skill metadata but
  must not pretend to have self-modifying executable skill learning.
- 2026-04-22: `PRJ-549` is now the first `READY` task; the next slice should
  expose backend-owned inspection surfaces for learned state and planning state
  so future UI can read real runtime truth instead of reconstructing it
  client-side.
- 2026-04-22: `PRJ-549` is complete: `/health.learned_state` now exposes the
  shared introspection posture and `/internal/state/inspect?user_id=...`
  exposes backend-owned identity, learned knowledge, role/skill metadata, and
  planning state through the existing internal debug boundary.
- 2026-04-22: `PRJ-550` is now the first `READY` task; the next slice should
  make learned-state introspection part of regression and incident-evidence
  truth so future UI- and operator-facing surfaces are release-stable.
- 2026-04-22: `PRJ-550` is complete: runtime incident evidence now requires
  `learned_state` posture, release smoke validates the learned-state
  introspection owner plus internal inspection path from `/health`, debug
  `incident_evidence`, and incident-evidence bundles, and behavior-validation
  fixtures now fail on missing or invalid learned-state posture.
- 2026-04-22: `PRJ-551` is now the first `READY` task; the next slice should
  synchronize learned-state and skill-introspection evidence across canonical
  contracts, runtime reality, testing guidance, ops notes, and planning or
  context truth.
- 2026-04-22: `PRJ-551` is complete: canonical contracts, logging/debugging
  guidance, runtime reality, testing guidance, ops notes, planning, and
  context truth now all describe the same learned-state inspection baseline
  built around `/health.learned_state`, internal
  `GET /internal/state/inspect?user_id=...`, and exported
  `incident_evidence.policy_posture["learned_state"]`.
- 2026-04-22: `PRJ-552` is now the first `READY` task; the next slice should
  freeze the architecture baseline for web-search and browser tool families
  before any provider-backed search or browsing adapter is added.
- 2026-04-22: `PRJ-552` is complete: web search and browser access are now
  frozen as action-owned external capability kinds under the same planning,
  permission-gate, and action validation boundary as existing connectors;
  they are explicitly not self-executing skills or a second browsing
  subsystem outside the action layer.
- 2026-04-22: `PRJ-553` is now the first `READY` task; the next slice should
  implement one shared capability and permission-gate owner for web knowledge
  tools before health visibility or provider-backed slices are widened.
- 2026-04-22: `PRJ-553` is complete: shared typed intents now model
  `knowledge_search` and `web_browser` under the same action-owned
  permission-gate path as existing external capability families, planner emits
  bounded search/browser intents through the shared connector policy owner,
  and action now blocks mode drift for those intents before any delivery path
  continues.
- 2026-04-22: `PRJ-554` is now the first `READY` task; the next slice should
  expose health and runtime-debug visibility for the selected web-knowledge
  tool-family posture before any provider-backed search or browser execution
  is introduced.
- 2026-04-22: `PRJ-554` is complete: `/health.connectors` now exposes one
  shared web-knowledge posture snapshot plus explicit policy-only execution
  baseline entries for `knowledge_search` and `web_browser`, and runtime
  `system_debug.adaptive_state` mirrors the same readiness, fallback, and
  non-live provider posture for operator or future-UI inspection.
- 2026-04-22: `PRJ-555` is now the first `READY` task; the next slice should
  synchronize contracts, runtime reality, testing guidance, ops notes, and
  planning/context truth around the new web-knowledge tooling baseline.
- 2026-04-22: `PRJ-555` is complete: contracts, runtime reality, testing
  guidance, ops notes, planning, and context truth now describe the same
  action-owned but still-policy-only web-knowledge tooling baseline built
  around `/health.connectors.web_knowledge_tools`,
  `/health.connectors.execution_baseline`, and runtime
  `system_debug.adaptive_state["web_knowledge_tools"]`.
- 2026-04-22: `PRJ-556` is now the first `READY` task; the next slice should
  freeze the first bounded provider-backed search, browser, and organization
  operations before live execution paths are introduced.
- 2026-04-22: `PRJ-556` is complete: the first provider-backed expansion set
  is now frozen as `knowledge_search:search_web` via `duckduckgo_html`,
  `web_browser:read_page` via `generic_http`, and `task_system:update_task`
  via ClickUp, all with explicit bounded evidence contracts.
- 2026-04-22: `PRJ-557` is now the first `READY` task; the next slice should
  implement those bounded search, browser, and ClickUp operations through the
  existing planning-to-action boundary.
- 2026-04-22: `PRJ-557` is complete: planner now emits the frozen bounded
  provider-backed slice set, action executes it through dedicated DuckDuckGo,
  generic HTTP, and ClickUp adapters, and `/health.connectors` plus runtime
  `system_debug.adaptive_state["web_knowledge_tools"]` now expose these paths
  as live first-slice execution instead of policy-only placeholders.
- 2026-04-22: `PRJ-558` is now the first `READY` task; the next slice should
  prove that these new tool paths stay role-governed and bounded through
  behavior-level validation instead of relying only on unit and integration
  regressions.
- 2026-04-22: `PRJ-558` is complete: behavior-validation now proves that
  analyst turns can use bounded DuckDuckGo search and generic HTTP page reads,
  while executor-aligned organization turns can update ClickUp tasks through
  the existing permission-gate and action boundary instead of bypassing role,
  planning, or connector guardrails.
- 2026-04-22: `PRJ-559` is now the first `READY` task; the next slice should
  synchronize contracts, runtime reality, testing guidance, ops notes, and
  planning/context truth around the approved bounded search, browser, and
  organization tool slices plus their new behavior-level proof.
- 2026-04-22: `PRJ-559` is complete: canonical contracts, behavior-testing
  guidance, runtime reality, ops notes, and planning/context truth now all
  describe the same live bounded tool slices and point to behavior-validation
  proof through `T14.1..T14.3` instead of describing search/browser as
  policy-only placeholders.
- 2026-04-23: `PRJ-570` is complete: repository-driven Coolify production now
  uses `pgvector/pgvector:pg15`, forced deploy
  `ihgdzv1gug3ketq0u7sm3n2s` finished on commit `e41772e`, public `/health`
  returned `200`, Telegram round-trip telemetry recorded a successful ingress
  and delivery after the repair, and the post-deploy migration hook was
  normalized to `python -m alembic upgrade head`.
- 2026-04-23: `PRJ-571` is complete: the next seeded queue now comes from live
  production gaps instead of synthetic backlog generation. The next active lane
  is post-`v1` production hardening:
  - externalize reflection queue ownership in production
  - externalize maintenance and proactive cadence ownership in production
  - sync docs and release evidence once those owner cutovers are real
- 2026-04-23: `PRJ-572` is complete: repository-driven Coolify production now
  defaults `REFLECTION_RUNTIME_MODE` to `deferred`, forced deploy
  `nlcp1kpmxxhvq094fssz7qfk` finished on commit `13d8972`, and production
  `/health.reflection.external_driver_policy` now reports
  `selected_runtime_mode=deferred` with `production_baseline_ready=true` while
  Telegram/API foreground turn handling remained healthy through the cutover.
- 2026-04-23: `PRJ-573` is complete: repository-driven Coolify production now
  defaults `SCHEDULER_EXECUTION_MODE` to `externalized`, forced deploy
  `m8jd7i3sqiv8f8fuvlo367ki` finished on commit `2a4a573`, production
  `/health.scheduler.external_owner_policy` now reports
  `selected_execution_mode=externalized`, `cutover_proof_ready=true`, and
  `production_baseline_ready=true`, and Telegram/API foreground turn handling
  remained healthy through the cutover.
- 2026-04-23: `PRJ-574` is complete: runtime reality, testing guidance,
  planning docs, runbook truth, and context now all describe the same
  externalized post-v1 production-hardening baseline, and the queue seeded by
  `PRJ-571` is complete through `PRJ-574`.
- 2026-04-23: after `PRJ-574`, no seeded `READY` slice remains in the
  post-v1 production-hardening lane; the next task should come from a fresh
  runtime or product-gap analysis.
- 2026-04-23: `PRJ-575` is complete: fresh architecture-gap analysis now
  compares canonical docs, runtime reality, and live production `/health`
  instead of relying on historical backlog residue.
- 2026-04-23: the next queue is now seeded through `PRJ-595` and is ordered
  around the clearest remaining architecture-to-production gaps:
  - durable attention production cutover
  - proactive opt-in production activation
  - retrieval provider baseline alignment
  - richer backend introspection of learned personality growth
  - production organizer-tool readiness for ClickUp, Calendar, and Drive
- 2026-04-23: `PRJ-576` is now the first `READY` task; it freezes the durable
  attention production cutover gate before any production switch, because live
  `/health.attention` still reports `coordination_mode=in_process` despite
  durable-inbox readiness already being green.
- 2026-04-23: `PRJ-576` is complete: durable attention now has one explicit
  production cutover gate with target owner `durable_inbox`, required proof
  surfaces (`/health.attention`, `/health.runtime_topology`,
  `/health.conversation_channels.telegram`, release smoke), and rollback
  posture back to `ATTENTION_COORDINATION_MODE=in_process`.
- 2026-04-23: `PRJ-577` is complete: repository-driven Coolify production now
  runs `ATTENTION_COORDINATION_MODE=durable_inbox`; deployment
  `amz31iyapwr3t9z9tanpe2jb` imported commit `d3707a0`, public `/health`
  reports `attention.coordination_mode=durable_inbox`,
  `attention.contract_store_mode=repository_backed`, and Telegram round-trip
  remained healthy through the cutover and release smoke.
- 2026-04-23: `PRJ-578` is now the first `READY` task; the next slice should
  convert the live durable-attention cutover into release-smoke,
  incident-evidence, and behavior-validation proof before broader docs sync in
  `PRJ-579`.
- 2026-04-23: `PRJ-578` is complete: release smoke, exported
  `incident_evidence`, incident-evidence bundles, and CI behavior validation
  now all require the durable-attention owner posture and
  `runtime_topology.attention_switch` proof, while a behavior-level durable
  burst-coalescing regression replaces manual operator inspection for this
  seam.
- 2026-04-23: `PRJ-579` is now the first `READY` task; the next slice should
  synchronize architecture, runtime reality, testing guidance, ops notes, and
  planning/context truth around the live durable-attention production baseline
  and its new proof surfaces.
- 2026-04-23: `PRJ-579` is complete: canonical contracts, runtime reality,
  testing guidance, ops notes, planning truth, and repository context now all
  describe the same live durable-attention production baseline and the same
  proof path through public `/health`, exported `incident_evidence`, release
  smoke, and behavior validation.
- 2026-04-23: `PRJ-580` is now the first `READY` task; the next slice should
  freeze one explicit production policy for bounded proactive follow-up before
  any runtime activation or release-evidence widening happens.
- 2026-04-23: `PRJ-580` is complete: production proactive is now frozen as
  bounded opt-in follow-up under external scheduler ownership, with the
  existing Telegram delivery target, current anti-spam thresholds, and one
  explicit rollback path back to `PROACTIVE_ENABLED=false`.
- 2026-04-23: `PRJ-581` is now the first `READY` task; the next slice should
  implement that bounded proactive policy in runtime and production deployment
  so `/health.proactive` stops reporting `disabled_by_policy`.
- 2026-04-23: `PRJ-581` is complete: repository-driven Coolify production now
  runs with the bounded proactive baseline enabled, live `/health.proactive`
  reports `enabled=true` and
  `production_baseline_state=external_scheduler_target_owner`, and the cutover
  also confirmed that an explicit Coolify env override can silently mask a
  repo-driven compose default.
- 2026-04-23: `PRJ-582` is complete: exported `incident_evidence`,
  incident-evidence bundle checks, release smoke, and CI behavior-validation
  gates now require the same proactive policy owner and enabled production
  baseline that `/health.proactive` exposes.
- 2026-04-23: `PRJ-583` is complete: runtime reality, testing guidance, ops
  notes, planning docs, and repository context now all describe the same live
  bounded proactive production baseline and its proof path.
- 2026-04-23: `PRJ-584` is now the first `READY` task; the next slice should
  freeze the production retrieval-provider baseline and its enforcement
  posture before any provider-alignment runtime changes proceed.
- 2026-04-23: `PRJ-584` is complete: production retrieval keeps
  `openai_api_embeddings` as the steady-state target baseline,
  `local_hybrid` remains transition-only, deterministic remains compatibility
  fallback, and provider/model/source-rollout enforcement stays `warn` until
  live runtime alignment lands in `PRJ-585`.
- 2026-04-23: `PRJ-585` is complete: repository-driven Coolify production now
  requests `EMBEDDING_PROVIDER=openai` and
  `EMBEDDING_MODEL=text-embedding-3-small` by default, and live
  `/health.memory_retrieval` reports requested/effective `openai`,
  `provider_owned_openai_api`, `aligned_openai_provider_owned`,
  `aligned_target_provider`, and no pending lifecycle gaps.
- 2026-04-23: `PRJ-586` is complete: release smoke, exported
  `incident_evidence`, incident-evidence bundles, and CI behavior validation
  now fail on retrieval-provider drift instead of leaving retrieval alignment
  as health-only operator evidence.
- 2026-04-23: `PRJ-587` is complete: runtime reality, testing guidance, ops
  notes, planning docs, and repository context now all describe the same
  aligned OpenAI retrieval-provider production baseline and strict evidence
  path.
- 2026-04-23: `PRJ-588` is complete: the repo now records one bounded backend
  contract for personality-growth introspection covering learned knowledge,
  learned preferences, role/skill metadata, reflection-backed summaries, and
  planning continuity, while explicitly rejecting self-modifying executable
  skill learning.
- 2026-04-23: `PRJ-589` is complete: `/health.learned_state` now exposes the
  richer bounded inspection contract, and
  `GET /internal/state/inspect?user_id=...` now returns backend-owned
  preference, learned-knowledge, role/skill visibility, and planning
  continuity summaries for future UI or admin inspection.
- 2026-04-23: `PRJ-590` is complete: release smoke, incident-evidence bundle
  validation, and targeted smoke regressions now require the richer
  learned-state section contract instead of only owner/path posture.
- 2026-04-23: `PRJ-591` is complete: canonical contracts, runtime reality,
  testing guidance, ops notes, planning docs, and context truth now describe
  the same richer learned-state and personality-growth inspection baseline.
- 2026-04-23: `PRJ-592` is complete: the first production organizer-tool stack
  is now frozen as ClickUp `create_task/list_tasks/update_task`, Google
  Calendar `read_availability`, and Google Drive `list_files`, with the
  existing opt-in and confirmation boundaries preserved.
- 2026-04-23: `PRJ-593` is complete: `/health.connectors.organizer_tool_stack`
  now exposes one shared acceptance snapshot for the frozen organizer-tool
  stack, covering approved operations, credential gaps, opt-in requirements,
  and confirmation boundaries.
- 2026-04-24: `PRJ-594` is complete: release smoke, incident evidence,
  incident-evidence bundles, and runtime behavior scenarios now prove the same
  organizer-tool posture that `/health.connectors.organizer_tool_stack`
  exposes, including `T16.1..T16.3` for ClickUp list, Google Calendar
  availability, and Google Drive metadata reads under work-partner selection.
- 2026-04-24: `PRJ-595` is complete: canonical contracts, runtime reality,
  testing guidance, runbook notes, planning docs, and repository context now
  describe the same first production organizer-tool baseline and its proof
  path.
- 2026-04-24: the queue seeded through `PRJ-595` is now complete; no seeded
  organizer-tool follow-up remains until the next fresh architecture or
  product gap analysis.
- 2026-04-24: `PRJ-596` is complete: fresh production/runtime analysis now
  seeds the next queue through `PRJ-611`, focused on the next blockers between
  a healthy no-UI `v1` runtime and a production-ready external-tool learning
  baseline.
- 2026-04-24: the next queue is intentionally ordered around four live gaps:
  - Coolify deployment automation reliability
  - organizer-tool credential activation in production
  - bounded tool-grounded learning capture for external reads
  - one clearer backend capability catalog for future UI/admin work
- 2026-04-24: `PRJ-597` is now the first `READY` task; the next slice should
  freeze the repo-driven Coolify deployment-automation baseline before deeper
  provider activation and tool-grounded learning work assumes automatic deploy
  behavior.
- 2026-04-24: `PRJ-597` is complete: repo-driven Coolify deployment
  automation now has one explicit baseline with the canonical app identity,
  intended primary automation path, bounded webhook/UI fallback path, and
  operator proof surfaces.
- 2026-04-24: `PRJ-598` is complete: `/health.deployment`, deploy webhook
  evidence, exported incident evidence, and release smoke now describe one
  shared deployment-automation provenance contract, including the canonical
  Coolify app identity and explicit `source_automation` versus
  `webhook_manual_fallback|ui_manual_fallback` trigger posture.
- 2026-04-24: `PRJ-599` is complete: runbook, planning docs, repository
  context, and task records now describe the same deployment-provenance
  baseline and explicitly note that release smoke should fail fast on older
  production until the new contract is deployed.
- 2026-04-24: `PRJ-600` is complete: canonical contracts, env/config guidance,
  runbook notes, planning docs, and repository context now freeze one explicit
  production credential-activation baseline for the first organizer-tool stack
  across ClickUp, Google Calendar, and Google Drive.
- 2026-04-24: `PRJ-612` is complete: canonical architecture now allows durable
  role presets with prompt-oriented definitions, durable skill descriptions
  with evolving usage guidance, and per-user tool authorization records for
  future UI/admin activation, while keeping raw secrets externalized and tool
  execution inside the existing planning -> permission-gate -> action
  boundary.
- 2026-04-24: `PRJ-601` is complete: `/health.connectors.organizer_tool_stack`
  now exposes one actionable activation snapshot with provider-specific
  required settings, missing settings, opt-in/confirmation posture, and next
  actions for the frozen organizer-tool stack.
- 2026-04-24: `PRJ-602` is complete: release smoke, incident evidence, and
  incident-evidence bundles now validate the same organizer-tool
  `activation_snapshot` contract and next-action posture exposed through
  `/health.connectors.organizer_tool_stack`.
- 2026-04-24: `PRJ-603` is complete: runtime reality, testing guidance, ops
  notes, planning truth, and repository context now describe the same richer
  organizer-tool activation snapshot and provider-specific next-action
  posture.
- 2026-04-24: `PRJ-604` is complete: canonical architecture now freezes one
  bounded tool-grounded learning contract where approved external reads may
  become durable learned knowledge only through action-owned summaries and
  memory-owned persistence.
- 2026-04-24: `PRJ-605` is complete: approved external reads now persist
  bounded tool-grounded semantic conclusions and learned-state inspection
  exposes the richer tool-grounded knowledge summaries.
- 2026-04-24: `PRJ-606` is complete: behavior validation, release smoke,
  incident evidence, and `v1_readiness` now prove the same bounded
  tool-grounded learning contract through `T17.1..T17.2` and
  learned-state contract gates.
- 2026-04-24: `PRJ-607` is complete: runtime reality, testing guidance, ops
  notes, architecture testing docs, and planning/context truth now describe
  the same bounded tool-grounded learning baseline and evidence path.
- 2026-04-24: `PRJ-608` is now the first `READY` task; the next slice should
  freeze one backend capability-catalog contract for future UI/admin work now
  that deploy automation, organizer activation, and tool-grounded learning are
  all machine-visible.
- 2026-04-22: `PRJ-560` is now the first `READY` task; the next slice should
  freeze the backend work-partner role baseline so future orchestration can
  grow from one explicit role contract instead of diffuse product wording.
- 2026-04-22: `PRJ-560` is complete: canonical product and contract docs now
  freeze `work_partner` as a role of the same personality, bounded to
  metadata-only skills plus already approved tools under the existing
  planning, permission-gate, and action boundary.
- 2026-04-22: `PRJ-561` is now the first `READY` task; the next slice should
  make that work-partner baseline machine-visible in role selection, selected
  skills, planning outputs, and backend inspection surfaces.
- 2026-04-22: `PRJ-561` is complete: explicit `work_partner` orchestration
  turns now select a shared backend role, carry a bounded work-partner skill
  mix, surface a machine-visible role-skill policy baseline, and can
  orchestrate approved search plus ClickUp tool paths through the existing
  typed-intent and action boundary.
- 2026-04-22: `PRJ-562` is now the first `READY` task; the next slice should
  prove work-partner behavior through work-organization and decision-support
  scenarios in the shared behavior-validation gate.
- 2026-04-22: `PRJ-562` is complete: behavior validation now proves
  work-partner organization and decision-support scenarios through `T15.1`
  and `T15.2`, keeping search, browser, and ClickUp usage inside the existing
  role, planning, permission-gate, and action boundary.
- 2026-04-22: `PRJ-563` is now the first `READY` task; the next slice should
  synchronize contracts, runtime reality, ops notes, testing guidance, and
  planning/context truth around the new backend work-partner baseline.
- 2026-04-22: `PRJ-563` is complete: canonical contracts, runtime reality,
  behavior-testing guidance, ops notes, and planning/context truth now all
  describe the same backend work-partner baseline and its scenario-level
  proof through `T15.1..T15.2`.
- 2026-04-22: `PRJ-564` is now the first `READY` task; the next slice should
  freeze one explicit no-UI `v1` release gate and operator acceptance bundle
  before more UI-readiness work lands.
- 2026-04-22: `PRJ-564` is complete: one explicit no-UI `v1` release gate is
  now frozen across conversation reliability, life-assistant behavior proof,
  learned-state inspection readiness, and approved tooling plus work-partner
  posture.
- 2026-04-22: `PRJ-565` is now the first `READY` task; the next slice should
  make that release gate machine-visible through `/health`, incident evidence,
  release smoke, and behavior-validation tooling.
- 2026-04-22: `PRJ-565` is complete: `/health.v1_readiness` now exposes one
  shared backend release-gate owner, exported incident evidence mirrors the
  same posture, and both release smoke and behavior-validation incident
  evidence checks now require that surface.
- 2026-04-22: `PRJ-566` is now the first `READY` task; the next slice should
  leave behind one stable backend API-readiness contract for future `v2` UI
  callers.
- 2026-04-22: `PRJ-566` is complete: `/health.api_readiness` now exposes one
  shared backend-readiness contract for future `v2` UI callers, and internal
  `GET /internal/state/inspect?user_id=...` carries the same snapshot so UI
  bootstrap can read learned-state, planning-state, role-skill, and
  current-turn-debug surface contracts from one backend-owned source.
- 2026-04-22: `PRJ-567` is now the first `READY` task; the final slice should
  synchronize architecture notes, runtime reality, testing guidance, ops
  notes, planning, and context around the completed no-UI `v1` baseline plus
  the new backend API-readiness contract for later `v2` UI work.
- 2026-04-22: `PRJ-567` is complete: canonical architecture docs, runtime
  reality, testing guidance, ops notes, planning, and context now all
  describe the same completed no-UI `v1` baseline plus the backend API
  readiness seed for future `v2` UI work.
- 2026-04-23: `PRJ-568` is complete: app startup now wires
  `AttentionTurnCoordinator` to the shared `MemoryRepository`, so
  `ATTENTION_COORDINATION_MODE=durable_inbox` no longer boots without the
  repository-backed contract store dependency.
- 2026-04-23: `PRJ-569` is complete: PostgreSQL semantic-vector runtime now
  treats the Python `pgvector` binding as a required deploy dependency and
  blocks startup before database initialization when semantic vectors are
  enabled on PostgreSQL without that dependency, preventing the broken
  `/health`-looks-healthy but `/event`-returns-500 posture seen in production.
- 2026-04-22: the seeded `v1` queue is complete through `PRJ-567`; no seeded
  `READY` task remains and the next lane should be derived from fresh
  production/runtime analysis.
- 2026-04-23: user-reported production Telegram silence is now being triaged as
  `PRJ-568`; the strongest candidate root cause is startup wiring drift for
  `ATTENTION_COORDINATION_MODE=durable_inbox`, where the main-app attention
  coordinator was instantiated without the shared memory repository even though
  route-level tests used repository-backed durable inbox state.
- 2026-04-23: `PRJ-568` is complete: app lifespan now wires the shared
  `memory_repository` into `AttentionTurnCoordinator`, and a lifespan-level
  regression guards the repository-backed `durable_inbox` startup path that
  was previously untested.
- 2026-04-22: fresh post-`PRJ-515` analysis has now seeded a new queue through
  `PRJ-539`, focused on operator-grade incident-evidence handling, actual
  debug-compat retirement, bounded connector read expansion, external cadence
  cutover proof, and the remaining relation-source retrieval decision.
- 2026-04-22: `PRJ-516` is now the first `READY` task; it freezes the
  operator-facing incident-evidence bundle and retention baseline before any
  further runtime cutover work depends on ad hoc debug JSON capture.
- 2026-04-22: `PRJ-516` is complete: architecture, runtime reality, and ops
  guidance now freeze one operator-facing incident-evidence bundle contract
  (`manifest.json`, `incident_evidence.json`, `health_snapshot.json`, optional
  `behavior_validation_report.json`) plus naming and retention posture.
- 2026-04-22: `PRJ-517` is now the first `READY` task; the next slice should
  implement a canonical helper or export path for collecting that bundle
  without changing ownership of `incident_evidence` or `/health`.
- 2026-04-22: `PRJ-517` is complete: the repo now exposes a canonical bundle
  helper at `scripts/export_incident_evidence_bundle.py`, and
  `/health.observability` advertises bundle-helper availability plus the
  helper entrypoint through the shared observability owner.
- 2026-04-22: `PRJ-518` is now the first `READY` task; the next slice should
  pin bundle integrity and failure posture in smoke and regression coverage.
- 2026-04-22: `PRJ-518` is complete: release smoke now supports
  `-IncidentEvidenceBundlePath` and validates full bundle integrity, while
  regression coverage pins both the valid bundle path and partial-bundle
  failure posture.
- 2026-04-22: `PRJ-519` is now the first `READY` task; the next slice should
  synchronize the new helper and smoke behavior across canonical docs,
  runtime reality, ops guidance, and planning/context truth.
- 2026-04-22: `PRJ-519` is complete: canonical docs, runtime reality, testing
  guidance, ops guidance, and context truth now describe the same
  incident-evidence bundle helper, bundle file set, and release-smoke
  verification path.
- 2026-04-22: `PRJ-520` is complete: shared debug retirement now has one
  explicit owner-level checklist and cutover posture, and
  `/health.runtime_policy` exposes retirement target, cutover posture, gate
  checklist, and gate state in addition to the existing blocker list.
- 2026-04-22: `PRJ-521` is complete: dedicated-admin debug ingress is now the
  default posture across environments, shared `/event/debug` defaults to
  break-glass-only, and query compat `POST /event?debug=true` is now
  disabled-by-default unless explicitly re-enabled.
- 2026-04-22: `PRJ-522` is complete: release smoke now validates
  dedicated-admin-only debug posture from both live `incident_evidence` and
  bundle-attached `incident_evidence.json`, while behavior-validation gates
  now fail on incident-evidence debug posture drift or missing explicit
  rollback-exception state.
- 2026-04-22: `PRJ-523` is complete: canonical docs, runtime reality, testing
  guidance, ops notes, and context truth now all describe dedicated-admin
  debug retirement proof through incident-evidence posture as well as
  `/health.runtime_policy`.
- 2026-04-22: `PRJ-524` is complete: the first bounded calendar live-read
  contract is now frozen as `calendar:read_availability` with
  `provider_hint=google_calendar`, read-only opt-in posture, and an
  action-owned safe output shape limited to normalized availability evidence.
- 2026-04-22: `PRJ-525` is complete: planner now emits
  `calendar:read_availability` with `provider_hint=google_calendar`, and
  action executes that typed read intent through a dedicated bounded Google
  Calendar availability adapter that returns normalized window evidence,
  busy-window count, and free-slot preview without raw calendar event
  payloads.
- 2026-04-22: `PRJ-526` is complete: `/health.connectors.execution_baseline`
  now exposes `calendar.google_calendar_read_availability` with one shared
  `provider_backed_when_configured` contract and machine-visible
  `credentials_missing|provider_backed_ready` posture for the bounded calendar
  live-read path.
- 2026-04-22: `PRJ-527` is complete: canonical contracts, runtime reality,
  testing guidance, ops notes, and context truth now describe the same bounded
  Google Calendar live-read baseline plus `/health.connectors.execution_baseline`
  readiness posture.
- 2026-04-22: `PRJ-528` is complete: the first bounded cloud-drive metadata
  live-read slice is now frozen as `cloud_drive:list_files` with
  `provider_hint=google_drive`, and its safe output boundary is limited to
  file metadata evidence rather than document content or write semantics.
- 2026-04-22: `PRJ-529` is complete: planner now emits
  `cloud_drive:list_files` with `provider_hint=google_drive`, and action
  executes that typed read intent through a dedicated bounded Google Drive
  metadata adapter that returns file metadata previews without exposing
  document bodies, downloads, or write semantics.
- 2026-04-22: `PRJ-530` is complete: `/health.connectors.execution_baseline`
  now exposes `cloud_drive.google_drive_list_files` with one shared
  `provider_backed_when_configured` contract and machine-visible
  `credentials_missing|provider_backed_ready` posture for the bounded
  cloud-drive metadata-read path.
- 2026-04-22: `PRJ-531` is complete: canonical contracts, runtime reality,
  testing guidance, ops notes, and context truth now describe the same
  bounded Google Drive metadata-read baseline plus its
  `cloud_drive.google_drive_list_files` health posture.
- 2026-04-22: `PRJ-532` is complete: canonical contracts now freeze one
  external cadence cutover-proof baseline, and runtime reality plus ops
  guidance now explicitly treat `/health.scheduler.external_owner_policy` as
  target-policy truth until recent last-run and duplicate-protection evidence
  becomes machine-visible.
- 2026-04-22: `PRJ-533` is complete:
  `/health.scheduler.external_owner_policy` now exposes maintenance and
  proactive external run evidence, bounded duplicate-protection posture, and
  `cutover_proof_ready` so proven cutover is distinct from target-mode
  selection.
- 2026-04-22: `PRJ-534` is complete: release smoke and behavior-validation
  gate logic now validate the external cadence cutover proof surface, so
  missing proof owner, invalid evidence states, and incomplete duplicate-
  protection posture are caught as explicit failures.
- 2026-04-22: `PRJ-535` is complete: runtime reality, testing guidance, ops
  notes, and context truth now describe the same external cadence cutover
  proof surface and the distinction between target owner selection and proven
  cutover readiness.
- 2026-04-22: `PRJ-536` is complete: semantic+affective are now frozen as the
  steady-state retrieval completion baseline, while relation embeddings remain
  an explicit optional follow-on family and relation records stay live
  adaptive inputs outside that completion condition.
- 2026-04-22: `PRJ-537` is complete: retrieval code and
  `/health.memory_retrieval` now treat semantic+affective as the foreground
  rollout-completion baseline, while relation has one explicit optional-family
  policy surface (`relation_source_retrieval_policy`) with state, hint,
  recommendation, and enabled/alignment visibility.
- 2026-04-22: `PRJ-538` is complete: runtime `system_debug.adaptive_state` now
  exposes the same shared relation-source posture as `/health`, while release
  smoke and focused regressions require relation-source policy owner/state/
  enabled evidence instead of treating it as an undocumented optional field.
- 2026-04-22: `PRJ-539` is complete: architecture, runtime reality, runtime
  behavior testing, ops guidance, testing guidance, and context truth now all
  describe the same optional-family relation-source posture and its `/health`,
  `system_debug`, plus release-smoke evidence surfaces.
- 2026-04-22: Group 81 (`PRJ-536..PRJ-539`) is complete, and there are no
  remaining seeded `READY` tasks in the current planning queue.
- 2026-04-22: Group 76 (`PRJ-516..PRJ-519`) is now complete, and the next
  `READY` task is `PRJ-520` for dedicated debug-ingress compatibility
  retirement.

## Product Decisions (Confirmed)

- 2026-04-16: this repo uses a project-specific agent workflow adapted to the
  Python, FastAPI, and AION stack.
- 2026-04-16: reflection is treated as a real app-local durable worker concern,
  not as a purely hypothetical future subsystem.
- 2026-04-17: `POST /event` exposes the smaller public response by default and
  the full internal runtime result only through `debug=true`.
- 2026-04-17: episodic memory persists both typed JSON payloads and a
  human-readable summary, with payload-first readers and legacy fallback.
- 2026-04-17: motivation uses only the documented shared mode set
  (`respond|ignore|analyze|execute|clarify`).
- 2026-04-18: runtime stages emit structured `start/success/failure` logs with
  `event_id`, `trace_id`, stage name, duration, and short summaries through the
  shared scaffold in `app/core/logging.py`.
- 2026-04-18: goal/task selection and progress-history signal logic now has
  shared utility owners in `app/utils/goal_task_selection.py` and
  `app/utils/progress_signals.py`, and runtime heuristics consume those helpers
  across context, planning, motivation, and reflection.
- 2026-04-18: event normalization now enforces an explicit API boundary
  (`source=api`, `subsource=event_endpoint`, normalized `payload.text`) and
  keeps debug details behind the explicit debug response path.
- 2026-04-18: startup schema ownership now defaults to migration-first behavior,
  while `create_tables()` remains only as an explicit compatibility mode.
- 2026-04-18: runtime now passes an explicit `ActionDelivery` contract from
  expression into action, keeping side effects inside action while reducing
  implicit stage coupling.
- 2026-04-18: action delivery now routes through an integration-level
  dispatcher (`DeliveryRouter`) so channel dispatch logic is owned by
  integrations while the action boundary remains explicit.
- 2026-04-19: startup now emits an explicit production warning when
  `EVENT_DEBUG_ENABLED=true`, so debug payload exposure policy is visible in
  logs before serving requests.
- 2026-04-19: debug payload exposure now uses environment-aware defaults:
  enabled by default in non-production, disabled by default in production
  unless explicitly enabled.
- 2026-04-19: production runtime policy checks now support explicit enforcement
  mode (`warn|strict`), so policy mismatches can be warning-only or fail-fast
  on startup.
- 2026-04-19: startup strict-policy fail-fast behavior is now pinned with a
  lifespan-level regression test that verifies block-before-database-init.
- 2026-04-19: startup strict-policy fail-fast lifecycle coverage now spans both
  mismatch families (debug exposure and schema compatibility mode).
- 2026-04-19: runtime policy mismatch detection now has a shared owner reused by
  startup and `/health`, and health now exposes a mismatch preview list for
  operator triage.
- 2026-04-19: runtime policy now exposes strict-rollout readiness signals
  (`production_policy_mismatch_count`, `strict_startup_blocked`,
  `strict_rollout_ready`) through shared helpers reused by startup and `/health`.
- 2026-04-19: runtime policy now also exposes strict-rollout recommendation
  signals (`recommended_production_policy_enforcement`, `strict_rollout_hint`),
  and startup emits an informational hint when production warn mode is strict-ready.
- 2026-04-19: debug payload access now supports optional token gating via
  `EVENT_DEBUG_TOKEN`, with policy visibility and startup warnings aligned.
- 2026-04-19: API event normalization now supports `X-AION-User-Id` fallback
  (when `meta.user_id` is missing), making user-scoped language/profile memory
  handling safer for multi-user API traffic.
- 2026-04-21: runtime now has a shared `identity_policy` owner for profile
  language continuity versus conclusion-owned learned preferences, and the
  same baseline is exposed through `/health.identity` and runtime
  `system_debug.adaptive_state.identity_policy`.
- 2026-04-21: language continuity now also has explicit operator/debug
  posture: `/health.identity.language_continuity` exposes the baseline
  precedence and supported codes, while runtime
  `system_debug.adaptive_state.language_continuity` exposes selected source,
  candidate continuity inputs, and fallback posture for the current event.
- 2026-04-19: runtime now carries a first-class affective contract slot
  (`affect_label`, `intensity`, `needs_support`, `confidence`, `source`,
  `evidence`) populated by deterministic perception placeholders.
- 2026-04-19: runtime now includes an AI-assisted affective assessor stage with
  deterministic fallback, so affective source can be traced as
  `ai_classifier` or `fallback` in stage-level runtime logs.
- 2026-04-19: motivation, role, and expression now consume
  `perception.affective` as the primary support/emotion signal, making
  supportive behavior traceable to one affective owner across runtime stages.
- 2026-04-19: empathy-oriented regression fixtures now pin emotionally heavy,
  ambiguous, and mixed-intent support quality across motivation, expression,
  and runtime integration tests.
- 2026-04-19: conclusions now support scoped storage
  (`scope_type=global|goal|task`, `scope_key`) and reflection writes
  goal-operational conclusions with goal scope, enabling scope-aware repository
  queries.
- 2026-04-19: runtime memory consumers now resolve scoped reflection state by
  primary active goal with global fallback, reducing cross-goal leakage across
  context, motivation, planning, and milestone enrichment.
- 2026-04-19: episodic payloads now persist lightweight affective tags and
  reflection derives reusable affective conclusions
  (`affective_support_pattern`, `affective_support_sensitivity`) consumed by
  runtime preferences, context summaries, and motivation scoring.
- 2026-04-19: runtime memory retrieval now loads deeper context
  (`MEMORY_LOAD_LIMIT=12`) and ranks memory candidates with affective relevance
  in addition to language, layer mode, topical overlap, and importance.
- 2026-04-19: repository and docs now share explicit memory-layer vocabulary
  (`episodic`, `semantic`, `affective`, `operational`) with layer-aware
  repository APIs for episodic retrieval, conclusion filtering, and operational
  memory reads.
- 2026-04-19: planning now emits explicit typed `domain_intents`
  (`upsert_goal`, `upsert_task`, `update_task_status`,
  `update_response_style`, `update_collaboration_preference`, `noop`), and
  action now executes only those intents for durable domain writes.
- 2026-04-19: reflection logic is now split into concern-owned modules
  (`goal_conclusions`, `adaptive_signals`, `affective_signals`), keeping
  worker orchestration separate from inference ownership.
- 2026-04-19: adaptive reflection signals (`preferred_role`, `theta`,
  collaboration fallback) now require outcome evidence and user-visible cues,
  reducing self-reinforcement loops from role-only traces.
- 2026-04-20: canonical adaptive influence governance policy is now explicit in
  architecture contracts, including evidence thresholds, precedence, and
  tie-break boundaries for affective, relation, preference, and theta signals.
- 2026-04-19: milestone pressure heuristics now prefer phase consistency and
  arc/transition evidence over pure time-window drift.
- 2026-04-19: runtime now exposes an explicit graph migration boundary through
  `GraphRuntimeState` contracts, runtime-result conversion helpers, and
  graph-compatible stage adapters around current foreground modules.
- 2026-04-19: foreground stage orchestration (`perception -> ... -> action`)
  now runs through LangGraph `StateGraph` nodes while preserving stage-level
  contracts, logs, and existing runtime/API behavior.
- 2026-04-19: documentation now explicitly separates canonical architecture in
  `docs/architecture/` from transitional implementation reality in
  `docs/implementation/runtime-reality.md`, so human-oriented design intent can
  stay stable while runtime details remain searchable.
- 2026-04-19: OpenAI prompt construction now supports optional LangChain
  templates through a compatibility wrapper while preserving non-LangChain
  fallback behavior.
- 2026-04-19: semantic retrieval contracts and storage are now explicit:
  embedding/retrieval contract types, pgvector-ready schema scaffolding, and
  deterministic embedding fallback helpers are all first-class runtime surfaces.
- 2026-04-19: runtime memory retrieval now supports hybrid lexical + vector
  scoring across episodic, semantic, and affective memory layers, with
  diagnostics emitted for retrieval observability.
- 2026-04-19: semantic vector retrieval posture is now explicit through
  `SEMANTIC_VECTOR_ENABLED`; runtime/action now honor that gate and
  `GET /health` exposes `memory_retrieval.semantic_vector_enabled` plus
  `memory_retrieval.semantic_retrieval_mode`
  (`hybrid_vector_lexical|lexical_only`).
- 2026-04-22: retrieval provider completion now treats `openai` as the target
  provider-owned production baseline when `OPENAI_API_KEY` is configured,
  keeps `local_hybrid` as an explicit local transition path, and keeps
  deterministic execution as the compatibility fallback baseline.
- 2026-04-22: embedding materialization now has one shared owner path across
  repository and action persistence; OpenAI provider-owned execution uses a
  dedicated client, while `/health.memory_retrieval` exposes
  `semantic_embedding_production_baseline`,
  `semantic_embedding_production_baseline_state`, and
  `semantic_embedding_production_baseline_hint` for rollout triage.
- 2026-04-22: deferred reflection externalization now has one shared policy
  owner in `app/core/background_worker_policy.py`, plus a canonical external
  queue-drain entrypoint at `scripts/run_reflection_queue_once.py` with
  PowerShell/bash wrappers.
- 2026-04-22: `/health.reflection.external_driver_policy` and release smoke now
  expose machine-visible external-driver posture so operators can distinguish
  target deferred-worker alignment from local in-process compatibility mode.
- 2026-04-22: proactive runtime activation now has one shared policy owner in
  `app/core/proactive_policy.py`; `/health.proactive`,
  `/health.scheduler.last_proactive_summary`, and runtime
  `system_debug.adaptive_state.proactive_policy` expose cadence ownership,
  delivery-target baseline, and anti-spam thresholds through one contract.
- 2026-04-22: in-process scheduler ownership can now execute bounded proactive
  cadence ticks by selecting opted-in candidates from repository state,
  building scheduler-owned proactive events, and routing them back through the
  normal foreground runtime boundary instead of treating proactive cadence as
  architecture-only scaffolding.
- 2026-04-22: proactive behavior validation now covers both delivery-ready and
  anti-spam-blocked posture, so proactive runtime is proven through
  scenario-level evidence in addition to unit and integration coverage.
- 2026-04-22: role/skill maturity now has one shared policy owner in
  `app/core/role_skill_policy.py`; `/health.role_skill` and runtime
  `system_debug.adaptive_state.role_skill_policy` expose the long-term
  metadata-only skill boundary instead of leaving it implicit in local role
  helpers.
- 2026-04-22: behavior validation now also covers role/skill metadata-only
  posture, connector execution boundary posture, and deferred reflection
  enqueue expectations, so the post-convergence runtime has stronger
  scenario-level proof across its remaining architectural seams.
- 2026-04-19: embedding strategy posture is now explicit through
  `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, and `EMBEDDING_DIMENSIONS` with
  deterministic-fallback visibility in `GET /health.memory_retrieval`
  (requested vs effective provider/model plus fallback hint).
- 2026-04-19: embedding provider readiness posture is now explicit through
  `GET /health.memory_retrieval` fields
  (`semantic_embedding_provider_ready`,
  `semantic_embedding_posture=ready|fallback_deterministic`) and startup now
  emits `embedding_strategy_warning` when requested provider posture falls
  back to deterministic execution.
- 2026-04-19: `MemoryRepository` now persists conclusion embedding shells with
  configured effective embedding posture (model/dimensions) and explicit
  requested-vs-effective provider metadata instead of hardcoded
  `pending/0` placeholders.
- 2026-04-19: embedding strategy warning posture semantics are now shared
  across startup logging and `/health.memory_retrieval` through one helper,
  with explicit warning fields
  (`semantic_embedding_warning_state`, `semantic_embedding_warning_hint`).
- 2026-04-19: embedding persistence scope is now explicit through
  `EMBEDDING_SOURCE_KINDS`; action/repository embedding writes respect enabled
  source families, and `/health.memory_retrieval` exposes configured source
  kinds for operator visibility.
- 2026-04-19: embedding source-coverage posture for current retrieval path is
  now explicit across `/health.memory_retrieval` and startup warning logs via
  shared coverage-state semantics.
- 2026-04-19: embedding refresh-cadence posture is now explicit through
  `EMBEDDING_REFRESH_MODE` (`on_write|manual`) and
  `EMBEDDING_REFRESH_INTERVAL_SECONDS`; `/health.memory_retrieval` exposes
  refresh posture fields and startup emits `embedding_refresh_warning` when
  vectors are enabled in manual mode.
- 2026-04-19: embedding refresh posture semantics are now owned by the shared
  embedding strategy helper, including derived refresh diagnostics
  (`semantic_embedding_refresh_state`,
  `semantic_embedding_refresh_hint`) reused by both `/health.memory_retrieval`
  and startup warning flow.
- 2026-04-19: embedding model-governance posture is now explicit through shared
  diagnostics (`semantic_embedding_model_governance_state`,
  `semantic_embedding_model_governance_hint`) reused by `/health.memory_retrieval`
  and startup warning flow (`embedding_model_governance_warning`).
- 2026-04-19: embedding provider-ownership posture is now explicit through
  shared diagnostics (`semantic_embedding_provider_ownership_state`,
  `semantic_embedding_provider_ownership_hint`) reused by
  `/health.memory_retrieval` and startup fallback warning flow.
- 2026-04-19: embedding provider-ownership enforcement posture is now explicit
  through `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` (`warn|strict`) and shared
  enforcement diagnostics in `/health.memory_retrieval`; strict mode can now
  block startup when provider ownership fallback remains active.
- 2026-04-19: embedding model-governance enforcement posture is now explicit
  through `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` (`warn|strict`) and shared
  enforcement diagnostics in `/health.memory_retrieval`; strict mode can now
  block startup for deterministic custom-model-name governance violations.
- 2026-04-19: embedding owner-strategy recommendation posture is now explicit
  through shared diagnostics
  (`semantic_embedding_owner_strategy_state`,
  `semantic_embedding_owner_strategy_hint`,
  `semantic_embedding_owner_strategy_recommendation`) reused by
  `/health.memory_retrieval` and startup fallback warning flow.
- 2026-04-19: embedding source-rollout recommendation posture is now explicit
  through shared diagnostics
  (`semantic_embedding_source_rollout_state`,
  `semantic_embedding_source_rollout_hint`,
  `semantic_embedding_source_rollout_recommendation`) reused by
  `/health.memory_retrieval` and startup source-coverage warning flow.
- 2026-04-20: embedding strict-rollout preflight posture is now explicit
  through shared diagnostics
  (`semantic_embedding_strict_rollout_violations`,
  `semantic_embedding_strict_rollout_violation_count`,
  `semantic_embedding_strict_rollout_ready`,
  `semantic_embedding_strict_rollout_state`,
  `semantic_embedding_strict_rollout_hint`) reused by `/health` and startup.
- 2026-04-20: embedding strict-rollout recommendation and enforcement-alignment
  posture are now explicit through shared diagnostics
  (`semantic_embedding_strict_rollout_recommendation`,
  `semantic_embedding_recommended_provider_ownership_enforcement`,
  `semantic_embedding_recommended_model_governance_enforcement`,
  `semantic_embedding_provider_ownership_enforcement_alignment`,
  `semantic_embedding_model_governance_enforcement_alignment`,
  `semantic_embedding_enforcement_alignment_state`,
  `semantic_embedding_enforcement_alignment_hint`) in
  `/health.memory_retrieval`.
- 2026-04-20: startup now emits `embedding_strategy_hint` with strict-rollout
  readiness, violation summary, recommendation, and enforcement-alignment
  diagnostics from one shared embedding strategy snapshot owner.
- 2026-04-20: source-rollout sequencing posture is now explicit through shared
  diagnostics
  (`semantic_embedding_source_rollout_order`,
  `semantic_embedding_source_rollout_enabled_sources`,
  `semantic_embedding_source_rollout_missing_sources`,
  `semantic_embedding_source_rollout_next_source_kind`,
  `semantic_embedding_source_rollout_completion_state`,
  `semantic_embedding_source_rollout_phase_index`,
  `semantic_embedding_source_rollout_phase_total`,
  `semantic_embedding_source_rollout_progress_percent`) in
  `/health.memory_retrieval`.
- 2026-04-20: source-rollout state now distinguishes relation-inclusive full
  activation posture (`all_vector_sources_enabled`) from semantic+affective
  baseline rollout posture.
- 2026-04-20: startup now emits `embedding_source_rollout_hint` whenever
  vectors are enabled and source rollout still has a pending next source kind.
- 2026-04-20: refresh cadence posture is now explicit through shared diagnostics
  (`semantic_embedding_refresh_cadence_state`,
  `semantic_embedding_refresh_cadence_hint`) in `/health.memory_retrieval`.
- 2026-04-20: refresh recommendation and alignment posture are now explicit
  through shared diagnostics (`semantic_embedding_recommended_refresh_mode`,
  `semantic_embedding_refresh_alignment_state`,
  `semantic_embedding_refresh_alignment_hint`) in `/health.memory_retrieval`.
- 2026-04-20: startup now emits `embedding_refresh_hint` whenever refresh
  posture deviates from rollout recommendation, and manual refresh warnings now
  include cadence diagnostics.
- 2026-04-20: source-rollout enforcement posture is now explicit through
  `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` (`warn|strict`) plus shared
  diagnostics (`semantic_embedding_source_rollout_enforcement`,
  `semantic_embedding_source_rollout_enforcement_state`,
  `semantic_embedding_source_rollout_enforcement_hint`) in
  `/health.memory_retrieval`; startup now emits
  `embedding_source_rollout_warning` in warn mode and
  `embedding_source_rollout_block` in strict mode for pending rollout states.
- 2026-04-20: source-rollout enforcement recommendation/alignment posture is
  now explicit through shared diagnostics
  (`semantic_embedding_recommended_source_rollout_enforcement`,
  `semantic_embedding_source_rollout_enforcement_alignment`,
  `semantic_embedding_source_rollout_enforcement_alignment_state`,
  `semantic_embedding_source_rollout_enforcement_alignment_hint`) in
  `/health.memory_retrieval`; startup now emits
  `embedding_source_rollout_enforcement_hint` and warning/block logs include
  the same recommendation/alignment diagnostics.
- 2026-04-19: relation memory is now a first-class subsystem (`aion_relation`)
  with scoped repository APIs; reflection derives relation updates and runtime
  stages now consume high-confidence relation cues across context, role,
  planning, and expression.
- 2026-04-19: scheduler-originated event contracts and cadence boundaries are
  now explicit (`scheduler_enabled`, reflection/maintenance/proactive
  intervals), preparing the runtime for scheduled and out-of-process execution.
- 2026-04-19: reflection runtime mode is now explicit (`in_process|deferred`);
  runtime persists reflection enqueue tasks even without in-process worker
  ownership, and reflection worker now supports one-shot pending-task execution
  for future scheduler/out-of-process drivers.
- 2026-04-19: scheduler cadence is now live for reflection and maintenance;
  scheduler runtime uses contract-bounded intervals, mode-aware reflection
  dispatch guardrails, and `/health` scheduler visibility for operations.
- 2026-04-19: subconscious proposal persistence and conscious handoff decisions
  are now explicit runtime owners, including read-only subconscious research
  policy/tool boundaries and proposal lifecycle tracking.
- 2026-04-19: proactive scheduler flow now applies an explicit attention gate
  before outreach planning, and connector-facing planning contracts now include
  permission gates plus typed calendar/task synchronization intents.
- 2026-04-19: `POST /event?debug=true` now emits explicit compatibility headers
  (`X-AION-Debug-Compat`, `Link`) that point to `POST /event/debug`, keeping
  migration intent machine-visible while preserving backward compatibility.
- 2026-04-20: internal debug ingress ownership now uses
  `POST /internal/event/debug` as the primary `system_debug` boundary;
  `POST /event/debug` is now explicit shared-route compatibility ingress, and
  `POST /event?debug=true` compatibility headers now point to the internal
  route.
- 2026-04-20: shared debug ingress posture is now explicitly configurable
  (`EVENT_DEBUG_SHARED_INGRESS_MODE=compatibility|break_glass_only`); in
  `break_glass_only` mode `POST /event/debug` requires explicit
  `X-AION-Debug-Break-Glass: true` override while internal ingress
  `POST /internal/event/debug` remains the primary diagnostics path.
- 2026-04-19: `/health` now exposes explicit attention turn-assembly posture
  (`burst_window_ms`, turn TTLs, `pending|claimed|answered` counters), making
  burst-coalescing diagnostics operator-visible without changing runtime turn
  behavior.
- 2026-04-19: attention turn-assembly timing is now explicitly configurable via
  runtime env/config (`ATTENTION_BURST_WINDOW_MS`,
  `ATTENTION_ANSWERED_TTL_SECONDS`, `ATTENTION_STALE_TURN_SECONDS`) with
  bounded validation and startup wiring into the shared coordinator.
- 2026-04-19: production debug payload access now supports explicit
  token-requirement policy (`PRODUCTION_DEBUG_TOKEN_REQUIRED`, default `true`);
  debug endpoints reject production access when debug exposure is enabled but no
  token is configured under that policy mode.
- 2026-04-19: runtime policy now exposes explicit debug hardening posture
  (`debug_access_posture`, `debug_token_policy_hint`) across health and startup
  policy logging, including dedicated warnings for relaxed
  `PRODUCTION_DEBUG_TOKEN_REQUIRED=false` production debug mode.
- 2026-04-19: strict production policy mismatch posture now includes
  `event_debug_token_missing=true` when debug exposure is enabled, token
  requirement mode is active, and no debug token is configured.
- 2026-04-19: compatibility debug query route posture is now explicitly
  hardening-oriented: `EVENT_DEBUG_QUERY_COMPAT_ENABLED` defaults to disabled
  in production, startup warnings surface explicit production opt-in, and
  strict mismatch previews include `event_debug_query_compat_enabled=true`
  when compatibility route stays enabled in production.
- 2026-04-19: compatibility `POST /event?debug=true` sunset readiness is now
  operator-visible through in-process telemetry
  (`event_debug_query_compat_telemetry`) and explicit compat deprecation
  response header (`X-AION-Debug-Compat-Deprecated=true`).
- 2026-04-19: `/health.runtime_policy` now includes compat sunset decision
  signals (`event_debug_query_compat_allow_rate`,
  `event_debug_query_compat_block_rate`,
  `event_debug_query_compat_recommendation`) derived from telemetry outcomes.
- 2026-04-19: `/health.runtime_policy` now also includes explicit compat sunset
  decision fields (`event_debug_query_compat_sunset_ready`,
  `event_debug_query_compat_sunset_reason`) for machine-readable
  go/no-go posture.
- 2026-04-19: `/health.runtime_policy` now also exposes rolling compat trend
  signals (`event_debug_query_compat_recent_attempts_total`,
  `event_debug_query_compat_recent_allow_rate`,
  `event_debug_query_compat_recent_block_rate`,
  `event_debug_query_compat_recent_state`) derived from telemetry snapshots.
- 2026-04-19: compat recommendation and sunset posture now treat any observed
  compat attempts as migration-needed, while rolling-window trend signals remain
  explicit release-window diagnostics.
- 2026-04-19: compat rolling-window size is now configurable via
  `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` (default `20`, minimum `1`) and is
  wired consistently across lifespan and request-level telemetry fallback.
- 2026-04-19: compat-route freshness posture is now explicit in
  `/health.runtime_policy`
  (`event_debug_query_compat_stale_after_seconds`,
  `event_debug_query_compat_last_attempt_age_seconds`,
  `event_debug_query_compat_last_attempt_state`) with config-driven stale-age
  threshold via `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`.
- 2026-04-19: `/health.runtime_policy` now also exposes compat activity posture
  fields (`event_debug_query_compat_activity_state`,
  `event_debug_query_compat_activity_hint`) so operators can distinguish
  disabled/no-attempt/stale-history/recent-traffic compat dependency states
  without weakening existing sunset-ready contract semantics.

## Technical Baseline

- Backend: Python 3.11, FastAPI, Pydantic v2
- Frontend: none in current repository scope
- Mobile: none in current repository scope
- Database: PostgreSQL with SQLAlchemy async and asyncpg
- Infra: Docker Compose locally, Coolify-targeted compose for deployment
- Hosting target: VPS deployment via Compose/Coolify-oriented runtime docs
- Deployment shape: API-first runtime with app-local reflection worker behavior
- Runtime services: FastAPI app, database, optional Telegram webhook path
- Background jobs / workers: reflection runs as an app-local durable concern;
  scheduler cadence can now trigger reflection/maintenance routines in-process,
  and reflection runtime mode can be `in_process` or `deferred`
- Persistent storage: PostgreSQL
- Health / readiness checks: `GET /health`, `POST /event` smoke, optional
  Telegram webhook verification
- Environment files: `.env`, Docker Compose env wiring, deployment env values
  documented in runtime ops docs
- Observability: stage timings and structured stage-level runtime logs both
  exist
- MCP / external tools: Playwright available locally for future browser-driven
  checks

## Validation Commands

- Lint: not configured yet
- Typecheck: not configured yet
- Unit tests: `.\.venv\Scripts\python -m pytest -q`
- Integration tests: `.\.venv\Scripts\python -m pytest -q tests/<file>.py`
- E2E / smoke: `docker compose up --build`
- Other high-risk checks:
  - `curl http://localhost:8000/health`
  - `curl -X POST http://localhost:8000/event ...`
  - Telegram webhook setup or delivery smoke when integration code changes

## Deployment Contract

- Primary deploy path: Docker Compose locally and Coolify-targeted container
  deployment
- Coolify app/service layout: documented in `docs/operations/runtime-ops-runbook.md`
- Dockerfiles / compose paths: `docker-compose.yml`, project Docker assets in
  repo root
- Required secrets: OpenAI credentials, database connection, Telegram bot
  configuration where relevant
- Public URLs / ports: local API default `http://localhost:8000`
- Backup / restore expectation: database safety and release smoke remain part of
  runtime ops runbook
- Rollback trigger and method: revert to previous container/image plus rerun
  health and `/event` smoke

## Current Focus

- Main active objective: make stage boundaries and architecture traceability
  explicit without regressing current runtime behavior, then deepen the runtime
  toward affective understanding, scoped memory, and stronger action intent
  ownership
- Active `PRJ` execution queue is complete through `PRJ-299`; execution is
  now in Group 19 production memory retrieval rollout after completing Group 18
  background reflection topology and baseline definition in `PRJ-284`.
- `PRJ-288` is the current `READY` implementation slice to define adaptive
  evidence thresholds and influence governance before adaptive signals spread
  further through runtime behavior.
- Top blockers:
  - runtime currently emits connector intents and permission gates but does not
    yet execute provider-backed calendar/task/drive integrations
- Success criteria for this phase:
  - shared goal and milestone signals keep one clear implementation owner
  - runtime stage decisions are observable through structured logs
  - event and startup contracts stay explicit and regression-covered
  - docs, task board, learning journal, and code stay synchronized after each
    slice

## Recent Progress

- 2026-04-20: `PRJ-287` is complete: production retrieval rollout posture is
  now regression-pinned across embedding-strategy, health API, context, and
  runtime pipeline suites, and planning/context docs are synchronized to the
  post-PRJ-286 rollout state.
- 2026-04-20: `PRJ-286` is complete: affective and relation embedding families
  now participate in source-gated rollout with explicit refresh ownership
  metadata (`materialized_on_write` vs `pending_manual_refresh`), and relation
  vectors are now materialized when relation source rollout is enabled.
- 2026-04-20: `PRJ-285` is complete: semantic conclusion embeddings now
  materialize vectors on write (with deterministic fallback posture when
  requested provider execution is unavailable), and episodic embeddings now
  honor explicit refresh ownership (`on_write` vs `manual`) with materialization
  status metadata.
- 2026-04-20: `PRJ-284` is complete: production retrieval baseline is now
  explicitly defined in canonical planning/architecture/runtime-reality/ops
  docs for provider ownership, refresh ownership, and family rollout order
  (`episodic+semantic -> affective -> relation`).
- 2026-04-20: `PRJ-283` is complete: background-topology regressions now pin
  worker-mode handoff guarantees across `/health.reflection.topology`,
  scheduler runtime log posture, and reflection retry skip semantics for
  exhausted tasks.
- 2026-04-20: `PRJ-282` is complete: `/health.reflection.topology` now exposes
  explicit handoff ownership for enqueue/dispatch/queue-drain/retry posture,
  and scheduler reflection tick logs now include mode-aware handoff fields for
  in-process versus external-driver operation.
- 2026-04-20: `PRJ-281` is complete: runtime and scheduler now share one
  reflection enqueue/dispatch boundary contract, with explicit mode-aware
  dispatch decisions (`in_process|deferred`) and regression coverage for the
  shared boundary behavior.
- 2026-04-20: `PRJ-280` is complete: reflection topology ownership is now
  explicit across `in_process|deferred` worker modes, durable queue semantics,
  and operator health posture boundaries in canonical docs and runtime reality.
- 2026-04-20: `PRJ-279` is complete: foreground architecture-parity regressions
  now pin runtime/API/logging boundary order invariants, and planning/context
  docs are synchronized to the converged foreground boundary.
- 2026-04-20: `PRJ-278` is complete: graph/runtime orchestration boundaries are
  now explicit in orchestrator structure (`pre-graph seed`, `graph run`,
  `post-graph follow-up`) with regression coverage.
- 2026-04-20: `PRJ-277` is complete: expression now emits an explicit
  response-execution handoff contract consumed by action, reducing implicit
  delivery coupling.
- 2026-04-20: `PRJ-276` is complete: canonical runtime-flow and
  agent-contract docs now define one explicit foreground ownership split
  (runtime baseline-load and post-action follow-up segments versus graph-owned
  stage spine), and migration invariants now pin stable stage outputs, stage
  ordering, and side-effect ownership while convergence continues.
- 2026-04-19: `PRJ-237` is complete: source-coverage posture for semantic
  retrieval is now operator-visible in `/health.memory_retrieval`, and startup
  warnings now use the same shared coverage-state semantics when vectors are
  enabled with partial/missing semantic-affective source coverage.
- 2026-04-19: `PRJ-237` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`
  passed with `154 passed`.
- 2026-04-19: `PRJ-236` is complete: embedding source-family scope is now
  configurable (`EMBEDDING_SOURCE_KINDS`), runtime embedding writes are gated
  by enabled families, and `/health.memory_retrieval` now exposes effective
  source-kind posture.
- 2026-04-19: `PRJ-236` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`
  passed with `151 passed`.
- 2026-04-19: `PRJ-235` is complete: embedding strategy warning-state semantics
  are now shared between startup logging and `/health.memory_retrieval`, and
  health exposes explicit warning-state/hint fields for operators.
- 2026-04-19: `PRJ-235` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `63 passed`.
- 2026-04-19: `PRJ-234` is complete: conclusion-driven semantic/affective
  embedding shells now use configured effective embedding model/dimensions and
  store requested-vs-effective provider metadata with explicit
  `pending_vector_materialization` status.
- 2026-04-19: `PRJ-234` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`
  passed with `51 passed`.
- 2026-04-19: `PRJ-233` is complete: embedding-provider fallback readiness is
  now operator-visible in `/health.memory_retrieval`, and startup logs now
  warn when configured embedding provider/model posture is not yet executable
  and falls back to deterministic vectors.
- 2026-04-19: `PRJ-233` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  passed with `158 passed`.
- 2026-04-19: `PRJ-232` is complete: embedding strategy config posture is now
  explicit (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`),
  runtime/action keep deterministic fallback semantics for non-implemented
  providers, and `/health.memory_retrieval` now surfaces requested vs
  effective embedding posture with fallback hint.
- 2026-04-19: `PRJ-232` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `142 passed`.
- 2026-04-19: `PRJ-231` is complete: semantic retrieval now has an explicit
  runtime feature gate (`SEMANTIC_VECTOR_ENABLED`) and operator-visible
  `/health.memory_retrieval` posture, while action/runtime preserve default
  hybrid behavior unless lexical-only mode is explicitly selected.
- 2026-04-19: `PRJ-231` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `136 passed`.
- 2026-04-19: `PRJ-221..PRJ-230` are complete: compat activity posture is now
  explicit in `/health.runtime_policy`, including stale-historical vs
  recent-attempt migration states and action hints.
- 2026-04-19: `PRJ-221..PRJ-230` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_config.py`
  passed with `92 passed`.
- 2026-04-19: `PRJ-211..PRJ-220` are complete: compat-route freshness telemetry
  is now policy-visible in `/health.runtime_policy` with config-bounded stale
  threshold and regression coverage across config, telemetry helper, and API.
- 2026-04-19: `PRJ-211..PRJ-220` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_config.py`
  passed with `87 passed`.
- 2026-04-19: `PRJ-201..PRJ-210` are complete: compat telemetry recent-window
  size is now config-driven with bounded validation and regression coverage
  across config, telemetry, and API health contract behavior.
- 2026-04-19: `PRJ-201..PRJ-210` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `94 passed`.
- 2026-04-19: `PRJ-191..PRJ-200` are complete: compat rolling trend slice now
  exposes recent-window counters and state mapping while preserving
  attempt-based migration recommendation posture.
- 2026-04-19: `PRJ-191..PRJ-200` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `89 passed`.
- 2026-04-19: `PRJ-181..PRJ-190` are complete: compat telemetry now includes
  rolling-window counters and `/health.runtime_policy` now exposes recent-trend
  attempts/rates/state for migration-window observability.
- 2026-04-19: `PRJ-181..PRJ-190` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `89 passed`.
- 2026-04-19: `PRJ-171..PRJ-180` are complete: compat-route sunset posture now
  includes explicit machine-readable readiness/reason signals, and recommendation
  logic now treats any observed compat attempts as migration-needed.
- 2026-04-19: `PRJ-171..PRJ-180` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `86 passed`.
- 2026-04-19: `PRJ-161..PRJ-170` are complete: compat sunset recommendation
  guidance is now explicit in `/health.runtime_policy` via allow/block rates
  and recommendation hints derived from compat telemetry.
- 2026-04-19: `PRJ-161..PRJ-170` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `85 passed`.
- 2026-04-19: `PRJ-151..PRJ-160` are complete: compat debug-route sunset
  readiness now includes explicit in-process telemetry counters, deprecation
  response header contract, and synchronized docs/context coverage.
- 2026-04-19: `PRJ-151..PRJ-160` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `82 passed`.
- 2026-04-19: `PRJ-141..PRJ-150` are complete: production debug query-compat
  hardening now has shared mismatch helper ownership, stricter startup/API
  regression coverage, and synchronized docs/context for
  `EVENT_DEBUG_QUERY_COMPAT_ENABLED` posture.
- 2026-04-19: `PRJ-141..PRJ-150` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`
  passed with `79 passed`.
- 2026-04-19: `PRJ-131..PRJ-140` are complete: strict rollout mismatch
  handling now includes `event_debug_token_missing=true` for production
  token-missing posture, and runtime-policy, startup-policy, API health tests,
  and docs/context are synchronized.
- 2026-04-19: `PRJ-131..PRJ-140` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`
  passed with `71 passed`.
- 2026-04-19: `PRJ-121..PRJ-130` are complete: runtime policy now emits
  explicit debug access posture/hint fields, startup policy logs warn when
  production debug runs with relaxed token requirement, and docs/context are
  synchronized for operator-visible debug hardening posture.
- 2026-04-19: `PRJ-121..PRJ-130` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`
  passed with `71 passed`.
- 2026-04-19: `PRJ-111..PRJ-120` are complete: production debug-token
  requirement is now explicit (`PRODUCTION_DEBUG_TOKEN_REQUIRED`), debug route
  access guard enforces production token posture when configured, runtime policy
  snapshots expose the new signal, and ops/config/context docs are synchronized.
- 2026-04-19: `PRJ-111..PRJ-120` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `68 passed`.
- 2026-04-19: `PRJ-101..PRJ-110` are complete: attention timing controls are
  now first-class settings, startup coordinator wiring is config-driven, config
  defaults/validation are regression-covered, and architecture/ops/context docs
  are synchronized for the attention hardening slice.
- 2026-04-19: `PRJ-101..PRJ-110` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_main_lifespan_policy.py tests/test_api_routes.py`
  passed with `48 passed`.
- 2026-04-19: `PRJ-100` is complete: `GET /health` now returns an explicit
  `attention` snapshot (`burst_window_ms`, `answered_ttl_seconds`,
  `stale_turn_seconds`, `pending|claimed|answered`) so burst-turn posture is
  visible in operations/debug workflows.
- 2026-04-19: `PRJ-100` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` passed with
  `29 passed`.
- 2026-04-19: `PRJ-099` is complete: `POST /event?debug=true` now adds explicit
  compatibility headers (`X-AION-Debug-Compat`, `Link`) pointing to
  `POST /event/debug` while preserving backward compatibility.
- 2026-04-19: `PRJ-099` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` passed with
  `28 passed`.
- 2026-04-19: `PRJ-098` is complete: API now exposes explicit
  `POST /event/debug` for internal full-runtime payload inspection while
  preserving `POST /event?debug=true` compatibility, both guarded by the same
  debug policy/token access checks.
- 2026-04-19: `PRJ-098` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` passed with
  `28 passed`; full suite also passes with `433 passed`.
- 2026-04-19: `PRJ-097` is complete: reflection now derives
  `suggest_connector_expansion` proposals from repeated unmet connector needs,
  planning promotes accepted proposals into bounded
  `connector_capability_discovery_intent` outputs, and action persists explicit
  `connector_expansion_update` traces without connector side effects.
- 2026-04-19: `PRJ-097` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_reflection_worker.py`
  passed with `158 passed`; full suite also passes with `429 passed`.
- 2026-04-19: `PRJ-096` is complete: planning and action contracts now include
  connected-drive access intents with explicit `read_only|suggestion_only|mutate_with_confirmation`
  modes, cloud-drive permission gates, and durable episode payload trace
  (`drive_connector_update`) without bypassing action boundaries.
- 2026-04-19: `PRJ-096` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`
  passed with `116 passed`.
- 2026-04-19: `PRJ-087..PRJ-095` are complete: internal planning ownership is
  now explicitly separated from external connector projections, subconscious
  proposals are persisted with conscious handoff resolution, read-only
  subconscious research policy is contract-owned, proactive flow applies an
  explicit attention gate, and connector contracts now expose permission gates
  plus typed calendar/task synchronization intents.
- 2026-04-19: validation for `PRJ-087..PRJ-095` is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`
  passed with `269 passed`.
- 2026-04-19: full regression remains green after dual-loop/connector contract
  coverage expansion:
  `.\.venv\Scripts\python -m pytest -q` passed with `425 passed`.
- 2026-04-19: `PRJ-086` is complete: Telegram burst events now flow through a
  shared attention-turn coordinator that coalesces rapid pending messages into
  one assembled turn and enforces `pending|claimed|answered` ownership before
  foreground runtime execution.
- 2026-04-19: `PRJ-086` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `85 passed`.
- 2026-04-19: `PRJ-085` is complete: runtime graph-state contracts now define
  explicit `attention_inbox`, `pending_turn`, `subconscious_proposals`, and
  `proposal_handoffs` surfaces, and architecture/implementation docs now align
  on one attention-inbox and proposal-handoff vocabulary.
- 2026-04-19: `PRJ-085` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`
  passed with `53 passed`.
- 2026-04-19: `PRJ-084` is complete: proactive delivery now enforces explicit
  user opt-in, outbound/unanswered throttle limits, and delivery-target checks
  before outreach; proactive scheduler deliveries now route via Telegram when a
  `chat_id` target is present.
- 2026-04-19: `PRJ-084` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `82 passed`; extended proactive regression command also passes
  with `177 passed`.
- 2026-04-19: `PRJ-083` is complete: scheduler proactive payloads now normalize
  trigger/importance/urgency plus user-context guardrails, a dedicated proactive
  decision engine now computes interruption-aware outreach decisions, and
  motivation/planning now consume typed proactive decisions for either defer or
  proactive message plans.
- 2026-04-19: `PRJ-083` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `124 passed`.
- 2026-04-19: `PRJ-082` is complete: an in-process scheduler worker now runs
  reflection and maintenance cadence independently from user-event turns,
  reflection dispatch is mode-aware (`in_process|deferred` guardrails), and
  `/health` now exposes scheduler runtime posture and latest tick summaries.
- 2026-04-19: `PRJ-082` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_scheduler_contracts.py tests/test_api_routes.py tests/test_config.py tests/test_reflection_worker.py tests/test_main_lifespan_policy.py`
  passed with `89 passed`; full suite also passes with `395 passed`.
- 2026-04-19: `PRJ-081` is complete: reflection enqueue no longer depends on an
  active in-process worker, runtime now supports deferred reflection mode, and
  reflection worker exposes one-shot queue drain execution for future
  out-of-process/scheduler usage.
- 2026-04-19: targeted `PRJ-081` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`
  passed with `124 passed`.
- 2026-04-19: `PRJ-072..PRJ-080` are complete: optional LangChain prompt
  wrappers landed, semantic retrieval contracts plus pgvector scaffold were
  added, hybrid retrieval diagnostics are now observable, relation storage and
  reflection updates are live, runtime stages became relation-aware, and
  scheduler/cadence contracts were formalized.
- 2026-04-19: validation for the `PRJ-072..PRJ-080` slice is green:
  `.\.venv\Scripts\python -m pytest -q` now passes with `382 passed`, and
  `.\.venv\Scripts\python -m alembic upgrade head --sql` includes both new
  revisions (`20260419_0004`, `20260419_0005`).
- 2026-04-19: `PRJ-071` is complete: foreground stage execution now runs
  through LangGraph with graph-compatible adapters and preserved runtime
  contract behavior; regressions remain green.
- 2026-04-19: `PRJ-069..PRJ-070` are complete: the repo now has an explicit
  graph-compatible state contract (`GraphRuntimeState`), runtime-result
  conversion helpers, and graph-ready adapters around current stage modules,
  with targeted contract tests and runtime regressions passing.
- 2026-04-19: planning and execution context now extend through `PRJ-097`,
  adding explicit follow-up groups for dual-loop coordination, attention
  gating, batched conversation handling, subconscious proposal handoff, and
  future external productivity connector boundaries.
- 2026-04-19: supplemental docs outside `docs/architecture/` now describe the
  planned attention inbox, turn assembly, subconscious proposal handoff, and
  internal-planning-vs-connector boundary so near-term direction is documented
  without rewriting canonical architecture files.
- 2026-04-19: `PRJ-061..PRJ-064` are complete: memory-layer contracts are
  formalized in docs/repository APIs, planning now owns explicit typed domain
  intents, action executes only explicit intents for durable writes, and
  contract tests now pin the planning-owned intent / action-owned execution
  boundary end to end.
- 2026-04-19: `PRJ-065..PRJ-068` are complete: reflection was split into
  concern-owned modules, adaptive updates now require stronger outcome
  evidence, low-leverage milestone pressure drift heuristics were pruned, and
  multi-goal reflection/planning behavior is now regression-covered.

- 2026-04-17: release smoke helper now covers health plus event verification,
  including optional UTF-8 payload and debug-response checks.
- 2026-04-17: next execution roadmap was regrouped into small task batches
  under `docs/planning/next-iteration-plan.md` and `.codex/context/TASK_BOARD.md`.
- 2026-04-17: emotional-turn contract tests now describe supportive behavior
  through documented runtime surfaces instead of the removed `support` mode.
- 2026-04-18: agent workflow context was refreshed to align with the current
  template-era standard, including learning-journal support and corrected
  canonical doc paths.
- 2026-04-18: runtime now emits structured stage-level logs for `memory_load`
  through `state_refresh`, and regression tests cover both success and failure
  logging paths.
- 2026-04-18: shared signal extraction group is complete (`PRJ-011..PRJ-013`);
  heuristic modules were reduced (`context: 801->751`, `planning: 755->676`,
  `motivation: 560->489`, `reflection: 1362->1318`) with behavior preserved by
  regression tests.
- 2026-04-18: the post-`PRJ-016` planning queue was expanded with future
  `Stage Boundary Alignment` and `Architecture Traceability And Contract Tests`
  groups so architecture-parity follow-up is visible without displacing the
  current execution order.
- 2026-04-18: `PRJ-015` and `PRJ-016` are complete: API boundary normalization
  is explicit and test-covered, and startup now defaults to migration-first with
  an explicit compatibility toggle.
- 2026-04-18: `PRJ-017` is complete: expression-to-action handoff now uses a
  dedicated `ActionDelivery` contract and regression tests pin the API/Telegram
  delivery path through that contract.
- 2026-04-18: `PRJ-019` is complete: overview and architecture docs now map
  runtime stages to code ownership and primary validation surfaces, with public
  vs debug runtime contract boundaries made explicit.
- 2026-04-18: `PRJ-018` is complete: action delivery dispatch moved to
  integration ownership through `DeliveryRouter`, preserving API/Telegram
  behavior while reducing action/integration coupling.
- 2026-04-18: `PRJ-020` is complete: runtime flow now has contract-level smoke
  tests across runtime pipeline, API response shape, and stage-level logging
  payload invariants.
- 2026-04-18: `PRJ-021` is complete: debug payload exposure for
  `POST /event?debug=true` is now explicitly gated by config and covered by API
  and config tests.
- 2026-04-19: `PRJ-022` is complete: `/health` now exposes non-secret runtime
  policy flags (`startup_schema_mode`, `event_debug_enabled`) for operator
  traceability, with API tests and docs synchronized.
- 2026-04-19: `PRJ-023` is complete: startup now warns when production runs with
  debug payload exposure enabled, with targeted tests and docs synchronized.
- 2026-04-19: `PRJ-024` is complete: startup now warns when production runs in
  schema compatibility mode (`STARTUP_SCHEMA_MODE=create_tables`), with
  targeted tests and docs synchronized.
- 2026-04-19: `PRJ-025` is complete: debug payload policy now has production-safe
  default behavior with explicit source visibility in `/health`, and tests/docs
  are synchronized.
- 2026-04-19: `PRJ-026` is complete: production runtime-policy enforcement now
  supports `warn|strict`, startup can fail fast on policy mismatches when
  strict mode is active, and `/health` exposes the enforcement posture.
- 2026-04-19: `PRJ-027` is complete: startup strict-policy behavior now has a
  lifespan-level fail-fast regression test that confirms policy mismatch blocks
  runtime before database initialization.
- 2026-04-19: `PRJ-028` is complete: strict startup-policy lifecycle tests now
  cover both debug and schema mismatch paths, confirming fail-fast behavior
  before database initialization side effects.
- 2026-04-19: `PRJ-029` is complete: runtime policy logic now has a shared core
  helper used by startup and `/health`, and `/health` now exposes
  `production_policy_mismatches` with regression coverage for startup/API
  consumers.
- 2026-04-19: `PRJ-030..PRJ-039` are complete: runtime policy now includes
  strict rollout readiness helpers and `/health` contract fields
  (`production_policy_mismatch_count`, `strict_startup_blocked`,
  `strict_rollout_ready`), startup and health now share the same strict-block
  semantics, and regression coverage/docs/context were synchronized.
- 2026-04-19: `PRJ-040..PRJ-045` are complete: runtime policy now includes
  strict rollout recommendation helpers and `/health` contract fields
  (`recommended_production_policy_enforcement`, `strict_rollout_hint`),
  startup now logs strict-ready rollout hints in production warn mode, and
  regression coverage/docs/context were synchronized.
- 2026-04-19: `PRJ-046..PRJ-051` are complete: debug payload access now
  supports optional token gating (`EVENT_DEBUG_TOKEN` and
  `X-AION-Debug-Token`), health policy now exposes token-required state,
  startup warns when production debug exposure is enabled without token, and
  regression coverage/docs/context were synchronized.
- 2026-04-19: `PRJ-052` is complete: `POST /event` now accepts
  `X-AION-User-Id` as fallback identity when `meta.user_id` is omitted,
  normalization/API tests now pin user-id precedence, and docs/context were
  synchronized for multi-user API safety.
- 2026-04-19: `PRJ-053` is complete: runtime contracts now include explicit
  affective assessment fields, perception emits deterministic affective
  placeholders, runtime exposes top-level affective state, and
  architecture/planning/context docs plus regression tests were synchronized.
- 2026-04-19: `PRJ-054` is complete: runtime now runs a dedicated affective
  assessor stage that can normalize LLM classification and safely fall back
  when unavailable or invalid, with regression tests and docs/context aligned.
- 2026-04-19: `PRJ-055` is complete: motivation, role, and expression now use
  the shared affective contract (`perception.affective`) as their support
  signal owner, replacing local emotional keyword ladders and adding
  affective-driven regression coverage.
- 2026-04-19: `PRJ-056` is complete: empathy-oriented shared fixtures now cover
  emotionally heavy, ambiguous, and mixed-intent turns, and support-quality
  regression coverage was expanded across motivation, expression, and runtime.
- 2026-04-19: `PRJ-057` is complete: scoped conclusions were introduced for
  global/goal/task context in schema, repository APIs, and reflection writes,
  with scope-aware tests and migration validation synchronized.
- 2026-04-19: `PRJ-058` is complete: runtime now consumes goal-scoped
  reflection state with global fallback, and regression tests pin no-leakage
  behavior across context, motivation, planning, and runtime.
- 2026-04-19: `PRJ-059` is complete: episodic memory now carries affective
  tags, reflection derives slower-moving affective conclusions, and runtime
  consumers reuse those signals across turns.
- 2026-04-19: `PRJ-060` is complete: runtime memory loading and context
  retrieval now go beyond latest-five depth with affective-aware ranking and
  compression.
- 2026-04-19: architecture docs were realigned so `docs/architecture/` again
  describes the canonical cognitive flow, while runtime-delivery shortcuts,
  live storage names, and policy details were moved into
  `docs/implementation/runtime-reality.md` and linked from the docs index.
- 2026-04-19: planning docs and execution context were extended through
  `PRJ-084`, adding grouped follow-up slices for affective understanding,
  scoped memory, explicit action intents, adaptive-signal governance, graph
  orchestration adoption, semantic retrieval infrastructure, relation system,
  and scheduled/proactive runtime.
- 2026-04-20: planning, board, and open-decisions context now extend through
  `PRJ-299`, shifting the next queue from generic architecture hardening toward
  target-state convergence across foreground runtime boundaries, background
  reflection topology, production retrieval rollout, adaptive governance,
  dual-loop execution boundaries, and operational hardening.
- 2026-04-20: foreground convergence group is now complete through `PRJ-279`;
  background topology convergence is complete through `PRJ-283`; production
  retrieval implementation is complete through `PRJ-287`; adaptive governance
  policy baseline is complete through `PRJ-288`; runtime behavior-validation
  lane is now complete through `PRJ-317`.
- 2026-04-20: `PRJ-288` is complete: architecture contracts now define explicit
  adaptive influence evidence gates, precedence, and tie-break guardrails for
  affective, relation, preference, and theta signals.
- 2026-04-20: `PRJ-288` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `151 passed`.
- 2026-04-20: `PRJ-289` is complete: role, motivation, and planning now consume
  shared governed adaptive-policy helpers (`app/core/adaptive_policy.py`) for
  relation evidence thresholds, preferred-role gating, theta dominance, and
  adaptive tie-break posture checks.
- 2026-04-20: `PRJ-289` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_adaptive_policy.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `156 passed`.
- 2026-04-20: `PRJ-290` is complete: proactive decision and attention gating
  now consume governed relation/theta policy surfaces from
  `app/core/adaptive_policy.py`, and adaptive cues can tighten proactive
  posture without bypassing attention or anti-spam guardrails.
- 2026-04-20: `PRJ-290` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_adaptive_policy.py`
  passed with `176 passed`.
- 2026-04-20: `PRJ-291` is complete: adaptive-governance regressions now pin
  anti-feedback-loop behavior in reflection, goal-scoped relation retrieval in
  runtime proactive attention gating, and sub-threshold adaptive influence
  boundaries across role/motivation/planning consumers.
- 2026-04-20: `PRJ-291` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `206 passed`.
- 2026-04-20: `PRJ-292` is complete: canonical dual-loop ownership is now
  explicit for attention turn assembly (`attention_inbox`, `pending_turn`),
  conscious proposal handoff decisions (`proposal_handoffs`), and action-side
  execution boundaries after planning decisions.
- 2026-04-20: `PRJ-292` validation is recorded as doc-and-context sync plus
  targeted dual-loop contract review across
  `docs/architecture/15_runtime_flow.md`,
  `docs/architecture/16_agent_contracts.md`,
  `docs/planning/open-decisions.md`,
  `docs/implementation/runtime-reality.md`,
  `.codex/context/TASK_BOARD.md`, and
  `docs/planning/next-iteration-plan.md`.
- 2026-04-20: `PRJ-293` is complete: subconscious proposal persistence now
  supports conscious re-entry from retriable lifecycle states
  (`pending|deferred`), planning skips non-retriable proposal states, and
  conscious handoff decisions continue to gate resolution before proposal-driven
  side-effect shaping.
- 2026-04-20: `PRJ-293` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_planning_agent.py`
  passed with `193 passed`.
- 2026-04-20: `PRJ-294` is complete: proactive outreach and connector
  permission-gate outcomes now share one conscious execution boundary, keeping
  connector discovery and proactive delivery aligned with the same plan/action
  gating model.
- 2026-04-20: `PRJ-294` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_planning_agent.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `181 passed`.
- 2026-04-20: `PRJ-295` is complete: dual-loop execution-boundary regressions
  now pin proactive-path separation from proposal handoff and connector
  permission-gate intent shaping, while attention turn assembly and conscious
  proposal resolution remain covered end to end.
- 2026-04-20: `PRJ-295` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py tests/test_action_executor.py tests/test_planning_agent.py`
  passed with `229 passed`.
- 2026-04-20: `PRJ-296` is complete: target production baseline now explicitly
  defines migration-only startup posture, strict production policy target, and
  internal debug boundary expectations (public compact event path, debug route
  hardening, production compat-route disable baseline).
- 2026-04-20: `PRJ-296` validation is recorded as doc-and-context sync plus
  targeted production-baseline review across
  `docs/planning/open-decisions.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `.codex/context/TASK_BOARD.md`, and
  `docs/planning/next-iteration-plan.md`.
- 2026-04-20: `PRJ-297` is complete: runtime policy now resolves production
  enforcement to `strict` by default when unset, while explicit
  `PRODUCTION_POLICY_ENFORCEMENT=warn` remains a controlled override; startup
  and `/health` policy surfaces now reflect that production-aware default.
- 2026-04-20: `PRJ-297` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`
  passed with `142 passed`.
- 2026-04-20: `PRJ-298` is complete: deployment trigger ownership now has one
  explicit operations baseline (Coolify automation first, explicit webhook/UI
  fallback), and release smoke ownership is codified as a release gate.
- 2026-04-20: `PRJ-298` validation is green:
  `.\.venv\Scripts\python -m pytest -q`
  passed with `598 passed`.
- 2026-04-20: `PRJ-299` is complete: `/health` now exposes a compact
  `release_readiness` gate snapshot (`ready`, `violations`) derived from
  runtime-policy release guardrails, and release smoke scripts fail fast on
  production-policy drift.
- 2026-04-20: `PRJ-299` validation is green:
  `.\.venv\Scripts\python -m pytest -q`
  passed with `602 passed`.
- 2026-04-20: `PRJ-300` is complete: first post-convergence planning queue is
  now seeded through `PRJ-304`, keeping execution continuity after
  operational-hardening closure (`PRJ-299`).
- 2026-04-20: `PRJ-300` validation is recorded as doc-and-context sync plus
  targeted planning coherence review across
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`,
  `.codex/context/PROJECT_STATE.md`, and
  `docs/planning/open-decisions.md`.
- 2026-04-20: `PRJ-301` is complete: production reflection deployment baseline
  now stays `REFLECTION_RUNTIME_MODE=in_process` by default, while deferred
  dispatch is explicitly gated behind external-readiness criteria.
- 2026-04-20: `PRJ-301` validation is recorded as doc-and-context sync plus
  targeted reflection-topology contract review across
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/implementation/runtime-reality.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-302` is complete: `/health.reflection` now exposes
  deployment-readiness posture (`ready`, `blocking_signals`,
  baseline/selected runtime mode) derived from runtime mode, topology, worker
  state, and reflection task health signals.
- 2026-04-20: `PRJ-302` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_reflection_worker.py`
  passed with `119 passed`.
- 2026-04-20: `PRJ-303` is complete: reflection deployment-readiness
  regressions now pin blocker semantics in shared scheduler contracts and
  `/health`, while release smoke scripts now fail fast on reflection readiness
  blockers with explicit fallback checks for older runtimes.
- 2026-04-20: `PRJ-303` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_scheduler_contracts.py`
  passed with `120 passed`.
- 2026-04-20: `PRJ-304` is complete: reflection deployment baseline/readiness
  docs are now synchronized across planning, runtime-reality, and operations
  runbook surfaces, including consistent release/rollback readiness gating.
- 2026-04-20: `PRJ-304` validation is recorded as doc-and-context sync plus
  targeted ops-runbook review across
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-305` is complete: post-reflection hardening queue is now
  seeded through `PRJ-309`, keeping execution continuity after reflection lane
  closure (`PRJ-304`).
- 2026-04-20: `PRJ-305` validation is recorded as doc-and-context sync plus
  targeted planning coherence review across
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`,
  `.codex/context/PROJECT_STATE.md`, and
  `docs/planning/open-decisions.md`.
- 2026-04-20: `PRJ-306` is complete: migration strategy now has explicit
  criteria and rollout guardrails for removing `create_tables` compatibility
  startup path without reopening production baseline decisions.
- 2026-04-20: `PRJ-306` validation is recorded as doc-and-context sync plus
  targeted migration-strategy review across
  `docs/planning/open-decisions.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-307` is complete: public API follow-up decision now defines
  explicit target internal debug ingress boundary and migration ownership away
  from shared public API service endpoint posture.
- 2026-04-20: `PRJ-307` validation is recorded as doc-and-context sync plus
  targeted public-api boundary review across
  `docs/planning/open-decisions.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-308` is complete: scheduler/proactive follow-up now defines
  explicit long-term external cadence ownership posture while keeping app-local
  scheduler cadence as transitional/fallback rollout surface.
- 2026-04-20: `PRJ-308` validation is recorded as doc-and-context sync plus
  targeted scheduler-boundary review across
  `docs/planning/open-decisions.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-309` is complete: post-reflection hardening queue decisions
  are now synchronized across planning, project state, and operations runbook
  before entering runtime behavior-validation execution lane.
- 2026-04-20: `PRJ-309` validation is recorded as doc-and-context sync plus
  targeted cross-doc consistency review across
  `docs/planning/open-decisions.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: canonical architecture now includes
  `docs/architecture/29_runtime_behavior_testing.md`, which defines required
  system-debug visibility, user-simulation mode, and behavior-driven validation
  expectations for memory, continuity, decision integrity, and failure
  handling.
- 2026-04-20: execution planning now extends through `PRJ-317`, adding a
  runtime-behavior validation lane for internal debug surfaces, memory
  influence checks, continuity scenarios, and failure-mode behavior gating.
- 2026-04-20: `PRJ-310..PRJ-313` are complete: runtime now exposes a canonical
  `system_debug` validation surface and behavior-harness helpers with
  structured scenario output (`test_id`, `status`, `reason`, `trace_id`,
  `notes`), and docs/context are synchronized to that contract.
- 2026-04-20: `PRJ-314..PRJ-316` are complete: scenario coverage now validates
  memory `write -> retrieve -> influence -> delayed recall`, multi-session
  continuity/personality stability, and contradiction/missing-data/noisy-input
  resilience.
- 2026-04-20: `PRJ-317` is complete: release-readiness now includes explicit
  behavior-validation evidence via `scripts/run_behavior_validation.{ps1,sh}`
  in addition to full regression checks.
- 2026-04-20: runtime behavior-validation checks are green:
  - `.\scripts\run_behavior_validation.ps1` passed with `6 passed`.
  - `.\.venv\Scripts\python -m pytest -q` passed with `612 passed`.
- 2026-04-20: execution planning now extends through `PRJ-337`, adding
  implementation lanes for internal debug ingress migration, scheduler
  externalization and attention ownership, identity/language boundary
  hardening, relation lifecycle rollout, and inferred goal/task growth through
  typed intents.
- 2026-04-20: `PRJ-318` is complete: runtime now exposes
  `POST /internal/event/debug` as the primary debug ingress, keeps
  `POST /event/debug` as compatibility ingress with explicit shared-route
  migration headers, and extends runtime policy snapshot with
  debug-ingress ownership/path posture fields.
- 2026-04-20: `PRJ-318` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`
  passed with `108 passed`.
- 2026-04-20: `PRJ-319` is complete: shared debug ingress now supports
  explicit `compatibility|break_glass_only` modes, break-glass override is
  enforced for shared endpoint access in `break_glass_only` mode, and runtime
  policy now surfaces shared-ingress break-glass posture fields.
- 2026-04-20: `PRJ-319` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`
  passed with `153 passed`.
- 2026-04-20: `PRJ-320` is complete: regression coverage now pins
  break-glass shared-ingress posture and health visibility for internal/shared
  debug ingress migration semantics.
- 2026-04-20: `PRJ-320` also extends release smoke scripts
  (`scripts/run_release_smoke.ps1`, `scripts/run_release_smoke.sh`) with
  explicit internal/shared debug-ingress contract checks
  (path ownership, shared mode, break-glass requirement, posture consistency).
- 2026-04-20: `PRJ-320` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`
  passed with `113 passed`.
- 2026-04-20: `PRJ-321` is complete: canonical docs, planning notes, and
  operations runbook now align with internal debug ingress migration reality
  (`POST /internal/event/debug` primary, shared `POST /event/debug`
  compatibility posture, break-glass controls, and updated compat headers).
- 2026-04-20: `PRJ-321` validation is recorded as doc-and-context sync plus
  targeted debug-ingress cross-doc review across
  `docs/overview.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-322` is complete: scheduler cadence ownership now has one
  explicit execution-mode contract (`in_process|externalized`) with shared
  scheduler-readiness posture, worker snapshot ownership fields, and
  `/health.scheduler` owner visibility for maintenance/proactive cadence.
- 2026-04-20: `PRJ-322` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_config.py`
  passed with `129 passed`.
- 2026-04-20: `PRJ-323` is complete: maintenance/proactive cadence now use
  shared owner-aware dispatch decisions, and scheduler maintenance execution
  explicitly respects `in_process|externalized` ownership mode with
  machine-visible dispatch reasons.
- 2026-04-20: `PRJ-323` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_api_routes.py`
  passed with `157 passed`.
- 2026-04-20: `PRJ-324` is complete: attention coordination now exposes
  explicit owner posture (`in_process|durable_inbox`) with deployment-readiness
  diagnostics and durable-owner blocker semantics in `/health.attention`.
- 2026-04-20: `PRJ-324` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_scheduler_contracts.py tests/test_config.py`
  passed with `188 passed`.
- 2026-04-20: `PRJ-325` is complete: docs/context/runbook are synchronized with
  owner-aware scheduler cadence posture and attention owner/readiness posture
  (`SCHEDULER_EXECUTION_MODE`, `ATTENTION_COORDINATION_MODE`, and health
  ownership/readiness fields).
- 2026-04-20: `PRJ-325` validation is recorded as doc-and-context sync plus
  targeted scheduler/attention cross-doc review across
  `docs/overview.md`,
  `docs/architecture/26_env_and_config.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-20: `PRJ-326` is complete: runtime identity loading now enforces an
  explicit owner boundary where `aion_profile` remains the durable owner for
  profile language, while identity response/collaboration preferences are
  sourced from conclusion-owned runtime preference inputs only.
- 2026-04-20: `PRJ-326` also keeps relation-derived collaboration fallback for
  planning/expression tie-break behavior without leaking that fallback into
  identity continuity fields.
- 2026-04-20: `PRJ-326` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `136 passed`.
- 2026-04-20: `PRJ-327` is complete: language detection now follows explicit
  precedence across current-turn lexical signals, recent memory continuity, and
  durable profile preference.
- 2026-04-20: `PRJ-327` also expands continuity parsing to use
  `payload.response_language` hints from episodic memory and ignores
  unsupported language codes before falling back to profile/default posture.
- 2026-04-20: `PRJ-327` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_context_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`
  passed with `140 passed`.
- 2026-04-20: `PRJ-328` is complete: identity/language continuity regressions
  now pin ambiguous-turn language continuity across runtime session restarts
  and profile-backed fallback behavior.
- 2026-04-20: `PRJ-328` also adds API fallback regression coverage to ensure
  `X-AION-User-Id` remains per-request identity fallback and does not leak into
  later requests without explicit identity input.
- 2026-04-20: `PRJ-328` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `141 passed`.
- 2026-04-21: `PRJ-329` is complete: canonical docs, runtime-reality notes,
  planning notes, and project context now share one identity/language/profile
  continuity baseline.
- 2026-04-21: `PRJ-329` sync explicitly records profile-versus-conclusion
  identity ownership (`aion_profile` language owner, conclusion-owned response
  and collaboration preferences), language continuity precedence, and
  request-scoped API identity fallback (`meta.user_id` ->
  `X-AION-User-Id` -> `anonymous`).
- 2026-04-21: `PRJ-329` validation is recorded as doc-and-context sync plus
  targeted identity-boundary cross-doc review across
  `docs/overview.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-330` is complete: relation retrieval now applies
  age-aware confidence revalidation with evidence-sensitive decay and explicit
  expiration posture for stale relation signals.
- 2026-04-21: `PRJ-330` also refreshes relation durability by blending
  repeated same-value relation evidence in upsert paths and allows reflection
  to persist relation-only revalidation updates (`delivery_reliability=low_trust`)
  without requiring a conclusion/theta write in the same turn.
- 2026-04-21: `PRJ-330` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
  passed with `155 passed`.
- 2026-04-21: `PRJ-331` is complete: trust governance now shapes proactive
  interruption behavior through shared relation/theta-aware cost adjustments,
  trust-calibrated proactive relevance, and low-trust/high-trust outreach
  output posture (including tone-oriented plan steps).
- 2026-04-21: `PRJ-331` also extends foreground trust influence so motivation
  uses delivery-reliability tie-breaks on ambiguous turns while planning adds
  explicit confidence posture steps (`plan_with_confident_next_step`,
  `plan_with_cautious_validation`) and trust-aware proactive outreach tone
  steps (`use_confident_outreach_tone`, `use_low_pressure_outreach_tone`).
- 2026-04-21: `PRJ-331` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_adaptive_policy.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
  passed with `172 passed`.
- 2026-04-21: `PRJ-331` required board validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `247 passed`.
- 2026-04-21: `PRJ-338` is complete: Telegram delivery now hardens exception
  boundaries (`4xx/5xx`, timeout, transport failure) in
  `DeliveryRouter`, degrading failures to structured
  `ActionResult(status=fail)` responses instead of uncaught action-stage
  exceptions that surface as endpoint 500s.
- 2026-04-21: `PRJ-338` also adds fail-path regression coverage across delivery
  router, action executor, runtime pipeline, and debug ingress API boundaries,
  including explicit `/internal/event/debug` fail-action response posture.
- 2026-04-21: `PRJ-338` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `160 passed`.
- 2026-04-21: `PRJ-338` app-lifespan manual smoke attempt through
  `POST /internal/event/debug` was blocked in this workspace by unresolved DB
  host startup dependency (`socket.gaierror [Errno 11001] getaddrinfo failed`);
  the recurring execution guardrail is captured in
  `.codex/context/LEARNING_JOURNAL.md`.
- 2026-04-21: `PRJ-332` is complete: relation lifecycle and trust-influence
  regressions now pin value-shift lifecycle reset posture in repository
  relation upserts, medium-trust derivation in reflection, low-confidence
  trust gating for proactive attention, and low-confidence support-intensity
  relation gating for expression tone selection.
- 2026-04-21: `PRJ-332` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_expression_agent.py`
  passed with `175 passed`.
- 2026-04-21: `PRJ-333` is complete: docs/planning/context now share one
  relation lifecycle and trust-influence baseline, including relation refresh
  vs value-shift reset posture, age-aware revalidation/expiration, and
  low-confidence trust-signal guardrails.
- 2026-04-21: `PRJ-333` validation is recorded as doc-and-context sync plus
  targeted relation-lifecycle cross-doc review across
  `docs/overview.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-334` is complete: planning now promotes bounded inferred
  goal/task intents from repeated blocker evidence when explicit declaration
  patterns are absent, while preserving confidence/evidence gates and
  duplicate guards against active planning state.
- 2026-04-21: `PRJ-334` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`
  passed with `167 passed`.
- 2026-04-21: `PRJ-335` is complete: inferred planning writes now use explicit
  typed intents (`promote_inferred_goal`, `promote_inferred_task`,
  `maintain_task_status`) and action executes those intents as the only owner
  of durable inferred promotion and maintenance writes.
- 2026-04-21: `PRJ-335` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  passed with `150 passed`.
- 2026-04-21: `PRJ-336` is complete: inference safety and duplicate-avoidance
  regressions now pin non-repeated/weak-signal no-promotion posture and
  no-duplicate behavior when matching active inferred planning state already
  exists.
- 2026-04-21: `PRJ-336` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py`
  passed with `202 passed`.
- 2026-04-21: `PRJ-337` is complete: architecture/planning/runtime-reality
  docs plus context truth now share one baseline for bounded inferred
  goal/task promotion, typed inferred and maintenance intents, and action-owned
  durable execution boundaries.
- 2026-04-21: `PRJ-337` validation is recorded as doc-and-context sync plus
  targeted planning-autonomy cross-doc review across
  `docs/architecture/16_agent_contracts.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/open-decisions.md`,
  `docs/planning/next-iteration-plan.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-339` is complete: affective classifier integration now uses
  structured parse/schema gates plus explicit fallback diagnostics, and runtime
  affective stage logs include fallback reason traces to avoid silent drift.
- 2026-04-21: `PRJ-339` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_openai_client.py tests/test_affective_contract.py tests/test_expression_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `165 passed`.
- 2026-04-21: `PRJ-340` is complete: planning goal/task detection now supports
  deterministic natural inline command phrasing in English and Polish
  (for example `add goal ...`, `add task ...`, `dodaj cel ...`,
  `dodaj zadanie ...`) in addition to strict prefix-only forms.
- 2026-04-21: `PRJ-340` also keeps false-positive guardrails for non-command
  mentions and preserves typed domain-intent extraction boundaries
  (`upsert_goal|upsert_task`) through shared signal utilities.
- 2026-04-21: `PRJ-340` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_goal_task_signals.py`
  passed with `204 passed`.
- 2026-04-21: `PRJ-341` is complete: operator-facing Telegram smoke workflow
  now includes explicit webhook/listen mode switching probes
  (`getWebhookInfo -> deleteWebhook -> getUpdates -> setWebhook`) across
  PowerShell and bash scripts.
- 2026-04-21: `PRJ-341` also adds runbook-level precondition checks for
  reliable delivery triage (`/start` handshake, known `chat_id`, bot token,
  webhook secret parity) to reduce false-negative Telegram diagnostics.
- 2026-04-21: `PRJ-341` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_event_normalization.py tests/test_delivery_router.py`
  passed with `83 passed`.
- 2026-04-21: `PRJ-341` live Telegram smoke execution is not recorded in this
  workspace because runtime bot credentials are unavailable here; evidence
  coverage is provided through shipped operator scripts and runbook checklist.
- 2026-04-21: `PRJ-342` is complete: planning docs, operations runbook, and
  context truth now align for manual runtime reliability fixes through
  `PRJ-342`.
- 2026-04-21: `PRJ-342` also seeds the next derived architecture queue
  (`PRJ-343..PRJ-346`) for relation-aware inferred promotion governance
  follow-up.
- 2026-04-21: `PRJ-342` validation is recorded as doc-and-context sync plus
  targeted cross-reference checks across
  `docs/planning/next-iteration-plan.md`,
  `docs/planning/open-decisions.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-343` is complete: inferred goal/task promotion gating now
  uses delivery-reliability posture (`low_trust|medium_trust|high_trust`)
  through deterministic thresholds while keeping explicit declaration intents
  unaffected.
- 2026-04-21: `PRJ-343` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_adaptive_policy.py`
  passed with `145 passed`.
- 2026-04-21: `PRJ-344` is complete: inferred-promotion gate diagnostics are
  now explicit in planning output (`reason=...`, `result=...`) and available in
  runtime `system_debug.plan.inferred_promotion_diagnostics`.
- 2026-04-21: `PRJ-344` also extends API debug contract coverage so
  `/internal/event/debug` plan payload remains stable while exposing inferred
  promotion diagnostics for operator triage.
- 2026-04-21: `PRJ-344` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `200 passed`.
- 2026-04-21: `PRJ-345` is complete: regression coverage now pins trust-aware
  inferred promotion gates and diagnostics across planning/runtime paths
  (including low-trust repeated-signal guardrails and high-trust/medium-trust
  promotion behavior).
- 2026-04-21: `PRJ-345` also extends debug-surface coverage so inferred gate
  diagnostics remain visible and contract-stable in runtime and API debug
  responses.
- 2026-04-21: `PRJ-345` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py`
  passed with `251 passed`.
- 2026-04-21: `PRJ-346` is complete: architecture/runtime/planning/context
  docs now align on trust-aware inferred promotion thresholds and
  machine-visible inferred gate diagnostics posture.
- 2026-04-21: `PRJ-346` also seeds the next derived queue
  (`PRJ-347..PRJ-350`) for behavior-validation CI-ingestion follow-up.
- 2026-04-21: `PRJ-346` validation is recorded as doc-and-context sync plus
  targeted cross-reference checks across
  `docs/architecture/16_agent_contracts.md`,
  `docs/implementation/runtime-reality.md`,
  `docs/planning/next-iteration-plan.md`,
  `docs/planning/open-decisions.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-347` is complete: behavior validation now has a shared
  Python entrypoint (`scripts/run_behavior_validation.py`) that emits a
  machine-readable JSON artifact with summary counts, per-test status, and
  pytest exit-code posture for CI ingestion.
- 2026-04-21: `PRJ-347` also updates both shell wrappers
  (`run_behavior_validation.ps1`, `run_behavior_validation.sh`) to consume the
  shared artifact-producing path without breaking local/operator behavior.
- 2026-04-21: `PRJ-347` validation is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj347-report.json`
  passed with `6 passed`.
- 2026-04-21: `PRJ-347` scope regression is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `140 passed`.
- 2026-04-21: `PRJ-348` is complete: behavior-validation release scripts now
  expose explicit gate posture controls (`operator|ci`) and CI mode can fail
  fast using artifact-level gate semantics.
- 2026-04-21: `PRJ-348` also extends artifact output with machine-readable gate
  metadata (`gate.mode`, `gate.status`, `gate.violations`) so CI consumers and
  operators share one contract.
- 2026-04-21: `PRJ-348` validation is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj348-operator.json --gate-mode operator`
  passed with `6 passed`.
- 2026-04-21: `PRJ-348` CI posture validation is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj348-ci.json --gate-mode ci`
  passed with `6 passed`.
- 2026-04-21: `PRJ-348` required regression scope is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `101 passed`.
- 2026-04-21: `PRJ-349` is complete: script-level regressions now pin
  behavior-validation artifact gate semantics for `operator` and `ci` modes,
  including explicit CI fail-fast posture when no tests are collected.
- 2026-04-21: `PRJ-349` regression contract now verifies artifact gate fields
  (`gate.mode`, `gate.status`, `gate.violations`, `gate.ci_require_tests`) and
  preserves operator-mode exit behavior.
- 2026-04-21: `PRJ-349` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py`
  passed with `5 passed`.
- 2026-04-21: `PRJ-349` required regression scope is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `176 passed`.
- 2026-04-21: `PRJ-350` is complete: planning, operations runbook, testing
  guidance, and context truth now align on behavior-validation artifact
  contract and `operator|ci` gate posture.
- 2026-04-21: `PRJ-350` also seeds the next derived queue
  (`PRJ-351..PRJ-354`) for behavior-validation artifact-governance follow-up.
- 2026-04-21: `PRJ-350` validation is recorded as doc-and-context sync plus
  targeted cross-reference checks across
  `docs/planning/next-iteration-plan.md`,
  `docs/planning/open-decisions.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/engineering/testing.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-351` is complete: behavior-validation artifact output now
  includes explicit schema-version metadata and normalized gate-reason
  taxonomy/version fields for deterministic CI parsing.
- 2026-04-21: `PRJ-351` also adds explicit gate `violation_context` payload so
  reason codes can be interpreted without parsing free-text fragments.
- 2026-04-21: `PRJ-351` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_runtime_pipeline.py`
  passed with `80 passed`.
- 2026-04-21: `PRJ-351` artifact smoke is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj351-report.json --gate-mode ci`
  passed with `6 passed`.
- 2026-04-21: `PRJ-352` is complete: behavior-validation script now supports
  local artifact-input gate evaluation mode for CI consumers without rerunning
  pytest.
- 2026-04-21: `PRJ-352` also hardens artifact-input parsing with UTF-8 BOM
  tolerance so PowerShell-authored artifact payloads remain readable by gate
  evaluation flows.
- 2026-04-21: `PRJ-352` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `108 passed`.
- 2026-04-21: `PRJ-352` artifact-input smoke is green:
  `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-input-path artifacts/behavior_validation/prj352-input.json --artifact-path artifacts/behavior_validation/prj352-output.json --gate-mode ci`
  produced `gate_status=pass`.
- 2026-04-21: `PRJ-353` is complete: regression coverage now pins
  schema-version metadata, normalized gate reason codes, and artifact-input
  failure posture (`missing`, `summary_missing`, `summary_invalid`).
- 2026-04-21: `PRJ-353` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `186 passed`.
- 2026-04-21: `PRJ-354` is complete: planning, operations runbook, testing
  guidance, and context truth now align on behavior-validation artifact
  governance posture (schema versioning, taxonomy, and artifact-input
  evaluation mode).
- 2026-04-21: `PRJ-354` also seeds the next derived queue
  (`PRJ-355..PRJ-358`) for deployment-trigger SLO instrumentation follow-up.
- 2026-04-21: `PRJ-354` validation is recorded as doc-and-context sync plus
  targeted cross-reference checks across
  `docs/planning/next-iteration-plan.md`,
  `docs/planning/open-decisions.md`,
  `docs/operations/runtime-ops-runbook.md`,
  `docs/engineering/testing.md`,
  `.codex/context/TASK_BOARD.md`, and
  `.codex/context/PROJECT_STATE.md`.
- 2026-04-21: `PRJ-355` is complete: Coolify deploy trigger now has a shared
  evidence-capable Python owner with optional machine-readable output for
  webhook invocation metadata and response posture.
- 2026-04-21: `PRJ-355` also aligns PowerShell/bash trigger wrappers onto the
  shared Python entrypoint so deployment evidence semantics remain consistent
  across operator environments.
- 2026-04-21: `PRJ-355` validation is green:
  `.\.venv\Scripts\python .\scripts\trigger_coolify_deploy_webhook.py --help`
  verified argument contract, and
  `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `101 passed`.
- 2026-04-21: `PRJ-356` is complete: release-smoke scripts now support optional
  deployment-trigger evidence verification with freshness and successful
  webhook response checks in both PowerShell and bash paths.
- 2026-04-21: `PRJ-356` preserves backward-compatible smoke behavior when
  deployment evidence is not provided.
- 2026-04-21: `PRJ-356` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `101 passed`.
- 2026-04-21: `PRJ-357` is complete: deployment-trigger SLO instrumentation is
  now regression-covered through a dedicated script suite that pins Coolify
  evidence shape for success/failure paths plus release-smoke optional
  evidence omission, freshness checks, and unsuccessful-webhook failure
  posture.
- 2026-04-21: `PRJ-357` also hardens PowerShell release-smoke compatibility by
  routing deployment-evidence JSON parsing through a version-tolerant
  `ConvertFrom-Json` helper instead of assuming `-Depth` support.
- 2026-04-21: `PRJ-357` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py`
  passed with `6 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `101 passed`.
- 2026-04-21: `PRJ-358` is complete: planning, testing, operations runbook,
  and context truth now align on deployment-trigger evidence capture,
  optional release-smoke evidence verification, and the new regression
  coverage for Group 34.
- 2026-04-21: `PRJ-358` also closes the currently seeded deployment-trigger
  SLO instrumentation lane (`PRJ-355..PRJ-358`); the next execution slice
  should now be derived from planning docs and open decisions because no task
  remains in `READY`.
- 2026-04-21: `PRJ-359` is complete: behavior-validation artifact gate
  evaluation now treats incompatible `artifact_schema_version` major values as
  CI-blocking posture while preserving operator-mode compatibility for local
  inspection of older artifacts.
- 2026-04-21: `PRJ-359` also makes schema-major compatibility machine-visible
  through gate violation context (`artifact_input_schema_version`,
  `artifact_input_schema_major`, `expected_artifact_schema_version`,
  `expected_artifact_schema_major`).
- 2026-04-21: `PRJ-359` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py`
  passed with `12 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `176 passed`.
- 2026-04-21: `PRJ-360` is complete: planning docs, testing guidance, and
  context truth now align on schema-major compatibility governance for
  behavior-validation artifacts.
- 2026-04-21: `PRJ-360` also closes the current compatibility-governance
  follow-up lane; no task remains in `READY`, so the next slice should again
  be derived from planning docs and open decisions.
- 2026-04-21: `PRJ-361` is complete: `/health.attention` now exposes explicit
  production timing baseline posture for burst coalescing (`120ms`), answered
  turn retention (`5s`), and stale-turn cleanup (`30s`) together with
  alignment diagnostics for customized overrides.
- 2026-04-21: `PRJ-361` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py`
  passed with `111 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_main_runtime_policy.py`
  passed with `111 passed`.
- 2026-04-21: `PRJ-362` is complete: planning docs, operations guidance, and
  context truth now align on the attention timing production baseline and
  health-visible alignment posture.
- 2026-04-21: `PRJ-362` also closes the current attention timing baseline
  governance slice; no task remains in `READY`, so the next slice should again
  be derived from planning docs and open decisions.
- 2026-04-21: the next architecture-to-code queue is now seeded through
  `PRJ-378`.
- 2026-04-21: newly planned Groups 37 through 40 now turn the remaining
  architecture follow-ups into executable lanes for connector execution
  policy, future-write typed intents, `ActionDelivery` extensibility, and
  compatibility-sunset readiness.
- 2026-04-21: `PRJ-363` is now the first `READY` task, focused on defining one
  shared connector operation policy before more connector/provider behavior is
  added.
- 2026-04-21: `PRJ-363` is complete: connector operation defaults now have one
  shared owner in `app/core/connector_policy.py` across `calendar`,
  `task_system`, and `cloud_drive`.
- 2026-04-21: `PRJ-363` also moves planner connector intent mode selection onto
  that shared policy owner, replacing open-coded local mode literals while
  preserving the current external side-effect boundary.
- 2026-04-21: `PRJ-363` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
  passed with `91 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `141 passed`.
- 2026-04-21: `PRJ-364` is complete: planning permission gates now consume the
  shared connector-policy helper and action now fails fast on inconsistent
  connector intent mode posture before response delivery.
- 2026-04-21: `PRJ-364` also persists connector guardrail posture in runtime
  memory payloads alongside connector intent update traces for operator triage.
- 2026-04-21: `PRJ-365` is complete: regressions now pin shared-policy-derived
  connector permission gates for read-only, suggestion-only, mutation, and
  proposal-only posture plus action-side connector mode mismatch blocking.
- 2026-04-21: `PRJ-365` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
  passed with `95 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `141 passed`.
- 2026-04-21: `PRJ-366` is complete: architecture, implementation reality,
  planning docs, testing guidance, and context truth now align on the shared
  connector execution-policy baseline and action guardrail posture.
- 2026-04-21: Group 37 (`PRJ-363..PRJ-366`) is now complete.
- 2026-04-21: `PRJ-367` is complete: runtime contracts now define
  `maintain_relation` and `update_proactive_state` as first-class typed
  intent families for future durable writes.
- 2026-04-21: `PRJ-367` also moves proactive planning off generic `noop`
  placeholders when durable proactive-state posture still needs to be
  recorded.
- 2026-04-21: `PRJ-368` is complete: action now executes
  relation-maintenance and proactive follow-up state only from explicit typed
  intents, and proactive paths now persist state through typed ownership even
  when delivery is deferred.
- 2026-04-21: `PRJ-369` is complete: regressions now pin typed future-write
  boundaries across planning, action, runtime, reflection, and scheduler
  paths so relation/proactive durable writes cannot drift back to generic
  mutation posture.
- 2026-04-21: `PRJ-369` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py tests/test_scheduler_worker.py`
  passed with `225 passed`.
- 2026-04-21: `PRJ-370` is complete: architecture, implementation reality,
  planning docs, testing guidance, and context truth now align on expanded
  typed-intent ownership for proactive follow-up state and
  relation-maintenance writes.
- 2026-04-21: Group 38 (`PRJ-367..PRJ-370`) is now complete.
- 2026-04-21: `PRJ-371..PRJ-373` are complete: `ActionDelivery` now carries a
  bounded connector-safe execution envelope, action validates envelope parity
  against planning before side effects, and regressions pin shared handoff
  stability across runtime, graph adapters, and delivery routing.
- 2026-04-21: Group 39 (`PRJ-371..PRJ-374`) is now complete.
- 2026-04-21: Group 39 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
  passed with `138 passed`.
- 2026-04-21: `PRJ-374` is complete: architecture, runtime-reality, planning
  docs, testing guidance, and context truth now align on one shared
  extensible `ActionDelivery` contract with connector-safe execution
  envelopes and bounded routing visibility.
- 2026-04-21: `PRJ-375..PRJ-377` are complete: `/health.runtime_policy` now
  exposes compatibility-sunset readiness for migration-only bootstrap and
  shared debug ingress retirement, startup logs surface the same posture, and
  release smoke verifies evidence presence/coherence before using it as
  release evidence.
- 2026-04-21: Group 40 (`PRJ-375..PRJ-378`) is now complete.
- 2026-04-21: Group 40 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
  passed with `127 passed`.
- 2026-04-21: `PRJ-378` is complete: architecture, operations guidance,
  planning docs, testing guidance, and context truth now align on
  compatibility-sunset readiness governance for migration bootstrap and shared
  debug ingress posture.
- 2026-04-21: no `READY` task remains after Group 40; the next slice should
  be derived again from planning docs and open decisions.
- 2026-04-21: the next architecture-to-code queue is now seeded through
  `PRJ-394`.
- 2026-04-21: newly planned Groups 41 through 44 now turn the remaining
  architecture follow-ups into executable lanes for background adaptive-output
  ownership, durable attention-inbox rollout, role-and-skill capability
  convergence, and retrieval/theta governance.
- 2026-04-21: `PRJ-379` is now the first `READY` task, focused on defining one
  shared adaptive-output contract for reflection/background runtime results
  before durable attention and role/skill follow-ups build on that boundary.
- 2026-04-21: `PRJ-379..PRJ-382` are complete: reflection/background runtime
  now has one explicit adaptive-output summary contract, reflection snapshots
  expose that summary, `/health.reflection` surfaces adaptive-output posture,
  and runtime `system_debug.adaptive_state` carries bounded background-owned
  adaptive visibility without foreground theta mutation.
- 2026-04-21: `PRJ-383..PRJ-386` are complete: durable attention rollout now
  uses explicit `persistence_owner` and `parity_state` semantics, and
  `ATTENTION_COORDINATION_MODE=durable_inbox` preserves the same turn-assembly
  behavior baseline instead of reporting a placeholder blocker posture.
- 2026-04-21: `PRJ-387..PRJ-390` are complete: role selection now emits
  bounded `selected_skills` capability metadata from a shared skill registry,
  planning carries the same selected-skill posture forward, and skills remain
  metadata-only capabilities rather than tool or side-effect owners.
- 2026-04-21: `PRJ-391..PRJ-394` are complete: runtime and `/health` now share
  one retrieval-depth policy snapshot plus bounded theta-influence diagnostics
  across role, motivation, planning, and expression, and `system_debug` also
  exposes adaptive-state metadata for retrieval depth, theta posture, and
  selected/planned skills.
- 2026-04-21: Group 41 through Group 44 are now complete, so no `READY` task
  remains on the task board after `PRJ-394`; the next queue should again be
  derived from planning docs and open decisions.
- 2026-04-21: the next architecture-to-code queue is now seeded through
  `PRJ-410`.
- 2026-04-21: newly planned Groups 45 through 48 now turn the remaining
  architecture follow-ups into executable lanes for role-selection evidence,
  affective rollout policy, reflection scope governance, and durable attention
  contract-store rollout.
- 2026-04-21: `PRJ-395..PRJ-398` are complete: role selection now has a shared
  policy owner (`app/core/role_selection_policy.py`) with explicit
  `selection_reason` and `selection_evidence` metadata on role outputs and
  system-debug surfaces.
- 2026-04-21: Group 45 (`PRJ-395..PRJ-398`) is now complete.
- 2026-04-21: Group 45 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `160 passed`, and
  `.\.venv\Scripts\python -m pytest -q`
  passed with `729 passed`.
- 2026-04-21: `PRJ-399` is now the first `READY` task, focused on explicit
  rollout policy ownership for AI-assisted affective assessment.
- 2026-04-21: `PRJ-399..PRJ-402` are complete: affective assessment now has an
  explicit rollout policy owner with environment-default enablement semantics,
  policy-disabled fallback posture, and machine-visible runtime policy / debug
  snapshots.
- 2026-04-21: Group 46 (`PRJ-399..PRJ-402`) is now complete.
- 2026-04-21: Group 46 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_config.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `199 passed`, and
  `.\.venv\Scripts\python -m pytest -q`
  passed with `734 passed`.
- 2026-04-21: `PRJ-403..PRJ-406` are complete: reflection outputs now share an
  explicit scope owner (`app/core/reflection_scope_policy.py`) that keeps
  goal-progress and milestone conclusions goal-scoped while preserving
  adaptive/affective reflection outputs as user-global by default.
- 2026-04-21: `MemoryRepository`, reflection worker scope resolution, and
  runtime test doubles now canonicalize reflection scopes through the shared
  policy owner, so invalid scoped overrides for global reflection outputs no
  longer leak into runtime preferences or scoped conclusion reads.
- 2026-04-21: Group 47 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
  passed with `172 passed`.
- 2026-04-21: `PRJ-407..PRJ-410` are complete: durable attention now has a
  repository-backed contract store through `aion_attention_turn`,
  `MemoryRepository` attention primitives, and durable-mode coordinator usage
  without changing burst coalescing semantics.
- 2026-04-21: `/health.attention` now exposes repository-backed contract-store
  posture and cleanup visibility (`contract_store_mode`,
  `contract_store_state`, cleanup candidates) instead of parity-only owner
  metadata.
- 2026-04-21: Group 48 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_graph_state_contract.py`
  passed with `122 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py`
  passed with `79 passed`.
- 2026-04-21: the next architecture-to-code queue is now seeded through
  `PRJ-414`.
- 2026-04-21: `PRJ-411` is complete: identity/profile ownership now has one
  shared policy owner in `app/core/identity_policy.py`, and `/health.identity`
  plus runtime `system_debug.adaptive_state.identity_policy` expose the same
  boundary for operator/debug visibility.
- 2026-04-21: `PRJ-411` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `149 passed`.
- 2026-04-21: `PRJ-412` is complete: language continuity posture is now
  explicit through `/health.identity.language_continuity` and runtime
  `system_debug.adaptive_state.language_continuity`.
- 2026-04-21: `PRJ-412` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `149 passed`.
- 2026-04-21: `PRJ-413` is complete: explicit-request posture,
  profile-continuity posture, and unsupported-profile fallback are now
  regression-pinned across language utility and runtime paths.
- 2026-04-21: `PRJ-413` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `165 passed`.
- 2026-04-21: `PRJ-414` is complete: architecture, runtime-reality, planning
  docs, testing guidance, and context truth now align on the shared
  identity-policy owner plus language-continuity diagnostics baseline.
- 2026-04-21: Group 49 (`PRJ-411..PRJ-414`) is now complete.
- 2026-04-21: no seeded `READY` task remains after Group 49; the next
  architecture slice should again be derived from planning docs and open
  decisions.
- 2026-04-22: the next architecture-to-code queue is now seeded through
  `PRJ-442`.
- 2026-04-22: newly planned Groups 50 through 56 now turn the remaining open
  architecture decisions into explicit convergence lanes for runtime topology
  finalization, production-boundary hardening, retrieval plus
  affective-memory productionization, adaptive identity governance,
  goal/task-plus-proposal governance, scheduler and connector capability
  convergence, and deployment standard plus release-reliability closure.
- 2026-04-22: `PRJ-415` is now the first `READY` task, focused on defining the
  production switch criteria for deferred reflection and durable attention
  ownership before any default-mode or release-window change is attempted.
- 2026-04-22: `PRJ-415..PRJ-442` are complete.
- 2026-04-22: Groups 50 through 56 are now complete: runtime topology switch
  policy is explicit, production debug ingress defaults to break-glass-only
  posture when not explicitly overridden, retrieval now supports a local
  provider-owned hybrid embedding path, health/runtime debug expose adaptive
  identity plus planning/connector governance snapshots, and deployment health
  plus release smoke now expose the selected hosting and trigger-SLO baseline.
- 2026-04-22: no seeded `READY` task remains after Group 56; the next
  architecture slice should again be derived from planning docs and any newly
  discovered post-convergence follow-ups.
- 2026-04-22: `PRJ-443` is complete: stale queue-seeding notes from earlier
  convergence waves were pruned from the top-level planning/context surfaces so
  the repo now has one shared post-convergence operating stance instead of a
  stack of historical queue headers.
- 2026-04-22: `PRJ-444..PRJ-447` are complete: shared debug-ingress posture
  vocabulary now uses final route-owned labels
  (`shared_route_compatibility|shared_route_break_glass_only`) across runtime
  policy, response headers, release smoke, and canonical docs.
- 2026-04-22: `PRJ-448..PRJ-451` are complete: `/health.affective` and runtime
  `system_debug.adaptive_state` now distinguish perception-owned affective
  input from final affective assessment resolution, including fallback-reuse
  diagnostics.
- 2026-04-22: `PRJ-452..PRJ-453` are complete: `/health.memory_retrieval` now
  exposes `semantic_embedding_execution_class` so deterministic baseline,
  local provider-owned execution, and fallback-to-deterministic posture are
  machine-visible in one field.
- 2026-04-22: `PRJ-454` is complete: top-level planning/context surfaces now
  consistently describe post-`PRJ-453` follow-up discovery mode and no longer
  keep stale references to the older seeded `PRJ-415..PRJ-442` queue as if it
  were still the current planning baseline.
- 2026-04-22: `PRJ-455..PRJ-457` are complete: canonical attention docs,
  config guidance, ops runbook notes, and planning/context surfaces now align
  on repository-backed `aion_attention_turn` durable inbox posture and the
  exact `/health.attention` contract-store visibility fields used for
  operator triage.
- 2026-04-22: `PRJ-458..PRJ-460` are complete: runtime reality now includes
  `aion_subconscious_proposal` in the live persisted schema inventory, and the
  runbook plus planning/context surfaces now describe the concrete operator
  meaning of post-convergence health surfaces for planning, connectors,
  adaptive identity governance, and deployment.
- 2026-04-22: `PRJ-461..PRJ-463` are complete: the runbook and
  planning/context surfaces now treat `/health.affective` and
  `memory_retrieval.semantic_embedding_execution_class` as explicit
  operator-facing diagnostics for empathy triage and retrieval execution
  posture.
- 2026-04-22: architecture-conformance analysis is now refreshed against
  canonical docs plus live runtime code. The highest-priority remaining gap is
  migration parity between `app/memory/models.py` and Alembic revisions,
  followed by canonical-doc consistency cleanup and productionization of still
  rollout-shaped subsystems (connector execution, retrieval provider path,
  background worker topology, proactive cadence, role/skill maturity, and
  behavior-validation breadth).
- 2026-04-22: a new post-convergence queue is now seeded through `PRJ-491`,
  starting with Group 63 for migration parity and schema governance.
- 2026-04-22: `PRJ-464..PRJ-467` are complete: Alembic head now includes
  durable attention (`aion_attention_turn`) and subconscious proposal
  (`aion_subconscious_proposal`) tables, and schema-baseline regressions now
  exercise a fresh `alembic upgrade head` instead of trusting metadata alone.
- 2026-04-22: migration-first schema ownership is now explicit as a release
  truth for the full current model set, reducing deployment drift between live
  runtime tables and bootstrap path.
- 2026-04-22: the next `READY` lane is Group 64 (`PRJ-468..PRJ-471`),
  focused on canonical architecture-doc consistency after schema truth was
  restored.
- 2026-04-22: `PRJ-468..PRJ-471` are complete: canonical docs no longer carry
  a competing older flow where `action` precedes `expression`, and action docs
  now distinguish action-owned side effects from runtime-owned post-action
  follow-ups such as episodic memory persistence and reflection enqueue.
- 2026-04-22: `docs/README.md` and `docs/overview.md` now explicitly direct
  readers to `02_architecture.md`, `15_runtime_flow.md`, and
  `16_agent_contracts.md` as the canonical ordering/ownership set.
- 2026-04-22: the next `READY` lane is Group 65 (`PRJ-472..PRJ-475`),
  focused on connector execution productionization.
- 2026-04-22: `PRJ-472..PRJ-475` are complete: the first live provider-backed
  connector path is now explicit and implemented through ClickUp task
  creation, while calendar, cloud-drive, and remaining task-system operations
  stay policy-only on purpose.
- 2026-04-22: action now executes
  `ExternalTaskSyncDomainIntent(operation="create_task", provider_hint="clickup")`
  through a dedicated provider adapter when `CLICKUP_API_TOKEN` and
  `CLICKUP_LIST_ID` are configured, without relaxing the existing
  `planning -> expression -> action` boundary or shared connector policy.
- 2026-04-22: `/health.connectors.execution_baseline` now exposes one machine-
  visible connector execution owner plus readiness posture for the selected
  ClickUp live path (`provider_backed_ready|credentials_missing`).
- 2026-04-22: Group 65 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  passed with `181 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
  passed with `184 passed`.
- 2026-04-22: the next `READY` lane is Group 66 (`PRJ-476..PRJ-479`),
  focused on retrieval provider completion.
- 2026-04-22: `PRJ-476..PRJ-479` are complete: the target provider-owned
  retrieval baseline is now explicit as OpenAI API embeddings when configured,
  retrieval materialization has a live provider-owned path, and `/health`
  exposes machine-visible production-baseline posture for retrieval rollout.
- 2026-04-22: Group 66 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `163 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_runtime_policy.py`
  passed with `104 passed`.
- 2026-04-22: the next `READY` lane is Group 67 (`PRJ-480..PRJ-483`),
  focused on background worker externalization.
- 2026-04-22: `PRJ-480..PRJ-483` are complete: deferred reflection
  externalization now has one explicit policy owner, one canonical
  queue-drain entrypoint, and release-smoke-visible external-driver posture
  instead of depending on app-local worker assumptions.
- 2026-04-22: Group 67 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_reflection_worker.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
  passed with `153 passed`, and
  `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
  passed with `98 passed`.
- 2026-04-22: the next `READY` lane is Group 68 (`PRJ-484..PRJ-487`),
  focused on proactive runtime activation.
- 2026-04-22: `PRJ-484..PRJ-487` are complete: proactive runtime now has one
  explicit policy owner for cadence baseline and anti-spam thresholds,
  in-process scheduler ownership can emit bounded proactive wakeups through
  the normal runtime path, `/health.proactive` exposes live proactive posture,
  and behavior validation now covers delivery-ready versus anti-spam-blocked
  proactive outcomes.
- 2026-04-22: Group 68 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `167 passed`, and
  `.\scripts\run_behavior_validation.ps1 -GateMode operator`
  passed with `7 passed`.
- 2026-04-22: the next `READY` lane is Group 69 (`PRJ-488..PRJ-491`),
  focused on freezing the long-term role-versus-skill boundary and widening
  behavior-validation proof for the post-convergence runtime.
- 2026-04-22: `PRJ-488..PRJ-491` are complete: skills remain an explicit
  metadata-only capability layer, `/health.role_skill` and runtime debug
  surfaces expose the same boundary, and behavior validation now covers
  role/skill, connector posture, proactive cadence, and deferred reflection
  expectations in one CI-ready artifact flow.
- 2026-04-22: Group 69 validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `236 passed`, and
  `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
  passed with `8 passed`.
- 2026-04-22: no seeded `READY` task remains after `PRJ-491`; the queued
  post-convergence architecture follow-ups are fully complete and the next
  slice should be derived only from new analysis, drift, or runtime evidence.
- 2026-04-22: architecture-planning follow-up has now seeded a new queue
  through `PRJ-515`, focused on remaining transitional runtime surfaces rather
  than broad convergence scaffolding.
- 2026-04-22: the new hardening lanes target six concrete gaps still visible
  against the canonical architecture and runtime reality:
  dedicated-admin debug ingress closure, external scheduler ownership,
  connector-read posture beyond ClickUp mutation-only baseline, retrieval
  lifecycle/source-rollout closure, reflection-worker supervision, and
  observability/export evidence.
- 2026-04-22: `PRJ-492` is now the first `READY` task, focused on freezing the
  dedicated-admin debug-ingress target and the retirement checklist for shared
  compatibility ingress before deeper runtime hardening proceeds.
- 2026-04-22: `PRJ-492` is complete: debug ingress now has one explicit shared
  policy owner in `app/core/debug_ingress_policy.py` that records the dedicated
  internal admin route as the target posture, keeps `/event/debug` and
  `/event?debug=true` as temporary compatibility surfaces only, and freezes the
  retirement checklist for shared ingress.
- 2026-04-22: `PRJ-493` is complete: `/health.runtime_policy` and release smoke
  now expose one machine-visible dedicated-admin debug posture through
  `event_debug_admin_*` fields plus explicit shared-ingress retirement blockers
  and readiness state.
- 2026-04-22: `PRJ-493` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
  passed with `98 passed`.
- 2026-04-22: `PRJ-494` is complete: production startup now emits one shared
  `runtime_policy_debug_ingress_hint` for the dedicated-admin debug target,
  and the runtime ops runbook plus release smoke consume the same
  `event_debug_admin_*` and shared-retirement fields.
- 2026-04-22: `PRJ-494` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed with `119 passed`.
- 2026-04-22: `PRJ-495` is complete: architecture contracts, runtime-reality
  notes, testing guidance, ops guidance, and planning/context truth now
  describe the same dedicated-admin debug target plus shared-retirement
  blocker fields.
- 2026-04-22: Group 70 (`PRJ-492..PRJ-495`) is now complete.
- 2026-04-22: `PRJ-496` is complete: the repo now records one explicit
  production external-scheduler policy owner in
  `app/core/external_scheduler_policy.py`, with `externalized` as the target
  cadence owner posture and app-local scheduler as fallback only.
- 2026-04-22: `PRJ-497` is complete: the repo now provides canonical
  maintenance/proactive external cadence entrypoints
  (`scripts/run_maintenance_tick_once.*`, `scripts/run_proactive_tick_once.*`)
  and `SchedulerWorker` exposes explicit external-owner execution methods.
- 2026-04-22: `PRJ-497` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
  passed with `170 passed`.
- 2026-04-22: `PRJ-498` is complete: `/health.scheduler.external_owner_policy`,
  startup logs, and release smoke now expose the same external cadence-owner
  policy with target entrypoints and baseline readiness posture.
- 2026-04-22: `PRJ-498` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py`
  passed with `120 passed`.
- 2026-04-22: `PRJ-499` is complete: implementation reality, ops guidance,
  testing guidance, planning, and context truth now describe the same
  external cadence-owner baseline with canonical maintenance/proactive
  entrypoints and explicit in-process fallback posture.
- 2026-04-22: Group 71 (`PRJ-496..PRJ-499`) is now complete.
- 2026-04-22: `PRJ-500` is complete: the next live read-capable connector
  expansion path is now explicitly selected as `task_system:list_tasks` for
  ClickUp, while calendar and cloud-drive remain policy-only until narrower
  read-boundary contracts are designed.
- 2026-04-22: `PRJ-501` is complete: ClickUp now has a provider-backed
  read-capable execution path for `task_system:list_tasks`, executed from
  explicit read-only typed intents before delivery while preserving the
  planning/action boundary.
- 2026-04-22: `PRJ-502` is complete: `/health.connectors.execution_baseline`
  now distinguishes ClickUp mutation and read-capable live paths from the
  remaining policy-only connector families through one shared execution
  baseline surface.
- 2026-04-22: `PRJ-503` is complete: contracts, runtime reality, ops notes,
  testing guidance, and planning/context truth now describe the same expanded
  ClickUp task-system baseline for both create and list execution.
- 2026-04-22: Group 72 (`PRJ-500..PRJ-503`) is now complete.
- 2026-04-22: `PRJ-504` is complete: retrieval lifecycle now has one explicit
  policy owner for target provider baseline, transition owner, compatibility
  fallback, steady-state refresh, and source-rollout completion posture.
- 2026-04-22: `PRJ-505` is complete: `/health.memory_retrieval` now exposes
  one retrieval lifecycle owner plus provider drift posture, pending lifecycle
  gaps, and baseline alignment state.
- 2026-04-22: `PRJ-506` is complete: release smoke now validates retrieval
  lifecycle owner and drift/alignment posture from `/health.memory_retrieval`,
  and runtime regression coverage now pins that the local-hybrid transition
  owner still exercises the active hybrid retrieval path.
- 2026-04-22: `PRJ-507` is complete: implementation reality, ops guidance,
  testing guidance, planning, and context truth now describe one shared
  retrieval steady-state lifecycle baseline with machine-visible
  provider-drift, alignment, and pending-gap posture.
- 2026-04-22: Group 73 (`PRJ-504..PRJ-507`) is now complete.
- 2026-04-22: `PRJ-508` is complete: deferred reflection supervision now has
  one shared policy owner in `app/core/reflection_supervision_policy.py` for
  target runtime mode, external queue-drain ownership, durable retry
  ownership, queue-health states, and recovery actions.
- 2026-04-22: `PRJ-508` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_reflection_supervision_policy.py`
  passed.
- 2026-04-22: `PRJ-509` is complete: `/health.reflection` now exposes one
  shared supervision snapshot with queue-health state, blocking signals, and
  recovery actions for deferred reflection execution.
- 2026-04-22: `PRJ-509` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_api_routes.py`
  passed.
- 2026-04-22: `PRJ-510` is complete: startup logs and release smoke now
  consume the same deferred-reflection supervision contract for queue-health
  state, readiness posture, blocking signals, and recovery actions.
- 2026-04-22: `PRJ-510` validation is green:
  `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
  passed.
- 2026-04-22: `PRJ-511` is complete: canonical contracts, runtime reality,
  ops guidance, testing guidance, planning, and context truth now describe one
  shared supervised deferred-reflection baseline with queue-health,
  blocking-signal, and recovery-action posture.
- 2026-04-22: Group 74 (`PRJ-508..PRJ-511`) is now complete.
- 2026-04-22: `PRJ-512` is complete: the repo now has one shared
  `incident_evidence_export_policy` owner in
  `app/core/observability_policy.py`, and `/health.observability` exposes the
  minimum exportable incident-evidence contract together with the remaining
  machine-readable export gaps.
- 2026-04-22: `PRJ-513` is complete: debug responses now expose
  `incident_evidence` from the shared observability owner, carrying stage
  timings plus machine-readable policy-posture snapshots for runtime policy,
  retrieval, scheduler, reflection supervision, and connector execution.
- 2026-04-22: `/health.observability` now marks exportable incident evidence
  as ready, and release smoke can validate that exported evidence directly in
  debug-mode smoke runs.
- 2026-04-22: `PRJ-514` is complete: release smoke now validates exported
  `incident_evidence` directly in debug mode, and behavior-validation
  artifacts can optionally ingest incident-evidence JSON through the shared
  gate flow.
- 2026-04-22: `PRJ-515` is complete: canonical architecture docs,
  runtime-reality notes, ops guidance, testing guidance, planning, and context
  truth now describe the same observability export baseline for
  `/health.observability`, debug-response `incident_evidence`, and validation
  or smoke consumption.
- 2026-04-22: Group 75 (`PRJ-512..PRJ-515`) is now complete.
- 2026-04-22: no seeded `READY` task remains after the observability export
  lane; the next task should again be derived from fresh runtime or
  operational analysis.

## Working Agreements

- Keep task board and project state synchronized.
- Keep planning docs synchronized with task board.
- Keep changes small and reversible.
- Validate touched areas before marking done.
- Keep repository artifacts in English.
- Communicate with users in their language.
- Delegate with explicit ownership and avoid overlapping subagent write scope.
- Use the default loop:
  `plan -> implement -> test -> architecture review -> sync context`.
- Treat deployment docs and smoke checks as part of done-state for runtime
  changes.

## Canonical Context

- `.codex/context/PROJECT_STATE.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/LEARNING_JOURNAL.md`
- `.agents/workflows/general.md`
- `.agents/workflows/subagent-orchestration.md`

## Canonical Docs

- `docs/README.md`
- `docs/overview.md`
- `docs/architecture/02_architecture.md`
- `docs/architecture/15_runtime_flow.md`
- `docs/architecture/16_agent_contracts.md`
- `docs/architecture/17_logging_and_debugging.md`
- `docs/architecture/29_runtime_behavior_testing.md`
- `docs/architecture/26_env_and_config.md`
- `docs/architecture/27_codex_instructions.md`
- `docs/engineering/local-development.md`
- `docs/engineering/testing.md`
- `docs/planning/next-iteration-plan.md`
- `docs/planning/open-decisions.md`
- `docs/operations/runtime-ops-runbook.md`
- `docs/ux/canonical-web-screen-reference-set.md`

## Optional Project Docs

- Add only if the repository truly needs them.
- Record their canonical paths here once they exist.
- `docs/implementation/runtime-reality.md`

## Current Repo Topology

- `backend/` is now the canonical home of the Python runtime, tests, scripts,
  Alembic config, and package metadata.
- `web/` is reserved for the browser client workspace.
- `mobile/` is reserved for the mobile client workspace.
- root-level files remain shared repo, deployment, and discovery surfaces.
- 2026-04-25: `PRJ-708` hardened shell hierarchy and badge semantics in the
  web client. Decorative badges were removed or converted into stat/detail
  tiles across login, route summary, settings, tools, and personality, while
  true tool-state chips were preserved. Refreshed screenshot proof was stored
  in `.codex/artifacts/prj708-visual-hierarchy-proof/`.
- 2026-04-28: `PRJ-743` continued the canonical flagship parity loop for
  `dashboard`, `chat`, and `personality`. The latest slice refined dashboard
  guidance tiering, reduced chat topbar control density, and introduced an
  anchored highlight hierarchy in the personality side column so the flagship
  shell reads closer to the canonical references before the next deploy
  compare-pass.
- 2026-04-28: the flagship convergence lane also tightened closure and mobile
  compression:
  - `dashboard` now uses a calmer bridge from hero to lower cards and a more
    explicit scenic ending
  - `chat` portrait crop and planning inset were rebalanced for both desktop
  and mobile
  - `personality` mobile callouts were compressed inward to preserve a more
    ceremonial figure stage
- 2026-04-28: the latest flagship polish pass then tuned route proportions:
  - `dashboard` now gives slightly more authority to the center hero scene
  - `chat` now reserves more desktop width for transcript reading and uses more
    intentional message-width hierarchy
  - `personality` now uses a slightly taller embodied stage with tighter
    mobile callout compression
  - validation after this pass:
    - `Push-Location .\web; npm run build; Pop-Location`
    - result: passed
  - `PRJ-772` is closed locally with deploy-backed screenshot comparison left
    to the broader `PRJ-743` parity loop
- 2026-04-28: another flagship calmness pass then refined shell and route
  pacing:
  - the shared desktop chrome is slightly narrower and quieter, so the route
    surfaces retain first-read authority
  - `dashboard` now uses denser sidebar/stage spacing for a more unified
    flagship composition
  - `chat` now tightens transcript rhythm and support-column padding so the
    conversation remains the dominant instrument
  - `personality` now uses a tighter side stack so the embodied preview keeps
    its ceremonial center
  - validation after this pass:
    - `Push-Location .\web; npm run build; Pop-Location`
    - result: passed
- 2026-04-28: a further flagship material pass then tightened scenic closure
  and route instrumentation:
  - `dashboard` now uses a taller and more editorial scenic closure with a
    calmer copy width
  - `chat` now joins action tray, composer, and feature strip more tightly so
    the conversation tool reads as one instrument
  - `personality` now uses slightly lighter callouts and longer connector
    lines for a clearer embodied explanation
  - validation after this pass:
    - `Push-Location .\web; npm run build; Pop-Location`
    - result: passed
- 2026-04-28: another flagship parity pass then improved one-screen read and
  embodied continuity:
  - `dashboard` lower rhythm and summary closure were tightened so the route
    stays closer to a single flagship read
  - `chat` preview transcript now feels more designed and less fallback-like
  - `personality` now links the embodied figure and timeline more clearly
    through a tighter hero shell and integrated timeline panel treatment
  - validation after this pass:
    - `Push-Location .\web; npm run build; Pop-Location`
    - result: passed
- 2026-04-28: a dashboard-specific compaction pass then reduced one of the
  biggest remaining canonical drifts:
  - conversation-channel status was folded into the guidance column instead of
    occupying its own full-width band
  - dashboard flow notes were reduced so the route finishes more like one
    composed flagship overview
  - validation after this pass:
    - `Push-Location .\web; npm run build; Pop-Location`
    - result: passed
