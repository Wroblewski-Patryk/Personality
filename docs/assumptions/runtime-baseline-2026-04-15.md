# Runtime Baseline Assumptions - 2026-04-15

## Audit Intent

This note started as the 2026-04-15 code-derived baseline and was refreshed on 2026-04-16 after the runtime grew beyond the initial MVP slice.

Its job is to preserve repo truth, especially where the long-form architecture docs are broader than the current implementation.

## Repo Facts Confirmed From Code

- The FastAPI entrypoint is `app.main:app`.
- Startup validates config, initializes logging, creates database tables, wires the runtime, and starts an in-app reflection worker.
- The foreground runtime is still linear and in-process, but it is no longer minimal:
  - load recent memory, profile, runtime preferences, conclusions, theta, goals, tasks, milestones, and histories
  - build identity snapshot
  - perception
  - context
  - motivation
  - role
  - planning
  - expression
  - action
  - episodic memory persistence
  - durable reflection enqueue
- Current external entry points are:
  - `GET /health`
  - `POST /event`
  - `POST /telegram/set-webhook`
- `POST /event` now returns a compact public response by default (`event_id`, `trace_id`, `source`, `reply`, and compact runtime metadata), while the full serialized `RuntimeResult` remains available only through `POST /event?debug=true`.
- Reflection is real and durable:
  - `aion_reflection_task` persists queued work
  - the worker retries failed jobs with bounded backoff
  - `GET /health` exposes a reflection snapshot with queue counters and worker state
- Role selection is dynamic and can use heuristics, reflected `preferred_role`, and lightweight theta bias.
- Runtime keeps lightweight semantic state in Postgres:
  - `aion_profile`
  - `aion_conclusion`
  - `aion_theta`
  - `aion_goal`
  - `aion_task`
  - `aion_goal_progress`
  - `aion_goal_milestone`
  - `aion_goal_milestone_history`
  - `aion_reflection_task`
- Language handling is dynamic per event and can fall back to recent memory or `aion_profile` for ambiguous short turns.
- Telegram remains the only direct side-effecting outbound integration.
- OpenAI is still optional. When unavailable, expression falls back to deterministic local behavior.

## Current Behavioral Assumptions

- Perception, context, motivation, role, and planning remain deterministic heuristic modules, even though they now consume richer memory and preference state.
- The runtime still loads only a small recent episodic window plus lightweight semantic state, not deep ranked or vector retrieval.
- Reflection currently learns lightweight preferences, theta bias, goal-progress signals, and milestone signals inside the app process; it is not a separate worker service.
- Goal and task creation still depends on explicit user phrasing such as `My goal is to ...` or `I need to ...`.
- Task completion updates still depend on explicit progress phrasing such as `I fixed ...`, not broad automatic action-result inference.

## Current vs Planned Gaps

- The intended architecture pipeline is still documented as `... -> action -> expression -> memory -> reflection`, but the current orchestrator computes `expression` before `action` so the action layer can reuse a ready-to-send payload while keeping side effects inside the action boundary.
- The public `/event` response is still an internal debugging contract rather than a minimal stable public DTO.
- Database bootstrap still relies on startup `create_all` behavior instead of formal migrations.
- LangGraph, vector retrieval, a separate reflection worker process, richer relation systems, and proactive loops are still planned, not implemented.
- Goal and milestone management is now real, but it is still a lightweight semantic layer rather than a full milestone engine with explicit dependency graphs or migration-backed lifecycle rules.
- Episodic memory now persists a typed JSON payload alongside a human-readable `aion_memory.summary`, and both context retrieval and background reflection prefer that payload while still falling back to legacy summary-only rows.
- The runtime now keeps emotional-turn behavior inside the documented shared motivation contract (`respond|ignore|analyze|execute|clarify`); supportive behavior remains expressed through role selection, negative valence, planning stance, and expression tone instead of an extra `support` mode.
- Logging currently exposes runtime start/end, reflection updates, and per-stage timings, but it still does not provide the consistent stage-level input/output summaries described in `docs/basics/17_logging_and_debugging.md`.

## Recommended Promotion Targets

The most important canonical docs to keep aligned with this baseline are:

- `docs/overview.md`
- `docs/basics/02_architecture.md`
- `docs/basics/15_runtime_flow.md`
- `docs/basics/16_agent_contracts.md`
- `docs/planning/open-decisions.md`
- `.codex/context/PROJECT_STATE.md`
