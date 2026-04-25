# V2 Product Entry Plan

## Purpose

This document records the approved entry plan for `v2`.

The goal is to evolve Personality from a backend-first no-UI `v1` runtime into
one product-shaped repository and deployment baseline with:

- `backend/` for the AION runtime and API
- `web/` for the first-party browser client
- `mobile/` for the later mobile client

This plan does not replace the canonical AION architecture.
It defines the repository, product-surface, and deployment work needed so the
existing backend can grow into a coherent multi-surface product without
creating a second logic stack outside the Python runtime.

## Approved Direction

Approved on 2026-04-25 through user decision:

- keep Python + FastAPI as the backend runtime
- use product-facing top-level directories:
  - `backend/`
  - `web/`
  - `mobile/`
- keep only repo-wide and deployment-wide files in the root
- introduce backend-owned authentication for first-party clients
- expose UI-safe app-facing API surfaces instead of reusing internal debug
  inspection endpoints directly

## Current Progress

Completed on 2026-04-25:

- `PRJ-655..PRJ-659`
  - repository now matches `backend/`, `web/`, and `mobile/` topology
  - root Docker and compose flows resolve the moved backend
  - `web/` has a working React + TypeScript + Vite + Tailwind + daisyUI build
  - `mobile/` is reserved without prematurely freezing a mobile stack
- `PRJ-660..PRJ-663`
  - backend now owns first-party auth/session state
  - backend now exposes initial app-facing endpoints for user session,
    settings, chat, and personality overview
- `PRJ-664..PRJ-666`
  - `web/` now provides the first product shell for auth, chat, settings, and personality inspection
  - the production image now builds `web/` and serves the built SPA from backend-owned topology
  - release smoke now proves backend runtime revision and served web revision move together after push
- `PRJ-669..PRJ-670`
  - backend now exposes an authenticated grouped tools and channels contract
    through `/app/tools/overview`
  - the response is built from backend truth for connectors, web knowledge
    tooling, Telegram readiness, and explicit placeholders for future tools
  - the first web tools screen can now consume one app-facing source of truth
    instead of inferring connector state from mixed overview payloads
- `PRJ-671`
  - `web/` now includes the first dedicated tools screen
  - grouped tools state is rendered directly from backend truth and remains
    read-only where mutation or linking is not implemented yet
- `PRJ-672`
  - supported tool and channel toggles now persist through backend-owned user
    preferences
  - the web tools screen now includes working toggles for supported items
    while preserving read-only posture for unsupported or integral entries
- `PRJ-673`
  - backend now exposes a bounded Telegram user-linking flow through
    `/app/tools/telegram/link/start` and Telegram `/link CODE` confirmation
  - Telegram link state now flows through the same app-facing tools contract
    instead of being guessed in the browser client
  - the web tools screen now shows truthful code-generation and confirmation
    guidance only when backend state says Telegram is enabled and still
    awaiting user linking

Next active lane:

- `PRJ-674` tools and channels proof and alignment
- `PRJ-667..PRJ-668` mobile foundation remains planned after that lane

## Target Repository Topology

Target root:

```text
/
  README.md
  AGENTS.md
  .gitignore
  .env.example
  docker-compose.yml
  docker-compose.coolify.yml
  /backend
  /web
  /mobile
  /docs
  /docker
```

Target meaning of each top-level product folder:

- `backend/`
  - FastAPI application
  - AION runtime
  - persistence, memory, reflection, scheduler, integrations
  - first-party auth/session logic
  - app-facing API for web and mobile
- `web/`
  - React + TypeScript + Vite
  - Tailwind + daisyUI
  - browser UI for login, settings, chat, and personality inspection
- `mobile/`
  - later mobile client workspace
  - must reuse backend-owned auth and client API contracts
  - concrete mobile stack remains a bounded follow-up decision

## Architecture Guardrails

- backend remains the only owner of cognition, memory, planning, action,
  reflection, and external integrations
