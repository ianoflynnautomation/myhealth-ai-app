# Feature Specification: app-shell

**Feature Branch**: `001-app-shell` (delivered across the PR branches listed in [plan.md](plan.md))

**Created**: 2026-10-18

**Status**: Implemented. The one open item is FR-020, the architecture doc.

**Input**: Module `app-shell` from [docs/capability-map.md](../../docs/capability-map.md). It is a local API that stores medical PDFs and answers questions from the stored text, with a citation to the file and the page. The behavior reference is the Azure Search + OpenAI demo (`prepdocs` plus chat). Document Intelligence, Azure AI Search and Azure OpenAI are replaced by local pieces.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Store a PDF (Priority: P1)

I upload a PDF (a letter, a lab result, a discharge note). The API stores it and tells me how many pages and chunks it kept. Uploading the same file again does not make a second copy. I can list what is stored.

**Why this priority**: Nothing can be answered until a document is stored.

**Independent Test**: In the stub profile, post the synthetic one-page fixture PDF and list the documents. No other story is needed.

**Acceptance Scenarios**:

1. **Given** an empty store, **When** I upload a one-page PDF whose text is `DemoMarker value is 10 units.`, **Then** I get 201 with `pageCount` 1, `chunkCount` 1, and an `id`.
2. **Given** that PDF is stored, **When** I upload the same bytes again, **Then** I get 200 and the same `id`, and the store still has one copy.
3. **Given** that PDF is stored, **When** I list documents, **Then** the list has that file name.
4. **Given** any store, **When** I upload a file that is not a PDF, **Then** I get 415 `UNSUPPORTED_MEDIA_TYPE`.
5. **Given** the stub profile, **When** I upload a PDF with no text layer (a scan), **Then** I get 422 `VALIDATION_ERROR` with a clear message.

---

### User Story 2 - Ask a question and get a cited answer (Priority: P1)

I ask a question. The answer cites the stored file and page that support it. When nothing stored answers it, the API says so and cites nothing.

**Why this priority**: This is the reason the app exists. It needs User Story 1.

**Independent Test**: Store the fixture PDF, ask `What is the DemoMarker value?`, and check the citation. Then ask a fresh app with an empty store.

**Acceptance Scenarios**:

1. **Given** the fixture PDF is stored, **When** I ask `What is the DemoMarker value?`, **Then** the response cites `sourcePage` 1 with `content` `DemoMarker value is 10 units.`, and in the stub profile `outputText` equals that content.
2. **Given** an empty store, **When** I ask anything, **Then** `outputText` is `No stored document answers that.` and `citations` is empty.
3. **Given** a stored PDF, **When** I ask a question that shares no words with it, **Then** I get the same fixed sentence and no citations.
4. **Given** any store, **When** the chat body is not JSON, **Then** I get 415.
5. **Given** any store, **When** `messages` is empty, the last message is from `assistant`, a `content` is blank, or the body has an unknown field, **Then** I get 422 `VALIDATION_ERROR`.
6. **Given** a service fault, **When** I call any route, **Then** I get 500 `INTERNAL_ERROR` with a fixed message and no stack trace.

---

### User Story 3 - Run both stories with no services (Priority: P2)

As the developer, I can run User Stories 1 and 2 in the dev server and in acceptance tests with no Docling, no Ollama, no Qdrant, no Docker and no network.

**Why this priority**: It keeps the edit loop and CI fast and offline (Constitution V).

**Independent Test**: Run `make check` after `uv sync`, without the local dependency group and with no Docker daemon.

**Acceptance Scenarios**:

1. **Given** `PROFILE` is unset, **When** the app starts, **Then** it reads no service URLs and opens no connection.
2. **Given** the stub app is built, **When** a test checks loaded modules, **Then** neither `docling` nor `qdrant_client` is imported.
3. **Given** `make dev` is running in stub mode, **When** I upload a text-layer PDF and later ask about it in the same process, **Then** it is cited.

---

### User Story 4 - Parse scans and tables with the local profile (Priority: P3)

With the local profile and Ollama plus Qdrant running, a scanned or table-heavy PDF goes through the same upload route. Its original bytes are kept on disk. Chunks and vectors go to the vector store. The model writes the answer only from the retrieved chunks.

**Why this priority**: Real records include scans and tables, but the contract and stub flow come first.

**Independent Test**: Mocked client tests for parse, upsert and the grounded chat call. The live Compose run is owned by `003-local-runtime`.

**Acceptance Scenarios**:

1. **Given** `PROFILE=local` and any required setting is missing, **When** the process starts, **Then** it refuses to start and names the setting.
2. **Given** `PROFILE=local` and the local dependency group is not installed, **When** the process starts, **Then** it refuses to start and shows the `uv sync --group local` hint.
3. **Given** the local parser, **When** a PDF is uploaded, **Then** the parser gets the PDF bytes and returns pages.
4. **Given** the local corpus, **When** pages are added, **Then** it upserts one point per page whose payload includes the file name, page and content, and the same document id is not upserted twice.
5. **Given** the local chat model, **When** a question is answered, **Then** the prompt has the retrieved chunks and not the raw file.

### Edge Cases

