# Runtime Flow

## Purpose

This document defines the canonical runtime flow of AION.

It describes:

- what enters the system
- how the foreground loop processes a turn
- how the background loop learns from completed turns
- which stage owns which responsibility

This file defines the intended cognitive order.
Implementation-specific shortcuts or transitional wiring are documented outside `docs/architecture/`.

---

## Core Principle

AION is a stateful event-processing system.

Every foreground cycle follows one canonical rule:

`event -> interpretation -> expression -> action -> memory -> reflection trigger`

The system always reasons from current state, not from an empty prompt.

---

## Runtime Modes

AION operates in two modes:

### 1. Foreground Runtime

Handles live interaction.

Examples:

- user message
- API request
- explicit runtime trigger

This path should stay responsive and user-facing.

### 2. Background Runtime

Handles delayed cognition.

Examples:

- reflection
- planned-work reevaluation
- conclusion maintenance
- theta adjustment
- relation updates

This path should never block foreground response.

---

## Foreground Runtime - Canonical Flow

### Step 1. Event Received

The system receives a raw input from a source such as:

- Telegram
- API
- scheduler
- internal trigger

Raw payloads are not yet part of cognition.

### Step 2. Event Normalization

Input is converted into the canonical event structure.

This creates:

- event_id
- source and subsource
- timestamp
- normalized payload
- trace metadata

Only normalized events enter the cognitive pipeline.

### Step 2a. Attention Intake And Turn Assembly

Before the foreground stage graph runs, the attention boundary prepares the
candidate turn.

This boundary owns:

- attention inbox intake (`pending|claimed|answered|deferred`)
- conversation-key grouping for burst traffic
- pending-turn assembly (`item_ids`, `assembled_text`, ownership state)
- intake of due planned-work prompts after background reevaluation

This boundary does not own side effects.
It only prepares the conscious turn input contract.

### Step 3. Runtime State Initialization

The runtime prepares the initial state for the turn.

At minimum, the state should contain:

- the normalized event
- identity baseline
- adaptive state such as theta
- working placeholders for perception, context, motivation, role, plan, expression, and action

The initialized state should remain orchestration-agnostic so the same contract
can run in a direct orchestrator or a graph runtime.

### Step 4. Identity and State Baseline Load

Before deeper cognition, AION loads the stable baseline needed for interpretation.

This can include:

- identity
- auth-owned human-facing identity facts such as linked display name
- recent memory
- semantic conclusions
- theta
- active goals
- active tasks
- current-turn timestamp posture and bounded tool-readiness posture needed for
  truthful foreground answers

This is the continuity layer of the turn.

### Step 5. Perception

Perception determines what happened.

Typical output:

- event type
- topic
- intent
- ambiguity
- initial salience
- language signal
- affective assessment placeholder (`affect_label`, `intensity`,
  `needs_support`, `confidence`, `source`, `evidence`)

Perception recognizes the event but does not decide what to do.

### Step 6. Memory Retrieval

The runtime retrieves relevant memory for the event.

Typical retrieval layers:

1. episodic layer (recent turns and payload traces)
2. semantic layer (stable conclusions)
3. affective layer (support patterns and affective continuity signals)
4. operational layer (runtime preferences, active goals, active tasks, milestone state)

Retrieved memory must be filtered and compressed.

### Step 7. Context Construction

Context combines:

- current event
- perception output
- retrieved memory
- identity
- goals and tasks
- theta

The output should explain:

- what is happening
- why it matters
- what background matters now
- what constraints or risks are present
- which bounded foreground truths are already available for this turn

### Step 8. Motivation Evaluation

Motivation determines how strongly the system should care.

Typical dimensions:

- importance
- urgency
- valence
- arousal
- mode

Motivation sets the turn posture but does not yet choose wording or side effects.

### Step 9. Role Selection

The runtime selects the role that best fits the current situation.

Role selection depends on:

