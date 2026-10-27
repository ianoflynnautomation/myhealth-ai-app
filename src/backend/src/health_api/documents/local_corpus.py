"""Corpus that embeds pages and searches them.

add and search are synchronous. The document route calls them without await.
"""

from collections.abc import Sequence
from typing import Protocol

from health_api.documents.memory_corpus import StoredChunk, StoredDocument
from health_api.documents.qdrant_corpus import CorpusPoint
from health_api.documents.qdrant_query import HybridQuery, hybrid_query
from health_api.documents.text_layer_parser import ParsedPage


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


class PageIndex(Protocol):
    def upsert(self, points: Sequence[CorpusPoint]) -> None: ...

    def search(self, query: HybridQuery) -> Sequence[CorpusPoint]: ...


class LocalCorpus:
    def __init__(self, *, embedder: Embedder, index: PageIndex) -> None:
        self._embedder = embedder
        self._index = index
        self.documents: dict[str, StoredDocument] = {}

    def add(
        self,
        *,
        document_id: str,
        source_file: str,
        pages: list[ParsedPage],
    ) -> tuple[StoredDocument, bool]:
        existing = self.documents.get(document_id)
        if existing is not None:
            return existing, False
        points = [
            CorpusPoint(
                id=f"{document_id}:{page.page_number}",
                vector=tuple(self._embedder.embed(page.text)),
                payload={
                    "sourceFile": source_file,
                    "sourcePage": page.page_number,
                    "content": page.text,
                },
            )
            for page in pages
        ]
        self._index.upsert(points)
        stored = StoredDocument(
            id=document_id,
            source_file=source_file,
            page_count=len(pages),
            chunk_count=len(points),
        )
        self.documents[document_id] = stored
        return stored, True

    def search(self, query: str) -> list[StoredChunk]:
        found = self._index.search(hybrid_query(vector=self._embedder.embed(query), text=query))
        chunks: list[StoredChunk] = []
        for point in found:
            document_id, separator, _page = point.id.rpartition(":")
            if separator != ":":
                continue
            chunks.append(
                StoredChunk(
                    document_id=document_id,
                    source_file=str(point.payload["sourceFile"]),
                    page_number=int(str(point.payload["sourcePage"])),
                    text=str(point.payload["content"]),
                )
            )
        return chunks
