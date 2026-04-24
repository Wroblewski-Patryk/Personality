# Task

## Header
- ID: PRJ-609
- Title: Expose one backend capability catalog for future UI/admin callers
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-608
- Priority: P1

## Context
The canonical architecture now freezes a bounded backend capability-catalog
contract. The runtime already exposes the component truth across
`/health.api_readiness`, `/health.learned_state`, `/health.role_skill`,
`/health.connectors`, and internal inspection. The next slice must expose one
aggregated catalog without creating a second execution or authorization
system.

## Goal
Expose one bounded backend capability catalog through approved backend surfaces
so future UI/admin callers can inspect role posture, metadata-only skills,
tool readiness, and learned-state linkage without reconstructing that truth
client-side.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `/health` exposes one bounded `capability_catalog` payload composed from
      existing backend truth.
- [x] `GET /internal/state/inspect?user_id=...` exposes the same bounded
      capability catalog together with selection visibility for future UI/admin
      callers.
- [x] targeted API regression coverage pins the new capability-catalog
      contract.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
- Manual checks:
  - none
- Screenshots/logs:
  - none
- High-risk checks:
  - preserve the existing action and authorization boundaries while only
    aggregating backend truth

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - n/a
- Follow-up architecture doc updates:
  - none in this slice; sync deferred to `PRJ-611`

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
The implementation uses one new helper module
`app/core/capability_catalog.py` only as an aggregation owner over already
approved source surfaces. It does not add a new execution system.
