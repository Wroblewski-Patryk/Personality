# Runtime Behavior Testing

## Purpose

This document defines how AION must be validated as a cognitive system, not
only as a collection of modules or passing unit tests.

The testing goal is to verify:

- real behavior
- architectural correctness
- continuity across time
- memory influence on later turns
- decision-making integrity
- graceful handling of failure, ambiguity, and noise

Unit tests alone are not sufficient proof of correctness.

---

## Core Principle

The primary testing question is not:

- does the code execute?

The primary testing question is:

- does the system behave correctly across time?

Architectural correctness requires past state to influence present reasoning
and future behavior in a traceable way.

---

## Required Testing Modes

### 1. System Debug Mode

The runtime must provide an internal testing/debug surface that exposes enough
structured state to verify the cognitive loop.

Minimum debug-visible fields:

- normalized event metadata
- perception output
- retrieved memory bundle
- retrieval governance posture when rollout-sensitive
- context summary
- motivation state
- selected role
- plan summary and explicit intents
- expression summary
- action result
- trace and event identifiers

Without this mode, the system is not behavior-testable.

Rules:

- this mode is for internal validation, not default public UX
- it must remain policy-gated
- it must preserve the action boundary and traceability rules from the core
  architecture
- when retrieval-family rollout is under governance, `system_debug` should also
  expose the owner-level posture needed to explain whether a source family is
  baseline, optional, or enabled ahead of baseline

### 2. User Simulation Mode

The system must also be tested through natural conversations without debug
payloads.

This mode validates:

- user-facing realism
- coherence of responses
- continuity across turns
- tone and personality stability

---

## Global Test Structure

Every meaningful behavior area should be validated through the following
sequence whenever the feature exists:

1. Implementation check
2. Isolated behavior test
3. Integration test
4. Persistence or time-based test
5. Failure test

If a feature is not implemented yet, the test should be marked as `skip`
instead of being silently ignored.

---

## Test Output Contract

Behavior-driven tests should emit or record results in a structured format:

```json
{
  "test_id": "T2.4",
  "status": "pass|fail|skip",
  "reason": "...",
  "trace_id": "...",
  "notes": "..."
}
```

This contract is intended for automated harnesses, debug tooling, and release
readiness workflows.

---

## Test Groups

## Group 1 - Event System

Run when event normalization exists.

Validate:

- raw input becomes canonical event structure
- event shape is consistent across supported sources
- event metadata includes `event_id`, `trace_id`, timestamp, and payload

Pass condition:

- all required fields exist and remain traceable across the turn

---

## Group 2 - Memory System

Run when memory write or retrieval exists.

Validation phases:

### Memory write

- confirm durable record creation after a meaningful user turn
- confirm stored summary is specific and non-generic

### Memory retrieval

- confirm a later related turn retrieves the relevant prior memory
- confirm retrieval is visible in debug surfaces or logs

### Memory influence

- confirm retrieved memory changes context or response instead of being a
  passive unused artifact

### Persistence over time

- confirm delayed recall still works after a simulated or real time gap

Fail conditions:

- write-only memory
- generic summaries
- retrieval without later influence
- generic follow-up response where prior state should matter

---

## Group 3 - Perception

Run when perception exists.

Validate:

- intent detection
- topic detection
- ambiguity detection
- affective placeholder or classifier outputs when applicable

Pass condition:

- perception produces structured signals that match the input meaning closely
  enough for downstream cognition to remain trustworthy

---

## Group 4 - Context System

Run when context construction exists.

Validate:

- multi-message coherence
- integration of memory into context summary
- linkage to active goals or tasks when those systems exist

Pass condition:

- context explains the current turn using relevant history and constraints
  rather than isolated-message interpretation

---

## Group 5 - Motivation

Run when motivation exists.

Validate:

- importance and urgency differentiation
- mode selection consistency
- alignment with risk-heavy versus low-signal input

Pass condition:

- materially urgent turns receive stronger motivation posture than trivial
  turns

---

## Group 6 - Planning

Run when planning exists.

Validate:

- plan structure
- explicit goal or step shaping
- separation between planning intent and action execution

Fail condition:

- output is generic advice with no usable plan structure when the input clearly
  calls for planning

---

## Group 7 - Action System

Run when action execution exists.

Validate:

- durable writes or side effects happen only through the action boundary
- repeated identical requests remain idempotent where required
- action traces are visible in debug or persistence layers

Pass condition:

- action succeeds without duplicate side effects or silent state drift

---

## Group 8 - Expression

Run when expression exists.

Validate:

- tone consistency with selected role and motivation
- language consistency with user and identity context
- message quality in both debug and user-facing modes

---

## Group 9 - Reflection

Run when reflection exists.

Validate:

- pattern detection
- conclusion generation
- gradual adaptive updates such as theta, relation state, or other slower
  behavioral signals

