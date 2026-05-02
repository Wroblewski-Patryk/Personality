# Data Model Reference

Last updated: 2026-05-03

This reference is grounded in:

- `backend/app/memory/models.py`
- `backend/migrations/versions/`
- `backend/app/memory/repository.py`
- `backend/tests/test_memory_repository.py`
- `backend/tests/test_schema_baseline.py`

It maps persistent state to features, repository ownership, migrations, and
tests. It is not a generated ERD and does not document every column. If a
relationship is not encoded in the inspected model file, this reference avoids
presenting it as a database-level constraint.

## Ownership Rules

- ORM table definitions live in `backend/app/memory/models.py`.
- Schema migrations live in `backend/migrations/versions/`.
- Runtime data access should flow through `MemoryRepository` in
  `backend/app/memory/repository.py`.
- Alembic migrations are the production schema path.
- `MemoryRepository.create_tables()` remains a compatibility/bootstrap path and
  must not be treated as the only schema proof.
- Data changes require both migration/startup compatibility awareness and test
  evidence, following the learning-journal guardrail for schema work.

## Model And Table Map

| Model | Table | Responsibility | Main Repository Ownership | Used By | Tests |
| --- | --- | --- | --- | --- | --- |
| `AionMemory` | `aion_memory` | Episodic memory, event summaries, transcript projection source, affective/action payload history | `write_episode`, `get_recent_for_user`, `get_recent_episodic_memory`, `get_recent_chat_transcript_for_user`, transcript projection helpers | Runtime, app chat, learned-state overview, reflection, proactive | `test_memory_repository.py`, `test_runtime_pipeline.py`, `test_api_routes.py` |
| `AionSemanticEmbedding` | `aion_semantic_embedding` | Semantic/retrieval materialization for memory, conclusions, and selected relation sources | `upsert_semantic_embedding`, `get_semantic_embeddings`, `query_semantic_similarity`, `get_hybrid_memory_bundle` | Retrieval and memory context, OpenAI/local embedding paths | `test_memory_repository.py`, `test_embedding_strategy.py`, `test_schema_baseline.py` |
| `AionProfile` | `aion_profile` | User language, UI language, UTC offset, Telegram identity/link fields | `get_user_profile`, `set_user_profile_language`, `set_user_profile_ui_language`, `set_user_profile_utc_offset`, Telegram profile/link methods | Auth/session settings, Telegram linking, runtime identity/language, app settings | `test_memory_repository.py`, `test_api_routes.py`, `test_schema_baseline.py` |
| `AionConclusion` | `aion_conclusion` | Scoped durable conclusions and runtime preferences | `upsert_conclusion`, `get_user_conclusions`, `get_conclusions_for_layer`, `get_user_runtime_preferences` | Reflection, settings, tools preferences, runtime context, proactive opt-in | `test_memory_repository.py`, `test_reflection_worker.py`, `test_runtime_pipeline.py` |
| `AionAuthUser` | `aion_auth_user` | First-party app user account | `get_auth_user_by_id`, `get_auth_user_by_email`, `create_auth_user`, `update_auth_user` | App auth/session, settings, reset | `test_api_routes.py`, `test_memory_repository.py`, `test_schema_baseline.py` |
| `AionAuthSession` | `aion_auth_session` | First-party app session token state | `create_auth_session`, `get_auth_session_by_token_hash`, `revoke_auth_session`, `touch_auth_session` | App auth/session, reset | `test_api_routes.py`, `test_memory_repository.py`, `test_schema_baseline.py` |
| `AionRelation` | `aion_relation` | Durable relation and communication-boundary truth with scoped uniqueness | `upsert_relation`, `get_user_relations`, relation serialization/revalidation, communication boundary backfill | Communication boundary, expression preferences, proactive, reflection | `test_memory_repository.py`, `test_communication_boundary.py`, `test_reflection_worker.py` |
| `AionTheta` | `aion_theta` | Support/analysis/execution bias state | `get_user_theta`, `upsert_theta` | Runtime motivation/personality overview | `test_memory_repository.py`, runtime tests |
| `AionGoal` | `aion_goal` | User goals | `get_active_goals`, `upsert_active_goal` | Context, motivation, planning, reflection, learned-state overview | `test_memory_repository.py`, `test_context_agent.py`, `test_planning_agent.py` |
| `AionTask` | `aion_task` | User tasks and goal-linked work | `get_active_tasks`, `upsert_active_task`, `update_task_status` | Context, motivation, planning, action, learned-state overview | `test_memory_repository.py`, `test_goal_task_signals.py`, planning/action tests |
| `AionPlannedWorkItem` | `aion_planned_work_item` | Time-aware planned work, recurrence, due-state, and foreground handoff | `get_active_planned_work`, `get_due_planned_work`, `upsert_planned_work_item`, snooze/reschedule/cancel/complete/advance methods | Scheduler/proactive cadence, planned-action observer, foreground delivery | `test_memory_repository.py`, `test_planned_action_observer.py`, `test_scheduler_worker.py` |
| `AionGoalProgress` | `aion_goal_progress` | Goal progress snapshots | `get_recent_goal_progress`, `append_goal_progress_snapshot` | Reflection, runtime preferences, personality/learned-state overview | `test_memory_repository.py`, `test_reflection_worker.py` |
| `AionGoalMilestone` | `aion_goal_milestone` | Active goal milestone state | `get_active_goal_milestones`, `sync_goal_milestone` | Reflection, context, planning, learned-state overview | `test_memory_repository.py`, `test_reflection_worker.py` |
| `AionGoalMilestoneHistory` | `aion_goal_milestone_history` | Historical milestone evidence | `get_recent_goal_milestone_history`, `append_goal_milestone_history` | Reflection, runtime preferences, learned-state overview | `test_memory_repository.py`, `test_reflection_worker.py` |
| `AionAttentionTurn` | `aion_attention_turn` | Durable attention inbox and conversation turn assembly | `get_attention_turn`, `upsert_attention_turn`, `get_attention_turn_stats`, `cleanup_attention_turns` | External event ingress, Telegram/durable inbox, attention health | `test_memory_repository.py`, `test_api_routes.py`, attention/runtime tests |
| `AionReflectionTask` | `aion_reflection_task` | Deferred reflection queue | `enqueue_reflection_task`, `get_pending_reflection_tasks`, mark processing/completed/failed, `get_reflection_task_stats` | Runtime post-followups, reflection worker, health/supervision | `test_memory_repository.py`, `test_reflection_worker.py`, `test_reflection_supervision_policy.py` |
| `AionSchedulerCadenceEvidence` | `aion_scheduler_cadence_evidence` | Scheduler cadence evidence for maintenance/proactive ownership | `upsert_scheduler_cadence_evidence`, `get_scheduler_cadence_evidence` | Scheduler/proactive health, external cadence owner policy | `test_memory_repository.py`, `test_scheduler_worker.py`, `test_api_routes.py` |
| `AionSubconsciousProposal` | `aion_subconscious_proposal` | Subconscious proposals and bounded autonomous research/action decisions | `upsert_subconscious_proposal`, `get_pending_subconscious_proposals`, `resolve_subconscious_proposal` | Runtime post-graph followups, subconscious proposals, planned work/action governance | `test_memory_repository.py`, `test_runtime_pipeline.py`, reflection/proactive tests |

