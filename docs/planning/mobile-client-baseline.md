# Mobile Client Baseline

## Purpose

This document freezes the initial mobile stack and shared client-contract
baseline for the `v2` mobile foundation.

It exists so `mobile/` can move from placeholder status to a real workspace
without guessing the mobile stack or inventing a second product contract.

## Approved Stack

The initial mobile client stack is:

- Expo-managed React Native app
- TypeScript
- Expo Router

This aligns with current Expo guidance where new Expo apps include Expo Router
as the default routing baseline and keeps the first mobile slice close to the
existing TypeScript-first `web/` workspace while remaining native-client
appropriate.

## Shared Client-Contract Baseline

`mobile/` must remain a thin client over backend-owned app-facing contracts.

The shared first-party resource model is:

- authenticated user/session state
- settings
- chat history
- chat message send
- personality overview
- tools overview
- allowed tools preference updates
- Telegram linking start flow

Current shared app-facing endpoints:

- `POST /app/auth/register`
- `POST /app/auth/login`
- `POST /app/auth/logout`
- `GET /app/me`
- `PATCH /app/me/settings`
- `GET /app/chat/history`
- `POST /app/chat/message`
- `GET /app/personality/overview`
- `GET /app/tools/overview`
- `PATCH /app/tools/preferences`
- `POST /app/tools/telegram/link/start`

## Boundary Rules

- backend remains the only owner of auth, cognition, memory, planning, action,
  reflection, and integrations
- mobile must not consume internal debug or operator-only surfaces such as
  `/internal/*`
- mobile must not manage provider secrets in UI
- mobile must not introduce a second domain model for tools, personality,
  settings, or chat
- mobile may add client-side presentation state, navigation state, and local
  input drafts only

## Auth Transport Posture

The shared resource contract is frozen now, but native auth transport details
must remain explicit.

Current repo fact:

- backend auth is already owned by first-party `/app/auth/*` contracts
- the current `web` client uses backend-owned session cookies

Bounded posture for the mobile foundation:

- `PRJ-668` may scaffold the client around the shared backend-owned resource
  model
- `PRJ-668` must not pretend the final native auth transport is already fully
  solved if the scaffold still relies on a later dedicated API-client adapter
  decision

## Non-Goals For This Freeze

- choosing store-release automation
- building native modules
- deciding offline-first sync strategy
- introducing mobile-specific backend contracts before the shared baseline is
  exercised
- exposing provider setup or admin debug tooling inside the mobile client
