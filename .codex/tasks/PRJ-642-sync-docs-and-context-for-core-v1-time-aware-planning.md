# Task

## Header
- ID: PRJ-642
- Title: Sync docs and context for core V1 time-aware planning
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-641
- Priority: P1

## Context
Once the revised core `v1` path is implemented, repository truth should say the
same thing across product, runtime, testing, ops, and planning docs.

## Goal
Synchronize docs/context for time-aware planned work as part of core `v1` and
for organizer tools as a later extension.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [ ] Product, runtime, testing, ops, planning, and context docs all describe the same core `v1` state.
- [ ] Organizer tools are clearly described as post-`v1` extension or sync layer.
- [ ] The next queue is left to fresh analysis instead of backlog residue.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: doc-and-context sync
- Manual checks: cross-review against final planned-work and research-window evidence
- Screenshots/logs:
- High-risk checks: avoid leaving the repo half on old reminder or organizer-blocking language

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/architecture/02_architecture.md`, `docs/architecture/10_future_vision.md`, `docs/architecture/15_runtime_flow.md`, `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: product/runtime/testing/ops/planning/context as needed

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
This slice should make the repository speak with one voice about core `v1`
time-aware planning and later organizer activation.

Completed on 2026-04-24.

Result:

- product, runtime, testing, ops, planning, and context docs now describe the
  same core no-UI `v1` boundary around conversation, bounded web reading,
  tool-grounded learning, and internal time-aware planned work
- organizer tools are now described consistently as a later extension or sync
  layer instead of a hidden core-`v1` blocker
- the seeded queue through `PRJ-642` is now closed; the next execution queue
  should come from fresh analysis instead of leftover backlog residue

Validation:

- doc-and-context cross-review across architecture, testing, runbook,
  planning, and `.codex/context/` source-of-truth files
