from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_COMPOSE = Path(__file__).resolve().parents[1].parents[1] / "compose.yaml"
_SETTINGS = (
    "PROFILE: local",
    "QDRANT_URL: http://qdrant:6333",
    "OLLAMA_BASE_URL: http://ollama:11434/v1",
    "OLLAMA_CHAT_MODEL: llama3.1",
    "OLLAMA_EMBED_MODEL: nomic-embed-text",
    "DATA_DIR: /data",
)
_PORTS = (
    "127.0.0.1:8080",
    "127.0.0.1:8000",
    "127.0.0.1:6333",
    "127.0.0.1:11434",
)


def test_compose_should_set_profile_local() -> None:
    # Given
    text = _COMPOSE.read_text()

    # When
    images = [
        line.split(":", 1)[1].strip()
        for line in text.splitlines()
        if line.strip().startswith("image:")
    ]

    # Then
    for setting in _SETTINGS:
        assert setting in text
    for port in _PORTS:
        assert port in text
    assert "./data:/data" in text
    assert images
    for image in images:
        assert ":" in image
        assert not image.endswith(":latest")


def test_compose_should_pull_the_two_models() -> None:
    # Given
    text = _COMPOSE.read_text()
    api = text.split("\n  api:\n", 1)[1].split("\n  qdrant:\n", 1)[0]

    # When
    pulls = [line.strip() for line in text.splitlines() if "ollama pull " in line]

    # Then
    assert any("ollama pull llama3.1" in line for line in pulls)
    assert any("ollama pull nomic-embed-text" in line for line in pulls)
    assert "model-pull" in api
    assert "service_completed_successfully" in api
    assert "ollama-models:" in text
    assert "qdrant-data:" in text


def test_compose_should_publish_on_localhost_only() -> None:
    # Given
    lines = _COMPOSE.read_text().splitlines()

    # When
    published: list[str] = []
    in_ports = False
    for line in lines:
        stripped = line.strip()
        if stripped == "ports:":
            in_ports = True
            continue
        if in_ports and stripped.startswith("- "):
            published.append(stripped[2:].strip().strip("\"'"))
            continue
        in_ports = False

    # Then
    assert published
    for port in published:
        assert port.startswith("127.0.0.1:"), port
