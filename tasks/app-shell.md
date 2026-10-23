# Tasks: app-shell

Spec: [docs/SPEC-app-shell.md](../docs/SPEC-app-shell.md). Plan: [tasks/plan.md](plan.md). Active work: [tasks/todo.md](todo.md).

This list is closed. Ids are stable: `AS-01` stays `AS-01` and is never renumbered. `Completed` is the date of the task commit, `YYYY-MM-DD`. Checkpoint dates are the day that gate was passed.

| PR | Branch | Ids | Flag |
| --- | --- | --- | --- |
| 1 | `feature/app-shell` | AS-01–AS-04 | `DOCUMENTS_ENABLED` defaults off. Health is always on. |
| 2 | `feature/list-stored-pdf` | AS-05–AS-06 | Same flag, still off. |
| 3 | `feature/cite-stored-page` | AS-07–AS-10 | `CHAT_ENABLED` defaults off. |
| 4 | `feature/reject-bad-uploads` | AS-11–AS-12 | `DOCUMENTS_ENABLED` defaults on. `CHAT_ENABLED` stays off. |
| 5 | `feature/reject-bad-chat` | AS-13–AS-18 | `CHAT_ENABLED` defaults on. |
| 6 | `feature/local-settings` | AS-19–AS-25 | `PROFILE=local` is the opt-in. No extra flag. |
| 7 | `feature/docling-parser` | AS-26–AS-27 | Used only when `PROFILE=local`. |
| 8 | `feature/qdrant-corpus` | AS-28–AS-29 | Used only when `PROFILE=local`. |
| 9 | `feature/ollama-chat` | AS-30–AS-32 | Used only when `PROFILE=local`. |
| 10 | `feature/local-factory` | AS-33–AS-34 | Wires the local adapters. Stub stays the default. |

## Completion

| Id | Completed | Task |
| --- | --- | --- |
| AS-01 | 2026-10-18 | The Python project runs make check |
| AS-02 | 2026-10-18 | GET /health returns ok |
| AS-03 | 2026-10-18 | The text-layer parser reads the fixture sentence |
| AS-04 | 2026-10-18 | POST /documents stores that PDF |
| AS-05 | 2026-10-18 | GET /documents lists the stored file |
| AS-06 | 2026-10-18 | The same PDF bytes return the existing document |
| AS-07 | 2026-10-18 | Search returns the page that contains the question words |
| AS-08 | 2026-10-18 | POST /chat cites the stored page |
| AS-09 | 2026-10-18 | An empty store returns the fixed sentence |
| AS-10 | 2026-10-18 | An unmatched question returns the fixed sentence |
| AS-11 | 2026-10-20 | A non-PDF upload returns 415 |
| AS-12 | 2026-10-20 | A PDF with no text returns 422 |
| AS-13 | 2026-10-20 | A non-JSON chat body returns 415 |
| AS-14 | 2026-10-20 | Empty messages return 422 |
| AS-15 | 2026-10-20 | Blank message content returns 422 |
| AS-16 | 2026-10-20 | An unknown chat field returns 422 |
| AS-17 | 2026-10-20 | An assistant last message returns 422 |
| AS-18 | 2026-10-20 | A server error hides the traceback |
| AS-19 | 2026-10-20 | Stub settings need no service URLs |
| AS-20 | 2026-10-20 | Local settings require qdrant_url |
| AS-21 | 2026-10-20 | Local settings require ollama_base_url |
| AS-22 | 2026-10-20 | Local settings require ollama_chat_model |
| AS-23 | 2026-10-20 | Local settings require ollama_embed_model |
| AS-24 | 2026-10-20 | Local settings require data_dir |
| AS-25 | 2026-10-20 | The stub app does not import local clients |
| AS-26 | 2026-10-20 | The Docling parser returns pages from an injected converter |
| AS-27 | 2026-10-20 | Both parsers satisfy the Parser protocol |
| AS-28 | 2026-10-20 | The Qdrant corpus upserts one point per page |
| AS-29 | 2026-10-20 | The same document id does not upsert twice |
| AS-30 | 2026-10-20 | The Ollama client posts to the configured model |
| AS-31 | 2026-10-20 | The Ollama prompt contains the citations and not the PDF |
| AS-32 | 2026-10-20 | The Ollama client returns the model text |
| AS-33 | 2026-10-20 | The local factory uses the three injected adapters |
| AS-34 | 2026-10-20 | A missing local install fails with the sync hint |
| AS-CPA | 2026-10-20 | Stub flow |
| AS-CPB | 2026-10-23 | app-shell complete |

