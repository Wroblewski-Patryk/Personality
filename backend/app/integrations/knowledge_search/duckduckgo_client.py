from __future__ import annotations

import html
import re
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx


_RESULT_PATTERN = re.compile(
    r'<a[^>]*class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>(?P<rest>.*?)(?=<a[^>]*class="result__a"|$)',
    re.IGNORECASE | re.DOTALL,
)
_SNIPPET_PATTERN = re.compile(
    r'<a[^>]*class="result__snippet"[^>]*>(?P<snippet>.*?)</a>|<div[^>]*class="result__snippet"[^>]*>(?P<divsnippet>.*?)</div>',
    re.IGNORECASE | re.DOTALL,
)
_TAG_PATTERN = re.compile(r"<[^>]+>")


class DuckDuckGoSearchClient:
    def __init__(
        self,
        *,
        base_url: str = "https://html.duckduckgo.com/html/",
        http_client: Any | None = None,
    ) -> None:
        self.base_url = base_url
        self.http_client = http_client

    @property
    def ready(self) -> bool:
        return True

    async def search_web(self, *, query: str, limit: int = 5) -> list[dict[str, str]]:
        params = {"q": query}
        if self.http_client is not None:
            response = await self.http_client.get(self.base_url, params=params)
            if hasattr(response, "raise_for_status"):
                response.raise_for_status()
            text = response.text if hasattr(response, "text") else str(response)
        else:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                text = response.text
        return self._parse_results(text=text, limit=limit)

    def _parse_results(self, *, text: str, limit: int) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        for rank, match in enumerate(_RESULT_PATTERN.finditer(text), start=1):
            title = self._clean_text(match.group("title"))
            url = self._unwrap_result_url(match.group("href"))
            snippet_match = _SNIPPET_PATTERN.search(match.group("rest"))
            snippet = ""
            if snippet_match is not None:
                snippet = self._clean_text(
                    snippet_match.group("snippet") or snippet_match.group("divsnippet") or ""
                )
            if not title or not url:
                continue
            results.append(
                {
                    "title": title[:120],
                    "url": url[:500],
                    "snippet": snippet[:280],
                    "rank": str(rank),
                }
            )
            if len(results) >= max(1, int(limit)):
                break
        return results

    def _unwrap_result_url(self, href: str) -> str:
        candidate = html.unescape(href or "").strip()
        parsed = urlparse(candidate)
        if parsed.path.startswith("/l/"):
            uddg = parse_qs(parsed.query).get("uddg", [""])[0]
            return unquote(uddg).strip()
        return candidate

    def _clean_text(self, value: str) -> str:
        without_tags = _TAG_PATTERN.sub(" ", html.unescape(value or ""))
        return " ".join(without_tags.split())
