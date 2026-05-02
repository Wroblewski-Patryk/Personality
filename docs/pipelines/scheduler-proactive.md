# Scheduler And Proactive Pipeline

Last updated: 2026-05-03

Grounded in:

- `backend/app/workers/scheduler.py`
- `backend/app/proactive/engine.py`
- `backend/app/core/planned_action_observer.py`
- `backend/app/core/external_scheduler_policy.py`
- `backend/app/core/proactive_policy.py`
- `backend/scripts/run_maintenance_tick_once.*`
- `backend/scripts/run_proactive_tick_once.*`
- `backend/tests/test_scheduler_worker.py`
- `backend/tests/test_planned_action_observer.py`

## Purpose

The scheduler/proactive pipeline owns cadence-based maintenance, due planned
work observation, proactive admission, and foreground handoff for work that is
allowed to wake the runtime.

## Cadence Owners

| Mode | Owner | Entrypoints |
| --- | --- | --- |
| In-process | `SchedulerWorker.start()` loop | runtime app process |
| Externalized | external scheduler | `run_maintenance_tick_once.*`, `run_proactive_tick_once.*` |

The selected owner is exposed through scheduler snapshots, `/health`, and
cadence evidence rows.

## Maintenance Tick

| Step | Code | Behavior |
| --- | --- | --- |
| Dispatch decision | `scheduler_cadence_dispatch_decision` | Decides whether this owner should run maintenance. |
| Reflection supervision | `run_reflection_tick_once`, maintenance summary | Can coordinate reflection queue posture. |
| Due planned work scan | `_handoff_due_planned_work` | Reads due planned work and records handoff/proposal evidence. |
| Foreground delivery | `_dispatch_due_planned_work_foreground` | Builds scheduler event for due planned work when foreground delivery is admitted. |
| Recurrence/expiry/quiet hours | planned-work helpers | Snoozes, advances, cancels, or delays according to policy. |
| Evidence write | `_record_cadence_evidence` | Writes `AionSchedulerCadenceEvidence(cadence_kind="maintenance")`. |

## Proactive Tick

| Step | Code | Behavior |
| --- | --- | --- |
| Dispatch decision | `scheduler_cadence_dispatch_decision` | Blocks when proactive disabled or owner should not dispatch. |
| Due planned work check | `_run_observer_admitted_proactive_tick` | Prioritizes due planned work before generic proactive outreach. |
| Planned-action observer | `planned_action_observer_snapshot` | Admits foreground only for due planned work or actionable proposal posture. |
| Proactive engine path | `backend/app/proactive/engine.py` and runtime result evidence | Candidate evaluation remains bounded by delivery guards. |
| Evidence write | `_record_cadence_evidence` | Writes `AionSchedulerCadenceEvidence(cadence_kind="proactive")`. |

## Data Read/Write

| Data | Read | Write |
| --- | --- | --- |
| Scheduler evidence | prior cadence state | `AionSchedulerCadenceEvidence` |
| Planned work | due/active `AionPlannedWorkItem` rows | status, snooze, recurrence, cancel/complete/due markers |
| Memory | recent user/proactive history | scheduled event memory through foreground runtime when emitted |
| Proposals | actionable proposal posture | proposal handoff evidence |
| Runtime | foreground delivery of admitted events | normal foreground runtime side effects |

See [Data Model Reference](../data/index.md) for table ownership.

## Failure Points

| Failure Point | Risk | Expected Handling |
| --- | --- | --- |
| Wrong cadence owner | Duplicate or missing ticks | Health/snapshot owner fields and dispatch decisions expose posture. |
| Proactive disabled | Unwanted outreach or false readiness | Proactive tick returns no-op posture. |
| Quiet hours | Interruptive due-work delivery | Planned work can be snoozed/delayed. |
| Due work expired | Stale foreground event | Expired items are cancelled/advanced rather than delivered. |
| Generic proactive scan | Scheduler wakes runtime without a due/actionable reason | Planned-action observer blocks empty scans. |
| Delivery/runtime failure | Foreground event fails | Summary/evidence tracks failures and blocked posture. |

## Tests

| Test File | Coverage |
| --- | --- |
| `backend/tests/test_scheduler_worker.py` | Reflection ticks, maintenance ticks, due planned work handoff/foreground dispatch, quiet hours, recurrence, externalized mode, cadence evidence, proactive observer admission/blocking, live proactive policy snapshots |
| `backend/tests/test_planned_action_observer.py` | Observer empty/noop posture, due planned work priority, actionable proposal posture |
| `backend/tests/test_runtime_pipeline.py` | Proactive delivery/anti-spam, due planned work foreground delivery, passive-active boundary scenarios |
| `backend/tests/test_api_routes.py` | Health exposure for scheduler/proactive/attention evidence |

## Related Docs

- [Pipeline Registry](index.md)
- [Foreground Runtime Pipeline](foreground-runtime.md)
- [Data Model Reference](../data/index.md)
- [Runtime Ops Runbook](../operations/runtime-ops-runbook.md)
- [Proactive System](../architecture/23_proactive_system.md)

## Known Gaps

- No sequence diagram exists for maintenance/proactive tick branching.
- Cadence evidence rows do not yet carry machine-readable pipeline IDs.
- External scheduler provider/runner setup is documented in ops context, not
  generated from code.
