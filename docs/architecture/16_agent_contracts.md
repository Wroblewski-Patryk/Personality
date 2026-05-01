# Agent Contracts

## Purpose

This document defines the canonical contracts between AION stages.

It exists to keep:

- stage boundaries explicit
- data flow predictable
- implementation aligned with architecture

These contracts describe cognitive responsibilities.
Transport- or endpoint-specific envelopes belong outside `docs/architecture/`.

---

## Core Principle

Every stage must:

- receive structured input
- return structured output
- own one responsibility
- avoid hidden side effects

No stage should absorb the responsibilities of another stage.

---

## Shared Runtime State

Stages receive only the subset of state they need.

Canonical shared runtime state may include:

```json
{
  "event": {},
  "identity": {},
  "memory": {
    "episodic": [],
    "semantic": [],
    "affective": [],
    "operational": {}
  },
  "conclusions": [],
  "theta": {},
  "affective": {},
  "goals": [],
  "tasks": [],
  "planned_work": [],
  "attention_inbox": [],
  "pending_turn": {},
  "background_adaptive_outputs": {},
  "subconscious_proposals": [],
  "proposal_handoffs": [],
  "connector_capabilities": [],
  "connector_permission_gates": [],
  "perception": {},
  "context": {},
  "motivation": {},
  "role": {},
  "plan": {},
  "expression": {},
  "action_result": {}
}
```

---

## Graph Compatibility Boundary

Foreground contracts should stay compatible with graph orchestration.

Minimum compatibility rules:

1. one shared runtime state object carries stage inputs and outputs
2. each stage reads only its required fields and writes only its own output
3. stage outputs keep stable key names (`perception`, `context`, `motivation`,
   `role`, `plan`, `expression`, `action_result`) during migration
4. conversion between runtime result and graph state is explicit and testable

These rules allow incremental migration from a direct orchestrator to LangGraph
without changing stage responsibilities.

---

## Behavior Validation Debug Surface Contract

Internal behavior validation requires a dedicated `system_debug` surface that
remains policy-gated and separate from default public UX payloads.

Dedicated admin-debug ingress target:

1. `POST /internal/event/debug` is the long-term admin/operator ingress for
   full runtime debug payloads
2. shared `POST /event/debug` and compatibility `POST /event?debug=true`
   remain transitional surfaces only
3. `/health.runtime_policy.event_debug_admin_*` and
   `event_debug_shared_ingress_retirement_*` are the machine-visible contract
   for dedicated-admin posture versus remaining compatibility blockers

Minimum `system_debug` fields:

1. normalized event metadata plus `event_id` / `trace_id`
2. perception output
3. retrieved memory bundle (`episodic`, `semantic`, `affective`, `relations`)
   plus retrieval diagnostics
4. context summary
5. motivation state
6. selected role
7. plan summary with explicit `domain_intents`
8. expression summary
9. action result
10. adaptive-state summary (`background_adaptive_outputs`,
    retrieval-depth posture, theta influence, selected skill metadata, and
    role/skill boundary policy)

Behavior tests should pair that internal mode with user-simulation mode
(no debug payloads) so correctness is validated both structurally and
user-facing.

---

## Behavior Feedback Interpretation Contract

Natural feedback about AION's own behavior is exposed as descriptive
foreground interpretation before any durable adaptation can occur.

Minimum behavior-feedback item shape:

```json
{
  "feedback_target": "interaction_ritual|contact_cadence|interruption_tolerance|response_style|collaboration|context_continuity|unknown",
  "feedback_polarity": "correction|approval|observation|unclear",
  "suggested_relation_type": "optional relation family",
  "suggested_relation_value": "optional relation value",
  "confidence": 0.0,
  "evidence": [],
  "source": "communication_boundary_observation"
}
```

Contract rules:

1. perception may expose `behavior_feedback` as current-turn interpretation.
2. `system_debug.behavior_feedback` mirrors that interpretation for behavior
   validation and incident evidence.
3. planning may consume structured behavior feedback and emit an explicit
   typed domain intent only when target, suggested relation, polarity, and
   confidence satisfy the approved gate.
4. durable relation or conclusion mutation still flows only through
   `planning -> action`.
5. low-confidence or unknown-target feedback must remain descriptive-only
   unless a later approved planning/action slice adds a guarded route.
6. expression may consume already-learned high-confidence communication truth,
   but must not write behavior-feedback state.
7. memory may preserve behavior-feedback evidence inside the completed episode
   so reflection can inspect repeated weaker signals later.
8. reflection may consolidate repeated relation-backed feedback candidates into
   relation updates, but a single weak candidate must not become learned truth.

This contract starts with the existing communication-boundary signal owner and
does not introduce a second memory subsystem or a second durable write path.

---

## Foreground Ownership Contract (Target-State Convergence)

Foreground execution keeps one explicit ownership split while orchestration
converges toward canonical architecture:

| Foreground segment | Contract owner | Notes |
| --- | --- | --- |
| Baseline load (`event` normalization result, state seed, identity/memory/task baseline acquisition) | Runtime orchestrator | Runs before graph execution and prepares one shared state seed for cognitive stages. |
| Stage graph (`perception -> affective_assessment -> context -> motivation -> role -> planning -> expression -> action`) | Graph runner + stage adapters | Owns cognitive stage sequencing and stage outputs. |
| Episodic memory write | Runtime orchestrator (`memory` follow-up stage) | Persists completed turn after action output exists. |
| Reflection trigger | Runtime orchestrator (`reflection` follow-up stage) | Emits/enqueues reflection work only after episodic persistence step. |

This split defines the target foreground boundary for `PRJ-276..PRJ-279`.

---

## Foreground Migration Invariants

During boundary migration, the following invariants must remain stable:

1. Stage output keys remain stable across orchestration boundaries:
   `perception`, `context`, `motivation`, `role`, `plan`, `expression`,
   `action_result`.
2. Canonical stage ordering remains stable inside the cognitive stage graph:
   `perception -> ... -> expression -> action`.
3. Baseline load completes before graph execution starts.
4. Episodic memory write runs only after action output exists.
5. Reflection trigger runs only after episodic memory persistence completes.
6. Side-effect ownership remains explicit:
   - cognitive reasoning stages stay side-effect-free
   - action owns world-facing execution and domain-intent execution
   - runtime follow-up stages own post-turn persistence/trigger operations.

Any further graph/runtime boundary move must preserve these invariants unless
canonical architecture docs are explicitly revised first.

---

## Shared Action-Delivery Contract

Expression and action continue to share one bounded handoff owner.

Contract rules:

1. expression may produce one `ActionDelivery` payload only after planning
   completes.
2. `ActionDelivery` may carry a bounded `execution_envelope` for
   connector-oriented execution metadata, but expression must not execute or
   authorize connector side effects.
3. action validates and consumes the delivery handoff, including any
   extension envelope, before world-facing side effects occur.
4. integration routing may consume bounded delivery-envelope metadata for
   transport-visible notes, but must not replace action as the side-effect
   owner.

This preserves the canonical ordering `planning -> expression -> action`
without fragmenting handoff ownership by connector family.

---

## Reflection Scope Governance Contract

Reflection outputs now follow one explicit scope owner rather than ad hoc
writer-side heuristics.

Contract rules:

1. goal-progress and goal-milestone reflection conclusions are goal-scoped
   adaptive outputs and must resolve through one shared scope-policy owner.
2. affective reflection conclusions plus adaptive role/collaboration signals
   remain user-global unless architecture docs explicitly promote them to
   narrower scope families later.
3. reflection writers and repository/runtime readers must consume the same
   scope-policy owner so invalid scoped overrides for global outputs are
   ignored instead of leaking across goals.
4. future task-scoped reflection additions must register their family in the
   shared scope policy before runtime readers depend on them.

This keeps multi-goal leakage guardrails explicit without moving reflection
logic back into stage-local conventions.

---

## Identity And Preference Ownership Contract

Identity loading keeps one explicit ownership policy between lightweight profile
continuity and learned runtime preferences.

1. `preferred_language` remains profile-owned continuity state and is loaded
   from `aion_profile`
2. first-party client localization must not reuse `preferred_language` as a
   GUI-locale override because conversation language remains runtime-owned
   continuity
3. if a first-party web or mobile client needs a persisted interface locale,
   it must use a separate backend-owned app-facing setting such as
   `ui_language`
4. a future `ui_language` field may shape only first-party shell copy,
   navigation labels, and client chrome; it must not directly override
   expression language, perception language, or memory-language continuity
5. if a first-party client needs explicit local-time truth for "what date or
   hour is it for me right now", it may persist one profile-owned `utc_offset`
   setting and runtime may localize the current-turn timestamp from that value
   before cognitive stages consume turn truth
6. profile-owned `utc_offset` is limited to explicit offset continuity only; it
   must not introduce a parallel region-timezone, DST-rule, calendar, or
   scheduling subsystem
7. `response_style`, `collaboration_preference`, and `preferred_role` remain
   conclusion-owned learned preferences and must not be copied into profile
   storage as identity fields
8. relation fallback cues may influence stage-level tie-break behavior, but
   they must not rewrite identity-owned profile continuity
9. runtime visibility should expose the shared policy owner through
   `/health.identity` and `system_debug.adaptive_state.identity_policy`
10. language continuity should also expose one explicit posture snapshot with
   precedence order, supported language codes, and current event-level
   continuity diagnostics through runtime debug
11. multilingual posture remains explicit and bounded to currently supported
   runtime language codes until a broader language model is intentionally added

