from fastapi import FastAPI

from health_api.documents.memory_corpus import MemoryCorpus
from health_api.http.documents import register_documents


def create_app() -> FastAPI:
    app = FastAPI()
    corpus = MemoryCorpus()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    register_documents(app, corpus)
    return app


app = create_app()
