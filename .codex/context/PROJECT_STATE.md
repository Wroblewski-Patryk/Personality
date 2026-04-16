# PROJECT_STATE

Last updated: 2026-04-17

## Product Snapshot

- Name: Personality / AION
- Goal: build a memory-aware AI runtime that receives events, reasons through a structured pipeline, replies through API or Telegram, and learns lightweight user preferences over time
- Commercial model: TBD
- Current phase: contract hardening and runtime simplification

## Confirmed Decisions

- 2026-04-15: repository docs were split into `docs/basics/` for long-form architecture intent and `docs/` category folders for repo-derived guidance.
- 2026-04-16: this repo now uses a project-specific agent workflow adapted to the current Python/FastAPI/AION stack.
- 2026-04-16: reflection is treated as a real app-local durable worker concern, not as a purely hypothetical future subsystem.
- 2026-04-16: runtime-facing docs now explicitly distinguish implemented runtime behavior from still-planned architecture, including the current expression-before-action orchestration detail.
- 2026-04-16: endpoint-level tests now cover the public reflection contract shape for both `GET /health` and `/event`.
- 2026-04-16: the repo now has a formal Alembic baseline for the current schema, while startup `create_tables()` remains as a temporary MVP bootstrap path.
- 2026-04-17: `POST /event` now returns a smaller public response contract by default, while the full internal `RuntimeResult` is exposed only through an explicit `debug=true` API path.
- 2026-04-17: the repo now has a repeatable release smoke helper for health plus event verification, including an optional UTF-8 payload check and optional debug response validation.
- 2026-04-17: repo analysis confirmed that the main remaining risks are semistructured episodic-memory contracts, motivation-mode drift versus `docs/basics`, duplicated signal logic, missing stage-level structured logging, and the temporary migration/bootstrap dual path.
- 2026-04-17: the next execution roadmap was regrouped into small task batches under `docs/planning/next-iteration-plan.md` and `.codex/context/TASK_BOARD.md`, with parallel-ready lanes for memory contracts, motivation alignment, and logging.
- 2026-04-17: episodic memory rows now persist a typed JSON payload alongside a human-readable summary, and both context retrieval and reflection now read payload-first with legacy summary fallback.
- 2026-04-17: motivation now uses only the documented shared mode set (`respond|ignore|analyze|execute|clarify`), while emotional support remains visible through role, valence, planning, and expression tone.
- 2026-04-17: emotional-turn contract tests now describe supportive behavior through the documented runtime surfaces (`respond`, negative valence, `friend` role, supportive planning, and supportive expression tone).

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

- Main active objective: harden the runtime contracts that future behavior depends on before adding more heuristics
- Current runtime emphasis: reduce duplicated signal logic across stages and improve structured observability
- Top blockers:
  - goal and milestone signal logic is duplicated across context, motivation, planning, and reflection
  - stage-level structured logging is still missing even though stage timings already exist
  - startup is still on a temporary dual-path schema model: Alembic baseline plus startup `create_tables()`
- Success criteria for this phase:
  - shared goal and milestone signals have one clear implementation owner
  - runtime stage decisions are observable through structured logs
  - docs, task board, and code stay synchronized after each slice

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
