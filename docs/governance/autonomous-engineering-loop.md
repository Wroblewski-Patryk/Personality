# Autonomous Engineering Loop

This document is the canonical operating loop for autonomous engineering agents
in this repository. It extends the existing task, documentation, review, and
delivery standards without replacing them.

## Purpose

Agents must continuously move the project toward production-ready,
premium-quality software. The goal is measurable project improvement through
small, verified, documented iterations.

## Process Self-Audit

Before every iteration, the active agent must verify:

- Am I executing all seven loop steps?
- Am I skipping any step?
- Is my process aligned with this repository's source-of-truth documents?
- Is exactly one priority task selected for this iteration?
- Is the current operation mode correct for this iteration number?

If any answer fails, the agent must fix the process before continuing. Process
correction means updating the plan, task contract, scope, validation approach,
or documentation target before making implementation changes.

## Seven-Step Loop

Every iteration must complete all seven steps:

1. Analyze Current State
2. Select One Priority Task
3. Plan Implementation
4. Execute Implementation
5. Verify and Test
6. Self-Review
7. Update Documentation and Knowledge

Do not merge steps together in task evidence. Small tasks may have concise
evidence, but every step must be represented.

## Step Requirements

### 1. Analyze Current State

Read the repository, relevant documentation, architecture docs, current planning
files, and affected implementation surfaces.

Required output:

- issues found
- gaps found
- inconsistencies found
- current architecture constraints

### 2. Select One Priority Task

Choose exactly one task for the iteration.

Priority order:

1. blockers that prevent progress
2. architecture issues
3. core features
4. improvements or refactors
5. UI polish or low-priority work

If multiple tasks qualify, choose the highest-impact task that can be completed
as a small, reversible slice.

### 3. Plan Implementation

Define:

- what will change
- exact files or surfaces to modify
- implementation logic
- validation path
- edge cases and failure modes
- documentation updates required

If the plan conflicts with approved architecture or user instructions, stop and
request a decision instead of implementing.

### 4. Execute Implementation

Implement only the selected task. Reuse existing systems and approved patterns.
Avoid unnecessary abstractions, duplicate logic, placeholder behavior, temporary
bypasses, and unrelated cleanup.

### 5. Verify and Test

Validate whether the change works, whether anything broke, and whether the
result is consistent with the documented system.

Use the strongest relevant evidence available:

- automated tests
- lint or typecheck
- manual smoke check
- logical validation for docs-only changes
- targeted simulation for edge cases

Record commands run and any checks that could not run.

### 6. Self-Review

Critically evaluate:

- Is this the cleanest solution for the current architecture?
- Is there a simpler approach?
- Did the change introduce technical debt?
- Is the result scalable enough for the declared scope?
- Are docs, task evidence, and project state aligned?

If a refinement is required, complete it before closing the iteration.

### 7. Update Documentation and Knowledge

Update the relevant source-of-truth files:

- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/context/LEARNING_JOURNAL.md` when a recurring pitfall is confirmed
- `docs/planning/*`
- architecture, operations, security, UX, or governance docs when those truths
  changed

Future agents must be able to continue from the updated repository without
needing hidden chat context.

## Operation Modes

Agents rotate operation modes by iteration number:

- `BUILDER`: default mode for implementation and feature delivery.
- `ARCHITECT`: every third iteration. Focus on structure, consistency,
  architecture drift, duplication, and refactor opportunities.
- `TESTER`: every fifth iteration. Focus on breaking assumptions, edge cases,
  robustness, and validation depth.

Mode selection:

- If the iteration number is divisible by 5, use `TESTER`.
- Else if the iteration number is divisible by 3, use `ARCHITECT`.
- Else use `BUILDER`.

When a mode reveals higher-priority work than the originally expected task, use
the priority order above and update the task plan before execution.

## Iteration Evidence

Every task contract must record:

- iteration number
- operation mode
- self-audit result
- selected priority task
- seven-step loop evidence
- validation evidence
- self-review outcome
- documentation and knowledge updates

Concise evidence is acceptable for docs-only tasks, but missing evidence blocks
`DONE`.

## Relationship To Existing Standards

This loop works together with:

- `AGENTS.md`
- `.agents/workflows/general.md`
- `.agents/workflows/documentation-governance.md`
- `.agents/workflows/world-class-delivery.md`
- `.codex/templates/task-template.md`
- `DEFINITION_OF_DONE.md`
- `INTEGRATION_CHECKLIST.md`
- `NO_TEMPORARY_SOLUTIONS.md`
- `AI_TESTING_PROTOCOL.md`
- `DEPLOYMENT_GATE.md`

If the loop and a risk-specific standard both apply, follow both. For example,
an AI feature still needs AI testing evidence, and a deployable runtime change
still needs deployment and rollback evidence.

## Final Rule

If the agent is unsure what to do next, return to Analyze Current State. Do not
guess, invent work randomly, or skip the task-selection step.
