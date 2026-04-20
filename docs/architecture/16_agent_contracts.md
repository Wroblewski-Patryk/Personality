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
  "attention_inbox": [],
  "pending_turn": {},
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

---

## Attention Inbox And Proposal Handoff Contract

The dual-loop boundary should remain explicit in runtime state.

Minimum contract fields:

```json
{
  "attention_inbox": [
    {
      "item_id": "attn-1",
      "source": "user_event|scheduler_tick|subconscious_proposal",
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
      "reason": "connector_not_enabled|permission_required|confirmation_required|proposal_only_no_external_access"
    }
  ]
}
```

Rules:

1. connector capabilities can inform planning but do not execute by themselves
2. permission gates are explicit plan outputs consumed by action boundaries
3. internal goals/tasks remain first-class internal planning state

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
    "related_goals": [],
    "related_tags": [],
    "risk_level": 0.0
  }
}
```

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
    "confidence": 0.0
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
  "theta": {}
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
    "proposal_handoffs": [],
    "accepted_proposals": [],
    "connector_permission_gates": [],
    "domain_intents": [
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
    "progress_update": {}
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
