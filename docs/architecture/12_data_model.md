# Data Model

## Purpose

This document defines the canonical data model of AION.

The goal is to support:

- memory
- identity
- adaptation
- decision making

Without proper structure, AION cannot function as a persistent cognitive system.

---

## Core Principle

Data must reflect cognition.

If the system:

- remembers
- learns
- adapts

then the data model must support those operations explicitly.

---

## Core Entities

### users

Stores the owner or user identity root.

Fields:

- id
- created_at
- updated_at
- name

### identity

Stores the stable identity definition.

Fields:

- id
- user_id
- mission
- values
- behavior_rules
- created_at
- updated_at

### theta

Stores adaptive parameters.

Fields:

- id
- user_id
- emotional
- display
- learning
- cognitive
- updated_at

### episodic_memory

Stores episode history.

Fields:

- id
- user_id
- event_id
- timestamp
- summary
- context
- role
- plan
- result
- importance

### conclusions

Stores learned patterns and semantic summaries.

Fields:

- id
- user_id
- type
- content
- confidence
- created_at
- updated_at

### goals

Stores long-lived direction.

Fields:

- id
- user_id
- name
- description
- priority
- status

### tasks

Stores actionable work linked to goals when possible.

Fields:

- id
- user_id
- goal_id
- name
- status
- priority

### planned_work_items

Stores time-aware future work derived from planning.

This entity extends internal planning state. It is not a separate reminder
subsystem, even when the eventual outward delivery is phrased as a reminder or
check-in.

Fields:

- id
- user_id
- goal_id
- task_id
- kind
- summary
- status
- not_before
- preferred_at
- expires_at
- recurrence_mode
- delivery_channel
- provenance
- last_evaluated_at

### metrics

Stores measurable runtime or behavioral data.

Fields:

- id
- user_id
- name
- value
- timestamp

### role_registry

Stores durable role presets available for runtime selection.

Fields:

- id
- user_id
- name
- description
- prompt_preset
- selection_hints
- provenance
- status
- created_at
- updated_at

### skill_registry

Stores durable skill descriptions and usage guidance.

Fields:

- id
- user_id
- name
- description
- usage_guidance
- limitations
- approved_tool_families
- revision_notes
- provenance
- status
- created_at
- updated_at

### tool_registry

Stores approved tool families and provider-backed operations.

Fields:

- id
- tool_family
- provider_hint
- operation
- activation_requirements
- status
- created_at
- updated_at

### user_tool_authorizations

Stores whether a user has authorized a tool family or provider path.

Fields:

- id
- user_id
- tool_family
- provider_hint
- activation_status
- consent_source
- created_at
- updated_at

---

## Relationships

- user -> identity (1:1)
- user -> theta (1:1)
- user -> episodic_memory (1:N)
- user -> conclusions (1:N)
- user -> role_registry (1:N)
- user -> skill_registry (1:N)
- user -> user_tool_authorizations (1:N)
- user -> goals (1:N)
- goals -> tasks (1:N)
- user -> planned_work_items (1:N)
- goals -> planned_work_items (1:N)
- tasks -> planned_work_items (1:N)
- tool_registry -> user_tool_authorizations (1:N)

Planned work may later produce due attention or bounded foreground delivery,
but scheduler reevaluation and durable storage must not bypass the existing
planning -> expression -> action boundary for user-visible output.

---

## Storage

The canonical model requires durable structured storage.

It may later be extended with:

- vector retrieval
- relation graphs
- richer memory-link structures
- role/skill revision history
- tool capability catalog snapshots

Those extensions should not replace the core entities above.

Raw provider secrets still remain external configuration.
Durable tool-authorization records exist to control whether a user may enable
or use a tool family, not to hardcode secrets into the database by default.

---

## Memory Priority

Not all stored data is equal.

Each retrievable memory should preserve:

- importance
- relevance
- recency

These signals influence retrieval quality.

---

## Minimal MVP Entities

- users
- identity
- theta
- episodic_memory
- conclusions

Goals and tasks may be introduced early, but the minimal architecture only requires enough persistence to preserve continuity and learning.

---

## Optional Future Entities

- relation_notes
- event_logs
- memory_links
- theta_history
- proactive_triggers
- planned_work_history
- role_revision_history
- skill_revision_history
- tool_credential_references

---

## Final Principle

Database design is part of cognition design.

If the data model is weak, the system cannot become meaningfully stateful.
