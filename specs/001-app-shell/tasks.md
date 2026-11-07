---
description: "Tasks for app-shell, migrated from tasks/app-shell.md and the CI section of tasks/todo.md"
---

# Tasks: app-shell

**Input**: [spec.md](spec.md), [plan.md](plan.md), [contracts/http.md](contracts/http.md)

**Tests**: required. Every task is RED → GREEN → `make check` (Constitution IV). The test named in each task must fail before the code exists.

**Ids**: `T###` is the spec-kit order. The stable id in parentheses (`AS-`, `CI-`) is the one used in commits and PR titles, and it is never renumbered. The date is the task commit.

## Format: `[ID] [P?] [Story] Description`

Paths are relative to `src/backend` unless they start with `.github/` or `docs/`.

## Phase 1: Setup (PR `feature/app-shell`)

- [X] T001 Create the uv project so `make check` runs, in pyproject.toml, .python-version, Makefile, src/health_api/main.py, tests/test_health.py (AS-01, 2026-10-18)
- [X] T002 `GET /health` returns `{"status":"ok"}` in src/health_api/main.py, tested by tests/test_health.py (AS-02, 2026-10-18)

## Phase 2: User Story 1 - Store a PDF (P1, PRs `feature/app-shell`, `feature/list-stored-pdf`)

- [X] T003 [US1] The text-layer parser reads the fixture sentence, in src/health_api/documents/text_layer_parser.py, tested by tests/test_text_layer_parser.py (AS-03, 2026-10-18)
- [X] T004 [US1] `POST /documents` stores the PDF and returns 201, in src/health_api/http/documents.py and src/health_api/documents/memory_corpus.py, tested by tests/test_documents.py (AS-04, 2026-10-18)
- [X] T005 [US1] `GET /documents` lists the stored file, in src/health_api/http/documents.py, tested by tests/test_documents.py (AS-05, 2026-10-18)
- [X] T006 [US1] The same PDF bytes return the existing document with 200, in src/health_api/documents/memory_corpus.py, tested by tests/test_documents.py (AS-06, 2026-10-18)

## Phase 3: User Story 2 - Cited answer (P1, PR `feature/cite-stored-page`)

- [X] T007 [US2] Search returns the page that contains the question words, in src/health_api/documents/memory_corpus.py, tested by tests/test_memory_corpus.py (AS-07, 2026-10-18)
- [X] T008 [US2] `POST /chat` cites the stored page, in src/health_api/chat/quoting_chat_model.py and src/health_api/http/chat.py, tested by tests/test_chat.py (AS-08, 2026-10-18)
- [X] T009 [US2] An empty store returns the fixed sentence, in src/health_api/chat/quoting_chat_model.py, tested by tests/test_chat.py (AS-09, 2026-10-18)
- [X] T010 [US2] An unmatched question returns the fixed sentence, in src/health_api/documents/memory_corpus.py, tested by tests/test_chat.py (AS-10, 2026-10-18)

## Phase 4: User Story 1 - Reject bad uploads (P1, PR `feature/reject-bad-uploads`)

- [X] T011 [US1] A non-PDF upload returns 415, in src/health_api/http/errors.py and src/health_api/http/documents.py, tested by tests/test_documents.py (AS-11, 2026-10-20)
- [X] T012 [US1] A PDF with no text layer returns 422, in src/health_api/http/documents.py, tested by tests/test_documents.py (AS-12, 2026-10-20)

## Phase 5: User Story 2 - Reject bad chat requests (P1, PR `feature/reject-bad-chat`)

- [X] T013 [US2] A non-JSON chat body returns 415, in src/health_api/http/chat.py, tested by tests/test_chat.py (AS-13, 2026-10-20)
- [X] T014 [US2] Empty `messages` returns 422, in src/health_api/http/chat.py, tested by tests/test_chat.py (AS-14, 2026-10-20)
- [X] T015 [US2] Blank message `content` returns 422, in src/health_api/http/chat.py, tested by tests/test_chat.py (AS-15, 2026-10-20)
- [X] T016 [US2] An unknown chat field returns 422, in src/health_api/http/chat.py, tested by tests/test_chat.py (AS-16, 2026-10-20)
- [X] T017 [US2] A last message from `assistant` returns 422, in src/health_api/http/chat.py, tested by tests/test_chat.py (AS-17, 2026-10-20)
- [X] T018 [US2] A server error returns 500 without a traceback, in src/health_api/http/errors.py, tested by tests/test_chat.py (AS-18, 2026-10-20)

**Checkpoint A** (AS-CPA, 2026-10-20): the stub flow passes `make check` with no Docker and no local group. Human review done.

## Phase 6: User Stories 3 and 4 - Settings (PR `feature/local-settings`)

