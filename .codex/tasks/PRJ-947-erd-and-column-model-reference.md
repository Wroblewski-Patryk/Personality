# Task

## Header
- ID: PRJ-947
- Title: ERD And Column Model Reference
- Task Type: research
- Current Stage: planning
- Status: BACKLOG
- Owner: Product Docs Agent
- Depends on: PRJ-946
- Priority: P1
- Coverage Ledger Rows: not applicable
- Iteration: 947
- Operation Mode: BUILDER

## Context

The data reference maps ORM models, tables, migrations, and repository groups,
but it does not include an ERD or column-by-column model reference.

## Goal

Create a reproducible data-model reference that maps tables, columns,
relationships, migrations, owners, tests, and known gaps.

## Scope

- `backend/app/memory/models.py`
- `backend/migrations/versions/`
- `docs/data/index.md`
- possible generated docs under `docs/data/`
- traceability and drift docs

## Implementation Plan

1. Inspect SQLAlchemy model metadata and Alembic migration history.
2. Generate or manually produce an ERD-friendly model artifact.
3. Add a column-level reference for core tables.
4. Link models to migrations, repository methods, features, and tests.
5. Validate coverage against ORM model/table names.

## Acceptance Criteria

- [ ] ERD artifact or text ERD exists.
- [ ] Column-level reference covers all current ORM models or marks gaps.
- [ ] Data reference links generated evidence.
- [ ] Drift report is updated.
- [ ] Validation evidence is recorded.

## Definition of Done

- [ ] `DEFINITION_OF_DONE.md` relevant checks are satisfied for docs scope.
- [ ] No DB schema changes are made.
- [ ] Validation passes.

## Result Report

- Task summary:
- Files changed:
- How tested:
- What is incomplete:
- Next steps:
