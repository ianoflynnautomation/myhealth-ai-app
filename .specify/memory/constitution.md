<!--
Sync Impact Report
- Version change: 1.0.0 → 1.0.1 (PATCH, wording only)
  - I: "Published ports" now reads "Host-published ports". A container may listen on 0.0.0.0 inside its own network.
  - VI: the approval rule names a host-published port on 0.0.0.0, and the ports are listed by their code names (StoredCorpus, Parser, ChatModel).
- Previous: template → 1.0.0 (first ratification)
- Principles added:
  I. Health Records Stay Local (NON-NEGOTIABLE)
  II. Grounded, Cited Answers
  III. One HTTP Contract
  IV. Test-First Thin Slices (NON-NEGOTIABLE)
  V. Offline Quality Gates
  VI. Modules, Ports, and Simplicity
- Sections added: Technology Constraints, Development Workflow, Governance
- Source: the Boundaries and Assumptions sections of the app-shell, chat-ui and
  local-runtime specs (formerly docs/SPEC-*.md, now specs/001–003), and CLAUDE.md.
- Templates: plan-template.md, spec-template.md and tasks-template.md need no change.
  The Constitution Check in each plan lists these principles by number.
- Deferred: none.
-->

# MyHealth AI Constitution

MyHealth AI answers questions about a person's own medical PDFs and cites the file and page. These principles bind every spec, plan and task in `specs/`.

## Core Principles

### I. Health Records Stay Local (NON-NEGOTIABLE)

- A PDF, a page chunk, or an embedding MUST NOT go to any host other than the configured Ollama and Qdrant URLs. There is no hosted parser, hosted model or hosted vector service.
- `data/`, model weights, `.venv`, and secrets MUST NOT be committed. A secret that a manifest needs is a SOPS file plus an example file. It is never a plain value.
- Fixtures, prompt examples and test names MUST be synthetic. A real health record or a realistic patient narrative never goes in the repo. The fixture sentence is `DemoMarker value is 10 units.`
- Host-published ports bind to `127.0.0.1` unless a spec approves otherwise. A process may listen on `0.0.0.0` inside its own container network.

Rationale: the corpus is personal health data. A leak can't be undone.

### II. Grounded, Cited Answers

- An answer MUST come only from chunks that were retrieved for that question. The chat model never gets the rest of the PDF.
- Every answer that uses a document MUST cite the stored file and its 1-based page.
- When nothing matches, the API returns the fixed sentence `No stored document answers that.` with no citations. It does not invent an answer.
- The UI shows answer and citation text as plain text, never as HTML.

Rationale: an uncited health answer can't be checked, and a misread one can cause harm.

### III. One HTTP Contract

- The wire contract in `specs/001-app-shell/contracts/http.md` is the only API definition. Later modules consume it. They MUST NOT add a route, a request field, a response field, a status code or a message.
- JSON on the wire is camelCase. Python is snake_case, with Pydantic aliases at the boundary. TypeScript uses the wire names.
- Input MUST be validated at the boundary: Pydantic on both POST routes, zod on every response the page reads. Errors use the `{ "error": { code, message, details } }` envelope. A 500 never carries a stack trace.
- A contract change starts as a spec change in `specs/001-app-shell` and is approved before any code changes.

### IV. Test-First Thin Slices (NON-NEGOTIABLE)

- A task is one behavior, one test, and the minimum code that makes it pass, in one commit.
- The named test MUST fail first (RED), then pass (GREEN). A test that passes on its first run does not count.
- Tests mock every network call. The frontend runs MSW with `onUnhandledFrame: 'error'`. The backend injects fakes for Docling, Qdrant and Ollama.
- Task ids are stable. They are never renumbered or reused.

### V. Offline Quality Gates

- `make check` in `src/backend` (ruff, ruff format, pyright strict, pytest) and `npm run check` in `src/frontend` MUST pass with no Docker daemon, no network, and without the backend `local` dependency group.
- The stub profile MUST NOT import `docling` or `qdrant_client`, open a connection to a service host, or write under `data/`.
- CI runs the same gates. CI never runs Compose or Minikube and never installs the `local` group.
- Live checks against Compose, Minikube or `make dev` are manual and are written down in the feature's plan.

### VI. Modules, Ports, and Simplicity

- Work follows the module order in `docs/capability-map.md`. One feature folder in `specs/` is one module.
- A module does not edit another module's code unless its spec says so. For example, `chat-ui` does not edit `src/backend`.
- `Parser`, `StoredCorpus` and `ChatModel` are the ports in app-shell. A port is added when a second implementation needs it, and later modules don't redefine it.
- Start simple. One chunk per page. One index. No streaming, auth, speech or chat history until a spec asks for it.
- These need explicit approval first: a new dependency, a new route, a CI change, a uv workspace, or publishing a host port on `0.0.0.0`.

## Technology Constraints

- Backend: Python 3.13, uv, FastAPI, Pydantic v2, httpx, pypdf. The optional `local` group adds `docling` and `qdrant-client`. The project lives in `src/backend`.
- Frontend: React 19, TypeScript, Vite, Node >= 24, shadcn/ui on Tailwind v4, TanStack Query, zod, Vitest, Testing Library, MSW. The project lives in `src/frontend`.
- Local runtime: Ollama (`llama3.1`, `nomic-embed-text`, 768 dimensions), Qdrant with hybrid BM25 plus dense search, Docker Compose, and Flux GitOps on Minikube. Upstream image tags and chart versions are pinned. `latest` is never used.
- Hosted Azure services from `docs/architecture.md` are replaced by these local pieces until a spec says otherwise.

## Development Workflow

1. `/speckit-specify` writes `specs/NNN-module/spec.md`. The module id comes from `docs/capability-map.md`.
2. `/speckit-clarify` settles open questions. A spec has no `[NEEDS CLARIFICATION]` markers when it is approved.
3. `/speckit-plan` writes `plan.md` and passes the Constitution Check below.
4. `/speckit-tasks` writes `tasks.md`. `/speckit-analyze` must report no CRITICAL findings before implementation starts.
5. `/speckit-implement` runs the tasks in order, one task per commit, under Principle IV.
6. Each feature lists its pull requests and branches in its plan. Merge one pull request before cutting the next branch from `main`.
7. Run `make check` or `npm run check` for each package a commit touches.

## Governance

- This constitution overrides other practice docs. `CLAUDE.md` gives runtime guidance and must not contradict it.
- A conflict with a MUST is CRITICAL. The fix goes into the spec, plan or tasks. The principle is not weakened to fit.
- Amendments go through `/speckit-constitution` and update the Sync Impact Report. Versions follow semantic versioning. MAJOR removes or redefines a principle, MINOR adds one or expands it materially, PATCH clarifies wording.
- Every plan's Constitution Check and every review checks compliance with these principles.

**Version**: 1.0.1 | **Ratified**: 2026-11-07 | **Last Amended**: 2026-11-07