---

## Self-Service Runtime Reset And Cleanup Boundary

Destructive reset behavior must reuse existing backend-owned identity,
profile, and runtime continuity owners instead of introducing a parallel
workspace or admin-reset subsystem.

Contract rules:

1. self-service reset is bounded to one authenticated user's runtime
   continuity and must not delete the auth account itself
2. self-service reset preserves:
   - `aion_auth_user`
   - `aion_profile`
   - explicit shell and continuity settings stored on the profile
   - user-managed operational enablement preferences
   - linked integrations and linked Telegram continuity
3. self-service reset removes runtime continuity owned by `user_id`,
   including memory, learned conclusions other than preserved user-managed
   settings, relations, theta, internal planning state, attention state,
   reflection queue state, and subconscious proposals
4. self-service reset revokes all auth sessions, including the current
   session, so the next authenticated foreground turn starts from a clean
   continuity baseline instead of a mixed pre-reset/post-reset session posture
5. operator-owned production cleanup remains a separate maintenance contract
   and must not be exposed through normal product UI
6. any destructive delete implementation must reuse one shared backend owner
   across app-facing reset and operator cleanup flows rather than duplicating
   per-table logic in endpoints or scripts

This preserves the architecture boundary:

- auth identity stays backend-owned
- settings and linked-channel continuity stay profile-owned
- runtime continuity stays explicitly resettable without turning "clear my
  data" into account deletion

---

## Shared App Chat Transcript Contract

First-party app chat and linked Telegram continuity now freeze one explicit
app-facing transcript posture for `/app/chat/history`.

Contract rules:

1. `/app/chat/history` is a transcript surface for exchanged messages, not a
   memory-inspection surface for summarized memory entries
2. transcript continuity remains backend-owned by the shared authenticated
   `user_id`; linked Telegram joins the same continuity owner only after the
   user explicitly links that channel
3. the frozen product-facing default window is the latest `10` exchanged
   messages
4. transcript items render in chronological order from oldest to newest so
   app clients can place the newest messages at the bottom of the thread
5. each message item must stay bounded to one app-facing shape:
   - `message_id`
   - `event_id`
   - `role`
   - `text`
   - `channel`
   - `timestamp`
   - optional bounded `metadata` only when product UX genuinely needs it
6. app-facing transcript items must not expose raw memory summaries, raw
   episodic payloads, or memory-specific inspection fields such as `source`,
   `summary`, or arbitrary stored payload blobs as the durable client
   contract
7. transcript projection must reuse existing episodic turn memory and action
   results; it must not introduce a second durable chat store
8. future pagination may widen the envelope with explicit paging metadata, but
   it must not reopen continuity ownership or replace the frozen item shape
9. web and future mobile remain thin `/app/*` clients over this same
   transcript contract; Telegram transport specifics stay in action and
   integration layers rather than the client contract
10. scheduler-originated or subconscious wakeups are internal runtime events,
    not user-authored turns, so they must never project into
    `/app/chat/history` as `role=user`
11. scheduler-originated outreach may appear in the transcript only when the
    conscious path actually authorized and delivered a user-visible outbound
    message; silent internal wakeups stay hidden from the transcript

## Shared Communication Governance Contract

Foreground communication now follows one explicit user-vs-scheduler boundary.

Contract rules:

1. direct user-authored turns from first-party app or linked Telegram are
   communication obligations and should always produce an outbound reply on the
   originating channel unless architecture docs later approve an explicit
   exception posture
2. scheduler-owned or subconscious wakeups may complete with no user-visible
   message when conscious evaluation concludes that no grounded outreach is
   justified
3. proactive outbound delivery is allowed only after the conscious
   `planning -> expression -> action` path positively authorizes it
4. a scheduler wakeup may stimulate analysis, relation maintenance, or
   planned-work reevaluation without becoming a pseudo-user transcript turn
5. the first-party authenticated app remains the canonical conversation owner;
   linked channels are transport surfaces that enrich and mirror that same
   continuity rather than replace it
6. when a user writes on a linked channel, the inbound turn must still become
   one canonical shared transcript turn and the reply must be written to the
   canonical app transcript before any linked-channel propagation completes
7. proactive propagation to linked channels may occur after technical
   delivery-failure evidence or relationally interpreted silence, but the
   decision remains runtime-owned and relation-sensitive rather than fixed to a
   global timeout
8. channel preference, sleep posture, response cadence, and interruption
   tolerance may be inferred and adapted through relation or preference owners,
   but the user may also state explicit preferences that runtime should honor
9. any user-authored message on any linked channel counts as contact and
   resets silence posture for proactive escalation logic
10. transcript history should show only real exchanged user or assistant
    messages; transport attempts, escalation bookkeeping, and propagation
    metadata stay outside the app-facing transcript

## Canonical Multi-Channel Conversation Contract

Linked transports now follow one canonical conversation-owner rule.

Contract rules:

1. the internal authenticated app chat is the source-of-truth conversation
   surface for the user
2. Telegram and future linked communicators are bounded transport mirrors over
   that same conversation owner after explicit account linking
3. inbound linked-channel user messages must be persisted into the canonical
   shared transcript under the same `user_id`
4. outbound replies triggered by a linked-channel inbound message must remain
   semantically consistent across:
   - the canonical app transcript
   - the originating linked channel
5. transport adaptation may change segmentation or formatting, but it must not
   change message meaning
6. the app transcript should store one canonical assistant reply, not one
   separate transcript row per transport segment
7. future linked channels must integrate through the same canonical transcript
   owner, not by creating channel-local chat truth

## Channel Propagation And Adaptation Contract

Outbound propagation follows one explicit semantic-preservation rule.

Contract rules:

1. expression produces one canonical assistant message for the turn
2. action and integration layers may adapt that canonical message for
   transport constraints such as Telegram length limits
3. transport adaptation must preserve semantic completeness; it may split or
   reformat, but it must not silently drop meaning
4. when a transport requires multiple segments, those segments must be sent in
   order so the user can reconstruct the full canonical reply
5. transport segmentation or formatting detail is an execution concern, not a
   second expression pass that rewrites the answer into a different message
6. future observability may expose propagation metadata, but app-facing chat
   history remains canonical-message-oriented rather than transport-segment-
   oriented

Illustrative contract shape:

```json
{
  "items": [
    {
      "message_id": "msg-1",
      "event_id": "evt-1",
      "role": "user",
      "text": "hello",
      "channel": "api",
      "timestamp": "2026-04-26T09:12:00Z",
      "metadata": {
        "delivery_state": "final"
      }
    }
  ]
}
```

This preserves the architecture boundary:

- one continuity owner across linked app and Telegram turns
- one backend-projected transcript instead of split client-local versus memory
  views
- one reusable app-facing contract for web now and mobile later

---

## Durable Capability-Record Contract

Durable role presets, durable skill descriptions, and per-user tool
authorization records now follow one explicit truth model.

Contract rules:

1. durable role records describe approved role presets, prompt variants,
   selection hints, and provenance; runtime still owns active role selection
   for the turn
2. durable skill records describe guidance, limitations, linked approved tool
   families, and provenance; they must not become direct execution authority
3. durable tool-authorization records describe per-user permission posture for
   approved tool families or bounded operations; they must not become a second
   side-effect engine outside action
4. backend truth surfaces must preserve the distinction between:
   - description: what is stored durably
   - selection: what runtime may choose or has chosen for the turn
   - authorization: what a given user is actually allowed to execute
5. capability aggregation surfaces may compose these records for operators or
   future UI, but they must reuse existing role, skill, connector, and health
   owners instead of inventing a parallel capability system
6. "learned skill" posture remains metadata-only until architecture is
   explicitly revised; no durable skill record may imply self-modifying
   executable tool logic

This keeps truthful growth visible without widening execution authority beyond
the existing planning -> action boundary.

---

## Adaptive Influence Governance Contract (PRJ-288 Baseline)

Adaptive signals may influence foreground cognition only through one governed
policy owner.

Signals below evidence threshold are descriptive-only inputs and must not
change role, motivation mode, planning steps, or expression tone by
themselves.

### Signal Families And Evidence Gates

| Signal family | Minimum evidence gate | Allowed influence scope |
| --- | --- | --- |
| Affective turn signal (`perception.affective`) | `needs_support=true` or `affect_label` is `support_distress` or `urgent_pressure`; source is explicit (`deterministic_placeholder`, `ai_classifier`, or `fallback`) | role, motivation, planning, expression |
| Relation cues (`aion_relation`) | relation `confidence >= 0.68`; role collaboration tie-break uses `confidence >= 0.70` | role, planning, expression tie-breaks |
| Preference conclusions (`response_style`, `collaboration_preference`, `preferred_role`) | conclusion `confidence >= 0.70`; role preference tie-break requires `preferred_role_confidence >= 0.72` | response style, role tie-break, motivation/planning tie-break |
| Theta adaptive bias (`support_bias`, `analysis_bias`, `execution_bias`) | dominant bias `>= 0.58` | final tie-break for role, motivation, planning, expression |

### Influence Precedence

1. explicit turn semantics and direct user intent are primary owners
2. affective safety/support signals may override lower adaptive families
3. relation and preference cues may shape tie-breaks on ambiguous turns
4. theta may shape only the last adaptive tie-break when stronger cues do not
   decide the turn

### Stage Gating Rules

1. role may consume preference/relation/theta tie-breaks only on ambiguous turn
   posture (`question`, `request_help`, or general-topic fallback path)
