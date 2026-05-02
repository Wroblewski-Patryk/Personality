# API Reference

Last updated: 2026-05-03

This reference is grounded in:

- `backend/app/api/routes.py`
- `backend/app/api/schemas.py`
- `web/src/lib/api.ts`

It documents the current HTTP surface at an engineering level. It is not a
generated OpenAPI export. When a route shape is intentionally flexible, this
file says so rather than inventing fields.

## Route Groups

| Group | Routes | Primary Consumer |
| --- | --- | --- |
| Health and readiness | `GET /health` | Operators, release smoke, web health panels |
| App auth/session | `/app/auth/*`, `/app/me` | Web shell |
| App profile/data | `/app/me/settings`, `/app/me/reset-data` | Web shell |
| App chat | `/app/chat/history`, `/app/chat/message` | Web shell |
| App learned state | `/app/personality/overview` | Web shell |
| App tools/channels | `/app/tools/*` | Web shell |
| Internal/debug | `/internal/state/inspect`, `/event/debug`, `/internal/event/debug`, debug query compat on `/event` | Operators/debug tooling |
| General event ingress | `POST /event` | API clients and transports |
| Telegram operator | `POST /telegram/set-webhook` | Operator tooling |

## Shared Client Behavior

The web API client in `web/src/lib/api.ts`:

- sends `credentials: "include"` on every request
- sends JSON with `Content-Type: application/json`
- parses JSON responses when possible
- throws `ApiError(status, detail)` on non-2xx responses
- falls back to raw response text or `Request failed with status <status>.`
  when no structured `detail` exists

## Auth And Trust Boundaries

| Boundary | Meaning |
| --- | --- |
| Public/runtime | No app session required; route may still enforce runtime/debug policy. |
| App auth required | Requires the first-party auth session cookie resolved by `_require_app_auth()`. |
| Debug access required | Requires debug policy/token posture enforced by `_enforce_debug_access()` or shared debug ingress policy. |
| Operator/provider | Intended for operator tooling or provider setup; environment configuration controls success. |

No secret values are documented here. Route behavior that depends on configured
tokens or provider credentials is described only as posture.

## Schemas

Verified in `backend/app/api/schemas.py`.

| Schema | Fields | Used By |
| --- | --- | --- |
| `EventReplyResponse` | `message`, `language`, `tone`, `channel` | `EventResponse`, `AppChatMessageResponse` |
| `EventRuntimeResponse` | `role`, `motivation_mode`, `action_status`, `reflection_triggered` | `EventResponse`, `AppChatMessageResponse` |
| `EventQueueResponse` | `queued`, `reason`, optional `turn_id`, optional `source_count` | `EventResponse` |
| `EventResponse` | `event_id`, `trace_id`, `source`, optional `reply`, `runtime`, `queue`, `debug`, `system_debug`, `incident_evidence` | `/event`, debug ingress routes |
| `SetWebhookRequest` | `webhook_url`, optional `secret_token` | `/telegram/set-webhook` |
| `AppRegisterRequest` | `email`, `password`, optional `display_name` | `/app/auth/register` |
| `AppLoginRequest` | `email`, `password` | `/app/auth/login` |
| `AppSettingsPatchRequest` | optional `preferred_language`, `ui_language`, `utc_offset`, `proactive_opt_in`, `display_name` | `/app/me/settings` |
| `AppResetDataRequest` | `confirmation_text` | `/app/me/reset-data` |
| `AppChatMessageRequest` | `text` | `/app/chat/message` |
| `AppAuthUserResponse` | `id`, `email`, optional `display_name` | `AppMeResponse` |
| `AppSettingsResponse` | optional `preferred_language`, `ui_language`, `utc_offset`, `proactive_opt_in` | `AppMeResponse`, `/app/me/settings` |
| `AppResetDataResponse` | `status`, `scope`, optional `target_user_id`, `total_deleted_records`, `revoked_session_count`, `cleared_categories`, `preserved_categories`, `preserved_conclusion_kinds` | `/app/me/reset-data` |
| `AppMeResponse` | `user`, `settings`, extra fields allowed | register/login/me |
| `AppChatHistoryEntry` | `message_id`, `event_id`, `role`, `text`, `channel`, `timestamp`, optional `metadata` | `AppChatHistoryResponse` |
| `AppChatHistoryResponse` | `items` | `/app/chat/history` |
| `AppChatMessageResponse` | `reply`, optional `runtime`, `event_id`, `trace_id` | `/app/chat/message` |
| `AppPersonalityOverviewResponse` | extra fields allowed | `/app/personality/overview` |
| `AppToolsOverviewResponse` | extra fields allowed | `/app/tools/overview`, `/app/tools/preferences` |
| `AppToolsPreferencesPatchRequest` | optional `telegram_enabled`, `clickup_enabled`, `google_calendar_enabled`, `google_drive_enabled` | `/app/tools/preferences` |
| `AppTelegramLinkStartResponse` | `link_code`, `instruction_text`, `link_state`, `expires_in_seconds` | `/app/tools/telegram/link/start` |

