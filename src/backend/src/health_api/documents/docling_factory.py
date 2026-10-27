"""Docling page converter.

Importing this module does not import docling. The package is loaded inside
docling_converter, and only when the local group is installed.
"""

import importlib
from io import BytesIO

from health_api.documents.docling_parser import PageConverter


class _DoclingConverter:
    def convert(self, *, file_name: str, data: bytes) -> dict[int, str]:
        document_converter = importlib.import_module("docling.document_converter")
        base_models = importlib.import_module("docling.datamodel.base_models")
        stream = base_models.DocumentStream(name=file_name, stream=BytesIO(data))
        document = document_converter.DocumentConverter().convert(stream).document
        pages: dict[int, str] = {}
        for page in document.pages.values():
            page_number = int(page.page_no)
            pages[page_number] = str(document.export_to_text(page_no=page_number))
        return pages


def docling_converter() -> PageConverter:
    try:
        importlib.import_module("docling")
    except ImportError as error:
        raise RuntimeError(
            "docling is not installed. Install the local group with `uv sync --group local`."
        ) from error
    return _DoclingConverter()
