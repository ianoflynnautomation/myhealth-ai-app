"""Qdrant corpus over an injected client.

The qdrant_client package is not imported here. Tests pass a fake.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from health_api.documents.text_layer_parser import ParsedPage


@dataclass(frozen=True)
class CorpusPoint:
    id: str
    vector: tuple[float, ...]
    payload: dict[str, str | int]


class VectorClient(Protocol):
    def upsert(self, points: Sequence[CorpusPoint]) -> None: ...


class QdrantCorpus:
    def __init__(self, client: VectorClient) -> None:
        self._client = client

    async def add(
        self,
        *,
        document_id: str,
        source_file: str,
        pages: list[ParsedPage],
        vectors: list[list[float]],
    ) -> None:
        points = [
            CorpusPoint(
                id=f"{document_id}:{page.page_number}",
                vector=tuple(vector),
                payload={
                    "sourceFile": source_file,
                    "sourcePage": page.page_number,
                    "content": page.text,
                },
            )
            for page, vector in zip(pages, vectors, strict=True)
        ]
        self._client.upsert(points)
