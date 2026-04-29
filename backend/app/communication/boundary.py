from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from app.utils.language import normalize_for_matching

CONTACT_CADENCE_RELATION = "contact_cadence_preference"
INTERRUPTION_TOLERANCE_RELATION = "interruption_tolerance"
INTERACTION_RITUAL_RELATION = "interaction_ritual_preference"

CONTACT_ON_DEMAND = "on_demand"
CONTACT_LOW_FREQUENCY = "low_frequency"
CONTACT_SCHEDULED_ONLY = "scheduled_only"
CONTACT_OPEN_TO_CHECKINS = "open_to_checkins"

INTERRUPTION_LOW = "low"
INTERRUPTION_MEDIUM = "medium"
INTERRUPTION_HIGH = "high"

RITUAL_AVOID_REPEATED_GREETING = "avoid_repeated_greeting"
RITUAL_WARM_OPENING_OK = "warm_opening_ok"

BOUNDARY_RELATION_TYPES = {
    CONTACT_CADENCE_RELATION,
    INTERRUPTION_TOLERANCE_RELATION,
    INTERACTION_RITUAL_RELATION,
}

GENERIC_PROACTIVE_TRIGGERS = {
    "time_checkin",
    "goal_stagnation",
    "memory_pattern",
    "relation_nudge",
}


@dataclass(frozen=True)
class CommunicationBoundarySignal:
    relation_type: str
    relation_value: str
    confidence: float
    source: str
    evidence: str


def extract_communication_boundary_signals(text: str) -> list[CommunicationBoundarySignal]:
    normalized = normalize_for_matching(text or "")
    if not normalized:
        return []

    signals: list[CommunicationBoundarySignal] = []
    if _contains_any(
        normalized,
        {
            "nie pisz do mnie co pol godziny",
            "nie pisz co pol godziny",
            "nie pinguj mnie co pol godziny",
            "nie odzywaj sie co pol godziny",
            "nie pisz tak czesto",
            "nie odzywaj sie tak czesto",
            "nie przypominaj co pol godziny",
            "stop checking in every 30 minutes",
            "do not message me every half hour",
            "dont message me every half hour",
            "not every half hour",
            "not every 30 minutes",
        },
    ):
        signals.append(
            CommunicationBoundarySignal(
                relation_type=CONTACT_CADENCE_RELATION,
                relation_value=CONTACT_LOW_FREQUENCY,
                confidence=0.94,
                source="communication_boundary_directive",
                evidence=_clip_evidence(text),
            )
        )

    if _contains_any(
        normalized,
        {
            "pisz tylko jak napisze",
            "odzywaj sie tylko jak napisze",
            "tylko jak napisze",
            "tylko gdy napisze",
            "tylko na zadanie",
            "nie pisz sam z siebie",
            "nie odzywaj sie sam z siebie",
            "only when i ask",
            "on demand only",
            "dont message unless i ask",
            "do not message unless i ask",
        },
    ):
        signals.append(
            CommunicationBoundarySignal(
                relation_type=CONTACT_CADENCE_RELATION,
                relation_value=CONTACT_ON_DEMAND,
                confidence=0.96,
                source="communication_boundary_directive",
                evidence=_clip_evidence(text),
            )
        )

    if _contains_any(
        normalized,
        {
            "tylko zaplanowane przypomnienia",
            "tylko ustawione przypomnienia",
            "pisz tylko zaplanowane",
            "only scheduled reminders",
            "scheduled reminders only",
        },
    ):
        signals.append(
            CommunicationBoundarySignal(
                relation_type=CONTACT_CADENCE_RELATION,
                relation_value=CONTACT_SCHEDULED_ONLY,
                confidence=0.95,
                source="communication_boundary_directive",
                evidence=_clip_evidence(text),
            )
        )

    if _contains_any(
        normalized,
        {
            "mozesz mnie pingowac",
            "mozesz sprawdzac co u mnie",
            "mozesz sie odzywac",
            "pinguj mnie smialo",
            "feel free to check in",
            "you can check in",
            "ping me freely",
        },
    ):
        signals.append(
            CommunicationBoundarySignal(
                relation_type=CONTACT_CADENCE_RELATION,
                relation_value=CONTACT_OPEN_TO_CHECKINS,
                confidence=0.86,
                source="communication_boundary_directive",
                evidence=_clip_evidence(text),
            )
        )

    if _contains_any(
        normalized,
        {
            "nie przerywaj",
            "nie przeszkadzaj",
            "nie rozpraszaj",
            "nie pinguj w trakcie pracy",
            "low interruption",
            "dont interrupt",
            "do not interrupt",
            "dont disturb",
        },
    ):
        signals.append(
            CommunicationBoundarySignal(
                relation_type=INTERRUPTION_TOLERANCE_RELATION,
                relation_value=INTERRUPTION_LOW,
                confidence=0.9,
                source="communication_boundary_directive",
                evidence=_clip_evidence(text),
            )
        )

    if _contains_any(
        normalized,
        {
            "mozesz przerywac",
            "mozesz mnie szturchac",
            "pinguj mnie smialo",
            "you can interrupt",
            "interrupt me if needed",
            "ping me freely",
        },
    ):
        signals.append(
            CommunicationBoundarySignal(
                relation_type=INTERRUPTION_TOLERANCE_RELATION,
                relation_value=INTERRUPTION_HIGH,
                confidence=0.84,
                source="communication_boundary_directive",
                evidence=_clip_evidence(text),
            )
        )

    if _contains_any(
        normalized,
        {
            "nie musisz sie witac co wiadomosc",
            "nie musisz witac sie co wiadomosc",
            "nie witaj sie za kazdym razem",
            "bez czesc co wiadomosc",
            "bez hej za kazdym razem",
            "nie zaczynaj zawsze od czesc",
            "do not greet me every message",
            "dont greet me every message",
            "no need to say hi every time",
            "no hello every time",
        },
    ):
        signals.append(
            CommunicationBoundarySignal(
                relation_type=INTERACTION_RITUAL_RELATION,
                relation_value=RITUAL_AVOID_REPEATED_GREETING,
                confidence=0.96,
                source="communication_boundary_directive",
                evidence=_clip_evidence(text),
            )
        )

    if _contains_any(
        normalized,
        {
            "mozesz sie witac",
            "lubie jak sie witasz",
            "warm opening ok",
            "hello is fine",
        },
    ):
        signals.append(
            CommunicationBoundarySignal(
                relation_type=INTERACTION_RITUAL_RELATION,
                relation_value=RITUAL_WARM_OPENING_OK,
                confidence=0.82,
                source="communication_boundary_directive",
                evidence=_clip_evidence(text),
            )
        )

    return _dedupe_signals(signals)


