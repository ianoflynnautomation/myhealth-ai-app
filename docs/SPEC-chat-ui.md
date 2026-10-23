# Spec: chat-ui

The existing React page uploads a PDF and shows an answer with the cited file and page. This is the `chat-ui` module in [capability-map.md](capability-map.md). The HTTP contract stays the one in [SPEC-app-shell.md](SPEC-app-shell.md). This module does not add a route or a field.

The page today is a placeholder at `/`. It shows the heading, an empty transcript, a message box, and a disabled Send button. It does not call the API.

## Objective

The person has the stub API running and uses this page to store a PDF and ask a question. The answer on screen is the API's `outputText`. When the API returns a citation, the page shows the file name, the page number, and the quoted text.

User stories:

1. I choose a PDF and the page shows that file's name and page count.
2. I ask a question and the page shows the answer. A citation shows the file, the page, and the quoted text.
3. I can run stories 1 and 2 in the frontend test suite with no API process.
4. With `make dev` and `npm run dev`, a one-page PDF whose text is `DemoMarker value is 10 units.` is cited when I ask `What is the DemoMarker value?`

Assumptions that bind this spec:

1. The only route is `/`. There is no settings page.
2. The page calls `GET /documents`, `POST /documents`, and `POST /chat` as they are. It does not change the backend.
3. Each chat request sends one message, the current question: `{ "role": "user", "content": "..." }`. Earlier questions stay on screen until reload. They are not sent again. Stored chat history is later.
4. `outputText` and citation `content` are shown as text. The page does not parse them as HTML or Markdown.
5. In dev, Vite proxies `/documents` and `/chat` to `http://127.0.0.1:8000`. The page uses those relative paths.
6. Opening the page loads `GET /documents`, so a refresh shows files still stored in that API process.
7. Upload is one file input, PDF only. Drag-and-drop and a page preview are later.
8. The fixture sentence remains `DemoMarker value is 10 units.`
9. The page does not choose stub or local. It talks to whichever API the proxy reaches.

## Tech stack

The stack already in `src/frontend` stays. This module adds no dependency.

- React 19, TypeScript, Vite, Node >= 24.
- shadcn/ui components already under `src/components/ui/`.
- TanStack Query for the document list, the upload, and the question.
- zod parses the JSON the API returns.
- Vitest, Testing Library, and MSW. A test mocks every request the page makes. An unhandled request fails the test.

## Commands

From `src/frontend`:

```sh
npm run dev
npm run build
npm run typecheck
npm run lint
npm run format:check
npm test
npm run check
```

`npm run check` is typecheck, lint, format check, and the unit tests. It does not start the API, Docker, or the backend `local` group.

Two processes for the manual story:

```sh
cd src/backend && uv sync && make dev
cd src/frontend && npm run dev
```

The API listens on `127.0.0.1:8000`. The Vite server proxies:

```ts
server: {
  proxy: {
    '/documents': 'http://127.0.0.1:8000',
    '/chat': 'http://127.0.0.1:8000',
  },
},
```

## Project structure

```text
src/frontend/src/
  app/App.tsx                         # route / stays ChatPage
  features/chat/ChatPage.tsx          # the page
  features/chat/ChatPage.test.tsx     # page behavior
  api/documents.ts                    # GET and POST /documents
  api/chat.ts                         # POST /chat
  api/errors.ts                       # read the error envelope
vite.config.ts                        # dev proxy
```

Implementation may split the page into smaller components under `features/chat/`. Tests stay next to the code as `*.test.tsx`. `src/components/ui/` stays vendored. This spec does not edit those files.

## Code style

Imports use `@/`. Components are functions. The existing names stay: the heading is `MyHealth AI`, the textbox is named `Message`, and the button is named `Send`.

Wire fields stay camelCase. The client types use those names.

```ts
const ChatResponse = z.object({
  outputText: z.string(),
  citations: z.array(
    z.object({
      id: z.string(),
      sourceFile: z.string(),
      sourcePage: z.number().int().positive(),
      content: z.string(),
    }),
  ),
})
```

A chat request is JSON and nothing else:

```ts
await fetch('/chat', {
  method: 'POST',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: question }],
  }),
})
```

An upload is `multipart/form-data` with one field named `file`. New test titles are sentences such as `the page should show the cited page`. The existing test `renders the chat page at /` keeps its name.

### Page