Pass condition:

- updates are evidence-based and gradual, not abrupt or self-reinforcing noise

---

## Group 10 - System Continuity

This group is always required.

Validate:

- multi-session continuity
- personality stability across breaks in conversation
- continuity of goals, memory, language, and tone

The system is not considered alive if continuity collapses between sessions.

---

## Failure Scenarios

Behavior validation must also cover:

- contradiction input
- missing data
- noisy or chaotic input
- fallback paths when memory or inference signals are weak

Pass condition:

- the runtime stays controlled, explainable, and non-chaotic under stress

---

## Release And Readiness Expectation

Feature work is not complete when only unit and contract tests pass.

For behavior-sensitive subsystems such as memory, reflection, planning,
language handling, relation influence, and proactive logic, done-state should
also include:

- at least one scenario-level behavior test
- proof that debug surfaces are sufficient to explain the observed behavior
- clear `skip` markers for intentionally unimplemented capability
- evidence that stored state changes later reasoning or response behavior

Post-convergence minimum scenario families now also include:

- no-UI `v1` life-assistant workflow continuity:
  reminder capture -> learned proactive preference -> daily planning anchor ->
  scheduler-owned proactive follow-up
- metadata-only role/skill boundary behavior
- connector execution and guardrail posture
- approved bounded tool-slice behavior for:
  - DuckDuckGo web search
  - generic HTTP page read
  - ClickUp task update
- proactive delivery-ready versus anti-spam-blocked posture
- deferred reflection enqueue and non-blocking background expectations
- exported `incident_evidence` consumption through smoke or validation tooling
  whenever observability-sensitive runtime or release slices change
- durable-attention burst-coalescing proof for the live
  `durable_inbox + repository_backed` production baseline

Current scenario anchors:

- `T13.1`: no-UI `v1` reminder capture -> continuity -> proactive follow-up
- `T14.1`: analyst-driven bounded web search via action-owned tool path
- `T14.2`: analyst-driven bounded page read via action-owned tool path
- `T14.3`: executor-aligned ClickUp update via action-owned connector path
- `T15.1`: work-partner organization via bounded search plus ClickUp update
- `T15.2`: work-partner decision support via bounded page-read browsing
- `T16.1`: work-partner ClickUp task listing
- `T16.2`: work-partner Google Calendar availability reads
- `T16.3`: work-partner Google Drive metadata listing
- `T17.1`: bounded search knowledge recall through persisted tool-grounded
  conclusions
- `T17.2`: organizer-tool snapshot recall through persisted tool-grounded
  conclusions
- `T18.1`: final no-UI `v1` website-reading then recall flow
- `T18.2`: final no-UI `v1` organizer review then follow-up focus flow
- `T19.1`: due planned-work delivery re-enters the normal foreground runtime
  path and resolves proposal handoff explicitly
- `T19.2`: recurring planned work is reevaluated by scheduler-owned cadence
  and advanced after foreground delivery without opening a second scheduler
  lane

Boundary note:

- `T18.2` and the organizer daily-use family remain valid extension evidence
  for later tool-readiness and work-partner quality
- after the post-`PRJ-642` product revision, they should not by themselves
  redefine the core no-UI `v1` blocker set unless architecture truth is
  explicitly revised again
- durable-attention burst-coalescing regression in API/runtime integration
  coverage, paired with:
  - `incident_evidence.policy_posture["attention"]`
  - `incident_evidence.policy_posture["runtime_topology.attention_switch"]`
  - release-smoke validation of the same durable-attention fields from
    `/health`

When behavior validation is used during release or incident triage, the
resulting artifact should attach to the same operator incident-evidence bundle
instead of creating a separate ad hoc evidence family.

Bundle expectation for behavior-sensitive incident work:

- `incident_evidence.json` explains the concrete runtime turn or smoke request
- `health_snapshot.json` captures the selected policy posture around that run
- optional `behavior_validation_report.json` proves scenario-level behavior
  when the incident touches memory, planning, proactive cadence, connector
  posture, or other behavior-sensitive seams
- when release smoke validates `-IncidentEvidenceBundlePath`, the bundle
  directory itself becomes part of the repeatable evidence contract

For dedicated debug-ingress retirement work, behavior validation must also
treat incident evidence as a policy gate:

- CI posture must fail if `incident_evidence.policy_posture.runtime_policy`
  stops proving dedicated-admin-only debug ingress
- CI posture must fail if incident evidence no longer records an explicit
  rollback-exception state through
  `shared_debug_route_break_glass_only` or
  `shared_debug_route_disabled_with_debug_payload_off`

---

## Final Principle

AION is correct only when:

`past -> influences -> present -> shapes -> future`

If this loop is broken, the system may still compile, log, or persist data,
but it is not behaving like the intended architecture.
