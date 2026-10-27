# Tasks: chat-ui and local-runtime

Finished work: [tasks/app-shell.md](app-shell.md). Map: [docs/capability-map.md](../docs/capability-map.md).

`chat-ui` has an approved spec: [docs/SPEC-chat-ui.md](../docs/SPEC-chat-ui.md). Plan: [tasks/plan-chat-ui.md](plan-chat-ui.md). `local-runtime` has an approved spec: [docs/SPEC-local-runtime.md](../docs/SPEC-local-runtime.md). Plan: [tasks/plan-local-runtime.md](plan-local-runtime.md).

Backend CI is on `main`. The jobs mirror the frontend gates.

## How to record completion

- **Id** is stable. `CU-01`, `CU-02`, `LR-01`, and `CI-01` are never renumbered or reused.
- **Completed** is the date of the task commit, `YYYY-MM-DD`. Leave it blank until that commit exists.
- One pull request is one branch from the table. Cut it from `main`.
- Do not add chat-ui or local-runtime implementation tasks to the spec branches.

| PR | Branch | Ids | Module |
| --- | --- | --- | --- |
| 1 | `docs/chat-ui-spec` | CU-01 | chat-ui |
| 2 | `docs/local-runtime-spec` | LR-01 | local-runtime |
| 3 | `ci/backend-check` | CI-01–CI-06 | backend CI |
| 4 | `feature/chat-documents` | CU-02–CU-07 | chat-ui |
| 5 | `feature/chat-answer` | CU-08–CU-11 | chat-ui |
| 6 | `feature/local-boot` | LR-02–LR-07 | local-runtime |
| 7 | `feature/compose-stack` | LR-08–LR-11 | local-runtime |
| 8 | `feature/gitops-minikube` | LR-12–LR-17 | local-runtime |
| 9 | `feature/gitops-homelab` | LR-18 | local-runtime |

## CU-01: Write the chat-ui spec

**Id:** CU-01
**Completed:** 2026-10-23

**Description:** Specify how the existing React page uploads a PDF and shows an answer with citations. The page today is a placeholder. The HTTP contract stays the one in [docs/SPEC-app-shell.md](../docs/SPEC-app-shell.md). This task does not change `src/frontend` or `src/backend`.

**Status:** done

**Acceptance criteria:**

- [x] `docs/SPEC-chat-ui.md` states the objective, commands, project structure, code style, testing strategy, boundaries, and success criteria.
- [x] The spec uses `POST /documents` and `POST /chat` as they are. It does not add a backend route.
- [x] The fixture sentence remains `DemoMarker value is 10 units.`
- [x] [docs/capability-map.md](../docs/capability-map.md) links this spec.

**Verification:**

- [x] A human reviews the spec before any chat-ui implementation task is added.

**Dependencies:** AS-CPB

**Files likely touched:**

- `docs/SPEC-chat-ui.md`
- `docs/capability-map.md`
- `tasks/todo.md`

**Estimated scope:** Medium

## LR-01: Write the local-runtime spec

**Id:** LR-01
**Completed:** 2026-10-27

**Description:** Specify Compose for Ollama, Qdrant, and the API, and Flux GitOps for the same images. The Minikube overlay keeps Ollama on the host at `host.minikube.internal:11434`. The homelab overlay runs Ollama as its own Helm release. This task does not add Compose files or a cluster manifest.

**Status:** done

**Acceptance criteria:**

- [x] `docs/SPEC-local-runtime.md` states the objective, commands, project structure, code style, testing strategy, boundaries, and success criteria.
- [x] The spec names how the API container gets `PROFILE=local` and the service URLs. It does not change the app-shell HTTP contract.
- [x] A live stack is out of `make check`. The spec says which check runs it.
- [x] [docs/capability-map.md](../docs/capability-map.md) links this spec.

**Verification:**

- [x] A human reviews the spec before any local-runtime implementation task is added.

**Dependencies:** AS-CPB

**Files likely touched:**

- `docs/SPEC-local-runtime.md`
- `docs/capability-map.md`
- `tasks/todo.md`

**Estimated scope:** Medium

## CI-01: Select backend changes in the path filter

**Id:** CI-01
**Completed:** 2026-10-23

**Description:** Add a `backend` filter so the new jobs run when `src/backend` or the workflow files change, and skip when a pull request only touches docs or markdown. Follow the existing `frontend` filter in `.github/path-filters.yml`.

**Status:** done

