# Task

## Header
- ID: PRJ-640
- Title: Add behavior and release proof for time-aware planned work
- Status: DONE
- Owner: QA/Test
- Depends on: PRJ-639
- Priority: P0

## Context
Core no-UI `v1` cannot claim time-aware planning honestly unless due work,
follow-up delivery, and recurring reevaluation are proven through behavior and
release evidence.

## Goal
Add behavior-validation, health, and release-smoke proof for time-aware planned
work.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Behavior scenarios prove due-item delivery through foreground execution.
- [ ] Health or incident-evidence surfaces expose planned-work posture.
- [ ] Release smoke validates the same planned-work contract.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted pytest, behavior validation, release smoke
- Manual checks: production or local smoke review as appropriate
- Screenshots/logs:
- High-risk checks: do not close core `v1` on repo-only proof if release evidence drifts

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/17_logging_and_debugging.md`, `docs/architecture/29_runtime_behavior_testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: testing, ops, planning/context

## Review Checklist (mandatory)
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This is the acceptance lane for time-aware planned work as a core `v1` capability.

Completed on 2026-04-24.

Result:

- behavior validation now includes `T19.1` for due planned-work foreground
  delivery and `T19.2` for recurring planned-work reevaluation plus bounded
  recurrence advancement
- `/health.v1_readiness` and exported
  `incident_evidence.policy_posture["v1_readiness"]` now expose the same
  compact time-aware planned-work posture
- release-smoke and incident-evidence regressions now fail when that
  planned-work acceptance contract drifts

Validation:

- `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py::test_runtime_behavior_time_aware_planned_work_scenarios`
- `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py::test_health_endpoint_shows_strict_rollout_hint_when_production_is_ready`
- `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "v1_readiness or time_aware_planned_work"`
