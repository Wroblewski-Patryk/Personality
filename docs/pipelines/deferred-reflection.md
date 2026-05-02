# Deferred Reflection Pipeline

Last updated: 2026-05-03

Grounded in:

- `backend/app/reflection/worker.py`
- `backend/app/reflection/adaptive_signals.py`
- `backend/app/reflection/affective_signals.py`
- `backend/app/reflection/goal_conclusions.py`
- `backend/app/reflection/relation_signals.py`
- `backend/app/reflection/proposals.py`
- `backend/app/core/reflection_supervision_policy.py`
- `backend/app/memory/repository.py`
- `backend/tests/test_reflection_worker.py`
- `backend/tests/test_reflection_supervision_policy.py`

## Purpose

Deferred reflection turns recent episodic memory into slower durable state:
conclusions, relations, theta bias, goal progress, milestones, and subconscious
proposals. It is background consolidation, not a foreground action path.

## Trigger Paths

| Trigger | Code | Notes |
| --- | --- | --- |
| Foreground runtime follow-up | `RuntimeOrchestrator._run_post_graph_followups` | Enqueues `AionReflectionTask` after a foreground run when reflection is enabled. |
| Worker enqueue | `ReflectionWorker.enqueue` | Persists a durable task and can dispatch it into the in-process queue. |
| External queue drain | `backend/scripts/run_reflection_queue_once.*` | Processes pending tasks without relying on in-process worker ownership. |
| Startup recovery | `ReflectionWorker.start` and pending scheduling | Recovers eligible pending tasks when worker starts. |

## Queue Lifecycle

1. Runtime or caller creates a reflection task through
   `MemoryRepository.enqueue_reflection_task`.
2. Worker reads ready tasks with `get_pending_reflection_tasks`.
3. Worker marks a task processing with `mark_reflection_task_processing`.
4. `reflect_user(user_id, event_id)` reads recent memory and derives outputs.
5. Successful processing marks the task completed with
   `mark_reflection_task_completed`.
6. Failures mark task failed with `mark_reflection_task_failed`.
7. Retry behavior respects max attempts and retry backoff.

## Signal Writers

| Signal Family | Code | Writes |
| --- | --- | --- |
| Explicit/adaptive conclusions | `worker._derive_conclusions`, `adaptive_signals.py` | `AionConclusion`, `AionTheta` |
| Affective conclusions | `affective_signals.py` | `AionConclusion` kinds such as affective support pattern/sensitivity |
| Goal conclusions and progress | `goal_conclusions.py` | `AionConclusion`, `AionGoalProgress`, `AionGoalMilestone`, `AionGoalMilestoneHistory` |
| Relations and communication boundary | `relation_signals.py` | `AionRelation` |
| Subconscious proposals | `proposals.py` | `AionSubconsciousProposal` |

## Data Read/Write

| Data | Read | Write |
| --- | --- | --- |
| Episodic memory | recent user memory for signal derivation | no direct mutation |
| Reflection queue | pending task state | processing/completed/failed status |
| Conclusions | current preference/conclusion state | scoped durable conclusions |
| Relations | current relation state and evidence | durable relation updates |
| Goals/tasks/progress/milestones | active goal/task and history state | progress snapshots, milestones, milestone history |
| Theta | current bias state | support/analysis/execution bias |
| Proposals | current proposal posture | pending or re-entered subconscious proposals |

See [Data Model Reference](../data/index.md) for table ownership.

## Failure Points

| Failure Point | Risk | Expected Handling |
| --- | --- | --- |
| Queue full | In-process dispatch cannot accept task | Durable task remains stored for later drain. |
| Retry backoff | Failed task reruns too early | `_is_task_ready` and retry backoff guard readiness. |
| Exhausted attempts | Repeated failure loops forever | Worker skips failed tasks past max attempts. |
| Weak evidence | Reflection overfits one noisy event | Signal modules require consistent or explicit evidence before writes. |
| Scope drift | Goal-scoped facts leak into global state | `reflection_scope_policy` resolves conclusion/relation scope. |
| Proposal/action confusion | Background reflection performs side effects | Reflection writes proposals; foreground/action boundary decides execution. |

## Tests

| Test File | Coverage |
| --- | --- |
| `backend/tests/test_reflection_worker.py` | Preference consolidation, structured payload priority, proposals, adaptive role/style/theta, relations, behavior feedback, affective patterns, goal/milestone/progress signals, enqueue/run-pending/retry behavior |
| `backend/tests/test_reflection_supervision_policy.py` | Supervision policy states and recovery posture |
| `backend/tests/test_memory_repository.py` | Reflection task stats and related persistence contracts |
| `backend/tests/test_runtime_pipeline.py` | Runtime reflection enqueue and deferred boundary behavior |

## Related Docs

- [Pipeline Registry](index.md)
- [Foreground Runtime Pipeline](foreground-runtime.md)
- [Data Model Reference](../data/index.md)
- [Traceability Matrix](../architecture/traceability-matrix.md)
- [Memory System](../architecture/04_memory_system.md)
- [Relation System](../architecture/22_relation_system.md)

## Known Gaps

- No generated reflection signal catalog exists.
- No sequence diagram exists for queue states and retry transitions.
- Test-to-signal ownership is inferred from test names and assertions, not a
  machine-readable signal ID.
