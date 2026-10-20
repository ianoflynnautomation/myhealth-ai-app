from typing import Self

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, model_validator

from health_api.chat.quoting_chat_model import quote
from health_api.documents.memory_corpus import MemoryCorpus
from health_api.http.errors import ApiError, register_error_handler


def _validation_message(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "Request is invalid."
    message = str(errors[0]["msg"])
    prefix = "Value error, "
    if message.startswith(prefix):
        return message.removeprefix(prefix)
    return message


def _require_json(request: Request) -> None:
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media_type != "application/json":
        raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "Chat body must be JSON.")


_JSON = Depends(_require_json)


class ChatMessage(BaseModel):
    role: str
    content: str

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message content must not be blank.")
        return value


class ChatRequest(BaseModel):
    messages: list[ChatMessage]

    @model_validator(mode="after")
    def at_least_one_message(self) -> Self:
        if not self.messages:
            raise ValueError("At least one message is required.")
        return self


class CitationResponse(BaseModel):
    id: str
    source_file: str = Field(serialization_alias="sourceFile")
    source_page: int = Field(serialization_alias="sourcePage", ge=1)
    content: str


class ChatResponse(BaseModel):
    output_text: str = Field(serialization_alias="outputText")
    citations: list[CitationResponse]


def register_chat(app: FastAPI, corpus: MemoryCorpus) -> None:
    register_error_handler(app)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": _validation_message(exc),
                    "details": {},
                }
            },
        )

    @app.post("/chat")
    def chat(body: ChatRequest, _: None = _JSON) -> ChatResponse:
        hits = corpus.search(body.messages[-1].content)
        content = quote(hits)
        citations = [
            CitationResponse(
                id=f"{hit.document_id}:{hit.page_number}",
                source_file=hit.source_file,
                source_page=hit.page_number,
                content=hit.text,
            )
            for hit in hits[:1]
        ]
        return ChatResponse(output_text=content, citations=citations)
