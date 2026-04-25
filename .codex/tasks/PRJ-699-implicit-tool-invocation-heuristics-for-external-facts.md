# Task

## Header
- ID: PRJ-699
- Title: Implicit Tool Invocation Heuristics For External Facts
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-698
- Priority: P1

## Context
Bounded search and bounded page-read execution already existed, but planning
still depended too much on literal trigger phrases such as `search the web` or
`read page`.

## Goal
Expand planning heuristics so weather asks, latest-fact asks, URLs, and bare
domains can trigger the existing bounded read-only tool paths naturally.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] weather and latest-fact asks can infer bounded web-search intents
- [x] explicit URLs and bare domains can infer bounded page-read intents
- [x] action delivery can summarize bounded read results in the same turn without changing side-effect ownership

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py; Pop-Location`
- Manual checks:
  - reviewed heuristic boundaries for read-only external facts and direct-domain inputs
- Screenshots/logs:
  - none
- High-risk checks:
  - heuristics remain bounded to approved `knowledge_search` and `web_browser`
    families only

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/16_agent_contracts.md`
  - `docs/architecture/15_runtime_flow.md`
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
The lane reuses the existing `knowledge_search.search_web` and
`web_browser.read_page` intent families plus action-owned provider execution.
