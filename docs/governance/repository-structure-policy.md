# Repository Structure Policy

## Goal

Keep the repository predictable, easy to scan, and friendly for human and AI contributors.

## Root Rules

- Keep the root focused on runtime, packaging, deployment, and repo entry files.
- Approved `v2` target topology uses product-facing root folders:
  - `backend/`
  - `web/`
  - `mobile/`
- Current transition note:
  - until the approved `v2` migration lands, the existing Python runtime still
    lives in the repository root
  - the target topology is now approved repo truth, but migration work is
    still required before filesystem reality fully matches it
- Allowed in root for the target topology:
  - `README.md`
  - `AGENTS.md`
  - `docker-compose*.yml`
  - `.env.example`
  - `backend/`
  - `web/`
  - `mobile/`
  - `docker/`
  - `docs/`
- Do not add random project documentation directly in the root unless the file is true repo metadata.

## Documentation Rules

- Keep long-form project documentation under `docs/`.
- Preserve the existing numbered files under `docs/basics/` because they already act as the original narrative map for AION.
- Put newer operational and governance docs in category folders such as:
  - `docs/assumptions/`
  - `docs/governance/`
  - `docs/engineering/`
  - `docs/planning/`
  - `docs/operations/`
- When a Codex run discovers a repo fact that should not yet overwrite the canonical story, record it in `docs/assumptions/` first.

## Code Layout Rules

- `backend/app/api/` is for HTTP entry points and request translation only.
- `backend/app/core/` owns contracts, runtime orchestration, configuration, and shared infrastructure glue.
- `backend/app/agents/`, `backend/app/motivation/`, and `backend/app/expression/` contain stage logic.
- `backend/app/integrations/` contains external system clients.
- `backend/app/memory/` contains persistence models and repository logic.
- `backend/tests/` should mirror behavior-focused coverage, not internal implementation trivia.
- `backend/scripts/` should contain repeatable operator and developer helpers only.
- `web/` is the dedicated browser-client workspace.
- `mobile/` is the dedicated mobile-client workspace.

## Migration Rule

When adding new docs:

1. Prefer an existing `docs/` subfolder.
2. If the content is current-state and still fluid, place it in `docs/assumptions/`.
3. Update `docs/README.md` so the new file is discoverable.

## Cross-Repo Boundary

- Do not reference sibling repository files as if they were part of this codebase.
- Template ideas may inform this repo, but the canonical paths in docs must always resolve inside `Personality`.