- The same bytes under a different file name: the document id is a hash of the bytes, so it returns the existing document.
- An empty PDF upload returns 422.
- A scanned PDF in the stub profile returns 422 and tells the person why. It is not stored with zero pages.
- Settings come from the environment. `DOCUMENTS_ENABLED` and `CHAT_ENABLED` accept `1`, `true` or `yes` to turn a route on. Any other set value turns it off. Unset means on in the stub profile.
- `GET /health` is always registered, even when both feature routes are off.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose `GET /health` returning `{ "status": "ok" }`. It is always registered.
- **FR-002**: The system MUST accept one PDF per `POST /documents` as multipart field `file`, and return the document's `id`, `sourceFile`, `pageCount` and `chunkCount`.
- **FR-003**: The document id MUST be the SHA-256 hex of the PDF bytes. Re-uploading the same bytes MUST return the existing document with 200 and MUST NOT store a second copy. A first store returns 201.
- **FR-004**: The system MUST store one chunk per page. The 1-based page number is the citation.
- **FR-005**: `GET /documents` MUST list stored documents in the same shape, without chunk text.
- **FR-006**: `POST /chat` MUST accept `messages` (non-empty, roles `user` or `assistant`, non-blank `content`, last message from `user`, no unknown fields) and return `outputText` plus `citations`, each with `id`, `sourceFile`, `sourcePage` and `content`.
- **FR-007**: The chat answer MUST be written only from retrieved chunks. With no matching chunk, it MUST return `No stored document answers that.` and an empty `citations` list.
- **FR-008**: In the stub profile, `outputText` MUST be the top citation's `content`.
- **FR-009**: The system MUST return 415 `UNSUPPORTED_MEDIA_TYPE` for a non-PDF upload or a non-JSON chat body.
- **FR-010**: The system MUST return 422 `VALIDATION_ERROR` for schema failures, an empty PDF, or a PDF with no text layer in the stub profile.
- **FR-011**: The system MUST return 500 `INTERNAL_ERROR` with a fixed message and no stack trace for any other fault.
- **FR-012**: All errors MUST use the envelope `{ "error": { "code", "message", "details" } }`.
- **FR-013**: The stub profile MUST need no service URLs, MUST NOT import `docling` or `qdrant_client`, MUST NOT open a network connection, and MUST NOT write under `data/`.
- **FR-014**: The local profile MUST refuse to start when any of `QDRANT_URL`, `OLLAMA_BASE_URL`, `OLLAMA_CHAT_MODEL`, `OLLAMA_EMBED_MODEL` or `DATA_DIR` is missing.
- **FR-015**: The local profile MUST refuse to start when the local dependency group is not installed, with the sync hint.
- **FR-016**: The local profile MUST parse text, tables and scans in-process, importing the parser on first use. It MUST keep original PDF bytes under `DATA_DIR` (built by `003-local-runtime` FR-017, LR-19), and store chunks and vectors in the vector store using hybrid keyword plus dense search.
- **FR-017**: `POST /documents` and `POST /chat` MUST be switchable with `DOCUMENTS_ENABLED` and `CHAT_ENABLED`, and through `create_app` arguments.
- **FR-018**: `POST /documents` MUST be safe to retry. `POST /chat` MUST NOT write.
- **FR-019**: Backend CI MUST run lint, format, type check, tests and the package build on pull requests and on `main` when `src/backend` changes, without the local group. Docs-only changes MUST skip those jobs.
- **FR-020**: `docs/architecture.md` MUST describe this local pipeline and a Python backend, and MUST NOT call the backend Java.

### Key Entities

- **Document**: one stored PDF. It has an id (SHA-256 of the bytes), a source file name, a page count and a chunk count.
- **Page chunk**: the text of one page of a document. Its id is `{documentId}:{pageNumber}`, with a 1-based page number. In the local profile it also has a dense vector.
- **Citation**: a retrieved page chunk returned with an answer. It has an id, a source file, a source page and content.
- **Chat message**: a role (`user` or `assistant`) and non-blank content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `make check` passes in `src/backend` after `uv sync`, with no Docker daemon and without the local dependency group.
- **SC-002**: The acceptance flow (store, re-store, list, cite, then a fresh empty app) passes in the stub profile.
- **SC-003**: `make dev` serves health, upload and chat on `127.0.0.1:8000` in stub mode, and an uploaded text-layer PDF is cited by a later question in that same process.
- **SC-004**: The local profile wires the parser, the `data/` directory, the vector store and the model. Missing config or a missing local group refuses to start. Mocked client tests cover parse, upsert and the grounded chat call.
- **SC-005**: A pull request that touches only docs skips backend CI. One that touches `src/backend` runs every backend gate.
- **SC-006**: `docs/architecture.md` describes this pipeline and a Python backend.

## Assumptions

- Documents stay on this machine (Constitution I).
- The first corpus is medical PDFs, including scans and tables. Office files, images as input, speech, ACLs and chat history come later.
- The backend is Python 3.13. The frontend stays TypeScript.
- Test fixtures are synthetic. Real records stay in the gitignored `data/` directory.

## Out of Scope

- React upload and citation UI (`002-chat-ui`).
- Compose and Minikube (`003-local-runtime`).
- Cross-encoder reranking and extractive captions.
- Figure descriptions and image embeddings.
- User and group filters, speech, auth and chat history.
- Streaming `POST /chat`.
- Chunks smaller than a page.
- A separate Docling container.
