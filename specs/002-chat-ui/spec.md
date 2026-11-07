# Feature Specification: chat-ui

**Feature Branch**: `002-chat-ui` (delivered across the PR branches listed in [plan.md](plan.md))

**Created**: 2026-10-23

**Status**: Implemented. The manual check against the stub API (SC-006) is still open.

**Input**: Module `chat-ui` from [docs/capability-map.md](../../docs/capability-map.md). The existing React page uploads a PDF and shows an answer with the cited file and page. It consumes [the app-shell HTTP contract](../001-app-shell/contracts/http.md) unchanged. Before this module the page at `/` was a placeholder: a heading, an empty transcript, a message box and a disabled Send button, with no API calls.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload a PDF and see it listed (Priority: P1)

I choose a PDF and the page shows that file's name and page count. When I reload, files still stored in that API process are listed.

**Why this priority**: A question can't be answered until the person has stored a document and can see that it was stored.

**Independent Test**: In the frontend suite, mock `GET /documents` and `POST /documents`, choose a file, and see the row.

**Acceptance Scenarios**:

1. **Given** the API returns an empty list, **When** the page opens, **Then** it shows `No documents yet.`
2. **Given** the page is open, **When** I choose a PDF and the upload returns 201 or 200, **Then** the list shows its `sourceFile` and `pageCount`, once per `id`.
3. **Given** a stored file, **When** I upload the same bytes again, **Then** there is still one row.
4. **Given** the upload returns 415 or 422, **When** the response is the error envelope, **Then** the page shows `error.message` (for example `Upload must be a PDF.`) and the list does not change.
5. **Given** the list request fails, **When** the page renders, **Then** it shows the envelope's `error.message`, or `The API could not be reached.` if the body is not the envelope. It does not show `No documents yet.`
6. **Given** an upload is in flight, **When** I look at the file input, **Then** it is disabled.

---

### User Story 2 - Ask and see a cited answer (Priority: P1)

I ask a question and the page shows the answer. Each citation shows the file, the page and the quoted text.

**Why this priority**: The answer with its citation is what the product is for.

**Independent Test**: In the frontend suite, mock `POST /chat` with the fixture citation and check the transcript.

**Acceptance Scenarios**:

1. **Given** the message box is empty or only whitespace, **When** I look at Send, **Then** it is disabled and no `POST /chat` is made.
2. **Given** I send `What is the DemoMarker value?`, **When** the API returns the fixture citation, **Then** the transcript shows the question, `outputText`, and a citation with `example.pdf`, page 1 and `DemoMarker value is 10 units.`
3. **Given** the API returns an empty `citations` list, **When** the answer renders, **Then** the page shows `No stored document answers that.` and no citation list.
4. **Given** the chat call fails, **When** the error renders, **Then** the page shows `error.message` (or `The API could not be reached.`) and keeps the typed question in the box.
5. **Given** a chat request is in flight, **When** I look at Send, **Then** it is disabled.

---

### User Story 3 - Test the page without the API (Priority: P2)

As the developer, I run User Stories 1 and 2 in `npm run check` with no API process.

**Independent Test**: `npm run check` in `src/frontend` with nothing listening on port 8000.

**Acceptance Scenarios**:

1. **Given** MSW with `onUnhandledFrame: 'error'`, **When** the suite runs, **Then** every request the page makes is mocked and the suite passes.

---

### User Story 4 - The page cites a real stub upload (Priority: P3)

With `make dev` and `npm run dev` running, a one-page PDF whose text is `DemoMarker value is 10 units.` is cited when I ask `What is the DemoMarker value?`

**Independent Test**: The manual check in [plan.md](plan.md#manual-check).

### Edge Cases

- A response that is not the error envelope, or a network failure, shows `The API could not be reached.` The page never invents an API message.
- A refetch of the list after an upload must not drop the new row. Rows merge by `id`.
- Earlier questions stay on screen until reload. They are not sent again.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The page MUST keep its existing elements: the heading `MyHealth AI`, the description `Ask questions about your documents.`, the textbox named `Message`, and the button named `Send`.
- **FR-002**: The page MUST load `GET /documents` on open and list each document's `sourceFile` and `pageCount`.
- **FR-003**: The page MUST offer a PDF-only file input named `Upload PDF` that posts the file to `POST /documents` as multipart field `file`, without setting `Content-Type` by hand.
- **FR-004**: The page MUST treat 201 and 200 uploads as stored and show each `id` once.
- **FR-005**: The page MUST show `error.message` from the envelope for failed list, upload and chat calls, and `The API could not be reached.` for any other failure.
- **FR-006**: A failed list MUST NOT show `No documents yet.`
- **FR-007**: The file input MUST be disabled while an upload is in flight. Send MUST be disabled while the trimmed message is empty or a chat request is in flight.
- **FR-008**: Each chat request MUST send exactly one message, `{ "role": "user", "content": <question> }`, as JSON.
- **FR-009**: A successful answer MUST be appended to the transcript with its question. Non-empty `citations` render as a list of `sourceFile`, `sourcePage` and `content`. Empty `citations` render no list.
- **FR-010**: The transcript MUST show `No messages yet.` until the first successful answer.
- **FR-011**: A failed chat MUST keep the typed question.
- **FR-012**: `outputText` and citation `content` MUST render as text, not HTML or Markdown.
- **FR-013**: Every response the page reads MUST be parsed with zod using the wire names.
- **FR-014**: In dev, Vite MUST proxy `/documents` and `/chat` to `http://127.0.0.1:8000`, and the page MUST call those relative paths.

### Key Entities

Same as app-shell: Document, Citation, Chat message. There are no new entities.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `npm run check` passes in `src/frontend`.
- **SC-002**: `/` still shows the heading `MyHealth AI` and the message box, and the existing test `renders the chat page at /` keeps its name.
- **SC-003**: With MSW, a chosen PDF appears with its name and page count, and the fixture question shows the fixture sentence plus `sourceFile`, `sourcePage` 1 and the same sentence as the citation.
- **SC-004**: An empty citation list shows `No stored document answers that.` and no citation.
- **SC-005**: A non-PDF upload shows `Upload must be a PDF.`
- **SC-006**: The manual check against `make dev` shows the fixture sentence cited on page 1.
- **SC-007**: `src/backend` is unchanged by this module.

## Assumptions

- The only route is `/`. There is no settings page.
- The page doesn't choose stub or local. It talks to whichever API the proxy reaches.
- Upload is one file input, PDF only.
- The fixture sentence is `DemoMarker value is 10 units.`

## Out of Scope

- A settings page.
- Drag-and-drop upload, and a PDF page preview or thumbnail.
- Streaming `POST /chat`.
- Auth, speech, and chat history kept across reloads.
- Hosting the built page, which belongs to `003-local-runtime`.
