# Task

## Header
- ID: PRJ-650
- Title: Sync docs and context for truthful v1-readiness
- Status: BACKLOG
- Owner: Product Docs Agent
- Depends on: PRJ-649
- Priority: P1

## Context
Fresh analysis found that high-level repo truth is no longer fully synchronized:
some docs still describe older deferred capability posture, while some
readiness wording still implies organizer daily use is part of the final core
`v1` gate.

## Goal
Synchronize product, runtime, testing, ops, and context truth around the
tightened `v1_readiness` semantics.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Canonical docs describe the same core-v1 versus extension boundary as runtime readiness surfaces.
- [ ] `docs/overview.md` and runtime-reality stop implying still-planned capability slices that are already live.
- [ ] Planning/context truth records the next post-readiness delivery lane without reviving stale backlog residue.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: doc-and-context sync
- Manual checks: cross-review architecture, runtime reality, testing, ops, and context
- Screenshots/logs:
- High-risk checks: avoid turning docs into a second competing product definition

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/10_future_vision.md`, `docs/architecture/17_logging_and_debugging.md`, `docs/architecture/29_runtime_behavior_testing.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: `docs/overview.md`, `docs/implementation/runtime-reality.md`, planning/context files

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
This slice should leave one easy-to-read repo story for "what still blocks a
fully convincing v1" versus "what is now extension work".
