import asyncio
import json

import httpx
import pytest

from health_api.chat.ollama_chat_model import Citation, OllamaChatModel

pytestmark = pytest.mark.unit

OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"
OLLAMA_CHAT_MODEL = "llama3.1"
_MODEL_TEXT = "cited answer"


def _response(content: str = _MODEL_TEXT) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})


def test_ollama_should_post_to_the_configured_model() -> None:
    # Given
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _response()

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


def test_the_ollama_prompt_should_contain_citations_only() -> None:
    # Given
    pdf = b"%PDF-1.7 synthetic-bytes"
    citations = [
        Citation(content="DemoMarker value is 10 units."),
        Citation(content="Second page marker is 4."),
    ]
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _response()

    model = OllamaChatModel(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_CHAT_MODEL,
        transport=httpx.MockTransport(handler),
    )

    # When
    asyncio.run(model.answer("What is the DemoMarker value?", citations))

    # Then
    body = seen[0].content.decode()
    assert "DemoMarker value is 10 units." in body
    assert "Second page marker is 4." in body
    assert pdf.decode() not in body


def test_ollama_should_return_the_model_text() -> None:
    # Given
    def handler(_request: httpx.Request) -> httpx.Response:
        return _response()

    model = OllamaChatModel(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_CHAT_MODEL,
        transport=httpx.MockTransport(handler),
    )

    # When
    text = asyncio.run(model.answer("What is the DemoMarker value?", []))

    # Then
    assert text == "cited answer"
