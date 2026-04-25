from datetime import datetime, timezone

import pytest

from app.core.contracts import (
    ActionResult,
    CalendarSchedulingIntentDomainIntent,
    ConnectorPermissionGateOutput,
    ContextOutput,
    Event,
    EventMeta,
    ExpressionOutput,
    IdentityOutput,
    MemoryRecord,
    MotivationOutput,
    NoopDomainIntent,
    PerceptionOutput,
    PlanOutput,
    RoleOutput,
    RuntimeResult,
)
from app.core.graph_state import (
    AttentionInboxItemState,
    ExternalConnectorCapabilityState,
    ExternalConnectorPermissionGateState,
    GRAPH_FOREGROUND_STAGE_ORDER,
    GRAPH_STATE_SCHEMA_VERSION,
    ProposalHandoffState,
    SubconsciousProposalState,
    TurnAssemblyState,
    build_graph_state_seed,
    graph_state_missing_runtime_fields,
    graph_state_to_runtime_result,
    runtime_result_to_graph_state,
)


def _event() -> Event:
    return Event(
        event_id="evt-graph-1",
        source="api",
        subsource="event_endpoint",
        timestamp=datetime.now(timezone.utc),
        payload={"text": "hello graph boundary"},
        meta=EventMeta(user_id="u-graph", trace_id="t-graph-1"),
    )


def _runtime_result() -> RuntimeResult:
    event = _event()
    return RuntimeResult(
        event=event,
        identity=IdentityOutput(
            mission="Help the user move forward.",
            values=["clarity"],
            behavioral_style=["direct", "supportive"],
            boundaries=["no hidden side effects"],
            summary="Direct and supportive help.",
        ),
        active_goals=[
            {
                "id": 11,
                "name": "Ship MVP",
                "description": "Deliver MVP flow",
                "priority": "high",
                "status": "active",
                "goal_type": "operational",
            }
        ],
        active_tasks=[
            {
                "id": 21,
                "goal_id": 11,
                "name": "Write migration contract",
                "description": "Define graph boundary",
                "priority": "medium",
                "status": "in_progress",
            }
        ],
        perception=PerceptionOutput(
            event_type="statement",
            topic="runtime",
            topic_tags=["runtime", "graph"],
            intent="share_information",
            language="en",
            language_source="default",
            language_confidence=0.7,
            ambiguity=0.1,
            initial_salience=0.6,
        ),
        context=ContextOutput(
            summary="User asked about runtime graph migration.",
            related_goals=["ship mvp"],
            related_tags=["runtime", "graph"],
            risk_level=0.2,
        ),
        motivation=MotivationOutput(
            importance=0.73,
            urgency=0.41,
            valence=0.12,
            arousal=0.44,
            mode="respond",
        ),
        role=RoleOutput(selected="advisor", confidence=0.77),
        plan=PlanOutput(
            goal="clarify migration boundary",
            steps=["interpret_event", "prepare_response"],
            needs_action=True,
            needs_response=True,
            domain_intents=[NoopDomainIntent()],
        ),
        action_result=ActionResult(
            status="success",
            actions=["api_response"],
            notes="Response returned via API.",
        ),
        expression=ExpressionOutput(
            message="Here is the migration boundary.",
            tone="supportive",
            channel="api",
            language="en",
        ),
        memory_record=MemoryRecord(
            id=31,
            event_id=event.event_id,
            timestamp=datetime.now(timezone.utc),
            summary="event=hello graph boundary; action=success",
            payload={"memory_kind": "continuity"},
            importance=0.73,
        ),
        reflection_triggered=True,
        stage_timings_ms={"total": 210},
        duration_ms=210,
    )


def test_build_graph_state_seed_defaults() -> None:
    state = build_graph_state_seed(_event())

    assert state.schema_version == GRAPH_STATE_SCHEMA_VERSION
    assert state.source_runtime == "python_orchestrator"
    assert state.event.event_id == "evt-graph-1"
    assert state.memory.episodic == []
    assert state.background_adaptive_outputs == {}
    assert state.attention_inbox == []
    assert state.pending_turn is None
    assert state.subconscious_proposals == []
    assert state.proposal_handoffs == []
    assert state.connector_capabilities == []
    assert state.connector_permission_gates == []
    assert GRAPH_FOREGROUND_STAGE_ORDER == (
        "perception",
        "context",
        "motivation",
        "role",
        "planning",
        "expression",
        "action",
    )
    assert "memory_load" not in GRAPH_FOREGROUND_STAGE_ORDER
    assert "memory_persist" not in GRAPH_FOREGROUND_STAGE_ORDER
    assert "reflection_enqueue" not in GRAPH_FOREGROUND_STAGE_ORDER


def test_runtime_result_to_graph_state_maps_orchestrator_contract() -> None:
    graph_state = runtime_result_to_graph_state(_runtime_result())

    assert graph_state.event.event_id == "evt-graph-1"
    assert graph_state.identity is not None
    assert graph_state.active_goals[0]["name"] == "Ship MVP"
    assert graph_state.active_tasks[0]["name"] == "Write migration contract"
    assert graph_state.memory.operational["active_goals"][0]["id"] == 11
    assert graph_state.action_delivery is not None
    assert graph_state.action_delivery.channel == "api"
    assert graph_state.action_delivery.execution_envelope.connector_safe is False
    assert graph_state.action_result is not None
    assert graph_state.action_result.status == "success"
    assert graph_state.background_adaptive_outputs == {}


def test_runtime_result_to_graph_state_builds_connector_safe_action_delivery_envelope() -> None:
    runtime_result = _runtime_result().model_copy(
        update={
            "plan": PlanOutput(
                goal="schedule follow-up",
                steps=["prepare_response"],
                needs_action=True,
                needs_response=True,
                domain_intents=[
                    CalendarSchedulingIntentDomainIntent(
                        operation="create_event",
                        provider_hint="google_calendar",
                        mode="mutate_with_confirmation",
                        title_hint="team sync",
                        time_hint="tomorrow 10:00",
                    )
                ],
                connector_permission_gates=[
                    ConnectorPermissionGateOutput(
                        connector_kind="calendar",
                        provider_hint="google_calendar",
                        operation="create_event",
                        mode="mutate_with_confirmation",
                        requires_opt_in=True,
                        requires_confirmation=True,
                        allowed=False,
                        reason="explicit_user_confirmation_required",
                    )
                ],
            )
        }
    )

    graph_state = runtime_result_to_graph_state(runtime_result)

    assert graph_state.action_delivery is not None
    assert graph_state.action_delivery.execution_envelope.connector_safe is True
    assert len(graph_state.action_delivery.execution_envelope.connector_intents) == 1
    assert len(graph_state.action_delivery.execution_envelope.connector_permission_gates) == 1
    assert graph_state.action_delivery.execution_envelope.connector_intents[0].operation == "create_event"


def test_graph_state_to_runtime_result_roundtrip() -> None:
    runtime_result = _runtime_result()
    graph_state = runtime_result_to_graph_state(runtime_result)
    restored = graph_state_to_runtime_result(graph_state)

    assert restored.event.event_id == runtime_result.event.event_id
    assert restored.identity.summary == runtime_result.identity.summary
    assert restored.plan.goal == runtime_result.plan.goal
    assert restored.action_result.status == runtime_result.action_result.status
    assert restored.active_goals[0].id == 11
    assert restored.duration_ms == runtime_result.duration_ms


def test_graph_state_to_runtime_result_requires_completed_state() -> None:
    state = build_graph_state_seed(_event())

    missing = graph_state_missing_runtime_fields(state)
    assert "identity" in missing
    assert "action_delivery" in missing
    assert "action_result" in missing

    with pytest.raises(ValueError, match="graph state is not complete"):
        graph_state_to_runtime_result(state)


