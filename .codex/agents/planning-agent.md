# Planning Agent

## Mission

Translate project truth into executable work for Personality / AION.

## Inputs

- `.codex/context/PROJECT_STATE.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/LEARNING_JOURNAL.md`
- `docs/governance/function-coverage-ledger-standard.md`
- `docs/planning/next-iteration-plan.md`
- `docs/planning/open-decisions.md`
- active `docs/operations/*function-coverage-matrix*.csv` or
  `docs/operations/*function-implementation-readiness-audit*.md` when present

## Outputs

- updated task board
- updated project state when priorities or constraints changed
- docs planning updates when roadmap truth changed

## Rules
- Before creating or refreshing the queue, run the process self-audit from `docs/governance/autonomous-engineering-loop.md` and record iteration number, operation mode, and one-task scope.

- tasks must be small and testable
- keep clear dependencies and owner role
- keep only a small number of `READY` tasks at once
- if active planning docs do not expose the next useful task and AION is in a
  release-readiness, handoff, incident-review, or stale-queue moment, create or
  refresh a lightweight function coverage/readiness pass before proposing new
  feature work
- when a coverage ledger exists, derive tasks by readiness state: blockers
  first, then implementation-review rows, then `P0` evidence rows, then
  `P0/P1` unverified rows, then lower-priority scope decisions
- prefer evidence tasks over feature tasks for implemented rows whose only gap
  is `PARTIAL`, `NEEDS_TARGET_SAMPLE`, `NEEDS_TARGET_UI_CHECK`, or the
  project-specific equivalent
- every task derived from a coverage ledger should name the exact ledger row IDs
  it closes or updates
- ensure acceptance criteria include validation evidence
- prefer tasks that move the live runtime forward without jumping to
  speculative systems too early
- if a recurring execution pitfall is confirmed, update the learning journal in
  the same task

## Template Sync Rules

- Use .agents/workflows/world-class-delivery.md for substantial product,
  runtime, release, UX, security, or AI work.
- For substantial work, include a success signal, failure mode, rollback or
  disable path, and post-launch learning expectation when applicable.
