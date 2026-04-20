from app.core.contracts import ActionDelivery, ActionResult
from app.integrations.telegram.client import TelegramClient


class DeliveryRouter:
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    async def deliver(self, delivery: ActionDelivery) -> ActionResult:
        if delivery.channel == "api":
            return ActionResult(
                status="success",
                actions=["api_response"],
                notes="Response returned via API.",
            )

        if delivery.channel == "telegram":
            return await self._deliver_telegram(delivery)

        return ActionResult(
            status="fail",
            actions=[],
            notes=f"Unsupported delivery channel: {delivery.channel}",
        )

    async def _deliver_telegram(self, delivery: ActionDelivery) -> ActionResult:
        if delivery.chat_id is None:
            return ActionResult(
                status="fail",
                actions=[],
                notes="Telegram response requested but chat_id is missing.",
            )

        try:
            telegram_result = await self.telegram_client.send_message(
                chat_id=delivery.chat_id,
                text=delivery.message,
            )
        except Exception as exc:
            return ActionResult(
                status="fail",
                actions=["send_telegram_message"],
                notes=f"Telegram delivery exception: {type(exc).__name__}: {exc}",
            )
        if telegram_result.get("ok"):
            return ActionResult(
                status="success",
                actions=["send_telegram_message"],
                notes="Telegram message sent.",
            )
        return ActionResult(
            status="fail",
            actions=["send_telegram_message"],
            notes=f"Telegram API error: {telegram_result}",
        )
