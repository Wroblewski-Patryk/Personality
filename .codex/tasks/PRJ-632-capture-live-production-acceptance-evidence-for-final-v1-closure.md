# Task

## Header
- ID: PRJ-632
- Title: Capture live production acceptance evidence for final V1 closure
- Current Stage: release
- Status: DONE
- Owner: Ops/Release
- Depends on: PRJ-631
- Priority: P0

## Context
Final no-UI `v1` closure should not rely only on repo-local evidence. The live system needs its own acceptance evidence bundle.

## Goal
Capture live production evidence for final no-UI `v1` closure.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Live release-smoke evidence is attached for the final acceptance contract.
- [x] Incident-evidence or bundle artifacts prove the same live posture.
- [x] Any operator-assisted deployment or credential steps are recorded explicitly.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: live release-smoke and artifact checks
- Manual checks: production `/health` and incident-evidence verification
- Screenshots/logs: deployment id, release-smoke result, and artifact location if relevant
- High-risk checks: do not mark `v1` closed on repo-only evidence if live production differs

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/17_logging_and_debugging.md`, `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: ops/runbook/planning/context likely

## Review Checklist (mandatory)
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal update was not required; no new recurring pitfall was
  confirmed in this closure sync.

## Notes
This task is intentionally live-production-focused.

This task was superseded on 2026-04-24 by the approved architecture revision
that redefines core no-UI `v1` around:

- stable conversation
- bounded web reading
- tool-grounded learning
- time-aware planned future work

Organizer-tool activation remains a prepared post-`v1` extension and no longer
blocks core `v1` closure.

## Closure Sync - 2026-05-03

- Current release status:
  - DONE. The task remained `BLOCKED` after it was superseded by the
    2026-04-24 architecture revision and later release-evidence tasks.
- Current source-of-truth evidence:
  - `PRJ-922` added the production-safe strict-mode incident evidence export
    path without enabling full debug payload access.
  - `PRJ-923` refreshed the final v1 acceptance bundle against the strict-mode
    incident evidence bundle.
  - `docs/planning/v1-core-acceptance-bundle.md` records core no-UI v1
    behavior, production deploy parity, production incident evidence, and the
    core no-UI declaration as `GO`.
- Remaining related work:
  - `PRJ-909` remains blocked only for a Telegram-led launch-channel claim
    until operator Telegram preconditions are available.
  - `PRJ-918` remains blocked only for the organizer extension until provider
    credentials are configured.
- Closure evidence:
  - reviewed `PRJ-632`, `PRJ-633`, `PRJ-908`, `PRJ-922`, core acceptance
    bundle, release audit plan, open decisions, task board, and project state.
  - no runtime files were changed by this closure sync.
