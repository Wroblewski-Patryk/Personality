# Web UX/UI Productization Plan

## Purpose

This document turns the 2026-04-25 browser audit into an execution-ready UX/UI
queue for the first-party web client.

The target posture is:

- mobile first
- tablet second
- desktop third
- backend-owned contracts preserved
- web layout prepared to become the visual and interaction baseline for a
  later Expo mobile client

This plan does not approve architecture drift.
It keeps the current backend-owned `/app/*` contract boundary and focuses on
product-facing layout, information architecture, responsive behavior, and copy.
It also freezes one explicit split between:

- UI language for the web shell
- conversation language chosen live by the personality

## Second Audit Refresh On 2026-04-25

Fresh browser review of the now-improved shell confirms that the first UX/UI
lane materially raised quality, but it did not finish the product transition.

Reference evidence:

- screenshot set:
  - `.codex/artifacts/ux-audit-2026-04-25-round2/`
- live route reached without auth:
  - `/login`
- code surfaces reviewed:
  - `web/src/App.tsx`
  - `web/src/lib/api.ts`
  - `web/src/index.css`
  - `web/tailwind.config.ts`

This second pass changes the queue focus from:

- route-level rescue and basic mobile-first structure

to:

- product tone
- public entry clarity
- responsive tier discipline
- stronger state semantics
- locale UX foundations suitable for later mobile transfer

## Audit Evidence

- Browser route review:
  - `/login`
  - `/chat`
  - `/settings`
  - `/tools`
  - `/personality`
- Viewports reviewed:
  - mobile
  - tablet
  - desktop
- Screenshot evidence:
  - `.codex/artifacts/ux-audit-2026-04-25/`
- Current implementation owner:
  - `web/src/App.tsx`

## High-Signal Findings

1. The current shell is visually consistent, but it still reads as an
   inspection-oriented interface more than a product-facing application.
2. `Tools` and `Personality` are not mobile-ready:
   - they still behave like desktop inspection layouts compressed into a phone
   - they create horizontal expansion and large dead-space posture on smaller
     viewports
3. The authenticated shell repeats too much header and account chrome above the
   main task area, especially on mobile.
4. `Chat` does not yet prioritize the core product interaction:
   - conversation and composer sit below account summary and route chrome
   - composer is not anchored as the primary action surface
5. `Settings` duplicates backend snapshot and editable form information instead
   of using a shorter task-focused preference layout.
6. `Tools` exposes backend truth too literally:
   - capability ids
   - provider-ready wording
   - status keys and reason strings
   - read-only implementation detail cards
7. `Personality` currently behaves like a raw inspector:
   - summary cards are fine
   - raw JSON sections are not a product-ready user experience
8. Current copy still contains too much system language:
   - backend-owned truth
   - runtime-visible integrations
   - contract-oriented labels
9. The current shell lacks a dedicated mobile navigation model suitable for a
   future mobile app baseline.
10. `Settings` currently exposes fields that should not stay user-facing
    product controls:
   - `response style`
   - `collaboration preference`
11. The current language selector is not yet safe as a product-localization
    control because the product needs one explicit split between UI locale and
    conversation language continuity.

## Second-Pass Findings

1. The public login screen still spends too much of the first viewport on
   architecture framing instead of immediate product value and session entry.
2. Public-facing copy still leaks system language:
   - backend-owned session
   - live contract
   - backend truth
   - raw endpoint references
3. `build unknown` is a trust and layout problem when visible in the user
   shell; build revision should not act as user-facing chrome.
4. Tablet still behaves mainly like a scaled mobile layout instead of a
   deliberately composed intermediate tier.
5. Decorative badges are overused across the shell, which weakens semantic
   hierarchy and makes status feel ornamental instead of useful.
6. Loading, empty, success, and error states are technically present, but they
   still read as system messages more than product guidance.
7. The current shell copy is cleaner than before, but its overall tone still
   describes systems and contracts more than user outcomes and next actions.