**Acceptance criteria:**

- [x] `.github/path-filters.yml` has a `backend` filter covering `src/backend/**` and the workflow files that call the backend jobs.
- [x] A docs-only change does not select `backend`.

**Verification:**

- [x] The filter matches `src/backend/src/health_api/main.py`.
- [x] The filter does not match `tasks/todo.md`.

**Dependencies:** AS-CPB

**Files likely touched:**

- `.github/path-filters.yml`

**Estimated scope:** Small

## CI-02: Lint the backend on a pull request

**Id:** CI-02
**Completed:** 2026-10-23

**Description:** On a pull request to `main`, when the `backend` filter matches, run Ruff lint from `src/backend`. Install with `uv sync --frozen` and do not install the `local` group. Pin actions to a full SHA, the same way the frontend jobs are pinned.

**Status:** done

**Acceptance criteria:**

- [x] `ci-pr.yml` has a backend lint job that runs `uv run ruff check .` in `src/backend`.
- [x] The job uses Python 3.13 and does not pass `--group local` or `--all-groups`.
- [x] The job is listed in `pr_complete.needs`.

**Verification:**

- [x] `actionlint` accepts `.github/workflows/ci-pr.yml`.
- [x] A reviewer can see the job is skipped unless `backend` is in the changed paths.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`

**Estimated scope:** Small

## CI-03: Check backend formatting on a pull request

**Id:** CI-03
**Completed:** 2026-10-23

**Description:** Add the format gate next to lint. It runs `uv run ruff format --check .` from `src/backend` after the same frozen sync.

**Status:** done

**Acceptance criteria:**

- [x] `ci-pr.yml` has a backend format job that runs `uv run ruff format --check .` in `src/backend`.
- [x] The job does not install the `local` group.
- [x] The job is listed in `pr_complete.needs`.

**Verification:**

- [x] `actionlint` accepts `.github/workflows/ci-pr.yml`.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`

**Estimated scope:** Small

## CI-04: Typecheck the backend on a pull request

**Id:** CI-04
**Completed:** 2026-10-23

**Description:** `make check` includes pyright. The pull request gate runs `uv run pyright` from `src/backend` so CI is not weaker than the local check.

**Status:** done

**Acceptance criteria:**

- [x] `ci-pr.yml` has a backend typecheck job that runs `uv run pyright` in `src/backend`.
- [x] The job does not install the `local` group.
- [x] The job is listed in `pr_complete.needs`.

**Verification:**

- [x] `actionlint` accepts `.github/workflows/ci-pr.yml`.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`

**Estimated scope:** Small

## CI-05: Test the backend on a pull request and on main

**Id:** CI-05
**Completed:** 2026-10-23

**Description:** Run pytest from `src/backend` on pull requests and again on `main`. Upload JUnit XML the way the frontend unit job uploads its report. Do not start Docker or install the `local` group.

**Status:** done

**Acceptance criteria:**

- [x] `ci-pr.yml` runs `uv run pytest --junitxml=test-results/pytest.xml` in `src/backend` and uploads that file.
- [x] `ci-main.yml` runs the same test command when `backend` changes.
- [x] Both jobs are listed in `pr_complete.needs` and `main_complete.needs`.
- [x] Neither job installs the `local` group.

**Verification:**

- [x] `actionlint` accepts both workflow files.
- [x] The pytest command does not select the `integration` marker.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`
- `.github/workflows/ci-main.yml`

**Estimated scope:** Medium

## CI-06: Build the backend package on a pull request and on main

**Id:** CI-06
**Completed:** 2026-10-23

**Description:** The backend build is the package build, `uv build`, from `src/backend`. Run it on pull requests and again on `main`. This is not a container image and does not start Compose or Minikube.

**Status:** done

**Acceptance criteria:**

- [x] `ci-pr.yml` runs `uv build` in `src/backend`.
- [x] `ci-main.yml` runs `uv build` when `backend` changes.
- [x] Both jobs are listed in `pr_complete.needs` and `main_complete.needs`.
- [x] Neither job installs the `local` group.

**Verification:**

