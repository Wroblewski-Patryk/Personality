# Definition Of Done

A task is `DONE` only when every applicable item below is validated with
evidence. If any required item is missing, the task is not done and must remain
`IN_PROGRESS`, `REVIEW`, or `BLOCKED`.

## Mandatory Completion Rules

- [ ] Code builds without errors.
- [ ] The feature works manually through the real UI, API, CLI, or operator
  surface affected by the task.
- [ ] No mock data, placeholder data, fake service, demo-only branch, or
  temporary bypass remains in the delivered path.
- [ ] Full data flow works end-to-end across every relevant layer:
  frontend, backend, database, workers, external services, and validation.
- [ ] Backend errors are handled deliberately and return safe, useful responses.
- [ ] UI or client errors show clear loading, empty, validation, and failure
  states where applicable.
- [ ] No existing functionality or documented behavior is broken.
- [ ] The feature still works after restart, reload, navigation away and back,
  or process restart when persistence or runtime state is involved.
- [ ] Changes are documented in the relevant source of truth.
- [ ] Behavior is reproducible by another agent or developer using the recorded
  validation steps.

## Evidence Required

Every completed task must include:

- automated commands run and their pass/fail result
- manual verification steps run and their pass/fail result
- files changed
- documentation updated or a clear reason no documentation changed
- known residual risks

## Blocking Rule

Tasks that do not meet all required conditions are `NOT DONE`. Do not mark them
complete, merge them, deploy them, or hand them off as finished.
