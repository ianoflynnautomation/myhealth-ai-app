# Spec: app-shell

A local Python API that stores medical PDFs and answers questions from the stored text. This is the first module in [capability-map.md](capability-map.md). The React page, Compose, and Minikube are later modules.

The behavior reference is the Azure Search + OpenAI demo (`prepdocs` plus chat). Document Intelligence, Azure AI Search, and Azure OpenAI are replaced by Docling, Qdrant, and Ollama.

## Objective

The person using this app has PDFs (letters, labs, discharge notes) and wants an answer that cites the file and the page. This module is that API. The React page is the next module.

Two profiles, one set of routes:

- **stub** — `make dev` and acceptance tests. No Docker and no Docling install. pypdf reads the text layer, an in-memory store holds the pages, search is token overlap, and the chat model quotes the retrieved chunk. A scanned PDF is refused with a clear error, because Docling is not loaded.
- **local** — the same routes. Docling parses text, tables, and scans. Original bytes go to `data/`. Chunks and vectors go to Qdrant. Ollama embeds and answers. The answer is written from the retrieved chunks.

User stories:

1. I upload a PDF and the API stores it and returns how many pages and chunks it kept.
2. I ask a question and the answer cites the stored file and page that support it.
3. I can run stories 1 and 2 in acceptance tests with no Docling, Ollama, or Qdrant.
4. With the local profile and Ollama plus Qdrant up, a scanned or tabular PDF takes the same upload path.

Assumptions that bind this spec:

1. Documents stay on this machine. Health records do not go to a hosted parser or a hosted vector service.
2. The first corpus is medical PDFs, including scans and tables. Office files, images-as-input, speech, ACLs, and chat history wait.
3. The backend is Python 3.13. The React frontend stays TypeScript.
4. Ollama serves the chat model and the embedding model. Qdrant does keyword search with BM25 plus dense vectors.
5. `PROFILE=stub` is the dev server and the acceptance-test profile. `PROFILE=local` is the same routes. Docling runs in-process and is imported on the first upload. Ollama and Qdrant stay separate processes.
6. JSON on the wire is camelCase. Python code uses snake_case. Pydantic aliases cross the boundary.
7. Test fixtures are synthetic. Real records stay in `data/`, which is gitignored.

## Tech stack

- Python 3.13, pinned in `src/backend/.python-version`. `requires-python = ">=3.13"`.
- uv for the environment and `uv.lock`.
- FastAPI with `fastapi[standard]`, so `fastapi dev` is available.
- Pydantic v2, as used by FastAPI.
- pypdf for the stub parser.
- httpx for Ollama and for the tests' ASGI client.
- Dev group: pytest, ruff, pyright, fpdf2 (the test builds its PDF with fpdf2).
- Local group, installed only for the local profile: docling, qdrant-client.
- Own project at `src/backend`. No uv workspace with other packages in this module.

`uv sync` installs the main and dev groups and does not install Docling. `uv sync --group local` adds it. CI and acceptance tests use `uv sync` only.

Service choices:

| Azure piece | Use |
| --- | --- |
| Document Intelligence | Docling, imported by the local parser on the first upload |
| Azure AI Search | Qdrant. Dense HNSW plus BM25, fused with reciprocal rank fusion |
| Azure OpenAI chat | Ollama chat model, OpenAI-compatible `/v1`, called with httpx |
| Azure OpenAI embeddings | Ollama embedding model (`nomic-embed-text` or `mxbai-embed-large`). Pin the vector size |
| Blob Storage | A directory under `data/` for original PDFs |
| Semantic ranker, Cosmos DB, speech, vision | Later. See Explicitly later |

The stub parser is pypdf. It reads a text layer and misses scans and tables. Those PDFs take the local profile.

## Commands

From `src/backend`:

```sh
uv sync
make dev
make test
make check
```

`Makefile` targets:

```make
dev:
	uv run fastapi dev src/health_api/main.py --host 127.0.0.1 --port 8000

test:
	uv run pytest

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run pyright
	uv run pytest
```

`PROFILE` defaults to `stub`. Local:

```sh
uv sync --group local
PROFILE=local \
  OLLAMA_BASE_URL=http://127.0.0.1:11434/v1 \
  OLLAMA_CHAT_MODEL=llama3.1 \
  OLLAMA_EMBED_MODEL=nomic-embed-text \
  QDRANT_URL=http://127.0.0.1:6333 \
  DATA_DIR=../../data \
  make dev
```

The process refuses to start when `PROFILE=local` and any of those variables is missing, or when the local dependency group is not installed. In stub mode it does not read the service URLs and does not open a connection to those hosts.