- [x] `actionlint` accepts both workflow files.
- [x] `uv build` from `src/backend` produces a wheel locally.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`
- `.github/workflows/ci-main.yml`

**Estimated scope:** Small

## CI-CP1: Backend CI is required

**Id:** CI-CP1
**Completed:**

- [ ] CI-01 through CI-06 are merged.
- [ ] A pull request that changes `src/backend` runs lint, format, pyright, pytest, and `uv build`.
- [ ] A push to `main` that changes `src/backend` runs pytest and `uv build`.
- [ ] Docs-only changes skip those jobs.
- [ ] The jobs use `uv sync --frozen` and do not install the `local` group.

## CU-CP1: chat-ui spec approved

**Id:** CU-CP1
**Completed:** 2026-10-23

- [x] CU-01 is merged.
- [x] A human has approved `docs/SPEC-chat-ui.md`.
- [x] Implementation tasks for chat-ui are added to this file only after that approval.

## CU-02: Proxy documents and chat to the API

**Id:** CU-02
**Completed:** 2026-10-23

**Description:** In dev, Vite proxies `/documents` and `/chat` to `http://127.0.0.1:8000`. The page calls those relative paths. This task does not change the page.

**Status:** done

**Acceptance criteria:**

- [x] `vite.config.ts` proxies `/documents` and `/chat` to `http://127.0.0.1:8000`.

**Verification:**

- [x] `npx vitest run src/api/__tests__/devProxy.test.ts -t "should proxy"` from `src/frontend`.

**Dependencies:** CU-CP1

**Files likely touched:**

- `src/frontend/vite.config.ts`
- `src/frontend/src/api/__tests__/devProxy.test.ts`

**Estimated scope:** Small

## CU-03: Parse a stored document from the API

**Id:** CU-03
**Completed:** 2026-10-23

**Description:** Add a document client. It parses the list and upload JSON with zod. An upload sends `FormData` with the field name `file` and does not set `Content-Type`.

**Status:** done

**Acceptance criteria:**

- [x] A 201 body `{ "id", "sourceFile", "pageCount", "chunkCount" }` parses.
- [x] The upload request is multipart, the field name is `file`, and the client does not set `Content-Type`.
- [x] A 415 body returns the message `Upload must be a PDF.`
- [x] A non-JSON error becomes `The API could not be reached.`

**Verification:**

- [x] `npx vitest run src/api/__tests__/documents.test.ts -t "should post the file"` from `src/frontend`.

**Dependencies:** CU-CP1

**Files likely touched:**

- `src/frontend/src/api/documents.ts`
- `src/frontend/src/api/errors.ts`
- `src/frontend/src/api/__tests__/documents.test.ts`

**Estimated scope:** Small

## CU-04: The page lists stored documents

**Id:** CU-04
**Completed:** 2026-10-23

**Description:** Opening the page calls `GET /documents`. A stored file shows `sourceFile` and `pageCount`. A successful empty list shows `No documents yet.`

**Status:** done

**Acceptance criteria:**

- [x] The heading `MyHealth AI` and the textbox named `Message` stay on the page.
- [x] An empty list shows `No documents yet.`
- [x] A stored file shows its `sourceFile` and `pageCount`.

**Verification:**

- [x] `npx vitest run src/features/chat/__tests__/ChatPage.test.tsx -t "should list a stored pdf"` from `src/frontend`.
- [x] `npx vitest run src/app/__tests__/App.test.tsx -t "renders the chat page"` from `src/frontend`.

