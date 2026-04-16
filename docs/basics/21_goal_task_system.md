# Goal and Task System

## Purpose

This document defines how AION stores, understands, and uses goals and tasks.

Goals and tasks give the system direction.

Without them:

- the system only reacts  
- planning has no anchor  
- motivation loses context  
- memory becomes disconnected from purpose  

The Goal and Task System turns AION from a reactive assistant into a directed cognitive system.

---

## Core Principle

Goals define direction.  
Tasks define executable steps.

AION must be able to:

- know what matters long-term  
- know what matters now  
- connect incoming events to active goals  
- turn plans into actionable tasks  
- monitor progress over time  

---

## Definitions

### Goal

A goal is a meaningful target the system should support over time.

Examples:

- improve health  
- finish project MVP  
- organize weekly planning  
- increase consistency in work  

Goals are directional and persistent.

---

### Task

A task is a concrete action or actionable unit related to a goal.

Examples:

- write first API endpoint  
- plan tomorrow morning  
- review memory retrieval logic  
- send project update  

Tasks are operational and shorter-term.

---

## Goal Hierarchy

Goals may exist on multiple levels.

### 1. Strategic Goals

Long-term and high-level.

Examples:

- build AION MVP  
- improve personal productivity  
- transition to remote work  

---

### 2. Tactical Goals

Mid-level goals that support strategic goals.

Examples:

- complete architecture docs  
- implement Telegram integration  
- improve runtime stability  

---

### 3. Operational Goals

Short-term and concrete.

Examples:

- finish file 15  
- fix API validation  
- test memory retrieval  

AION does not need full hierarchy in MVP,
but the model should allow it.

---

## Task Hierarchy

Tasks may also have structure.

### 1. Atomic Tasks

Single executable unit.

Examples:

- write endpoint  
- send message  
- update task status  

---

### 2. Composite Tasks

Task made of multiple subtasks.

Examples:

- implement conscious loop  
  - define state  
  - add perception  
  - connect planning  
  - test output  

For MVP, simple tasks are enough, but composition should be possible later.

---

## Why Goals Matter in Cognition

Goals influence:

- memory relevance  
- motivation intensity  
- role selection  
- planning quality  
- proactive behavior  

If an event relates strongly to an active goal, it should matter more.

This is how AION stays purposeful.

---

## Why Tasks Matter in Cognition

Tasks influence:

- short-term action  
- operational planning  
- workload awareness  
- progress monitoring  
- what the system reminds or suggests next  

If goals define “why”,
tasks define “what next”.

---

## Goal Data Model

Each goal should contain at least:

- id  
- user_id  
- name  
- description  
- priority  
- status  
- type  
- created_at  
- updated_at  

Optional fields:

- parent_goal_id  
- target_date  
- domain  
- success_criteria  
- tags  
- progress_estimate  

---

## Task Data Model

Each task should contain at least:

- id  
- user_id  
- goal_id  
- name  
- description  
- status  
- priority  
- created_at  
- updated_at  

Optional fields:

- due_date  
- recurrence_rule  
- tags  
- estimated_effort  
- parent_task_id  
- completion_notes  

---

## Goal Status

Possible goal statuses:

- active  
- paused  
- completed  
- dropped  
- archived  

Goals should not be silently forgotten.

---

## Task Status

Possible task statuses:

- todo  
- in_progress  
- blocked  
- done  
- cancelled  

Status must stay explicit.

---

## Goal Priority

Goal priority helps AION decide what matters more.

Simple MVP scale:

- low  
- medium  
- high  
- critical  

Future version may use numeric scoring.

---

## Task Priority

Task priority helps AION choose execution order.

Simple MVP scale:

- low  
- medium  
- high  

Priority should interact with urgency and motivation, not replace them.

---

## Goal Influence on Runtime

During runtime, AION should ask:

- does this event relate to an active goal?  
- which goals are affected?  
- does this increase or reduce progress?  
- should goal relevance raise motivation?  

This connects cognition to direction.

---

## Task Influence on Runtime

During runtime, AION should ask:

- is there an existing task related to this event?  
- should a new task be created?  
- should a task be updated?  
- is a blocked task causing repeated issues?  

This connects cognition to operational reality.

---

## Goal Retrieval Strategy

Before deeper planning, the system should retrieve:

- active high-priority goals  
- goals related to current event  
- recent goal changes  
- goal-linked conclusions if relevant  

Not all goals should be loaded every time.

Relevance matters.

---

## Task Retrieval Strategy

System should retrieve:

- active tasks related to current event  
- tasks linked to relevant goals  
- overdue or blocked tasks if they matter  
- recent task changes if context requires it  

This prevents repetitive suggestions and disconnected planning.

---

## Goal-Task Relationship

Each task should preferably belong to a goal.

This creates structure:

goal → tasks → actions

If a task has no goal:

- it may be temporary  
- or the goal structure may be incomplete  

For MVP, some goal-less tasks may exist,
but the system should move toward linkage.

---

## Goal-Task Flow in Planning

