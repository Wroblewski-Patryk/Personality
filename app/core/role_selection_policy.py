from __future__ import annotations

from dataclasses import dataclass

from app.core.adaptive_policy import (
    ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN,
    dominant_theta_channel,
    is_role_adaptive_tie_break_turn,
    preferred_role_allowed,
    relation_value,
)
from app.core.contracts import ContextOutput, Event, PerceptionOutput, RoleSelectionEvidenceOutput
from app.utils.language import normalize_for_matching

ANALYSIS_KEYWORDS = {
    "analyze",
    "analysis",
    "review",
    "compare",
    "debug",
    "explain",
    "analiza",
    "przeanalizuj",
    "porownaj",
    "wyjasnij",
    "sprawdz",
    "zaplanuj",
}
EXECUTOR_KEYWORDS = {
    "build",
    "create",
    "write",
    "fix",
    "implement",
    "add",
    "setup",
    "deploy",
    "zbuduj",
    "stworz",
    "napisz",
    "napraw",
    "wdroz",
    "dodaj",
    "skonfiguruj",
    "ustaw",
    "zrob",
}
WORK_PARTNER_EXPLICIT_MARKERS = {
    "work partner",
    "business partner",
    "partner at work",
    "partner for work",
}
PREFERRED_ROLES = {"friend", "analyst", "executor", "mentor", "work_partner"}


@dataclass(frozen=True)
class RoleSelectionDecision:
    selected: str
    confidence: float
    reason: str
    evidence: list[RoleSelectionEvidenceOutput]


