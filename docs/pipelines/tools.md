# Tools Pipeline

Last updated: 2026-05-03

This document maps the app-facing tools and connector readiness flow. It is
grounded in the current codebase and should be treated as the technical
reference for the browser tools surface, connector readiness snapshots, user
tool preferences, and Telegram link-code start path.

## Scope

Covered:

- browser tools overview load
- tool preference updates
- Telegram link-code start
- connector readiness and authorization snapshots used by the overview
- relationship to health/capability catalog surfaces

Not covered:

- provider credential setup steps; use
  [Runtime Ops Runbook](../operations/runtime-ops-runbook.md) and the active
  organizer activation runbooks for operations
- provider-specific API contracts beyond readiness and permission posture
- runtime tool execution details outside the action boundary

## Trigger Paths

| Trigger | Frontend Entry | Backend Route/API | Result |
| --- | --- | --- | --- |
| Tools route load | `web/src/App.tsx`, `api.getToolsOverview()` in `web/src/lib/api.ts` | `GET /app/tools/overview` | Builds the authenticated user's tool/channel readiness snapshot. |
| Preference toggle | `web/src/App.tsx`, `api.patchToolsPreferences()` in `web/src/lib/api.ts` | `PATCH /app/tools/preferences` | Stores supported tool preferences and returns a refreshed overview. |
| Telegram link start | `web/src/App.tsx`, `api.startTelegramLink()` in `web/src/lib/api.ts` | `POST /app/tools/telegram/link/start` | Creates or rotates a Telegram link code when Telegram is configured. |
| Operator/runtime health | Health callers and app health surfaces | `GET /health` | Exposes connector execution baseline, organizer tool stack, web knowledge tools, and capability catalog posture. |

## Runtime Flow

1. The browser tools route asks `web/src/lib/api.ts` for the overview.
2. `backend/app/api/routes.py` authenticates the app session through
   `_require_app_auth`.
3. The route reads the current user profile and runtime preferences through
   `MemoryRepository`.
4. Telegram telemetry is converted into a channel snapshot with provider
   configuration and round-trip readiness hints.
5. `app_tools_overview_snapshot` in `backend/app/core/app_tools_policy.py`
   composes:
   - first-party internal chat status
   - Telegram provider/link/preference status
   - ClickUp readiness
   - Google Calendar readiness
   - Google Drive readiness
   - web knowledge and web browser tool posture
6. Connector readiness is derived from
   `connector_execution_baseline_snapshot` and
   `organizer_tool_stack_snapshot` in
   `backend/app/core/connector_execution.py`.
7. Connector permission posture is owned by
   `connector_authorization_matrix_snapshot`,
   `build_connector_permission_gate`, and `_OPERATION_POLICIES` in
   `backend/app/core/connector_policy.py`.
8. The capability catalog can expose a higher-level snapshot through
   `capability_catalog_snapshot` without moving execution authority into the
   frontend.

## Preference Writes

`PATCH /app/tools/preferences` accepts the supported preference fields:

- `telegram_enabled`
- `clickup_enabled`
- `google_calendar_enabled`
- `google_drive_enabled`

For each non-null field, `backend/app/api/routes.py` writes an `AionConclusion`
through `MemoryRepository.upsert_conclusion` with:

- `kind`: the preference key
- `content`: `"true"` or `"false"`
- `confidence`: `1.0`
- `source`: `app_tools_preferences`

The route then rebuilds the overview from persisted preferences instead of
trusting the request body as the display source of truth.

## Telegram Link Start

`POST /app/tools/telegram/link/start`:

- requires an authenticated app session
- fails with `409` when `telegram_bot_token` is not configured
- creates a new link code with `_new_telegram_link_code`
- persists the code and issue time through
  `MemoryRepository.create_or_rotate_telegram_link_code`
- returns the link code and an instruction string for the user

The link-code confirmation path is handled by Telegram transport code and the
external event ingress/runtime path, not by this route directly.

## Data Read And Write

| Data | Owner | Read/Write | Notes |
| --- | --- | --- | --- |
| `AionConclusion` | `backend/app/memory/models.py`, `MemoryRepository` | Read/write | Stores supported tool preference keys from the tools surface. |
| `AionProfile` | `backend/app/memory/models.py`, `MemoryRepository` | Read/write | Stores Telegram link/profile fields such as link code and chat identity. |
| Telegram telemetry snapshot | `backend/app/integrations/telegram/telemetry.py` | Read | Supplies provider configuration and round-trip readiness hints. |
| Connector execution baseline | `backend/app/core/connector_execution.py` | Read | Separates provider-ready operations from credentials-missing operations. |
| Connector authorization matrix | `backend/app/core/connector_policy.py` | Read | Declares allowed operation modes and permission gate posture. |

## Failure Points

- Provider readiness can be confused with policy capability. The overview must
  keep provider-ready state separate from connector authorization posture.
- Missing ClickUp, Google Calendar, Google Drive, or Telegram credentials keep
  provider-backed operations unavailable even when policy allows the operation
  shape.
- Stale preference conclusions can make the user request an integration that is
  not provider-ready; the overview should surface that as configuration
  required, not as enabled execution.
- Telegram link start must fail closed when the Telegram provider is not
  configured.
- Telegram link codes can be stale or unconfirmed; the overview exposes
  `linked`, `pending_confirmation`, or `not_linked` state from profile data.
- Connector permission gates must remain backend-owned; the frontend can render
  status but must not reconstruct operation authorization.
- Provider/API-owned text should not be translated or rewritten client-side
  without an explicit contract decision.

## Tests

Current relevant tests:

- `backend/tests/test_api_routes.py` for tools overview, preferences, auth, and
  Telegram link behavior when covered by route tests.
- `backend/tests/test_connector_policy.py` for connector permission and
  authorization matrix behavior.
- `backend/tests/test_action_executor.py` for action/tool execution boundaries.
- `backend/tests/test_runtime_pipeline.py` for runtime paths that can invoke
  provider-backed connector behavior through approved action boundaries.

`GAP`: tests are not tagged with machine-readable pipeline IDs, so this mapping
is inferred from file responsibility and inspected route/module names.

## Related Modules

- `backend/app/api/routes.py`
- `backend/app/api/schemas.py`
- `backend/app/core/app_tools_policy.py`
- `backend/app/core/capability_catalog.py`
- `backend/app/core/connector_execution.py`
- `backend/app/core/connector_policy.py`
- `backend/app/integrations/telegram/`
- `backend/app/integrations/clickup/`
- `web/src/App.tsx`
- `web/src/lib/api.ts`

## Related Docs

- [Pipeline Registry](index.md)
- [Traceability Matrix](../architecture/traceability-matrix.md)
- [API Reference](../api/index.md)
- [Data Model Reference](../data/index.md)
- [Action System](../architecture/20_action_system.md)
- [Runtime Ops Runbook](../operations/runtime-ops-runbook.md)

## Known Gaps

- Provider-specific capability/configuration docs are still incomplete.
- No generated connector capability matrix is checked in.
- Frontend e2e coverage for the tools toggles and Telegram link start is not
  stable in this documentation pass.
- Live provider smoke remains blocked when provider credentials are missing.
