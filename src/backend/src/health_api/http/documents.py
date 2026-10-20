import hashlib

from fastapi import FastAPI, File, Response, UploadFile
from pydantic import BaseModel, Field

from health_api.documents.memory_corpus import MemoryCorpus
from health_api.documents.text_layer_parser import parse_text_layer
from health_api.http.errors import ApiError, register_error_handler

_UPLOAD = File()


class DocumentResponse(BaseModel):
    id: str
    source_file: str = Field(serialization_alias="sourceFile")
    page_count: int = Field(serialization_alias="pageCount", ge=0)
    chunk_count: int = Field(serialization_alias="chunkCount", ge=0)


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


def register_documents(app: FastAPI, corpus: MemoryCorpus) -> None:
    register_error_handler(app)

    @app.get("/documents")
    def list_documents() -> DocumentListResponse:
        return DocumentListResponse(
            documents=[
                DocumentResponse(
                    id=stored.id,
                    source_file=stored.source_file,
                    page_count=stored.page_count,
                    chunk_count=stored.chunk_count,
                )
                for stored in corpus.documents.values()
            ]
        )

    @app.post("/documents", status_code=201)
    async def upload_document(response: Response, file: UploadFile = _UPLOAD) -> DocumentResponse:
        data = await file.read()
        if not data.startswith(b"%PDF"):
            raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "Upload must be a PDF.")
        pages = parse_text_layer(data)
        if not any(page.text.strip() for page in pages):
            raise ApiError(422, "VALIDATION_ERROR", "PDF has no text layer.")
        stored, created = corpus.add(
            document_id=hashlib.sha256(data).hexdigest(),
            source_file=file.filename or "upload.pdf",
            pages=pages,
        )
        if not created:
            response.status_code = 200
        return DocumentResponse(
            id=stored.id,
            source_file=stored.source_file,
            page_count=stored.page_count,
            chunk_count=stored.chunk_count,
        )
