# Documentation System Gap Repair Plan

Last updated: 2026-05-03

## Purpose

This plan turns the remaining documentation system-map gaps into a bounded
execution queue. The goal is to make the documentation mechanically
verifiable where practical, while keeping every slice small enough to review
and revert.

## Current Gaps

The current documentation system map is useful, but five gaps remain visible:

1. No generated OpenAPI artifact is checked in or referenced.
2. No ERD or column-by-column data/model reference exists.
3. Tests do not carry stable feature or pipeline ownership IDs.
4. Frontend traceability is coarse because much of the app shell is still in
   `web/src/App.tsx`.
5. Provider-specific integration docs are incomplete.

## Repair Queue

| Order | Task | Status | Outcome |
| --- | --- | --- | --- |
| 1 | `PRJ-946` Generated OpenAPI Reference | READY | A reproducible OpenAPI export and docs link route schemas to the API reference. |
| 2 | `PRJ-947` ERD And Column Model Reference | BACKLOG | Data docs include generated ERD evidence and model/table/column ownership. |
| 3 | `PRJ-948` Test Feature Pipeline Ownership Ledger | BACKLOG | Tests map to stable feature and pipeline IDs that traceability can verify. |
| 4 | `PRJ-949` Frontend Route And Component Map | BACKLOG | Web shell routes, state owners, API calls, and component boundaries are mapped below `App.tsx`. |
| 5 | `PRJ-950` Provider Specific Integration Docs | BACKLOG | ClickUp, Google Calendar, Google Drive, Telegram, web knowledge, and browser integration docs list readiness, config, operations, tests, and gaps. |

## Execution Notes

- `PRJ-946` should run first because the API artifact can later support
  frontend and provider documentation checks.
- `PRJ-947` should follow because data ownership is the second-largest
  machine-checkable surface.
- `PRJ-948` should not rewrite tests broadly. Start with a test ownership
  ledger, then only add inline IDs if the repo accepts that convention.
- `PRJ-949` should document the current monolithic frontend honestly before
  proposing any component extraction.
- `PRJ-950` must separate provider credential readiness from policy capability
  and must not record secrets.

## Acceptance Criteria For The Queue

- Each task updates the central docs index, traceability matrix, and drift
  report when it closes a gap.
- Each task records validation evidence in its task contract.
- Generated artifacts must include the command or script used to reproduce
  them.
- Unverified provider behavior must be marked `UNVERIFIED` or `GAP`.
- Runtime behavior must not change unless a later task explicitly requests and
  verifies an implementation slice.

## Rollback

Each task is documentation or generated-artifact oriented. Rollback is a normal
git revert of the relevant task files and docs updates.