## Endpoints

### `GET /health`

- Boundary: public/runtime readiness; no app auth.
- Request: no body.
- Response: built by `build_health_response()` and includes policy/readiness
  sections such as runtime policy, release readiness, v1 readiness, API
  readiness, capability catalog, topology, observability, identity, affective,
  retrieval, learned state, connectors, deployment, Telegram, scheduler,
  proactive, role/skill, attention, and reflection.
- Side effects: reads runtime, worker, scheduler, repository, telemetry, and
  policy state; no route-owned writes expected.
- Frontend caller: `api.getHealth()` in `web/src/lib/api.ts`.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_runtime_policy.py`,
  `backend/tests/test_main_runtime_policy.py`,
  `backend/tests/test_deployment_trigger_scripts.py`.
- Related pipeline: [Release and deployment smoke](../pipelines/index.md#release-and-deployment-smoke).

### `POST /app/auth/register`

- Boundary: public app auth.
- Request schema: `AppRegisterRequest`.
- Response schema: `AppMeResponse`.
- Behavior: normalizes email, rejects duplicate users with `409`, creates an
  auth user, creates a session, updates `last_login_at`, sets the auth cookie,
  and returns user/settings.
- Side effects: writes `AionAuthUser`, `AionAuthSession`; reads profile and
  runtime preferences.
- Frontend caller: `api.register(...)`.
- Tests: `backend/tests/test_api_routes.py`.
- Related pipeline: [App auth session](../pipelines/index.md#app-auth-session).

### `POST /app/auth/login`

- Boundary: public app auth.
- Request schema: `AppLoginRequest`.
- Response schema: `AppMeResponse`.
- Behavior: verifies email/password, rejects invalid credentials with `401`,
  rejects inactive users with `403`, creates a session, sets the auth cookie,
  and returns user/settings.
- Side effects: writes `AionAuthSession`, updates `AionAuthUser.last_login_at`;
  reads profile and runtime preferences.
- Frontend caller: `api.login(...)`.
- Tests: `backend/tests/test_api_routes.py`.
- Related pipeline: [App auth session](../pipelines/index.md#app-auth-session).

### `POST /app/auth/logout`

- Boundary: app auth required.
- Request: no body.
- Response: `{ "ok": true }`.
- Behavior: revokes current auth session and clears auth cookie.
- Side effects: writes `AionAuthSession.revoked_at`.
- Frontend caller: `api.logout()`.
- Tests: `backend/tests/test_api_routes.py`.
- Related pipeline: [App auth session](../pipelines/index.md#app-auth-session).

### `GET /app/me`

- Boundary: app auth required.
- Request: no body.
- Response schema: `AppMeResponse`.
- Behavior: returns authenticated user and current settings payload.
- Side effects: reads auth user/session, profile, and runtime preferences.
- Frontend caller: `api.getMe()`.
- Tests: `backend/tests/test_api_routes.py`.
- Related pipeline: [App auth session](../pipelines/index.md#app-auth-session).

### `PATCH /app/me/settings`

- Boundary: app auth required.
- Request schema: `AppSettingsPatchRequest`.
- Response schema: `AppSettingsResponse`.
- Behavior: updates display name, preferred language, UI language, UTC offset,
  and/or `proactive_opt_in` when the corresponding field is present.
- Side effects:
  - updates `AionAuthUser.display_name`
  - updates `AionProfile` language/UI/UTC fields
  - upserts `AionConclusion(kind="proactive_opt_in")`
- Frontend caller: `api.patchSettings(...)`.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_preferences.py`.
- Related pipeline: [Profile settings](../pipelines/index.md#profile-settings).

### `POST /app/me/reset-data`

- Boundary: app auth required.
- Request schema: `AppResetDataRequest`.
- Response schema: `AppResetDataResponse`.
- Behavior: requires the exact confirmation text from the route constant,
  resets user runtime data through the repository, clears the auth cookie, and
  returns deletion/preservation summary.
- Side effects: deletes or preserves user-scoped data according to repository
  reset policy; revokes sessions as reported by the summary.
- Frontend caller: `api.resetData(...)`.
- Tests: `backend/tests/test_api_routes.py`.
- Related pipeline: [User data reset](../pipelines/index.md#user-data-reset).

### `GET /app/chat/history`

- Boundary: app auth required.
- Query: `limit` integer, default `10`, minimum `1`, maximum `100`.
- Response schema: `AppChatHistoryResponse`.
- Behavior: returns recent durable transcript entries for the authenticated
  user.
- Side effects: reads transcript projection from repository; no route-owned
  writes expected.
- Frontend caller: `api.getChatHistory()`.
- Tests: `backend/tests/test_api_routes.py`.
- Related pipeline: [App chat turn](../pipelines/index.md#app-chat-turn).

### `POST /app/chat/message`

- Boundary: app auth required.
- Request schema: `AppChatMessageRequest`.
- Response schema: `AppChatMessageResponse`.
- Behavior: wraps text in an event payload with authenticated `user_id`, runs
  `_handle_event_request(..., include_debug=False)`, and returns event id,
  trace id, reply, and runtime summary.
- Side effects: normal foreground runtime side effects, including memory write
  and possible reflection enqueue/action delivery.
- Frontend caller: `api.sendChatMessage(...)`.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_runtime_pipeline.py`,
  `backend/tests/test_expression_agent.py`.
- Related pipeline: [App chat turn](../pipelines/index.md#app-chat-turn).

### `GET /app/personality/overview`

- Boundary: app auth required.
- Request: no body.
- Response schema: `AppPersonalityOverviewResponse` with extra fields allowed.
- Behavior: builds the learned-state snapshot for the authenticated user.
- Side effects: reads memory/profile/conclusion/relation/goal/task state; no
  route-owned writes expected.
- Frontend caller: `api.getPersonalityOverview()`.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_memory_repository.py`.
- Related pipeline: [Learned state overview](../pipelines/index.md#learned-state-overview).

### `GET /app/tools/overview`

- Boundary: app auth required.
- Request: no body.
- Response schema: `AppToolsOverviewResponse` with extra fields allowed.
- Behavior: builds tool/channel overview from settings, user preferences,
  profile, and Telegram telemetry.
- Side effects: reads settings/profile/preferences/telemetry; no route-owned
  writes expected.
- Frontend caller: `api.getToolsOverview()`.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_connector_policy.py`.
- Related pipeline: [Tools overview](../pipelines/index.md#tools-overview).

### `PATCH /app/tools/preferences`

- Boundary: app auth required.
- Request schema: `AppToolsPreferencesPatchRequest`.
- Response schema: `AppToolsOverviewResponse` with extra fields allowed.
- Behavior: upserts a boolean conclusion for each provided tool preference,
  then returns the same overview shape as `GET /app/tools/overview`.
- Side effects: upserts `AionConclusion` rows for:
  `telegram_enabled`, `clickup_enabled`, `google_calendar_enabled`,
  `google_drive_enabled`.
- Frontend caller: `api.patchToolsPreferences(...)`.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_connector_policy.py`,
  `backend/tests/test_action_executor.py`.
- Related pipeline: [Tools overview](../pipelines/index.md#tools-overview).

### `POST /app/tools/telegram/link/start`

- Boundary: app auth required.
- Request: no body.
- Response schema: `AppTelegramLinkStartResponse`.
- Behavior: requires Telegram provider configuration, rotates/creates a link
  code for the authenticated user, and returns user-facing link instructions.
- Failure posture: returns `409` when Telegram provider is not configured.
- Side effects: writes Telegram link-code fields on `AionProfile`.
- Frontend caller: `api.startTelegramLink()`.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_telegram_client.py`.
- Related pipeline: [Telegram linking and transport](../pipelines/index.md#telegram-linking-and-transport).

### `GET /internal/state/inspect`

- Boundary: debug access required.
- Query: required `user_id`.
- Response: learned-state snapshot for the requested user.
- Behavior: enforces debug access and returns `_build_learned_state_snapshot`.
- Side effects: reads learned-state data; no route-owned writes expected.
- Frontend caller: none.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_runtime_policy.py`.
- Related pipeline: [Learned state overview](../pipelines/index.md#learned-state-overview).

### `POST /event`

- Boundary: public/runtime event ingress.
- Request: generic JSON payload consumed by `_handle_event_request()`.
- Query: optional `debug=true` compatibility mode.
- Response schema: `EventResponse`.
- Behavior:
  - without debug: runs normal event handling with `include_debug=False`
  - with debug: requires debug query compatibility to be enabled and delegates
    to internal debug ingress
- Side effects: normal runtime side effects for accepted events; debug compat
  telemetry may record allowed/blocked attempts.
- Frontend caller: none in `web/src/lib/api.ts`; app chat uses
  `/app/chat/message`.
- Tests: `backend/tests/test_event_normalization.py`,
  `backend/tests/test_api_routes.py`,
  `backend/tests/test_runtime_pipeline.py`,
  `backend/tests/test_debug_compat_telemetry.py`.
- Related pipeline: [External event ingress](../pipelines/index.md#external-event-ingress).

### `POST /event/debug`

- Boundary: shared debug ingress policy.
- Request: generic JSON payload consumed by `_handle_internal_debug_ingress()`.
- Response schema: `EventResponse`.
- Behavior: enforces shared debug ingress policy, runs internal debug ingress,
  and marks shared debug compatibility headers.
- Side effects: debug event execution can perform normal runtime memory/action
  side effects; headers expose debug posture, not secrets.
- Frontend caller: none.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_runtime_policy.py`,
  `backend/tests/test_debug_compat_telemetry.py`.
- Related pipeline: [Debug and incident evidence](../pipelines/index.md#debug-and-incident-evidence).

### `POST /internal/event/debug`

- Boundary: dedicated internal debug ingress.
- Request: generic JSON payload consumed by `_handle_internal_debug_ingress()`.
- Response schema: `EventResponse`.
- Behavior: runs internal debug ingress. The canonical path is represented in
  code by `DEBUG_INTERNAL_INGRESS_PATH`.
- Side effects: debug event execution can perform normal runtime memory/action
  side effects and may include debug/system/incident evidence depending on
  policy.
- Frontend caller: none.
- Tests: `backend/tests/test_api_routes.py`,
  `backend/tests/test_observability_policy.py`,
  `backend/tests/test_incident_evidence_bundle_script.py`.
- Related pipeline: [Debug and incident evidence](../pipelines/index.md#debug-and-incident-evidence).

### `POST /telegram/set-webhook`

- Boundary: operator/provider setup.
- Request schema: `SetWebhookRequest`.
- Response: provider client response from `TelegramClient.set_webhook(...)`.
- Behavior: uses request `secret_token` when provided, otherwise falls back to
  configured Telegram webhook secret, then calls Telegram provider webhook
  setup.
- Side effects: external Telegram provider mutation.
- Frontend caller: none.
- Tests: `backend/tests/test_telegram_client.py`,
  `backend/tests/test_api_routes.py`.
- Related pipeline: [Telegram linking and transport](../pipelines/index.md#telegram-linking-and-transport).

## Web Client Coverage

| Web Method | Endpoint | Response Type |
| --- | --- | --- |
| `api.getMe()` | `GET /app/me` | `AppMeResponse` |
| `api.register(...)` | `POST /app/auth/register` | `AppMeResponse` |
| `api.login(...)` | `POST /app/auth/login` | `AppMeResponse` |
| `api.logout()` | `POST /app/auth/logout` | `{ ok: boolean }` |
| `api.patchSettings(...)` | `PATCH /app/me/settings` | `AppSettings` |
| `api.resetData(...)` | `POST /app/me/reset-data` | `AppResetDataResponse` |
| `api.getChatHistory()` | `GET /app/chat/history` | `AppChatHistoryResponse` |
| `api.sendChatMessage(...)` | `POST /app/chat/message` | `AppChatMessageResponse` |
| `api.getPersonalityOverview()` | `GET /app/personality/overview` | `AppPersonalityOverviewResponse` |
| `api.getToolsOverview()` | `GET /app/tools/overview` | `AppToolsOverviewResponse` |
| `api.patchToolsPreferences(...)` | `PATCH /app/tools/preferences` | `AppToolsOverviewResponse` |
| `api.startTelegramLink()` | `POST /app/tools/telegram/link/start` | `AppTelegramLinkStartResponse` |
| `api.getHealth()` | `GET /health` | `AppHealthResponse` |

## Known API Documentation Gaps

- No generated OpenAPI artifact is checked in or linked from this reference.
- Flexible response schemas with `extra="allow"` still need dedicated shape
  docs for personality overview and tools overview.
- `GET /health` has a broad nested response assembled from policy snapshots;
  this file documents the sections, not every nested field.
- Generic event payload shape for `/event` and debug ingress is owned by
  event normalization/runtime contracts and needs a dedicated event contract
  reference.
- Route tests are mapped by file responsibility, not machine-readable endpoint
  metadata.