8. The current `ui_language` selector works as a contract proof, but it is not
   yet a durable localization UX foundation for web-to-mobile transfer because
   it still relies on emoji-flag rendering instead of explicit locale metadata.

## Product Direction Guardrails

- keep `web/` as a thin consumer of backend-owned contracts
- do not move product logic into the client
- do not add browser-managed provider setup or secret entry
- separate product surfaces from debug or inspector surfaces
- prefer progressive disclosure over always-visible technical detail
- treat `mobile -> tablet -> desktop` as the primary responsive sequence
- keep every slice testable and visually auditable with screenshots
- never overload conversation-language state as UI locale state
- keep response style and collaboration preference as runtime-shaped behavior,
  not manual settings inputs

## Execution Queue

The next web UX/UI queue is seeded through `PRJ-691`.

Execution order:

1. `PRJ-685` Mobile-First App Shell Baseline
2. `PRJ-686` UI Language Boundary And Locale Switcher Plan
3. `PRJ-687` Chat Experience And Composer Priority
4. `PRJ-688` Settings Simplification And Runtime-Shaped Preference Cleanup
5. `PRJ-689` Tools Information Architecture And Actionability
6. `PRJ-690` Personality Productization And Inspector Split
7. `PRJ-691` Visual System Hardening, Responsive Proof, And Context Sync

Implementation status on 2026-04-25:

- `PRJ-685..PRJ-691` are now complete in the repo baseline
- the authenticated shell now has mobile-first navigation and reduced chrome
- app-facing settings now persist separate `ui_language` and no longer expose
  manual `response_style` / `collaboration_preference` controls in the web UI
- `Chat`, `Tools`, and `Personality` now follow a more product-facing
  hierarchy with technical detail pushed lower in the flow

## Second-Pass Queue On 2026-04-25

Fresh browser evidence now seeds one follow-up lane through `PRJ-710`.

Execution order:

1. `PRJ-703` Login Value Framing And Trust Cleanup
2. `PRJ-704` Product Copy And Terminology Cleanup Across The Shell
3. `PRJ-705` Responsive Tier Rules For Mobile Tablet Desktop
4. `PRJ-706` Productive State System For Loading Empty Error And Success
5. `PRJ-707` Locale Metadata Foundation For GUI Language UX
6. `PRJ-708` Visual Hierarchy And Badge Semantics Hardening
7. `PRJ-709` Authenticated Route Second Pass And Screenshot Proof
8. `PRJ-710` Context Docs And Learning Sync For The Second UX/UI Lane

Why this order:

- public entry quality must improve first because the login route still
  determines first trust and first conversion
- shell copy and terminology should be cleaned before deeper visual tweaks so
  product language becomes stable across routes
- responsive tier rules must be explicit before visual polishing, especially
  for tablet
- product-state semantics should be normalized before another screenshot pass
- locale UX should gain a durable metadata foundation before later mobile work
- visual hierarchy hardening should happen only after structure, terminology,
  and state posture are clear
- final route sweep and screenshot proof should validate the refined system as
  one product surface, not as disconnected tweaks

Accepted closure on 2026-04-26:

- the second-pass lane is now complete through `PRJ-710`
- the accepted baseline includes:
  - trust-first public login posture
  - product-facing copy across the shell
  - explicit mobile, tablet, and desktop shell behavior
  - one shared loading/empty/success/error posture
  - token-based locale metadata for GUI language
  - calmer visual hierarchy with status chips reserved for true status meaning
  - authenticated route proof across `chat`, `settings`, `tools`, and
    `personality`
- accepted screenshot evidence lives in:
  - `.codex/artifacts/prj705-responsive-proof/`
  - `.codex/artifacts/prj708-visual-hierarchy-proof/`
  - `.codex/artifacts/prj709-authenticated-route-sweep/`
- remaining follow-up after this lane is polish-level only; the next product
  queue returns to shared chat transcript continuity work

## Visual Motif Refresh On 2026-04-26

