from app.core.action_delivery import summarize_action_delivery_envelope
from app.core.contracts import ActionDelivery, ActionResult
from app.integrations.telegram.client import TelegramClient
from app.integrations.telegram.telemetry import TelegramChannelTelemetry


class DeliveryRouter:
    def __init__(
        self,
        telegram_client: TelegramClient,
        *,
        telegram_telemetry: TelegramChannelTelemetry | None = None,
    ):
        self.telegram_client = telegram_client
        self.telegram_telemetry = telegram_telemetry

    async def deliver(self, delivery: ActionDelivery) -> ActionResult:
        envelope_note = summarize_action_delivery_envelope(delivery.execution_envelope)
        if delivery.channel == "api":
            return ActionResult(
                status="success",
                actions=["api_response"],
                notes=self._with_envelope_note("Response returned via API.", envelope_note),
            )

        if delivery.channel == "telegram":
            return await self._deliver_telegram(delivery, envelope_note=envelope_note)

        return ActionResult(
            status="fail",
            actions=[],
            notes=f"Unsupported delivery channel: {delivery.channel}",
        )

    async def _deliver_telegram(self, delivery: ActionDelivery, *, envelope_note: str) -> ActionResult:
        if delivery.chat_id is None:
            if self.telegram_telemetry is not None:
                self.telegram_telemetry.record_delivery_failure(
                    state="missing_chat_id",
                    note="telegram_chat_id_missing",
                    chat_id=None,
                )
            return ActionResult(
                status="fail",
                actions=[],
                notes=self._with_envelope_note(
                    "Telegram response requested but chat_id is missing.",
                    envelope_note,
                ),
            )

        if self.telegram_telemetry is not None:
            self.telegram_telemetry.record_delivery_attempt(chat_id=delivery.chat_id)
        try:
            telegram_result = await self.telegram_client.send_message(
                chat_id=delivery.chat_id,
                text=delivery.message,
            )
        except Exception as exc:
            if self.telegram_telemetry is not None:
                self.telegram_telemetry.record_delivery_failure(
                    state="delivery_exception",
                    note=f"{type(exc).__name__}: {exc}",
                    chat_id=delivery.chat_id,
                )
            return ActionResult(
                status="fail",
                actions=["send_telegram_message"],
                notes=self._with_envelope_note(
                    f"Telegram delivery exception: {type(exc).__name__}: {exc}",
                    envelope_note,
                ),
            )
        if telegram_result.get("ok"):
            if self.telegram_telemetry is not None:
                self.telegram_telemetry.record_delivery_success(chat_id=delivery.chat_id)
            return ActionResult(
                status="success",
                actions=["send_telegram_message"],
                notes=self._with_envelope_note("Telegram message sent.", envelope_note),
            )
        if self.telegram_telemetry is not None:
            self.telegram_telemetry.record_delivery_failure(
                state="telegram_api_error",
                note=str(telegram_result.get("description", "telegram_api_error")),
                chat_id=delivery.chat_id,
            )
        return ActionResult(
            status="fail",
            actions=["send_telegram_message"],
            notes=self._with_envelope_note(f"Telegram API error: {telegram_result}", envelope_note),
        )

    def _with_envelope_note(self, base: str, envelope_note: str) -> str:
        if not envelope_note:
            return base
        return f"{base} Execution envelope: {envelope_note}."