- [X] T019 [US3] Stub settings need no service URLs, in src/health_api/config.py, tested by tests/test_config.py (AS-19, 2026-10-20)
- [X] T020 [US4] Local settings require `qdrant_url`, in src/health_api/config.py, tested by tests/test_config.py (AS-20, 2026-10-20)
- [X] T021 [US4] Local settings require `ollama_base_url`, in src/health_api/config.py, tested by tests/test_config.py (AS-21, 2026-10-20)
- [X] T022 [US4] Local settings require `ollama_chat_model`, in src/health_api/config.py, tested by tests/test_config.py (AS-22, 2026-10-20)
- [X] T023 [US4] Local settings require `ollama_embed_model`, in src/health_api/config.py, tested by tests/test_config.py (AS-23, 2026-10-20)
- [X] T024 [US4] Local settings require `data_dir`, in src/health_api/config.py, tested by tests/test_config.py (AS-24, 2026-10-20)
- [X] T025 [US3] The stub app does not import `docling` or `qdrant_client`, in src/health_api/main.py, tested by tests/test_config.py (AS-25, 2026-10-20)

## Phase 7: User Story 4 - Local adapters (PRs `feature/docling-parser`, `feature/qdrant-corpus`, `feature/ollama-chat`, `feature/local-factory`)

- [X] T026 [US4] The Docling parser returns pages from an injected converter, in src/health_api/documents/docling_parser.py, tested by tests/test_docling_parser.py (AS-26, 2026-10-20)
- [X] T027 [US4] Both parsers satisfy the `Parser` protocol, in src/health_api/documents/parser.py, tested by tests/test_docling_parser.py (AS-27, 2026-10-20)
- [X] T028 [US4] The Qdrant corpus upserts one point per page, in src/health_api/documents/qdrant_corpus.py, tested by tests/test_qdrant_corpus.py (AS-28, 2026-10-20)
- [X] T029 [US4] The same document id is not upserted twice, in src/health_api/documents/qdrant_corpus.py, tested by tests/test_qdrant_corpus.py (AS-29, 2026-10-20)
- [X] T030 [US4] The Ollama client posts to the configured model, in src/health_api/chat/ollama_chat_model.py, tested by tests/test_ollama_chat.py (AS-30, 2026-10-20)
- [X] T031 [US4] The Ollama prompt has the citations and not the PDF, in src/health_api/chat/ollama_chat_model.py, tested by tests/test_ollama_chat.py (AS-31, 2026-10-20)
- [X] T032 [US4] The Ollama client returns the model text, in src/health_api/chat/ollama_chat_model.py, tested by tests/test_ollama_chat.py (AS-32, 2026-10-20)
- [X] T033 [US4] The local factory uses the three injected adapters, in src/health_api/main.py, tested by tests/test_local_factory.py (AS-33, 2026-10-20)
- [X] T034 [US4] A missing local install fails with the sync hint, in src/health_api/main.py, tested by tests/test_local_factory.py (AS-34, 2026-10-20)

**Checkpoint B** (AS-CPB, 2026-10-23): `make check` passes after a clean `uv sync`. `make dev` in stub mode cites a PDF uploaded in the same process. No files under `src/frontend` changed.

## Phase 8: Backend CI (PR `ci/backend-check`, FR-019)

- [X] T035 Select backend changes in the path filter, in .github/path-filters.yml (CI-01, 2026-10-23)
- [X] T036 Lint the backend on a pull request, in .github/workflows/ci-pr.yml (CI-02, 2026-10-23)
- [X] T037 Check backend formatting on a pull request, in .github/workflows/ci-pr.yml (CI-03, 2026-10-23)
- [X] T038 Typecheck the backend on a pull request, in .github/workflows/ci-pr.yml (CI-04, 2026-10-23)
- [X] T039 Test the backend on a pull request and on `main`, in .github/workflows/ci-pr.yml and .github/workflows/ci-main.yml (CI-05, 2026-10-23)
- [X] T040 Build the backend package on a pull request and on `main`, in .github/workflows/ci-pr.yml and .github/workflows/ci-main.yml (CI-06, 2026-10-23)
- [ ] T041 Confirm backend CI on GitHub (CI-CP1): a PR that touches src/backend runs lint, format, pyright, pytest and `uv build`; a push to `main` runs pytest and `uv build`; a docs-only PR skips them. Record the run links here.

## Phase 9: Polish

- [ ] T042 Rewrite the backend sections of docs/architecture.md to describe the Python FastAPI pipeline and the local Docling/Qdrant/Ollama replacements, and drop the "Java API" and "Flask/Quart" labels and the dead links to README.md, http_protocol.md, deploy_features.md and appservice.md (FR-020, SC-006)

## Dependencies

- T001 → T002 → T003 … T018 run in order. They share one app (no [P] across routes).
- T020–T024 each add one validator to config.py. They come after T019, one at a time (same file, no [P]).
- T026–T027, T028–T029 and T030–T032 run in order within each group. T033 waits for T027, T029 and T032. T034 waits for T033.
- T035 comes before T036–T040. T041 waits for T040.
- T042 has no code dependency.