## Unique Constraints

Verified in `backend/app/memory/models.py`.

| Table | Constraint | Purpose |
| --- | --- | --- |
| `aion_semantic_embedding` | `uq_aion_semantic_embedding_source` on `user_id`, `source_kind`, `source_id` | One embedding materialization per user/source identity |
| `aion_conclusion` | `uq_aion_conclusion_user_kind_scope` on `user_id`, `kind`, `scope_type`, `scope_key` | One conclusion per user/kind/scope |
| `aion_auth_session` | `uq_aion_auth_session_token_hash` on `session_token_hash` | Session token hash uniqueness |
| `aion_relation` | `uq_aion_relation_user_type_scope` on `user_id`, `relation_type`, `scope_type`, `scope_key` | One durable relation per user/type/scope |
| `aion_attention_turn` | `uq_aion_attention_turn_user_conversation` on `user_id`, `conversation_key` | One active attention turn per user/conversation |
| `aion_reflection_task` | `uq_aion_reflection_task_event_id` on `event_id` | One reflection task per event |
| `aion_scheduler_cadence_evidence` | `uq_aion_scheduler_cadence_evidence_kind` on `cadence_kind` | One cadence evidence row per cadence kind |

## Migration Timeline

Verified from `backend/migrations/versions/`.

| Revision File | Purpose From Filename | Data Areas |
| --- | --- | --- |
| `20260416_0001_schema_baseline.py` | Initial schema baseline | Core memory/profile/conclusion/theta/goal/task/progress/milestone tables |
| `20260417_0002_add_aion_memory_payload.py` | Add structured memory payload | `aion_memory` |
| `20260419_0003_add_conclusion_scope_columns.py` | Add conclusion scope columns | `aion_conclusion` |
| `20260419_0004_add_pgvector_semantic_embedding_scaffold.py` | Add semantic embedding scaffold | `aion_semantic_embedding` |
| `20260419_0005_add_relation_table.py` | Add relation table | `aion_relation` |
| `20260422_0006_add_attention_and_subconscious_tables.py` | Add attention and subconscious proposal tables | `aion_attention_turn`, `aion_subconscious_proposal` |
| `20260423_0007_add_scheduler_cadence_evidence_table.py` | Add scheduler cadence evidence table | `aion_scheduler_cadence_evidence` |
| `20260424_0008_add_planned_work_table.py` | Add planned work table | `aion_planned_work_item` |
| `20260425_0009_add_auth_user_and_session_tables.py` | Add auth user/session tables | `aion_auth_user`, `aion_auth_session` |
| `20260425_0010_add_telegram_link_fields_to_profile.py` | Add Telegram link fields to profile | `aion_profile` |
| `20260425_0011_add_ui_language_to_profile.py` | Add UI language to profile | `aion_profile` |
| `20260426_0012_add_utc_offset_to_profile.py` | Add UTC offset to profile | `aion_profile` |

