from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI


class OpenAIEmbeddingClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.api_key = str(api_key or "").strip()
        self.client = client

    @property
    def ready(self) -> bool:
        return bool(self.client is not None or self.api_key)

    async def create_embedding(
        self,
        *,
        text: str,
        model: str,
        dimensions: int,
    ) -> list[float]:
        if not self.ready:
            raise RuntimeError("OpenAI embedding execution is not configured.")

        if self.client is not None:
            response = await self.client.embeddings.create(
                input=text,
                model=model,
                dimensions=dimensions,
                encoding_format="float",
            )
        else:
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.embeddings.create(
                input=text,
                model=model,
                dimensions=dimensions,
                encoding_format="float",
            )

        return [float(value) for value in response.data[0].embedding]
