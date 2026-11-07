"""Original PDF bytes kept under DATA_DIR in the local profile.

The stub profile has no store, so it never writes under data/.
"""

from pathlib import Path
from typing import Protocol


class PdfStore(Protocol):
    def keep(self, *, document_id: str, data: bytes) -> None: ...


class DirectoryPdfStore:
    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def keep(self, *, document_id: str, data: bytes) -> None:
        path = self._directory / f"{document_id}.pdf"
        if path.exists():
            return
        self._directory.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
