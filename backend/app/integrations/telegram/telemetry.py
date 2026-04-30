from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any

TELEGRAM_DELIVERY_ADAPTATION_POLICY_OWNER = "telegram_delivery_channel_adaptation"
TELEGRAM_DELIVERY_SEGMENTATION_STATE = "bounded_transport_segmentation"
TELEGRAM_DELIVERY_FORMATTING_STATE = "supported_markdown_to_html_with_plain_text_fallback"
TELEGRAM_DELIVERY_MESSAGE_LIMIT = 4096
TELEGRAM_DELIVERY_SEGMENT_TARGET = 3500
TELEGRAM_DELIVERY_SUPPORTED_MARKDOWN = [
    "bold",
    "italic",
    "inline_code",
    "fenced_code",
    "ordered_lists_plain_text",
    "unordered_lists_plain_text",
]


class TelegramChannelTelemetry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._ingress_attempts = 0
        self._ingress_rejections = 0
        self._ingress_queued = 0
        self._ingress_processed = 0
        self._ingress_runtime_failures = 0
        self._delivery_attempts = 0
        self._delivery_successes = 0
        self._delivery_failures = 0
        self._last_ingress: dict[str, Any] = {}
        self._last_delivery: dict[str, Any] = {}

    def record_ingress_attempt(
        self,
        *,
        update_id: int | str | None,
        chat_id: int | str | None,
    ) -> None:
        with self._lock:
            self._ingress_attempts += 1
            self._last_ingress = self._ingress_event(
                state="received",
                reason="telegram_update_received",
                update_id=update_id,
                chat_id=chat_id,
            )

    def record_ingress_rejection(
        self,
        *,
        reason: str,
        update_id: int | str | None,
        chat_id: int | str | None,
    ) -> None:
        with self._lock:
            self._ingress_rejections += 1
            self._last_ingress = self._ingress_event(
                state="rejected",
                reason=reason,
                update_id=update_id,
                chat_id=chat_id,
            )

    def record_ingress_queued(
        self,
        *,
        reason: str,
        update_id: int | str | None,
        chat_id: int | str | None,
        source_count: int,
    ) -> None:
        with self._lock:
            self._ingress_queued += 1
            payload = self._ingress_event(
                state="queued",
                reason=reason,
                update_id=update_id,
                chat_id=chat_id,
            )
            payload["source_count"] = int(source_count)
            self._last_ingress = payload

    def record_ingress_processed(
        self,
        *,
        update_id: int | str | None,
        chat_id: int | str | None,
        action_status: str,
        reflection_triggered: bool,
    ) -> None:
        with self._lock:
            self._ingress_processed += 1
            payload = self._ingress_event(
                state="processed",
                reason="runtime_result_ready",
                update_id=update_id,
                chat_id=chat_id,
            )
            payload["action_status"] = action_status
            payload["reflection_triggered"] = bool(reflection_triggered)
            self._last_ingress = payload

    def record_ingress_runtime_failure(
        self,
        *,
        reason: str,
        update_id: int | str | None,
        chat_id: int | str | None,
    ) -> None:
        with self._lock:
            self._ingress_runtime_failures += 1
            self._last_ingress = self._ingress_event(
                state="runtime_failed",
                reason=reason,
                update_id=update_id,
                chat_id=chat_id,
            )

    def record_delivery_attempt(
        self,
        *,
        chat_id: int | str | None,
        segment_count: int | None = None,
        formatting_state: str | None = None,
    ) -> None:
        with self._lock:
            self._delivery_attempts += 1
            self._last_delivery = self._delivery_event(
                state="attempted",
                note="telegram_delivery_attempted",
                chat_id=chat_id,
                segment_count=segment_count,
                formatting_state=formatting_state,
            )

    def record_delivery_success(
        self,
        *,
        chat_id: int | str | None,
        segment_count: int | None = None,
        formatting_state: str | None = None,
    ) -> None:
        with self._lock:
            self._delivery_successes += 1
            self._last_delivery = self._delivery_event(
                state="sent",
                note="telegram_message_sent",
                chat_id=chat_id,
                segment_count=segment_count,
                formatting_state=formatting_state,
            )

    def record_delivery_failure(
        self,
        *,
        state: str,
        note: str,
        chat_id: int | str | None,
        segment_count: int | None = None,
        formatting_state: str | None = None,
    ) -> None:
        with self._lock:
            self._delivery_failures += 1
            self._last_delivery = self._delivery_event(
                state=state,
                note=note,
                chat_id=chat_id,
                segment_count=segment_count,
                formatting_state=formatting_state,
            )

    def snapshot(
        self,
        *,
        bot_token_configured: bool,
        webhook_secret_configured: bool,
    ) -> dict[str, Any]:
        with self._lock:
            delivery_ready = bool(bot_token_configured)
            return {
                "policy_owner": "telegram_conversation_reliability_telemetry",
                "channel": "telegram",
                "bot_token_configured": bool(bot_token_configured),
                "webhook_secret_configured": bool(webhook_secret_configured),
                "round_trip_ready": delivery_ready,
                "round_trip_state": (
                    "provider_backed_ready" if delivery_ready else "missing_bot_token"
                ),
                "round_trip_hint": (
                    "telegram_round_trip_ready"
                    if delivery_ready
                    else "configure_telegram_bot_token_for_v1_round_trip"
                ),
                "delivery_adaptation_policy_owner": TELEGRAM_DELIVERY_ADAPTATION_POLICY_OWNER,
                "delivery_segmentation_state": TELEGRAM_DELIVERY_SEGMENTATION_STATE,
                "delivery_formatting_state": TELEGRAM_DELIVERY_FORMATTING_STATE,
                "delivery_message_limit": TELEGRAM_DELIVERY_MESSAGE_LIMIT,
                "delivery_segment_target": TELEGRAM_DELIVERY_SEGMENT_TARGET,
                "delivery_supported_markdown": list(TELEGRAM_DELIVERY_SUPPORTED_MARKDOWN),
                "ingress_attempts": self._ingress_attempts,
                "ingress_rejections": self._ingress_rejections,
                "ingress_queued": self._ingress_queued,
                "ingress_processed": self._ingress_processed,
                "ingress_runtime_failures": self._ingress_runtime_failures,
                "delivery_attempts": self._delivery_attempts,
                "delivery_successes": self._delivery_successes,
                "delivery_failures": self._delivery_failures,
                "last_ingress": dict(self._last_ingress),
                "last_delivery": dict(self._last_delivery),
            }

    def _ingress_event(
        self,
        *,
        state: str,
        reason: str,
        update_id: int | str | None,
        chat_id: int | str | None,
    ) -> dict[str, Any]:
        return {
            "at": self._timestamp(),
            "state": state,
            "reason": reason,
            "update_id": update_id,
            "chat_id": chat_id,
        }

    def _delivery_event(
        self,
        *,
        state: str,
        note: str,
        chat_id: int | str | None,
        segment_count: int | None = None,
        formatting_state: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "at": self._timestamp(),
            "state": state,
            "note": note,
            "chat_id": chat_id,
        }
        if segment_count is not None:
            payload["segment_count"] = int(segment_count)
        if formatting_state:
            payload["formatting_state"] = formatting_state
        return payload

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()