Each task was one failing test, then the smallest change, then `make check` from `src/backend`.

```sh
cd src/backend
uv run pytest tests/<file>.py::<test> -q
make check
```

`make check` is ruff, ruff format, pyright, and pytest. It must not need Docker or the `local` dependency group.

## AS-01: The Python project runs make check

**Id:** AS-01
**Completed:** 2026-10-18

**Description:** Create `src/backend` so pytest, ruff, and pyright run. `create_app` returns an app. No routes yet.

**Status:** done

**Acceptance criteria:**

- [x] `create_app()` returns a FastAPI app.
- [x] `make check` passes.
- [x] `git check-ignore` matches `src/backend/.venv`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, and `.pyright`. `uv.lock` is committed.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_health.py::test_create_app_returns_an_app -q`
- [x] `make check`
- [x] `git check-ignore -v src/backend/.venv`

**Dependencies:** None

**Files likely touched:**

- `src/backend/pyproject.toml`
- `src/backend/.python-version`
- `src/backend/Makefile`
- `src/backend/src/health_api/main.py`
- `src/backend/tests/test_health.py`
- `.gitignore`
- `src/backend/uv.lock`

**Estimated scope:** Medium

## AS-02: GET /health returns ok

**Id:** AS-02
**Completed:** 2026-10-18

**Description:** The running app answers a liveness check.

**Status:** done

**Acceptance criteria:**

- [x] `GET /health` returns 200 and `{"status": "ok"}`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_health.py::test_health_returns_ok -q`
- [x] `make check`
- [x] `make dev` answers on `http://127.0.0.1:8000/health`, then stop the server

**Dependencies:** AS-01

**Files likely touched:**

- `src/backend/src/health_api/main.py`
- `src/backend/tests/test_health.py`

**Estimated scope:** Small

## AS-03: The text-layer parser reads the fixture sentence

**Id:** AS-03
**Completed:** 2026-10-18

**Description:** pypdf reads a one-page PDF built with fpdf2. No HTTP route in this task. If the extracted text is wrapped or split, fix the fixture here and stop.

**Status:** done

**Acceptance criteria:**

- [x] The page text is `DemoMarker value is 10 units.` and the page number is 1.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_text_layer_parser.py::test_parser_reads_fixture_sentence -q`
- [x] `make check`

**Dependencies:** AS-01

**Files likely touched:**

- `src/backend/src/health_api/documents/text_layer_parser.py`
- `src/backend/tests/test_text_layer_parser.py`
- `src/backend/pyproject.toml`

**Estimated scope:** Small

## AS-04: POST /documents stores that PDF

**Id:** AS-04
**Completed:** 2026-10-18

**Description:** The upload route parses the PDF, keeps one chunk per page in memory, and returns the new document.

**Status:** done

**Acceptance criteria:**

- [x] `POST /documents` returns 201.
- [x] `pageCount` is 1, `chunkCount` is 1, `sourceFile` is the uploaded name, and `id` is the SHA-256 hex of the bytes.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_documents.py::test_post_document_stores_pdf -q`
- [x] `make check`

**Dependencies:** AS-02 and AS-03

**Files likely touched:**

- `src/backend/src/health_api/documents/memory_corpus.py`
- `src/backend/src/health_api/http/documents.py`
- `src/backend/src/health_api/main.py`
- `src/backend/tests/test_documents.py`

**Estimated scope:** Medium

## AS-05: GET /documents lists the stored file

**Id:** AS-05
**Completed:** 2026-10-18

**Description:** The list shows what was stored and does not include chunk text.

**Status:** done

**Acceptance criteria:**