`GET /health` is always registered. `POST /documents` is registered only when `documents_enabled` is true. `POST /chat` is registered only when `chat_enabled` is true, once that route exists. The module-level app reads `DOCUMENTS_ENABLED` and `CHAT_ENABLED` from the environment. A value of `1`, `true`, or `yes` turns that route on. The default is off, so `make dev` does not expose a route whose behavior is still short of this spec. Tests opt in with `create_app(documents_enabled=True)` or `create_app(chat_enabled=True)`. The stub profile turns `documents_enabled` on by default after bad uploads are rejected, and `chat_enabled` on by default after bad chat bodies are rejected.

## Project structure

```text
src/backend/
  pyproject.toml
  uv.lock
  .python-version
  Makefile
  src/
    health_api/
      __init__.py
      main.py                  # create_app, then uvicorn when run as main
      config.py                # pydantic settings, fail on startup
      http/
        health.py
        documents.py
        chat.py
        errors.py
      documents/
        parser.py              # Protocol
        text_layer_parser.py   # pypdf
        docling_parser.py      # lazy import
        chunk.py               # one chunk per page
        corpus.py              # Protocol
        memory_corpus.py
        qdrant_corpus.py
      chat/
        chat_model.py          # Protocol
        quoting_chat_model.py
        ollama_chat_model.py
        chat_service.py
  tests/
    test_acceptance.py
    test_local_clients.py
```

`data/` is gitignored. The stub profile never writes there.

### Pipeline

```text
POST /documents
  bytes -> Parser.parse -> one chunk per page -> Corpus.add
  stub:  pypdf, in-memory corpus
  local: Docling on first upload, PDF bytes in DATA_DIR, chunks + vectors in Qdrant

POST /chat
  question -> Corpus.search -> ChatModel.answer(question, citations)
  stub:  token overlap against stored chunk text
  local: embed the question with Ollama, Qdrant hybrid search, Ollama writes the answer from those chunks
```

One chunk per page. The page number is the citation. Finer splits wait until a page is too coarse to be useful.

Document id is the SHA-256 hex of the PDF bytes. Uploading the same bytes again returns the existing document and does not insert a second copy.

## Code style

Ruff formats the code (double quotes, its default). Ruff lint selects `E`, `F`, `I`, `UP`, and `B`. Pyright runs in strict mode. Public functions have type hints. Pydantic models are the HTTP boundary. Protocols are the ports. Internal code trusts a value that has already been parsed.

Wire fields are camelCase. Python attributes are snake_case.

```python
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    id: str
    source_file: str = Field(alias="sourceFile")
    source_page: int = Field(alias="sourcePage", ge=1)
    content: str


class ParsedPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_number: int = Field(ge=1)
    text: str


class Parser(Protocol):
    async def parse(self, *, file_name: str, data: bytes) -> list[ParsedPage]: ...


class Corpus(Protocol):
    async def add(
        self, *, document_id: str, source_file: str, pages: list[ParsedPage]
    ) -> tuple[int, int, bool]: ...

    async def search(self, query: str) -> list[Citation]: ...


class ChatModel(Protocol):
    async def answer(self, query: str, citations: list[Citation]) -> str: ...
```

`page_number` and `sourcePage` are 1-based. `Corpus.add` returns `(page_count, chunk_count, created)`. Files are `snake_case.py`. No `I` prefix on protocols.

### HTTP contract

`GET /health` → `200` `{ "status": "ok" }`

`POST /documents` as `multipart/form-data` with one file field named `file`. The file must be a PDF.

`201` the first time those bytes are stored. `200` when the same bytes were already stored.

```json
{
  "id": "sha256-hex",
  "sourceFile": "example.pdf",
  "pageCount": 1,
  "chunkCount": 1
}
```

`GET /documents` → `200` with `{ "documents": [ /* the same shape, without chunk text */ ] }`.

`POST /chat`, JSON:

```json
{
  "messages": [
    { "role": "user", "content": "What is the DemoMarker value?" }
  ]
}
```

`messages` is non-empty. Each item has `role` of `user` or `assistant` and a non-empty `content`. The last message is from `user`. Unknown fields are rejected.

`200` when the store has a matching chunk:

```json
{
  "outputText": "DemoMarker value is 10 units.",
  "citations": [
    {
      "id": "sha256-hex:1",
      "sourceFile": "example.pdf",
      "sourcePage": 1,
      "content": "DemoMarker value is 10 units."
    }
  ]
}
```

`200` when the store is empty or nothing matches:

```json
{
  "outputText": "No stored document answers that.",
  "citations": []
}
```

