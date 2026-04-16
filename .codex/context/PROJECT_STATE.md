# PROJECT_STATE

Last updated: 2026-04-16

## Product Snapshot

- Name: Personality / AION
- Goal: build a memory-aware AI runtime that receives events, reasons through a structured pipeline, replies through API or Telegram, and learns lightweight user preferences over time
- Commercial model: TBD
- Current phase: MVP-plus runtime refinement

## Confirmed Decisions

- 2026-04-15: repository docs were split into `docs/basics/` for long-form architecture intent and `docs/` category folders for repo-derived guidance.
- 2026-04-16: this repo now uses a project-specific agent workflow adapted to the current Python/FastAPI/AION stack.
- 2026-04-16: reflection is treated as a real app-local durable worker concern, not as a purely hypothetical future subsystem.

## Technical Baseline

- Backend: Python 3.11, FastAPI, Pydantic v2
- Frontend: none yet
- Mobile: none
- Database: PostgreSQL with SQLAlchemy async and asyncpg
- Infra: Docker Compose locally, Coolify-targeted compose for deployment
- External APIs: OpenAI Responses API, Telegram Bot API
- MCP / external tools: Playwright available locally for future UI or browser-driven checks

## Validation Commands

- Lint: not configured yet
- Typecheck: not configured yet
- Unit and integration tests: `.\.venv\Scripts\python -m pytest -q`
- Targeted tests: `.\.venv\Scripts\python -m pytest -q tests/<file>.py`
- Runtime smoke: `docker compose up --build`
- HTTP smoke: `curl http://localhost:8000/health` and `curl -X POST http://localhost:8000/event ...`
- Other high-risk checks: Telegram webhook setup/verification when deployment or integration code changes

## Current Focus

- Main active objective: keep growing memory, preference, role, and reflection behavior without losing runtime honesty or deterministic test coverage
- Current runtime emphasis: lightweight goal and milestone management now includes phase, arc, pressure, dependency, due, due-window, risk, and completion signals, still without a heavyweight milestone engine
- Top blockers:
  - no formal migration framework yet
  - `/event` still exposes a verbose internal runtime contract
  - deployment automation and release confidence still need hardening
- Success criteria for this phase:
  - runtime changes remain test-covered
  - docs and code describe the same system
  - reflection and preference behavior stay observable and bounded

## Working Agreements

- Keep task board and project state synchronized.
- Keep changes small and reversible.
- Validate touched areas before marking done.
- Keep repository artifacts in English.
- Communicate with users in their language.
- Delegate with explicit ownership and avoid overlapping subagent write scope.
- Use the default loop: plan -> implement -> test -> architecture review -> sync context.

## Canonical Files

- `docs/README.md`
- `docs/overview.md`
- `docs/assumptions/runtime-baseline-2026-04-15.md`
- `docs/basics/02_architecture.md`
- `docs/basics/15_runtime_flow.md`
- `docs/basics/16_agent_contracts.md`
- `docs/basics/26_env_and_config.md`
- `docs/basics/27_codex_instructions.md`
- `docs/planning/next-iteration-plan.md`
- `docs/planning/open-decisions.md`
- `docs/engineering/testing.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/context/TASK_BOARD.md`

## Optional Project Docs

- Add new canonical docs only when they clearly improve delivery or reduce drift.
