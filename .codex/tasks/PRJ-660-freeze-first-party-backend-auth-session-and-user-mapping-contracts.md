# Task

## Header
- ID: PRJ-660
- Title: Freeze first-party backend auth/session and user mapping contracts
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-659
- Priority: P1

## Context
The repo already had `user_id` as runtime identity, but first-party clients
needed backend-owned auth/session instead of treating `X-AION-User-Id` as the
product login boundary.

## Goal
Define one bounded contract where backend auth users map directly onto runtime
`user_id`, and sessions stay backend-owned via cookies.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Auth user identity maps directly onto the existing runtime `user_id`.
- [x] Session ownership is backend-owned and cookie-based.
- [x] Docs and task/context truth describe this as the first-party contract baseline.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: contract cross-review plus targeted API tests in `tests/test_api_routes.py -k "app_"`
- Manual checks: reviewed auth/session route behavior against the approved v2 plan
- Screenshots/logs:
- High-risk checks: first-party app routes no longer depend on `X-AION-User-Id` for primary identity

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/v2-product-entry-plan.md`, `docs/overview.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed: backend-owned auth option `A` approved by user
- Follow-up architecture doc updates: recorded in overview and backend README

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
This freeze intentionally keeps auth simple: backend users, backend sessions,
and direct reuse of runtime `user_id`.
