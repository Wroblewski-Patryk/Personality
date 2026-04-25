# Task

## Header
- ID: PRJ-659
- Title: Scaffold the `mobile/` workspace as a reserved product surface
- Status: DONE
- Owner: Frontend Builder
- Depends on: PRJ-658
- Priority: P2

## Context
The user explicitly wants a later mobile client, but the concrete mobile stack
was not yet approved.

## Goal
Reserve a real `mobile/` product surface without prematurely locking the
repository into Expo or another mobile stack.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] `mobile/` exists as a tracked workspace in the repo.
- [x] The placeholder states that mobile must reuse backend auth and app-facing API.
- [x] No unapproved mobile runtime stack is introduced yet.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: workspace and docs cross-review
- Manual checks: confirmed `mobile/README.md` preserves the undecided stack boundary
- Screenshots/logs:
- High-risk checks: no premature mobile-framework lock-in

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/v2-product-entry-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: user approved `backend/web/mobile` root topology
- Follow-up architecture doc updates: reflected in docs index and v2 plan progress

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
The next mobile slice should start from explicit stack approval, not assumption.
