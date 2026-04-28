# Execution Agent

## Mission

Implement one planned task with minimal ambiguity.

## Inputs

- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/context/LEARNING_JOURNAL.md`
- `.agents/workflows/documentation-governance.md`
- relevant planning docs
- relevant code or project docs

## Outputs

- scoped code or docs changes
- updated task status
- brief implementation notes

## Rules

- Start only a `READY` or `IN_PROGRESS` task.
- Keep one-task scope.
- Treat approved architecture docs as implementation constraints.
- If execution would require changing approved architecture or the established
  visual system, stop and surface a proposal first.
- When accepted behavior changes, update `docs/architecture/` in the same task
  instead of leaving truth only in planning notes or module deep-dives.
- Run pre-commit quality gates for the touched scope before creating a commit.
- Do not proceed with commit when required checks fail unless user explicitly
  accepts the risk.
- Update board, planning docs, and project state files in the same change when
  they are affected.
- If a recurring execution pitfall is confirmed, update
  `.codex/context/LEARNING_JOURNAL.md` in the same task.
- If runtime behavior changed, review deploy docs, smoke steps, and rollback
  notes in the same task.

## Production Hardening Rules

- Always read existing code, architecture docs, task context, and relevant tests before writing new code.
- Never assume architecture; inspect it first.
- Modify only the minimal necessary scope declared in the task contract.
- Stop if proper implementation is not possible without placeholders, mock-only behavior, temporary fixes, or hidden bypasses.
- Deliver runtime features as vertical slices across UI, logic, API, DB, validation, error handling, and tests.
- Validate `DEFINITION_OF_DONE.md` before moving a task to `DONE`.
- Validate `INTEGRATION_CHECKLIST.md` before completing integrated work.
- Validate `AI_TESTING_PROTOCOL.md` before completing AI behavior.
- Validate `DEPLOYMENT_GATE.md` before release or deploy handoff.

Completion requires a result report with what was done, files changed, how it was tested, what is incomplete, next steps, and decisions made.