2. motivation may consume collaboration/theta tie-breaks only when explicit
   emotional, execution, and analysis signals did not already determine mode
3. planning and expression may consume adaptive cues only to shape guidance,
   tone, and response structure, not to mint new side effects
4. action remains the sole side-effect owner regardless of adaptive influence

### Guardrails

1. adaptive cues must not bypass attention gates, connector permission gates,
   or action-boundary intent ownership
2. adaptive cues must not self-reinforce without reflection-side outcome
   evidence
3. undocumented tie-breakers are disallowed; new adaptive influence requires
   contract updates first
4. AI-assisted affective classification rollout posture must remain explicit
   through one rollout-policy owner; disabled-policy fallback and
   classifier-unavailable fallback are both valid but must be machine-visible

---

## Role And Skill Boundary Contract

Role remains the behavior selector.
Skills may evolve as durable capability descriptions, but they do not become
execution owners.

Contract rules:

1. role selection owns the chosen behavioral stance for the turn
2. role selection may read from a durable role registry that stores approved
   presets, prompt-oriented definitions, selection hints, provenance, and
   lifecycle status
3. skill selection may annotate that stance with bounded capability metadata
   read from a durable skill registry
4. the skill registry may carry evolving descriptions, usage guidance,
   limitations, linked approved tool families, provenance, and lifecycle
   status
5. skills may inform planning and debug visibility, but they do not execute
   tools, side effects, or connector operations on their own
6. skills may reference approved tool families, but those references are
   planning guidance only and never executable authority
7. action must never treat selected skills as executable authority; explicit
   plan intents and action-boundary contracts remain the only execution owner
8. `/health` and runtime debug should expose one shared role/skill policy
   owner so registry-backed posture remains machine-visible during rollout and
   review
9. future reflection or runtime learning may update role or skill descriptions
   inside their registries, but those updates must remain bounded data
   revisions rather than a second tool-execution path

This preserves the canonical `role -> planning -> expression -> action`
boundary while allowing roles and skills to become durable, inspectable, and
revisable runtime data.

---

## Attention Inbox And Proposal Handoff Contract

The dual-loop boundary should remain explicit in runtime state.

Minimum contract fields:

```json
{
  "attention_inbox": [
    {
      "item_id": "attn-1",
      "source": "user_event|scheduler_tick|planned_work_due|subconscious_proposal",
      "conversation_key": "telegram:123456",
      "status": "pending|claimed|answered|deferred",
      "priority": 0.0,
      "event": {},
      "proposal": {}
    }
  ],
  "pending_turn": {
    "turn_id": "turn-1",
    "conversation_key": "telegram:123456",
    "item_ids": ["attn-1"],
    "assembled_text": "...",
    "status": "pending|claimed|answered",
    "owner": "conscious|none"
  },
  "subconscious_proposals": [
    {
      "proposal_id": "prop-1",
      "proposal_type": "ask_user|research_topic|suggest_goal|nudge_user|suggest_connector_expansion",
      "summary": "...",
      "confidence": 0.0,
      "payload": {},
      "status": "pending|accepted|merged|deferred|discarded",
      "research_policy": "none|read_only",
      "allowed_tools": ["memory_retrieval", "knowledge_search"]
    }
  ],
  "proposal_handoffs": [
    {
      "proposal_id": "prop-1",
      "decision": "accept|merge|defer|discard",
      "reason": "...",
      "decided_by": "conscious"
    }
  ]
}
```

Rules:

1. subconscious proposals are suggestions, not actions
2. conscious runtime must record a handoff decision before user-visible action
3. turn assembly state owns pending/claimed/answered ownership semantics
4. subconscious research proposals must declare read-only policy and tool bounds
5. connector-expansion proposals must stay suggestion-only until conscious
   planning emits explicit permission-gated connector intents

Deferred reflection external-driver baseline:

1. `deferred` reflection may not rely on an app-local worker for queue drain.
2. one shared external-driver policy owner must expose the selected runtime
   mode, the queue-drain target owner, and the canonical queue-drain
   entrypoint.
3. the canonical queue-drain entrypoint is
   `scripts/run_reflection_queue_once.py` with PowerShell/bash wrappers.
4. `/health.reflection` should expose machine-visible external-driver posture
   before deferred reflection is treated as production baseline.

Deferred reflection supervision baseline:

1. one shared supervision policy owner must freeze the target runtime mode,
   target queue-drain owner, target scheduler execution mode, and durable
   retry owner for deferred reflection operations.
2. supervision posture must classify queue state as one of:
   - `steady_state_clear`
   - `active_backlog_under_supervision`
   - `recovery_required`
3. stuck-processing rows, exhausted-failed rows, app-local worker conflicts,
   or non-externalized scheduler ownership are supervision blockers until
   explicit recovery action is taken.
4. `/health.reflection.supervision` and release evidence should expose the same
   blocking signals plus recovery actions, so deferred durability posture does
   not depend on manual interpretation of raw task counts.

External cadence cutover proof baseline:

1. `scheduler_execution_mode=externalized` alone is not sufficient proof that
   maintenance and proactive cadence are production-owned by the external
   scheduler.
2. one explicit cutover-proof contract must define the minimum machine-visible
   evidence required before production treats the external scheduler as the
   real cadence owner.
3. that cutover-proof contract must cover both cadence families:
   - maintenance cadence
   - proactive cadence
4. minimum evidence categories are:
   - recent successful external last-run evidence for each cadence family
   - bounded duplicate-protection or idempotency posture for each canonical
     entrypoint
   - explicit stale-or-missing evidence state for operator triage
   - release/smoke visibility for the same fields
   - rollback posture showing that app-local cadence remains the explicit
     recovery owner when cutover proof is missing
5. until that evidence is present, `/health.scheduler.external_owner_policy`
   remains target-policy posture only and production must treat app-local
   cadence ownership as the active fallback baseline.

## Time-Aware Planned Work Contract

Time-aware planned work is the canonical future-work layer for no-UI `v1`.

For core no-UI `v1`, this future-work layer is part of the required product
baseline, while organizer-tool activation remains a later extension rather
than a closure prerequisite.

It extends existing goals, tasks, proactive cadence, and scheduler ownership
without introducing a separate reminder engine.

Minimum durable shape:

```json
{
  "planned_work": [
    {
      "work_id": "pw-1",
      "user_id": "...",
      "goal_id": "optional-goal-id",
      "task_id": "optional-task-id",
      "kind": "follow_up|check_in|reminder|routine|research_window",
      "status": "pending|due|snoozed|completed|cancelled",
      "summary": "...",
      "delivery_window": {
        "not_before": "ISO-8601",
        "preferred_at": "ISO-8601",
        "expires_at": "ISO-8601"
      },
      "recurrence": {
        "mode": "none|daily|weekly|custom"
      },
      "delivery_policy": {
        "channel": "telegram|api|none",
        "requires_foreground_execution": true,
        "quiet_hours_policy": "respect_user_context"
      },
      "provenance": "explicit_user_request|planning_inference|reflection_inference",
      "last_evaluated_at": "ISO-8601"
    }
  ]
}
```

Rules:

1. planned work is an extension of internal planning state, not a separate
   reminder subsystem
2. background cadence may reevaluate planned work against current time and
   context, but it must not deliver user-visible output directly
3. if a planned item becomes due, background ownership may only:
   - update durable planned-work state
   - emit an attention item
   - emit a bounded proposal for foreground handling
4. any later message, notification, or side effect still goes through
   planning -> expression -> action
5. planned work may be one-time or recurring, but recurrence remains bounded
   data plus reevaluation rules rather than a second scheduler outside the
   existing cadence owner
6. planned work may support reminders, check-ins, routines, and bounded
   research windows, but those are all variants of one future-work model
7. current time, timezone posture, quiet-hour posture, active goals, and
   recent user context are valid reevaluation inputs; they do not by
   themselves grant direct delivery authority
8. external contact planning, including care/check-in reasoning inferred from
   relationship history, may create or update planned work or proposals, but it
   must not become a hard-coded scheduler obligation to contact the user
9. a planned-action observer should check for due or actionable work before
   starting a full foreground runtime cycle; an empty observer result should be
   a cheap no-op
10. this contract governs future-facing external planning only; once a
    foreground stimulus is admitted, the internal execution path still proceeds
    through planning -> expression -> action -> memory -> reflection trigger

### Passive And Active Runtime Trigger Boundary

Runtime trigger ownership follows one passive/active split.

Passive triggers may run:

- reflection queue drain
- relationship and behavior-pattern analysis
- planned-work reevaluation
- proposal maintenance
- cheap planned-action observer checks

Passive triggers may write only background-owned state:

- conclusions
- relations
- theta updates
- planned-work records
- subconscious proposals
- execution or failure evidence for later reflection

Active triggers may start conscious foreground execution only when one of these
inputs exists:

- a direct user-authored event
- a due planned-work item that crossed the observer and attention boundary
- an actionable retriable proposal admitted through attention
- an explicit admin/system event allowed by the foreground event contract

Rules:

1. subconscious and passive scheduler loops must not call conscious runtime as
   a generic stimulus.
2. passive loops must not send, notify, mutate external systems, or perform
   user-visible delivery.
3. active conscious execution remains the only path that may decide and perform
   user-visible outreach.
4. failed action attempts should be preserved as execution evidence even when
   expression decides not to report the failure to the user.
5. learned expression policy may shape whether failures are communicated, but
   it must not suppress durable failure evidence needed by reflection.

