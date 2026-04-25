import json
import logging
from dataclasses import dataclass
from typing import Any


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


@dataclass(frozen=True)
class RuntimeLogContext:
    event_id: str
    trace_id: str
    source: str


class RuntimeStageLogger:
    def __init__(self, logger: logging.Logger, context: RuntimeLogContext):
        self.logger = logger
        self.context = context

    def start(self, stage: str, *, summary: str | None = None) -> None:
        self._emit(
            level=logging.INFO,
            stage=stage,
            status="start",
            summary=summary,
        )

    def success(self, stage: str, *, duration_ms: int, summary: str | None = None) -> None:
        self._emit(
            level=logging.INFO,
            stage=stage,
            status="success",
            duration_ms=duration_ms,
            summary=summary,
        )

    def failure(
        self,
        stage: str,
        *,
        duration_ms: int,
        error: Exception,
        summary: str | None = None,
    ) -> None:
        self._emit(
            level=logging.ERROR,
            stage=stage,
            status="failure",
            duration_ms=duration_ms,
            summary=summary,
            error=error,
        )

    def _emit(
        self,
        *,
        level: int,
        stage: str,
        status: str,
        duration_ms: int | None = None,
        summary: str | None = None,
        error: Exception | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "kind": "runtime_stage",
            "event_id": self.context.event_id,
            "trace_id": self.context.trace_id,
            "source": self.context.source,
            "stage": stage,
            "status": status,
        }
        if duration_ms is not None:
            payload["duration_ms"] = duration_ms
        if summary:
            payload["summary"] = summarize_for_log(summary)
        if error is not None:
            payload["error_type"] = type(error).__name__
            payload["error"] = summarize_for_log(str(error))
        self.logger.log(level, json.dumps(payload, sort_keys=True))


def summarize_for_log(value: Any, *, max_length: int = 180) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return "-"
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 3].rstrip()}..."
