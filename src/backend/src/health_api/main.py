import os

from fastapi import FastAPI

from health_api.documents.memory_corpus import MemoryCorpus
from health_api.http.chat import register_chat
from health_api.http.documents import register_documents


def create_app(*, documents_enabled: bool = False, chat_enabled: bool = False) -> FastAPI:
    app = FastAPI()
    corpus = MemoryCorpus()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    if documents_enabled:
        register_documents(app, corpus)
    if chat_enabled:
        register_chat(app, corpus)
    return app


def _enabled_from_env(name: str) -> bool:
    return os.environ.get(name, "").lower() in {"1", "true", "yes"}


app = create_app(
    documents_enabled=_enabled_from_env("DOCUMENTS_ENABLED"),
    chat_enabled=_enabled_from_env("CHAT_ENABLED"),
)
