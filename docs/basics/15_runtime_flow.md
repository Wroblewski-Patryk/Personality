# Runtime Flow

## Purpose

This document defines how AION operates step by step during runtime.

It describes:

- what enters the system  
- what happens next  
- which layer processes what  
- what gets stored  
- what gets returned  
- what is sent to background reflection  

Without this runtime flow, architecture stays theoretical.
With it, architecture becomes implementable.

---

## Core Principle

AION runs as a stateful event-processing system.

Every runtime cycle follows one rule:

event → processing → decision → action → memory → reflection trigger

The system does not generate behavior from nothing.
It always processes an event using current state.

---

## Runtime Modes

AION operates in two runtime modes:

### 1. Foreground Runtime

Handles real-time behavior.

Examples:

- user message  
- API request  
- alert  
- explicit trigger  

This runtime path is synchronous or near-synchronous.

---

### 2. Background Runtime

Handles delayed cognition.

Examples:

- reflection  
- conclusion generation  
- theta update  
- periodic analysis  

This runtime path is asynchronous.

---

## Foreground Runtime – Full Flow

### Step 1. Event Received

System receives input from a source:

- Telegram  
- API  
- scheduler  
- internal trigger  

Raw input must not be processed directly.

It must first be normalized into event format.

---

### Step 2. Event Normalization

Input is converted into canonical event structure.

Example:

{
  "event_id": "uuid",
  "source": "telegram",
  "subsource": "user_message",
  "timestamp": "ISO-8601",
  "payload": {
    "text": "..."
  },
  "meta": {
    "user_id": "uuid",
    "trace_id": "uuid"
  }
}

This is the official entry point into cognition.

---

### Step 3. Runtime State Initialization

System creates initial runtime state.

Initial state should contain at least:

- event  
- identity  
- theta  
- empty context  
- empty retrieved memory  
- empty role  
- empty plan  
- empty result  

This state is passed through the rest of the runtime pipeline.

---

### Step 4. Identity and Core Context Load

Before deeper cognition begins, system loads stable state:

- identity  
- theta  
- user profile  
- active goals  
- active tasks  
- relevant metrics  

This creates the minimal baseline for interpretation.

Current MVP status:

- runtime now builds a lightweight identity snapshot from a stable code-defined core plus user-linked profile, conclusion, and theta signals
- this happens before context construction and is exposed in the runtime result for debugging and verification
- runtime now also loads active goals and active tasks so the conscious loop can connect the current event to ongoing direction and operational blockers

---

### Step 5. Perception

Perception layer determines:

- what kind of event this is  
- what the likely intent is  
- what topic it concerns  
- whether it is ambiguous  
- whether it is likely important  

Output example:

{
  "event_type": "question",
  "topic": "planning",
  "intent": "request_help",
  "ambiguity": 0.2,
  "initial_salience": 0.7
}

Perception does not decide what to do.
It only detects what happened.

---

### Step 6. Memory Retrieval

System retrieves relevant memory.

This should happen in layers:

1. recent temporal memory  
2. semantically related episodes  
3. semantically related conclusions  
4. linked goals and tasks  

Retrieved memory must be filtered and compressed.

Too much memory creates noise.
Too little memory creates statelessness.

---

### Step 7. Context Construction

Context layer combines:

- current event  
- perception output  
- retrieved memory  
- goals  
- tasks  
- theta  
- identity  

Context output should answer:

- what is happening  
- why it matters  
- what it relates to  
- what background matters now  

Output example:

{
  "summary": "User is asking for help organizing the day in an ongoing productivity context.",
  "related_goals": ["goal_1"],
  "related_tags": ["planning", "life"],
  "risk_level": 0.1
}

---

### Step 8. Motivation Evaluation

Motivation layer evaluates:

- importance  
- urgency  
- valence  
- arousal  
- action tendency  
- whether response is needed  

Output example:

{
  "importance": 0.8,
  "urgency": 0.5,
  "valence": 0.1,
  "arousal": 0.6,
  "mode": "respond"
}

This stage determines how strongly the system should care.

---

### Step 9. Role Selection

System chooses which role should be active.

Selection depends on:

- event type  
- context  
- motivation  
- user situation  
- goal relevance  

Example outputs:

- advisor  
- analyst  
- mentor  
- executor  
- friend  

Role affects framing, not truth.

---

### Step 10. Planning

Planning layer decides what should happen next.

It may produce:

- communication plan  
- tool usage plan  
- internal-only action  
- no-op decision  
- escalation recommendation  

Output example:

{
  "goal": "Help user create a usable daily plan",
  "steps": [
    "Identify priorities",
    "Group by effort",
    "Return simple structure"
  ],
  "needs_action": false,
  "needs_response": true
}

Planning proposes.
It does not execute.

---

### Step 11. Action Decision

System decides whether to execute anything externally.

Possible outcomes:

- no external action  
- database update  
- Telegram send  
- internal task creation  
- external API call  
- combined action  

Only Action layer can do this.

If no external effect is needed, Action layer still returns structured result.

---

### Step 12. Action Execution

If needed, system executes side effects.

Examples:

- write record  
- update task  
- call external API  
- send Telegram message  

Output example:

{
  "status": "success",
  "actions": ["send_message"],
  "notes": "Telegram response sent successfully"
}

If action fails, system should return structured failure, not crash silently.

---

### Step 13. Expression

Expression layer formats user-visible output.

It determines:

- wording  
- tone  
- structure  
- final phrasing  
- channel adaptation  

It must respect:

- identity  
- selected role  
- theta  
- motivation  
- context  

Expression converts cognition into communication.

---

### Step 14. Episodic Memory Write

After foreground processing completes, the system stores an episode.

Each episode should include:

- event  
- context summary  
- role used  
- motivation snapshot  
- plan summary  
- action result  
- expression summary  
- importance / salience  

This creates the raw material for future learning.

---

### Step 15. Reflection Trigger

After episode write, system should emit a signal for later reflection.

This does not mean reflection happens immediately.

It means the system marks:

- new memory available  
- new pattern candidate exists  
- future subconscious processing may be needed  

Foreground runtime ends here.

---

## Background Runtime – Full Flow

### Step 1. Reflection Trigger or Schedule

Background runtime starts when:

- scheduler fires  
- enough episodes accumulate  
- explicit reflection is requested  
- periodic cycle begins  

This runtime is not tied to user waiting time.

---

### Step 2. Load Reflection Scope

System selects:

- recent episodes  
- relevant old conclusions  
- recent theta state  
- relation notes  
- relevant goal/task changes  

This defines the scope of reflection.

---

### Step 3. Pattern Analysis

System looks for:

- repetition  
- success patterns  
- failure patterns  
- user preference signals  
- consistency issues  
- useful generalizations  

This is the start of real adaptation.

---

### Step 4. Conclusion Generation

System converts patterns into conclusions.

Possible conclusion types:

- reinforcement  
- refinement  
- warning  
- preference  
- rhythm  
- relation  
- strategy  

Example:

- user responds better to short structured plans  
- mornings are better for proactive planning  
- certain style increases clarity  

---

### Step 5. Conclusion Update

System must decide:

- create new conclusion  
- strengthen existing conclusion  
- weaken old conclusion  
- replace outdated conclusion  

Reflection is not only adding.
It is also maintaining quality.

---

### Step 6. Theta Update

If justified, system updates theta.

This may affect:

- directness  
- warmth  
- reactivity  
- learning rate  
- confidence thresholds  
- reflection depth  

Theta updates must be gradual.

One reflection must not radically rewrite the system.

---

### Step 7. Relation Update

If relevant, background runtime updates relation model.

Examples:

- communication preference shift  
- trust / rapport adjustments  
- preferred style changes  
- recurring emotional context  

This helps improve future interaction quality.

---

### Step 8. Reflection Persistence

System stores:

- updated conclusions  
- theta changes  
- relation notes  
- reflection log  

Now future foreground runs have better internal guidance.

Background runtime ends here.

---

## Runtime State Flow Summary

Foreground:

event  
→ normalize  
→ load identity/theta/goals  
→ perceive  
→ retrieve memory  
→ build context  
→ evaluate motivation  
→ select role  
→ plan  
→ act  
→ express  
→ write episode  
→ emit reflection trigger  

Background:

trigger  
→ load scope  
→ analyze patterns  
→ update conclusions  
→ update theta  
→ update relation state  
→ persist reflection results  

---

## Foreground vs Background Responsibility Split

### Foreground runtime

- speed  
- clarity  
- action  
- communication  
- memory creation  

### Background runtime

- pattern detection  
- adaptation  
- consolidation  
- system refinement  

This separation keeps AION fast and stable.

---

## Failure Handling in Runtime

### Foreground failure rules

If one stage fails:

- return structured fallback  
- log trace  
- do not lose the event  
- still attempt memory write if possible  

User-visible runtime should degrade gracefully.

---

### Background failure rules

If reflection fails:

- do not break foreground system  
- log failure  
- retry later  
- preserve pending reflection markers  

Background cognition must be isolated from real-time usability.

---

## Runtime Logging

Every runtime cycle should log:

- event_id  
- trace_id  
- source  
- selected role  
- motivation mode  
- action status  
- memory write status  
- reflection trigger status  
- duration  

This makes the runtime debuggable.

---

## Runtime Invariants

These rules must always hold:

1. Every input becomes an event before cognition  
2. Every foreground cycle produces structured result  
3. Every completed cycle attempts episode storage  
4. Only Action layer performs side effects  
5. Reflection never blocks user response  
6. Identity remains more stable than theta  
7. Conclusions influence future behavior  

If these break, architecture is drifting.

---

## Minimal MVP Runtime

The smallest acceptable runtime is:

Foreground:
- event normalization  
- context build  
- motivation  
- planning  
- expression  
- memory write  

Background:
- simple reflection  
- conclusion generation  
- small theta updates  

That is enough to prove the system lives across time.

---

## Final Principle

Runtime is where architecture becomes reality.

If the runtime flow is clear:

- implementation is possible  
- debugging is possible  
- scaling is possible  

If runtime flow is unclear, the whole system remains theory.