### Bounded Autonomous Research-Window Policy

Research windows remain planned-work items, not a separate autonomy engine.

Rules:

1. `kind=research_window` is valid only as a planned-work variant on the same
   durable entity as reminders, follow-ups, and routines
2. research-window creation requires one bounded trigger:
   - explicit user request to check later, revisit later, or research in a
     spare window
   - accepted conscious proposal linked to an already active user goal or
     task
   - explicit follow-up commitment already captured in planned work
3. background cadence may only reevaluate or hand off a research window; it
   must not perform uncontrolled browsing directly from the background
4. foreground execution of a research window remains limited to the existing
   approved read-only tool slices:
   - `knowledge_search.search_web`
   - `web_browser.read_page`
5. each research window must stay bounded to one topic or decision frame plus
   a small number of reads; it is not a standing crawl, monitor, or open-ended
   browsing loop
6. research windows must preserve the same safety and execution guardrails as
   other external reads:
   - no credential bypass
   - no hidden-auth browsing

### Foreground Capability And Time Awareness Contract

Foreground turns may receive bounded awareness of already-approved runtime
truth, but that awareness must not become a second execution or authorization
engine.

Contract rules:

1. the active foreground turn may receive only bounded awareness of:
   - current turn time derived from normalized event timestamp
   - active planned-work posture already owned by runtime continuity
   - approved bounded tool families and their current readiness posture
2. this awareness is visibility-only input for context, planning, and
   expression; it must not by itself trigger side effects or bypass normal
   intent selection
3. foreground awareness may summarize whether the runtime can currently:
   - answer from continuity already loaded for the turn
   - use bounded search/page-read capability through approved tool slices
   - reason about due planned work and current time
4. foreground awareness must not:
   - grant tool authorization outside existing connector permission gates
   - create a second scheduler or delivery path outside planned-work and
     attention ownership
   - imply organizer or channel-specific extension posture is part of the core
     cognition contract
5. any later external read, mutation, or delivery still flows through:
   - planning intent selection
   - expression handoff
   - action-owned execution
6. foreground awareness may improve truthful replies about time, memory
   continuity, and available bounded capability, but the source of truth stays
   below the same runtime-owned health, continuity, and connector surfaces

This contract freezes what the active turn may know, not a new way to execute.
   - no direct mutations in external systems
   - no second planning or side-effect engine outside action
7. any durable learning produced by a research window still goes only through
   the existing action-owned tool-grounded summary path and memory-owned
   persistence
8. if bounded evidence is not found, the runtime should fall back to a normal
   foreground outcome such as no-op, defer, or ask-user follow-up rather than
   widening browsing authority

Durable attention rollout baseline:

1. owner mode may be `in_process` or `durable_inbox`
2. `/health.attention` should expose `persistence_owner` and `parity_state`
   for rollout parity visibility
3. durable mode must preserve the same burst/claim/answer semantics unless a
   later contract revision explicitly changes turn assembly behavior

Durable attention contract-store rollout:

1. `durable_inbox` now uses one repository-backed turn contract store keyed by
   `(user_id, conversation_key)`.
2. the durable store must preserve `pending|claimed|answered` semantics,
   `source_count`, coalesced `event_ids`, `update_keys`, and optional
   `assembled_text`.
3. attention boundary remains the only owner of turn-state mutation and
   cleanup timing, while repository code owns durable storage primitives.
4. `/health.attention` should expose contract-store posture and cleanup
   candidate visibility before any production-default switch to durable owner
   mode, including `contract_store_mode`, `deployment_readiness.contract_store_state`,
   `stale_cleanup_candidates`, and `answered_cleanup_candidates`.

Canonical ownership baseline:

1. attention boundary owns `attention_inbox` and `pending_turn` state mutation
2. planning owns `proposal_handoffs` decisions and `accepted_proposals` turn
   outputs
3. action consumes planning decisions and remains the only side-effect owner
4. subconscious/background paths may create `subconscious_proposals` but cannot
   claim `pending_turn` or execute actions

Proposal lifecycle baseline:

1. proposal creation starts at `status=pending`
2. conscious planning decides one of `accept|merge|defer|discard`
3. decision maps to durable proposal status
  - `accept -> accepted`
  - `merge -> merged`
  - `defer -> deferred`
  - `discard -> discarded`
4. any transition outside this mapping requires an explicit contract update
5. `pending_turn.owner=conscious` is required whenever `pending_turn.status=claimed`

---

## Connector Capability And Permission Gate Contract

External productivity integrations are capability surfaces, not cognitive owners.

Minimum contract fields:

```json
{
  "connector_capabilities": [
    {
      "connector_kind": "calendar|task_system|cloud_drive",
      "provider": "google_calendar|trello|clickup|gdrive|onedrive",
      "enabled": true,
      "allowed_operations": ["read", "suggest", "mutate"],
      "scope": "account|workspace"
    }
  ],
  "connector_permission_gates": [
    {
      "connector_kind": "calendar|task_system|cloud_drive",
      "provider_hint": "google_calendar|clickup|google_drive|generic",
      "operation": "read_availability|create_task|upload_file|discover_task_sync",
      "mode": "read_only|suggestion_only|mutate_with_confirmation",
      "requires_opt_in": true,
      "requires_confirmation": false,
      "allowed": false,
      "reason": "suggestion_or_read_only_allowed|explicit_user_confirmation_required|proposal_only_no_external_access"
    }
  ]
}
```

Rules:

1. connector capabilities can inform planning but do not execute by themselves
2. permission gates are explicit plan outputs consumed by action boundaries
3. internal goals/tasks remain first-class internal planning state
4. one shared connector execution-policy owner defines baseline operation
   posture for `calendar`, `task_system`, and `cloud_drive`
5. action must validate connector intent posture against that shared policy
   before any delivery or external execution path continues
6. current MVP execution baseline is intentionally narrow:
   - `task_system:create_task` with `provider_hint=clickup` is the first live
     provider-backed action path when both `CLICKUP_API_TOKEN` and
     `CLICKUP_LIST_ID` are configured
   - the next selected live read-capable expansion path is
     `task_system:list_tasks` with `provider_hint=clickup`, so the repo can
     widen provider-backed connector coverage without reopening calendar or
     cloud-drive read scope first
   - `calendar` and `cloud_drive` remain permission-gated planning surfaces;
     only the explicitly approved bounded read paths below may execute through
     provider adapters
   - other `task_system` operations remain policy-only until pre-action read
     paths and additional provider adapters are introduced
7. `/health.connectors.execution_baseline` must expose whether the selected
   live paths are configured and whether all other connector families remain in
   policy-only posture by design
8. current read-capable expansion baseline is intentionally still narrow:
   - `task_system:list_tasks` with `provider_hint=clickup` is the first live
     provider-backed read path under the same task-system family
   - its output remains action-owned execution evidence, not a new pre-planning
     memory or context read surface
9. the next bounded calendar-read baseline is frozen before implementation:
   - selected operation: `calendar:read_availability`
   - selected provider hint: `google_calendar`
   - permission posture remains `read_only` with explicit user opt-in and
     without mutation confirmation
   - safe output shape must stay action-owned and bounded to availability
     evidence only:
     - requested time hint or normalized window
     - timezone or provider default timezone note
     - bounded free/busy summary
     - bounded free-slot preview count and top candidate slots
   - provider-backed execution must not expose raw event titles, attendee
     lists, descriptions, or become a new background/context ingestion path
10. once implemented, bounded calendar live-read posture must be visible in
    `/health.connectors.execution_baseline` through one explicit provider path:
    - `calendar.google_calendar_read_availability`
    - `execution_mode=provider_backed_when_configured`
    - `state=credentials_missing|provider_backed_ready`
    - all other calendar operations remain policy-only until separately
      approved through their own contract slices
11. the first bounded cloud-drive metadata-read baseline is now implemented:
    - selected operation: `cloud_drive:list_files`
    - selected provider hint: `google_drive`
    - permission posture remains `read_only` with explicit user opt-in and
      without mutation confirmation
    - safe output shape must stay metadata-only and action-owned:
      - bounded file-name preview
      - provider file id
      - mime type or provider file kind
      - modified-time or recency note
      - optional next-page or truncation note
    - provider-backed execution must not expose document body content, file
      download payloads, or become a new pre-planning retrieval surface
12. bounded cloud-drive live-read posture must be visible in
    `/health.connectors.execution_baseline` through one explicit provider path:
    - `cloud_drive.google_drive_list_files`
    - `execution_mode=provider_backed_when_configured`
    - `state=credentials_missing|provider_backed_ready`
    - all other cloud-drive operations remain policy-only until separately
      approved through their own contract slices
13. web search and browser access now extend the same action-owned capability
    family instead of creating a skill-owned execution subsystem:
    - `knowledge_search`
    - `web_browser`
14. they stay on the same planning -> permission-gate -> action validation
    path as the existing connector families, so provider access remains
    explicit and reviewable
15. selected skills may explain why planning can consider those tool families,
    but skills must not execute, authorize, or self-install provider access on
    their own
16. until an explicit provider-backed slice is approved, web knowledge tools
    remain policy-only or suggestion-only surfaces and must not bypass the
    action boundary through direct model-side browsing claims
17. the first bounded provider-backed web-knowledge and organization slices are
    now frozen as:
    - `knowledge_search:search_web` with `provider_hint=duckduckgo_html`
    - `web_browser:read_page` with `provider_hint=generic_http`
    - `task_system:update_task` with `provider_hint=clickup`
