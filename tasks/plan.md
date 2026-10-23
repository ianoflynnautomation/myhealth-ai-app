# Implementation Plan: app-shell

## Overview

Build the Python API in [docs/SPEC-app-shell.md](../docs/SPEC-app-shell.md) as 34 slices. Each slice is one behavior, one test, the minimum code that makes that test pass, and one commit. The full heading, description, acceptance criteria, and test command for every slice are in [tasks/app-shell.md](app-shell.md). The list is closed. Active work is [tasks/todo.md](todo.md).

The stub profile is finished and reviewed before any Docling, Qdrant, or Ollama code exists.

## How an agent runs this

Pull requests stay small. `feature/app-shell` is only Tasks 1–4. The slice table in [tasks/app-shell.md](app-shell.md) names the branch for every group. Merge one pull request before cutting the next branch from `main`.

1. Implement exactly one pending task on the branch for its slice. Stop after it. `/build auto` runs the rest of that slice only after an explicit approval, and it does not cross into the next pull request.
2. Read that task and the spec sections it names. Do not load later tasks or the frontend.
3. From `src/backend`:
   - RED: `uv run pytest <file>::<test> -q` fails because the behavior is missing.
   - GREEN: the smallest code that passes that test.
   - REFACTOR only inside the files the task lists.
4. Run `make check`. Commit only this task's files. Mark the task done. Stop.
5. A route that is not safe to call yet is registered only when its flag is on. `DOCUMENTS_ENABLED` and `CHAT_ENABLED` default on for the stub app. Tests that need a route off pass that flag into `create_app`. `PROFILE=local` is the opt-in for Docling, Qdrant, and Ollama, so those adapters do not need another flag.
6. Turn a flag on for the stub profile only in the pull request that makes that route match the spec. Documents turn on at the end of Tasks 11–12. Chat turns on at the end of Tasks 13–18.
7. Stop at Checkpoint A and Checkpoint B for a human review.
8. Do not run these tasks in parallel. They share one app.

A task is done when its named test failed first, then passed, and `make check` passed. A test that passed on the first run does not count.

One HTTP response is one task. A second behavior, even on the same route, is the next task.

## Architecture decisions

- `Parser`, `Corpus`, and `ChatModel` ports appear in Tasks 27, 28, and 30, when the second implementation needs them. Earlier slices use plain functions.
- One chunk per page is a loop in the store. No `chunk.py` until a second splitting rule exists.
- Docling and `qdrant-client` stay in the `local` dependency group and are imported only inside the local adapters. Tests inject fakes. `make check` never installs Docling and never opens a port.
- Wire JSON stays camelCase. Python stays snake_case.
- Backend CI, the React page, Compose, and Minikube are not tasks in this list.

## Order

```text
1 project → 2 health
  → 3 parse fixture → 4 store PDF → 5 list documents → 6 same bytes
  → 7 search page → 8 cite that page
  → 9 empty store → 10 unmatched question
  → 11 non-PDF → 12 no text layer
  → 13 non-JSON chat → 14 empty messages → 15 blank content
  → 16 unknown field → 17 assistant last message → 18 hide traceback
  → Checkpoint A
  → 19 stub settings → 20 qdrant url → 21 ollama url
  → 22 chat model → 23 embed model → 24 data dir
  → 25 stub does not import local clients
  → 26 Docling parser → 27 Parser protocol
  → 28 Qdrant upsert → 29 no duplicate upsert
  → 30 Ollama URL → 31 prompt is citations → 32 return model text
  → 33 wire factory → 34 missing install message
  → Checkpoint B
```

Tasks 26–27, 28–29, and 30–32 can be written in that order only. Task 33 waits for 27, 29, and 32. Task 34 waits for 33.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| pypdf does not return the fpdf2 sentence unchanged | High at Task 3 | Stop in that task and fix the fixture. Do not change the expected sentence. |
| A local adapter imports Docling at import time | High | Task 25 fails if `docling` or `qdrant_client` is in `sys.modules`. Later tasks keep that test green. |
| Several tasks get implemented in one turn | High | Each heading is a stop. |

## Out of scope

React upload and citations, Compose, Minikube, backend CI, streaming, auth, speech, chat history, reranking, image embeddings, finer chunks, and `docling-serve`.
