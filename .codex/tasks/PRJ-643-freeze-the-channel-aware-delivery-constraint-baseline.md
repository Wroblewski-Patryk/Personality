# Task

## Header
- ID: PRJ-643
- Title: Freeze the channel-aware delivery constraint baseline
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-654
- Priority: P1

## Context
Telegram delivery quality is now the next true remaining user-facing gap after
readiness-truth and foreground-awareness closure. The runtime still delivers
through one raw Telegram `sendMessage` path, so the delivery boundary needs one
explicit contract before segmentation and formatting logic land in `PRJ-644`.

## Goal
Freeze one explicit channel-aware delivery contract that keeps adaptation below
expression, inside action and integration delivery ownership.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Canonical contracts define channel-aware delivery as a delivery-layer concern, not a planning or cognition concern.
- [x] The contract freezes bounded Telegram segmentation and formatting posture without widening execution authority.
- [x] Planning and context truth point cleanly to `PRJ-644` as the implementation slice.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: architecture and delivery-contract cross-review
- Manual checks: reviewed `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`, `docs/planning/next-iteration-plan.md`, `docs/planning/open-decisions.md`, `.codex/context/TASK_BOARD.md`, and `.codex/context/PROJECT_STATE.md`
- Screenshots/logs:
- High-risk checks: do not push Telegram length limits or markdown policy up into planning, expression, or a second channel-specific cognition path

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`, `docs/architecture/17_logging_and_debugging.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: planning/context sync completed in this slice

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
This slice freezes only the ownership and constraints for delivery adaptation.
It does not yet implement segmentation or markdown formatting.