18. safe output boundaries for those slices must stay action-owned:
    - search returns bounded result evidence only:
      - title
      - canonical url
      - snippet preview
      - rank
      - truncation note
    - browser returns bounded page-read evidence only:
      - final url
      - page title
      - content type
      - bounded text excerpt
      - truncation note
    - ClickUp update returns bounded mutation evidence only:
      - task id
      - task name preview
      - updated status or field summary
19. the first live website-reading workflow is now frozen as one bounded
    user-facing behavior baseline:
    - direct page review when the turn already contains a URL
    - search-first page review when the turn contains only a topic, site
      hint, or "check this website" style request without a final URL
    - canonical execution path remains:
      - planning
      - connector permission gates
      - `knowledge_search:search_web` when discovery is needed
      - `web_browser:read_page` for the selected page
      - expression
      - action-owned delivery
20. bounded website-reading input, output, and safety boundaries are explicit:
    - allowed bounded inputs:
      - explicit URL
      - explicit site or domain hint
      - explicit answer focus for what should be checked on the page
    - required bounded outputs:
      - final page URL
      - page title when available
      - bounded summary of what was found
      - source note pointing back to the page that was read
      - explicit blocker or uncertainty note when the read was incomplete
    - forbidden outputs:
      - raw full-page dumps
      - hidden-auth or paywall bypass claims
      - implicit multi-page crawling presented as one page review
      - pretending a page was read when the provider path was unavailable
    - website reading stays read-only and must not click, submit, log in, or
      mutate external systems as part of this workflow
21. tool-grounded memory posture for website reading remains explicit:
    - search or page-read evidence may become durable learned knowledge only
      through the existing action-owned tool-grounded learning path
    - durable capture must stay bounded to summary-level semantic conclusions,
      not raw provider payloads or raw HTML persistence
22. these slices must not execute JavaScript, submit forms, follow login flows,
    widen memory retrieval ownership, or expose raw provider payloads beyond
    the bounded evidence contract
23. the live execution path for these slices remains unchanged architecturally:
    - role and selected skills may shape planning posture
    - planning must emit explicit typed intents
    - permission gates and execution envelopes remain authoritative
    - action remains the only provider-call owner
24. behavior validation for this lane should prove the live bounded slices as:
    - `T14.1` analyst-driven web search via `duckduckgo_html`
    - `T14.2` analyst-driven page read via `generic_http`
    - `T14.3` executor-aligned ClickUp task update through the action layer
25. user authorization remains the owner of tool activation:
    - a tool family or provider path may be available only when the user has
      enabled it through the approved authorization surface
    - `v1` may keep that activation backend-managed for the single-user
      baseline
    - later UI may manage the same per-user authorization records directly
26. user authorization does not change secret ownership:
    - raw provider credentials remain external configuration unless a later
      credential-storage contract is approved explicitly
    - durable authorization records exist to express consent, readiness, and
      allowed tool posture

---

## Work-Partner Role Baseline

Work-partner is a role of the same personality, not a second persona or
separate execution subsystem.

Rules:

1. `work_partner` may be selected only through the same role-selection owner
   as every other role.
2. it may combine bounded, non-executable skill descriptions for work
   organization and decision support, especially:
   - structured reasoning
   - execution planning
   - connector boundary review
   - memory recall when the turn explicitly asks for remembered context
3. it may use only already approved tool families through the existing
   planning -> permission-gate -> action boundary:
   - `task_system`
   - `knowledge_search`
   - `web_browser`
   - bounded `calendar` or `cloud_drive` reads when those contracts are active
4. it must not bypass:
   - connector opt-in rules
   - confirmation requirements for external mutations
   - the non-executable skill boundary
5. its `v1` scope is work organization and decision support, not autonomous
   execution outside explicit user-facing turns or approved proactive flows.
6. the first production organizer-tool stack for this role is explicitly
   bounded to:
   - ClickUp `create_task`, `list_tasks`, `update_task`
   - Google Calendar `read_availability`
   - Google Drive `list_files`
   and must stay machine-visible through one shared
   `/health.connectors.organizer_tool_stack` acceptance surface plus matching
   smoke, incident-evidence, and behavior-validation proof.
7. the production credential-activation baseline for that stack is explicit:
   - ClickUp activation requires:
     - `CLICKUP_API_TOKEN`
     - `CLICKUP_LIST_ID`
   - Google Calendar activation requires:
     - `GOOGLE_CALENDAR_ACCESS_TOKEN`
     - `GOOGLE_CALENDAR_CALENDAR_ID`
     - `GOOGLE_CALENDAR_TIMEZONE`
   - Google Drive activation requires:
     - `GOOGLE_DRIVE_ACCESS_TOKEN`
     - `GOOGLE_DRIVE_FOLDER_ID`
   - read-only operations (`list_tasks`, `read_availability`, `list_files`)
     still require explicit user opt-in before production use
   - mutation operations (`create_task`, `update_task`) require both explicit
     user opt-in and per-action confirmation
8. partial provider configuration is valid bounded posture, but it is not the
   same as full organizer-stack activation:
   - `/health.connectors.organizer_tool_stack.readiness_state` remains the
     shared operator summary for credential gaps across the frozen stack
   - later activation surfaces may add actionable next steps, but they must
     reuse this baseline rather than invent a second readiness model

First practical daily-use organizer workflows for no-UI `v1`:

1. task review and triage
   - user-facing prompt examples:
     - "show me my ClickUp tasks"
     - "what is still blocked?"
     - "what should I focus on today?"
   - permitted external action posture:
     - bounded `task_system:list_tasks`
   - architectural rule:
     - internal goals and tasks remain primary planning state; external task
       reads may inform answers and planning, but do not replace internal
       planning ownership
2. task capture and status update
   - user-facing prompt examples:
     - "create a task for this"
     - "mark that task as done"
     - "move this to in progress"
   - permitted external action posture:
     - bounded `task_system:create_task`
     - bounded `task_system:update_task`
   - architectural rule:
     - these remain confirmation-gated mutations even when the selected role
       is `work_partner` or selected skills suggest execution support
3. availability inspection
   - user-facing prompt examples:
     - "am I free tomorrow morning?"
     - "check whether 15:00 looks open"
   - permitted external action posture:
     - bounded `calendar:read_availability`
   - architectural rule:
     - output stays availability evidence only and does not widen into event
       creation or calendar-grade scheduling semantics
4. file-space inspection
   - user-facing prompt examples:
     - "what files are in that folder?"
     - "show me recent documents"
   - permitted external action posture:
     - bounded `cloud_drive:list_files`
   - architectural rule:
     - output stays metadata-only and does not widen into upload, edit, or
       raw document-body ingestion

Shared boundary rules for that daily-use baseline:

1. provider boundaries stay explicit:
   - ClickUp owns task review and mutation slices
   - Google Calendar owns availability inspection
   - Google Drive owns metadata-only file inspection
2. opt-in remains required for organizer connector families
3. confirmation remains required for organizer mutations
4. role or skill selection must not imply organizer execution authority on its
   own
5. external organizer data supports internal planning state; it does not
   become a second planning system

---

## Skill-Guided Bounded Action Loop Contract

Complex user requests may require several read-only tool steps before AION can
truthfully answer. This does not move side effects into planning. It extends
the action layer with one bounded execution loop that can consume a detailed
plan, selected skills, approved tool bindings, and intermediate observations.

Definitions:

1. skill = reusable execution strategy or cognitive procedure
2. tool = external or internal capability executed only by action
3. skill-tool binding = approved metadata that says which tools a skill may
   consider, not authority to execute those tools by itself
4. observation = bounded summary of one tool result, produced inside action
   and safe for later expression, memory, and debugging

Rules:

1. planning remains the owner of the turn goal, constraints, ordered model
   plan, selected skills, allowed tool families, permission gates, and typed
   domain intents.
2. action remains the only owner of tool execution, provider calls, delivery,
   and durable side effects.
3. action may run a bounded execute-observe-adjust loop when the plan contains
   approved read-only or confirmation-gated tool work.
4. the loop may choose the next step from the current plan, skill guidance,
   available observations, and approved tool bindings.
5. the loop may refine execution order inside the approved goal, for example
   direct page read first when a URL is present or search-first review when the
   URL is missing or ambiguous.
6. the loop must not invent a new goal, widen provider access, bypass
   permission gates, bypass confirmation requirements, or execute a tool that
   is not allowed by the selected skill/tool contract and connector policy.
7. read-only steps may execute without per-step confirmation only when the
   connector policy marks the operation as read-only and the user/tool
   authorization posture allows it.
8. mutation steps remain confirmation-gated even when they are part of a
   multi-step execution plan.
9. every tool result must be reduced into bounded observation fields before it
   can influence further execution:
   - tool id and operation
   - provider path
   - source reference
   - bounded result summary
   - confidence or blocker
   - next-step relevance
10. raw provider payloads, raw HTML, full page dumps, mail bodies, and hidden
    auth data must not become planning inputs or durable memory records.
11. loop execution must have explicit stop conditions:
    - goal satisfied
    - blocker found
    - clarification or confirmation required
    - max step count reached
    - provider/tool failure
12. runtime debug and health surfaces should expose the loop policy owner,
    step count, selected skills, used tools, completion state, and blockers
    without leaking secrets or raw provider payloads.

Initial approved skill-tool bindings:

1. `website_review`
   - allowed tools:
     - `knowledge_search.search_web`
     - `web_browser.read_page`
   - execution posture:
     - read-only
     - direct URL review
     - search-first page review when the target page is ambiguous
   - bounded outputs:
     - final page URL
     - page title
     - requested fact or summary
     - source note
     - uncertainty or blocker note
2. `web_research`
   - allowed tools:
     - `knowledge_search.search_web`
     - optional `web_browser.read_page`
   - execution posture:
     - read-only public knowledge lookup
     - source-backed summary
3. `clickup_task_management`
   - allowed tools:
     - `task_system.clickup_list_tasks`
     - `task_system.clickup_create_task`
     - `task_system.clickup_update_task`
   - execution posture:
     - read-only task review when enabled and configured
     - create/update only after explicit confirmation

The first implementation target for this contract is not a new connector. It
is stronger capability truth and orchestration over the already-approved
`web_search`, `web_browser`, and ClickUp paths.

---

## Tool-Grounded Learning Capture Baseline

Approved external reads may become durable learned knowledge only through one
explicit bounded contract.

Rules:

1. eligible source families are limited to approved read operations executed
   through the existing planning -> permission-gate -> action boundary:
   - `knowledge_search.search_web`
   - `web_browser.read_page`
   - `task_system.list_tasks`
   - `calendar.read_availability`
   - `cloud_drive.list_files`
2. Action owns reduction of provider results into bounded learning candidates.
3. Memory owns persistence of those candidates after action completes, using
   normal conclusion writes rather than a second ingestion path.
4. persisted tool-grounded knowledge must remain bounded summary data:
   - short evidence-oriented text
   - source family and operation
   - optional bounded source reference such as query, URL, or provider path
5. raw provider payloads, full documents, attendee lists, login state, or
   unconstrained excerpts must not be persisted as tool-grounded learned state.
6. tool-grounded learning remains semantic knowledge, not executable skill
   growth:
   - it may influence later retrieval, planning, or reflection
   - it must not imply self-modifying tools, self-installed integrations, or
     a second execution subsystem
7. canonical initial conclusion kinds for this lane are:
   - `tool_grounded_search_knowledge`
   - `tool_grounded_page_knowledge`
   - `tool_grounded_task_snapshot`
   - `tool_grounded_calendar_snapshot`
   - `tool_grounded_drive_snapshot`
8. learned-state inspection may expose these summaries as part of learned
   knowledge, but their capture owner remains Action and their persistence
   owner remains Memory.

Machine-visible expectation:

1. backend surfaces should make it clear when `work_partner` was selected
2. selected skills and planned skills should remain inspectable metadata
3. authorized tool use should stay visible through typed intents, permission
   gates, execution envelopes, and action results
4. organizer-tool production readiness must remain visible through the shared
   organizer stack snapshot instead of provider-by-provider operator inference

---

## V1 Life-Assistant Workflow Baseline

No-UI `v1` uses the existing goal/task, proactive, scheduler, and action
boundaries. It does not introduce a second orchestration path for "assistant"
workflows.

Canonical workflow set:

1. reminder capture and follow-up
   - explicit reminder phrasing may create an internal active task through
     normal planning intents
   - explicit reminder or check-in consent may update a learned proactive
     preference through a typed planning intent and action-owned persistence
   - later follow-up delivery must still enter through scheduler-owned
     proactive ticks and pass attention plus delivery guardrails
2. daily planning activation
   - explicit day or week planning turns may create operational goals or tasks
     through the same planning/action boundary used by other internal work
   - expression must return concrete planning help in the same turn
3. task or goal check-in
   - explicit user progress reports and proactive follow-up turns must reuse
     active goals, active tasks, task-status writes, and scoped reflection
     state instead of creating a separate check-in store
4. reflection-backed continuity
   - memory persistence plus reflection outputs remain the only long-horizon
     owners for continuity across reminder, planning, and check-in turns

Bounded reminder-preference contract:

1. proactive reminder eligibility remains preference-owned and must not be
   inferred solely from scheduler heuristics
2. explicit user opt-in or opt-out for reminders/check-ins may be represented
   as a typed planning intent and persisted through the action-owned
   conclusion-preference path
3. that preference may influence scheduler candidate selection and proactive
   delivery guards, but it must not bypass attention gates or action ownership
4. richer scheduling semantics such as calendar-grade due dates, recurrence
   editing, or UI-managed reminder controls remain outside the `v1` baseline

Production proactive baseline for no-UI `v1`:

1. production proactive should be enabled only for bounded opt-in follow-up,
   not for generic autonomous outreach
2. cadence ownership remains external-scheduler-owned in production
3. candidate selection remains limited to due planned work or relation-backed
   proposals admitted by the planned-action observer, rather than generic
   time-passing check-in pressure
4. delivery target remains bounded to Telegram direct message using recent chat
   id or the existing numeric user-id fallback
5. rollback posture remains explicit:
   - return production to `PROACTIVE_ENABLED=false`
   - treat `disabled_by_policy` as the safe fallback baseline if outreach drift
     or guardrail regressions appear

## Learned-State Introspection Baseline

Future UI or admin surfaces must distinguish backend-owned state families
instead of flattening them into one generic "personality memory" view.

Canonical learned-state families:

1. learned knowledge
   - semantic conclusions
   - tool-grounded semantic conclusions from approved external reads
   - affective conclusions
   - relation records
   - reflection-derived adaptive outputs such as theta or support patterns
2. learned preferences
   - profile-owned identity continuity such as `preferred_language`
   - conclusion-owned preferences such as `response_style`,
     `collaboration_preference`, `preferred_role`, and `proactive_opt_in`
3. selected role and selected skill metadata
   - current-turn role selection remains contextual runtime state
   - role and skill registries may be durable and revisable
   - selected skills remain non-executable capability guidance and not proof
     of a second execution subsystem
4. planning and active-work state
   - active goals, tasks, milestones, current plan steps, and pending
     subconscious proposals
5. adaptive state versus identity state
   - adaptive state may change through memory, reflection, relations, and
     policy-owned diagnostics
   - stable identity remains bounded by profile language continuity plus
     conclusion-owned preferences; adaptive state must not silently rewrite the
     identity contract

Truthfulness rule for "learned skills":

1. the repo may expose registry-defined skill metadata selected for the current
   turn or current plan
2. the repo may expose learned knowledge that influences skill selection
3. the repo may expose durable role presets and skill descriptions that were
   seeded manually or revised through bounded runtime or reflection learning
4. the repo must not claim that the personality learned a new executable skill,
   self-installed a tool, or created a second side-effect path unless an
   approved architecture change adds that capability explicitly
5. therefore `v1` introspection may truthfully show:
   - what the personality learned
   - which stable preferences it now carries
   - which role it selected
   - which role presets it has available
   - which skill metadata it selected
   - which skill descriptions or usage guidance it has available
   - what it is actively planning or tracking
   but not arbitrary self-authored tool logic or code-level skill mutation

Canonical introspection surfaces for that baseline:

1. `/health.learned_state`
   - exposes the shared policy owner for learned-state inspection
   - exposes the stable internal inspection path used by admin or future UI
     callers
   - freezes the bounded section contract for:
     - `identity_state`
     - `learned_knowledge`
     - `role_skill_state`
     - `planning_state`
   - freezes the bounded summary families for:
     - `preference_summary`
     - `knowledge_summary`
     - `reflection_growth_summary`
     - `planning_continuity_summary`
   - may describe tool-grounded learning posture and tool-grounded semantic
     conclusion families as part of `learned_knowledge`
2. `/health.api_readiness`
   - exposes the shared backend API-readiness owner for later `v2` UI
     consumers
   - freezes canonical health, internal inspection, connector, and current-turn
     debug surfaces instead of leaving UI integration to infer them
3. `GET /internal/state/inspect?user_id=...`
   - remains an internal debug-boundary surface
   - includes an `api_readiness` snapshot alongside bounded learned-state
     families
   - returns bounded backend-owned snapshots for:
     - `identity_state`
     - `learned_knowledge`
     - `role_skill_state`
     - `planning_state`
   - bounded summary views now include:
     - `identity_state.preference_summary`
     - `learned_knowledge.knowledge_summary`
     - `learned_knowledge.reflection_growth_summary`
     - `role_skill_state.selection_visibility_summary`
     - `planning_state.continuity_summary`
   - role/skill visibility remains metadata-only:
     - skill registry and role-skill policy may be inspected
     - current-turn selected role and selected skills are still read from
       `system_debug`, not inferred as durable executable skill growth
4. exported `incident_evidence.policy_posture["learned_state"]`
   - must carry the same policy owner, internal inspection path, and bounded
     section-contract metadata as `/health.learned_state`
   - exists so release smoke, behavior validation, and future UI readiness do
     not depend only on live health calls during incident review
5. learned personality-growth introspection remains explicitly bounded:
   - it may expose learned preferences, learned knowledge summaries, bounded
     reflection outputs, tool-grounded knowledge summaries, role registry
     metadata, selected role metadata, skill registry metadata, selected skill
     metadata, and planning continuity
   - it must not imply self-modifying executable skill learning, code
     generation ownership, or a second tool-execution path outside planning and
     action
   - tool use remains governed by the existing planning, permission-gate, and
     action boundary even when future UI inspects learned-state surfaces

---

## Backend Capability Catalog Baseline

Future UI or admin work must not reconstruct capability truth by stitching
together ad hoc health fields client-side.

Instead, one bounded backend capability catalog should compose already approved
backend-owned truth.