The stub chat model sets `outputText` to the top citation's `content`, or to the fixed sentence `No stored document answers that.` when there is no citation. The local chat model must use the retrieved chunk text as the only source for the answer. It does not get the rest of the PDF.

Errors:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Last message must be from the user.",
    "details": {}
  }
}
```

| Status | Code | When |
| --- | --- | --- |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | Chat body is not JSON, or the upload is not a PDF |
| 422 | `VALIDATION_ERROR` | JSON fails the schema, the PDF is empty, or the stub parser finds no text layer |
| 500 | `INTERNAL_ERROR` | Anything else. Fixed message. No stack in the body. |

`POST /documents` is safe to retry: the same bytes return the existing row. `POST /chat` writes nothing.

## Testing strategy

pytest. Acceptance tests build the app with `create_app(Settings(profile="stub"))` and call it through FastAPI's `TestClient`. No Docker, no network.

Acceptance test, one flow:

1. Build a one-page PDF with fpdf2 whose text is `DemoMarker value is 10 units.`
2. `POST /documents` returns 201, `pageCount` 1, `chunkCount` 1.
3. `POST` the same bytes again returns 200 and the same `id`.
4. `GET /documents` lists that file.
5. `POST /chat` with `What is the DemoMarker value?` returns a citation whose `content` is that sentence, `sourcePage` is 1, and `outputText` equals that content.
6. A new `create_app(...)` answers with empty `citations` and the fixed empty sentence.

Also:

- A non-PDF upload returns 415.
- A PDF with no text layer returns 422 in the stub profile.
- Empty `messages`, a last `assistant` message, blank `content`, and an unknown field return 422.
- A non-JSON chat body returns 415.
- A raised service error returns 500 with no stack string.
- `Settings` rejects `profile="local"` when `qdrant_url` is missing.
- Constructing the stub app does not import `docling` or `qdrant_client`.

`tests/test_local_clients.py` mocks httpx and the Qdrant client. It asserts the Docling parser is asked for the PDF bytes, the corpus upserts a point whose payload includes the file name, page, and content, and the chat client sends those chunks and not the raw file. A live Compose run belongs to `local-runtime`, not this suite.

No coverage percentage gate.

## Boundaries

Always:

- Validate settings at startup and inputs at both POST routes.
- Keep stub mode free of network calls, free of Docling imports, and free of writes under `data/`.
- Cite a stored page. Do not answer from a chunk that was not retrieved.
- Run `make check` in `src/backend` before a commit that touches it.
- Update this spec when the contract changes.

Ask first:

- A dependency outside the groups listed in Tech stack.
- CI edits. Backend `make check` joins `ci-pr.yml` and `ci-main.yml` when the package exists, following `.grok/skills/ci-cd-and-automation`. The job uses `uv sync` and does not install the local group.
- A uv workspace, or any move of `src/frontend`.
- Changing the frontend husky hook to run ruff.
- Chunks smaller than a page, or a second index.
- Moving Docling out to `docling-serve`.

Never:

- Send a PDF or a chunk to a host other than the configured Ollama and Qdrant URLs.
- Commit `data/`, secrets, model weights, or `.venv`.
- Put a real health record, or a realistic patient narrative, in a fixture, a prompt example, or a test name. `DemoMarker value is 10 units.` is the fixture sentence.
- Add streaming, auth, speech, or chat history in this module.
- Edit `src/frontend` from this module.

## Success criteria

1. `make check` passes in `src/backend` after `uv sync`, with no Docker daemon and without the local dependency group.
2. The acceptance flow above passes against `PROFILE=stub`.
3. With `DOCUMENTS_ENABLED=1` and `CHAT_ENABLED=1`, `make dev` serves the three routes on `127.0.0.1:8000` in stub mode, and an uploaded text-layer PDF is still cited by a later question in that same process. Before those flags default on, the routes stay off unless the test or the environment opts in.
4. `PROFILE=local` wires Docling, the `data/` directory, Qdrant, and Ollama. Missing config, or a missing local group, refuses to start. Mocked client tests cover parse, upsert, and the grounded chat call.
5. `docs/capability-map.md` and this file are in the repo.
6. `docs/architecture.md` describes this pipeline and a Python backend. It no longer says the backend is Java or TypeScript.

## Open questions

None. The backend language is Python.

## Explicitly later

- React upload and citation UI (`chat-ui`).
- Compose and Minikube (`local-runtime`).
- Cross-encoder reranker and extractive captions.
- Figure descriptions and image embeddings.
- User and group filters, speech, auth, chat history.
- Streaming `POST /chat`.
- Splits finer than one chunk per page.
- A separate Docling container, if the API image is too large.
