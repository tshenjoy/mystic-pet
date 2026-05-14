"""LLM client wrapper.

Honors the standard Anthropic env vars (ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL),
plus the AMD-internal gateway pattern (ANTHROPIC_CUSTOM_HEADERS containing
'Ocp-Apim-Subscription-Key: <key>'). On the AMD gateway, ANTHROPIC_API_KEY
is a dummy and the real auth lives in the custom header.
"""

from __future__ import annotations

import os

import anthropic


def _parse_custom_headers(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    headers: dict[str, str] = {}
    for entry in raw.split(","):
        if ":" not in entry:
            continue
        k, v = entry.split(":", 1)
        headers[k.strip()] = v.strip()
    return headers


class LLMClient:
    def __init__(
        self,
        model: str,
        max_tokens: int = 400,
        timeout_seconds: int = 15,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds

        kwargs: dict = {"timeout": timeout_seconds}
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            kwargs["api_key"] = api_key
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        if base_url:
            kwargs["base_url"] = base_url
        custom_headers = _parse_custom_headers(os.environ.get("ANTHROPIC_CUSTOM_HEADERS"))
        if custom_headers:
            kwargs["default_headers"] = custom_headers

        self._client = anthropic.Anthropic(**kwargs)

    def complete(self, system: str, user: str) -> str:
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        parts: list[str] = []
        for block in msg.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts).strip()