- web and mobile are product clients, not second runtimes
- internal debug and admin inspection surfaces stay operator-only unless an
  explicit client-safe boundary is created
- auth and session state belong to backend-owned contracts
- deployment automation must remain repo-driven and production-proof after the
  topology change

## Production Baseline For V2 Entry

The initial `v2` production goal is not "ship every screen at once".

It is:

1. the repo can be restructured into `backend/`, `web/`, and `mobile/`
2. the existing Python runtime still deploys correctly after push
3. the `web` client can be built and deployed from the same repo-driven flow
4. backend auth and app-facing API become stable enough for first-party
   clients
5. `mobile` has a reserved workspace and contract path instead of being an
   afterthought

Production expectation for the first `v2` web release:

- current backend workers and API keep their bounded ownership
- `web` becomes a separately buildable client surface
- repo-driven Coolify deploy remains the source of truth after push
- release smoke must prove the deployed backend revision and deployed web
  revision belong to the same repository truth

## Execution Order

### Group 109 - V2 Product Topology And Repository Migration

- `PRJ-655` Freeze the `backend/web/mobile` repository topology and naming.
- `PRJ-656` Move the current Python runtime into `backend/` without changing
  runtime behavior.
- `PRJ-657` Normalize tooling, docs, compose paths, test commands, and
  migration paths after the `backend/` move.
- `PRJ-658` Scaffold the `web/` workspace with React + TypeScript + Vite +
  Tailwind + daisyUI.
- `PRJ-659` Scaffold the `mobile/` workspace as a reserved product surface
  with a minimal baseline and explicit no-runtime-logic posture.

### Group 110 - First-Party Auth And Client API Boundary

- `PRJ-660` Freeze the backend auth/session and user-identity mapping contract
  for first-party clients.
- `PRJ-661` Implement the backend auth/session baseline.
- `PRJ-662` Freeze the app-facing client API boundary for settings, chat, and
  personality inspection.
- `PRJ-663` Implement the UI-safe app-facing API surfaces over existing
  backend truth.

### Group 111 - Web Product Shell

- `PRJ-664` Build the `web/` product shell for:
  - login
  - settings
  - chat
  - personality inspector
- `PRJ-665` Integrate `web/` build and serving into the production topology.
- `PRJ-666` Add release smoke and deploy proof for the combined backend + web
  repo-driven push-deploy baseline.

### Group 112 - Mobile Product Foundation

- `PRJ-667` Freeze the mobile client stack and shared client-contract baseline.
- `PRJ-668` Build the initial `mobile/` foundation using the same auth and
  client API boundary as `web/`.

### Group 113 - Tools And Channels Visibility

- `PRJ-669` Freeze the backend-owned app-facing contract for grouped tools,
  channels, and capability states.
- `PRJ-670` Implement the backend `tools overview` read model from existing
  connector, channel, and readiness truth.
- `PRJ-671` Build the first `web` tools screen with grouped sections and
  backend-truth state rendering.
- `PRJ-672` Add user-owned enablement preferences for allowed tools and
  channels without introducing browser-managed provider secrets.
- `PRJ-673` Implement Telegram user-linking flow between backend auth identity
  and Telegram channel identity.
- `PRJ-674` Add release, testing, and documentation proof so the tools screen
  and its enablement states stay aligned with backend truth.

## Definition Of Success

The `v2` entry phase is successful when:

- the repository truth, docs, and deploy scripts all describe the same
  `backend/web/mobile` topology
- the current AION runtime runs from `backend/` without semantic drift
- `web/` exists as a real buildable client surface with daisyUI baseline
- `mobile/` exists as a deliberate product surface with an approved contract
  path
- backend-owned auth/session and app-facing API are stable enough for
  first-party clients
- production push deploy still works and is proven by smoke/release evidence

## Non-Goals For The Entry Phase

- rewriting the AION runtime into JavaScript or TypeScript
- exposing debug/admin surfaces directly to product clients
- building a second domain model in `web/` or `mobile/`
- shipping fully mature mobile release automation in the same slice as the
  first topology move
