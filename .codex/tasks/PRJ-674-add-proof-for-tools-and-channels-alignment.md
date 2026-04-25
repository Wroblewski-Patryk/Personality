# Task

## Header
- ID: PRJ-674
- Title: Add proof that tools and channels UI stays aligned with backend truth
- Status: READY
- Owner: QA/Test
- Depends on: PRJ-670, PRJ-671, PRJ-672, PRJ-673
- Priority: P1

## Context
The tools screen must remain truthful over time. Existing repo standards
already require release smoke, tests, and context synchronization for new
product-facing boundaries.

## Goal
Add validation, test coverage, and documentation so tools and channels state
remain aligned across backend API, web UI, and deployment truth.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- reuse existing release and regression patterns where possible

## Definition of Done
- [ ] Focused backend and web validations cover the tools overview flow.
- [ ] Release or smoke guidance includes the tools and channels truth checks
  when relevant to deploy scope.
- [ ] Canonical docs describe the new app-facing tools boundary and its limits.
- [ ] Context files are synchronized with the delivered baseline.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
- Manual checks:
- Screenshots/logs:
- High-risk checks: ensure no UI state claims provider readiness or linkage
  that backend does not confirm

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: docs/architecture/16_agent_contracts.md; docs/architecture/26_env_and_config.md; docs/engineering/testing.md
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: testing and product-shell docs

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
This task should explicitly guard against the web client becoming a second
source of truth for connector availability.
