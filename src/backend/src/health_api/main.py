import importlib
import os
from collections.abc import Callable, Sequence

import httpx
from fastapi import FastAPI

from health_api.chat.ollama_chat_model import Citation, OllamaChatModel
from health_api.config import Settings
from health_api.documents.docling_factory import docling_converter
from health_api.documents.docling_parser import DoclingParser
from health_api.documents.local_corpus import LocalCorpus
from health_api.documents.memory_corpus import MemoryCorpus, StoredCorpus
from health_api.documents.ollama_embeddings import OllamaEmbeddings
from health_api.documents.parser import Parser
from health_api.documents.qdrant_index import qdrant_index
from health_api.http.chat import ChatModel, CitationResponse, register_chat
from health_api.http.documents import register_documents


def create_app(
    settings: Settings | None = None,
    *,
    documents_enabled: bool = True,
    chat_enabled: bool = True,
    corpus: StoredCorpus | None = None,
    parser_factory: Callable[[Settings], Parser] | None = None,
    corpus_factory: Callable[[Settings], StoredCorpus] | None = None,
    chat_model_factory: Callable[[Settings], ChatModel] | None = None,
) -> FastAPI:
    settings = Settings() if settings is None else settings
    app = FastAPI()
    parser: Parser | None
    chat_model: ChatModel | None
    if settings.profile == "local":
        if parser_factory is None or corpus_factory is None or chat_model_factory is None:
            _require_local_group()
        if parser_factory is None:
            parser_factory = _parser_from_settings
        if corpus_factory is None:
            corpus_factory = _corpus_from_settings
        if chat_model_factory is None:
            chat_model_factory = _chat_from_settings
        parser = parser_factory(settings)
        active_corpus = corpus_factory(settings)
        chat_model = chat_model_factory(settings)
    else:
        parser = None
        chat_model = None
        active_corpus = MemoryCorpus() if corpus is None else corpus

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    if documents_enabled:
        register_documents(app, active_corpus, parser=parser)
    if chat_enabled:
        register_chat(app, active_corpus, chat_model=chat_model)
    return app


def _required(value: str | None) -> str:
    if value is None or value.strip() == "":
        raise RuntimeError("local settings are incomplete")
    return value


def _parser_from_settings(_settings: Settings) -> Parser:
    return DoclingParser(docling_converter())


def _corpus_from_settings(settings: Settings) -> StoredCorpus:
    embeddings = OllamaEmbeddings(
        base_url=_required(settings.ollama_base_url),
        model=_required(settings.ollama_embed_model),
        transport=httpx.HTTPTransport(),
    )
    return LocalCorpus(embedder=embeddings, index=qdrant_index(_required(settings.qdrant_url)))


class _OllamaChat:
    def __init__(self, model: OllamaChatModel) -> None:
        self._model = model

    async def answer(self, query: str, citations: Sequence[CitationResponse]) -> str:
        quoted = [Citation(content=citation.content) for citation in citations]
        return await self._model.answer(query, quoted)


def _chat_from_settings(settings: Settings) -> ChatModel:
    model = OllamaChatModel(
        base_url=_required(settings.ollama_base_url),
        model=_required(settings.ollama_chat_model),
        transport=httpx.AsyncHTTPTransport(),
    )
    return _OllamaChat(model)


def _require_local_group() -> None:
    missing: list[str] = []
    for module in ("docling", "qdrant_client"):
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(module)
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(
            f"{names} is not installed. Install the local group with `uv sync --group local`."
        )


def _settings_from_env() -> Settings:
    raw = os.environ.get("PROFILE")
    if raw is None or raw.strip().lower() != "local":
        return Settings()
    return Settings(
        profile="local",
        qdrant_url=os.environ.get("QDRANT_URL"),
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL"),
        ollama_chat_model=os.environ.get("OLLAMA_CHAT_MODEL"),
        ollama_embed_model=os.environ.get("OLLAMA_EMBED_MODEL"),
        data_dir=os.environ.get("DATA_DIR"),
    )


def _enabled_from_env(name: str, *, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes"}


app = create_app(
    _settings_from_env(),
    documents_enabled=_enabled_from_env("DOCUMENTS_ENABLED", default=True),
    chat_enabled=_enabled_from_env("CHAT_ENABLED", default=True),
)
