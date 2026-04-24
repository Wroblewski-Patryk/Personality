# Task

## Header
- ID: PRJ-597
- Title: Freeze the repo-driven Coolify deployment-automation baseline
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-596
- Priority: P0

## Context
The runtime is healthy in production, but the current operational truth still
shows deployment ambiguity: a push to `main` does not always appear to result
in an automatic Coolify deploy without manual observation or intervention.
Before organizer-tool activation or tool-grounded learning work can rely on a
repo-driven release path, the repository needs one explicit deployment
automation baseline with proof surfaces and rollback posture.

## Goal
Freeze the production baseline for repo-driven Coolify deployment automation so
later execution slices can distinguish a healthy automation path from webhook
fallback or manual UI redeploy.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] One explicit production deployment-automation baseline is recorded for the canonical Coolify app.
- [x] Canonical proof surfaces and fallback posture are defined before evidence or enforcement work.
- [x] Planning/context truth points to the same next execution slice after this baseline freeze.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
- Manual checks:
  - reviewed repository-driven Coolify compose baseline
  - reviewed deployment and release path in the runtime ops runbook
  - reviewed live production release smoke after user-triggered deploy
- Screenshots/logs:
  - production release-smoke summary from 2026-04-24
- High-risk checks:
  - confirmed the baseline still treats webhook/UI deploy as fallback, not as a
    silent replacement for repo-driven source automation

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/10_future_vision.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/26_env_and_config.md`
  - `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - runtime ops and planning truth updated in this slice

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
Frozen production baseline:

1. canonical app:
   - Coolify project `icmgqml9uw3slzch9m9ok23z`
   - environment `qxooi9coxat272krzjx221fv`
   - application `jr1oehwlzl8tcn3h8gh2vvih`
2. intended primary deploy path:
   - push `main`
   - Coolify source automation should enqueue a deploy for the canonical app
   - operator verifies the target commit in Coolify deployment history
   - operator verifies live production with release smoke
3. bounded fallback path:
   - trigger the existing deploy webhook helper when source automation is
     delayed or unavailable
   - if webhook trigger is unavailable, use the Coolify UI redeploy for the
     same canonical app
4. next slice:
   - `PRJ-598` should add machine-visible evidence for whether the primary
     automation path actually fired or whether fallback was required
