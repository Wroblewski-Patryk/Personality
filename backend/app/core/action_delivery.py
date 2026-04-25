from __future__ import annotations

from app.core.contracts import (
    ActionDeliveryExecutionEnvelope,
    ActionDeliveryConnectorIntent,
    CalendarSchedulingIntentDomainIntent,
    ConnectedDriveAccessDomainIntent,
    ConnectorCapabilityDiscoveryDomainIntent,
    ConnectorPermissionGateOutput,
    ExternalTaskSyncDomainIntent,
    PlanOutput,
)


def build_action_delivery_execution_envelope(plan: PlanOutput | None) -> ActionDeliveryExecutionEnvelope:
    if plan is None:
        return ActionDeliveryExecutionEnvelope()

    connector_permission_gates = [
        gate.model_copy(deep=True)
        for gate in plan.connector_permission_gates
    ]
    connector_intents: list[ActionDeliveryConnectorIntent] = []
    for intent in plan.domain_intents:
        gate = _matching_connector_permission_gate(
            connector_permission_gates=connector_permission_gates,
            intent=intent,
        )
        connector_snapshot = _connector_intent_snapshot(intent=intent, gate=gate)
        if connector_snapshot is not None:
            connector_intents.append(connector_snapshot)

    return ActionDeliveryExecutionEnvelope(
        connector_safe=bool(connector_intents or connector_permission_gates),
        connector_intents=connector_intents,
        connector_permission_gates=connector_permission_gates,
    )


def action_delivery_envelope_matches_plan(
    *,
    envelope: ActionDeliveryExecutionEnvelope,
    plan: PlanOutput | None,
) -> bool:
    expected = build_action_delivery_execution_envelope(plan)
    return envelope.model_dump(mode="json") == expected.model_dump(mode="json")


def summarize_action_delivery_envelope(envelope: ActionDeliveryExecutionEnvelope) -> str:
    if not envelope.connector_safe:
        return ""
    return (
        f"connector_safe={envelope.connector_safe} "
        f"connector_intents={len(envelope.connector_intents)} "
        f"permission_gates={len(envelope.connector_permission_gates)}"
    )


def _matching_connector_permission_gate(
    *,
    connector_permission_gates: list[ConnectorPermissionGateOutput],
    intent: object,
) -> ConnectorPermissionGateOutput | None:
    if isinstance(intent, CalendarSchedulingIntentDomainIntent):
        connector_kind = "calendar"
        provider_hint = intent.provider_hint
        operation = intent.operation
    elif isinstance(intent, ExternalTaskSyncDomainIntent):
        connector_kind = "task_system"
        provider_hint = intent.provider_hint
        operation = intent.operation
    elif isinstance(intent, ConnectedDriveAccessDomainIntent):
        connector_kind = "cloud_drive"
        provider_hint = intent.provider_hint
        operation = intent.operation
    elif isinstance(intent, ConnectorCapabilityDiscoveryDomainIntent):
        connector_kind = intent.connector_kind
        provider_hint = intent.provider_hint
        operation = f"discover_{intent.requested_capability}"
    else:
        return None

    for gate in connector_permission_gates:
        if gate.connector_kind != connector_kind:
            continue
        if str(gate.provider_hint or "") != str(provider_hint or ""):
            continue
        if gate.operation != operation:
            continue
        return gate
    return None


def _connector_intent_snapshot(
    *,
    intent: object,
    gate: ConnectorPermissionGateOutput | None,
) -> ActionDeliveryConnectorIntent | None:
    if isinstance(intent, CalendarSchedulingIntentDomainIntent):
        return ActionDeliveryConnectorIntent(
            connector_kind="calendar",
            provider_hint=intent.provider_hint,
            operation=intent.operation,
            mode=intent.mode,
            allowed=bool(gate.allowed) if gate is not None else False,
            requires_confirmation=bool(gate.requires_confirmation) if gate is not None else False,
            reason=str(gate.reason) if gate is not None else "explicit_user_authorization_required",
        )
    if isinstance(intent, ExternalTaskSyncDomainIntent):
        return ActionDeliveryConnectorIntent(
            connector_kind="task_system",
            provider_hint=intent.provider_hint,
            operation=intent.operation,
            mode=intent.mode,
            allowed=bool(gate.allowed) if gate is not None else False,
            requires_confirmation=bool(gate.requires_confirmation) if gate is not None else False,
            reason=str(gate.reason) if gate is not None else "explicit_user_authorization_required",
        )
    if isinstance(intent, ConnectedDriveAccessDomainIntent):
        return ActionDeliveryConnectorIntent(
            connector_kind="cloud_drive",
            provider_hint=intent.provider_hint,
            operation=intent.operation,
            mode=intent.mode,
            allowed=bool(gate.allowed) if gate is not None else False,
            requires_confirmation=bool(gate.requires_confirmation) if gate is not None else False,
            reason=str(gate.reason) if gate is not None else "explicit_user_authorization_required",
        )
    if isinstance(intent, ConnectorCapabilityDiscoveryDomainIntent):
        return ActionDeliveryConnectorIntent(
            connector_kind=intent.connector_kind,
            provider_hint=intent.provider_hint,
            operation=f"discover_{intent.requested_capability}",
            mode=intent.mode,
            allowed=bool(gate.allowed) if gate is not None else False,
            requires_confirmation=bool(gate.requires_confirmation) if gate is not None else False,
            reason=str(gate.reason) if gate is not None else "proposal_only_no_external_access",
        )
    return None
