# Task

## Header
- ID: PRJ-596
- Title: Analyze post-v1 tool-activation and deploy-automation gaps
- Status: DONE
- Owner: Planning Agent
- Depends on: PRJ-595
- Priority: P0

## Context
No-UI `v1` is now live in production and the queue seeded through `PRJ-595`
is complete. Fresh production truth shows the next blockers are no longer
core-runtime survival:

- release smoke is green and core runtime topology is aligned
- organizer-tool posture is machine-visible, but production still reports
  `provider_credentials_missing` for ClickUp, Calendar, and Drive
- bounded web-search and browser reads are live, but there is still no explicit
  backend contract for how approved external reads become durable learned
  knowledge without breaking the planning/action boundary
- user-observed Coolify behavior shows that repo pushes do not always result in
  an automatic deploy, so production deployment automation is not yet a proven
  repo-driven baseline

## Goal
Seed the next execution queue from live production gaps so the repository moves
from a healthy no-UI `v1` into a production-ready external-tool and
tool-grounded-learning baseline without architectural drift.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Fresh production/runtime gaps are summarized from live release evidence and canonical docs.
- [x] A new execution queue is seeded in planning/context truth with one explicit `READY` task.
- [x] The next queue stays inside approved architecture boundaries for tool execution and learned-state ownership.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
- Manual checks:
  - reviewed live production `/health` and release-smoke summary for
    organizer-tool readiness, retrieval alignment, proactive posture, and
    deployment/runtime truth
- Screenshots/logs:
  - production release-smoke summary from 2026-04-24
- High-risk checks:
  - confirmed the next queue does not invent a second tool-execution or
    self-modifying skill-learning path outside the approved planning/action
    boundary

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed:
  - `docs/architecture/02_architecture.md`
  - `docs/architecture/10_future_vision.md`
  - `docs/architecture/16_agent_contracts.md`
  - `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates:
  - planning and context truth only in this slice

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
Seeded queue:

- `PRJ-597..PRJ-599` Coolify Deployment Automation Reliability
- `PRJ-600..PRJ-603` Organizer-Tool Credential Activation
- `PRJ-604..PRJ-607` Tool-Grounded Learning Capture
- `PRJ-608..PRJ-611` Capability Catalog And Future-UI Bootstrap
