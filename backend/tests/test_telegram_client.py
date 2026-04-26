import httpx

from app.integrations.telegram.client import TelegramClient


async def test_telegram_client_omits_parse_mode_when_not_provided() -> None:
    captured: list[dict] = []

    async def _handler(request: httpx.Request) -> httpx.Response:
        captured.append(request.content.decode("utf-8"))
        return httpx.Response(200, json={"ok": True})

    client = TelegramClient(token="bot-token")
    await client._client.aclose()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))

    try:
        result = await client.send_message(chat_id=42, text="hello")
    finally:
        await client.close()

    assert result == {"ok": True}
    assert '"parse_mode"' not in captured[0]


async def test_telegram_client_includes_parse_mode_when_requested() -> None:
    captured: list[dict] = []

    async def _handler(request: httpx.Request) -> httpx.Response:
        captured.append(request.content.decode("utf-8"))
        return httpx.Response(200, json={"ok": True})

    client = TelegramClient(token="bot-token")
    await client._client.aclose()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))

    try:
        result = await client.send_message(chat_id=42, text="<b>hello</b>", parse_mode="HTML")
    finally:
        await client.close()

    assert result == {"ok": True}
    assert '"parse_mode":"HTML"' in captured[0]
