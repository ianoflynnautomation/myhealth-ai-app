import asyncio
import inspect
import sys

import pytest

from health_api.documents.docling_parser import DoclingParser
from health_api.documents.parser import Parser
from health_api.documents.text_layer_parser import ParsedPage, TextLayerParser

pytestmark = pytest.mark.unit


def test_docling_parser_should_return_converter_pages() -> None:
    # Given
    class Converter:
        def convert(self, *, file_name: str, data: bytes) -> dict[int, str]:
            assert file_name == "example.pdf"
            assert data == b"pdf-bytes"
            return {1: "DemoMarker value is 10 units."}

    parser = DoclingParser(Converter())

    # When
    pages = asyncio.run(parser.parse(file_name="example.pdf", data=b"pdf-bytes"))

    # Then
    assert pages == [ParsedPage(page_number=1, text="DemoMarker value is 10 units.")]
    assert "docling" not in sys.modules


def test_both_parsers_should_match_the_parser_protocol() -> None:
    # Given
    class Converter:
        def convert(self, *, file_name: str, data: bytes) -> dict[int, str]:
            return {1: "page"}

    # When
    text_layer: Parser = TextLayerParser()
    docling: Parser = DoclingParser(Converter())

    # Then
    assert isinstance(text_layer, Parser)
    assert isinstance(docling, Parser)
    assert inspect.iscoroutinefunction(text_layer.parse)
    assert inspect.iscoroutinefunction(docling.parse)