- context
- motivation
- user need
- goal relevance
- identity

Role affects how AION behaves, not who AION is.

### Step 10. Planning

Planning turns understanding into intended next steps.

Planning should answer:

- what is the turn goal?
- what ordered steps make sense?
- is response needed?
- is side-effect execution needed?
- should future work be scheduled, updated, snoozed, cancelled, or completed?
- which subconscious proposals are accepted, deferred, merged, or discarded?
- which connector permission gates apply to proposed external operations?
- which explicit domain intents (if any) should action execute?

Planning proposes. It does not execute.

Proposal-lifecycle ownership in this stage:

- planning is the canonical owner of conscious proposal handoff decisions
  (`accept|merge|defer|discard`)
- planning may mark accepted proposals for downstream intent shaping
- planning must not execute proposal side effects directly

### Step 11. Expression

Expression forms the outward communicative result of the turn.

It decides:

- message content
- tone
- structure
- language
- channel adaptation

Expression answers "what and how to communicate."
It also emits the explicit response-execution handoff consumed by action.

Foreground truthfulness rules in this step:

- expression may answer current-turn name or time questions directly from
  foreground truth when those facts are already loaded
- expression must not deny memory continuity, current-turn time awareness, or
  bounded page-read/search capability when the active turn already carries
  those facts
- when action-owned bounded read results exist in the same turn, the outward
  reply may summarize them without moving execution authority out of action

### Step 12. Action

Action performs the actual side effects.

Examples:

- send the prepared response
- execute explicit domain intents from planning
- enforce proactive attention-gate and connector permission-gate outcomes
- create or update tasks
- trigger background work
- call an external integration

Action answers "what is executed in the world or in durable state."
Action consumes the explicit response-execution handoff as its delivery input.

### Step 13. Episodic Memory Write

After the turn completes, the system stores an episode.

The episode should preserve at least:

- event summary
- context summary
- role used
- motivation snapshot
- plan summary
- expression summary
- action result
- importance or salience

### Step 14. Reflection Trigger

After episode persistence, the system emits a signal for future reflection.

Foreground runtime ends here.
Reflection itself belongs to the background loop.

---

## Foreground Ownership Boundary (Target State)

Foreground convergence follows one explicit ownership split:

- runtime-owned pre-graph segment: baseline load and state preparation
- graph-owned segment: canonical stage graph (`perception -> ... -> action`)
- runtime-owned post-graph segment: episodic memory write and reflection trigger

The detailed ownership and migration invariants are defined in
`docs/architecture/16_agent_contracts.md` under the foreground boundary
contract.

## Dual-Loop Ownership Boundary (Target State)

Dual-loop execution keeps one explicit ownership split:

- attention boundary owns inbox state and pending-turn assembly
- planning owns conscious proposal handoff decisions
- action owns user-visible execution after planning decisions and gates
- subconscious/background paths may propose, but never directly execute

This split keeps turn assembly and proposal lifecycle durable without blurring
the action boundary.

---

## Adaptive Influence Governance Boundary

Adaptive signals (`affective`, `relation`, `preference`, `theta`) must pass
through one governed influence policy before they shape foreground behavior.

Policy requirements:

- influence is evidence-gated (low-confidence signals remain descriptive-only)
- precedence is explicit (`affective` before relation/preference, `theta` last)
- ambiguous-turn tie-break use is explicit and stage-bounded
- action-boundary and permission-gate contracts remain unchanged

Detailed evidence thresholds and stage-level guardrails are defined in
`docs/architecture/16_agent_contracts.md` under adaptive influence governance.

---

## Background Runtime - Canonical Flow

### Step 1. Reflection Trigger or Schedule

The background loop starts because:

- a new episode was stored
- a reflection schedule fires
- explicit reflection was requested
- a scheduler cadence tick reopens time-aware planned work for reevaluation

### Step 2. Planned-Work Reevaluation

