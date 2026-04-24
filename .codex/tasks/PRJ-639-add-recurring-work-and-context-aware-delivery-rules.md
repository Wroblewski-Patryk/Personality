# Task

## Header
- ID: PRJ-639
- Title: Add recurring work and context-aware delivery rules
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-638
- Priority: P1

## Context
The planned-work model should support routines and recurring follow-ups without
becoming a second scheduler or a simplistic reminder engine.

## Goal
Add recurring planned-work semantics plus context-aware delivery rules such as
quiet hours, not-before windows, and skip-versus-delay posture.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Recurring planned work is represented as bounded data plus reevaluation rules.
- [x] Delivery can be delayed, skipped, or handed off based on context and policy.
- [x] The system remains explainable through explicit state and policy surfaces.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted scheduler/planning/runtime coverage
- Manual checks: verify recurring work does not create a parallel scheduler
- Screenshots/logs:
- High-risk checks: avoid hidden autonomous delivery loops

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`, `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: runtime reality and runbook

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
The goal is time-aware reasoning, not a generic calendar product.

## Result

- planner now captures recurring planned work as bounded internal data
  (`daily`, `weekly`, and explicit `interval_days:N` custom cadence) instead
  of forcing recurring requests into one-off reminder wording
- scheduler reevaluation now applies explicit delay-versus-skip posture:
  quiet-hours-sensitive items snooze to the next morning, expired one-off
  items are skipped out of the active queue, and recurring items advance to
  their next occurrence instead of spawning a parallel scheduler
- recurring state remains explainable through existing planned-work fields and
  maintenance summary counters rather than hidden background behavior

## Validation Evidence

- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_planning_agent.py tests/test_scheduler_worker.py tests/test_memory_repository.py`
- Manual checks:
  - reviewed scheduler maintenance flow to confirm recurring progression and
    quiet-hours delay stay inside planned-work state transitions
- High-risk checks:
  - recurring advancement reuses the same durable planned-work row instead of
    creating a second scheduler-owned reminder lane
