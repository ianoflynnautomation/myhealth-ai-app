from fastapi import FastAPI
from pydantic import BaseModel, Field

from health_api.chat.quoting_chat_model import quote
from health_api.documents.memory_corpus import MemoryCorpus


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class CitationResponse(BaseModel):
    id: str
    source_file: str = Field(serialization_alias="sourceFile")
    source_page: int = Field(serialization_alias="sourcePage", ge=1)
    content: str


class ChatResponse(BaseModel):
    output_text: str = Field(serialization_alias="outputText")
    citations: list[CitationResponse]


def register_chat(app: FastAPI, corpus: MemoryCorpus) -> None:
    @app.post("/chat")
    def chat(body: ChatRequest) -> ChatResponse:
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
