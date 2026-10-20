import importlib
import os
from collections.abc import Callable

from fastapi import FastAPI

from health_api.config import Settings
from health_api.documents.memory_corpus import MemoryCorpus, StoredCorpus
from health_api.documents.parser import Parser
from health_api.http.chat import ChatModel, register_chat
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
            raise RuntimeError("local adapters are required")
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
