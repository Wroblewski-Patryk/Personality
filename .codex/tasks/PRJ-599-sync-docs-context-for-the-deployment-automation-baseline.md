# Task

## Header
- ID: PRJ-599
- Title: Sync docs/context for the deployment-automation baseline
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-598
- Priority: P1

## Context
`PRJ-598` made deployment provenance machine-visible in runtime posture,
deploy evidence artifacts, and release smoke. Canonical docs and planning
truth must now describe the same repo-driven Coolify automation contract.

## Goal
Synchronize runbook, planning truth, and repository context around the shared
deployment-automation provenance baseline.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] runbook describes the canonical Coolify app identity and primary versus fallback trigger posture.
- [x] planning truth no longer points at `PRJ-598` as the next active slice.
- [x] repository context points to the next smallest task after deployment-provenance sync.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` now fails fast on older production until the new deployment provenance contract is deployed, which matches the updated runbook wording
- Manual checks:
  - cross-review of runbook, planning docs, task board, and project state
- Screenshots/logs:
- High-risk checks:
  - docs preserve the primary repo-driven automation stance and do not reframe webhook/UI fallback as the default deploy path

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/17_logging_and_debugging.md`, `docs/operations/runtime-ops-runbook.md`
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
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Notes
This slice intentionally syncs docs and context only; production still needs a
manual Coolify deploy before live `/health.deployment` matches the new repo
contract.
