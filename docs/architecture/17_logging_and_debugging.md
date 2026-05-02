# Logging and Debugging

## Purpose

This document defines how to observe, debug, and understand AION during runtime.

Without proper logging:

- system behavior becomes invisible  
- debugging becomes guesswork  
- errors become hard to trace  
- development slows down  

Logging is not optional.  
It is part of the architecture.

---

## Core Principle

Everything important must be observable.

If you cannot see:

- what happened  
- why it happened  
- what the system decided  

then you cannot trust or improve the system.

---

## What Must Be Logged

Every runtime cycle should log:

- event_id  
- trace_id  
- source  
- timestamp  
- selected role  
- motivation state  
- action result  
- memory write status  
- total execution time  

---

## Stage-Level Logging

Each stage should log:

- stage name  
- input summary  
- output summary  
- duration  
- errors (if any)  

---

## Example Runtime Log

{
  "trace_id": "trace_123",
  "event_id": "evt_456",
  "stage": "planning",
  "duration_ms": 120,
  "status": "success"
}

---

## Trace Concept

Every event should have a trace_id.

trace_id connects:

- all stages  
- all logs  
- all actions  

This allows full tracking of a single runtime cycle.

---

## Log Levels

### INFO

Normal operation:

- event received  
- stage completed  
- action executed  

---

### WARNING

Potential issues:

- missing data  
- fallback used  
- partial failure  

---

### ERROR

Failures:

- stage failure  
- API failure  
- DB failure  

---

### DEBUG

Detailed internal data:

- intermediate values  
- internal state  
- raw outputs  

Used during development.

---

## Logging Strategy

- log at every stage  
- keep logs structured  
- avoid excessive noise  
- focus on important signals  

---

## Structured Logging

Logs should be structured, not plain text.

Example:

{
  "stage": "context",
  "status": "success",
  "duration": 80,
  "summary": "context built"
}

---

## Error Handling Strategy

When error occurs:

1. catch error  
2. log error  
3. return safe fallback  
4. continue system if possible  

System must not crash silently.

---

## Debugging Workflow

When something breaks:

1. find trace_id  
2. follow logs step by step  
3. identify failing stage  
4. inspect input/output  
5. fix issue  
6. retest  

---

## Common Debug Problems

### Missing Context

- memory not retrieved  
- wrong event structure  

---

### Wrong Role Selection

- motivation incorrect  
- context incomplete  

---

### Bad Responses

- expression layer issue  
- incorrect planning  

---

### Memory Issues

- not stored  
- not retrieved  
- wrong importance  

---

## Observability Goals

You should be able to answer:

- what happened?  
- why did it happen?  
- what did system decide?  
- what changed after?  

Passive/active trigger evidence must preserve skipped, delayed, blocked, and
failed observer-admitted work in scheduler cadence evidence without forcing a
user-visible expression. The evidence shape should stay bounded to metadata
such as source, work id, user id, work kind, channel, outcome, reason, and
`expression_visible`.
Release smoke and incident-evidence bundle validation must consume the same
planned-action observer posture exposed under proactive policy evidence:
`policy_owner=planned_action_observer_policy`, latest observer state,
`empty_result_behavior`, and due/actionable counts. Missing observer posture is
release drift, not a manual-interpretation warning.

---

## V1 Release Evidence

No-UI `v1` acceptance should be readable from one backend-facing evidence
bundle, not inferred manually from unrelated logs.

Minimum `v1` release evidence categories:

1. conversation reliability posture
2. life-assistant workflow behavior proof
3. learned-state inspection readiness
4. approved tooling and work-partner posture

Canonical evidence surfaces for that bundle may include:

- `/health.v1_readiness`
- `/health.conversation_channels.telegram`
- `/health.learned_state`
- `/health.api_readiness`
- debug/exported `incident_evidence.policy_posture["v1_readiness"]`
- behavior-validation scenario anchors for the current `v1` baseline

`/health.v1_readiness` is also the final no-UI `v1` acceptance-bundle surface.
It should expose:

- one explicit bundle owner
- named final gate states for:
  - conversation reliability
  - learned-state inspection
  - website reading
  - tool-grounded learning reuse
  - time-aware planned work
  - deploy parity