**Dependencies:** CU-03

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/__tests__/ChatPage.test.tsx`
- `src/frontend/src/test/server.ts`

**Estimated scope:** Small

## CU-05: A failed document list is not an empty store

**Id:** CU-05
**Completed:** 2026-10-23

**Description:** When `GET /documents` fails, the page does not show `No documents yet.` A network failure shows `The API could not be reached.` An error envelope shows `error.message`.

**Status:** done

**Acceptance criteria:**

- [x] A network failure shows `The API could not be reached.`
- [x] That failure does not show `No documents yet.`

**Verification:**

- [x] `npx vitest run src/features/chat/__tests__/ChatPage.test.tsx -t "should not call an empty store"` from `src/frontend`.

**Dependencies:** CU-04

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/__tests__/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-06: An upload shows the file once

**Id:** CU-06
**Completed:** 2026-10-23

**Description:** Choosing a PDF posts it to `POST /documents`. `201` and `200` both show that `id` once. The same bytes do not add a second row.

**Status:** done

**Acceptance criteria:**

- [x] After a 201, the list shows that file's `sourceFile` and `pageCount`.
- [x] A 200 for an `id` already on the page does not add a second row.

**Verification:**

- [x] `npx vitest run src/features/chat/__tests__/ChatPage.test.tsx -t "should show an uploaded pdf once"` from `src/frontend`.

**Dependencies:** CU-03, CU-04

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/__tests__/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-07: A rejected upload shows the API message

**Id:** CU-07
**Completed:** 2026-10-23

**Description:** A failed upload shows `error.message` and leaves the document list as it was.

**Status:** done

**Acceptance criteria:**

- [x] A 415 response shows `Upload must be a PDF.`
- [x] The files already listed stay listed.

**Verification:**

- [x] `npx vitest run src/features/chat/__tests__/ChatPage.test.tsx -t "should show the upload error"` from `src/frontend`.

**Dependencies:** CU-06

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/__tests__/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-08: A blank question does not send

**Id:** CU-08
**Completed:** 2026-10-27

**Description:** Send stays disabled while the trimmed message is empty. That message does not call `POST /chat`.

**Status:** done

**Acceptance criteria:**

- [x] Send is disabled for an empty message and for a message that is only spaces.
- [x] Neither case calls `POST /chat`.

**Verification:**

- [x] `npx vitest run src/features/chat/__tests__/ChatPage.test.tsx -t "should not send a blank question"` from `src/frontend`.

**Dependencies:** CU-04

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/__tests__/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-09: The page shows the answer and the citation

**Id:** CU-09
**Completed:** 2026-10-27

**Description:** A question calls `POST /chat` with one user message. The page shows `outputText` and, for each citation, `sourceFile`, `sourcePage`, and `content`.

**Status:** done

**Acceptance criteria:**

- [x] The request body is `{ "messages": [{ "role": "user", "content": "What is the DemoMarker value?" }] }`.
- [x] The page shows `DemoMarker value is 10 units.`
- [x] The citation shows `example.pdf`, page 1, and that same sentence.

**Verification:**

- [x] `npx vitest run src/features/chat/__tests__/ChatPage.test.tsx -t "should show the cited page"` from `src/frontend`.

**Dependencies:** CU-08

**Files likely touched:**

- `src/frontend/src/api/chat.ts`
- `src/frontend/src/features/chat/Transcript.tsx`
- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/__tests__/ChatPage.test.tsx`

**Estimated scope:** Medium

## CU-10: An empty citation list shows the fixed sentence

**Id:** CU-10
**Completed:** 2026-10-27

**Description:** When `citations` is empty, the page shows `outputText` and no citation list.

**Status:** done

**Acceptance criteria:**

- [x] The page shows `No stored document answers that.`
- [x] The page shows no citation.

**Verification:**

- [x] `npx vitest run src/features/chat/__tests__/ChatPage.test.tsx -t "should show the fixed sentence"` from `src/frontend`.

**Dependencies:** CU-09

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/__tests__/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-11: A failed question keeps the typed text

**Id:** CU-11
**Completed:** 2026-10-27

**Description:** A failed chat shows `error.message` and leaves the typed question in the message box.

**Status:** done

**Acceptance criteria:**

- [x] A 500 response shows `Internal server error.`
- [x] The message box still contains the question.

**Verification:**

- [x] `npx vitest run src/features/chat/__tests__/ChatPage.test.tsx -t "should keep the typed question"` from `src/frontend`.

**Dependencies:** CU-09

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/__tests__/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-CP2: Chat page against the stub API

**Id:** CU-CP2
**Completed:**

- [ ] CU-02 through CU-11 are merged.
- [ ] `npm run check` passes in `src/frontend`.
- [ ] With `make dev` and `npm run dev`, a one-page PDF whose text is `DemoMarker value is 10 units.` is cited on page 1 after the question `What is the DemoMarker value?`
- [ ] `src/backend` is unchanged by this module.

## LR-CP1: local-runtime spec approved

**Id:** LR-CP1
**Completed:** 2026-10-27

- [x] LR-01 is merged.
- [x] A human has approved `docs/SPEC-local-runtime.md`.
- [x] Implementation tasks for local-runtime are added to this file only after that approval.

## LR-02: Declare the local dependency group

**Id:** LR-02
**Completed:** 2026-10-27

**Description:** Add the `local` dependency group with `docling` and `qdrant-client`. `make check` and the backend CI jobs still install without that group.

**Status:** done

**Acceptance criteria:**

