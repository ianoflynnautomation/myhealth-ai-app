import hashlib

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, Field

from health_api.documents.memory_corpus import MemoryCorpus
from health_api.documents.text_layer_parser import parse_text_layer

_UPLOAD = File()


class DocumentResponse(BaseModel):
    id: str
    source_file: str = Field(serialization_alias="sourceFile")
    page_count: int = Field(serialization_alias="pageCount", ge=0)
    chunk_count: int = Field(serialization_alias="chunkCount", ge=0)


def register_documents(app: FastAPI, corpus: MemoryCorpus) -> None:
    @app.post("/documents", status_code=201)
    async def upload_document(file: UploadFile = _UPLOAD) -> DocumentResponse:
        data = await file.read()
        pages = parse_text_layer(data)
        stored = corpus.add(
            document_id=hashlib.sha256(data).hexdigest(),
            source_file=file.filename or "upload.pdf",
            pages=pages,
        )
        return DocumentResponse(
            id=stored.id,
            source_file=stored.source_file,
            page_count=stored.page_count,
            chunk_count=stored.chunk_count,
        )