- [x] After the Task 4 upload, `GET /documents` returns that `id`, `sourceFile`, `pageCount`, and `chunkCount`.
- [x] The body has no page text and no `content` field.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_documents.py::test_get_documents_lists_file -q`
- [x] `make check`

**Dependencies:** AS-04

**Files likely touched:**

- `src/backend/src/health_api/http/documents.py`
- `src/backend/src/health_api/documents/memory_corpus.py`
- `src/backend/tests/test_documents.py`

**Estimated scope:** Small

## AS-06: The same PDF bytes return the existing document

**Id:** AS-06
**Completed:** 2026-10-18

**Description:** A retry of the same upload is not a second document.

**Status:** done

**Acceptance criteria:**

- [x] The second `POST` returns 200 and the same `id`.
- [x] `GET /documents` still returns one entry.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_documents.py::test_same_bytes_return_existing_document -q`
- [x] `make check`

**Dependencies:** AS-05

**Files likely touched:**

- `src/backend/src/health_api/documents/memory_corpus.py`
- `src/backend/src/health_api/http/documents.py`
- `src/backend/tests/test_documents.py`

**Estimated scope:** Small

## AS-07: Search returns the page that contains the question words

**Id:** AS-07
**Completed:** 2026-10-18

**Description:** In-memory search is token overlap. This task does not add a route.

**Status:** done

**Acceptance criteria:**

- [x] Searching for `DemoMarker` returns the stored page's text, file name, and page number 1.
- [x] A query whose words are absent returns no pages.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_memory_corpus.py::test_search_should_return_the_page_with_the_question_words -q`
- [x] `make check`

**Dependencies:** AS-04

**Files likely touched:**

- `src/backend/src/health_api/documents/memory_corpus.py`
- `src/backend/tests/test_memory_corpus.py`

**Estimated scope:** Small

## AS-08: POST /chat cites the stored page

**Id:** AS-08
**Completed:** 2026-10-18

**Description:** The chat route searches the store and quotes the top page.

**Status:** done

**Acceptance criteria:**

- [x] `POST /chat` with `What is the DemoMarker value?` returns 200.
- [x] `citations[0]` has `content` `DemoMarker value is 10 units.`, `sourcePage` 1, `sourceFile` of the upload, and `id` `<document id>:1`.
- [x] `outputText` equals that content.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_chat.py::test_chat_should_cite_the_stored_page -q`
- [x] `make check`

**Dependencies:** AS-07

**Files likely touched:**

- `src/backend/src/health_api/chat/quoting_chat_model.py`
- `src/backend/src/health_api/http/chat.py`
- `src/backend/src/health_api/main.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Medium

## AS-09: An empty store returns the fixed sentence

**Id:** AS-09
**Completed:** 2026-10-18

**Description:** A new app must not invent a citation.

**Status:** done

**Acceptance criteria:**

- [x] `POST /chat` returns 200, `citations` is `[]`, and `outputText` is `No stored document answers that.`

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_chat.py::test_an_empty_store_should_return_the_fixed_sentence -q`
- [x] `make check`

**Dependencies:** AS-08

**Files likely touched:**

- `src/backend/src/health_api/chat/quoting_chat_model.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Small

## AS-10: An unmatched question returns the fixed sentence

**Id:** AS-10
**Completed:** 2026-10-18

**Description:** Stored text that does not share words with the question is not a citation.

**Status:** done

**Acceptance criteria:**

- [x] After storing the fixture PDF, a question with none of its words returns 200, `citations` `[]`, and `outputText` `No stored document answers that.`

**Verification:**

- [x] The named test passed on the first run: `uv run pytest tests/test_chat.py::test_an_unmatched_question_should_return_the_fixed_sentence -q`. Search already drops a page with no shared words, and an empty citation list already returns the fixed sentence.
- [x] `make check`

**Dependencies:** AS-09

**Files likely touched:**

- `src/backend/src/health_api/documents/memory_corpus.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Small

## AS-11: A non-PDF upload returns 415

**Id:** AS-11
**Completed:** 2026-10-20

**Description:** The first error response uses the spec error body. The file is not stored.

**Status:** done

**Acceptance criteria:**

- [x] Uploading `notes.txt` returns 415 and `{"error": {"code": "UNSUPPORTED_MEDIA_TYPE", ...}}`.
- [x] `GET /documents` does not list it.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_documents.py::test_a_non_pdf_upload_should_return_unsupported_media_type -q`
- [x] `make check`

**Dependencies:** AS-05

**Files likely touched:**

- `src/backend/src/health_api/http/errors.py`
- `src/backend/src/health_api/http/documents.py`
- `src/backend/tests/test_documents.py`

**Estimated scope:** Small

## AS-12: A PDF with no text returns 422

**Id:** AS-12
**Completed:** 2026-10-20

**Description:** The stub profile refuses a scan by refusing an empty text layer.

**Status:** done

**Acceptance criteria:**

- [x] An empty text layer returns 422 and `VALIDATION_ERROR`.
- [x] `GET /documents` does not list that file.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_documents.py::test_a_pdf_with_no_text_should_return_validation_error -q`
- [x] `make check`

**Dependencies:** AS-11

**Files likely touched:**

- `src/backend/src/health_api/http/documents.py`
- `src/backend/src/health_api/documents/text_layer_parser.py`
- `src/backend/tests/test_documents.py`

**Estimated scope:** Small

## AS-13: A non-JSON chat body returns 415

**Id:** AS-13
**Completed:** 2026-10-20

**Description:** Chat only accepts JSON.

**Status:** done

**Acceptance criteria:**

- [x] `POST /chat` with `Content-Type: text/plain` returns 415 and `UNSUPPORTED_MEDIA_TYPE`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_chat.py::test_a_non_json_chat_body_should_return_unsupported_media_type -q`
- [x] `make check`

**Dependencies:** AS-08

**Files likely touched:**

- `src/backend/src/health_api/http/chat.py`
- `src/backend/src/health_api/http/errors.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Small

## AS-14: Empty messages return 422

**Id:** AS-14
**Completed:** 2026-10-20

**Description:** A chat body must contain at least one message.

**Status:** done

**Acceptance criteria:**

- [x] `{"messages": []}` returns 422 and `VALIDATION_ERROR`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_chat.py::test_empty_messages_should_return_validation_error -q`
- [x] `make check`

**Dependencies:** AS-13

**Files likely touched:**

- `src/backend/src/health_api/http/chat.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Small

## AS-15: Blank message content returns 422

**Id:** AS-15
**Completed:** 2026-10-20

**Description:** Message text cannot be empty or whitespace.

**Status:** done

**Acceptance criteria:**

- [x] A user message whose `content` is `"   "` returns 422 and `VALIDATION_ERROR`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_chat.py::test_blank_content_should_return_validation_error -q`
- [x] `make check`

**Dependencies:** AS-14

**Files likely touched:**

- `src/backend/src/health_api/http/chat.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Small

## AS-16: An unknown chat field returns 422

**Id:** AS-16
**Completed:** 2026-10-20

**Description:** Extra JSON fields are rejected so a typo is not ignored.

**Status:** done

**Acceptance criteria:**

- [x] A valid message plus `"extra": true` returns 422 and `VALIDATION_ERROR`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_chat.py::test_an_unknown_chat_field_should_return_validation_error -q`
- [x] `make check`

**Dependencies:** AS-14

**Files likely touched:**

- `src/backend/src/health_api/http/chat.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Small

## AS-17: An assistant last message returns 422

**Id:** AS-17
**Completed:** 2026-10-20

**Description:** The question has to be the last message.

**Status:** done

**Acceptance criteria:**

- [x] A body whose last message has role `assistant` returns 422 and `VALIDATION_ERROR`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_chat.py::test_an_assistant_last_message_should_return_validation_error -q`
- [x] `make check`

**Dependencies:** AS-14

**Files likely touched:**

- `src/backend/src/health_api/http/chat.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Small

## AS-18: A server error hides the traceback

**Id:** AS-18
**Completed:** 2026-10-20

**Description:** An unexpected failure returns the fixed 500 body. `create_app` takes a corpus override so the test can raise without a new route.

