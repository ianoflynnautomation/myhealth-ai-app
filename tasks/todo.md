# Tasks: chat-ui and local-runtime

Finished work: [tasks/app-shell.md](app-shell.md). Map: [docs/capability-map.md](../docs/capability-map.md).

`chat-ui` has an approved spec: [docs/SPEC-chat-ui.md](../docs/SPEC-chat-ui.md). Plan: [tasks/plan-chat-ui.md](plan-chat-ui.md). `local-runtime` does not have a spec yet. LR-01 writes that spec. Implementation tasks for a module are added only after a human approves that spec.

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
**Completed:**

**Description:** Specify Compose for Ollama, Qdrant, and the API, and a Minikube profile that uses the same images. Ollama stays on the host at `host.minikube.internal:11434` unless the spec chooses a different place and says why. This task does not add Compose files or a cluster manifest.

**Status:** open

**Acceptance criteria:**

- [ ] `docs/SPEC-local-runtime.md` states the objective, commands, project structure, code style, testing strategy, boundaries, and success criteria.
- [ ] The spec names how the API container gets `PROFILE=local` and the service URLs. It does not change the app-shell HTTP contract.
- [ ] A live stack is out of `make check`. The spec says which check runs it.
- [ ] [docs/capability-map.md](../docs/capability-map.md) links this spec.

**Verification:**

- [ ] A human reviews the spec before any local-runtime implementation task is added.

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

- [x] `npx vitest run src/api/devProxy.test.ts -t "should proxy"` from `src/frontend`.

**Dependencies:** CU-CP1

**Files likely touched:**

- `src/frontend/vite.config.ts`
- `src/frontend/src/api/devProxy.test.ts`

**Estimated scope:** Small

## CU-03: Parse a stored document from the API

**Id:** CU-03
**Completed:**

**Description:** Add a document client. It parses the list and upload JSON with zod. An upload sends `FormData` with the field name `file` and does not set `Content-Type`.

**Status:** open

**Acceptance criteria:**

- [ ] A 201 body `{ "id", "sourceFile", "pageCount", "chunkCount" }` parses.
- [ ] The upload request is multipart, the field name is `file`, and the client does not set `Content-Type`.
- [ ] A 415 body returns the message `Upload must be a PDF.`
- [ ] A non-JSON error becomes `The API could not be reached.`

**Verification:**

- [ ] `npx vitest run src/api/documents.test.ts -t "should post the file"` from `src/frontend`.

**Dependencies:** CU-CP1

**Files likely touched:**

- `src/frontend/src/api/documents.ts`
- `src/frontend/src/api/errors.ts`
- `src/frontend/src/api/documents.test.ts`

**Estimated scope:** Small

## CU-04: The page lists stored documents

**Id:** CU-04
**Completed:**

**Description:** Opening the page calls `GET /documents`. A stored file shows `sourceFile` and `pageCount`. A successful empty list shows `No documents yet.`

**Status:** open

**Acceptance criteria:**

- [ ] The heading `MyHealth AI` and the textbox named `Message` stay on the page.
- [ ] An empty list shows `No documents yet.`
- [ ] A stored file shows its `sourceFile` and `pageCount`.

**Verification:**

- [ ] `npx vitest run src/features/chat/ChatPage.test.tsx -t "should list a stored pdf"` from `src/frontend`.
- [ ] `npx vitest run src/app/App.test.tsx -t "renders the chat page"` from `src/frontend`.

