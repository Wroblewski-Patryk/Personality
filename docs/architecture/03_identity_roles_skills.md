# Identity / Roles / Skills

## Purpose

This document defines how AION maintains a stable identity while adapting
behavior across different contexts.

Key distinction:

- identity = who the system is
- role = how it behaves in a situation
- skill = what it can do

These must never be mixed.

---

## Identity

Identity is the stable core of AION.

It defines:

- values
- long-term orientation
- behavioral style
- boundaries
- system purpose
- relation to the user

Identity must remain stable over time.

It is not:

- a mood
- a role
- a temporary prompt

It is the behavioral spine of the system.

---

## Identity as Constraint

Identity is not only descriptive.
It actively influences behavior.

It affects:

- decision making
- communication style
- prioritization
- response patterns
- conflict handling

Every action should pass through identity.

---

## Roles

Roles are dynamic modes of operation.

They depend on:

- context
- event type
- user need
- goal relevance
- situation complexity

Examples:

- friend
- advisor
- analyst
- executor
- mentor

AION always remains the same identity.

Roles only change expression and behavior mode.

---

## Role Selection

Role selection is a runtime decision.

It should be based on:

- event type
- context
- user state
- goals
- risk

Roles can be combined:

- advisor + analyst
- mentor + executor

But must remain controlled and intentional.

---

## Role Registry

Roles may be backed by a durable registry.

That registry may store:

- role name
- role description
- role prompt or prompt preset
- selection hints
- status such as preset, learned, archived
- provenance such as seed, runtime-derived, reflection-derived

The registry exists so AION can keep multiple role presets and later choose
between them at runtime.

This does not change the core rule:

- runtime still selects the active role for the turn
- role records do not become separate personas
- role prompt storage does not bypass identity

---

## Skills

Skills are capabilities.

They define what AION can do.

Examples:

- communication
- planning
- programming
- analysis
- research
- problem solving

Skills are reusable across roles.

Example:

- both advisor and mentor use communication
- but in different ways

---

## Skill Registry

Skills may be backed by a durable registry.

That registry may store:

- skill name
- current description
- usage guidance
- limitations
- linked approved tool families
- revision or confidence metadata
- provenance such as seed, runtime-derived, reflection-derived

This allows AION to improve how it describes and selects skills over time.

The registry does not grant execution authority.

So even when a skill description evolves:

- planning may use it as guidance
- runtime may inspect it as learned capability metadata
- action remains the only side-effect owner

## Tool Authorization Records

Approved tool use may also be backed by durable per-user authorization
records.

That registry layer may store:

- user identity or scope owner
- approved tool family
- approved operation or bounded workflow
- authorization state such as available, opt-in required, confirmation
  required, or blocked
- provider-readiness hints and provenance

These records exist so runtime and operator surfaces can describe which tools
are merely available in the product, which ones are selectable in planning,
and which ones are actually authorized for a given user.

They do not create a second execution boundary.

So even when authorization records evolve:

- planning may use them as permission gates and bounded tool hints
- runtime may expose them through truthful inspection surfaces
- action remains the only side-effect owner

## Durable Capability Records

Role presets, skill descriptions, and per-user tool authorization records form
one durable capability-record layer.

That layer exists to preserve learned or configured capability metadata over
time without changing the core architecture rule:

- identity stays stable
- runtime still selects the active role for the turn
- skills remain descriptive guidance rather than executable authority
- tool authorization remains a bounded permission posture, not a second action
  engine

The capability-record layer must always distinguish:

- description: what is stored or described durably
- selection: what runtime may choose for a turn
- authorization: what tools or operations are actually allowed for a user

Any caller that cannot preserve those distinctions should consume backend
truth surfaces rather than reconstruct them client-side.

---

## Core Rule

Identity = ONE
Roles = MANY
Skills = MANY

Breaking this rule leads to chaos.

---

## Theta System

Theta is the adaptive parameter layer.

It controls how identity is expressed.

Categories:

- emotional
- display
- learning
- unconscious
- cognitive

---

## Theta Parameters

Examples:

- reactivity
- emotional regulation
- directness
- warmth
- learning rate
- reflection depth
- uncertainty tolerance

Theta evolves over time.

---

## Identity vs Theta

Identity:
- stable
- rarely changes
- defines principles

Theta:
- dynamic
- updates gradually
- defines expression

---

## Example

Identity:
- direct
- constructive
- analytical

Theta:
- warmth: 0.6
- directness: 0.8
- learning_rate: 0.1

Result:
Same system, different expression over time.

---

## Identity Evolution

Identity can change only when:

- patterns repeat consistently
- strong evidence exists
- reflection confirms necessity

It must never change based on a single event.

---

## Role Safety Rules

Roles must not:

- contradict identity
- bypass safety
- invent authority
- behave like separate personalities

Roles are controlled modes, not independent entities.

---

## Skills and Execution

Skills define ability.

Execution is handled by the Action layer.

Example:

Skill:
- research

Execution:
- database query
- API call
- retrieval system

Skills != tools
Skills != actions

Skills may reference approved tool families, but they still do not execute
those tools on their own.

---

## Roles, Skills, And Tools

The boundary stays explicit:

- role = behavioral preset or mode
- skill = reusable capability description
- tool = external capability executed only through permission-gated action

Tools may be linked from skills as approved usage context.

That does not mean:

- the skill owns the tool
- the role owns the tool
- the model may bypass permission gates

User authorization remains the owner of tool activation.

---

## Suggested Structure

identity_profile:
- mission
- values
- behavior

theta_profile:
- emotional
- display
- learning

role_registry:
- role name
- description
- prompt preset
- conditions
- provenance
- status

skill_registry:
- skill name
- capability
- usage guidance
- limitations
- approved tool families
- provenance
- status

tool_registry:
- tool family
- provider hint
- allowed operations
- activation requirements

user_tool_authorizations:
- user id
- tool family
- provider hint
- activation status
- consent source

---

## Final Principle

AION is coherent because:

- identity is stable
- roles are controlled
- skills are reusable
- theta adapts expression

This is what turns the system from a chatbot into a cognitive architecture.
