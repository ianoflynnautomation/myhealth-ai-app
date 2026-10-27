"""Hybrid query for the pages collection.

The dense leg is the embedding vector. The text leg is BM25 on the page text.
Qdrant fuses the two with reciprocal rank fusion. This module does not import
qdrant_client.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

COLLECTION = "pages"
DENSE_SIZE = 768


@dataclass(frozen=True)
class HybridQuery:
    collection: str
    dense_size: int
    dense_vector: tuple[float, ...]
    bm25_text: str
    fusion: str


class HybridClient(Protocol):
    def query(self, query: HybridQuery) -> None: ...


def hybrid_query(*, vector: Sequence[float], text: str) -> HybridQuery:
    return HybridQuery(
        collection=COLLECTION,
        dense_size=DENSE_SIZE,
        dense_vector=tuple(vector),
        bm25_text=text,
        fusion="rrf",
    )


def submit_hybrid_query(client: HybridClient, *, vector: Sequence[float], text: str) -> None:
    client.query(hybrid_query(vector=vector, text=text))
