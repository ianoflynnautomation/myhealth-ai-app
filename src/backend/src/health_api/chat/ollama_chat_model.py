"""Ollama chat model over an injected HTTP transport.

Tests pass ``httpx.MockTransport``. This module does not open a port.
"""

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class Citation:
    content: str


class OllamaChatModel:
    def __init__(self, *, base_url: str, model: str, transport: httpx.AsyncBaseTransport) -> None:
        self._base_url = base_url
        self._model = model
        self._transport = transport

    async def answer(self, query: str, citations: list[Citation]) -> str:
        async with httpx.AsyncClient(transport=self._transport) as client:
            await client.post(
                f"{self._base_url.rstrip('/')}/chat/completions",
                json={"model": self._model},
            )
        return ""
