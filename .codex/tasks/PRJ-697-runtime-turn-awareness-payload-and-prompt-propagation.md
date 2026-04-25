# Task

## Header
- ID: PRJ-697
- Title: Runtime Turn-Awareness Payload And Prompt Propagation
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-696
- Priority: P1

## Context
Foreground truth existed in runtime state, but current-turn timestamp and
foreground-awareness posture were not propagated clearly enough into context,
prompting, and final reply generation.

## Goal
Propagate turn-awareness payloads through runtime, context, and OpenAI prompt
construction so the active turn can answer from truthful current-turn state.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] runtime loads and carries current-turn awareness through the foreground path
- [x] OpenAI reply prompting receives explicit foreground-awareness and current-turn timestamp fields
- [x] expression has deterministic direct-reply handling for current-turn time questions

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_openai_prompting.py tests/test_expression_agent.py tests/test_runtime_pipeline.py; Pop-Location`
- Manual checks:
  - verified runtime result and delivered reply stay aligned after action-side enrichment
- Screenshots/logs:
  - none
- High-risk checks:
  - prompt expansion stays bounded and reuses existing expression/OpenAI layers

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/15_runtime_flow.md`
  - `docs/architecture/16_agent_contracts.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
  - none
- Follow-up architecture doc updates:
  - completed in this lane

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
Implemented through `backend/app/core/runtime.py`,
`backend/app/integrations/openai/prompting.py`,
`backend/app/integrations/openai/client.py`, and
`backend/app/expression/generator.py`.
