# Implementation Plan: chat-ui

**Branch**: `002-chat-ui` | **Date**: 2026-10-23 (migrated to spec-kit 2026-11-07) | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-chat-ui/spec.md`

## Summary

Connect the placeholder page at `/` to the app-shell API. TanStack Query handles the document list, the upload and the question. zod parses every response. The page uses relative URLs, and Vite proxies them to the stub API in dev. This module adds no dependency.

## Technical Context

**Language/Version**: TypeScript, React 19, Vite, Node >= 24.

**Primary Dependencies**: shadcn/ui (already vendored in `src/components/ui/`), TanStack Query, zod. Nothing new.

**Storage**: none. The transcript lives in component state until reload.

**Testing**: Vitest (jsdom), Testing Library and MSW 3. Render with `renderWithProviders` from `@/test/render` and override handlers with `server.use(...)` from `@/test/server`. New test titles are sentences, such as `the page should show the cited page`.

**Target Platform**: a modern desktop browser.

**Project Type**: web app (the frontend half).

**Performance Goals / Scale**: one user, one page.

**Constraints**: consumes [contracts/http.md](../001-app-shell/contracts/http.md) unchanged. No edits under `src/backend` or `src/components/ui/`.

## Constitution Check

| Principle | Status | How |
| --- | --- | --- |
| I. Health records stay local | Pass | The PDF goes only to the app API through the dev proxy. Fixtures are synthetic. |
| II. Grounded, cited answers | Pass | The citation file, page and text are shown. Text renders as text (FR-012). |
| III. One HTTP contract | Pass | No new route or field. zod schemas mirror the contract. API messages are shown, not invented. |
| IV. Test-first thin slices | Pass | CU-02 to CU-11, one test each. |
| V. Offline quality gates | Pass | `npm run check` mocks every request and starts no API. |
| VI. Modules, ports, simplicity | Pass | No backend edits. No new dependency. |

## Project Structure

```text
specs/002-chat-ui/
├── spec.md
├── plan.md
└── tasks.md

src/frontend/
  vite.config.ts                          # dev proxy
  src/app/App.tsx                         # route / is ChatPage
  src/api/documents.ts                    # GET and POST /documents
  src/api/chat.ts                         # POST /chat
  src/api/errors.ts                       # read the error envelope
  src/api/devProxy.ts                     # proxy table used by vite.config.ts
  src/api/__tests__/
  src/features/chat/ChatPage.tsx
  src/features/chat/DocumentList.tsx
  src/features/chat/Transcript.tsx
  src/features/chat/__tests__/ChatPage.test.tsx
  src/test/server.ts                      # default handler returns an empty list
```

**Structure Decision**: the feature code lives in `features/chat/` and API clients in `api/`. Tests sit in `__tests__` folders next to the code.

## Architecture Decisions

- Document and chat JSON stay camelCase. zod parses the wire names, including `id`, which is how a second upload of the same bytes stays one row.
- An upload uses `FormData` and doesn't set `Content-Type`, so the browser sets the multipart boundary.
- The page merges the upload response into the list by `id`, so a stale refetch can't drop it.
- The default MSW handler returns an empty document list, so the existing test doesn't fail on the new request.

## Commands

From `src/frontend`: `npm run dev`, `npm run build`, `npm run check` (typecheck, lint, format check, tests).

### Manual check

1. `cd src/backend && uv sync && make dev` with `PROFILE` unset.
2. `cd src/frontend && npm run dev`.
3. Upload a one-page PDF whose text is `DemoMarker value is 10 units.`
4. Ask `What is the DemoMarker value?`
5. The page shows that sentence, the file name, and page 1.

## Delivery (pull requests)

| PR | Branch | Tasks |
| --- | --- | --- |
| 1 | `docs/chat-ui-spec` | CU-01 |
| 2 | `feature/chat-documents` | CU-02–CU-07 |
| 3 | `feature/chat-answer` | CU-08–CU-11 |

## Boundaries

- **Ask first**: a new npm dependency; a route other than `/`; drag-and-drop, a PDF viewer or a thumbnail; any change to an API message, status code or field.
- **Never**: edit `src/backend`; render API text as HTML; start Docker, Compose, Minikube or the backend local group from `npm run check`.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| The existing test hits the new list request | Unhandled request fails it | Default handler returns an empty list |
| A refetch replaces the new row with a stale list | The uploaded file disappears | Merge by `id` |
| Setting `Content-Type` on the upload | The file is dropped | Leave it unset |

## Complexity Tracking

No violations.
