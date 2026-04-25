# Task

## Header
- ID: PRJ-667
- Title: Freeze mobile client stack and shared client-contract baseline
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-655, PRJ-660, PRJ-662
- Priority: P1

## Context
`mobile/` already exists as an approved product surface, but it still only
contains a placeholder README. The next delivery step needs one explicit mobile
stack choice and one shared client-contract baseline so later scaffold work
does not guess architecture ad hoc.

## Goal
Freeze the initial mobile stack and define the shared backend-owned client
contract boundary that the first mobile scaffold must follow.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- keep backend as the only owner of auth, cognition, memory, planning, and
  integrations

## Definition of Done
- [x] The repository records one explicit mobile stack choice.
- [x] The repository records one explicit shared client-contract baseline for
  `web` and `mobile`.
- [x] Mobile docs and context no longer describe the stack as intentionally
  deferred.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - not applicable; docs-and-planning-only slice
- Manual checks:
  - `mobile/README.md` and planning docs now describe the same frozen stack and
    backend-owned contract boundary
- Screenshots/logs:
- High-risk checks:
  - do not imply that native mobile auth transport is already implemented just
    because the shared resource contract is frozen

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: docs/architecture/16_agent_contracts.md; docs/architecture/26_env_and_config.md; docs/governance/repository-structure-policy.md
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: mobile planning baseline and docs index

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
Approved baseline for the first mobile foundation:

- Expo-managed React Native app
- TypeScript
- Expo Router
- backend-owned app-facing resource contracts reused from `/app/*`
- no internal debug or provider-secret management in the mobile client
