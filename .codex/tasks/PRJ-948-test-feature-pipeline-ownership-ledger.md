# Task

## Header
- ID: PRJ-948
- Title: Test Feature Pipeline Ownership Ledger
- Task Type: research
- Current Stage: planning
- Status: BACKLOG
- Owner: QA/Test
- Depends on: PRJ-946, PRJ-947
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 948
- Operation Mode: ARCHITECT

## Context

Traceability currently maps tests by file responsibility and inspected names.
Tests do not carry stable feature or pipeline IDs.

## Goal

Create a test ownership ledger or accepted inline metadata convention so
feature and pipeline coverage can be verified mechanically.

## Scope

- `backend/tests/`
- `docs/architecture/traceability-matrix.md`
- possible `docs/engineering/test-ownership-ledger.md`
- `docs/engineering/testing.md`
- drift report and context files

## Implementation Plan

1. Inspect test naming, markers, and existing pytest configuration.
2. Choose the smallest non-invasive ownership format.
3. Add a ledger mapping test files or cases to feature/pipeline IDs.
4. Update traceability docs to point to the ledger.
5. Validate that all traceability tests have an ownership entry or explicit gap.

## Acceptance Criteria

- [ ] Test ownership ledger or metadata convention exists.
- [ ] Core traceability rows link to test ownership IDs.
- [ ] Unmapped tests are listed as gaps.
- [ ] Validation evidence is recorded.

## Definition of Done

- [ ] `DEFINITION_OF_DONE.md` relevant checks are satisfied.
- [ ] Test behavior is unchanged unless deliberately adding metadata.
- [ ] Validation passes.

## Result Report

- Task summary:
- Files changed:
- How tested:
- What is incomplete:
- Next steps:
