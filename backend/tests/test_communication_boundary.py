from app.communication.boundary import (
    communication_boundary_summary,
    extract_communication_boundary_signals,
    proactive_boundary_block_reason,
    should_avoid_repeated_greeting,
)
from app.memory.episodic import extract_episode_fields
from app.reflection.relation_signals import derive_relation_updates


def test_extracts_contact_cadence_and_ritual_boundary_signals() -> None:
    signals = extract_communication_boundary_signals(
        "Nie pisz do mnie co pol godziny i nie musisz sie witac co wiadomosc."
    )

    assert {
        (signal.relation_type, signal.relation_value)
        for signal in signals
    } == {
        ("contact_cadence_preference", "low_frequency"),
        ("interaction_ritual_preference", "avoid_repeated_greeting"),
    }


def test_boundary_relations_block_generic_proactive_checkins() -> None:
    relations = [
        {
            "relation_type": "contact_cadence_preference",
            "relation_value": "low_frequency",
            "confidence": 0.94,
        }
    ]

    reason = proactive_boundary_block_reason(
        relations=relations,
        trigger="time_checkin",
        recent_outbound_count=0,
        unanswered_proactive_count=0,
    )

    assert reason == "contact_cadence_low_frequency_generic_trigger"


def test_boundary_summary_and_ritual_flag_use_relation_model() -> None:
    relations = [
        {
            "relation_type": "interaction_ritual_preference",
            "relation_value": "avoid_repeated_greeting",
            "confidence": 0.96,
        }
    ]

    assert should_avoid_repeated_greeting(relations) is True
    assert "avoid greeting" in communication_boundary_summary(relations)


def test_episode_field_extraction_exposes_relation_and_proactive_updates() -> None:
    fields = extract_episode_fields(
        {
            "payload": {
                "event": "Nie pisz co pol godziny",
                "relation_update": "contact_cadence_preference:low_frequency:global:global",
                "proactive_preference_update": "proactive_opt_in:false",
                "proactive_state_update": "delivery_guard_blocked:time_checkin:recent_outbound_limit",
            }
        }
    )

    assert fields["relation_update"] == "contact_cadence_preference:low_frequency:global:global"
    assert fields["proactive_preference_update"] == "proactive_opt_in:false"
    assert fields["proactive_state_update"] == "delivery_guard_blocked:time_checkin:recent_outbound_limit"


def test_reflection_derives_boundary_relations_from_episode_text() -> None:
    updates = derive_relation_updates(
        [
            {
                "payload": {
                    "event": "Nie pisz do mnie co pol godziny.",
                    "memory_kind": "episodic",
                }
            }
        ],
        extract_memory_fields=extract_episode_fields,
    )

    assert {
        (update["relation_type"], update["relation_value"])
        for update in updates
    } >= {("contact_cadence_preference", "low_frequency")}
