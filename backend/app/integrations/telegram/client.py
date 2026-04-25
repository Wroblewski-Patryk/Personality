import httpx


class TelegramClient:
    def __init__(self, token: str | None):
        self.token = token
        self._client = httpx.AsyncClient(timeout=10.0)

    async def send_message(self, chat_id: int | str, text: str) -> dict:
        if not self.token:
            return {"ok": False, "description": "missing TELEGRAM_BOT_TOKEN"}

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        response = await self._client.post(url, json={"chat_id": chat_id, "text": text})
        response.raise_for_status()
        return response.json()

    async def set_webhook(self, webhook_url: str, secret_token: str | None = None) -> dict:
        if not self.token:
            return {"ok": False, "description": "missing TELEGRAM_BOT_TOKEN"}

        url = f"https://api.telegram.org/bot{self.token}/setWebhook"
        payload = {"url": webhook_url}
        if secret_token:
            payload["secret_token"] = secret_token
        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()
