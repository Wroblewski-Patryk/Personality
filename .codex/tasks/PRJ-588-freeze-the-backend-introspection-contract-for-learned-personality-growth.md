# Task

## Header
- ID: PRJ-588
- Title: Freeze the backend introspection contract for learned personality growth
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-587
- Priority: P1

## Context
The retrieval-provider production drift is now closed, so the next remaining
backend-first architecture gap is richer introspection of how the personality
has learned over time. The repo already exposes `/health.learned_state` and
`GET /internal/state/inspect?user_id=...`, but the contract still needs one
explicit bounded definition before widening those surfaces in `PRJ-589`.

## Goal
Freeze one explicit backend introspection contract for learned personality
growth that future UI and operators can trust without implying self-modifying
code or unconstrained skill execution.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] the repo records one explicit bounded contract for personality-growth introspection
- [x] the contract separates learned knowledge, learned preferences, role/skill metadata, reflection outputs, and planning continuity
- [x] the contract explicitly rejects any implication of self-modifying executable skill learning

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
- Manual checks:
  - architecture/product/runtime cross-review across canonical docs and current internal inspection surfaces
- Screenshots/logs:
- High-risk checks:
  - contract remains backend-owned and bounded, with tools still routed through planning/action instead of learned-state introspection

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/02_architecture.md`
  - `docs/implementation/runtime-reality.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - synchronized in this task for contract wording only; runtime widening stays in `PRJ-589`

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
This task freezes contract language only. Any richer payload widening remains a
separate backend execution slice in `PRJ-589`.
