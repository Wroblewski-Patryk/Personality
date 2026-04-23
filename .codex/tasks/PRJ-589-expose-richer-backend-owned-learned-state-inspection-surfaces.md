# Task

## Header
- ID: PRJ-589
- Title: Expose richer backend-owned learned-state inspection surfaces
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-588
- Priority: P1

## Context
`PRJ-588` froze the bounded contract for personality-growth introspection. The
repo already exposes `/health.learned_state` and
`GET /internal/state/inspect?user_id=...`, but they still need richer
backend-owned summaries so future UI and operators can inspect growth without
reconstructing it client-side.

## Goal
Widen learned-state inspection surfaces with bounded summaries for learned
knowledge, role/skill metadata, and planning continuity while staying inside
the existing internal debug boundary.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `/health.learned_state` exposes the richer bounded inspection contract
- [x] `GET /internal/state/inspect?user_id=...` exposes backend-owned summary views for growth, role/skill, and planning continuity
- [x] focused API regressions pin the richer learned-state inspection output

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` -> `86 passed`
- Manual checks:
- Screenshots/logs:
- High-risk checks:

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/implementation/runtime-reality.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - `PRJ-591`

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
This slice must stay backend-owned and bounded. It may expose summaries and
section contracts, but it must not imply live tool execution, self-modifying
skills, or a second action path outside planning/action.
