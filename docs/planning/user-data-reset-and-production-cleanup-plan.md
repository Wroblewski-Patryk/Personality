# User Data Reset And Production Cleanup Plan

## Purpose

This plan freezes a safe implementation lane for two related but different
needs raised on 2026-04-25:

- one operator-owned production cleanup path for resetting live data during the
  product transition from Telegram-first usage toward a web-first experience
- one authenticated self-service reset path for clearing runtime data that
  belongs to a single user without deleting the account itself

The goal is not to introduce a second storage model or a public destructive
admin surface.
The goal is to reuse the existing backend-owned identity, profile, memory,
planning, and app-settings contracts while making destructive reset behavior
explicit, bounded, and testable.

## Fresh Gap Snapshot

Observed from the current backend and web product baseline:

- first-party app identity is now backend-owned through auth sessions and
  `/app/*` routes
- user-owned continuity is spread across multiple `user_id`-owned tables:
  - episodic memory
  - semantic embeddings
  - conclusions and relations
  - theta
  - goals, tasks, planned work, progress, and milestones
  - attention turns, reflection tasks, and subconscious proposals
  - profile-owned Telegram link state
- the current web settings route already owns profile and preference mutations
  through `PATCH /app/me/settings`
- there is no shared repository-owned delete/reset primitive yet
- there is no operator runbook step or script for a bounded production cleanup
- the current schema uses explicit indexed ownership fields rather than
  database-level foreign-key cascades, so cleanup must be intentional and
  centralized instead of being spread across ad hoc endpoint logic

## Core Product Direction

Recommended direction for this lane:

- do not expose production-wide cleanup in product UI
- keep full production cleanup as an operator-only maintenance action
- add one self-service reset action under authenticated account settings
- self-service reset should clear runtime continuity for the current user, not
  delete the auth account
- self-service reset should preserve connected integrations, linked channels,
  and existing user settings so the user can start "from new" without
  reconfiguring the product shell
- self-service reset should reuse backend-owned auth/session, profile, and
  memory ownership instead of inventing a parallel "workspace reset" subsystem
- destructive deletion logic should have one shared backend owner so:
  - operator scripts
  - authenticated app endpoints
  - later admin tooling
  can all reuse the same deletion contract without duplicating table-by-table
  logic

## Architecture Fit

This lane fits the approved architecture because it reuses:

- backend-owned auth identity as the boundary for self-service requests
- existing `aion_profile` ownership for linked-channel continuity
- existing `user_id` ownership across memory, planning, and adaptive state
- existing backend-first `/app/*` contract for settings and account surfaces
- the ops/runbook layer for production-only destructive maintenance

This lane must not:

- create a public endpoint that wipes all production data
- move destructive side effects into the web client
- introduce a second identity map or separate "reset store"
- leave table cleanup as scattered endpoint-specific SQL
- blur account deletion with runtime-data reset

## Data Ownership Inventory

The current per-user runtime footprint spans these durable owners:

- keep by default for self-service reset:
  - `aion_auth_user`
- preserve by default for self-service reset:
  - `aion_profile`
    - keep Telegram link fields and link codes unless a later product decision
      explicitly says that linked-channel identity should be reset too
    - keep `preferred_language`
    - keep `ui_language`
    - keep language confidence/source when those fields are part of the user's
      chosen shell and continuity settings
  - settings-shaped operational conclusions:
    - `proactive_opt_in`
    - `telegram_enabled`
    - `clickup_enabled`
    - `google_calendar_enabled`
    - `google_drive_enabled`
- reset or delete for self-service reset:
  - `aion_memory`
  - `aion_semantic_embedding`
  - `aion_conclusion`
    - excluding the preserved settings-shaped operational conclusions above
  - `aion_relation`
  - `aion_theta`
  - `aion_goal`
  - `aion_task`
  - `aion_planned_work_item`
  - `aion_goal_progress`
  - `aion_goal_milestone`
  - `aion_goal_milestone_history`
  - `aion_attention_turn`
  - `aion_reflection_task`
  - `aion_subconscious_proposal`
- revoke during self-service reset:
  - `aion_auth_session`
    - revoke all sessions, including the current session, so the next
      authenticated turn starts from a clean continuity baseline

Production cleanup should be built from the same ownership map, but the lane
must keep two distinct operator scopes:

1. runtime cleanup while preserving auth accounts
2. full destructive wipe including auth users and sessions, only if explicitly
   approved later

## Recommended Product Contract

### Self-Service Reset

Recommended first implementation:

- authenticated route:
  - `POST /app/me/reset-data`
- request body:
  - explicit confirmation text or boolean confirmation field
  - optional future scope selector, but start with one fixed safe scope
- success semantics:
  - runtime continuity for the current authenticated user is removed
  - connected integrations and user settings stay in place
  - linked Telegram continuity stays attached unless a later explicit product
    decision says otherwise
  - the response returns a compact destructive-operation summary, not raw delete
    counts only

Recommended first reset scope:

- preserve:
  - auth account identity
  - email
  - password hash
  - display name
  - UI and conversation settings
  - tool enablement preferences
  - linked integrations and linked channels
- reset:
  - memory continuity
  - learned preferences that are not explicit user-managed settings
  - adaptive state
  - internal planning state
  - transient queue and proposal state

Why this scope:

- it matches the user clarification that connected APIs and settings should not
  change
- it keeps the feature separate from account deletion
- it lets the user keep the configured shell and integrations while removing
  learned continuity, goals, tasks, and recall

### Production Cleanup

Recommended first implementation:

- one repo-owned operator script under `backend/scripts/`
- no public production wipe endpoint
- script should call the same shared backend cleanup owner used by the
  self-service reset path
- the script should support at least:
  - `runtime_only_preserve_auth`
  - `single_user_runtime_reset`

Do not implement full-auth destructive wipe in the same first slice unless it
is explicitly approved after the safer runtime-only path exists and is proven.

## Implementation Order

### PRJ-719 Reset Boundary Contract And Retention Policy Freeze

Result:

- one explicit reset contract is frozen for:
  - self-service user reset
  - operator-owned production runtime cleanup
- the repo records exactly which tables and conclusion kinds are:
  - deleted
  - preserved
  - optionally session-revoked
- session posture after reset is frozen
- product wording distinguishes:
  - clear my data
  - delete my account
  - operator production cleanup

Validation:

- architecture, planning, and data-ownership cross-review

### PRJ-720 Shared Backend Cleanup Owner And Operator Script

Result:

- backend gains one shared repository-owned cleanup primitive for per-user
  runtime reset
- backend gains one operator script that reuses that same primitive for:
  - single-user runtime reset
  - runtime-only production cleanup preserving auth accounts
- `POST /app/me/reset-data` is implemented against the same cleanup owner
- destructive work stays server-side and testable

Validation:

- `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py; Pop-Location`

### PRJ-721 Account Settings Reset UX And Confirmation Flow

Result:

- the authenticated settings route gains one explicit destructive-action card
- the UI explains the exact effect:
  - clears memory and learned runtime state
  - keeps integrations, linked channels, and user settings
  - keeps the account
- the flow requires a deliberate confirmation step instead of a one-click
  toggle

Validation:

- `Push-Location .\web; npm run build; Pop-Location`

### PRJ-722 Regression Proof, Ops Runbook, And Context Sync

Result:

- regression coverage pins the reset contract and destructive guardrails
- the runtime ops runbook documents the operator-only production cleanup flow
- planning and context truth describe the same reset boundary
- if implementation confirms the expected pitfall, the learning journal records
  the guardrail

Validation:

- `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
- `Push-Location .\web; npm run build; Pop-Location`

## Open Decisions To Confirm Before Implementation

1. should self-service reset preserve `display_name`, or should it return the
   user to a near-first-login state?
   - resolved by user direction: preserve `display_name` and other settings
2. should the first operator script support full auth-user deletion?
   - recommended: no; start with runtime-only production cleanup and single-user
     reset
3. should self-service reset keep the current session alive?
   - resolved for the first implementation: no; revoke all auth sessions,
     including the current session, after reset

## Risks And Guardrails

1. avoid mixing runtime-data reset with account deletion
   - deleting `aion_auth_user` from a profile settings button is a different
     product contract
2. keep production cleanup out of product UI
   - a full production wipe is an ops action, not a normal user action
3. centralize destructive ownership
   - table cleanup must live behind one backend owner, not several hand-written
     endpoint-specific delete blocks
4. clear linked-channel continuity too
   - superseded by user direction for this lane: linked integrations and
     settings should stay in place unless a later product decision narrows the
     reset scope
5. prove reset behavior with regression coverage
   - destructive flows should not rely on manual confidence alone

## Recommended Execution Order

1. `PRJ-719` Reset Boundary Contract And Retention Policy Freeze
2. `PRJ-720` Shared Backend Cleanup Owner And Operator Script
3. `PRJ-721` Account Settings Reset UX And Confirmation Flow
4. `PRJ-722` Regression Proof, Ops Runbook, And Context Sync

## Queue Update (2026-04-25)

- `PRJ-719` is complete.
- `PRJ-720` is now complete:
  - one shared cleanup owner now lives in `MemoryRepository`
  - `POST /app/me/reset-data` reuses that owner for self-service runtime reset
  - operator scripts now support bounded runtime cleanup with explicit
    confirmation guards
- `PRJ-721` is now complete:
  - the first-party settings route now exposes a dedicated destructive reset
    card with exact-phrase confirmation
  - the product shell now returns the user to login after successful reset,
    matching the backend session-revocation contract
- `PRJ-722` is now complete:
  - the runtime ops runbook now documents the bounded operator cleanup flow
  - testing guidance now records the required regression proof for reset and
    cleanup slices
  - final lane validation is green:
    - backend full suite: `937 passed`
    - web build: passed
- the destructive-data lane seeded through `PRJ-722` is now complete.