- [x] `src/backend/pyproject.toml` has a `local` group that names `docling` and `qdrant-client`.
- [x] `make check` does not pass `--group local`.
- [x] The backend jobs in `ci-pr.yml` and `ci-main.yml` do not pass `--group local`.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_local_group.py::test_the_local_group_should_stay_out_of_make_check -q`

**Dependencies:** LR-CP1

**Files likely touched:**

- `src/backend/pyproject.toml`
- `src/backend/uv.lock`
- `src/backend/tests/test_local_group.py`

**Estimated scope:** Small

## LR-03: Build the Docling converter without importing it on the stub path

**Id:** LR-03
**Completed:** 2026-10-27

**Description:** Add a factory that returns the `PageConverter` used by `DoclingParser`. Importing the module does not import `docling`. The import happens inside the factory, and a missing install still names `uv sync --group local`.

**Status:** done

**Acceptance criteria:**

- [x] Importing the factory module leaves `docling` out of `sys.modules`.
- [x] Calling the factory when `docling` is missing raises the existing sync hint.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_docling_factory.py::test_the_docling_factory_should_not_import_docling -q`

**Dependencies:** LR-02

**Files likely touched:**

- `src/backend/src/health_api/documents/docling_factory.py`
- `src/backend/tests/test_docling_factory.py`

**Estimated scope:** Small

## LR-04: Embed a text with the Ollama embeddings route

**Id:** LR-04
**Completed:** 2026-10-27

**Description:** Add a sync embeddings client. It posts `{base}/embeddings` with `nomic-embed-text` and returns the vector. Tests pass an `httpx` mock transport. The client does not open a port.

**Status:** done

**Acceptance criteria:**

- [x] The request URL is `{base}/embeddings` and the model is `nomic-embed-text`.
- [x] The returned value is the embedding vector from the response.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_ollama_embeddings.py::test_the_embed_client_should_post_the_text -q`

**Dependencies:** LR-CP1

**Files likely touched:**

- `src/backend/src/health_api/documents/ollama_embeddings.py`
- `src/backend/tests/test_ollama_embeddings.py`

**Estimated scope:** Small

## LR-05: Build the hybrid Qdrant query without importing the client

**Id:** LR-05
**Completed:** 2026-10-27

**Description:** Add a pure function that builds the hybrid query from the dense vector and the question text, using BM25 plus that vector. Add a wrapper that sends it through an injected client. Importing the module does not import `qdrant_client`. The collection name is `pages` and the dense size is 768.

**Status:** done

**Acceptance criteria:**

- [x] The query passed to the injected client contains the vector and the question text.
- [x] The collection size in that call is 768.
- [x] Importing the module leaves `qdrant_client` out of `sys.modules`.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_qdrant_query.py::test_the_hybrid_query_should_carry_the_text_and_the_vector -q`

**Dependencies:** LR-CP1

**Files likely touched:**

- `src/backend/src/health_api/documents/qdrant_query.py`
- `src/backend/tests/test_qdrant_query.py`

**Estimated scope:** Small

## LR-06: Store and search pages through the corpus protocol

**Id:** LR-06
**Completed:** 2026-10-27

**Description:** Add a corpus that implements `StoredCorpus`. `add` embeds each page, upserts camelCase points, and returns `(StoredDocument, created)`. The same document id returns the existing document and does not upsert again. `search` embeds the question, runs the hybrid query, and returns `StoredChunk` values. Both methods are synchronous.

**Status:** done

**Acceptance criteria:**

- [x] One page becomes one point with id `{document_id}:{page_number}` and payload keys `sourceFile`, `sourcePage`, and `content`.
- [x] A second `add` of the same document id returns `created` false and does not upsert.
- [x] `search` returns the stored page text for the question.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_local_corpus.py::test_the_local_corpus_should_return_the_stored_page -q`

**Dependencies:** LR-04, LR-05

**Files likely touched:**

- `src/backend/src/health_api/documents/local_corpus.py`
- `src/backend/tests/test_local_corpus.py`

**Estimated scope:** Medium

## LR-07: Wire the local profile from settings

**Id:** LR-07
**Completed:** 2026-10-27

**Description:** When `PROFILE=local` and no factories are passed, `create_app` builds the Docling parser, the local corpus, and the Ollama chat model from settings. A missing local group still raises the sync hint. Injected factories still win. The stub app still does not import `docling` or `qdrant_client`.

**Status:** done

**Acceptance criteria:**

- [x] `create_app` with local settings and no factories calls the three builders.
- [x] A missing `docling` or `qdrant_client` still names `uv sync --group local`.
- [x] Constructing the stub app does not import those modules.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_local_factory.py::test_the_local_profile_should_build_adapters_from_settings -q`

