from app.core.contracts import (
    ActionDelivery,
    ActionDeliveryConnectorIntent,
    ActionDeliveryExecutionEnvelope,
)
from app.integrations.delivery_router import DeliveryRouter
from app.integrations.telegram.telemetry import TelegramChannelTelemetry


class FakeTelegramClient:
    def __init__(self, *, ok: bool = True, error: Exception | None = None):
        self.ok = ok
        self.error = error
        self.calls: list[dict[str, int | str | None]] = []

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        *,
        parse_mode: str | None = None,
    ) -> dict:
        self.calls.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})
        if self.error is not None:
            raise self.error
        if self.ok:
            return {"ok": True}
        return {"ok": False, "description": "telegram error"}


async def test_delivery_router_handles_api_channel() -> None:
    router = DeliveryRouter(telegram_client=FakeTelegramClient())

    result = await router.deliver(
        ActionDelivery(
            message="hello",
            tone="supportive",
            channel="api",
            language="en",
        )
    )

    assert result.status == "success"
    assert result.actions == ["api_response"]


async def test_delivery_router_appends_execution_envelope_note_for_connector_safe_delivery() -> None:
    router = DeliveryRouter(telegram_client=FakeTelegramClient())

    result = await router.deliver(
        ActionDelivery(
            message="hello",
            tone="supportive",
            channel="api",
            language="en",
            execution_envelope=ActionDeliveryExecutionEnvelope(
                connector_safe=True,
                connector_intents=[
                    ActionDeliveryConnectorIntent(
                        connector_kind="task_system",
                        provider_hint="clickup",
                        operation="create_task",
                        mode="mutate_with_confirmation",
                        allowed=False,
                        requires_confirmation=True,
                        reason="explicit_user_confirmation_required",
                    )
                ],
            ),
        )
    )

    assert result.status == "success"
    assert "Execution envelope:" in result.notes
    assert "connector_intents=1" in result.notes
    assert "permission_gates=0" in result.notes


async def test_delivery_router_handles_telegram_channel() -> None:
    telegram_client = FakeTelegramClient(ok=True)
    telemetry = TelegramChannelTelemetry()
    router = DeliveryRouter(
        telegram_client=telegram_client,
        telegram_telemetry=telemetry,
    )

    result = await router.deliver(
        ActionDelivery(
            message="hello",
            tone="supportive",
            channel="telegram",
            language="en",
            chat_id=42,
        )
    )

    assert result.status == "success"
    assert result.actions == ["send_telegram_message"]
    assert telegram_client.calls == [{"chat_id": 42, "text": "hello", "parse_mode": None}]
    snapshot = telemetry.snapshot(bot_token_configured=True, webhook_secret_configured=False)
    assert snapshot["delivery_attempts"] == 1
    assert snapshot["delivery_successes"] == 1
    assert snapshot["delivery_failures"] == 0
    assert snapshot["last_delivery"]["state"] == "sent"
    assert snapshot["last_delivery"]["chat_id"] == 42
    assert snapshot["last_delivery"]["segment_count"] == 1
    assert snapshot["last_delivery"]["formatting_state"] == "plain_text"


async def test_delivery_router_requires_chat_id_for_telegram() -> None:
    telemetry = TelegramChannelTelemetry()
    router = DeliveryRouter(
        telegram_client=FakeTelegramClient(),
        telegram_telemetry=telemetry,
    )

    result = await router.deliver(
        ActionDelivery(
            message="hello",
            tone="supportive",
            channel="telegram",
            language="en",
        )
    )

    assert result.status == "fail"
    assert result.actions == []
    assert "chat_id is missing" in result.notes
    snapshot = telemetry.snapshot(bot_token_configured=True, webhook_secret_configured=False)
    assert snapshot["delivery_attempts"] == 0
    assert snapshot["delivery_failures"] == 1
    assert snapshot["last_delivery"]["state"] == "missing_chat_id"


async def test_delivery_router_surfaces_telegram_api_errors() -> None:
    telegram_client = FakeTelegramClient(ok=False)
    telemetry = TelegramChannelTelemetry()
    router = DeliveryRouter(
        telegram_client=telegram_client,
        telegram_telemetry=telemetry,
    )

    result = await router.deliver(
        ActionDelivery(
            message="hello",
            tone="supportive",
            channel="telegram",
            language="en",
            chat_id=42,
        )
    )

    assert result.status == "fail"
    assert result.actions == ["send_telegram_message"]
    assert "telegram error" in result.notes
    snapshot = telemetry.snapshot(bot_token_configured=True, webhook_secret_configured=False)
    assert snapshot["delivery_attempts"] == 1
    assert snapshot["delivery_failures"] == 1
    assert snapshot["last_delivery"]["state"] == "telegram_api_error"
    assert snapshot["last_delivery"]["segment_count"] == 1
    assert snapshot["last_delivery"]["formatting_state"] == "plain_text"


