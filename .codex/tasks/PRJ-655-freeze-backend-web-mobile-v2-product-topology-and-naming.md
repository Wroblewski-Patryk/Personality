# Task

## Header
- ID: PRJ-655
- Title: Freeze the `backend/web/mobile` v2 product topology and naming
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-646
- Priority: P1

## Context
The user approved the post-no-UI `v2` direction as one product-shaped
repository with `backend/`, `web/`, and `mobile/` top-level folders. Current
repo truth still described the older single-runtime root topology, so the
approved structure and execution plan had to be frozen before filesystem
migration could begin safely.

## Goal
Record one explicit approved `v2` repository topology, product-surface naming,
and execution order for the migration and first-party client work.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Repo truth explicitly records `backend/`, `web/`, and `mobile/` as the approved target topology.
- [x] Governance and architecture notes acknowledge the migration target without pretending filesystem reality already changed.
- [x] The execution queue is seeded with bounded `PRJ-655..PRJ-668` slices for topology, auth, web, deploy, and mobile.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: architecture, governance, and planning cross-review
- Manual checks: compared `docs/planning/v2-product-entry-plan.md`, `docs/planning/next-iteration-plan.md`, `docs/planning/open-decisions.md`, `docs/governance/repository-structure-policy.md`, `docs/architecture/13_repository_structure.md`, `.codex/context/PROJECT_STATE.md`, and `.codex/context/TASK_BOARD.md`
- Screenshots/logs:
- High-risk checks: target topology is recorded as approved truth, while transition notes still mark root-level runtime layout as current filesystem reality until migration lands

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/13_repository_structure.md`, `docs/architecture/architecture-source-of-truth.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: no
- Approval reference if architecture changed: user approval on 2026-04-25 for `backend/web/mobile`, backend-owned auth, and first-party client direction
- Follow-up architecture doc updates: completed for planning and repository-topology truth; filesystem migration remains follow-up work in `PRJ-656..PRJ-668`

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This task freezes the approved product topology and queue only. It does not
move files yet.
