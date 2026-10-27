"""Qdrant page index.

Importing this module does not import qdrant_client. The client is loaded
inside qdrant_index.
"""

import importlib
import uuid
from collections.abc import Sequence
from typing import Any, cast

from health_api.documents.local_corpus import PageIndex
from health_api.documents.qdrant_corpus import CorpusPoint
from health_api.documents.qdrant_query import COLLECTION, DENSE_SIZE, HybridQuery

_NAMESPACE = uuid.UUID("6f1b1c2a-4e3d-4a7b-9c8d-0e1f2a3b4c5d")


def qdrant_index(url: str) -> PageIndex:
    try:
        client_module = importlib.import_module("qdrant_client")
        models = importlib.import_module("qdrant_client.models")
    except ImportError as error:
        raise RuntimeError(
            "qdrant_client is not installed. Install the local group with `uv sync --group local`."
        ) from error
    client: Any = client_module.QdrantClient(url=url)
    _ensure_collection(client, models)
    return _QdrantIndex(client, models)


def _payload(point: Any) -> dict[object, object] | None:
    raw = cast(object, point.payload or {})
    if not isinstance(raw, dict):
        return None
    return cast(dict[object, object], raw)


def _ensure_collection(client: Any, models: Any) -> None:
    if client.collection_exists(COLLECTION):
        return
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={
            "dense": models.VectorParams(size=DENSE_SIZE, distance=models.Distance.COSINE),
        },
    )
    client.create_payload_index(
        collection_name=COLLECTION,
        field_name="content",
        field_schema=models.TextIndexParams(
            type="text",
            tokenizer=models.TokenizerType.WORD,
            lowercase=True,
        ),
    )


class _QdrantIndex:
    def __init__(self, client: Any, models: Any) -> None:
        self._client = client
        self._models = models

    def upsert(self, points: Sequence[CorpusPoint]) -> None:
        structs: list[Any] = []
        for point in points:
            payload = dict(point.payload)
            payload["pointId"] = point.id
            structs.append(
                self._models.PointStruct(
                    id=str(uuid.uuid5(_NAMESPACE, point.id)),
                    vector={"dense": list(point.vector)},
                    payload=payload,
                )
            )
        self._client.upsert(collection_name=COLLECTION, points=structs)

    def search(self, query: HybridQuery) -> list[CorpusPoint]:
        result = self._client.query_points(
            collection_name=query.collection,
            prefetch=[
                self._models.Prefetch(
                    query=self._models.TextQuery(text=query.bm25_text),
                    using="content",
                    limit=20,
                ),
                self._models.Prefetch(
                    query=list(query.dense_vector),
                    using="dense",
                    limit=20,
                ),
            ],
            query=self._models.RrfQuery(rrf=self._models.Rrf()),
            limit=1,
            with_payload=True,
        )
        found: list[CorpusPoint] = []
        for point in result.points:
            payload = _payload(point)
            if payload is None:
                continue
            point_id = payload.get("pointId")
            page_number = payload.get("sourcePage")
            source_file = payload.get("sourceFile")
            content = payload.get("content")
            if not isinstance(point_id, str) or not isinstance(source_file, str):
                continue
            if not isinstance(content, str):
                continue
            if isinstance(page_number, bool) or not isinstance(page_number, int):
                continue
            found.append(
                CorpusPoint(
                    id=point_id,
                    vector=(),
                    payload={
                        "sourceFile": source_file,
                        "sourcePage": page_number,
                        "content": content,
                    },
                )
            )
        return found
