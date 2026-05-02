# Task

## Header
- ID: PRJ-949
- Title: Frontend Route And Component Map
- Task Type: research
- Current Stage: planning
- Status: BACKLOG
- Owner: Frontend Builder
- Depends on: PRJ-946, PRJ-948
- Priority: P2
- Coverage Ledger Rows: not applicable
- Iteration: 949
- Operation Mode: BUILDER

## Context

Frontend traceability is coarse because most routes and UI state are currently
owned by `web/src/App.tsx`.

## Goal

Document the current frontend route, state, API, and component ownership map
without forcing a refactor.

## Scope

- `web/src/App.tsx`
- `web/src/lib/api.ts`
- `web/src/index.css`
- `docs/architecture/codebase-map.md`
- possible `docs/frontend/` or approved docs location
- traceability and drift docs

## Implementation Plan

1. Inspect route definitions and route-specific render branches.
2. Map frontend routes to API calls, local state, backend features, and docs.
3. Mark static/fallback-only surfaces as `GAP` where backend ownership is
   missing.
4. Link the map from codebase and traceability docs.
5. Validate route coverage against `web/src/App.tsx`.

## Acceptance Criteria

- [ ] Frontend route/component map exists.
- [ ] Routes map to API calls or explicit static/fallback status.
- [ ] Traceability matrix uses the map for frontend entries.
- [ ] Validation evidence is recorded.

## Definition of Done

- [ ] `DEFINITION_OF_DONE.md` relevant checks are satisfied for docs scope.
- [ ] No UI behavior changes.
- [ ] Validation passes.

## Result Report

- Task summary:
- Files changed:
- How tested:
- What is incomplete:
- Next steps:
