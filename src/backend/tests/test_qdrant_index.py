import importlib
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from health_api.documents import qdrant_index as qdrant_index_module

pytestmark = pytest.mark.unit


class _FakeClient:
    existing = True

    def __init__(self, url: str) -> None:
        self.url = url
        self.indexes: list[dict[str, Any]] = []
        _FakeClient.last = self

    def collection_exists(self, _name: str) -> bool:
        return _FakeClient.existing

    def create_collection(self, **_kwargs: Any) -> None:
        return None

    def create_payload_index(self, **kwargs: Any) -> None:
        self.indexes.append(kwargs)

    last: "_FakeClient"


def _params(**kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def _fake_modules() -> dict[str, ModuleType]:
    client_module = ModuleType("qdrant_client")
    client_module.QdrantClient = _FakeClient  # type: ignore[attr-defined]
    models = ModuleType("qdrant_client.models")
    for name in ("VectorParams", "TextIndexParams", "TextScoringParams"):
        setattr(models, name, _params)
    models.Distance = SimpleNamespace(COSINE="Cosine")  # type: ignore[attr-defined]
    models.TokenizerType = SimpleNamespace(WORD="word")  # type: ignore[attr-defined]
    models.TextScoringType = SimpleNamespace(BM25="bm25")  # type: ignore[attr-defined]
    return {"qdrant_client": client_module, "qdrant_client.models": models}


def test_an_existing_collection_should_get_a_bm25_scored_text_index(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    modules = _fake_modules()

    def import_module(name: str) -> ModuleType:
        return modules[name]

    monkeypatch.setattr(importlib, "import_module", import_module)
    _FakeClient.existing = True

    # When
    qdrant_index_module.qdrant_index("http://qdrant:6333")

    # Then
    [index] = _FakeClient.last.indexes
    assert index["field_name"] == "content"
    assert index["field_schema"].scoring.type == "bm25"