**Status:** done

**Acceptance criteria:**

- [x] When the corpus raises, `POST /chat` returns 500, `code` is `INTERNAL_ERROR`, and the body has no traceback and no exception text.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_chat.py::test_a_server_error_should_hide_the_traceback -q`
- [x] `make check`

**Dependencies:** AS-08

**Files likely touched:**

- `src/backend/src/health_api/main.py`
- `src/backend/src/health_api/http/errors.py`
- `src/backend/tests/test_chat.py`

**Estimated scope:** Small

## AS-CPA: Stub flow

**Id:** AS-CPA
**Completed:** 2026-10-20

- [x] `uv sync` then `make check` passes with no Docker.
- [x] The `local` dependency group is still not installed.
- [x] AS-03 through AS-10 cover the spec acceptance flow: parse, store, list, cite, empty, unmatched.
- [x] Stop for a human review before AS-19.

## AS-19: Stub settings need no service URLs

**Id:** AS-19
**Completed:** 2026-10-20

**Description:** The default profile starts with no Ollama, Qdrant, or data directory settings.

**Status:** done

**Acceptance criteria:**

- [x] `Settings(profile="stub")` succeeds when those values are unset.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_config.py::test_stub_settings_should_need_no_service_urls -q`
- [x] `make check`

**Dependencies:** AS-CPA

**Files likely touched:**

- `src/backend/src/health_api/config.py`
- `src/backend/tests/test_config.py`

**Estimated scope:** Small

## AS-20: Local settings require qdrant_url

**Id:** AS-20
**Completed:** 2026-10-20

**Description:** Local mode fails before listen when Qdrant is not configured. Other local fields may still be optional after this task.

**Status:** done

**Acceptance criteria:**

- [x] `profile="local"` with no `qdrant_url` raises, and the error names `qdrant_url`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_config.py::test_local_settings_should_require_qdrant_url -q`
- [x] `make check`

**Dependencies:** AS-19

**Files likely touched:**

- `src/backend/src/health_api/config.py`
- `src/backend/tests/test_config.py`

**Estimated scope:** Small

## AS-21: Local settings require ollama_base_url

**Id:** AS-21
**Completed:** 2026-10-20

**Description:** Add the Ollama URL as a required local setting.

**Status:** done

**Acceptance criteria:**

- [x] `profile="local"` with a Qdrant URL and no `ollama_base_url` raises, and the error names `ollama_base_url`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_config.py::test_local_settings_should_require_ollama_base_url -q`
- [x] `make check`

**Dependencies:** AS-20

**Files likely touched:**

- `src/backend/src/health_api/config.py`
- `src/backend/tests/test_config.py`

**Estimated scope:** Small

## AS-22: Local settings require ollama_chat_model

**Id:** AS-22
**Completed:** 2026-10-20

**Description:** Add the chat model name as a required local setting.

**Status:** done

**Acceptance criteria:**

- [x] A local configuration with no `ollama_chat_model` raises, and the error names `ollama_chat_model`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_config.py::test_local_settings_should_require_a_chat_model -q`
- [x] `make check`

**Dependencies:** AS-21

**Files likely touched:**

- `src/backend/src/health_api/config.py`
- `src/backend/tests/test_config.py`

**Estimated scope:** Small

## AS-23: Local settings require ollama_embed_model

**Id:** AS-23
**Completed:** 2026-10-20

**Description:** Add the embedding model name as a required local setting.

**Status:** done

**Acceptance criteria:**

- [x] A local configuration with no `ollama_embed_model` raises, and the error names `ollama_embed_model`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_config.py::test_local_settings_should_require_an_embed_model -q`
- [x] `make check`

**Dependencies:** AS-22

**Files likely touched:**

- `src/backend/src/health_api/config.py`
- `src/backend/tests/test_config.py`

**Estimated scope:** Small

## AS-24: Local settings require data_dir

**Id:** AS-24
**Completed:** 2026-10-20

**Description:** Add the PDF directory as a required local setting.

**Status:** done

**Acceptance criteria:**