Before slower reflection-only work, the background runtime may reevaluate
durable planned work against current context and current time.

Typical inputs:

- current timestamp and timezone posture
- active goals and tasks
- existing planned-work items
- quiet-hour or delivery-boundary policy
- recent user activity

Typical outcomes:

- keep the item pending
- mark the item due
- reschedule the item
- cancel the item
- emit a bounded attention item or proposal for later foreground handling
- reopen a bounded `research_window` as the same kind of foreground handoff
  rather than as an autonomous background browsing loop

Background reevaluation must not send user-visible messages directly.
If something becomes due, it still crosses into the normal attention ->
planning -> expression -> action path.

### Step 3. Reflection Scope Load

The system loads the material needed for pattern analysis:

- recent episodes
- existing conclusions
- theta state
- relation state
- goal and task progress

### Step 4. Pattern Analysis

The background loop searches for:

- repetition
- preference signals
- success patterns
- failure patterns
- friction and blockers

### Step 5. Conclusion Generation

Patterns are converted into more stable conclusions.

Examples:

- preference conclusions
- collaboration conclusions
- role tendencies
- goal progress conclusions

### Step 6. Adaptive State Update

When justified, reflection updates slower-changing adaptive state such as:

- theta
- relation notes
- goal progress signals
- milestone signals

These updates should be gradual and evidence-based.

### Step 7. Reflection Persistence

The system persists the conclusions and updated adaptive state so future foreground turns can use them.

Background runtime ends here.

---

## Runtime State Flow Summary

Foreground:

`event -> normalize -> attention intake/turn assembly -> load baseline -> perceive -> retrieve memory -> build context -> evaluate motivation -> select role -> plan -> express -> act -> write memory -> trigger reflection`

Background:

`trigger -> reevaluate planned work -> load reflection scope -> analyze patterns -> update conclusions and adaptive state -> persist reflection outputs`

---

## Foreground vs Background Responsibility Split

### Foreground runtime owns

- speed
- clarity
- user-facing communication
- direct side effects
- episodic memory creation

### Background runtime owns

- consolidation
- adaptation
- pattern detection
- slower behavioral refinement

This split keeps AION fast without becoming stateless.

---

## Background Topology Ownership

Background reflection topology keeps one explicit ownership split:

- foreground runtime owns durable reflection enqueue after episode persistence
- reflection worker/scheduler ownership is mode-dependent
  (`in_process` immediate dispatch or `deferred` external dispatch)
- queue and retry semantics stay durable and mode-independent

This topology allows worker deployment shape to evolve without changing
reflection semantics or foreground guarantees.

---

## Failure Handling

### Foreground failure rules

If a foreground stage fails:

- preserve traceability
- return a controlled fallback where possible
- avoid silent loss of the event
- still preserve memory when safely possible

### Background failure rules

If reflection fails:

- do not block foreground runtime
- log the failure
- preserve retry or reprocessing capability
- avoid losing the reflection signal

---

## Runtime Invariants

These rules must remain true:

1. every raw input becomes a normalized event before deeper reasoning
2. only the Action layer performs side effects
3. expression shapes communication before action executes it
4. every completed foreground cycle attempts episodic memory persistence
5. reflection does not block user-facing response
6. identity changes more slowly than theta
7. stored conclusions influence future behavior
8. adaptive signals influence foreground behavior only through explicit
   governance policy surfaces

If these invariants break, runtime and architecture are drifting apart.

---

## Minimal MVP Runtime

The smallest viable AION runtime still requires:

Foreground:

- event normalization
- context construction
- motivation
- planning
- expression
- action
- episodic memory

Background:

- simple reflection
- conclusion maintenance
- small adaptive updates

That is enough to prove continuity across time.

---

## Final Principle

Runtime flow is where architecture becomes operational.

If the flow is clear:

- implementation can stay honest
- debugging can stay structured
- growth can stay controlled

If the flow is unclear, the system remains theory.