What is already on the page stays visible: the heading, the description `Ask questions about your documents.`, the message box, and Send.

The page adds:

- A file input named `Upload PDF`. It accepts a PDF. The control posts that file to `POST /documents`.
- A document list. Each row shows `sourceFile` and `pageCount`. No documents: `No documents yet.`
- The transcript. No successful answer yet: `No messages yet.`

Upload:

- `201` and `200` both mean the file is stored. The list includes that `id` once. A second upload of the same bytes does not add a second row.
- `415` and `422` show `error.message` and leave the list as it was.
- The input is disabled while the upload request is in flight.

Question:

- Send stays disabled while the message is blank or a chat request is in flight. A blank message does not call `POST /chat`.
- A `200` appends the question and `outputText` to the transcript.
- When `citations` is not empty, the page shows a list. Each item shows `sourceFile`, `sourcePage`, and `content`.
- When `citations` is empty, the page shows `outputText` and no citation list. The stub uses `No stored document answers that.`
- A failed chat shows `error.message` and keeps the typed question.

Any other failure, including a response that is not the error envelope, shows `The API could not be reached.` The page does not invent the API's own messages. It shows the `message` field it received.

| API message | When the page shows it |
| --- | --- |
| `Upload must be a PDF.` | Upload returned 415 |
| `PDF has no text layer.` | Upload returned 422 |
| `Internal server error.` | Either call returned 500 |

## Testing strategy

Vitest, Testing Library, and MSW. Render with `renderWithProviders` from `@/test/render`. Override handlers with `server.use(...)` from `@/test/server`.

`npm run check` from `src/frontend` is the gate. It does not start `make dev`.

Tests:

1. The existing test still finds the heading `MyHealth AI` and the textbox named `Message`.
2. Choosing a file shows `sourceFile` and `pageCount` from `POST /documents`. The list request is mocked.
3. Sending `What is the DemoMarker value?` shows `outputText` and a citation whose `content` is `DemoMarker value is 10 units.`, whose `sourceFile` is `example.pdf`, and whose `sourcePage` is 1.
4. An empty `citations` array shows `No stored document answers that.` and no citation.
5. A 415 upload shows `Upload must be a PDF.`

Manual check, after the tests pass:

1. Start `make dev` from `src/backend` with `PROFILE` unset.
2. Start `npm run dev` from `src/frontend`.
3. Upload a one-page PDF whose text is `DemoMarker value is 10 units.`
4. Ask `What is the DemoMarker value?`
5. The page shows that sentence, `example.pdf` or the chosen file name, and page 1.

## Boundaries

Always:

- Call `POST /documents` and `POST /chat` as [SPEC-app-shell.md](SPEC-app-shell.md) defines them.
- Show API text as text.
- Mock every request in a test.
- Run `npm run check` in `src/frontend` before a commit that touches it.
- Keep the fixture sentence `DemoMarker value is 10 units.`

Ask first:

- A new npm dependency.
- A route other than `/`.
- Drag-and-drop, a PDF viewer, or a thumbnail of the page.
- A change to an API message, status code, or JSON field.

Never:

- Edit `src/backend` from this module.
- Add a backend route or a request field.
- Commit a real health record, or a realistic patient narrative, in a fixture or a test name.
- Send the PDF to any host except the app API through the dev proxy.
- Render `outputText` or citation `content` as HTML.
- Add auth, streaming, speech, or stored chat history.
- Start Docker, Compose, Minikube, or the backend `local` group from `npm run check`.

## Success criteria

1. `npm run check` passes in `src/frontend`.
2. `/` still shows the heading `MyHealth AI` and the message box.
3. With MSW, a chosen PDF appears with its file name and page count, and the fixture question shows the fixture sentence plus `sourceFile`, `sourcePage` 1, and that same sentence as the citation.
4. An empty citation list shows `No stored document answers that.` and no citation.
5. A non-PDF upload shows `Upload must be a PDF.`
6. The manual check against `make dev` shows the fixture sentence cited on page 1.
7. [capability-map.md](capability-map.md) links this spec.
8. `src/backend` is unchanged by this module.

## Open questions

None. The choices in the assumptions section are the contract for implementation.

## Explicitly later

- A settings page.
- Drag-and-drop upload and a PDF page preview.
- Streaming `POST /chat`.
- Auth, speech, and chat history kept across reloads.
- Hosting the built page. That belongs to `local-runtime`.