async def test_delivery_router_handles_telegram_delivery_exception_as_fail_result() -> None:
    telegram_client = FakeTelegramClient(error=TimeoutError("upstream timeout"))
    telemetry = TelegramChannelTelemetry()
    router = DeliveryRouter(
        telegram_client=telegram_client,
        telegram_telemetry=telemetry,
    )

    result = await router.deliver(
        ActionDelivery(
            message="hello",
            tone="supportive",
            channel="telegram",
            language="en",
            chat_id=42,
        )
    )

    assert result.status == "fail"
    assert result.actions == ["send_telegram_message"]
    assert "TimeoutError" in result.notes
    assert "upstream timeout" in result.notes
    snapshot = telemetry.snapshot(bot_token_configured=True, webhook_secret_configured=False)
    assert snapshot["delivery_attempts"] == 1
    assert snapshot["delivery_failures"] == 1
    assert snapshot["last_delivery"]["state"] == "delivery_exception"
    assert snapshot["last_delivery"]["segment_count"] == 1
    assert snapshot["last_delivery"]["formatting_state"] == "plain_text"


async def test_delivery_router_segments_long_telegram_messages() -> None:
    telegram_client = FakeTelegramClient(ok=True)
    telemetry = TelegramChannelTelemetry()
    router = DeliveryRouter(telegram_client=telegram_client, telegram_telemetry=telemetry)
    message = "\n\n".join(f"Section {index}: " + ("alpha " * 350) for index in range(1, 8))

    result = await router.deliver(
        ActionDelivery(
            message=message,
            tone="supportive",
            channel="telegram",
            language="en",
            chat_id=42,
        )
    )

    assert result.status == "success"
    assert len(telegram_client.calls) > 1
    assert all(len(str(call["text"])) <= 4096 for call in telegram_client.calls)
    assert str(telegram_client.calls[0]["text"]).startswith("Section 1:")
    assert str(telegram_client.calls[-1]["text"]).startswith("Section 7:")
    assert "sent in" in result.notes
    snapshot = telemetry.snapshot(bot_token_configured=True, webhook_secret_configured=False)
    assert snapshot["delivery_segmentation_state"] == "bounded_transport_segmentation"
    assert snapshot["delivery_formatting_state"] == "supported_markdown_to_html_with_plain_text_fallback"
    assert snapshot["last_delivery"]["segment_count"] == len(telegram_client.calls)
    assert snapshot["last_delivery"]["formatting_state"] == "plain_text"


async def test_delivery_router_applies_safe_html_formatting_for_supported_markdown() -> None:
    telegram_client = FakeTelegramClient(ok=True)
    telemetry = TelegramChannelTelemetry()
    router = DeliveryRouter(telegram_client=telegram_client, telegram_telemetry=telemetry)

    result = await router.deliver(
        ActionDelivery(
            message="Use **bold** and `code`.\n\n```python\nprint('ok')\n```",
            tone="supportive",
            channel="telegram",
            language="en",
            chat_id=42,
        )
    )

    assert result.status == "success"
    assert telegram_client.calls == [
        {
            "chat_id": 42,
            "text": "Use <b>bold</b> and <code>code</code>.\n\n<pre><code>print(&#x27;ok&#x27;)\n</code></pre>",
            "parse_mode": "HTML",
        }
    ]
    snapshot = telemetry.snapshot(bot_token_configured=True, webhook_secret_configured=False)
    assert snapshot["last_delivery"]["segment_count"] == 1
    assert snapshot["last_delivery"]["formatting_state"] == "telegram_html"


async def test_delivery_router_falls_back_to_plain_text_when_markdown_is_unsafe() -> None:
    telegram_client = FakeTelegramClient(ok=True)
    telemetry = TelegramChannelTelemetry()
    router = DeliveryRouter(telegram_client=telegram_client, telegram_telemetry=telemetry)

    result = await router.deliver(
        ActionDelivery(
            message="This **markdown never closes.",
            tone="supportive",
            channel="telegram",
            language="en",
            chat_id=42,
        )
    )

    assert result.status == "success"
    assert telegram_client.calls == [
        {
            "chat_id": 42,
            "text": "This **markdown never closes.",
            "parse_mode": None,
        }
    ]
    snapshot = telemetry.snapshot(bot_token_configured=True, webhook_secret_configured=False)
    assert snapshot["last_delivery"]["segment_count"] == 1
    assert snapshot["last_delivery"]["formatting_state"] == "plain_text"
