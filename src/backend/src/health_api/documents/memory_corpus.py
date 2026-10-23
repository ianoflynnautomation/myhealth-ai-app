import re
from dataclasses import dataclass
from typing import Protocol

from health_api.documents.text_layer_parser import ParsedPage

_TOKEN = re.compile(r"[0-9A-Za-z]+")


def _tokens(text: str) -> set[str]:
    return {token.casefold() for token in _TOKEN.findall(text)}


@dataclass(frozen=True)
class StoredChunk:
    document_id: str
    source_file: str
    page_number: int
    text: str


@dataclass(frozen=True)
class StoredDocument:
    id: str
    source_file: str
    page_count: int
    chunk_count: int


class StoredCorpus(Protocol):
    documents: dict[str, StoredDocument]

    def add(
        self, *, document_id: str, source_file: str, pages: list[ParsedPage]
    ) -> tuple[StoredDocument, bool]: ...

    def search(self, query: str) -> list[StoredChunk]: ...


class MemoryCorpus:
    def __init__(self) -> None:
        self.documents: dict[str, StoredDocument] = {}
        self.chunks: list[StoredChunk] = []

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
        chunks = [
            StoredChunk(
                document_id=document_id,
                source_file=source_file,
                page_number=page.page_number,
                text=page.text,
            )
            for page in pages
        ]
        self.chunks.extend(chunks)
        stored = StoredDocument(
            id=document_id,
            source_file=source_file,
            page_count=len(pages),
            chunk_count=len(chunks),
        )
        self.documents[document_id] = stored
        return stored, True

    def search(self, query: str) -> list[StoredChunk]:
        needles = _tokens(query)
        if not needles:
            return []
        return [chunk for chunk in self.chunks if needles & _tokens(chunk.text)]
