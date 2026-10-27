import sys

import pytest

from health_api.documents.qdrant_query import HybridQuery, submit_hybrid_query

pytestmark = pytest.mark.unit


def test_the_hybrid_query_should_carry_the_text_and_the_vector() -> None:
    # Given
    sys.modules.pop("qdrant_client", None)

    seen: list[HybridQuery] = []

    class Client:
        def query(self, query: HybridQuery) -> None:
            seen.append(query)

    # When
    submit_hybrid_query(Client(), vector=[0.25, 0.5], text="Where was the zebra?")

    # Then
    assert seen[0].dense_vector == (0.25, 0.5)
    assert seen[0].bm25_text == "Where was the zebra?"
    assert seen[0].dense_size == 768
    assert seen[0].collection == "pages"
    assert seen[0].fusion == "rrf"
    assert "qdrant_client" not in sys.modules
