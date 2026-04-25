# Task

## Header
- ID: PRJ-670
- Title: Implement the backend tools overview read model from existing truth
- Status: DONE
- Owner: Backend Builder
- Depends on: PRJ-669
- Priority: P1

## Context
Backend truth for channels and tools already exists across connector execution
snapshots, organizer stack snapshots, web knowledge tooling snapshots, Telegram
channel telemetry, capability catalog, and app-facing user state. The web
client needs one stable app-facing endpoint instead of reverse-engineering
mixed inspection sections.

## Goal
Expose one backend-owned `tools overview` response for authenticated product
clients using existing runtime truth and without creating a second connector
domain model.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- reuse connector, channel, and readiness snapshots already present in backend
- keep the endpoint client-safe and separate from admin-only debug surfaces

## Definition of Done
- [ ] A new authenticated app-facing endpoint returns grouped tools and
  channels for the current user.
- [ ] The response is composed from existing connector and channel truth rather
  than duplicated state tables.
- [ ] Integral capabilities such as internal chat, web search, and web browser
  are surfaced as always-on backend truth where appropriate.
- [ ] Placeholder entries for not-yet-implemented tools can be returned only if
  their state is explicit and non-deceptive.
- [ ] Focused backend tests cover the response shape and main state mappings.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location backend; ..\.venv\Scripts\python -m pytest -q tests\test_api_routes.py; Pop-Location`
- Manual checks: authenticated `GET /app/tools/overview` returns grouped communication, task, knowledge, and organizer sections
- Screenshots/logs:
- High-risk checks: verify the endpoint does not expose secrets or admin-only
  payloads

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: docs/architecture/16_agent_contracts.md; docs/architecture/26_env_and_config.md
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: app-facing API docs and overview docs

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
Expected truth sources include:
- connector execution baseline
- organizer tool stack snapshot
- web knowledge tools snapshot
- conversation channels telegram snapshot
- user settings and runtime preferences

Completed on 2026-04-25:
- added `backend/app/core/app_tools_policy.py`
- added authenticated route `GET /app/tools/overview`
- added route coverage for auth requirement, default grouped truth, and
  provider-ready variants
