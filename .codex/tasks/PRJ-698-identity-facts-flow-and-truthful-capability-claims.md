# Task

## Header
- ID: PRJ-698
- Title: Identity Facts Flow And Truthful Capability Claims
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-697
- Priority: P1

## Context
Linked identity continuity had been repaired, but human-facing identity facts
such as `display_name` still did not reliably reach foreground expression, and
the assistant could still emit false capability-denial wording.

## Goal
Flow identity facts into runtime-facing identity output and prevent expression
from denying capabilities that foreground truth already exposes.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] auth-owned `display_name` can reach identity and context outputs
- [x] direct name-recall questions can be answered from existing identity truth
- [x] false capability-denial wording is rejected when foreground truth says memory continuity is available

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_identity_service.py tests/test_expression_agent.py tests/test_runtime_pipeline.py; Pop-Location`
- Manual checks:
  - verified identity summary and foreground-awareness summary both carry
    human-facing name posture without creating a second profile model
- Screenshots/logs:
  - none
- High-risk checks:
  - name recall remains bounded to already owned auth/profile truth only

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - none
- Follow-up architecture doc updates:
  - completed in this lane

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
Implemented through existing auth-user lookup plus identity/context/expression
reuse; no new identity storage or memory layer was added.
