import json

import httpx
import pytest

from health_api.documents.ollama_embeddings import OllamaEmbeddings

pytestmark = pytest.mark.unit

_BASE_URL = "http://127.0.0.1:11434/v1"
_MODEL = "nomic-embed-text"
_TEXT = "DemoMarker value is 10 units."


def test_the_embed_client_should_post_the_text() -> None:
    # Given
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": [{"embedding": [0.1, 0.2]}]})

    client = OllamaEmbeddings(
        base_url=_BASE_URL,
        model=_MODEL,
        transport=httpx.MockTransport(handler),
    )

    # When
    vector = client.embed(_TEXT)

    # Then
    assert vector == [0.1, 0.2]
    assert str(seen[0].url) == f"{_BASE_URL}/embeddings"
    body = json.loads(seen[0].content)
    assert body["model"] == _MODEL
    assert body["input"] == _TEXT
