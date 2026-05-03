# V1 Reality Audit And Roadmap

Date: 2026-05-03
Task: `PRJ-951`
Status: READY queue created

## Purpose

This audit compares current v1 release claims with code, generated docs,
production health, and the task board. Its goal is to make the path to a real
v1 factual, executable, and resistant to drift.

## Current Reality

| Area | Code or Evidence Checked | Current State | V1 Meaning |
| --- | --- | --- | --- |
| Git source | `git status --short --branch`, `git log`, `git remote -v` | `main` matches `origin/main`; origin is `Wroblewski-Patryk/Aviary`; only local `.codex/tmp/` and `artifacts/` are untracked | Repository truth is ready for deploy work |
| Production revision | `GET https://aviary.luckysparrow.ch/health`, `/settings` meta | Production still reports `ed1c4d981314787d76252985b53c14ea1d7886ed` | Current `origin/main` is not deployed |
| Release smoke | `run_release_smoke.ps1 -WaitForDeployParity` in PRJ-938 | Failed after 900 seconds because production stayed on the older SHA | Release marker remains blocked |
| V1 health gates | `/health.v1_readiness` | Existing deployed SHA reports `core_v1_bundle_ready` and green final gates | Core v1 behavior appears green only for the currently deployed older SHA |
| Deploy policy | `backend/app/core/deployment_policy.py`, `/health.deployment` | Runtime declares source automation and build revision | The proof surface exists; the automation did not converge for the latest push |
| API/routes | `backend/app/api/routes.py`, `docs/api/openapi.json` | App auth, chat, tools, Telegram link, event, debug, health, and webhook routes exist; generated OpenAPI is in sync | API foundation is documented enough for v1 hardening |
| Database/model docs | `backend/app/memory/models.py`, `docs/data/columns.md`, `docs/data/erd.mmd` | Generated column reference and ERD match the current ORM metadata | The previous ERD/model-reference gap is closed |
| Frontend | `web/src/App.tsx`, `web/src/lib/api.ts`, `docs/frontend/route-component-map.md` | Browser shell exists but most route ownership remains monolithic in `App.tsx` | Usable, but future v1-web confidence needs e2e route coverage before refactor |
| Tests | `backend/tests/*`, focused deployment-trigger tests | Backend coverage is broad; deployment parity tests passed locally | Missing evidence is now mostly live/fixture/e2e, not basic unit coverage |
| AI/security hardening | `docs/security/v1-ai-red-team-scenario-pack.md`, PRJ-932/933 audits | Scenario pack and audits exist; execution evidence gaps remain | Public v1 claim should either run or explicitly defer these |
| Provider integrations | `backend/app/integrations/**`, `docs/integrations/index.md` | Provider docs exist; live provider credentials are still missing for some smokes | Core v1 can proceed, broader organizer/provider claims remain blocked |

## Main Finding

The project is not blocked by missing engineering documentation anymore. The
current blocker is release reality:

- the repository candidate is ahead of production
- Coolify source automation did not converge within the release-smoke window
- the core acceptance bundle still contains historical GO language for an older
  deployed SHA
- the release marker remains correctly blocked until a selected SHA has fresh
  production smoke

## Current Acceptance Boundary

| Claim | Decision | Why |
| --- | --- | --- |
| Historical core no-UI v1 behavior on deployed production SHA | GO with stale-revision caveat | `/health.v1_readiness` is green on the deployed SHA |
| Current `origin/main` as deployed v1 | NO-GO | production revision does not match `origin/main` |
| Final release tag/marker | BLOCKED | PRJ-936 and PRJ-938 correctly block marker creation |
| Telegram-led launch claim | BLOCKED | PRJ-909 needs operator token/secret/chat preconditions |
| Organizer/provider daily-use launch claim | BLOCKED | PRJ-918 needs provider credentials |
| Public/web-led v1 confidence | PARTIAL | frontend exists, but stable frontend e2e coverage is still missing |

## Roadmap

### P0: Make V1 Deployable And Truthful

| ID | Task | Status | Definition Of Done |
| --- | --- | --- | --- |
| PRJ-952 | Recover Coolify source automation or run approved fallback | BLOCKED_EXTERNAL | Coolify history shows the pushed SHA or webhook/UI fallback evidence exists; production begins deploying selected SHA |
| PRJ-953 | Rerun production release smoke for selected SHA | READY_AFTER_PRJ-952 | backend revision, web revision, release smoke, and optional fallback evidence all match selected SHA |
| PRJ-954 | Refresh v1 acceptance bundle for current selected SHA | READY_AFTER_PRJ-953 | acceptance bundle no longer implies stale deploy parity and records exact SHA evidence |
| PRJ-955 | Create release marker only after green production evidence | READY_AFTER_PRJ-954 | tag/marker created for selected SHA; task board/project state record evidence |
| PRJ-956 | Add a release reality audit script | DONE | local script checks git SHA, production backend SHA, web meta SHA, release readiness, and v1 gates in one command |
| PRJ-957 | Make production health monitor revision-aware | READY | monitor can alert on revision drift, not only HTTP health |

