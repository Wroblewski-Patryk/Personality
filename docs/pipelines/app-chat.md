# App Chat Pipeline

Last updated: 2026-05-03

This reference documents the browser app chat flow from local UI state through
backend runtime execution and durable transcript projection.

Grounded in:

- `web/src/App.tsx`
- `web/src/lib/api.ts`
- `backend/app/api/routes.py`
- `backend/app/memory/repository.py`
- `backend/tests/test_api_routes.py`
- `backend/tests/test_memory_repository.py`
- `backend/tests/test_runtime_pipeline.py`

## Purpose

App chat is the first-party browser conversation path. It must feel immediate
in the UI while keeping durable conversation truth backend-owned through memory
and transcript projection.

## Trigger

- User submits chat text in the authenticated web shell.
- `web/src/App.tsx` creates a transient local user message with
  `delivery_state: "sending"`.
- The web client calls `api.sendChatMessage(text)`.

## Frontend Flow

| Step | File | Behavior |
| --- | --- | --- |
| Initial history load | `web/src/App.tsx`, `web/src/lib/api.ts` | Calls `api.getChatHistory()` and stores durable backend transcript items in `history`. |
| Local optimistic user turn | `web/src/App.tsx` | Adds a local user item before awaiting backend response. |
| Runtime send | `web/src/lib/api.ts` | `api.sendChatMessage(text)` calls `POST /app/chat/message`. |
| Delivered local user update | `web/src/App.tsx` | Replaces/updates local user item with returned event id and delivered state. |
| Local assistant reply | `web/src/App.tsx` | Adds transient assistant item from returned reply while durable history catches up. |
| History refresh | `web/src/App.tsx` | Calls `api.getChatHistory()` after send and reconciles local items against durable items. |
| Reconciliation | `reconcileLocalTranscriptItems` in `web/src/App.tsx` | Removes transient local items only when durable `message_id` or matching `(event_id, role)` exists. |

## Backend Routes

| Endpoint | Function | Responsibility |
| --- | --- | --- |
| `GET /app/chat/history` | `app_chat_history` | Requires app auth and returns `get_recent_chat_transcript_for_user(user_id, limit)`. |
| `POST /app/chat/message` | `app_chat_message` | Requires app auth, wraps text as an event with authenticated `user_id`, runs `_handle_event_request(..., include_debug=False)`, and returns reply/runtime summary. |

See [API Reference](../api/index.md) for request/response schemas.

## Runtime Handoff

`POST /app/chat/message` enters the [Foreground Runtime Pipeline](foreground-runtime.md)
with:

- source resolved through event handling
- authenticated app `user_id` in event metadata
- debug output disabled for the app route
- normal runtime side effects allowed through planning/action boundaries

The response returns:

- `event_id`
- `trace_id`
- canonical assistant `reply`
- optional runtime summary: role, motivation mode, action status, reflection
  trigger state

## Durable Transcript Projection

Durable transcript truth is projected from `AionMemory` by
`MemoryRepository.get_recent_chat_transcript_for_user()`.

Important repository helpers:

- `_project_memory_to_transcript_items`
- `_event_projects_to_transcript`
- `_assistant_projects_to_transcript`
- `_normalize_transcript_channel`
- `_is_conversation_turn_memory`

The projection can emit user and assistant transcript items from one memory
record while filtering internal/system rows.

## Data Read/Write

| Area | Tables/Data |
| --- | --- |
| Chat send | Writes `AionMemory` through foreground runtime and may enqueue `AionReflectionTask`. |
| History read | Reads `AionMemory` projected as transcript items. |
| User identity | Reads auth session/user and profile state. |
| Context | Reads profile, conclusions, relations, memory, goals/tasks, retrieval state as part of foreground runtime. |
| Post-send refresh | Reads durable transcript again to reconcile local UI state. |

See [Data Model Reference](../data/index.md) for table ownership.

## Failure Points

| Failure Point | Risk | Expected Handling |
| --- | --- | --- |
| Initial history load | Empty or failed history can make chat look broken | UI has loading/error/no-history states. |
| Auth expiry | App route rejects unauthenticated calls | Frontend surfaces API error and should return user to auth flow. |
| Runtime failure | Send request fails before assistant reply | Local user item can be marked failed and error surfaced. |
| Durable history lag | Backend reply returns before transcript projection refresh includes durable assistant item | Local assistant item remains transient until exact message or role-aware durable item appears. |
| Event-level reconciliation | Removing assistant too early when only user durable item exists | Reconciliation is role-aware through exact `message_id` or `(event_id, role)`. |
| Scheduler/internal memory rows | Internal prompts could appear as user-authored transcript | Repository projection helpers filter internal/system rows. |
| Cross-channel identity | Linked Telegram and app turns may share transcript; unlinked turns must not leak | Route/repository tests cover linked and unlinked Telegram transcript behavior. |

## Tests

| Test File | Coverage |
| --- | --- |
| `backend/tests/test_api_routes.py` | App chat history, auth scoping, latest ten chronological order, scheduler prompt hiding, linked/unlinked Telegram transcript behavior, app chat message runtime user id and UTC offset behavior |
| `backend/tests/test_memory_repository.py` | Recent chat transcript projection order, scheduler internal prompt hiding, proactive/internal row filtering, communication-boundary transcript evidence |
| `backend/tests/test_runtime_pipeline.py` | Shared transcript projection for API/Telegram turns, scheduler prompt exclusion, foreground runtime behavior behind chat |

## Related Docs

- [Pipeline Registry](index.md)
- [Foreground Runtime Pipeline](foreground-runtime.md)
- [API Reference](../api/index.md)
- [Data Model Reference](../data/index.md)
- [Traceability Matrix](../architecture/traceability-matrix.md)
- [Runtime Reality](../implementation/runtime-reality.md)

## Known Gaps

- No dedicated frontend e2e test suite is documented for chat send/history UI.
- The optimistic UI behavior is documented from `web/src/App.tsx`, but not
  protected by a stable frontend test.
- Long-message rendering and markdown behavior are covered by task history and
  backend/client code, but they are not split into this first pipeline pass.
- A future app-chat sequence diagram would make the local/durable transcript
  reconciliation easier to audit.