Canonical source surfaces for that catalog:

1. `/health.api_readiness`
   - declares the stable backend readiness owner and canonical source surfaces
     for later UI consumers
2. `/health.learned_state`
   - exposes the learned-state and tool-grounded-learning posture used to
     explain what the personality has learned
3. `/health.role_skill`
   - exposes the shared role/skill boundary owner, work-partner posture, and
     metadata-only skill boundary
4. `/health.connectors`
   - exposes connector execution baseline, web-knowledge tooling posture,
     organizer-tool activation snapshot, and provider-readiness truth
5. internal inspection and current-turn debug surfaces
   - `GET /internal/state/inspect?user_id=...`
   - `system_debug.role`
   - `system_debug.adaptive_state.selected_skills`
   - `system_debug.plan`

Canonical bounded sections for that catalog:

1. role posture
   - current role-selection boundary owner
   - current role visibility for internal callers
   - durable role-registry posture when registry-backed presets exist
2. skill catalog posture
   - metadata-only skill boundary owner
   - registry-backed skill catalog visibility
   - currently selected skill metadata for the turn or active plan
3. tool and connector posture
   - approved tool families
   - approved organizer-tool stack
   - provider activation and readiness posture
   - confirmation or opt-in boundaries
4. learned-state linkage
   - learned-state posture and tool-grounded-learning posture may be referenced
     so future UI can distinguish capability from learned knowledge

Guardrails:

1. the backend capability catalog is an aggregation contract over existing
   backend truth, not a new execution owner
2. the catalog must not become a second authorization matrix; connector
   permission gates and action-owned policies remain canonical
3. the catalog must not expose provider secrets, raw external payloads, or
   self-modifying executable skill-learning claims
4. role presets and skill catalog entries may be durable and inspectable, but
   they remain descriptive metadata unless planning and action explicitly use
   them through existing contracts
5. future UI or admin work may consume one backend capability-catalog surface,
   but the underlying source surfaces remain the canonical owners of truth
   until an explicit architecture change says otherwise

---

## Relation Retrieval Completion Baseline

Relation memory remains a first-class adaptive influence family, but relation
embeddings do not become part of the default steady-state retrieval completion
baseline.

1. steady-state retrieval completion remains `semantic + affective` for the
   foreground memory-retrieval baseline.
2. `relation` stays an explicit optional follow-on source family rather than a
   required completion condition for rollout readiness.
3. relation cues may still influence foreground behavior through
   relation-record reads and adaptive tie-break logic without promoting
   relation embeddings to default vector-retrieval coverage.
4. if `relation` embeddings are enabled, they remain governed by explicit
   source-rollout posture and must not silently redefine the steady-state
   retrieval baseline.
5. refresh ownership and provider ownership for relation embeddings inherit the
   same bounded embedding policy surfaces as other source families, but health
   and rollout guidance must continue to distinguish:
   - steady-state retrieval baseline
   - optional relation-source expansion posture
6. runtime `system_debug.adaptive_state.relation_source_policy` must expose the
   same owner-level optional-family posture for behavior-level traces, so
   event-scoped evidence does not rely only on `/health`.
7. future promotion of relation embeddings into the steady-state baseline
   requires a separate approved contract slice plus matching health, smoke, and
   behavior evidence.

---

## Perception Agent

### Purpose

Identify what happened.

### Input

```json
{
  "event": {}
}
```

### Output

```json
{
  "perception": {
    "event_type": "...",
    "topic": "...",
    "intent": "...",
    "language": "en",
    "ambiguity": 0.0,
    "initial_salience": 0.0,
    "affective": {
      "affect_label": "neutral|support_distress|urgent_pressure|positive_engagement",
      "intensity": 0.0,
      "needs_support": false,
      "confidence": 0.0,
      "source": "deterministic_placeholder|ai_classifier|fallback",
      "evidence": []
    }
  }
}
```

---

## Context Agent

### Purpose

Build situational understanding for the current turn.

### Input

```json
{
  "event": {},
  "perception": {},
  "memory": {},
  "conclusions": [],
  "goals": [],
  "tasks": [],
  "identity": {},
  "theta": {}
}
```

### Output

```json
{
  "context": {
    "summary": "...",
    "foreground_awareness_summary": "...",
    "known_user_name": "optional display name",
    "memory_continuity_available": true,
    "available_tool_hints": ["search_web", "read_page"],
    "related_goals": [],
    "related_tags": [],
    "risk_level": 0.0
  }
}
```

Foreground-awareness guardrails:

1. context must carry a bounded foreground-awareness summary for the active
   turn when runtime truth already knows current-turn time, human-facing
   identity facts, memory continuity posture, or bounded tool readiness
2. this foreground-awareness payload is descriptive turn truth, not a second
   planning or action subsystem
3. downstream stages may use it for truthful answers and tool selection, but
   execution authority still stays in planning and action

---

## Channel-Aware Delivery Constraint Contract

Channel-aware delivery belongs below expression, inside action and integration
delivery ownership.

Contract rules:

1. expression may still choose message content, tone, and structure, but it
   must not own Telegram length splitting, markdown escape policy, or
   transport-specific retry behavior
2. action remains the owner of delivery execution and may hand off one bounded
   delivery envelope to integration routing
3. integration delivery may adapt one prepared response for the selected
   transport, including:
   - bounded segmentation for channel message-length limits
   - bounded formatting normalization required by the selected transport
   - explicit fallback to plain text when transport formatting is unsafe
4. channel-aware delivery must not:
   - introduce a second cognition path outside planning -> expression -> action
   - make Telegram-specific limits a planning concern
   - change the semantic intent of the prepared response
5. transport adaptation is allowed to change only delivery shape, such as:
   - message chunk boundaries
   - safe markdown or plain-text formatting posture
   - per-message delivery ordering inside one response handoff
6. the same delivery contract must remain portable to later first-party app
   channels; Telegram is only the first channel that needs stronger adaptation
   proof

This contract freezes channel adaptation as delivery behavior, not channel-
specific reasoning.

---

## Motivation Agent

### Purpose

Determine how strongly the system should care.

### Input

```json
{
  "event": {},
  "context": {},
  "goals": [],
  "tasks": [],
  "theta": {},
  "identity": {}
}
```

### Output

```json
{
  "motivation": {
    "importance": 0.0,
    "urgency": 0.0,
    "valence": 0.0,
    "arousal": 0.0,
    "mode": "respond|ignore|analyze|execute|clarify"
  }
}
```

---

## Role Selection Agent

### Purpose

Select the behavioral stance for the turn.

### Input

```json
{
  "event": {},
  "context": {},
  "motivation": {},
  "identity": {},
  "theta": {}
}
```

### Output

```json
{
  "role": {
    "selected": "advisor|analyst|mentor|executor|friend",
    "confidence": 0.0,
    "selection_policy_owner": "role_selection_policy",
    "selection_reason": "...",
    "selection_evidence": [
      {
        "signal": "preferred_role",
        "source": "user_preference",
        "value": "analyst",
        "applied": true,
        "note": "..."
      }
    ],
    "selected_skills": [
      {
        "skill_id": "structured_reasoning",
        "label": "Structured reasoning",
        "capability_family": "analysis",
        "reason": "...",
        "side_effect_posture": "metadata_only"
      }
    ]
  }
}
```

---

## Planning Agent

### Purpose

Decide what should happen next.

### Input

```json
{
  "event": {},
  "context": {},
  "motivation": {},
  "role": {},
  "subconscious_proposals": [],
  "connector_capabilities": [],
  "goals": [],
  "tasks": [],
  "planned_work": [],
  "theta": {},
  "behavior_feedback": []
}
```

### Output

