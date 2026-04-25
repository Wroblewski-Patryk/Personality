# Task

## Header
- ID: PRJ-666
- Title: Add release smoke and repo-driven post-push deploy proof for `backend + web`
- Status: DONE
- Owner: QA/Test
- Depends on: PRJ-665
- Priority: P1

## Context
Once backend and web ship together, release proof must validate both layers as
one deployable unit instead of checking backend revision alone.

## Goal
Extend deploy-proof coverage so release smoke validates that the served web
build revision matches the backend runtime build revision and local repo truth.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] release smoke validates the served web shell revision from `/`
- [x] PowerShell regression coverage pins success and failure paths
- [x] combined backend + web deploy parity is part of the repo-driven smoke baseline

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "release_smoke_allows_optional_deployment_evidence_to_be_omitted or web_shell_build_revision or runtime_build_revision or deployment_evidence_after_sha"; Pop-Location`
- Manual checks:
  - release smoke summary now exports `web_shell_build_revision`
- Screenshots/logs:
  - targeted pytest run passed with `6 passed`
- High-risk checks:
  - verified failure when web revision is empty or drifts from runtime build revision

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/v2-product-entry-plan.md`, `docs/engineering/testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: testing and planning docs

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
The bash smoke path was kept in parity with the PowerShell deploy-proof logic,
but PowerShell remains the directly exercised regression path in this
workspace.
