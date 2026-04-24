# Task

## Header
- ID: PRJ-649
- Title: Add proof for v1-readiness truthfulness
- Status: BACKLOG
- Owner: QA/Test
- Depends on: PRJ-648
- Priority: P0

## Context
The current release and regression proof strongly checks surface presence and
parity, but fresh analysis shows that the remaining gap is semantic truth of
the acceptance summary itself.

## Goal
Add regression and smoke proof that `v1_readiness` stays aligned with the
approved boundary and live source surfaces.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] API tests fail when core gate states drift from their underlying health-policy owners.
- [ ] Release-smoke or incident-evidence checks fail when extension posture is incorrectly treated as a core-`v1` blocker.
- [ ] Proof covers the approved no-UI `v1` boundary after the post-`PRJ-642` architecture revision.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: targeted pytest plus release-smoke regressions
- Manual checks: compare failing versus passing `v1_readiness` summaries
- Screenshots/logs:
- High-risk checks: avoid proof that only checks field presence again

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/17_logging_and_debugging.md`, `docs/architecture/29_runtime_behavior_testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: testing and ops notes

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
This slice should prove semantics, not only serialization.
