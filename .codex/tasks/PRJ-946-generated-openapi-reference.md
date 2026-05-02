# Task

## Header
- ID: PRJ-946
- Title: Generated OpenAPI Reference
- Task Type: research
- Current Stage: planning
- Status: READY
- Owner: Product Docs Agent
- Depends on: PRJ-945
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 946
- Operation Mode: BUILDER

## Context

The API reference is manually grounded in routes and schemas, but no generated
OpenAPI artifact is checked in or linked.

## Goal

Add a reproducible OpenAPI export and connect it to the API reference and
traceability docs.

## Scope

- discover the FastAPI OpenAPI generation path
- add generated artifact under an approved docs location
- document the regeneration command
- update `docs/api/index.md`, `docs/index.md`,
  `docs/analysis/documentation-drift.md`, and relevant task/context files

## Implementation Plan

1. Inspect app factory/import path for OpenAPI generation.
2. Generate OpenAPI JSON without starting a production service.
3. Add or document the regeneration command.
4. Link the artifact from the API reference.
5. Validate JSON shape and markdown links.

## Acceptance Criteria

- [ ] OpenAPI artifact exists or a blocker is documented.
- [ ] Regeneration command is documented.
- [ ] API reference links to the artifact.
- [ ] Drift report marks the OpenAPI gap fixed or blocked.
- [ ] Validation evidence is recorded.

## Definition of Done

- [ ] `DEFINITION_OF_DONE.md` relevant checks are satisfied for docs scope.
- [ ] No runtime behavior changes.
- [ ] Validation passes.

## Result Report

- Task summary:
- Files changed:
- How tested:
- What is incomplete:
- Next steps:
