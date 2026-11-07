---
description: "Tasks for chat-ui, migrated from the CU section of tasks/todo.md"
---

# Tasks: chat-ui

**Input**: [spec.md](spec.md), [plan.md](plan.md), [contracts/http.md](../001-app-shell/contracts/http.md)

**Tests**: required. RED → GREEN → `npm run check` for every task (Constitution IV).

**Ids**: `T###` is the spec-kit order. The stable `CU-` id in parentheses is the one used in commits, and it is never renumbered. Paths are relative to `src/frontend` unless they start with `specs/` or `docs/`.

## Phase 1: Setup

- [X] T001 Write and approve the chat-ui spec in specs/002-chat-ui/spec.md (CU-01, 2026-10-23; approval CU-CP1, 2026-10-23)
- [X] T002 Proxy `/documents` and `/chat` to `http://127.0.0.1:8000` in vite.config.ts, tested by src/api/__tests__/devProxy.test.ts (CU-02, 2026-10-23)
- [X] T003 Parse a stored document and the error envelope with zod in src/api/documents.ts and src/api/errors.ts, tested by src/api/__tests__/documents.test.ts (CU-03, 2026-10-23)

## Phase 2: User Story 1 - Upload and list (P1, PR `feature/chat-documents`)

- [X] T004 [US1] The page lists stored documents in src/features/chat/ChatPage.tsx, with a default empty-list handler in src/test/server.ts, tested by src/features/chat/__tests__/ChatPage.test.tsx (CU-04, 2026-10-23)
- [X] T005 [US1] A failed document list is not shown as an empty store in src/features/chat/ChatPage.tsx, tested by src/features/chat/__tests__/ChatPage.test.tsx (CU-05, 2026-10-23)
- [X] T006 [US1] An upload shows the file once, merged by `id`, in src/features/chat/ChatPage.tsx, tested by src/features/chat/__tests__/ChatPage.test.tsx (CU-06, 2026-10-23)
- [X] T007 [US1] A rejected upload shows the API message in src/features/chat/ChatPage.tsx, tested by src/features/chat/__tests__/ChatPage.test.tsx (CU-07, 2026-10-23)

## Phase 3: User Story 2 - Cited answer (P1, PR `feature/chat-answer`)

- [X] T008 [US2] A blank question does not send in src/features/chat/ChatPage.tsx, tested by src/features/chat/__tests__/ChatPage.test.tsx (CU-08, 2026-10-27)
- [X] T009 [US2] The page shows the answer and the citation in src/api/chat.ts and src/features/chat/Transcript.tsx, tested by src/features/chat/__tests__/ChatPage.test.tsx (CU-09, 2026-10-27)
- [X] T010 [US2] An empty citation list shows the fixed sentence in src/features/chat/Transcript.tsx, tested by src/features/chat/__tests__/ChatPage.test.tsx (CU-10, 2026-10-27)
- [X] T011 [US2] A failed question keeps the typed text in src/features/chat/ChatPage.tsx, tested by src/features/chat/__tests__/ChatPage.test.tsx (CU-11, 2026-10-27)

## Phase 4: Verification

- [ ] T012 [US4] Run the manual check in specs/002-chat-ui/plan.md against `make dev` and `npm run dev`, confirm `npm run check` passes and `src/backend` is unchanged by CU-02–CU-11, then record the date here (CU-CP2)

## Dependencies

- T002 and T003 come before the page tasks.
- T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 run in order, because they all edit ChatPage.tsx.
- T012 waits for T011.