def test_graph_state_supports_attention_inbox_turn_assembly_and_proposal_handoff_contract() -> None:
    state = build_graph_state_seed(_event()).model_copy(
        update={
            "subconscious_proposals": [
                SubconsciousProposalState(
                    proposal_id="prop-1",
                    proposal_type="ask_user",
                    summary="Ask a clarifying question about the blocker scope.",
                    payload={"question": "Which deploy environment is blocked?"},
                    confidence=0.79,
                )
            ],
            "attention_inbox": [
                AttentionInboxItemState(
                    item_id="attn-1",
                    source="subconscious_proposal",
                    conversation_key="telegram:123456",
                    proposal=SubconsciousProposalState(
                        proposal_id="prop-1",
                        proposal_type="ask_user",
                        summary="Ask a clarifying question about the blocker scope.",
                        payload={"question": "Which deploy environment is blocked?"},
                        confidence=0.79,
                    ),
                    status="pending",
                    priority=0.72,
                )
            ],
            "pending_turn": TurnAssemblyState(
                turn_id="turn-1",
                conversation_key="telegram:123456",
                item_ids=["attn-1"],
                assembled_text="Can you clarify which deploy environment is blocked?",
                status="claimed",
                owner="conscious",
                source_item_count=1,
            ),
            "proposal_handoffs": [
                ProposalHandoffState(
                    proposal_id="prop-1",
                    decision="accept",
                    reason="clarification is required before execution",
                )
            ],
        }
    )

    assert state.attention_inbox[0].source == "subconscious_proposal"
    assert state.pending_turn is not None
    assert state.pending_turn.status == "claimed"
    assert state.subconscious_proposals[0].proposal_type == "ask_user"
    assert state.subconscious_proposals[0].status == "pending"
    assert state.subconscious_proposals[0].research_policy == "read_only"
    assert state.proposal_handoffs[0].decision == "accept"


def test_graph_state_supports_connector_capability_and_permission_gate_contracts() -> None:
    state = build_graph_state_seed(_event()).model_copy(
        update={
            "connector_capabilities": [
                ExternalConnectorCapabilityState(
                    connector_kind="calendar",
                    provider_hint="google_calendar",
                    capability="calendar_write",
                    mode="mutate_with_confirmation",
                    requires_opt_in=True,
                    requires_confirmation=True,
                ),
                ExternalConnectorCapabilityState(
                    connector_kind="task_system",
                    provider_hint="clickup",
                    capability="task_sync",
                    mode="suggestion_only",
                    requires_opt_in=True,
                    requires_confirmation=False,
                ),
                ExternalConnectorCapabilityState(
                    connector_kind="cloud_drive",
                    provider_hint="google_drive",
                    capability="file_upload",
                    mode="mutate_with_confirmation",
                    requires_opt_in=True,
                    requires_confirmation=True,
                ),
            ],
            "connector_permission_gates": [
                ExternalConnectorPermissionGateState(
                    connector_kind="calendar",
                    provider_hint="google_calendar",
                    operation="create_event",
                    mode="mutate_with_confirmation",
                    allowed=False,
                    reason="explicit_user_confirmation_required",
                ),
                ExternalConnectorPermissionGateState(
                    connector_kind="task_system",
                    provider_hint="clickup",
                    operation="suggest_sync",
                    mode="suggestion_only",
                    allowed=True,
                    reason="suggestion_or_read_only_allowed",
                ),
                ExternalConnectorPermissionGateState(
                    connector_kind="cloud_drive",
                    provider_hint="google_drive",
                    operation="upload_file",
                    mode="mutate_with_confirmation",
                    allowed=False,
                    reason="explicit_user_confirmation_required",
                ),
            ],
        }
    )

    assert state.connector_capabilities[0].connector_kind == "calendar"
    assert state.connector_capabilities[0].requires_confirmation is True
    assert state.connector_permission_gates[0].operation == "create_event"
    assert state.connector_permission_gates[0].allowed is False
    assert state.connector_permission_gates[1].allowed is True
    assert state.connector_permission_gates[2].connector_kind == "cloud_drive"
    assert state.connector_permission_gates[2].operation == "upload_file"
