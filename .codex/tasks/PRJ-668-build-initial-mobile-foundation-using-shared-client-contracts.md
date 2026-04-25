# Task

## Header
- ID: PRJ-668
- Title: Build initial mobile foundation using shared client contracts
- Status: READY
- Owner: Frontend Builder
- Depends on: PRJ-667
- Priority: P1

## Context
The mobile stack and client-contract baseline are now frozen. The next slice
should create the first real mobile workspace foundation without introducing a
second domain model or bypassing backend-owned contracts.

## Goal
Build the first mobile workspace baseline using the approved Expo-managed stack
and the same backend-owned client resource model as `web`.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- do not move runtime logic into the mobile client

## Definition of Done
- [ ] `mobile/` contains a real buildable app workspace baseline.
- [ ] The mobile workspace records the same backend-owned app resource
  boundaries as `web`.
- [ ] The first scaffold avoids internal debug surfaces and provider-secret UI.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
- Manual checks:
- Screenshots/logs:
- High-risk checks:
  - avoid implying completed native auth transport if the scaffold only freezes
    the shared API boundary

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: docs/architecture/16_agent_contracts.md; docs/architecture/26_env_and_config.md; docs/planning/mobile-client-baseline.md
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: mobile local-dev and workspace docs after scaffold

## Review Checklist (mandatory)
- [ ] Architecture alignment confirmed.
- [ ] Existing systems were reused where applicable.
- [ ] No workaround paths were introduced.
- [ ] No logic duplication was introduced.
- [ ] Definition of Done evidence is attached.
- [ ] Relevant validations were run.
- [ ] Docs or context were updated if repository truth changed.
- [ ] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
The first mobile scaffold should stay intentionally small:

- workspace config
- app shell
- shared API-boundary notes
- no product-domain reimplementation
