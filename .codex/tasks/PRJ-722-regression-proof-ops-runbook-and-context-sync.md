# Task

## Header
- ID: PRJ-722
- Title: Regression Proof, Ops Runbook, And Context Sync
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-721
- Priority: P1

## Context
The destructive-data lane already had the frozen boundary, shared backend
cleanup owner, and web settings UX. The remaining closure slice was to leave
behind final regression evidence, operator guidance, and synchronized
source-of-truth notes for the completed lane.

## Goal
Close the user-data reset and production-cleanup lane with full validation,
runbook guidance, testing guidance, and context sync that all describe the
same bounded destructive posture.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Full backend regression and web build evidence are recorded for the lane.
- [x] Runtime ops runbook documents the operator cleanup path and self-service reset boundary.
- [x] Planning and context truth mark the destructive-data lane complete.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - result: `937 passed`
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: build passed
- Manual checks:
  - runbook now includes the canonical cleanup commands and destructive guardrails
- Screenshots/logs:
  - full-suite regression was green after refreshing the graph-stage fake OpenAI client signature
- High-risk checks:
  - self-service reset and operator cleanup now share one documented preserved-versus-cleared boundary
  - destructive operator flow stays outside product UI

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/planning/user-data-reset-and-production-cleanup-plan.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - not applicable
- Follow-up architecture doc updates:
  - lane closure synced through task board, project state, plan, runbook, and testing guidance

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
- Full-lane evidence includes one harness-drift fix in `backend/tests/test_graph_stage_adapters.py` so the test fake matches the current expression-client call shape.
- The destructive-data lane seeded through `PRJ-722` is now complete.
