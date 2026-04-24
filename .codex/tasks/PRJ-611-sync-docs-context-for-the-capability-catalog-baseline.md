# Task

## Header
- ID: PRJ-611
- Title: Sync docs/context for the capability-catalog baseline
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-610
- Priority: P1

## Context
The capability-catalog contract and proof path are now live in runtime and
release validation. Canonical docs, planning truth, and repository context
must describe the same backend-owned surface and its future UI/admin role.

## Goal
Synchronize runtime reality, testing guidance, ops notes, planning truth, and
repository context around the bounded backend capability-catalog baseline.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] runtime reality describes the capability catalog and its backend-owned
      aggregation boundary.
- [x] testing guidance and ops guidance describe the same validation and
      operator-facing proof surfaces.
- [x] task board, project state, planning docs, and open decisions reflect
      that the queue seeded through `PRJ-611` is complete.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
- Manual checks:
  - docs/context cross-review against runtime and smoke contract
- Screenshots/logs:
  - none
- High-risk checks:
  - keep docs aligned with the bounded aggregation contract rather than
    describing capability catalog as a new system

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - n/a
- Follow-up architecture doc updates:
  - runtime-reality, testing, runbook, planning, and context sync included in
    this task

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
This sync closes the queue seeded through `PRJ-611`. The next slice should
come from fresh analysis rather than synthetic backlog extension.
