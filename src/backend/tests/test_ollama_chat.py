import asyncio
import json

import httpx
import pytest

from health_api.chat.ollama_chat_model import OllamaChatModel

pytestmark = pytest.mark.unit

OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"
OLLAMA_CHAT_MODEL = "llama3.1"


def test_ollama_should_post_to_the_configured_model() -> None:
    # Given
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={})

    model = OllamaChatModel(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_CHAT_MODEL,
        transport=httpx.MockTransport(handler),
    )

    # When
    asyncio.run(model.answer("What is the DemoMarker value?", []))

    # Then
    assert len(seen) == 1
    assert str(seen[0].url).startswith(OLLAMA_BASE_URL)
    assert json.loads(seen[0].content)["model"] == OLLAMA_CHAT_MODEL
