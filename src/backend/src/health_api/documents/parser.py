"""Parser port shared by the stub and local parsers."""

from typing import Protocol, runtime_checkable

from health_api.documents.text_layer_parser import ParsedPage


@runtime_checkable
class Parser(Protocol):
    async def parse(self, *, file_name: str, data: bytes) -> list[ParsedPage]: ...