- [x] A local configuration with no `data_dir` raises, and the error names `data_dir`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_config.py::test_local_settings_should_require_a_data_dir -q`
- [x] `make check`

**Dependencies:** AS-23

**Files likely touched:**

- `src/backend/src/health_api/config.py`
- `src/backend/tests/test_config.py`

**Estimated scope:** Small

## AS-25: The stub app does not import local clients

**Id:** AS-25
**Completed:** 2026-10-20

**Description:** Building the stub app must not load Docling or the Qdrant client.

**Status:** done

**Acceptance criteria:**

- [x] Importing `create_app` and building a stub app leaves `docling` and `qdrant_client` out of `sys.modules`.

**Verification:**

- [x] The named test passed on the first run: `uv run pytest tests/test_config.py::test_the_stub_app_should_not_import_local_clients -q`. The stub app does not import those modules, so no production change.
- [x] `make check`

**Dependencies:** AS-19

**Files likely touched:**

- `src/backend/src/health_api/main.py`
- `src/backend/tests/test_config.py`

**Estimated scope:** Small

## AS-26: The Docling parser returns pages from an injected converter

**Id:** AS-26
**Completed:** 2026-10-20

**Description:** The local parser adapts converter output into pages. The test passes a fake converter and must not import Docling.

**Status:** done

**Acceptance criteria:**

- [x] One converted page becomes `page_number` 1 and that page's text.
- [x] `docling` is not in `sys.modules` after the test.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_docling_parser.py::test_docling_parser_should_return_converter_pages -q`
- [x] `make check` without the `local` group

**Dependencies:** AS-25

**Files likely touched:**

- `src/backend/src/health_api/documents/docling_parser.py`
- `src/backend/tests/test_docling_parser.py`

**Estimated scope:** Small

## AS-27: Both parsers satisfy the Parser protocol

**Id:** AS-27
**Completed:** 2026-10-20

**Description:** Extract the shared `Parser` protocol now that a second parser exists. Behavior stays the same.

**Status:** done

**Acceptance criteria:**

- [x] The text-layer parser and the Docling parser both match `Parser`.
- [x] Task 3 and Task 26 tests still pass.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_docling_parser.py::test_both_parsers_should_match_the_parser_protocol -q`
- [x] `make check`

**Dependencies:** AS-26

**Files likely touched:**

- `src/backend/src/health_api/documents/parser.py`
- `src/backend/src/health_api/documents/text_layer_parser.py`
- `src/backend/src/health_api/documents/docling_parser.py`
- `src/backend/tests/test_docling_parser.py`

**Estimated scope:** Small

## AS-28: The Qdrant corpus upserts one point per page

**Id:** AS-28
**Completed:** 2026-10-20

**Description:** Given pages and vectors, the corpus records one point each. The test passes a fake client and does not import `qdrant_client` or open a port.

**Status:** done

**Acceptance criteria:**

- [x] Two pages produce two upserts, ids `<document id>:1` and `<document id>:2`.
- [x] Each payload includes `sourceFile`, `sourcePage`, and `content`.
- [x] `qdrant_client` is not in `sys.modules`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_qdrant_corpus.py::test_qdrant_corpus_should_upsert_one_point_per_page -q`
- [x] `make check` without the `local` group

**Dependencies:** AS-25

**Files likely touched:**

- `src/backend/src/health_api/documents/qdrant_corpus.py`
- `src/backend/tests/test_qdrant_corpus.py`

**Estimated scope:** Medium

## AS-29: The same document id does not upsert twice

**Id:** AS-29
**Completed:** 2026-10-20

**Description:** A second add of the same document id replaces the points instead of inserting another pair.

**Status:** done

**Acceptance criteria:**

- [x] After two adds of the same id and the same two pages, the fake client holds two points, not four.

**Verification:**

- [x] The named test passed on the first run: `uv run pytest tests/test_qdrant_corpus.py::test_the_same_document_should_not_upsert_twice -q`. Point ids are `<document id>:<page>`, and the fake client replaces a point with the same id, so a second add stays at two points. No production change.
- [x] `make check`

**Dependencies:** AS-28

