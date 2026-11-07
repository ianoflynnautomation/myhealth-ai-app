# Implementation Plan: app-shell

**Branch**: `001-app-shell` | **Date**: 2026-10-18 (migrated to spec-kit 2026-11-07) | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-app-shell/spec.md`

## Summary

A local FastAPI service with two profiles behind one set of routes. **stub** uses pypdf for the text layer, an in-memory store, token-overlap search, and a chat model that quotes the top chunk. It needs no Docker and no network. **local** uses Docling in-process, original bytes under `DATA_DIR`, Qdrant hybrid search (BM25 plus dense, fused with reciprocal rank fusion), and Ollama for embeddings and answers. The wire contract is [contracts/http.md](contracts/http.md).

## Technical Context

**Language/Version**: Python 3.13, pinned in `src/backend/.python-version`. `requires-python = ">=3.13"`.

**Primary Dependencies**: FastAPI (`fastapi[standard]`), Pydantic v2, pypdf, httpx. Dev group: pytest, ruff, pyright, fpdf2. Local group, installed only for the local profile: docling, qdrant-client.

**Storage**: stub uses process memory. local uses `DATA_DIR` for original PDFs and Qdrant for chunks and vectors.

**Testing**: pytest with markers `unit` and `acceptance`, both in `make check`. `integration` (testcontainers) is reserved and stays out of `make check`. No coverage gate.

**Target Platform**: macOS or Linux developer machine, and the containers in `003-local-runtime`.

**Project Type**: web service (the backend half of a web app).

**Performance Goals**: none set. It is a single-user local tool.

**Constraints**: offline gate (Constitution V). The stub path imports no local clients. Settings are validated at startup.

**Scale/Scope**: one person's PDFs. One chunk per page.

Service mapping from the Azure reference:

| Azure piece | Local replacement |
| --- | --- |
| Document Intelligence | Docling, imported by the local parser on the first upload |
| Azure AI Search | Qdrant. Dense HNSW plus BM25, fused with reciprocal rank fusion |
| Azure OpenAI chat | Ollama chat model, OpenAI-compatible `/v1`, called with httpx |
| Azure OpenAI embeddings | Ollama `nomic-embed-text`, 768 dimensions |
| Blob Storage | A directory under `data/` |
| Semantic ranker, Cosmos DB, speech, vision | Later |

## Constitution Check

| Principle | Status | How |
| --- | --- | --- |
| I. Health records stay local | Pass | Only the configured Ollama and Qdrant URLs are called. The fixture is the synthetic `DemoMarker` sentence. `data/` is gitignored. |
| II. Grounded, cited answers | Pass | The chat model gets the retrieved chunks only (AS-31). The empty and unmatched cases return the fixed sentence (AS-09, AS-10). |
| III. One HTTP contract | Pass | [contracts/http.md](contracts/http.md). Pydantic models with camelCase aliases and `extra="forbid"`. |
| IV. Test-first thin slices | Pass | 34 slices, one test each. |
| V. Offline quality gates | Pass | AS-25 fails if `docling` or `qdrant_client` is loaded. CI-02 to CI-06 use `uv sync --frozen` without `--group local`. |
| VI. Modules, ports, simplicity | Pass | Ports appear when the second implementation does (AS-27, AS-28, AS-30). One chunk per page. |

## Project Structure

### Documentation (this feature)

```text
specs/001-app-shell/
├── spec.md
├── plan.md
├── contracts/http.md
└── tasks.md
```

### Source Code

```text
src/backend/
  pyproject.toml  uv.lock  .python-version  Makefile  Dockerfile
  src/health_api/
    main.py                  # create_app, GET /health, local factory, env flags
    config.py                # Settings, fails on startup
    http/documents.py chat.py errors.py
    documents/
      parser.py              # Parser protocol
      text_layer_parser.py   # pypdf (stub)
      docling_parser.py      # local, converter injected
      docling_factory.py     # lazy Docling import (003)
      memory_corpus.py       # StoredCorpus protocol, stub store, token-overlap search
      qdrant_corpus.py       # upsert helper
      qdrant_query.py        # hybrid query body, no client import (003)
      qdrant_index.py        # (003)
      local_corpus.py        # StoredCorpus over Qdrant and Ollama embeddings (003)
      ollama_embeddings.py   # (003)
      pdf_store.py           # DATA_DIR/<id>.pdf in the local profile (003)
    chat/
      quoting_chat_model.py  # stub
      ollama_chat_model.py   # local
  tests/                     # one test_*.py per module
