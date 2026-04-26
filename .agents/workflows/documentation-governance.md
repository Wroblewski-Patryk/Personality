# Documentation Governance

Use this workflow whenever work changes repository truth and you must decide
where that truth belongs.

## Rules

- Architecture truth belongs in `docs/architecture/`.
- Runtime or deploy reality belongs in `docs/operations/` or
  `docs/implementation/`.
- Planning queues and future slices belong in `docs/planning/`.
- UX principles, reusable patterns, and visual direction belong in `docs/ux/`.
- Do not leave accepted behavior only in task notes or ephemeral summaries.
- If code changes what future agents must know, update the canonical doc in the
  same task.
