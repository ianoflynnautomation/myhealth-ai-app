"""Ollama embeddings over an injected HTTP transport.

Tests pass ``httpx.MockTransport``. This module does not open a port.
The base URL includes ``/v1``, and the client posts to ``{base}/embeddings``.
"""

from typing import cast

import httpx


class OllamaEmbeddings:
    def __init__(self, *, base_url: str, model: str, transport: httpx.BaseTransport) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._transport = transport

    def embed(self, text: str) -> list[float]:
        with httpx.Client(transport=self._transport) as client:
            response = client.post(
                f"{self._base_url}/embeddings",
                json={"model": self._model, "input": text},
            )
        vector = response.json()["data"][0]["embedding"]
        if not isinstance(vector, list):
            raise TypeError("Ollama embedding must be a list")
        values: list[float] = []
        for item in cast(list[object], vector):
            if isinstance(item, bool) or not isinstance(item, int | float):
                raise TypeError("Ollama embedding must be a list")
            values.append(float(item))
        return values