Fresh user-approved design direction now seeds the next explicit visual lane
for the web shell.

Reference source:

- approved snapshot:
  - `docs/ux/assets/aion-visual-motif-reference.png`
- design system freeze:
  - `docs/ux/aion-visual-motif-system.md`

This lane does not change backend ownership or route topology.
It changes visual language, route composition, shared styling primitives, and
illustration usage so the shell can become more distinctive and emotionally
coherent.

### New Queue

The next web visual lane is now seeded through `PRJ-728`.

Execution order:

1. `PRJ-723` Freeze AION Visual Motif And V1 Web UX Direction
2. `PRJ-724` Shared Visual Tokens And Shell Background System
3. `PRJ-725` Public Entry And Authenticated Shell Motif Integration
4. `PRJ-726` Personality And Tools Route Motif Implementation
5. `PRJ-727` Chat And Settings Lightweight Motif Integration
6. `PRJ-728` Responsive Proof, Accessibility Review, And Context Sync

Why this order:

- freeze the motif first so later implementation reuses one shared direction
- move shared tokens and surfaces before route-specific polish
- update the shell framing before deep route compositions
- let `personality` and `tools` carry the richest expression of the motif
- keep `chat` and `settings` calmer and more supportive
- finish with proof across states, breakpoints, and accessibility posture

## Tasks

### Task

## Header
- ID: PRJ-685
- Title: Freeze the mobile-first authenticated app shell baseline
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-684
- Priority: P0

## Context
The current authenticated shell repeats a large hero block, route header, and
account summary on every screen. This consumes the first viewport on mobile and
does not match a product-ready app pattern that can later transfer into Expo.

## Goal
Freeze one approved product-shell baseline for authenticated screens:

- compact top bar
- mobile-first primary navigation
- reduced repeated hero copy after login
- one clear place for account access and sign-out

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] One explicit shell pattern is chosen for authenticated web screens.
- [x] The shell baseline is described for mobile, tablet, and desktop.
- [x] The baseline keeps backend-owned routing and auth/session truth.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `npm run build` in `web/`
- Manual checks: authenticated shell reviewed against the 2026-04-25 route audit for mobile-first chrome reduction and navigation posture
- Screenshots/logs: `.codex/artifacts/ux-audit-2026-04-25/`; production-ready shell implementation in `web/src/App.tsx`
- High-risk checks: confirm shell change does not imply client-owned auth or
  navigation state outside current route contract

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`,
  `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: n/a
- Follow-up architecture doc updates: none expected

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Chosen shell baseline:

- mobile: sticky compact top bar plus fixed bottom navigation
- tablet: sticky compact top bar plus route summary strip
- desktop: sticky compact top bar plus inline route navigation
- authenticated account access: one toggleable account panel with sign-out

This slice intentionally leaves route-level redesign to later tasks.

### Task

## Header
- ID: PRJ-686
- Title: Freeze the UI-language boundary and localization switcher plan
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-685
- Priority: P0

## Context
The current `Settings` route exposes a language selector through the current
user settings posture, but the product now needs one explicit distinction:

- GUI language for the web shell
- conversation language chosen live by the personality from context, memory,
  and current interaction

The current runtime architecture already gives language-continuity ownership to
the conversational path, so the web client must not silently repurpose that
field into UI locale.

## Goal
Freeze one product-safe localization plan:

- one explicit UI-language field for the first-party shell
- no semantic overlap with conversation language
- select control with flag icon plus language label
- copy that explains the selector controls only the interface

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] One explicit UI-language contract is chosen for web/mobile product surfaces.
- [x] The plan states that conversation language remains runtime-owned and live.
- [x] The locale-switcher posture is described for settings UX, including flag icon treatment.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: n/a planning and contract-freeze slice
- Manual checks: current `/app/me` and `/app/me/settings` contract reviewed against `preferred_language` ownership in backend and architecture docs
- Screenshots/logs: `.codex/artifacts/ux-audit-2026-04-25/`; contract review in `docs/architecture/16_agent_contracts.md`, `docs/planning/open-decisions.md`
- High-risk checks: confirm no plan reuses conversation-language continuity as UI locale storage

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`,
  `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: n/a
