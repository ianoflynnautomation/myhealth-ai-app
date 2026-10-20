import asyncio
import sys
from collections.abc import Sequence

import pytest

from health_api.documents.qdrant_corpus import CorpusPoint, QdrantCorpus
from health_api.documents.text_layer_parser import ParsedPage

pytestmark = pytest.mark.unit


class _FakeClient:
    def __init__(self) -> None:
        self.points: dict[str, CorpusPoint] = {}

    def upsert(self, points: Sequence[CorpusPoint]) -> None:
        for point in points:
            self.points[point.id] = point


def test_qdrant_corpus_should_upsert_one_point_per_page() -> None:
    # Given
    client = _FakeClient()
    corpus = QdrantCorpus(client)
    pages = [
        ParsedPage(page_number=1, text="alpha"),
        ParsedPage(page_number=2, text="beta"),
    ]

    # When
    asyncio.run(
        corpus.add(
            document_id="doc-1",
            source_file="example.pdf",
            pages=pages,
            vectors=[[0.1, 0.2], [0.3, 0.4]],
        )
    )

    # Then
    assert set(client.points) == {"doc-1:1", "doc-1:2"}
    assert client.points["doc-1:1"] == CorpusPoint(
        id="doc-1:1",
        vector=(0.1, 0.2),
        payload={"sourceFile": "example.pdf", "sourcePage": 1, "content": "alpha"},
    )
    assert client.points["doc-1:2"].payload == {
        "sourceFile": "example.pdf",
        "sourcePage": 2,
        "content": "beta",
    }
    assert "qdrant_client" not in sys.modules