```json
{
  "plan": {
    "goal": "...",
    "steps": [],
    "needs_action": true,
    "needs_response": true,
    "inferred_promotion_diagnostics": [
      "reason=gate_open|trust_gate_low_confidence|missing_issue_marker|missing_repeated_signal|mode_not_supported|empty_event_text",
      "result=promote_inferred_task|promote_inferred_goal|maintain_task_status|no_goal_candidate|duplicate_goal_candidate|active_goal_already_present|goal_intent_already_present"
    ],
    "proposal_handoffs": [],
    "accepted_proposals": [],
    "selected_skills": [],
    "connector_permission_gates": [],
    "domain_intents": [
      {
        "intent_type": "upsert_planned_work_item",
        "work_kind": "follow_up|check_in|reminder|routine|research_window",
        "summary": "...",
        "delivery_window": {
          "not_before": "ISO-8601",
          "preferred_at": "ISO-8601",
          "expires_at": "ISO-8601"
        },
        "recurrence_mode": "none|daily|weekly|custom",
        "channel_hint": "telegram|api",
        "provenance": "explicit_user_request|planning_inference|reflection_inference"
      },
      {
        "intent_type": "reschedule_planned_work_item",
        "work_id": "pw-1",
        "delivery_window": {
          "not_before": "ISO-8601",
          "preferred_at": "ISO-8601",
          "expires_at": "ISO-8601"
        },
        "reason": "..."
      },
      {
        "intent_type": "cancel_planned_work_item",
        "work_id": "pw-1",
        "reason": "..."
      },
      {
        "intent_type": "complete_planned_work_item",
        "work_id": "pw-1",
        "reason": "..."
      },
      {
        "intent_type": "upsert_goal",
        "name": "...",
        "description": "...",
        "priority": "medium",
        "goal_type": "tactical"
      },
      {
        "intent_type": "update_task_status",
        "status": "done",
        "task_hint": "..."
      },
      {
        "intent_type": "promote_inferred_goal",
        "name": "...",
        "description": "Inferred goal from repeated execution evidence: ...",
        "priority": "medium|high",
        "goal_type": "tactical|operational",
        "evidence": "repeated_execution_blocker"
      },
      {
        "intent_type": "promote_inferred_task",
        "name": "...",
        "description": "Inferred task from repeated execution evidence: ...",
        "priority": "medium|high",
        "status": "todo|blocked",
        "evidence": "repeated_execution_blocker"
      },
      {
        "intent_type": "maintain_task_status",
        "status": "blocked",
        "task_hint": "...",
        "reason": "inferred_repeated_blocker_evidence"
      },
      {
        "intent_type": "calendar_scheduling_intent",
        "operation": "read_availability|suggest_slots|create_event|update_event|cancel_event",
        "provider_hint": "google_calendar|generic",
        "mode": "read_only|suggestion_only|mutate_with_confirmation",
        "title_hint": "...",
        "time_hint": "..."
      },
      {
        "intent_type": "external_task_sync_intent",
        "operation": "list_tasks|suggest_sync|create_task|update_task|link_internal_task",
        "provider_hint": "clickup|trello|generic",
        "mode": "read_only|suggestion_only|mutate_with_confirmation",
        "task_hint": "..."
      },
      {
        "intent_type": "connected_drive_access_intent",
        "operation": "list_files|search_documents|read_document|suggest_file_plan|upload_file|update_document|delete_file",
        "provider_hint": "google_drive|onedrive|dropbox|generic",
        "mode": "read_only|suggestion_only|mutate_with_confirmation",
        "file_hint": "..."
      },
      {
        "intent_type": "connector_capability_discovery_intent",
        "connector_kind": "calendar|task_system|cloud_drive",
        "provider_hint": "google_calendar|clickup|google_drive|generic",
        "requested_capability": "availability_read|task_sync|file_upload|connector_access",
        "evidence": "repeated_unmet_need",
        "mode": "suggestion_only"
      },
      {
        "intent_type": "maintain_relation",
        "relation_type": "delivery_reliability|collaboration_dynamic|support_intensity_preference|contact_cadence_preference|interruption_tolerance|interaction_ritual_preference",
        "relation_value": "high_trust|guided|high_support|on_demand|low_frequency|scheduled_only|low|high|avoid_repeated_greeting|warm_opening_ok",
        "confidence": 0.0,
        "source": "planning_intent",
        "scope_type": "global|goal|task",
        "scope_key": "global|goal_id|task_id",
        "evidence_count": 1,
        "decay_rate": 0.02
      },
      {
        "intent_type": "update_proactive_state",
        "state": "attention_gate_blocked|interruption_deferred|delivery_guard_blocked|delivery_ready",
        "trigger": "task_blocked|goal_stagnation|time_checkin|...",
        "reason": "...",
        "output_type": "suggestion|reminder|question|warning|encouragement|insight",
        "mode": "soft|medium|strong",
        "source": "proactive_planning"
      },
      {
        "intent_type": "noop",
        "reason": "no_domain_change_detected"
      }
    ]
  }
}
```

---

## Expression Agent

### Purpose

Form the outward communication of the turn.

### Input

```json
{
  "event": {},
  "context": {},
  "motivation": {},
  "role": {},
  "plan": {},
  "identity": {},
  "theta": {}
}
```

### Output

```json
{
  "expression": {
    "message": "...",
    "tone": "...",
    "channel": "api|telegram",
    "language": "en"
  }
}
```

Foreground truthfulness guardrails:

1. expression may answer current-turn name or time questions directly from
   foreground runtime truth when those facts are already present
2. expression must not claim that memory continuity, current-turn time
   awareness, or bounded search/page-read capability are unavailable when the
   active foreground-awareness contract marks them as available
3. if bounded external-read results already exist in the same turn, expression
   or the action-delivery handoff may summarize them, but action remains the
   side-effect owner of those reads
4. expression may consume high-confidence communication-boundary relations to
   shape wording and interaction ritual, including avoiding repeated greeting
   openings when the relation model requests it; expression must not mutate
   durable relation state

---

## Response-Execution Handoff Contract

Expression produces an explicit execution handoff consumed by action.

Minimum handoff fields:

```json
{
  "response_execution_handoff": {
    "message": "...",
    "tone": "...",
    "channel": "api|telegram",
    "language": "en",
    "chat_id": 123456
  }
}
```

Rules:

1. expression owns wording, tone, and language in the handoff payload
2. action consumes the handoff contract instead of rebuilding delivery details
   from implicit expression coupling
3. handoff creation is side-effect-free; action remains the only execution
   owner

Current no-UI `v1` delivery baseline:

1. the stable production contract is still text-first
2. Telegram delivery remains bounded to a normal outbound text reply using the
   resolved `chat_id`
3. richer channel behavior such as segmentation, media attachments, or
   generated-image replies requires an explicit bounded handoff extension
   before action may execute it

Future multimodal direction:

1. if the repo later supports photo context, voice-note transcription, or
   image reply delivery, the handoff should widen through explicit bounded
   content blocks or attachment descriptors rather than ad hoc transport flags
2. expression may describe the intended communicative payload, for example:
   - reply text
   - caption text
   - requested output modality
   - bounded attachment descriptors
3. action and integration routing must remain the only owners of:
   - provider file upload or fetch
   - Telegram or app-specific media-send methods
   - final delivery execution evidence
4. multimodal support must stay channel-neutral enough that Telegram and a
   later first-party app can share one cognitive handoff shape with
   transport-specific execution adapters

---

## Action Layer Contract

### Purpose

Execute the required side effects.

### Input

```json
{
  "event": {},
  "plan": {},
  "response_execution_handoff": {},
  "domain_intents": []
}
```

### Output

```json
{
  "action_result": {
    "status": "success|partial|fail|noop",
    "actions": [],
    "notes": "..."
  }
}
```

---

## Memory Write Contract

### Purpose

Persist the finished episode after the turn.

### Input

```json
{
  "event": {},
  "context": {},
  "role": {},
  "motivation": {},
  "plan": {},
  "domain_intents": [],
  "expression": {},
  "action_result": {}
}
```

### Output

```json
{
  "memory_record": {
    "summary": "...",
    "importance": 0.0
  }
}
```

---

## Reflection Agent

### Purpose

Analyze patterns across memory and update slower-moving state.

### Input

```json
{
  "recent_memory": [],
  "existing_conclusions": [],
  "theta": {},
  "goals": [],
  "tasks": []
}
```

### Output

```json
{
  "reflection": {
    "new_conclusions": [],
    "updated_conclusions": [],
    "theta_update": {},
    "relation_update": {},
    "progress_update": {},
    "adaptive_output_summary": {
      "adaptive_output_count": 0,
      "conclusion_kinds": [],
      "relation_types": [],
      "proposal_types": [],
      "progress_signal_kinds": [],
      "theta_update": {
        "present": false,
        "dominant_channel": null
      },
      "foreground_mutation_posture": "background_owned_only"
    }
  }
}
```

---

## Reflection Topology And Worker-Mode Contract

Background reflection keeps one explicit enqueue/dispatch boundary independent
of worker deployment shape.

Minimum topology fields:

```json
{
  "reflection_topology": {
    "runtime_mode": "in_process|deferred",
    "enqueue_owner": "runtime_followup",
    "dispatch_owner": "in_process_worker|external_driver|none",
    "queue_backend": "durable_postgres_queue"
  },
  "reflection_task": {
    "task_id": 1,
    "user_id": "...",
    "event_id": "...",
    "status": "pending|processing|completed|failed",
    "attempts": 0,
    "max_attempts": 3,
    "retry_backoff_seconds": [5, 30, 120],
    "last_error": null
  }
}
```

Rules:

1. foreground runtime enqueues reflection durably after episodic persistence
2. enqueue ownership does not depend on in-process worker availability
3. `in_process` mode may dispatch immediately; `deferred` mode leaves tasks
   pending for a scheduler/driver
4. retry semantics are queue-owned and stable across worker modes
5. reflection execution never blocks foreground response completion
6. health posture must expose runtime mode plus queue/worker visibility
   required for operator triage

---

## Contract Rules

1. every stage returns only its own output field
2. no stage returns the full system state as its main output
3. no stage except Action performs side effects
4. expression shapes communication before action executes it
5. reflection updates future state asynchronously
6. planning owns domain-change intent; action executes only explicit domain intents
7. proactive follow-up state and future relation-maintenance writes must use
   explicit typed intents instead of generic fallback payloads or `noop`
8. runtime topology switches (reflection mode, durable attention owner) must
   be driven by one explicit machine-visible switch policy instead of implicit
   rollout intuition
9. proposal handoff decisions remain fixed to
   `accept|merge|defer|discard` unless a future contract explicitly widens the
   decision set
10. learned preferences and theta remain bounded tie-break signals, not broader
    identity or proactive-attention owners

---

## Validation

Each contract should be:

- schema-valid
- minimal
- explicit
- testable

---

## Common Mistakes

- mixing cognition with side effects
- returning too much state from one stage
- letting action decide message content
- letting expression mutate durable state
- letting reflection silently rewrite identity

---

## Final Principle

Contracts are what keep AION coherent while the implementation evolves.

If contracts are clear:

- the runtime is predictable
- testing is straightforward
- refactors stay safe

If contracts are unclear, architectural drift becomes invisible.