Planning should work like this:

1. identify relevant goal  
2. determine whether task already exists  
3. update or create task if necessary  
4. align response with goal context  

This prevents planning from becoming abstract fluff.

---

## Goal-Task Flow in Memory

Memory should store links to:

- related goal  
- related task  
- progress relevance  
- whether the event advanced or blocked the goal  

This makes memory more useful later.

---

## Goal-Task Flow in Reflection

Subconscious loop should analyze:

- which goals are progressing  
- which goals are stagnating  
- which tasks repeat without completion  
- where system/user friction exists  
- whether tasks are realistic  

This allows AION to detect patterns such as:

- overplanning  
- poor follow-through  
- recurring blockers  
- low alignment between goals and daily actions  

---

## Goal Relevance Scoring

AION may estimate goal relevance during context building.

Simple example factors:

- direct mention in event  
- semantic similarity  
- recent activity on goal  
- priority of goal  
- task linkage  

This score can influence motivation.

---

## Task Creation Rules

AION may create a task when:

- event implies a clear actionable next step  
- no equivalent active task already exists  
- task supports an active goal  
- user intent or system logic justifies it  

Task creation must not be automatic in every case.

Too many tasks = cognitive spam.

---

## Task Update Rules

AION may update a task when:

- event changes its status  
- action completed it  
- blocker was identified  
- priority changed  
- due date changed  
- task is no longer relevant  

Updates should be explicit and logged.

---

## Task Deletion Rules

Hard deletion should be rare.

Prefer:

- cancelled  
- archived  
- inactive  

This preserves history and reduces data loss.

---

## Recurring Tasks

Some tasks may repeat.

Examples:

- morning review  
- daily planning  
- weekly reflection  

Recurring tasks should use explicit recurrence logic.

AION must distinguish between:

- one-time task  
- recurring task  
- repeated pattern mistaken for task  

---

## Goals and Motivation

Goals strongly influence motivation.

Example:

If event is linked to a critical active goal,
importance should increase.

If event blocks an important goal,
danger or urgency may increase.

This makes AION purpose-sensitive rather than merely reactive.

---

## Goals and Roles

Goal context may influence role selection.

Examples:

- planning-related goal → advisor / executor  
- emotionally difficult blocked goal → mentor  
- technical implementation goal → analyst / executor  

This helps role selection stay grounded.

---

## Tasks and Action System

Action System may execute:

- create task  
- update task  
- close task  
- link task to event or goal  

This is where planning becomes operational reality.

---

## Proactive Use of Goals and Tasks

AION may become proactive when:

- important goal has no recent progress  
- high-priority task remains blocked  
- recurring goal pattern is being ignored  
- timing suggests reminder or check-in is useful  

This is one of the key future strengths of the system.

---

## Safety Rules

Goals and tasks must not:

- overwhelm the user with busywork  
- multiply without clear value  
- replace strategic thinking with endless micro-actions  
- become disconnected from real priorities  

AION should reduce chaos, not automate it.

---

## MVP Requirements

For MVP, Goal and Task System must support:

- active goals  
- active tasks  
- goal/task retrieval during runtime  
- simple task creation  
- simple task update  
- task-goal linkage where possible  

That is enough to make the system directional.

---

## Future Extensions

Later versions may support:

- nested goals  
- task dependencies  
- progress scoring  
- automatic prioritization  
- calendar linkage  
- energy-aware task suggestions  
- business goal layers  
- long-term strategic reviews  

But the foundation must stay simple first.

---

## Final Principle

Goals give AION direction.
Tasks give AION operational traction.

Without goals, the system has no direction.
Without tasks, the system has no execution path.

Current MVP status:

- runtime can now load active goals and active tasks before deeper planning
- context can surface relevant active goals and tasks for the current event
- motivation can now care more when an event touches a higher-priority goal or a blocked active task
- planning can now align with an active goal and suggest unblocking or advancing an active task
- explicit user phrases such as `My goal is to ...` and `I need to ...` can now seed lightweight goals and tasks through the Action layer
- explicit user progress phrases such as `I fixed ...` can now update matching task status
- runtime now refreshes active goal/task state after Action-layer writes, so the returned result reflects the latest operational state
- background reflection can now derive a lightweight `goal_execution_state` such as `blocked`, `recovering`, `advancing`, or `progressing` from active goals, active tasks, and recent task status updates
- background reflection can now also detect an early `stagnating` pattern when the system keeps planning around an active goal without seeing recent operational traction
- background reflection can now also estimate a lightweight `goal_progress_score` from the active task mix, so runtime can distinguish an early-stage goal from one that is close to completion
- background reflection can now also compare the latest reflected score against the previous one and infer a lightweight `goal_progress_trend` such as `improving`, `steady`, or `slipping`
- background reflection now also writes lightweight `aion_goal_progress` snapshots for the primary active goal, so runtime can use short progress history during context-building and planning
- that reflected goal state can now shape context, motivation, and planning even when the current turn does not restate the full blocker details

Together, they turn cognition into progress.
