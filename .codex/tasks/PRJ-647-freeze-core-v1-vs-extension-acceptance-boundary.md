# Task

## Header
- ID: PRJ-647
- Title: Freeze the core-v1 versus extension acceptance boundary
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-642
- Priority: P0

## Context
Fresh analysis after `PRJ-642` shows that repo truth now says core no-UI `v1`
is stable conversation, bounded website reading, tool-grounded learning, and
internal time-aware planned work. But some runtime acceptance surfaces and
tests still mix that core boundary with later organizer-extension posture.

## Goal
Freeze one explicit acceptance boundary that separates core no-UI `v1` from
later organizer or channel-polish extensions.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Canonical planning truth defines which gates are core no-UI `v1` blockers and which are extension-only posture.
- [x] Organizer daily-use posture is explicitly classified as extension readiness rather than a hidden core-`v1` blocker.
- [x] The next implementation slice has one clear contract target for truthful `v1_readiness`.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: architecture and planning cross-review
- Manual checks: compared `docs/architecture/10_future_vision.md`, `docs/architecture/17_logging_and_debugging.md`, `docs/architecture/29_runtime_behavior_testing.md`, `docs/implementation/runtime-reality.md`, and `app/core/v1_readiness_policy.py`
- Screenshots/logs:
- High-risk checks: organizer daily-use posture is now explicitly described as mirrored extension readiness rather than a core blocker

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/10_future_vision.md`, `docs/architecture/16_agent_contracts.md`, `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: completed in architecture docs, planning truth, runtime reality, and context

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
This slice is about truthfulness of the product boundary, not new runtime
capability.

Completed on 2026-04-25.
