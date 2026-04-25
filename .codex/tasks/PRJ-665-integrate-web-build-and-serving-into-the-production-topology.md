# Task

## Header
- ID: PRJ-665
- Title: Integrate `web/` build and serving into the production topology
- Status: DONE
- Owner: Ops/Release
- Depends on: PRJ-664
- Priority: P1

## Context
The first `web/` shell is only product-real when the repo-driven deployment
path can build and ship it together with the existing Python backend.

## Goal
Integrate the browser client into the same repo-driven production topology so
backend and web are built from one commit truth.

## Constraints
- use existing systems and approved mechanisms
- do not introduce new structures without approval
- do not implement workarounds
- do not duplicate logic

## Definition of Done
- [x] Docker builds the browser client in the same repo-driven image flow.
- [x] FastAPI serves the built SPA without replacing backend ownership.
- [x] Production topology keeps one shared build revision across backend and web.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval

## Validation Evidence
- Tests:
  - `docker build -f docker/Dockerfile . --build-arg APP_BUILD_REVISION=test-web-build-rev -t aion-web-smoke:local`
  - `docker compose config`
- Manual checks:
  - confirmed multi-stage Docker build copies `web/dist` into the runtime image
- Screenshots/logs:
  - local Docker build log recorded in task execution notes
- High-risk checks:
  - verified the build revision is injected into the web shell meta tag for deploy parity checks

## Architecture Evidence (required for architecture-impacting tasks)
- Architecture source reviewed: `docs/planning/v2-product-entry-plan.md`, `docs/architecture/13_repository_structure.md`
- Fits approved architecture: yes
- Mismatch discovered: no
- Decision required from user: no
- Approval reference if architecture changed:
- Follow-up architecture doc updates: repository structure and local-development docs

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
Serving stays bounded to the built `web/dist` artifact and SPA fallback paths;
backend APIs remain explicit route owners.