Current latest revision recorded in project/release context: `20260426_0012`.

## Repository Capability Groups

`MemoryRepository` is intentionally broad. Use these groups when finding the
right persistence owner.

| Capability Group | Representative Methods | Main Tables |
| --- | --- | --- |
| Schema/bootstrap | `create_tables` | All ORM tables via metadata |
| Identity merge and legacy Telegram migration | `_reassign_user_rows`, `_merge_profile_identity_state`, `_merge_legacy_telegram_user_state` | Profile, memory, conclusions, relations, embeddings, attention |
| Episodic memory and transcript projection | `write_episode`, `get_recent_for_user`, `get_recent_chat_transcript_for_user`, transcript projection helpers | `aion_memory` |
| Retrieval and embeddings | `upsert_semantic_embedding`, `get_semantic_embeddings`, `query_semantic_similarity`, `get_hybrid_memory_bundle` | `aion_semantic_embedding`, `aion_memory`, `aion_conclusion`, `aion_relation` |
| Profile and app settings | `get_user_profile`, language/UI/UTC setters, Telegram link setters | `aion_profile` |
| Auth/session | auth user/session create/read/update/revoke/touch methods | `aion_auth_user`, `aion_auth_session` |
| Conclusions/preferences | `upsert_conclusion`, `get_user_conclusions`, `get_user_runtime_preferences`, layer helpers | `aion_conclusion` |
| Relations/communication boundary | `upsert_relation`, `get_user_relations`, backfill and revalidation helpers | `aion_relation`, `aion_memory` |
| Goals/tasks/planned work | goal/task/planned-work read/upsert/status/snooze/reschedule/cancel/complete methods | `aion_goal`, `aion_task`, `aion_planned_work_item` |
| Goal progress and milestones | progress and milestone read/write methods | `aion_goal_progress`, `aion_goal_milestone`, `aion_goal_milestone_history` |
| Attention inbox | attention turn get/upsert/stats/cleanup methods | `aion_attention_turn` |
| Reflection queue | reflection enqueue/pending/mark/stats methods | `aion_reflection_task` |
| Scheduler evidence | cadence evidence upsert/read methods | `aion_scheduler_cadence_evidence` |
| Subconscious proposals | proposal upsert/pending/resolve methods | `aion_subconscious_proposal` |
| Runtime reset and cleanup | `reset_user_runtime_data`, `cleanup_runtime_data_preserving_auth`, delete/revoke helpers | Multiple user-scoped runtime tables |

