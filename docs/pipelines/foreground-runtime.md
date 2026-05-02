# Foreground Runtime Pipeline

Last updated: 2026-05-03

This is the dedicated reference for the foreground AION runtime pipeline. It is
grounded in:

- `backend/app/core/runtime.py`
- `backend/app/core/runtime_graph.py`
- `backend/app/core/contracts.py`
- `backend/tests/test_runtime_pipeline.py`
- `backend/tests/test_graph_stage_adapters.py`
- `backend/tests/test_graph_state_contract.py`

## Purpose

The foreground runtime turns a normalized event into one canonical assistant
response plus explicit action, memory, debug, and follow-up state. It is the
main path behind app chat, generic event ingress, debug event ingress, Telegram
handoff, and due planned-work foreground delivery.

## Trigger Paths

| Trigger | Route/Caller | Notes |
| --- | --- | --- |
| App chat | `POST /app/chat/message` | Authenticated web chat wraps text with the app user id and calls event handling without debug payloads. |
| Generic event | `POST /event` | External/API ingress; debug query compatibility can delegate to internal debug when enabled. |
| Debug event | `POST /event/debug`, `POST /internal/event/debug` | Runs the same foreground path with debug/system/incident evidence according to policy. |
| Telegram/durable inbox | Attention coordination and transport paths | Telegram identity and attention ownership can hand assembled turns into the foreground path. |
| Due planned work | Scheduler/planned action observer | Planned work can be delivered through the same foreground path when admitted. |

## Runtime Graph Stage Order

Verified in `backend/app/core/runtime_graph.py`.

```text
START
  -> perception
  -> affective_assessment
  -> context
  -> motivation
  -> role
  -> planning
  -> expression
  -> action
END
```

The broader architecture includes memory and reflection after expression/action.
In the current implementation, memory persistence, reflection enqueue, proposal
resolution, and runtime-state refresh are handled by `RuntimeOrchestrator`
around and after the graph.

## Stage Contracts

| Stage | Primary Code | Contract Output | Responsibility |
| --- | --- | --- | --- |
| Event seed | `RuntimeOrchestrator.run`, `GraphRuntimeState` seed builders | `Event`, graph seed | Normalize runtime inputs, load memory/state, seed graph helper context |
| Perception | `backend/app/agents/perception.py` | `PerceptionOutput` | Interpret source/text/language/request signals and behavior feedback evidence |
| Affective assessment | `backend/app/affective/assessor.py` | `AffectiveAssessmentOutput` | Classify affective label/intensity/support posture with fallback behavior |
| Context | `backend/app/agents/context.py` | `ContextOutput`, `IdentityOutput` | Build memory, identity, preference, goal/task, relation, and capability context |
| Motivation | `backend/app/motivation/engine.py` | `MotivationOutput` | Choose motivation mode and urgency/support/execution posture |
| Role | `backend/app/agents/role.py` | `RoleOutput` | Select runtime role under role/skill boundary policies |
| Planning | `backend/app/agents/planning.py` | `PlanOutput` | Produce response plan and explicit domain/action intents |
| Expression | `backend/app/expression/generator.py` | `ExpressionOutput`, `ActionDelivery` handoff | Produce canonical assistant text and delivery envelope |
| Action | `backend/app/core/action.py` | `ActionResult` | Execute approved side effects and delivery actions at the action boundary |
| Result assembly | `RuntimeOrchestrator.run` | `RuntimeResult` | Assemble final runtime result and optional debug surfaces |

## Data Reads

Foreground runtime reads user-scoped state through `MemoryRepository` before or
during graph execution:

- recent episodic memory and transcript-relevant memory
- hybrid retrieval bundle and semantic embeddings when enabled
- profile language, UI/local time, Telegram identity, and auth-linked state
- runtime preferences and scoped conclusions
- durable relations and communication-boundary truth
- theta bias
- active goals, tasks, planned work, progress, and milestones
- pending subconscious proposals

See [Data Model Reference](../data/index.md) for table ownership.

## Data Writes And Side Effects