**Dependencies:** LR-03, LR-06

**Files likely touched:**

- `src/backend/src/health_api/main.py`
- `src/backend/tests/test_local_factory.py`

**Estimated scope:** Small

## LR-CP2: Local profile boots without Docker

**Id:** LR-CP2
**Completed:** 2026-10-27

- [x] LR-02 through LR-07 are merged.
- [x] `cd src/backend && make check` passes.
- [x] That command does not start Docker and does not install the local group.
- [x] `POST /documents` and `POST /chat` are unchanged.

## LR-08: Build the API image

**Id:** LR-08
**Completed:** 2026-10-27

**Description:** Add the API image at `src/backend/Dockerfile`. It installs the locked environment with `uv sync --frozen --no-dev --group local` and runs `fastapi run` on `0.0.0.0:8000`. It does not use `fastapi dev` and it does not install the dev group.

**Status:** done

**Acceptance criteria:**

- [x] The Dockerfile installs the `local` group and does not install the dev group.
- [x] The process command is `fastapi run`, bound to `0.0.0.0:8000`.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_api_image.py::test_the_api_image_should_install_the_local_group -q`

**Dependencies:** LR-CP2

**Files likely touched:**

- `src/backend/Dockerfile`
- `src/backend/tests/test_api_image.py`

**Estimated scope:** Small

## LR-09: Build the web image

**Id:** LR-09
**Completed:** 2026-10-27

**Description:** Add the web image at `src/frontend/Dockerfile`. It runs `npm run build` and nginx serves that build. Nginx proxies `/documents`, `/chat`, and `/health` to `http://api:8000`. No npm dependency is added.

**Status:** done

**Acceptance criteria:**

- [x] The image build runs `npm run build`.
- [x] The proxy targets are `/documents`, `/chat`, and `/health`.
- [x] `src/frontend/package.json` gains no dependency.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_web_image.py::test_the_web_image_should_proxy_the_api -q`

**Dependencies:** LR-CP2

**Files likely touched:**

- `src/frontend/Dockerfile`
- `src/frontend/nginx.conf`
- `src/backend/tests/test_web_image.py`

**Estimated scope:** Small

## LR-10: Compose the four services

**Id:** LR-10
**Completed:** 2026-10-27

**Description:** Add `compose.yaml` at the repo root with `web`, `api`, `qdrant`, and `ollama`. Host ports are bound to `127.0.0.1`. The API gets `PROFILE=local` and the five settings. `./data` is bind-mounted at `/data`. Image tags are pinned.

**Status:** done

**Acceptance criteria:**

- [x] The API environment sets `PROFILE=local`, `QDRANT_URL=http://qdrant:6333`, `OLLAMA_BASE_URL=http://ollama:11434/v1`, `OLLAMA_CHAT_MODEL=llama3.1`, `OLLAMA_EMBED_MODEL=nomic-embed-text`, and `DATA_DIR=/data`.
- [x] Published ports are `127.0.0.1:8080`, `127.0.0.1:8000`, `127.0.0.1:6333`, and `127.0.0.1:11434`.
- [x] No image uses the tag `latest`.

**Verification:**

- [x] `cd src/backend && uv run pytest tests/test_compose.py::test_compose_should_set_profile_local -q`

**Dependencies:** LR-08, LR-09

**Files likely touched:**

- `compose.yaml`
- `src/backend/tests/test_compose.py`

**Estimated scope:** Medium

## LR-11: Pull both Ollama models before the API starts

**Id:** LR-11
**Completed:**

**Description:** The first Compose start pulls `llama3.1` and `nomic-embed-text` into the `ollama-models` volume. The API does not start until that pull has finished. `docker compose down -v` is the command that removes the volume. It does not delete the `./data` bind mount.

**Status:** open

**Acceptance criteria:**

- [ ] The compose file names both models.
- [ ] `api` waits for the model pull.
- [ ] The Ollama volume is `ollama-models` and the Qdrant volume is `qdrant-data`.

**Verification:**

- [ ] `cd src/backend && uv run pytest tests/test_compose.py::test_compose_should_pull_the_two_models -q`

**Dependencies:** LR-10

**Files likely touched:**

- `compose.yaml`
- `src/backend/tests/test_compose.py`

**Estimated scope:** Small

## LR-CP3: Compose file matches the spec

**Id:** LR-CP3
**Completed:**

