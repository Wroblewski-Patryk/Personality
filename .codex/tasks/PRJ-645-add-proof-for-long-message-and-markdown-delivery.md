# Task

## Header
- ID: PRJ-645
- Title: Add proof for long-message and markdown delivery
- Status: DONE
- Owner: QA/Test
- Depends on: PRJ-644
- Priority: P1

## Context
Channel-aware delivery should be proven through tests and release evidence, not
left as a best-effort transport detail.

## Goal
Add behavior and regression proof for long Telegram messages and markdown-safe
rendering.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Regression tests prove Telegram segmentation for content beyond the channel limit.
- [x] Regression tests prove formatting behavior for markdown-style content.
- [x] Release or incident evidence records the same delivery adaptation posture.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_observability_policy.py; Pop-Location`
- Manual checks: cross-review that `/health.conversation_channels.telegram`, release smoke, and incident evidence now expose the same Telegram delivery-adaptation posture
- Screenshots/logs:
- High-risk checks: avoid declaring the fix complete on unit tests alone if runtime evidence drifts

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/17_logging_and_debugging.md`, `docs/engineering/testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: testing and ops notes

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
If Telegram markdown mode requires escaping rules, that policy should be proven
explicitly.

Release-facing proof now reuses the existing `conversation_channels.telegram`
surface and `run_release_smoke.ps1` instead of inventing a second delivery
evidence path.
