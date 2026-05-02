# Documentation Maintenance Rules

These rules keep documentation as a system map instead of loose notes.

## Required Updates By Change Type

| Change | Required Documentation Update |
| --- | --- |
| New feature | Update `docs/architecture/traceability-matrix.md` with feature, frontend entry, backend route/API, module, model, pipeline, tests, and related docs. |
| New route or endpoint | Update the traceability matrix, `docs/architecture/codebase-map.md`, and the API reference once it exists. |
| New system flow | Update `docs/pipelines/index.md` or add a dedicated pipeline doc and link it from the registry. |
| New module/package | Update `docs/modules/index.md` with responsibility, interface, dependencies, pipelines, routes, models, tests, and gaps. |
| Database model or migration change | Update `docs/architecture/codebase-map.md`, the traceability matrix if feature-facing, and the data/model reference once it exists. |
| New test or validation command | Link the test to the protected feature or pipeline in `docs/architecture/traceability-matrix.md` or the relevant pipeline/module doc. |
| Runtime behavior change | Update canonical architecture if intended design changed; otherwise update `docs/implementation/runtime-reality.md`, affected pipeline/module docs, and operations docs if needed. |
| Deployment, health, smoke, or operator change | Update `docs/operations/runtime-ops-runbook.md`, `docs/architecture/codebase-map.md` if scripts/topology changed, and related task/context files. |
| UX route or visual-system change | Update the relevant `docs/ux/` source, task evidence, and traceability row if API/module behavior changed. |

## Source Of Truth Split

- Canonical design belongs in `docs/architecture/`.
- Live or transitional implementation details belong in `docs/implementation/`,
  `docs/operations/`, and the system-map docs.
- Planning and future work belong in `docs/planning/`.
- Task evidence and current queue truth belong in `.codex/context/` and
  `.codex/tasks/`.

If code and canonical architecture conflict, do not hide the mismatch in a
local note. Record the mismatch, propose options, and wait for a decision.

## Traceability Rules

Every important feature should answer:

- What user or system action triggers it?
- Which frontend entry renders or calls it?
- Which backend route/API receives it?
- Which service/module owns behavior?
- Which database models are read or written?
- Which pipeline describes the flow?
- Which tests protect it?
- Which docs explain it?

Use `GAP` when a part is missing. Use `UNVERIFIED` or `NEEDS CONFIRMATION`
when a claim was not proven from code.

## Pipeline Documentation Rules

Every pipeline must include:

- trigger
- user/system action
- involved frontend files
- involved backend files
- involved services
- data read/write
- failure points
- tests
- related docs

## Module Documentation Rules

Every module entry must include:

- responsibility
- public interface
- dependencies
- used pipelines
- related routes/endpoints
- related database models
- related tests
- known gaps

## Drift Review Checklist

Before closing a meaningful task:

- Does `docs/index.md` still point to the right entrypoints?
- Did a route, module, model, pipeline, script, or test change?
- Did the traceability matrix need a new or changed row?
- Did the module or pipeline registry need a new link?
- Did an operations command or path change?
- Did a docs statement become historical or wrong?
- Are any unverified statements marked clearly?

## Style Rules

- Keep repository documentation in English.
- Prefer repository-relative links.
- Do not include secrets, local `.env` values, tokens, or private production
  values.
- Do not rewrite broad documents just to add one fact. Update the smallest
  source of truth that owns the fact.
- Avoid generic architecture prose. Use real paths, real route names, real
  models, real scripts, and real tests.
