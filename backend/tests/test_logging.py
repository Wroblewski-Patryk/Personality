import json
import logging

from app.core.logging import RuntimeLogContext, RuntimeStageLogger, summarize_for_log


def _runtime_logs(caplog, logger_name: str) -> list[dict]:
    return [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == logger_name and record.getMessage().startswith("{")
    ]


def test_runtime_stage_logger_emits_required_contract_fields(caplog) -> None:
    logger_name = "aion.runtime.contract"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    stage_logger = RuntimeStageLogger(
        logger=logger,
        context=RuntimeLogContext(event_id="evt-1", trace_id="trace-1", source="api"),
    )

    stage_logger.start("perception", summary="  user text  ")
    stage_logger.success("perception", duration_ms=12, summary="done")

    entries = _runtime_logs(caplog, logger_name)
    assert len(entries) == 2
    start, success = entries

    assert start == {
        "event_id": "evt-1",
        "kind": "runtime_stage",
        "source": "api",
        "stage": "perception",
        "status": "start",
        "summary": "user text",
        "trace_id": "trace-1",
    }
    assert success["event_id"] == "evt-1"
    assert success["trace_id"] == "trace-1"
    assert success["source"] == "api"
    assert success["stage"] == "perception"
    assert success["status"] == "success"
    assert success["duration_ms"] == 12
    assert success["summary"] == "done"


def test_runtime_stage_logger_failure_payload_is_traceable(caplog) -> None:
    logger_name = "aion.runtime.contract.failure"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    stage_logger = RuntimeStageLogger(
        logger=logger,
        context=RuntimeLogContext(event_id="evt-fail", trace_id="trace-fail", source="telegram"),
    )

    stage_logger.failure(
        "action",
        duration_ms=7,
        error=RuntimeError("x" * 260),
        summary="delivery failure",
    )

    entries = _runtime_logs(caplog, logger_name)
    assert len(entries) == 1
    payload = entries[0]
    assert payload["event_id"] == "evt-fail"
    assert payload["trace_id"] == "trace-fail"
    assert payload["source"] == "telegram"
    assert payload["stage"] == "action"
    assert payload["status"] == "failure"
    assert payload["duration_ms"] == 7
    assert payload["summary"] == "delivery failure"
    assert payload["error_type"] == "RuntimeError"
    assert payload["error"].endswith("...")


def test_runtime_stage_logger_supports_foreground_followup_stage_names(caplog) -> None:
    logger_name = "aion.runtime.contract.followup"
    caplog.set_level("INFO", logger=logger_name)
    logger = logging.getLogger(logger_name)
    stage_logger = RuntimeStageLogger(
        logger=logger,
        context=RuntimeLogContext(event_id="evt-followup", trace_id="trace-followup", source="api"),
    )

    stage_logger.start("memory_persist", summary="persist episode")
    stage_logger.success("memory_persist", duration_ms=3, summary="stored")
    stage_logger.start("reflection_enqueue", summary="enqueue reflection")
    stage_logger.success("reflection_enqueue", duration_ms=1, summary="queued")

    entries = _runtime_logs(caplog, logger_name)
    assert [(entry["stage"], entry["status"]) for entry in entries] == [
        ("memory_persist", "start"),
        ("memory_persist", "success"),
        ("reflection_enqueue", "start"),
        ("reflection_enqueue", "success"),
    ]
    assert entries[1]["duration_ms"] == 3
    assert entries[3]["duration_ms"] == 1


def test_summarize_for_log_contract() -> None:
    assert summarize_for_log("  hello   world ") == "hello world"
    assert summarize_for_log("") == "-"
    assert summarize_for_log("x" * 220, max_length=50) == ("x" * 47) + "..."
