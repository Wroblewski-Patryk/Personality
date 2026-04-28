---
description: Workspace rules for this project
---

# General Workspace Rules

## Stack Snapshot
- Backend: FastAPI, Python, PostgreSQL, background workers
- Frontend: React, TypeScript, browser product shell
- Mobile: reserved surface
- Database: PostgreSQL
- Hosting target: Coolify / container runtime
- Deployment shape: backend-owned runtime with served web shell
- Runtime constraints:
  - architecture-first stage ownership
  - backend truth for app-facing contracts
  - user trust and continuity across channels

## Architecture Rules
- Keep project-specific conventions explicit.
- Document where state lives and why.
- Treat `docs/architecture/` as the approved implementation contract.
- If a better design requires changing architecture, propose it before
  changing code direction or docs.
- Prefer existing patterns over introducing a new style per feature.
- Keep cross-module contracts explicit when shared code or shared schemas exist.
- Do not remove potentially shared code without checking remaining consumers.

## Repository And Docs Rules
- Keep root minimal and intentional.
- Put project documentation under `docs/`.
- Update planning, architecture, or operations docs when behavior or structure changes.
- Treat docs parity as a real done-state requirement when routes, modules, IA,
  or runtime ownership change.
- Use `.agents/workflows/documentation-governance.md` when deciding where new
  truth should live.
- Keep links repository-relative and avoid sibling-repository references.

## UI/UX Rules
- Define approved component style and motion approach.
- Treat the visual system as a reuse-first contract.
- Reuse an existing shared component or approved variant before creating a new
  visual pattern.
- If a new visual pattern is necessary, make it reusable and document it.
- Use `docs/ux/visual-direction-brief.md` when setting or changing visual
  direction.
- Use `docs/ux/experience-quality-bar.md` for substantial UI review.
- Record reusable UI decisions and proven patterns in `docs/ux/design-memory.md`.
- Use `docs/ux/screen-quality-checklist.md` before calling a screen polished.
- Avoid recurring traps in `docs/ux/anti-patterns.md`.
- If design tools are used, record source-of-truth links.
- For UX-heavy work, require states, responsive checks, accessibility checks,
  and parity evidence.
- When a canonical screenshot or mockup exists, require a visual gap audit,
  asset strategy, and screenshot comparison pass.
- Do not replace decorative image assets with gradient approximations when the
  approved design depends on textured or illustrated backgrounds.
- Figma is the primary implementation source when available.
- Stitch is draft-only unless the repository explicitly approves another rule.

## Deployment Rules
- Treat Coolify as the default deployment target unless the project declares
  otherwise.
- Keep env ownership, health checks, persistent data, and worker processes
  explicit.
- When runtime behavior changes, review deploy docs, smoke checks, and rollback
  notes in the same task.
- Record the real deployment artifacts and paths in
  `.codex/context/PROJECT_STATE.md`.

## Delivery Rules
- Keep changes scoped and reversible.
- Require acceptance evidence before completion.
- Keep planning docs and task board synchronized.
- Declare the current delivery stage in each task and keep output aligned to
  that stage only.
- Do not skip from analysis or planning straight to implementation unless
  explicitly requested.
- Follow the default loop:
  `plan -> implement -> test -> architecture review -> sync context -> repeat`.
- Apply the validation commands from `.codex/context/PROJECT_STATE.md` before
  every commit.
- Use subagents only according to `.agents/workflows/subagent-orchestration.md`.

## Production Hardening Delivery Rules

- Use `.codex/templates/task-template.md` for every task and include Goal, Scope, Implementation Plan, Acceptance Criteria, Definition of Done, and Result Report.
- Check `DEFINITION_OF_DONE.md` before any task moves to `DONE`.
- Check `INTEGRATION_CHECKLIST.md` before integrated runtime work is accepted.
- Check `NO_TEMPORARY_SOLUTIONS.md` whenever a blocker appears.
- Check `AI_TESTING_PROTOCOL.md` for AI features.
- Check `DEPLOYMENT_GATE.md` before release or deploy handoff.
- Implement features as vertical slices across UI, logic, API, DB, validation, error handling, and tests.
- Do not mark partial runtime work as done.
- Stop and report when the proper solution is blocked.
