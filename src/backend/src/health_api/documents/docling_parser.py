"""Local parser over an injected page converter.

The Docling package is not imported here. A later factory supplies the real
converter. Tests pass a fake.
"""

from collections.abc import Mapping
from typing import Protocol

from health_api.documents.text_layer_parser import ParsedPage


class PageConverter(Protocol):
    def convert(self, *, file_name: str, data: bytes) -> Mapping[int, str]: ...


class DoclingParser:
    def __init__(self, converter: PageConverter) -> None:
        self._converter = converter

    async def parse(self, *, file_name: str, data: bytes) -> list[ParsedPage]:
        pages = self._converter.convert(file_name=file_name, data=data)
        return [ParsedPage(page_number=number, text=pages[number]) for number in sorted(pages)]
