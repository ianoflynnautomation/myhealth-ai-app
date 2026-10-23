# Implementation Plan: chat-ui

## Overview

Connect the page at `/` to the API in [docs/SPEC-app-shell.md](../docs/SPEC-app-shell.md), as specified in [docs/SPEC-chat-ui.md](../docs/SPEC-chat-ui.md). The task list is [tasks/todo.md](todo.md). `tasks/plan.md` stays the closed app-shell plan.

Two pull requests. `feature/chat-documents` is CU-02 through CU-07. `feature/chat-answer` is CU-08 through CU-11. Merge the first before cutting the second from `main`.

## Architecture decisions

- The page calls relative `/documents` and `/chat`. Vite proxies both to `http://127.0.0.1:8000` in dev. Tests mock those paths with MSW and do not start the API.
- Document and chat JSON stay camelCase. zod parses the wire names, including `id`, which is how a second upload of the same bytes stays one row.
- An upload uses `FormData` and does not set `Content-Type`.
- A trimmed-empty question does not call `POST /chat`.
- A failed document list does not show `No documents yet.`
- Answer text and citation text render as text.

## Task list

- [ ] CU-02: Proxy documents and chat to the API
- [ ] CU-03: Parse a stored document from the API
- [ ] CU-04: The page lists stored documents
- [ ] CU-05: A failed document list is not an empty store
- [ ] CU-06: An upload shows the file once
- [ ] CU-07: A rejected upload shows the API message
- [ ] CU-08: A blank question does not send
- [ ] CU-09: The page shows the answer and the citation
- [ ] CU-10: An empty citation list shows the fixed sentence
- [ ] CU-11: A failed question keeps the typed text
- [ ] CU-CP2: Chat page against the stub API

## Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| The existing chat-page test starts fetching once the page loads documents | The current test fails on an unhandled request | The default MSW handler returns an empty document list |
| A refetch after upload replaces the new row with a stale list | The uploaded file disappears | The page merges the upload response by `id` |
| Setting `Content-Type` on the upload drops the file | The API never returns 415 for a non-PDF | The client leaves `Content-Type` unset |

## Open questions

None.
