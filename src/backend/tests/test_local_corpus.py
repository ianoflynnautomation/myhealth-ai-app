from collections.abc import Sequence

import pytest

from health_api.documents.local_corpus import LocalCorpus
from health_api.documents.memory_corpus import StoredChunk, StoredDocument
from health_api.documents.qdrant_corpus import CorpusPoint
from health_api.documents.qdrant_query import HybridQuery
from health_api.documents.text_layer_parser import ParsedPage

pytestmark = pytest.mark.unit

_TEXT = "DemoMarker value is 10 units."
_QUESTION = "What is the DemoMarker value?"


class _Embedder:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 0.5]


class _Index:
    def __init__(self) -> None:
        self.points: dict[str, CorpusPoint] = {}
        self.upserts = 0
        self.queries: list[HybridQuery] = []

    def upsert(self, points: Sequence[CorpusPoint]) -> None:
        self.upserts += 1
        for point in points:
            self.points[point.id] = point

    def search(self, query: HybridQuery) -> list[CorpusPoint]:
        self.queries.append(query)
        return list(self.points.values())


def test_the_local_corpus_should_return_the_stored_page() -> None:
    # Given
    index = _Index()
    corpus = LocalCorpus(embedder=_Embedder(), index=index)
    pages = [ParsedPage(page_number=1, text=_TEXT)]

    # When
    stored, created = corpus.add(
        document_id="doc-1",
        source_file="example.pdf",
        pages=pages,
    )
    again, created_again = corpus.add(
        document_id="doc-1",
        source_file="example.pdf",
        pages=pages,
    )
    hits = corpus.search(_QUESTION)

    # Then
    assert created is True
    assert stored == StoredDocument(
        id="doc-1",
        source_file="example.pdf",
        page_count=1,
        chunk_count=1,
    )
    assert index.points["doc-1:1"] == CorpusPoint(
        id="doc-1:1",
        vector=(float(len(_TEXT)), 0.5),
        payload={"sourceFile": "example.pdf", "sourcePage": 1, "content": _TEXT},
    )
    assert created_again is False
    assert again == stored
    assert index.upserts == 1
    assert index.queries[0].bm25_text == _QUESTION
    assert index.queries[0].dense_vector == (float(len(_QUESTION)), 0.5)
    assert hits == [
        StoredChunk(
            document_id="doc-1",
            source_file="example.pdf",
            page_number=1,
            text=_TEXT,
        )
    ]
