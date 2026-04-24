# Task

## Header
- ID: PRJ-643
- Title: Freeze the channel-aware delivery constraint baseline
- Status: BACKLOG
- Owner: Planning Agent
- Depends on: PRJ-650
- Priority: P1

## Context
Telegram currently uses one plain `sendMessage` path without explicit
channel-specific formatting or message-length adaptation. That causes long
messages to fail the real channel contract and makes markdown-style output show
literal symbols instead of styled text.

## Goal
Freeze one delivery baseline where response delivery is channel-aware rather
than Telegram-hardcoded.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Architecture and planning truth define channel-aware delivery constraints as part of the existing action-delivery boundary.
- [ ] Telegram-specific message-length and formatting rules are explicit.
- [ ] The baseline keeps future UI or API channels free to declare different limits and formatting capabilities.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: architecture and delivery-contract cross-review
- Manual checks: compare Telegram/current API behavior against the frozen baseline
- Screenshots/logs:
- High-risk checks: avoid baking Telegram-only assumptions into expression or planning

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`, `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: runtime reality, testing, ops, planning/context

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
The key boundary is still expression -> action -> delivery. Channel adaptation
belongs below expression, not inside planning.
