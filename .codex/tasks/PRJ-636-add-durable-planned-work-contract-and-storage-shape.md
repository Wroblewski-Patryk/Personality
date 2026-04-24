# Task

## Header
- ID: PRJ-636
- Title: Add the durable planned-work contract and storage shape
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-635
- Priority: P0

## Context
Core no-UI `v1` now requires time-aware planned future work. The runtime needs
one explicit durable model for future work items before scheduler reevaluation
or user-visible delivery can stay architecture-aligned.

## Goal
Add the planned-work contract and durable storage shape without creating a
parallel reminder subsystem.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] A durable planned-work entity exists in the runtime contract and storage model.
- [x] Planning can express create, reschedule, cancel, and complete intents for planned work.
- [x] The new model remains explicitly internal-first and action-owned for durable writes.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_schema_baseline.py`
- Manual checks: verified that reminder-like phrasing now writes one canonical planned-work record plus existing task anchors without creating a separate reminder delivery path
- Screenshots/logs:
- High-risk checks: durable writes stay inside `ActionExecutor` and background/runtime consumers only read or refresh planned-work state

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/12_data_model.md`, `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: runtime reality, testing, ops notes

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
This task should extend existing goal/task/proactive ownership rather than fork it.
Implemented through the existing planning -> action -> memory path:
- typed planned-work contracts and runtime result state
- durable `aion_planned_work_item` storage plus Alembic migration
- planner support for create, reschedule, cancel, and complete intents
- action-owned persistence and runtime/test coverage