def communication_boundary_values(
    relations: Iterable[Mapping[str, object]],
    *,
    min_confidence: float = 0.68,
) -> dict[str, str]:
    values: dict[str, str] = {}
    for relation in relations:
        relation_type = str(relation.get("relation_type", "")).strip().lower()
        if relation_type not in BOUNDARY_RELATION_TYPES or relation_type in values:
            continue
        try:
            confidence = float(relation.get("confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0
        if confidence < min_confidence:
            continue
        relation_value = str(relation.get("relation_value", "")).strip().lower()
        if relation_value:
            values[relation_type] = relation_value
    return values


def communication_boundary_summary(relations: Iterable[Mapping[str, object]]) -> str:
    values = communication_boundary_values(relations)
    parts: list[str] = []
    cadence = values.get(CONTACT_CADENCE_RELATION)
    interruption = values.get(INTERRUPTION_TOLERANCE_RELATION)
    ritual = values.get(INTERACTION_RITUAL_RELATION)
    if cadence == CONTACT_ON_DEMAND:
        parts.append("Contact cadence: user prefers on-demand contact only.")
    elif cadence == CONTACT_LOW_FREQUENCY:
        parts.append("Contact cadence: user asked for less frequent proactive contact.")
    elif cadence == CONTACT_SCHEDULED_ONLY:
        parts.append("Contact cadence: user prefers only scheduled reminders.")
    elif cadence == CONTACT_OPEN_TO_CHECKINS:
        parts.append("Contact cadence: user is open to check-ins.")
    if interruption == INTERRUPTION_LOW:
        parts.append("Interruption tolerance: low.")
    elif interruption == INTERRUPTION_HIGH:
        parts.append("Interruption tolerance: high.")
    if ritual == RITUAL_AVOID_REPEATED_GREETING:
        parts.append("Interaction ritual: avoid greeting the user at the start of every message.")
    elif ritual == RITUAL_WARM_OPENING_OK:
        parts.append("Interaction ritual: warm openings are acceptable.")
    return " ".join(parts)


def proactive_boundary_block_reason(
    *,
    relations: Iterable[Mapping[str, object]],
    trigger: str,
    recent_outbound_count: int = 0,
    unanswered_proactive_count: int = 0,
) -> str | None:
    values = communication_boundary_values(relations)
    cadence = values.get(CONTACT_CADENCE_RELATION)
    interruption = values.get(INTERRUPTION_TOLERANCE_RELATION)
    normalized_trigger = str(trigger or "time_checkin").strip().lower()

    if cadence == CONTACT_ON_DEMAND:
        return "contact_cadence_on_demand"
    if cadence == CONTACT_SCHEDULED_ONLY:
        return "contact_cadence_scheduled_only"
    if cadence == CONTACT_LOW_FREQUENCY:
        if normalized_trigger in GENERIC_PROACTIVE_TRIGGERS:
            return "contact_cadence_low_frequency_generic_trigger"
        if recent_outbound_count >= 1:
            return "contact_cadence_low_frequency_recent_outbound"
    if interruption == INTERRUPTION_LOW and unanswered_proactive_count >= 1:
        return "low_interruption_tolerance_unanswered_proactive"
    return None


def should_avoid_repeated_greeting(relations: Iterable[Mapping[str, object]]) -> bool:
    return (
        communication_boundary_values(relations).get(INTERACTION_RITUAL_RELATION)
        == RITUAL_AVOID_REPEATED_GREETING
    )


def _contains_any(text: str, needles: set[str]) -> bool:
    return any(needle in text for needle in needles)


def _clip_evidence(text: str, *, limit: int = 160) -> str:
    normalized = " ".join(str(text or "").split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _dedupe_signals(signals: list[CommunicationBoundarySignal]) -> list[CommunicationBoundarySignal]:
    deduped: list[CommunicationBoundarySignal] = []
    seen: set[tuple[str, str]] = set()
    for signal in signals:
        key = (signal.relation_type, signal.relation_value)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(signal)
    return deduped
