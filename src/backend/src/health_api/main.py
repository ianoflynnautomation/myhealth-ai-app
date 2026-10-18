import os

from fastapi import FastAPI

from health_api.documents.memory_corpus import MemoryCorpus
from health_api.http.documents import register_documents


def create_app(*, documents_enabled: bool = False) -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    if documents_enabled:
        register_documents(app, MemoryCorpus())
    return app


def _documents_enabled_from_env() -> bool:
    return os.environ.get("DOCUMENTS_ENABLED", "").lower() in {"1", "true", "yes"}


app = create_app(documents_enabled=_documents_enabled_from_env())
