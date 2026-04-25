from app.core.contracts import ContextOutput, Event, PerceptionOutput, RoleOutput
from app.core.role_selection_policy import select_role
from app.core.skill_registry import skills_for_role_and_topic


class RoleAgent:
    def run(
        self,
        event: Event,
        perception: PerceptionOutput,
        context: ContextOutput,
        user_preferences: dict | None = None,
        relations: list[dict] | None = None,
        theta: dict | None = None,
    ) -> RoleOutput:
        decision = select_role(
            event=event,
            perception=perception,
            context=context,
            user_preferences=user_preferences,
            relations=relations,
            theta=theta,
        )
        return self._build_role_output(
            selected=decision.selected,
            confidence=decision.confidence,
            selection_reason=decision.reason,
            selection_evidence=decision.evidence,
            perception=perception,
            event_text=str(event.payload.get("text", "")).strip(),
        )

    def _build_role_output(
        self,
        *,
        selected: str,
        confidence: float,
        selection_reason: str,
        selection_evidence: list,
        perception: PerceptionOutput,
        event_text: str,
    ) -> RoleOutput:
        return RoleOutput(
            selected=selected,
            confidence=confidence,
            selection_reason=selection_reason,
            selection_evidence=list(selection_evidence),
            selected_skills=skills_for_role_and_topic(
                role_name=selected,
                topic=perception.topic,
                event_text=event_text,
            ),
        )
