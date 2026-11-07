"""Ollama chat model over an injected HTTP transport.

Tests pass ``httpx.MockTransport``. This module does not open a port.
"""

from dataclasses import dataclass

import httpx

# A cold llama3.1 on CPU takes longer than httpx's 5 s default to load and answer.
_TIMEOUT = httpx.Timeout(300.0, connect=5.0)


@dataclass(frozen=True)
class Citation:
    content: str


class OllamaChatModel:
    def __init__(self, *, base_url: str, model: str, transport: httpx.AsyncBaseTransport) -> None:
        self._base_url = base_url
        self._model = model
        self._transport = transport

    async def answer(self, query: str, citations: list[Citation]) -> str:
        content = "\n".join([query, *(citation.content for citation in citations)])
        async with httpx.AsyncClient(transport=self._transport, timeout=_TIMEOUT) as client:
            response = await client.post(
                f"{self._base_url.rstrip('/')}/chat/completions",
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": content}],
                },
            )
        text = response.json()["choices"][0]["message"]["content"]
        if not isinstance(text, str):
            raise TypeError("Ollama content must be text")
        return text