## Feature And Pipeline Usage

| Feature/Pipeline | Main Tables | Reference |
| --- | --- | --- |
| App auth session | `aion_auth_user`, `aion_auth_session`, `aion_profile` | [API Reference](../api/index.md), [Pipeline Registry](../pipelines/index.md#app-auth-session) |
| Profile settings | `aion_profile`, `aion_conclusion`, `aion_auth_user` | [API Reference](../api/index.md), [Pipeline Registry](../pipelines/index.md#profile-settings) |
| App chat turn | `aion_memory`, `aion_profile`, `aion_conclusion`, `aion_relation`, `aion_reflection_task` | [Pipeline Registry](../pipelines/index.md#app-chat-turn) |
| External event ingress | `aion_attention_turn`, `aion_memory`, `aion_reflection_task` | [Pipeline Registry](../pipelines/index.md#external-event-ingress) |
| Learned state overview | `aion_memory`, `aion_profile`, `aion_conclusion`, `aion_relation`, `aion_theta`, goals/tasks/progress/milestones | [Pipeline Registry](../pipelines/index.md#learned-state-overview) |
| Tools overview/preferences | `aion_conclusion`, `aion_profile` | [Pipeline Registry](../pipelines/index.md#tools-overview) |
| Telegram linking/transport | `aion_profile`, `aion_attention_turn`, `aion_memory` | [Pipeline Registry](../pipelines/index.md#telegram-linking-and-transport) |
| Deferred reflection | `aion_reflection_task`, `aion_memory`, `aion_conclusion`, `aion_relation`, goal/progress/milestone/proposal tables | [Pipeline Registry](../pipelines/index.md#deferred-reflection) |
| Scheduler/proactive cadence | `aion_scheduler_cadence_evidence`, `aion_planned_work_item`, `aion_subconscious_proposal`, `aion_memory` | [Pipeline Registry](../pipelines/index.md#scheduler-and-proactive-cadence) |
| Retrieval and memory context | `aion_semantic_embedding`, `aion_memory`, `aion_conclusion`, selected relations | [Pipeline Registry](../pipelines/index.md#retrieval-and-memory-context) |
| User data reset | Multiple user-scoped runtime tables, auth sessions, preserved profile/auth categories | [Pipeline Registry](../pipelines/index.md#user-data-reset) |

## Validation Ownership

| Test File | Data Coverage |
| --- | --- |
| `backend/tests/test_schema_baseline.py` | Expected table inventory, named unique constraints, structured payload column, Alembic head schema checks, attention/proposal contracts, UI language profile field |
| `backend/tests/test_memory_repository.py` | Repository behavior across memory payloads, attention, scheduler evidence, embeddings, relations, proposals, conclusions, goals/tasks, planned work, auth/profile/reset/transcript/proactive behavior |
| `backend/tests/test_api_routes.py` | Route-level persistence behavior for auth, settings, reset, chat, tools, personality overview, debug/event flows |
| `backend/tests/test_runtime_pipeline.py` | Runtime persistence and reflection/proposal integration paths |
| `backend/tests/test_reflection_worker.py` | Reflection queue and output persistence |
| `backend/tests/test_scheduler_worker.py` | Scheduler/proactive cadence persistence and evidence |

## Change Checklist

For any data-affecting change:

1. Update `backend/app/memory/models.py`.
2. Add or update an Alembic migration in `backend/migrations/versions/`.
3. Update `MemoryRepository` instead of adding ad hoc SQL in feature code.
4. Add focused repository/schema tests.
5. Run a relevant schema validation path. For broad schema changes, include:
   - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py; Pop-Location`
   - targeted repository/API/runtime tests for the changed behavior
6. Update this data reference, the traceability matrix, and any affected
   pipeline/module docs.
7. If startup compatibility is affected, update operations docs and project
   context.

## Known Data Documentation Gaps

- No generated ERD exists.
- No column-by-column model reference exists yet.
- Repository methods are grouped by responsibility, not exhaustively documented
  one by one.
- Some relationships are logical/application-level rather than encoded as
  inspected database foreign keys; this reference does not infer unverified
  database constraints.
- Migration-to-column mapping is currently filename-level and should be deepened
  only when schema work requires it.
