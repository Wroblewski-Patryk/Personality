# Task

## Header
- ID: PRJ-818
- Title: Rebuild public home into a full-bleed hero shell
- Task Type: design
- Current Stage: verification
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-800L
- Priority: P1

## Context
The user added a new explicit interpretation to the canonical `home` screen:
the public shell should not read as a nested panel. `header`, `hero`, and
`footer` should each span full width, while their inner content remains
constrained by the same max-width rhythm. The hero artwork should stretch from
left to right and top to bottom, with navigation visually floating above it.

## Goal
Turn the public `home` surface into a full-bleed scenic shell with a
canonical-feeling hero background, overlaid navigation, and cleaner `bridge`
and `trust band` framing on wide screens.

## Success Signal
- User or operator problem:
  - `home` still feels like a panel inside a panel instead of one continuous
    scenic flagship entry
- Expected product or reliability outcome:
  - `home` reads as a full-width public landing where the hero art owns the
    stage and supporting sections align under the same shell rhythm
- How success will be observed:
  - the rendered structure clearly shows `header` overlaying the hero
    background and the internal content staying max-width constrained
- Post-launch learning needed: no

## Deliverable For This Stage
One bounded implementation slice that rebuilds the public shell structure and
retunes the `hero`, `feature bridge`, and `trust band` to match the merged
canonical spec plus the user's notes.

## Scope
- `web/src/App.tsx`
- `web/src/index.css`
- `docs/ux/design-memory.md`
- `.codex/tasks/PRJ-818-home-full-bleed-hero-shell-pass.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`

## Implementation Plan
1. Move the public shell from a nested `window` layout toward full-width
   `header/main/footer` sections with full-bleed backgrounds and constrained
   inner content rhythm.
2. Place the navigation above the scenic hero background and give the hero a
   true full-bleed `100vh` stage on desktop.
3. Retune the `feature bridge` and `trust band` so they sit as calmer
   follow-up sections instead of interior cards.
4. Validate with frontend build and focused diff checks, then sync the new
   shell pattern in design memory and project context.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- stay within the declared current stage unless explicit approval changes it

## Acceptance Criteria
- `home` no longer renders as a nested public window panel
- navigation overlays the hero background on wide screens
- hero artwork fills the public stage more like the canonical reference
- `feature bridge` and `trust band` follow the new shell rhythm
- build and diff checks pass

## Definition of Done
- [x] The public shell structure is rebuilt.
- [x] Validation evidence is attached.
- [x] Task and repository truth are updated.

## Stage Exit Criteria
- [x] The output matches the declared `Current Stage`.
- [x] Work from later stages was not mixed in without explicit approval.
- [x] Risks and assumptions for this stage are stated clearly.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval
- implicit stage skipping

## Validation Evidence
- Tests:
  - `Push-Location .\web; npm exec tsc -b; Pop-Location`
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/ux/design-memory.md .codex/tasks/PRJ-818-home-full-bleed-hero-shell-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- Manual checks:
  - confirmed the public branch now uses full-width `header`, `hero`, and
    `footer` shells with constrained inner content rhythm instead of a single
    nested panel
- Screenshots/logs:
  - frontend TypeScript build and production bundle completed successfully
- High-risk checks:
  - kept the auth modal contract and the existing landing artwork system intact

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/27_codex_instructions.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - not applicable

## UX/UI Evidence (required for UX tasks)
- Design source type: approved_snapshot
- Design source reference:
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- Canonical visual target:
  - public `home` full-bleed flagship shell
- Fidelity target: pixel_close
- Stitch used: no
- Experience-quality bar reviewed: yes
- Visual-direction brief reviewed: yes
- Existing shared pattern reused:
  - landing scenic artwork
  - auth modal entry flow
- New shared pattern introduced: yes
- Design-memory entry reused:
  - landing-specific scenic hero artwork
- Design-memory update required: yes
- Visual gap audit completed: yes
- Background or decorative asset strategy:
  - keep image-based scenic hero treatment; do not degrade into gradient-only
    approximation
- Canonical asset extraction required: no
- Screenshot comparison pass completed: no
- Remaining mismatches:
  - deploy-side crop and note-card polish should still be checked on the live
    render
- State checks: success
- Feedback locality checked: yes
- Raw technical errors hidden from end users: yes
- Responsive checks: desktop | tablet | mobile
- Input-mode checks: pointer | touch
- Accessibility checks:
  - preserved existing navigation links, CTA buttons, and auth modal semantics