| Boundary | Owner | Writes/Side Effects |
| --- | --- | --- |
| Action boundary | `backend/app/core/action.py`, integration clients, delivery router | Domain intents, connector calls, delivery attempts, tool-grounded learning capture |
| Memory persistence | `RuntimeOrchestrator.run`, `MemoryRepository.write_episode` | Episodic memory with event/reply/action/runtime payload |
| Reflection enqueue | `RuntimeOrchestrator._run_post_graph_followups`, `enqueue_reflection_task` | `AionReflectionTask` when reflection is enabled/required |
| Subconscious proposal resolution | `RuntimeOrchestrator._run_post_graph_followups` | Proposal decisions after foreground handoff |
| Runtime state refresh | `RuntimeOrchestrator._run_post_graph_followups` | Fresh goals/tasks/preferences after domain writes |

Side effects belong in action or integration layers. Reasoning stages should
produce intents and diagnostics, not direct external mutations.

## Debug And Observability

The runtime emits or can expose:

- structured stage logs
- stage timing/debug summaries
- `RuntimeResult`
- `RuntimeSystemDebugOutput`
- optional incident evidence through debug/observability policy surfaces
- health-policy snapshots outside the foreground run

Failure logs are expected to preserve the stage where a failure happened.

## Failure Points

| Area | Failure Mode | Expected Handling |
| --- | --- | --- |
| Event/user identity | Missing or shared user scope | Route/event normalization and identity fallback rules must keep precedence explicit |
| Memory load | Repository read failure or stale/missing state | Runtime should fail visibly or degrade only through documented fallback paths |
| Graph helper context | Auxiliary state dropped between graph nodes | Each node must re-emit required helper keys; see learning journal guardrail |
| Affective classifier | Provider missing/invalid output | Deterministic fallback remains valid and logged |
| Planning/action boundary | Reasoning stage tries to mutate state directly | Must stay as domain intent until action/repository owner executes |
| Connector/provider | Provider missing, permission blocked, or external failure | Action result and delivery envelope should reflect blocked/failed posture |
| Memory write | Episodic persistence failure | Stage failure log and tests cover fail path; runtime must not silently claim durable memory |
| Reflection enqueue | Queue unavailable or worker mode mismatch | Post-graph followup records enqueue result/supervision posture |
| Transcript projection | Internal/system rows shown as user-authored turns | Repository projection helpers protect transcript truth |

## Tests

| Test File | Coverage |
| --- | --- |
| `backend/tests/test_runtime_pipeline.py` | End-to-end foreground behavior, memory/state loading, graph invocation, action delivery, logs, empathy, scoped memory, goals/tasks, proactive/planned work, connector/tool behavior, transcript truth, behavior scenarios |
| `backend/tests/test_graph_stage_adapters.py` | Stage adapter execution, required state validation, action delivery handoff, connector-safe expression/action envelope |
| `backend/tests/test_graph_state_contract.py` | Graph state seed/defaults, runtime-result conversion, connector-safe action delivery, required completed state, attention/proposal/capability contracts |
| `backend/tests/test_expression_agent.py` | Expression contract and communication preference behavior |
| `backend/tests/test_planning_agent.py` | Planning/domain intent behavior |
| `backend/tests/test_action_executor.py` | Action boundary and side-effect execution behavior |

## Related Docs

- [Pipeline Registry](index.md)
- [API Reference](../api/index.md)
- [Data Model Reference](../data/index.md)
- [Traceability Matrix](../architecture/traceability-matrix.md)
- [Runtime Flow](../architecture/15_runtime_flow.md)
- [Agent Contracts](../architecture/16_agent_contracts.md)
- [Runtime Reality](../implementation/runtime-reality.md)
- [Runtime Behavior Testing](../architecture/29_runtime_behavior_testing.md)

## Known Gaps

- No rendered sequence diagram exists yet.
- Stage input/output details are summarized; a generated contract table from
  `backend/app/core/contracts.py` does not exist.
- Some trigger paths, especially Telegram/durable inbox and due planned work,
  need their own dedicated pipeline docs.
- Test-to-stage coverage is inferred from test names and assertions, not stable
  machine-readable pipeline IDs.
