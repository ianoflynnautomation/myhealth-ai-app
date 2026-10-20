import importlib
import sys

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


def test_local_settings_should_require_a_data_dir() -> None:
    # Given
    configured = {
        "qdrant_url": "http://127.0.0.1:6333",
        "ollama_base_url": "http://127.0.0.1:11434/v1",
        "ollama_chat_model": "llama3.1",
        "ollama_embed_model": "nomic-embed-text",
    }

    # When
    with pytest.raises(ValidationError, match="data_dir"):
        Settings(profile="local", **configured)

    # Then
    settings = Settings(profile="local", data_dir="../../data", **configured)
    assert settings.data_dir == "../../data"


def test_the_stub_app_should_not_import_local_clients() -> None:
    # Given
    sys.modules.pop("docling", None)
    sys.modules.pop("qdrant_client", None)

    # When
    import health_api.main as main

    importlib.reload(main)
    main.create_app()

    # Then
    assert "docling" not in sys.modules
    assert "qdrant_client" not in sys.modules
