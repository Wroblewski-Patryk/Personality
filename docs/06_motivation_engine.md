# Motivation Engine

## Purpose

The motivation engine determines what matters, how much it matters, and what the system should do about it.

Without motivation:

- everything is equally important  
- decisions become random  
- behavior becomes flat  

Motivation gives direction to cognition.

---

## Core Principle

Motivation is not emotion.

Motivation is functional prioritization.

It answers:

- is this important?  
- is this urgent?  
- should I act now?  
- should I ignore it?  
- should I investigate further?  

---

## Base Model

motivation = f(importance, urgency, context, goals, memory)

---

## Key Parameters

- importance  
- urgency  
- valence  
- arousal  
- goal relevance  
- uncertainty  
- risk  

---

## Definitions

### Importance
How much the event matters overall.

### Urgency
How quickly action is required.

### Valence
Positive / negative / neutral nature.

### Arousal
Level of activation or intensity.

### Goal Relevance
Connection to active goals.

### Uncertainty
How unclear the situation is.

### Risk
Potential negative outcome.

---

## RGD Model

A simple functional model:

- Reward → positive outcome  
- Gain → opportunity  
- Danger → threat  

This helps bias behavior.

---

## Motivation Output

Example:

{
  "importance": 0.8,
  "urgency": 0.5,
  "valence": 0.2,
  "arousal": 0.6,
  "mode": "respond"
}

---

## Action Tendencies

Motivation should map to actions:

- act_now  
- respond  
- investigate  
- defer  
- ignore  
- escalate  
- initiate  

---

## Motivation and Behavior

Examples:

High urgency + high risk → direct, fast response  
Low urgency + high uncertainty → exploration  
High reward → encouraging behavior  

---

## Motivation and Memory

Higher motivation → higher memory importance

Important events:

- are stored more strongly  
- are retrieved more often  
- influence future decisions  

---

## Motivation and Theta

Theta modifies how motivation is expressed.

Example:

- high directness → sharper responses  
- high emotional reactivity → stronger reactions  

---

## Computation Strategy

Use hybrid approach:

Deterministic:
- urgency  
- repetition  
- risk  

LLM:
- context interpretation  
- subtle meaning  

---

## Anti-Randomness Rule

Motivation exists to prevent randomness.

System must:

- prioritize  
- choose  
- act intentionally  

---

## Safety Rules

Motivation must not:

- overreact to single event  
- amplify noise  
- destabilize identity  

---

## MVP Requirement

Motivation must decide:

- should respond or not  
- how strong response should be  
- what type of action  

---

## Final Principle

Motivation transforms:

"something happened"

into

"this is what matters and what to do"