### P1: Close Hardening Evidence Gaps

| ID | Task | Status | Definition Of Done |
| --- | --- | --- | --- |
| PRJ-958 | Execute AI red-team scenario pack | READY | scenarios from `v1-ai-red-team-scenarios.json` have pass/fail evidence or documented non-executable cases |
| PRJ-959 | Add cross-user/session regression tests | READY | two-user transcript, reset, cookie switching, and Telegram relink/conflict scenarios are covered |
| PRJ-960 | Add provider payload sentinel regressions | READY | frontend/backend projections prove raw provider payloads do not leak through app surfaces |
| PRJ-961 | Add strict-mode incident sentinel regression | READY | strict-mode incident export keeps safe health-derived evidence and excludes debug payloads |
| PRJ-962 | Execute production Telegram live-mode smoke | BLOCKED_EXTERNAL | operator token, webhook secret, and known chat id are provided; smoke passes in live mode |
| PRJ-963 | Execute organizer provider activation smoke | BLOCKED_EXTERNAL | ClickUp, Google Calendar, and Google Drive credentials are configured; provider smoke passes |

### P2: Improve Web And Operator Confidence

| ID | Task | Status | Definition Of Done |
| --- | --- | --- | --- |
| PRJ-964 | Add provider request/response examples | READY | provider docs include sanitized examples for ready/failure paths without secrets |
| PRJ-965 | Add OpenAPI-to-web type sync plan or generator | READY | web API client drift can be checked against generated OpenAPI |
| PRJ-966 | Add stable frontend route e2e smoke | READY | public, auth, dashboard, chat, personality, and tools routes have repeatable smoke coverage |
| PRJ-967 | Split `web/src/App.tsx` after e2e coverage | READY_AFTER_PRJ-966 | route/component extraction reduces monolith without changing behavior |
| PRJ-968 | Add release evidence index | READY | one index shows current candidate, production SHA, smoke status, blockers, and next action |
| PRJ-969 | Add Coolify fallback secret/runbook readiness check | READY | operator docs and local check clearly show whether approved webhook fallback can be run |
| PRJ-970 | Add release go/no-go command wrapper | READY_AFTER_PRJ-956 | one command runs local release audit plus production smoke and prints GO/HOLD |

## First Execution Order

1. `PRJ-956` because it is local, unblocked, and turns the current release
   ambiguity into a repeatable command.
2. `PRJ-957` because the external monitor should catch exactly the deploy
   parity drift that blocked PRJ-938.
3. `PRJ-952` when operator/Coolify access is available.
4. `PRJ-953` immediately after a deployment starts or fallback evidence exists.
5. `PRJ-954` and `PRJ-955` only after production is green for the selected SHA.

## Validation Performed During This Audit

```powershell
git status --short --branch
git remote -v
git log --oneline --decorate -5
Invoke-RestMethod -Uri "https://aviary.luckysparrow.ch/health" -TimeoutSec 30
curl.exe -s -L --max-time 30 https://aviary.luckysparrow.ch/settings
Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "deploy_parity or runtime_build_revision"; Pop-Location
Push-Location .\backend; ..\.venv\Scripts\python .\scripts\export_openapi_schema.py --output ..\.codex\tmp\audit-openapi.json; Pop-Location
Push-Location .\backend; ..\.venv\Scripts\python .\scripts\export_data_model_reference.py --columns-output ..\.codex\tmp\audit-data-model.md --erd-output ..\.codex\tmp\audit-erd.md; Pop-Location
```

Results:

- deployment-trigger focused tests: `6 passed, 46 deselected`
- generated OpenAPI matched `docs/api/openapi.json`
- generated column model matched `docs/data/columns.md`
- generated ERD matched `docs/data/erd.mmd`
- production still served `ed1c4d981314787d76252985b53c14ea1d7886ed`

## Residual Risks

- Coolify source automation may be disconnected, delayed, or pointing at an
  unexpected source configuration despite `/health.deployment` declaring the
  source-automation policy.
- The current core acceptance bundle still needs a fresh SHA refresh after
  deploy parity is recovered.
- Live provider and Telegram smokes remain external-input blockers.
- Frontend confidence is currently route-map and task-evidence based rather
  than a stable e2e test command.
