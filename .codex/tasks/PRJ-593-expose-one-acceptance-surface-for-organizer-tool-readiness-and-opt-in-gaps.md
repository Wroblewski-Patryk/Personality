# Task

## Header
- ID: PRJ-593
- Title: Expose one acceptance surface for organizer-tool readiness and opt-in gaps
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-592
- Priority: P2

## Context
`PRJ-592` froze the first production organizer-tool stack, but production
readiness was still fragmented across per-provider entries. Operators need one
bounded surface that summarizes ClickUp, Google Calendar, and Google Drive
readiness together with the explicit opt-in and confirmation boundaries.

## Goal
Expose one shared organizer-tool acceptance surface in `/health.connectors`
that summarizes readiness, credential gaps, opt-in requirements, and
confirmation boundaries for the frozen production stack.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `/health.connectors` exposes one shared organizer-tool readiness surface
- [x] the surface summarizes approved operations, readiness gaps, and opt-in boundaries
- [x] focused API regressions pin both partial and fully ready organizer-tool stack states

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` -> `87 passed`
- Manual checks:
- Screenshots/logs:
- High-risk checks:
  - acceptance surface must stay bounded to already approved ClickUp, Calendar, and Drive slices

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/planning/next-iteration-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - `PRJ-595`

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
The organizer-tool readiness surface is intentionally operator-facing. It
describes which approved stack operations are ready, which still have provider
credential gaps, and which operations remain opt-in or confirmation gated.