- Parity evidence:
  - merged canonical spec plus explicit user notes about full-width sections

## Deployment / Ops Evidence (required for runtime or infra tasks)
- Deploy impact: low
- Env or secret changes: none
- Health-check impact: none
- Smoke steps updated: not applicable
- Rollback note:
  - revert the route-only public shell pass if layout framing regresses
- Observability or alerting impact: none
- Staged rollout or feature flag: none

## Review Checklist (mandatory)
- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
- This slice intentionally focused only on `home` shell framing and did not
  reopen dashboard/chat/personality polish in parallel.

## Production-Grade Required Contract

Every task must include these mandatory sections before it can move to `READY`
or `IN_PROGRESS`:

- `Goal`
- `Scope` with exact files, modules, routes, APIs, schemas, docs, or runtime surfaces
- `Implementation Plan` with step-by-step execution and validation
- `Acceptance Criteria` with testable conditions
- `Definition of Done` using `DEFINITION_OF_DONE.md`
- `Result Report`

Runtime tasks must be delivered as a vertical slice: UI -> logic -> API -> DB
-> validation -> error handling -> test. Partial implementations, mock-only
paths, placeholders, fake data, and temporary fixes are forbidden.

## Integration Evidence

- `INTEGRATION_CHECKLIST.md` reviewed: not applicable
- Real API/service path used: yes
- Endpoint and client contract match: yes
- DB schema and migrations verified: not applicable
- Loading state verified: not applicable
- Error state verified: not applicable
- Refresh/restart behavior verified: not applicable
- Regression check performed:
  - auth modal and landing CTA flow remain wired to the same handlers

## Product / Discovery Evidence
- Problem validated: yes
- User or operator affected:
  - public-entry visitors on desktop and wide screens
- Existing workaround or pain:
  - nested container framing weakened the scenic flagship effect
- Smallest useful slice:
  - rebuild only the `home` shell framing and immediate supporting bands
- Success metric or signal:
  - the public hero reads as one full-bleed stage with overlay navigation
- Feature flag, staged rollout, or disable path: no
- Post-launch feedback or metric check:
  - next deploy-side visual compare

## Reliability / Observability Evidence
- `docs/operations/service-reliability-and-observability.md` reviewed: not applicable
- Critical user journey:
  - first-view public landing read
- SLI:
  - not applicable
- SLO:
  - not applicable
- Error budget posture: not applicable
- Health/readiness check:
  - frontend build succeeds
- Logs, dashboard, or alert route:
  - not applicable
- Smoke command or manual smoke:
  - `Push-Location .\web; npm run build; Pop-Location`
- Rollback or disable path:
  - revert the public-shell framing patch

## AI Testing Evidence (required for AI features)

- `AI_TESTING_PROTOCOL.md` reviewed: not applicable
- Memory consistency scenarios:
- Multi-step context scenarios:
- Adversarial or role-break scenarios:
- Prompt injection checks:
- Data leakage and unauthorized access checks:
- Result:

## Security / Privacy Evidence
- `docs/security/secure-development-lifecycle.md` reviewed: not applicable
- Data classification:
  - public shell layout and copy only
- Trust boundaries:
  - unauthenticated web shell
- Permission or ownership checks:
  - existing auth modal behavior preserved
- Abuse cases:
  - not applicable
- Secret handling:
  - none
- Security tests or scans:
  - not applicable
- Fail-closed behavior:
  - not applicable
- Residual risk:
  - live crop and note-card density still need deploy-side visual confirmation

## Result Report

- Task summary:
  - rebuilt the public `home` surface into a full-bleed flagship shell with
    overlay navigation, a `100vh` scenic hero, and calmer bridge/trust-band
    framing
- Files changed:
  - `web/src/App.tsx`
  - `web/src/index.css`
  - `docs/ux/design-memory.md`
  - `.codex/tasks/PRJ-818-home-full-bleed-hero-shell-pass.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
- How tested:
  - `Push-Location .\web; npm exec tsc -b; Pop-Location`
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/ux/design-memory.md .codex/tasks/PRJ-818-home-full-bleed-hero-shell-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- What is incomplete:
  - deploy-side proof for final crop and note-card spacing
- Next steps:
  - compare live `home` against the canonical crop and do one last micro-pass
    if needed
- Decisions made:
  - interpreted the user notes as an approved shell override on top of the
    canonical landing image
