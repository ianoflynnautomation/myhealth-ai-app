import pytest
from pydantic import ValidationError

from health_api.config import Settings

pytestmark = pytest.mark.unit


def test_stub_settings_should_need_no_service_urls() -> None:
    # Given

    # When
    settings = Settings(profile="stub")

    # Then
    assert settings.profile == "stub"


def test_local_settings_should_require_qdrant_url() -> None:
    # Given

    # When
    with pytest.raises(ValidationError, match="qdrant_url"):
        Settings(profile="local")

    # Then


def test_local_settings_should_require_ollama_base_url() -> None:
    # Given

    # When
    with pytest.raises(ValidationError, match="ollama_base_url"):
        Settings(profile="local", qdrant_url="http://127.0.0.1:6333")

    # Then


def test_local_settings_should_require_a_chat_model() -> None:
    # Given

    # When
    with pytest.raises(ValidationError, match="ollama_chat_model"):
        Settings(
            profile="local",
            qdrant_url="http://127.0.0.1:6333",
            ollama_base_url="http://127.0.0.1:11434/v1",
        )

    # Then


def test_local_settings_should_require_an_embed_model() -> None:
    # Given

    # When
    with pytest.raises(ValidationError, match="ollama_embed_model"):
        Settings(
            profile="local",
            qdrant_url="http://127.0.0.1:6333",
            ollama_base_url="http://127.0.0.1:11434/v1",
            ollama_chat_model="llama3.1",
        )

    # Then
