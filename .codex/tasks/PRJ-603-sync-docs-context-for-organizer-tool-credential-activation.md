# Task

## Header
- ID: PRJ-603
- Title: Sync docs/context for organizer-tool credential activation
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-602
- Priority: P1

## Context
Organizer-tool activation posture is now actionable through
`/health.connectors.organizer_tool_stack.activation_snapshot` and proven
through release smoke plus incident evidence, but canonical repo truth still
needs to describe that richer contract consistently.

## Goal
Synchronize docs and context around the organizer-tool activation contract.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] runtime reality describes the organizer-tool activation snapshot
- [x] testing guidance records the activation proof path
- [x] ops notes describe activation-state triage and next-action posture
- [x] planning and context truth align on the richer organizer-tool activation contract

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
- Manual checks:
  - docs/context cross-review against `/health.connectors.organizer_tool_stack`
    and the `PRJ-602` release-smoke contract
- Screenshots/logs:
- High-risk checks:

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/operations/runtime-ops-runbook.md`, `docs/engineering/testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:

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
This slice keeps the richer organizer-tool activation posture inside the
existing `/health`, incident-evidence, and release-smoke truth path instead of
creating a parallel onboarding document or admin-only contract.