- [ ] LR-08 through LR-11 are merged.
- [ ] `cd src/backend && make check` passes without a Docker daemon.
- [ ] The manual check `docker compose up --build` is still to be run. It is not part of this checkpoint's command.

## LR-12: Watch this repo from the Minikube cluster

**Id:** LR-12
**Completed:**

**Description:** Add `gitops/clusters/myhealth/sync.yaml`, its kustomization, and `ks.yaml`. `sync.yaml` is the `GitRepository` `flux-system` for this public repo on `main`, with no secret, and the `Kustomization` `flux-system` whose path is `./gitops/clusters/myhealth`. `ks.yaml` is the `Kustomization` `apps` whose path is `./gitops/apps/overlays/myhealth`, with `prune: true` and `wait: false`.

**Status:** open

**Acceptance criteria:**

- [ ] `sync.yaml` names `flux-system` and contains no secret.
- [ ] `apps` points at `./gitops/apps/overlays/myhealth`.
- [ ] No `gotk-components.yaml` is added.

**Verification:**

- [ ] `cd src/backend && uv run pytest tests/test_gitops.py::test_sync_should_watch_this_repo_without_a_secret -q`

**Dependencies:** LR-CP1

**Files likely touched:**

- `gitops/clusters/myhealth/sync.yaml`
- `gitops/clusters/myhealth/kustomization.yaml`
- `gitops/clusters/myhealth/ks.yaml`
- `src/backend/tests/test_gitops.py`

**Estimated scope:** Small

## LR-13: Add the myhealth namespace

**Id:** LR-13
**Completed:**

**Description:** Add the `myhealth` namespace. Enforce pod security `baseline`. Audit and warn at `restricted`. The base kustomization lists the namespace only.

**Status:** open

**Acceptance criteria:**

- [ ] The namespace name is `myhealth`.
- [ ] The three pod-security labels are `baseline`, `restricted`, and `restricted`.
- [ ] The base kustomization does not list a component.

**Verification:**

- [ ] `cd src/backend && uv run pytest tests/test_gitops.py::test_the_namespace_should_enforce_baseline -q`

**Dependencies:** LR-12

**Files likely touched:**

- `gitops/apps/base/myhealth/namespace.yaml`
- `gitops/apps/base/myhealth/kustomization.yaml`
- `src/backend/tests/test_gitops.py`

**Estimated scope:** Small

## LR-14: Run the API in the cluster

**Id:** LR-14
**Completed:**

**Description:** Add the API Flux `Kustomization` and its Deployment, Service, `health-data` claim, and NetworkPolicy. The image is `myhealth-api:local` with `imagePullPolicy: IfNotPresent`. The Minikube environment sets `QDRANT_URL` to `http://qdrant.myhealth.svc.cluster.local:6333` and `OLLAMA_BASE_URL` to `http://host.minikube.internal:11434/v1`. Egress allows Qdrant and the host Ollama address.

**Status:** open

**Acceptance criteria:**

- [ ] `PROFILE=local` and the five settings are set on the Deployment.
- [ ] `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1`.
- [ ] The claim name is `health-data` and it is mounted at `/data`.

**Verification:**

- [ ] `cd src/backend && uv run pytest tests/test_gitops.py::test_the_minikube_api_should_keep_ollama_on_the_host -q`

**Dependencies:** LR-13

**Files likely touched:**

- `gitops/apps/base/myhealth/api/ks.yaml`
- `gitops/apps/base/myhealth/api/app/kustomization.yaml`
- `gitops/apps/base/myhealth/api/app/api.yaml`
- `gitops/apps/base/myhealth/api/app/networkpolicy.yaml`
- `src/backend/tests/test_gitops.py`

**Estimated scope:** Medium

## LR-15: Run the web page in the cluster

**Id:** LR-15
**Completed:**

**Description:** Add the web Flux `Kustomization`, Deployment, and Service. The image is `myhealth-web:local` with `imagePullPolicy: IfNotPresent`. `web` depends on `api`. The NetworkPolicy allows `web` to call `api`.

**Status:** open

**Acceptance criteria:**

- [ ] The image is `myhealth-web:local`.
- [ ] The Flux `Kustomization` depends on `api`.
- [ ] `prune` is true, `wait` is true, and `sourceRef.name` is `flux-system`.

**Verification:**

- [ ] `cd src/backend && uv run pytest tests/test_gitops.py::test_the_web_kustomization_should_depend_on_api -q`

**Dependencies:** LR-14

