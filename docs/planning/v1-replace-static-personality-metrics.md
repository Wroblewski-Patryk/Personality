# V1 Replace Static Personality Metrics

Last updated: 2026-05-03

## Status

`PRJ-914` is DONE.

The Personality route no longer presents the removed static clarity, intuition,
or skill-count claims as live product truth.

## Evidence

Validation commands and results:

- `Push-Location .\web; npm run build; Pop-Location`
  - passed
- bundled Node + Playwright focused `/personality` metrics smoke against local
  Vite and local backend:
  - `checks=2`
  - `failures=0`
  - `unexpectedConsoleIssueCount=0`
  - `benignConsoleIssueCount=2`
  - `screenshots=2`
- `git diff --check`
  - passed

The two benign console issues were expected unauthenticated `401` responses
from `/app/me` while checking `/login` before local registration.

## Product-Honesty Changes

`web/src/App.tsx` now derives the Personality metric strip from existing
overview data:

- focus from active goals
- clarity from learned semantic conclusions, preferences, and active goals
- energy from pending proposals
- load from active and blocked tasks
- intuition from relations, affective conclusions, adaptive output keys, and
  theta presence
- skills from the role-skill catalog visibility summary or skill registry

The previous fixed values were removed:

- `87%`
- `Strong`
- fallback `18` skills

## Evidence Artifacts

Local, uncommitted artifacts:

- `.codex/artifacts/prj914-personality-metrics/personality-metrics-smoke-results.json`
- `.codex/artifacts/prj914-personality-metrics/personality-desktop.png`
- `.codex/artifacts/prj914-personality-metrics/personality-mobile.png`

## Notes

This task intentionally stayed inside the Personality route. Static dashboard
summary cards and broader empty/error state coverage remain in `PRJ-915` and
`PRJ-916`.

Production route evidence still requires a fresh deploy parity smoke after the
commit is pushed and deployed.
