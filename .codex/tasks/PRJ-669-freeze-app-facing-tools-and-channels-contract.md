# Task

## Header
- ID: PRJ-669
- Title: Freeze the backend-owned app-facing tools and channels contract
- Status: DONE
- Owner: Product Docs Agent
- Depends on: PRJ-663, PRJ-664, PRJ-666
- Priority: P1

## Context
The first `v2` browser release already exposes auth, settings, chat, and
personality inspection. The next requested product slice is a dedicated tools
and channels experience that shows what the personality can use, which parts
are integral, which require provider configuration, and which are user-owned
enablement choices. Existing truth is currently spread across `/health`,
connector snapshots, and personality overview payloads.

## Goal
Define one app-facing contract for grouped tools and channels so `web/` can
render a truthful tools screen without rebuilding backend capability logic in
the client.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic
- provider secrets must remain external configuration unless architecture is
  explicitly changed
- user-owned enablement must stay distinct from provider readiness and
  integral capabilities

## Definition of Done
- [ ] A canonical app-facing tools and channels response shape is defined.
- [ ] The contract explicitly distinguishes integral, provider-blocked,
  user-toggleable, and link-required states.
- [ ] Telegram is defined as identity linking rather than browser secret entry.
- [ ] Future tools such as Trello or a custom Nest app have an approved
  placeholder posture in the grouped model.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests: `Push-Location backend; ..\.venv\Scripts\python -m pytest -q tests\test_api_routes.py -k "app_tools_overview or app_personality_overview or app_patch_settings or app_login_logout_and_me_roundtrip"; Pop-Location`
- Manual checks: contract is now implemented through authenticated `GET /app/tools/overview`
- Screenshots/logs:
- High-risk checks: contract does not require provider secrets to move into UI

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: docs/architecture/16_agent_contracts.md; docs/architecture/26_env_and_config.md; docs/architecture/27_codex_instructions.md
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: app-facing tools contract docs if the
  contract becomes canonical beyond task notes

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
This task should freeze the grouping model first:
- Communication
- Task Management
- Knowledge and Web
- Internal
- later optional families such as Calendar, Files, and Custom Apps

Completed on 2026-04-25:
- app-facing grouped tools contract now exists
- contract distinguishes integral capabilities, provider-blocked tools,
  provider-ready-but-link-required Telegram, and explicit planned placeholders