```

**Structure Decision**: a standalone uv project in `src/backend`, not a uv workspace. Files marked (003) were added by `003-local-runtime` to wire the local profile.

### Commands

From `src/backend`:

```sh
uv sync            # main + dev groups, no Docling
make dev           # uv run fastapi dev src/health_api/main.py --host 127.0.0.1 --port 8000
make test          # uv run pytest
make check         # ruff check, ruff format --check, pyright, pytest
```

Local profile:

```sh
uv sync --group local
PROFILE=local OLLAMA_BASE_URL=http://127.0.0.1:11434/v1 OLLAMA_CHAT_MODEL=llama3.1 \
  OLLAMA_EMBED_MODEL=nomic-embed-text QDRANT_URL=http://127.0.0.1:6333 DATA_DIR=../../data make dev
```

## Architecture Decisions

- The ports are `Parser` (`documents/parser.py`, async `parse(file_name, data) -> list[ParsedPage]`), `StoredCorpus` (`documents/memory_corpus.py`: a `documents` map, sync `add(document_id, source_file, pages) -> (StoredDocument, created)`, and `search(query) -> list[StoredChunk]`), and `ChatModel` (`http/chat.py`, async `answer(query, citations) -> str`). Each appears when a second implementation needs it. Earlier slices used plain functions. `add` is sync because the async upload route calls it without `await`.
- One chunk per page is a loop in the store. There is no `chunk.py` until a second splitting rule exists.
- Docling and `qdrant-client` are imported only inside the local adapters. Tests inject fakes.
- Route flags let a route ship dark until it matches this spec. Documents turned on with AS-11 and AS-12. Chat turned on with AS-13 to AS-18.
- Code style: ruff (`E`, `F`, `I`, `UP`, `B`), pyright strict, typed public functions, and Pydantic at the HTTP boundary. Internal code trusts a value that has already been parsed. No `I` prefix on protocols.

## Delivery (pull requests)

| PR | Branch | Tasks |
| --- | --- | --- |
| 1 | `feature/app-shell` | AS-01–AS-04 |
| 2 | `feature/list-stored-pdf` | AS-05–AS-06 |
| 3 | `feature/cite-stored-page` | AS-07–AS-10 |
| 4 | `feature/reject-bad-uploads` | AS-11–AS-12 |
| 5 | `feature/reject-bad-chat` | AS-13–AS-18 |
| 6 | `feature/local-settings` | AS-19–AS-25 |
| 7 | `feature/docling-parser` | AS-26–AS-27 |
| 8 | `feature/qdrant-corpus` | AS-28–AS-29 |
| 9 | `feature/ollama-chat` | AS-30–AS-32 |
| 10 | `feature/local-factory` | AS-33–AS-34 |
| 11 | `ci/backend-check` | CI-01–CI-06 |

## Boundaries

- **Ask first**: a dependency outside the groups above; CI edits; a uv workspace or moving `src/frontend`; running ruff from the frontend husky hook; chunks smaller than a page or a second index; moving Docling to `docling-serve`.
- **Never**: edit `src/frontend` from this module; add streaming, auth, speech or chat history.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| pypdf does not return the fpdf2 sentence unchanged | High at AS-03 | Fix the fixture, never the expected sentence |
| A local adapter imports Docling at import time | High | AS-25 stays green on every later task |

## Complexity Tracking

No violations.
