# Dual-Loop Coordination Notes

## Purpose

This document records the near-term coordination direction for conscious and
subconscious runtime behavior without rewriting the canonical architecture
files.

Use it as a supplemental implementation note alongside:

- `docs/implementation/runtime-reality.md`
- `docs/planning/open-decisions.md`
- `docs/planning/next-iteration-plan.md`

The canonical design still lives in `docs/architecture/`.

---

## Coordination Goal

The repository is moving toward a runtime where:

- conscious processing remains the only path that can communicate directly with
  the user or execute external side effects
- subconscious processing can analyze, infer, and prepare proposals without
  becoming a second direct messaging loop
- bursty user conversations are assembled into coherent turns instead of
  producing one reply per raw message

This direction is currently planned through `PRJ-085..PRJ-097`.

---

## Attention Inbox

Planned direction:

- one explicit attention inbox accepts user-originated events, scheduler
  wakeups, and subconscious proposals
- conscious runtime wakes from attention items, not only from raw inbound
  chat messages
- subconscious runtime contributes proposals into the inbox flow rather than
  bypassing conscious evaluation

This keeps all wakeups explicit and traceable.

---

## Turn Assembly

The current runtime still processes one normalized event at a time.

Planned direction:

- rapid inbound messages from the same conversation can be coalesced into one
  assembled turn
- the runtime should track pending, claimed, and answered turn ownership
- duplicate reply risk should be reduced before delivery, not only after the
  fact

This is the main architectural answer to burst-message spam and fragmented
multi-message replies.

---

## Proposal Handoff

Subconscious processing should remain non-user-facing.

Planned direction:

- subconscious runtime may persist proposals such as:
  - `ask_user`
  - `research_topic`
  - `suggest_goal`
  - `nudge_user`
- proposals are not actions by themselves
- conscious runtime decides whether to accept, merge, defer, or discard a
  proposal before any user-visible or external effect occurs

This preserves the conscious/action boundary while still letting subconscious
processing shape future behavior.

---

## Tool Boundary

Planned direction:

- subconscious runtime may gain read-only retrieval or research capabilities
- subconscious runtime should not gain direct side-effect authority
- conscious runtime remains the only owner of outbound communication, external
  mutations, and user-visible execution

This keeps exploration and execution separate even if the subconscious path
gains richer research ability later.

---

## Internal Planning State

Goals and tasks remain integral internal planning state of the personality.

They are not intended to become detached external-only objects.

Planned direction:

- internal goals/tasks stay part of cognition, motivation, planning, memory,
  and reflection
- external systems such as calendar, task apps, and cloud drives are future
  authorized integration surfaces
- internal planning may later synchronize with those systems, but connected
  tools do not replace the internal planning model

This preserves the idea that the personality plans internally first and uses
external systems as tools, not as its cognitive core.

---

## Connector Boundary

Productivity integrations follow one explicit rule:

- user-authorized external connectors expose capabilities
- planning may reason about those capabilities
- action may execute against them only through explicit permission and action
  boundaries

Connector families in current contract scope:

- calendar systems
- task platforms such as ClickUp or Trello
- cloud drives such as Google Drive or OneDrive

The personality may also propose new integrations or capability expansions, but
it must not self-authorize access to outside systems.

---

## Proactive Guardrails

Planned proactive delivery should evaluate:

- quiet hours
- interruption cost
- cooldown
- recent outbound count
- unanswered proactive count
- current user context when available

This guardrail layer sits between subconscious proposals or scheduler wakeups
and any final user-facing message.

---

## Planned Work Map

- `PRJ-085..PRJ-092`
  - attention inbox
  - turn assembly
  - proposal handoff
  - subconscious read-only tool policy
  - proactive attention gating
  - dual-loop coordination regressions

- `PRJ-093..PRJ-097`
  - connector contracts
  - calendar boundary
  - external task-system adapters
  - connected-drive access
  - capability-expansion proposals

---

## Status

These notes describe the coordination direction and current implementation
baseline.

Current implementation status:

- contract scaffolding is now explicit in runtime graph state:
  - `attention_inbox`
  - `pending_turn`
  - `subconscious_proposals`
  - `proposal_handoffs`
- baseline Telegram burst coalescing now runs through a shared attention-turn
  coordinator with `pending|claimed|answered` ownership and queued no-op
  responses for non-owner burst events
- subconscious proposals are now persisted in durable storage with explicit
  lifecycle status and conscious handoff decisions
- subconscious research proposals now carry explicit read-only policy and
  allowed-tool bounds
- proactive scheduler events now pass through an explicit attention gate before
  delivery planning
- connector contracts now include permission-gate outputs plus typed calendar
  and task-system synchronization intents
- provider-backed connector execution is still intentionally deferred; current
  contracts keep integration authority inside action boundaries
