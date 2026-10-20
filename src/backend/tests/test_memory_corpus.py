import pytest

from health_api.documents.memory_corpus import MemoryCorpus
from health_api.documents.text_layer_parser import ParsedPage

pytestmark = pytest.mark.unit


def test_search_should_return_the_page_with_the_question_words() -> None:
    # Given
    corpus = MemoryCorpus()
    corpus.add(
        document_id="doc-1",
        source_file="example.pdf",
        pages=[ParsedPage(page_number=1, text="DemoMarker value is 10 units.")],
    )

    # When
    found = corpus.search("DemoMarker")

    # Then
    assert len(found) == 1
    assert found[0].text == "DemoMarker value is 10 units."
    assert found[0].source_file == "example.pdf"
    assert found[0].page_number == 1

    # When
    missed = corpus.search("not-in-the-page")

    # Then
    assert missed == []