**Files likely touched:**

- `src/backend/src/health_api/documents/qdrant_corpus.py`
- `src/backend/tests/test_qdrant_corpus.py`

**Estimated scope:** Small

## AS-30: The Ollama client posts to the configured model

**Id:** AS-30
**Completed:** 2026-10-20

**Description:** The chat client sends one HTTP request to the configured base URL and names the chat model. The test records the request with a fake transport.

**Status:** done

**Acceptance criteria:**

- [x] The request URL starts with `OLLAMA_BASE_URL`.
- [x] The JSON body names `OLLAMA_CHAT_MODEL`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_ollama_chat.py::test_ollama_should_post_to_the_configured_model -q`
- [x] `make check`

**Dependencies:** AS-25

**Files likely touched:**

- `src/backend/src/health_api/chat/ollama_chat_model.py`
- `src/backend/tests/test_ollama_chat.py`

**Estimated scope:** Small

## AS-31: The Ollama prompt contains the citations and not the PDF

**Id:** AS-31
**Completed:** 2026-10-20

**Description:** The request carries the retrieved page text. It does not carry the original PDF bytes.

**Status:** done

**Acceptance criteria:**

- [x] The recorded body includes each citation's `content`.
- [x] The recorded body does not include a sample PDF byte string passed beside the citations.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_ollama_chat.py::test_the_ollama_prompt_should_contain_citations_only -q`
- [x] `make check`

**Dependencies:** AS-30

**Files likely touched:**

- `src/backend/src/health_api/chat/ollama_chat_model.py`
- `src/backend/tests/test_ollama_chat.py`

**Estimated scope:** Small

## AS-32: The Ollama client returns the model text

**Id:** AS-32
**Completed:** 2026-10-20

**Description:** The answer shown to the caller is the text from the model response.

**Status:** done

**Acceptance criteria:**

- [x] When the fake response content is `cited answer`, `answer(...)` returns `cited answer`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_ollama_chat.py::test_ollama_should_return_the_model_text -q`
- [x] `make check`

**Dependencies:** AS-31

**Files likely touched:**

- `src/backend/src/health_api/chat/ollama_chat_model.py`
- `src/backend/tests/test_ollama_chat.py`

**Estimated scope:** Small

## AS-33: The local factory uses the three injected adapters

**Id:** AS-33
**Completed:** 2026-10-20

**Description:** Complete local settings build the app from injectable parser, corpus, and chat-model constructors. Construction does not connect to a service.

**Status:** done

**Acceptance criteria:**

- [x] Upload uses the injected parser.
- [x] Chat uses the injected corpus and chat model.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_local_factory.py::test_the_local_factory_should_use_injected_adapters -q`
- [x] `make check`

**Dependencies:** AS-27, AS-29, AS-32

**Files likely touched:**

- `src/backend/src/health_api/main.py`
- `src/backend/tests/test_local_factory.py`

**Estimated scope:** Medium

## AS-34: A missing local install fails with the sync hint

**Id:** AS-34
**Completed:** 2026-10-20

**Description:** When the local constructors report that Docling or the Qdrant client is not installed, startup fails before listen.

**Status:** done

**Acceptance criteria:**

- [x] Startup raises an error whose message contains `uv sync --group local`.
- [x] The stub tests still pass and still do not import `docling` or `qdrant_client`.

**Verification:**

- [x] RED then GREEN: `uv run pytest tests/test_local_factory.py::test_a_missing_local_install_should_name_the_sync_command -q`
- [x] `make check` without Docker and without the `local` group

**Dependencies:** AS-33

**Files likely touched:**

- `src/backend/src/health_api/main.py`
- `src/backend/tests/test_local_factory.py`

**Estimated scope:** Small

## AS-CPB: app-shell complete

**Id:** AS-CPB
**Completed:** 2026-10-23

- [x] `make check` passes after a clean `uv sync`.
- [x] `make dev` in stub mode stores a text-layer PDF and cites it in a later question in the same process.
- [x] No files under `src/frontend` changed.
- [x] Stop. `chat-ui` and `local-runtime` need their own specs.