**Dependencies:** CU-03

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/ChatPage.test.tsx`
- `src/frontend/src/test/server.ts`

**Estimated scope:** Small

## CU-05: A failed document list is not an empty store

**Id:** CU-05
**Completed:**

**Description:** When `GET /documents` fails, the page does not show `No documents yet.` A network failure shows `The API could not be reached.` An error envelope shows `error.message`.

**Status:** open

**Acceptance criteria:**

- [ ] A network failure shows `The API could not be reached.`
- [ ] That failure does not show `No documents yet.`

**Verification:**

- [ ] `npx vitest run src/features/chat/ChatPage.test.tsx -t "should not call an empty store"` from `src/frontend`.

**Dependencies:** CU-04

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-06: An upload shows the file once

**Id:** CU-06
**Completed:**

**Description:** Choosing a PDF posts it to `POST /documents`. `201` and `200` both show that `id` once. The same bytes do not add a second row.

**Status:** open

**Acceptance criteria:**

- [ ] After a 201, the list shows that file's `sourceFile` and `pageCount`.
- [ ] A 200 for an `id` already on the page does not add a second row.

**Verification:**

- [ ] `npx vitest run src/features/chat/ChatPage.test.tsx -t "should show an uploaded pdf once"` from `src/frontend`.

**Dependencies:** CU-03, CU-04

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-07: A rejected upload shows the API message

**Id:** CU-07
**Completed:**

**Description:** A failed upload shows `error.message` and leaves the document list as it was.

**Status:** open

**Acceptance criteria:**

- [ ] A 415 response shows `Upload must be a PDF.`
- [ ] The files already listed stay listed.

**Verification:**

- [ ] `npx vitest run src/features/chat/ChatPage.test.tsx -t "should show the upload error"` from `src/frontend`.

**Dependencies:** CU-06

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-08: A blank question does not send

**Id:** CU-08
**Completed:**

**Description:** Send stays disabled while the trimmed message is empty. That message does not call `POST /chat`.

**Status:** open

**Acceptance criteria:**

- [ ] Send is disabled for an empty message and for a message that is only spaces.
- [ ] Neither case calls `POST /chat`.

**Verification:**

- [ ] `npx vitest run src/features/chat/ChatPage.test.tsx -t "should not send a blank question"` from `src/frontend`.

**Dependencies:** CU-04

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-09: The page shows the answer and the citation

**Id:** CU-09
**Completed:**

**Description:** A question calls `POST /chat` with one user message. The page shows `outputText` and, for each citation, `sourceFile`, `sourcePage`, and `content`.

**Status:** open

**Acceptance criteria:**

- [ ] The request body is `{ "messages": [{ "role": "user", "content": "What is the DemoMarker value?" }] }`.
- [ ] The page shows `DemoMarker value is 10 units.`
- [ ] The citation shows `example.pdf`, page 1, and that same sentence.

**Verification:**

- [ ] `npx vitest run src/features/chat/ChatPage.test.tsx -t "should show the cited page"` from `src/frontend`.

**Dependencies:** CU-08

**Files likely touched:**

- `src/frontend/src/api/chat.ts`
- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/ChatPage.test.tsx`

**Estimated scope:** Medium

## CU-10: An empty citation list shows the fixed sentence

**Id:** CU-10
**Completed:**

**Description:** When `citations` is empty, the page shows `outputText` and no citation list.

**Status:** open

**Acceptance criteria:**

- [ ] The page shows `No stored document answers that.`
- [ ] The page shows no citation.

**Verification:**

- [ ] `npx vitest run src/features/chat/ChatPage.test.tsx -t "should show the fixed sentence"` from `src/frontend`.

**Dependencies:** CU-09

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/ChatPage.test.tsx`

**Estimated scope:** Small

## CU-11: A failed question keeps the typed text

**Id:** CU-11
**Completed:**

**Description:** A failed chat shows `error.message` and leaves the typed question in the message box.

**Status:** open

**Acceptance criteria:**

- [ ] A 500 response shows `Internal server error.`
- [ ] The message box still contains the question.

**Verification:**

- [ ] `npx vitest run src/features/chat/ChatPage.test.tsx -t "should keep the typed question"` from `src/frontend`.

**Dependencies:** CU-09

**Files likely touched:**

- `src/frontend/src/features/chat/ChatPage.tsx`
- `src/frontend/src/features/chat/ChatPage.test.tsx`

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
**Completed:**

- [ ] LR-01 is merged.
- [ ] A human has approved `docs/SPEC-local-runtime.md`.
- [ ] Implementation tasks for local-runtime are added to this file only after that approval.
