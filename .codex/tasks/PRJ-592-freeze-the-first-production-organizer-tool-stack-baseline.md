# Task

## Header
- ID: PRJ-592
- Title: Freeze the first production organizer-tool stack baseline
- Status: DONE
- Owner: Planner
- Depends on: PRJ-591
- Priority: P2

## Context
The repo already has bounded live ClickUp, Google Calendar, and Google Drive
paths, but production readiness is still fragmented across per-provider
surfaces. Before adding one acceptance snapshot, the project needs one explicit
definition of which slices count as the first real organizer-tool stack for the
no-UI assistant and work-partner role.

## Goal
Freeze one bounded production organizer-tool baseline covering ClickUp,
Calendar, and Drive together with explicit opt-in, confirmation, and bounded
read constraints.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] one explicit organizer-tool baseline is defined for production
- [x] the baseline names approved ClickUp, Calendar, and Drive slices
- [x] opt-in and confirmation boundaries stay explicit for the frozen stack

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - architecture/product/connector cross-review
- Manual checks:
  - cross-review of connector policy, connector execution baseline, and work-partner role boundary
- Screenshots/logs:
- High-risk checks:
  - baseline must not imply broader mutations than the already approved action-owned slices

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/10_future_vision.md`
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
The frozen stack is bounded to:
- ClickUp `create_task`, `list_tasks`, `update_task`
- Google Calendar `read_availability`
- Google Drive `list_files`

It stays behind the existing planning/action boundary, preserves user opt-in
requirements, and keeps mutation confirmation semantics for ClickUp writes.
