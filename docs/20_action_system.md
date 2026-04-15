# Action System

## Purpose

This document defines how AION performs real actions in the world.

The Action System is responsible for executing side effects.

Without it:

- plans stay theoretical  
- decisions never become outcomes  
- system cannot affect anything outside reasoning  

The Action System is the execution layer of AION.

---

## Core Principle

Action is separate from cognition.

Reasoning decides:

- what should happen  
- why it should happen  

Action executes:

- database writes  
- API calls  
- task creation  
- message sending  
- internal state changes  

This separation is mandatory.

---

## Responsibilities

The Action System must:

- receive structured plan  
- decide which side effects are required  
- execute them safely  
- return structured result  
- log execution status  

---

## What Counts as Action

Examples of valid actions:

- save memory  
- create task  
- update goal  
- send Telegram message  
- call external API  
- trigger internal background job  
- write metric  
- store conclusion  

Examples of non-actions:

- analyzing context  
- generating plan  
- choosing tone  
- reflecting on patterns  

Those belong to other layers.

---

## Action Input

The Action System receives:

- event  
- plan  
- context  
- action requirements  
- user_id  
- trace_id  

Example:

{
  "event": {},
  "plan": {
    "goal": "Create task for follow-up",
    "steps": [
      "Create task",
      "Notify user"
    ],
    "needs_action": true,
    "needs_response": true
  },
  "context": {},
  "meta": {
    "user_id": "uuid",
    "trace_id": "uuid"
  }
}

---

## Action Output

The Action System must return structured output.

Example:

{
  "action_result": {
    "status": "success",
    "actions": [
      "task_created",
      "telegram_sent"
    ],
    "notes": "Task created and user notified"
  }
}

Possible statuses:

- success  
- partial  
- fail  
- noop  

---

## Core Rule

Only the Action System may perform side effects.

No other part of AION may:

- write to database directly  
- call external services directly  
- send user messages directly  
- modify persistent state directly  

If this rule breaks, architecture becomes chaotic.

---

## Action Categories

### 1. Internal Persistence

Used for:

- saving memory  
- storing conclusions  
- updating theta  
- writing logs  
- saving metrics  

These actions affect internal state.

---

### 2. User Communication

Used for:

- sending Telegram messages  
- future app notifications  
- reminders  
- proactive check-ins  

These actions affect the user directly.

---

### 3. External Tool Actions

Used for:

- HTTP requests  
- API integrations  
- external services  
- future automation systems  

These actions affect outside systems.

---

### 4. Runtime Triggers

Used for:

- starting background reflection  
- scheduling next event  
- triggering internal workers  

These actions affect internal execution flow.

---

## Action Decision Model

Not every plan requires action.

Possible outcomes:

### Noop

Nothing external should happen.

Example:
- internal reasoning only  
- response handled elsewhere  
- no state change needed  

---

### Internal Action Only

Example:
- write memory  
- update state  
- create reflection trigger  

---

### Communication Action Only

Example:
- send Telegram message  

---

### Combined Action

Example:
- create task  
- store result  
- notify user  

---

## Action Safety Rules

Every action must be:

- explicit  
- validated  
- traceable  
- reversible when possible  
- logged  

System must never perform uncontrolled side effects.

---

## Validation Before Execution

Before execution, Action System should validate:

- is action required?  
- is input complete?  
- is target valid?  
- does user/context allow this action?  
- is duplicate action likely?  

If validation fails, action should not execute blindly.

---

## Idempotency

Where possible, actions should be idempotent.

This means:

- retrying should not create duplicate effects  
- same event should not create two identical tasks  
- same trace should not send same notification twice unless intended  

This is critical in real systems.

---

## Action Execution Flow

1. receive plan  
2. validate action requirements  
3. classify action type  
4. execute action(s)  
5. collect results  
6. build structured action_result  
7. log trace  
8. return result  

---

## Database Actions

Examples:

- insert memory  
- update theta  
- create task  
- update goal  
- store metric  
- save reflection result  

Rules:

- use repository/service layer  
- validate before write  
- log write result  
- avoid silent failures  

---

## Messaging Actions

Examples:

- send Telegram message  
- send proactive prompt  
- send alert  

Rules:

- channel formatting should be prepared before action  
- Action System sends, but does not decide content  
- failures must be logged  
- duplicate sends should be prevented where possible  

---

## API Actions

Examples:

- call external service  
- fetch external data  
- update remote system  

Rules:

- use timeout  
- handle failure gracefully  
- validate response  
- log request/response summary  
- never crash whole runtime because one API failed  

---

## Partial Success

Sometimes one action succeeds and another fails.

Example:

- task created  
- Telegram send failed  

This must return:

- partial status  
- detailed actions list  
- failure notes  

Example:

{
  "action_result": {
    "status": "partial",
    "actions": [
      "task_created"
    ],
    "notes": "Task created, Telegram send failed"
  }
}

This is better than fake success.

---

## Failure Handling

If action fails:

- log error  
- return structured failure  
- preserve trace_id  
- do not hide the failure  
- allow retry if safe  

System should degrade gracefully.

---

## Retry Strategy

Retries are useful for:

- temporary API failure  
- DB timeout  
- message send issue  

Retries are dangerous for:

- non-idempotent actions  
- duplicate creation  
- repeated notifications  

Retry policy must depend on action type.

---

## Action Logging

Each action should log:

- trace_id  
- event_id  
- action type  
- target  
- status  
- duration  
- error if any  

This allows debugging and trust.

---

## Action Examples

### Example 1 – Memory Write

Plan says:

- store current episode  

Action result:

{
  "action_result": {
    "status": "success",
    "actions": [
      "memory_written"
    ],
    "notes": "Episode stored successfully"
  }
}

---

### Example 2 – Task Creation + Notification

Plan says:

- create task  
- notify user  

Action result:

{
  "action_result": {
    "status": "success",
    "actions": [
      "task_created",
      "telegram_sent"
    ],
    "notes": "Task created and notification sent"
  }
}

---

### Example 3 – No Action

Plan says:

- respond only, no external changes  

Action result:

{
  "action_result": {
    "status": "noop",
    "actions": [],
    "notes": "No side effects required"
  }
}

---

## Action System and Expression

Expression creates the message content.  
Action sends the message.

This distinction must stay clear.

Expression answers:
- what to say  

Action answers:
- how to deliver it  

---

## Action System and Memory

After execution, Action System must make result available to memory layer.

Why?

Because what happened matters.

The system should remember not only what it planned,
but also what actually happened.

---

## MVP Requirements

For MVP, Action System must support at least:

- memory write  
- Telegram send  
- simple DB update  
- task creation  
- noop handling  

That is enough to make AION operational.

---

## Future Extensions

Later Action System may support:

- business tools  
- calendar integration  
- email  
- document generation  
- internal workflow triggers  
- external automation hooks  

But only after the core remains stable.

---

## Final Principle

The Action System is the hands of AION.

Without it, the system can think but cannot act.

With it, cognition becomes execution.