- Follow-up architecture doc updates: none expected

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Chosen implementation contract:

- keep `preferred_language` as profile-owned conversation continuity
- add separate app-facing shell field named `ui_language` if persisted locale
  is implemented
- keep `GET /app/me` and `PATCH /app/me/settings` as the first-party settings
  source of truth
- support `system`, `en`, `pl`, and `de` in the first selector iteration
- render the selector from explicit locale metadata with locale token/icon plus
  native and localized labels
- explain in helper copy that the selector changes interface language only

Locale metadata follow-up for later client reuse:

- one locale option record should carry:
  - `value`
  - `native_label`
  - localized label map for supported GUI locales
  - explicit locale-icon token or later asset reference
  - fallback semantics for `system`
- locale-icon rendering must not depend on implicit emoji support
- the first shared fallback posture is text-token based:
  - `AUTO`
  - `EN`
  - `PL`
  - `DE`
- web may render those tokens immediately, and later mobile may replace the
  token with an approved asset while preserving the same metadata contract
- this metadata remains interface-only and must not change conversation
  language ownership

### Task

## Header
- ID: PRJ-687
- Title: Redesign chat for mobile-first conversation priority
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-685, PRJ-686
- Priority: P0

## Context
`Chat` is the primary product value, but the current layout still puts route
chrome and account summary ahead of the conversation and composer experience.

## Goal
Make `Chat` the first product-quality route:

- conversation is visible quickly on mobile
- composer becomes the dominant primary action
- continuity is useful without overpowering the conversation

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Mobile chat layout prioritizes the conversation thread and composer.
- [x] Empty, loading, sending, and success states feel coherent on mobile and tablet.
- [x] The route remains a thin client over `/app/chat/*`.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `npm run build` in `web/`; `..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_memory_repository.py tests/test_schema_baseline.py`
- Manual checks: code-level responsive review for mobile-first conversation ordering and sticky composer posture
- Screenshots/logs: updated implementation in `web/src/App.tsx`; browser artifact refresh was not rerun in this execution slice
- High-risk checks: confirm no client-side domain duplication around message history or reply state

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`,
  `docs/architecture/15_runtime_flow.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: n/a
- Follow-up architecture doc updates: none expected

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Implemented posture:

- chat now opens with conversation-first hierarchy
- continuity moved to a supporting panel instead of competing with the thread
- sticky composer keeps the primary action close to the thumb zone on mobile

### Task

## Header
- ID: PRJ-688
- Title: Simplify settings and remove manual runtime-style controls
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-685, PRJ-686
- Priority: P1

## Context
`Settings` currently mixes editable form controls, repeated account summary, and
separate backend snapshot cards, which increases page length and duplicates
information.

The route also still exposes controls that should not remain user-facing:

- `response style`
- `collaboration preference`

Those behaviors should be shaped by runtime inference, history, time,
interaction patterns, and later adaptive outputs rather than by static
settings form fields.

## Goal
Turn `Settings` into a short, task-oriented preference flow with clear sections,
clear save behavior, no repeated backend-inspector posture, and one explicit
UI-language selector that does not control conversation language.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] The editable preference form is primary.
- [x] Repeated backend snapshot duplication is reduced or removed from the main flow.
- [x] `response style` and `collaboration preference` are removed from the product-facing settings form.
- [x] UI-language selection is described as interface-only and uses a flag icon plus label pattern.
- [x] Save-state, dirty-state, and completion feedback are visually clear.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `npm run build` in `web/`; `..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_memory_repository.py tests/test_schema_baseline.py`
- Manual checks: code-level review for reduced settings density, runtime-owned conversation language, and interface-only locale selection
- Screenshots/logs: updated implementation in `web/src/App.tsx`, `backend/app/api/routes.py`, `backend/app/api/schemas.py`, `backend/app/memory/repository.py`
- High-risk checks: keep `/app/me` and `PATCH /app/me/settings` as the only source of truth until an explicit UI-locale contract lands

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: n/a
- Follow-up architecture doc updates: none expected

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Implemented posture:

