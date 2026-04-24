# Task

## Header
- ID: PRJ-637
- Title: Implement scheduler reevaluation and due-item attention handoff
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-636
- Priority: P0

## Context
Time-aware planned work needs a scheduler-owned reevaluation path that can wake
foreground cognition without sending messages directly.

## Goal
Implement background reevaluation of planned work and convert due items into
attention or proposal handoffs for foreground processing.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] External scheduler cadence reevaluates planned work with current time and context.
- [x] Due items enter the existing attention or proposal boundary instead of bypassing it.
- [x] Background ownership remains side-effect-free with respect to user-visible delivery.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_scheduler_worker.py tests/test_runtime_pipeline.py`
- Manual checks: verified maintenance cadence only marks due planned work and upserts `nudge_user` subconscious proposals; it does not call Telegram/API delivery directly
- Screenshots/logs:
- High-risk checks: due-item reevaluation remains side-effect-free and defers user-visible delivery to a later foreground slice

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`, `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: runtime reality and runbook

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
The important boundary is reevaluate in background, deliver in foreground.
Implemented by reusing the existing subconscious proposal boundary:
- scheduler maintenance cadence now reevaluates due planned work
- due items are marked `due` and handed off as `nudge_user` subconscious proposals
- no background path sends Telegram or API messages directly
