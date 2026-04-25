# Task

## Header
- ID: PRJ-658
- Title: Scaffold the `web/` workspace with React, TypeScript, Vite, Tailwind, and daisyUI
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-657
- Priority: P1

## Context
The approved `v2` topology requires a real browser-client workspace instead of
frontend intent living only in planning notes.

## Goal
Create the first buildable `web/` workspace using the approved stack.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `web/` contains a buildable React + TypeScript + Vite workspace.
- [x] Tailwind and daisyUI are wired into the workspace.
- [x] The initial shell renders a product-aware placeholder for auth, chat, and personality inspection.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `npm run build` in `web/`
- Manual checks: installed dependencies and confirmed production build output
- Screenshots/logs:
- High-risk checks: Windows build path uses `npm exec` for `tsc` and `vite` to avoid local PATH drift

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/v2-product-entry-plan.md`, `docs/architecture/13_repository_structure.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: user-approved React + TypeScript + daisyUI baseline
- Follow-up architecture doc updates: reflected in docs index, overview, and v2 plan progress

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
This task intentionally stops at a real product shell, not yet the integrated
login/settings/chat implementation.
