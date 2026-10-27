import sys
from collections.abc import Sequence

import pytest
from fastapi.testclient import TestClient

import health_api.main as main
from health_api.config import Settings
from health_api.documents.memory_corpus import StoredChunk, StoredDocument
from health_api.documents.text_layer_parser import ParsedPage
from health_api.http.chat import CitationResponse
from health_api.main import create_app


def _local_settings() -> Settings:
    return Settings(
        profile="local",
        qdrant_url="http://127.0.0.1:6333",
        ollama_base_url="http://127.0.0.1:11434/v1",
        ollama_chat_model="llama3.1",
        ollama_embed_model="nomic-embed-text",
        data_dir="../../data",
    )


class _Parser:
    def __init__(self) -> None:
        self.data: list[bytes] = []

    async def parse(self, *, file_name: str, data: bytes) -> list[ParsedPage]:
        self.data.append(data)
        return [ParsedPage(page_number=1, text="DemoMarker value is 10 units.")]


class _Corpus:
    def __init__(self) -> None:
        self.documents: dict[str, StoredDocument] = {}
        self.queries: list[str] = []

    def add(
        self, *, document_id: str, source_file: str, pages: list[ParsedPage]
    ) -> tuple[StoredDocument, bool]:
        stored = StoredDocument(
            id=document_id,
            source_file=source_file,
            page_count=len(pages),
            chunk_count=len(pages),
        )
        self.documents[document_id] = stored
        return stored, True

    def search(self, query: str) -> list[StoredChunk]:
        self.queries.append(query)
        return [
            StoredChunk(
                document_id="doc-1",
                source_file="example.pdf",
                page_number=1,
                text="DemoMarker value is 10 units.",
            )
        ]


class _ChatModel:
    def __init__(self) -> None:
        self.queries: list[str] = []
        self.contents: list[str] = []

    async def answer(self, query: str, citations: Sequence[CitationResponse]) -> str:
        self.queries.append(query)
        self.contents.extend(citation.content for citation in citations)
        return "cited answer"


@pytest.mark.acceptance
def test_the_local_factory_should_use_injected_adapters() -> None:
    # Given
    settings = _local_settings()
    parser = _Parser()
    corpus = _Corpus()
    chat_model = _ChatModel()
    pdf = b"%PDF-1.7 synthetic"
    built: list[str] = []

    def parser_factory(given: Settings) -> _Parser:
        assert given is settings
        built.append("parser")
        return parser

    def corpus_factory(given: Settings) -> _Corpus:
        assert given is settings
        built.append("corpus")
        return corpus

    def chat_model_factory(given: Settings) -> _ChatModel:
        assert given is settings
        built.append("chat")
        return chat_model

    # When
    app = create_app(
        settings,
        parser_factory=parser_factory,
        corpus_factory=corpus_factory,
        chat_model_factory=chat_model_factory,
    )
    constructed = list(built)
    client = TestClient(app)
    uploaded = client.post(
        "/documents",
        files={"file": ("example.pdf", pdf, "application/pdf")},
    )
    answered = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "What is the DemoMarker value?"}]},
    )

    # Then
    assert constructed == ["parser", "corpus", "chat"]
    assert uploaded.status_code == 201
    assert parser.data == [pdf]
    assert answered.status_code == 200
    assert answered.json()["outputText"] == "cited answer"
    assert corpus.queries == ["What is the DemoMarker value?"]
    assert chat_model.queries == ["What is the DemoMarker value?"]
    assert chat_model.contents == ["DemoMarker value is 10 units."]


@pytest.mark.unit
def test_a_missing_local_install_should_name_the_sync_command() -> None:
    # Given
    sys.modules.pop("docling", None)
    sys.modules.pop("qdrant_client", None)

    # When
    with pytest.raises(RuntimeError, match="uv sync --group local"):
        create_app(_local_settings())

    # Then
    assert "docling" not in sys.modules
    assert "qdrant_client" not in sys.modules


@pytest.mark.unit
def test_the_local_profile_should_build_adapters_from_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    settings = _local_settings()
    built: list[str] = []

    def parser_from_settings(given: Settings) -> _Parser:
        assert given is settings
        built.append("parser")
        return _Parser()

    def corpus_from_settings(given: Settings) -> _Corpus:
        assert given is settings
        built.append("corpus")
        return _Corpus()

    def chat_from_settings(given: Settings) -> _ChatModel:
        assert given is settings
        built.append("chat")
        return _ChatModel()

    monkeypatch.setattr(main, "_require_local_group", lambda: None)
    monkeypatch.setattr(main, "_parser_from_settings", parser_from_settings)
    monkeypatch.setattr(main, "_corpus_from_settings", corpus_from_settings)
    monkeypatch.setattr(main, "_chat_from_settings", chat_from_settings)

    # When
    create_app(settings)

    # Then
    assert built == ["parser", "corpus", "chat"]
