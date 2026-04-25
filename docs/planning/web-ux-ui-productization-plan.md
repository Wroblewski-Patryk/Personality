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
- render the selector as `flag + language label`
- explain in helper copy that the selector changes interface language only

### Task

## Header
- ID: PRJ-687
- Title: Redesign chat for mobile-first conversation priority
- Status: BACKLOG
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
- [ ] Mobile chat layout prioritizes the conversation thread and composer.
- [ ] Empty, loading, sending, and success states feel coherent on mobile and tablet.
- [ ] The route remains a thin client over `/app/chat/*`.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted web route coverage if component structure changes
- Manual checks: mobile, tablet, desktop route screenshots plus one send-message pass
- Screenshots/logs: updated route captures for `/chat`
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
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Treat this route as the design reference for the later mobile client.

### Task

## Header
- ID: PRJ-688
- Title: Simplify settings and remove manual runtime-style controls
- Status: BACKLOG
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
- [ ] The editable preference form is primary.
- [ ] Repeated backend snapshot duplication is reduced or removed from the main flow.
- [ ] `response style` and `collaboration preference` are removed from the product-facing settings form.
- [ ] UI-language selection is described as interface-only and uses a flag icon plus label pattern.
- [ ] Save-state, dirty-state, and completion feedback are visually clear.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted web route coverage if interaction states change
- Manual checks: mobile, tablet, desktop route screenshots plus save-state check
- Screenshots/logs: updated route captures for `/settings`
- High-risk checks: keep `/app/me` and `PATCH /app/me/settings` as the only source of truth until an explicit UI-locale contract lands

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: n/a
- Follow-up architecture doc updates: none expected

## Review Checklist (mandatory)
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Preference editing should feel closer to a mobile settings screen than to an
admin form.

### Task

## Header
- ID: PRJ-689
- Title: Reframe tools into status-plus-action product cards
- Status: BACKLOG
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
- [ ] Mobile layout avoids horizontal expansion and dead-space posture.
- [ ] Primary states and actions are understandable without backend vocabulary.
- [ ] Technical detail is reduced, hidden, or clearly secondary.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted web route coverage if rendering logic changes
- Manual checks: mobile, tablet, desktop route screenshots and toggle flow review
- Screenshots/logs: updated route captures for `/tools`
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
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This route must become suitable for a later mobile app transfer, not stay an
inspection-heavy dashboard.

### Task

## Header
- ID: PRJ-690
- Title: Split personality insights from raw inspector payloads
- Status: BACKLOG
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
- [ ] Product-facing insights are understandable without reading JSON.
- [ ] Raw payload visibility is clearly secondary or moved behind an explicit inspect action.
- [ ] Mobile layout remains readable and bounded for all major sections.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted web route coverage if route rendering structure changes
- Manual checks: mobile, tablet, desktop route screenshots plus inspector fallback review
- Screenshots/logs: updated route captures for `/personality`
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
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice should protect the line between product insight and developer
inspection.

### Task

## Header
- ID: PRJ-691
- Title: Harden the visual system and prove responsive product quality
- Status: BACKLOG
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
- [ ] Shared visual and copy rules are synchronized across the main routes.
- [ ] Mobile, tablet, and desktop screenshot proof exists for all major routes.
- [ ] Task board, project state, and planning truth describe the same UX/UI baseline.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted web regression coverage plus production build if route structure changed
- Manual checks: screenshot review for `/login`, `/chat`, `/settings`, `/tools`, `/personality`
- Screenshots/logs: refreshed artifact set for the final UX baseline
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
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
The final posture should feel like a real mobile-first product shell, not a
thin visual wrapper over inspection payloads.