def select_role(
    *,
    event: Event,
    perception: PerceptionOutput,
    context: ContextOutput,
    user_preferences: dict | None = None,
    relations: list[dict] | None = None,
    theta: dict | None = None,
) -> RoleSelectionDecision:
    text = str(event.payload.get("text", "")).strip()
    lowered = normalize_for_matching(text)
    affective_label = str(perception.affective.affect_label).strip().lower()
    affective_needs_support = bool(perception.affective.needs_support)
    preferred_role = str((user_preferences or {}).get("preferred_role", "")).strip().lower()
    preferred_role_confidence = float((user_preferences or {}).get("preferred_role_confidence", 0.0) or 0.0)
    collaboration_preference = str((user_preferences or {}).get("collaboration_preference", "")).strip().lower()
    relation_collaboration = relation_value(
        relations=relations or [],
        relation_type="collaboration_dynamic",
        min_confidence=ROLE_COLLABORATION_RELATION_CONFIDENCE_MIN,
    )
    relation_support = relation_value(
        relations=relations or [],
        relation_type="support_intensity_preference",
    )
    is_help_turn = perception.event_type == "question" or perception.intent == "request_help"
    is_general_turn = perception.topic == "general"
    is_role_tie_break_turn = is_role_adaptive_tie_break_turn(
        event_type=perception.event_type,
        intent=perception.intent,
        topic=perception.topic,
    )
    has_active_goal_context = bool(context.related_goals)
    work_partner_explicit = any(marker in lowered for marker in WORK_PARTNER_EXPLICIT_MARKERS)

    if affective_needs_support or affective_label == "support_distress":
        return RoleSelectionDecision(
            selected="friend",
            confidence=0.74,
            reason="affective_support_signal",
            evidence=[
                RoleSelectionEvidenceOutput(
                    signal="affective_support_signal",
                    source="affective",
                    value=affective_label or "support_distress",
                    applied=True,
                    note="support-distress posture overrides lower-priority role tie breaks",
                )
            ],
        )

    if relation_support == "high_support" and perception.event_type == "question":
        return RoleSelectionDecision(
            selected="mentor",
            confidence=0.68,
            reason="support_intensity_relation_question",
            evidence=[
                RoleSelectionEvidenceOutput(
                    signal="support_intensity_relation",
                    source="relation",
                    value=relation_support,
                    applied=True,
                    note="high-support relation keeps the turn in guided-help posture",
                )
            ],
        )

    if work_partner_explicit:
        evidence = [
            RoleSelectionEvidenceOutput(
                signal="work_partner_orchestration_signal",
                source="event_text",
                value=text,
                applied=True,
                note="explicit work-partner phrasing selects the shared work-partner role",
            )
        ]
        if has_active_goal_context:
            evidence.append(
                RoleSelectionEvidenceOutput(
                    signal="active_goal_context",
                    source="context",
                    value=context.related_goals[0],
                    applied=True,
                    note="active-goal context reinforces explicit work-partner posture",
                )
            )
        return RoleSelectionDecision(
            selected="work_partner",
            confidence=0.86 if has_active_goal_context else 0.82,
            reason=(
                "work_partner_goal_orchestration"
                if has_active_goal_context
                else "work_partner_explicit_orchestration"
            ),
            evidence=evidence,
        )

    if perception.topic == "planning" or any(keyword in lowered for keyword in ANALYSIS_KEYWORDS):
        evidence = [
            RoleSelectionEvidenceOutput(
                signal="analysis_topic_signal",
                source="perception",
                value=perception.topic,
                applied=True,
                note="planning or analysis phrasing keeps role selection analytical",
            )
        ]
        confidence = 0.82
        reason = "planning_topic_or_analysis_keyword"
        if has_active_goal_context:
            evidence.append(
                RoleSelectionEvidenceOutput(
                    signal="active_goal_context",
                    source="context",
                    value=context.related_goals[0],
                    applied=True,
                    note="active-goal context reinforces analytical role selection",
                )
            )
            confidence = 0.85
            reason = "planning_topic_active_goal_context"
        return RoleSelectionDecision(
            selected="analyst",
            confidence=confidence,
            reason=reason,
            evidence=evidence,
        )

    if any(lowered.startswith(keyword) for keyword in EXECUTOR_KEYWORDS):
        return RoleSelectionDecision(
            selected="executor",
            confidence=0.78,
            reason="explicit_execution_request",
            evidence=[
                RoleSelectionEvidenceOutput(
                    signal="execution_keyword",
                    source="event_text",
                    value=text,
                    applied=True,
                    note="direct execution phrasing keeps role selection execution-oriented",
                )
            ],
        )

    if is_help_turn and has_active_goal_context and context.risk_level >= 0.45:
        return RoleSelectionDecision(
            selected="advisor",
            confidence=0.75,
            reason="active_goal_risk_review",
            evidence=[
                RoleSelectionEvidenceOutput(
                    signal="active_goal_context",
                    source="context",
                    value=context.related_goals[0],
                    applied=True,
                    note="active goal keeps the turn grounded in the current workstream",
                ),
                RoleSelectionEvidenceOutput(
                    signal="context_risk",
                    source="context",
                    value=f"{context.risk_level:.2f}",
                    applied=True,
                    note="higher risk shifts ambiguous help turns toward advisory posture",
                ),
            ],
        )

    if preferred_role_allowed(
        preferred_role=preferred_role,
        preferred_role_confidence=preferred_role_confidence,
        allowed_roles=PREFERRED_ROLES,
    ):
        if is_help_turn:
            return RoleSelectionDecision(
                selected=preferred_role,
                confidence=0.73,
                reason="preferred_role_help_tie_break",
                evidence=[
                    RoleSelectionEvidenceOutput(
                        signal="preferred_role",
                        source="user_preference",
                        value=preferred_role,
                        applied=True,
                        note="preferred role is allowed on ambiguous help turns",
                    )
                ],
            )
        if is_general_turn:
            return RoleSelectionDecision(
                selected=preferred_role,
                confidence=0.68,
                reason="preferred_role_general_tie_break",
                evidence=[
                    RoleSelectionEvidenceOutput(
                        signal="preferred_role",
                        source="user_preference",
                        value=preferred_role,
                        applied=True,
                        note="preferred role is allowed on general ambiguous turns",
                    )
                ],
            )

    collaboration_role = _collaboration_role(collaboration_preference)
    if collaboration_role is not None and is_role_tie_break_turn:
        if is_help_turn:
            return RoleSelectionDecision(
                selected=collaboration_role,
                confidence=0.71,
                reason="collaboration_preference_help_tie_break",
                evidence=[
                    RoleSelectionEvidenceOutput(
                        signal="collaboration_preference",
                        source="user_preference",
                        value=collaboration_preference,
                        applied=True,
                        note="collaboration preference shapes ambiguous help posture",
                    )
                ],
            )
        if is_general_turn:
            return RoleSelectionDecision(
                selected=collaboration_role,
                confidence=0.66,
                reason="collaboration_preference_general_tie_break",
                evidence=[
                    RoleSelectionEvidenceOutput(
                        signal="collaboration_preference",
                        source="user_preference",
                        value=collaboration_preference,
                        applied=True,
                        note="collaboration preference shapes general ambiguous turns",
                    )
                ],
            )

    relation_role = _collaboration_role(relation_collaboration or "")
    if relation_role is not None and is_role_tie_break_turn:
        if is_help_turn:
            return RoleSelectionDecision(
                selected=relation_role,
                confidence=0.69,
                reason="relation_collaboration_help_tie_break",
                evidence=[
                    RoleSelectionEvidenceOutput(
                        signal="collaboration_relation",
                        source="relation",
                        value=relation_collaboration or "",
                        applied=True,
                        note="trusted collaboration relation shapes ambiguous help posture",
                    )
                ],
            )
        if is_general_turn:
            return RoleSelectionDecision(
                selected=relation_role,
                confidence=0.64,
                reason="relation_collaboration_general_tie_break",
                evidence=[
                    RoleSelectionEvidenceOutput(
                        signal="collaboration_relation",
                        source="relation",
                        value=relation_collaboration or "",
                        applied=True,
                        note="trusted collaboration relation shapes general ambiguous turns",
                    )
                ],
            )

    theta_role = _theta_role(theta)
    if theta_role is not None and is_role_tie_break_turn:
        if is_help_turn:
            return RoleSelectionDecision(
                selected=theta_role,
                confidence=0.69,
                reason="theta_help_tie_break",
                evidence=[
                    RoleSelectionEvidenceOutput(
                        signal="theta_bias",
                        source="theta",
                        value=dominant_theta_channel(theta) or "",
                        applied=True,
                        note="theta remains a bounded final tie-break owner",
                    )
                ],
            )
        if is_general_turn:
            return RoleSelectionDecision(
                selected=theta_role,
                confidence=0.64,
                reason="theta_general_tie_break",
                evidence=[
                    RoleSelectionEvidenceOutput(
                        signal="theta_bias",
                        source="theta",
                        value=dominant_theta_channel(theta) or "",
                        applied=True,
                        note="theta remains a bounded final tie-break owner",
                    )
                ],
            )

    if is_help_turn:
        return RoleSelectionDecision(
            selected="mentor",
            confidence=0.71,
            reason="help_turn_default",
            evidence=[
                RoleSelectionEvidenceOutput(
                    signal="help_turn_default",
                    source="fallback",
                    value="mentor",
                    applied=True,
                    note="general help turns default to guided mentoring posture",
                )
            ],
        )

    if context.risk_level >= 0.5:
        return RoleSelectionDecision(
            selected="advisor",
            confidence=0.70,
            reason="risk_level_fallback",
            evidence=[
                RoleSelectionEvidenceOutput(
                    signal="context_risk",
                    source="context",
                    value=f"{context.risk_level:.2f}",
                    applied=True,
                    note="higher context risk keeps the role in advisory posture",
                )
            ],
        )

    return RoleSelectionDecision(
        selected="advisor",
        confidence=0.60,
        reason="default_advisor_fallback",
        evidence=[
            RoleSelectionEvidenceOutput(
                signal="default_fallback",
                source="fallback",
                value="advisor",
                applied=True,
                note="no stronger role evidence was selected for this turn",
            )
        ],
    )


def _theta_role(theta: dict | None) -> str | None:
    channel = dominant_theta_channel(theta)
    if channel is None:
        return None
    role_by_channel = {
        "support": "friend",
        "analysis": "analyst",
        "execution": "executor",
    }
    return role_by_channel.get(channel)


def _collaboration_role(collaboration_preference: str) -> str | None:
    if collaboration_preference == "hands_on":
        return "executor"
    if collaboration_preference == "guided":
        return "mentor"
    return None