**Files likely touched:**

- `gitops/apps/base/myhealth/web/ks.yaml`
- `gitops/apps/base/myhealth/web/app/kustomization.yaml`
- `gitops/apps/base/myhealth/web/app/web.yaml`
- `gitops/apps/base/myhealth/web/app/networkpolicy.yaml`
- `src/backend/tests/test_gitops.py`

**Estimated scope:** Small

## LR-16: Run Qdrant from its Helm chart

**Id:** LR-16
**Completed:**

**Description:** Add the Qdrant Helm repository `https://qdrant.github.io/qdrant-helm`, a `HelmRelease` of chart `qdrant` with one replica, and its Flux `Kustomization`. The chart version is pinned. The release is not `latest`.

**Status:** open

**Acceptance criteria:**

- [ ] The chart name is `qdrant` and the repository URL is `https://qdrant.github.io/qdrant-helm`.
- [ ] The chart version is a pinned version.
- [ ] `api` depends on `qdrant`.

**Verification:**

- [ ] `cd src/backend && uv run pytest tests/test_gitops.py::test_qdrant_should_be_a_pinned_helm_release -q`

**Dependencies:** LR-14

**Files likely touched:**

- `gitops/apps/base/myhealth/qdrant/ks.yaml`
- `gitops/apps/base/myhealth/qdrant/app/kustomization.yaml`
- `gitops/apps/base/myhealth/qdrant/app/helmrepository.yaml`
- `gitops/apps/base/myhealth/qdrant/app/helmrelease.yaml`
- `src/backend/tests/test_gitops.py`

**Estimated scope:** Small

## LR-17: Point the Minikube overlay at api, web, and Qdrant

**Id:** LR-17
**Completed:**

**Description:** Add `gitops/apps/overlays/myhealth`. It lists the base and the `ks.yaml` files for `api`, `web`, and `qdrant`. It does not list `ollama/ks.yaml`.

**Status:** open

**Acceptance criteria:**

- [ ] The overlay lists `api/ks.yaml`, `web/ks.yaml`, and `qdrant/ks.yaml`.
- [ ] The overlay does not list `ollama/ks.yaml`.

**Verification:**

- [ ] `cd src/backend && uv run pytest tests/test_gitops.py::test_the_myhealth_overlay_should_omit_ollama -q`

**Dependencies:** LR-15, LR-16

**Files likely touched:**

- `gitops/apps/overlays/myhealth/kustomization.yaml`
- `src/backend/tests/test_gitops.py`

**Estimated scope:** Small

## LR-18: Run Ollama on the homelab overlay

**Id:** LR-18
**Completed:**

**Description:** Add the Ollama Helm release from `https://otwld.github.io/ollama-helm`, chart `ollama`, version pinned, with no model baked into an image we build. The release pulls `llama3.1` and `nomic-embed-text`. Add `gitops/apps/overlays/homelab`, which lists the Minikube components plus `ollama/ks.yaml`. The homelab API depends on `ollama`, sets `OLLAMA_BASE_URL` to `http://ollama.myhealth.svc.cluster.local:11434/v1`, and its NetworkPolicy allows the in-cluster Ollama Service and not the host.

**Status:** open

**Acceptance criteria:**

- [ ] The homelab overlay lists `ollama/ks.yaml`.
- [ ] The homelab API base URL is `http://ollama.myhealth.svc.cluster.local:11434/v1`.
- [ ] The homelab API manifest does not contain `host.minikube.internal`.

**Verification:**

- [ ] `cd src/backend && uv run pytest tests/test_gitops.py::test_the_homelab_overlay_should_run_ollama -q`

**Dependencies:** LR-17

**Files likely touched:**

- `gitops/apps/base/myhealth/ollama/ks.yaml`
- `gitops/apps/base/myhealth/ollama/app/helmrelease.yaml`
- `gitops/apps/overlays/homelab/kustomization.yaml`
- `gitops/apps/overlays/homelab/api-patch.yaml`
- `src/backend/tests/test_gitops.py`

**Estimated scope:** Medium

## LR-CP4: GitOps tree matches the spec

**Id:** LR-CP4
**Completed:**

- [ ] LR-12 through LR-18 are merged.
- [ ] `cd src/backend && make check` passes without a Docker daemon.
- [ ] The manual Minikube check is still to be run. It does not `kubectl apply` a Deployment.
- [ ] The homelab overlay is not applied to a shared cluster from this checkpoint.
