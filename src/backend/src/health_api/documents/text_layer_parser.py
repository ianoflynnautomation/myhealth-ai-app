from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


@dataclass(frozen=True)
class ParsedPage:
    page_number: int
    text: str


def parse_text_layer(data: bytes) -> list[ParsedPage]:
    reader = PdfReader(BytesIO(data))
    return [
        ParsedPage(page_number=index, text=page.extract_text() or "")
        for index, page in enumerate(reader.pages, start=1)
    ]