- canonical runtime surfaces for each gate

Organizer daily-use posture may still be mirrored from
`/health.connectors.organizer_tool_stack` for operator convenience, but it
should be labeled as extension readiness rather than a core no-UI `v1` gate.
Core gate truth and extension posture must stay distinguishable in both live
`/health.v1_readiness` and exported incident evidence.

For the time-aware planned-work gate, the minimum machine-visible posture is:

- `time_aware_planned_work_policy_owner`
- `time_aware_planned_work_delivery_path`
- `time_aware_planned_work_recurrence_owner`
- `time_aware_planned_work_gate_state`
- parity between `/health.v1_readiness` and exported
  `incident_evidence.policy_posture["v1_readiness"]`

When extension posture is mirrored into the same `v1_readiness` surface, the
minimum rule is:

- extension-only fields must not silently redefine the core final gate result
- organizer daily-use or channel-specific delivery quality must remain
  machine-visible without pretending to be a required cognition blocker for the
  post-`PRJ-642` core boundary

---

## Tools

Basic:

- console logs  
- file logs  

Advanced (future):

- dashboards  
- log aggregation  
- tracing systems  

---

## Performance Logging

Track:

- response time  
- stage duration  
- memory retrieval time  
- LLM call time  

This helps optimization.

---

## Debug Mode

System should support debug mode:

- more logs  
- detailed outputs  
- no silent failures  

Runtime behavior-validation baseline requires two explicit modes:

- `system_debug`: internal payload surface with normalized event metadata,
  perception, retrieved memory bundle, context, motivation, role, plan intents,
  expression, and action result
- `user_simulation`: natural conversation checks without debug payload exposure

Behavior-driven scenario outcomes should be recorded in the canonical format:

```json
{
  "test_id": "T2.4",
  "status": "pass|fail|skip",
  "reason": "...",
  "trace_id": "...",
  "notes": "..."
}
```

Current post-convergence diagnostics also require:

- `/health.affective` to expose heuristic affective-input ownership separately
  from assessment rollout posture
- `system_debug.adaptive_state.affective_input_policy` and
  `system_debug.adaptive_state.affective_resolution` to show how the live turn
  moved from heuristic input to final affective result
- `/health.observability` to expose the shared export-policy owner and whether
  machine-readable incident evidence is actually available beyond local logs
- debug-mode runtime responses to expose `incident_evidence` with:
  - `trace_id`, `event_id`, `duration_ms`, and `stage_timings_ms`
  - machine-readable posture snapshots for runtime policy, retrieval,
    scheduler external ownership, reflection supervision, and connector
    execution baseline
  - machine-readable learned-state inspection posture for `learned_state`
  - machine-readable conversation-channel posture for
    `conversation_channels.telegram`
  - machine-readable durable-attention posture for `attention`
  - machine-readable runtime-topology attention-switch posture for
    `runtime_topology.attention_switch`

Durable-attention production proof is now part of the logging/debugging
baseline too:

- public `/health.attention` proves the live durable owner and
  repository-backed contract-store posture
- public `/health.runtime_topology.attention_switch` proves the selected
  attention owner switch and production-default readiness
- exported `incident_evidence.policy_posture["attention"]` and
  `incident_evidence.policy_posture["runtime_topology.attention_switch"]`
  carry the same owner-level durable-attention evidence for release and
  incident review
- behavior-validation CI gates must fail when that durable-attention posture is
  missing or invalid, so burst-coalescing proof does not regress silently

For the no-UI `v1` release baseline, conversation reliability is now also an
operator-visible evidence contract:

- `/health.conversation_channels.telegram` must expose:
  - policy owner
  - round-trip readiness posture
  - token/secret configuration posture
  - last ingress state
  - last delivery state
- ingress telemetry must distinguish:
  - received
  - rejected
  - queued
  - processed
  - runtime-failed
- delivery telemetry must distinguish:
  - attempted
  - sent
  - missing_chat_id
  - telegram_api_error
  - delivery_exception

## Operator Incident Evidence Bundle

When runtime or release investigation requires more than local logs, operators
must treat incident evidence as one bounded artifact bundle rather than a set
of unrelated JSON snippets.

Canonical bundle contents:

- `manifest.json`
  - bundle schema version
  - capture timestamp
  - capture mode (`incident|release_smoke|behavior_validation`)
  - optional `trace_id` and `event_id`
- `incident_evidence.json`
  - exported machine-readable runtime evidence from the debug surface
- `health_snapshot.json`
  - captured `GET /health` payload from the same investigation window
- optional `behavior_validation_report.json`
  - attached only when behavior validation was run for the same incident or
    release investigation

Conversation-reliability evidence is part of that bundle contract too:

- `incident_evidence.json` must carry
  `policy_posture["conversation_channels.telegram"]`
- bundle validation must fail when Telegram conversation posture is missing or
  carries an invalid round-trip baseline

Learned-state inspection evidence is part of that bundle contract too:

- `incident_evidence.json` must carry `policy_posture["learned_state"]`
- that posture must expose:
  - `policy_owner = learned_state_inspection_policy`
  - `internal_inspection_path = /internal/state/inspect`
- bundle validation must fail when learned-state posture is missing or drifts
  away from the shared owner/path contract

Backend API-readiness evidence for later `v2` UI bootstrap is now frozen too:

- `/health.api_readiness` must expose:
  - `policy_owner = v2_backend_api_readiness_policy`
  - stable health surfaces for learned-state, role-skill, connectors, and
    `v1` readiness
  - the canonical internal inspection path
  - the canonical current-turn debug path
- internal `GET /internal/state/inspect?user_id=...` must carry the same
  `api_readiness` snapshot so backend inspection and health posture do not
  drift between admin or future UI entrypoints

Canonical naming posture:

- artifact root should be operator-readable and trace-oriented:
  `artifacts/incident_evidence/<captured_at_utc>_<trace_id_or_event_id>/`
- file names inside the bundle stay fixed so later tooling can consume them
  without path heuristics

Retention baseline:

- keep the most recent successful release-evidence bundle
- keep the most recent failing release or incident bundle
- keep active incident bundles until the incident and rollback follow-up are
  closed
- do not treat console logs alone as sufficient incident evidence once bundle
  export exists

Producer or retrieval boundary:

- the debug/runtime surface remains the source of truth for
  `incident_evidence.json`
- `/health` remains the source of truth for `health_snapshot.json`
- the canonical collection helper is now
  `scripts/export_incident_evidence_bundle.py`
- the helper may collect both runtime-owned files into one bundle, but it must
  not redefine their ownership or schema independently of those runtime
  surfaces

## Dedicated Debug Ingress Retirement Gate

The long-term debug-ingress owner is the dedicated internal admin route:

- `POST /internal/event/debug`

Shared debug surfaces remain compatibility-only:

- `POST /event/debug`
- `POST /event?debug=true`

Retirement cutover posture is fixed as:

- `dedicated_internal_admin_route_primary_shared_routes_break_glass_then_remove`

Shared-route retirement gate checklist:

- `normal_operator_debug_uses_dedicated_internal_admin_route`
- `shared_event_debug_route_is_break_glass_only_or_disabled`
- `query_debug_compatibility_route_disabled`
- `release_smoke_green_for_dedicated_admin_debug_path`
- `rollback_notes_cover_shared_debug_break_glass_reenablement`

Machine-visible gate state belongs to `/health.runtime_policy` through:

- `event_debug_shared_ingress_retirement_target`
- `event_debug_shared_ingress_retirement_cutover_posture`
- `event_debug_shared_ingress_retirement_gate_checklist`
- `event_debug_shared_ingress_retirement_gate_state`
- `event_debug_shared_ingress_retirement_blockers`

Release and validation evidence for this retirement lane must also prove the
same posture from exported incident evidence, not only from `/health`:

- release smoke must validate dedicated-admin-only debug posture directly from
  live `incident_evidence.policy_posture.runtime_policy`
- bundle verification must validate the same posture from
  `incident_evidence.json`
- behavior-validation CI gates must fail when incident evidence drifts away
  from dedicated-admin-only posture or omits an explicit rollback-exception
  state (`shared_debug_break_glass_only|shared_debug_disabled`)
- `event_debug_shared_ingress_retirement_ready`

---

## Final Principle

If you cannot observe the system,
you cannot control or improve it.

Logging turns AION from a black box into a transparent system.
