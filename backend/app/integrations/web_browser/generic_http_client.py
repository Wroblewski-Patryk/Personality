from __future__ import annotations

import html
import re
from typing import Any

import httpx


_TITLE_PATTERN = re.compile(r"<title[^>]*>(?P<title>.*?)</title>", re.IGNORECASE | re.DOTALL)
_SCRIPT_STYLE_PATTERN = re.compile(r"<(script|style)[^>]*>.*?</\\1>", re.IGNORECASE | re.DOTALL)
_TAG_PATTERN = re.compile(r"<[^>]+>")


class GenericHttpPageClient:
    def __init__(self, *, http_client: Any | None = None) -> None:
        self.http_client = http_client

    @property
    def ready(self) -> bool:
        return True

    async def read_page(self, *, url: str, excerpt_length: int = 500) -> dict[str, str]:
        if self.http_client is not None:
            response = await self.http_client.get(url)
            if hasattr(response, "raise_for_status"):
                response.raise_for_status()
            text = response.text if hasattr(response, "text") else str(response)
            final_url = str(getattr(response, "url", url))
            content_type = str(getattr(response, "headers", {}).get("Content-Type", "text/html"))
        else:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                text = response.text
                final_url = str(response.url)
                content_type = response.headers.get("Content-Type", "text/html")

        title_match = _TITLE_PATTERN.search(text)
        title = self._clean_text(title_match.group("title") if title_match else "")
        body_text = self._clean_text(_SCRIPT_STYLE_PATTERN.sub(" ", text))
        excerpt = body_text[: max(80, int(excerpt_length))].strip()
        return {
            "url": final_url[:500],
            "title": title[:160],
            "content_type": content_type[:120],
            "excerpt": excerpt,
            "truncated": str(len(body_text) > len(excerpt)).lower(),
        }

    def _clean_text(self, value: str) -> str:
        without_tags = _TAG_PATTERN.sub(" ", html.unescape(value or ""))
        return " ".join(without_tags.split())