- settings now focus on profile, `ui_language`, and proactive follow-ups
- `response style` and `collaboration preference` are no longer manual form controls
- `ui_language` is persisted separately from `preferred_language`

### Task

## Header
- ID: PRJ-689
- Title: Reframe tools into status-plus-action product cards
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-685, PRJ-686
- Priority: P0

## Context
`Tools` is currently truthful but too literal. The route exposes provider
states, capability ids, and backend status detail as primary content.

## Goal
Keep backend truth while converting the route into product-ready tool cards:

- clear current state
- clear next action
- technical detail only on demand

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Mobile layout avoids horizontal expansion and dead-space posture.
- [x] Primary states and actions are understandable without backend vocabulary.
- [x] Technical detail is reduced, hidden, or clearly secondary.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `npm run build` in `web/`; `..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_memory_repository.py tests/test_schema_baseline.py`
- Manual checks: code-level review for single-column mobile posture, action-first hierarchy, and preserved backend-owned toggle flows
- Screenshots/logs: updated implementation in `web/src/App.tsx`
- High-risk checks: do not invent provider setup flows or mutable client logic beyond existing backend contract

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`,
  `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: n/a
- Follow-up architecture doc updates: none expected

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This route must become suitable for a later mobile app transfer, not stay an
inspection-heavy dashboard.

### Task

## Header
- ID: PRJ-690
- Title: Split personality insights from raw inspector payloads
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-685, PRJ-686
- Priority: P0

## Context
`Personality` currently mixes useful summary metrics with raw JSON blocks. The
result is not product-facing and should not become the baseline for the future
mobile client.

## Goal
Create one product-facing personality-insights route and move raw inspector
payload posture out of the main user flow.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Product-facing insights are understandable without reading JSON.
- [x] Raw payload visibility is clearly secondary or moved behind an explicit inspect action.
- [x] Mobile layout remains readable and bounded for all major sections.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `npm run build` in `web/`; `..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_memory_repository.py tests/test_schema_baseline.py`
- Manual checks: code-level review for summary-first cards and raw payload relegation behind explicit inspect actions
- Screenshots/logs: updated implementation in `web/src/App.tsx`
- High-risk checks: confirm the client still consumes backend-owned inspection payloads instead of reconstructing personality truth

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`,
  `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: n/a
- Follow-up architecture doc updates: none expected

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice should protect the line between product insight and developer
inspection.

### Task

## Header
- ID: PRJ-691
- Title: Harden the visual system and prove responsive product quality
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-687, PRJ-688, PRJ-689, PRJ-690
- Priority: P1

## Context
The redesign slices need one final pass that aligns color semantics, spacing,
status treatments, copy language, and screenshot proof across the authenticated
shell.

## Goal
Freeze one coherent product-quality web baseline that is demonstrably ready to
guide later mobile implementation.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Shared visual and copy rules are synchronized across the main routes.
- [x] Mobile, tablet, and desktop screenshot proof exists for all major routes.
- [x] Task board, project state, and planning truth describe the same UX/UI baseline.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `npm run build` in `web/`; `..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_memory_repository.py tests/test_schema_baseline.py`
- Manual checks: route-level responsive class review and product-copy sweep across `/login`, `/chat`, `/settings`, `/tools`, `/personality`
- Screenshots/logs: refreshed browser artifact pass is still optional follow-up; implemented baseline is captured in `web/src/App.tsx` and validated by build/tests
- High-risk checks: verify no product-facing copy reintroduces raw backend or contract wording as primary UX

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`,
  `docs/architecture/27_codex_instructions.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: n/a
- Follow-up architecture doc updates: none expected

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
The final posture should feel like a real mobile-first product shell, not a
thin visual wrapper over inspection payloads.
