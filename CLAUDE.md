# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

A local RAG app over your own medical PDFs. `src/backend` is a Python 3.13 FastAPI API (stub and local profiles). `src/frontend` is the React page. `compose.yaml` runs the local stack. `data/` is gitignored. It is meant for local source documents and should never be committed.

## Spec-driven development (spec-kit)

Specs, plans and tasks live in `specs/NNN-module/` (`spec.md`, `plan.md`, `tasks.md`, optional `contracts/`). Module ids and build order are in `docs/capability-map.md`. The non-negotiable rules are in `.specify/memory/constitution.md`.

| Feature | Status |
| --- | --- |
| `specs/001-app-shell` | Implemented. HTTP contract in `contracts/http.md`. |
| `specs/002-chat-ui` | Implemented. Manual check open. |
| `specs/003-local-runtime` | In progress. LR-19/LR-20 on `feature/compose-stack`, then GitOps T016–T025. |

- The workflow is `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`. A new module gets the next `NNN`.
- To work on an existing feature, point spec-kit at it: `SPECIFY_FEATURE_DIRECTORY=specs/003-local-runtime`, or set `.specify/feature.json`, which is gitignored and per checkout.
- Every task line keeps its stable id in parentheses (`AS-`, `CU-`, `LR-`, `CI-`). Commits and PR titles use that id. It is never renumbered.
- One task is one failing test, then the code that passes it, then one commit. Mark it `[X]` with the commit date.
- The older agent-skills commands (`/spec`, `/planning`, `/build`) expect `SPEC.md` and `tasks/todo.md`, which no longer exist. Use the `speckit-*` commands for feature work.

## Backend (`src/backend`)

Python 3.13, uv, FastAPI, Pydantic v2. Run from `src/backend`: `uv sync`, `make dev` (stub on 127.0.0.1:8000), `make check` (ruff, ruff format, pyright strict, pytest). `make check` never needs Docker or the `local` group (`uv sync --group local` adds Docling and qdrant-client). See `specs/001-app-shell/plan.md`.

## Frontend (`src/frontend`)

React 19 + TypeScript 6 + Vite 8, with Node >= 24 (`.nvmrc`). Run every command from `src/frontend`:

```sh
npm run dev            # dev server
npm run build          # tsc -b && vite build
npm run typecheck      # tsc -b --noEmit
npm run lint           # oxlint && eslint .   (lint:fix to autofix)
npm run format         # prettier --write .   (format:check in CI)
npm test               # vitest run           (test:watch, test:coverage)
npm run check          # typecheck + lint + format:check + test, the full gate
npx vitest run src/app/__tests__/App.test.tsx -t "renders"   # single file / single test
```

- **UI**: shadcn/ui (`radix-nova` style) on Tailwind v4. Add components with `npx shadcn@latest add <name>`. Generated code in `src/components/ui/` is vendored. It is excluded from Prettier and the type-aware ESLint rules, so don't hand-reformat it. `cn` comes from shadcn's `cn` package, not clsx/tailwind-merge.
- **Libraries**: TanStack Query (server state), React Router v8 (declarative `<Routes>`), zod (validate API responses), react-hook-form, react-markdown + remark-gfm (render answers, no raw HTML).
- **Imports**: use the `@/` alias for `src/` (set in `tsconfig.json`, `tsconfig.app.json` and `vite.config.ts`).
- **Layout**: `app/` (App, providers, routes), `features/<name>/` (feature code), `components/ui/` (shadcn), `lib/`, `test/`.
- **Linting**: oxlint runs first (correctness, suspicious, jsx-a11y, import, vitest). ESLint adds only typescript-eslint `strictTypeChecked` and react-hooks. `eslint-plugin-oxlint` turns off the overlapping rules. `eslint-plugin-jsx-a11y` is not used, because it doesn't support ESLint 10. a11y comes from oxlint.
- **Tests**: Vitest (jsdom, globals) + Testing Library + MSW 3 (`onUnhandledFrame: 'error'`, so mock every request). Put tests in a `__tests__` folder next to the code, named `*.test.ts` or `*.test.tsx`. Render with `renderWithProviders` from `@/test/render`, and add network mocks with `server.use(...)` from `@/test/server`.
- **Git hooks**: husky (hooks dir `src/frontend/.husky`, installed by `npm install` via `prepare`) runs lint-staged on commit.

## Reference architecture

`docs/architecture.md` describes the Azure reference design this app is modelled on. The local build replaces Document Intelligence, Azure AI Search, Azure OpenAI and Blob Storage with Docling, Qdrant, Ollama and `data/` (see `specs/001-app-shell/plan.md`). The Azure design:

- **Frontend**: a React/TypeScript chat UI with a settings panel and citation display (see above).
- **Backend**: a REST API with chat, search, config and document-upload endpoints, plus optional Azure AD auth. Query handling is organised as pluggable "approaches". The first one is `ChatReadRetrieveRead`, which does multi-turn chat with retrieval.
- **Chat query flow**: the frontend sends `POST /chat`. The backend queries Azure AI Search (vector, semantic and full-text) for relevant chunks, sends the query plus that context to Azure OpenAI, and returns the answer with citations. It can optionally log the interaction to Blob Storage.
- **Ingestion flow (PrepDocs pipeline)**: documents go into Blob Storage. Azure Document Intelligence extracts text and layout, the pipeline splits it into chunks, Azure OpenAI generates embeddings, and the result is indexed in Azure AI Search. This pipeline is separate from the request-serving backend.
- **Optional features**: GPT-4 Vision for image-heavy docs, Azure Speech, Cosmos DB chat history, auth, and private endpoints.
- **Hosting**: Azure Container Apps by default, or App Service. Telemetry goes to Application Insights and secrets live in Key Vault. Infrastructure lives in a **separate infra repo**, not here.

Known inconsistencies in `docs/architecture.md`, tracked as `specs/001-app-shell/tasks.md` T042:
- It labels the backend "Java API" and "Flask/Quart". The backend is Python (FastAPI). Ignore the Java label.
- It links to `README.md`, `docs/http_protocol.md`, `docs/deploy_features.md` and `docs/appservice.md`, none of which exist. The HTTP contract is `specs/001-app-shell/contracts/http.md`.

## Agent workflow tooling

`.claude/skills/speckit-*` and `.specify/` are spec-kit (v1.3.2, managed by the Specify CLI). Don't hand-edit `.specify/scripts` or `.specify/templates`, because their hashes are tracked. `.claude/` also holds project skills, slash commands (`/spec`, `/planning`, `/build`, `/test`, `/review`, `/code-simplify`, `/ship`, `/constraints`) and agent personas (code-reviewer, security-auditor, test-engineer, web-performance-auditor). `.claude/skills/using-agent-skills/SKILL.md` maps each development phase to its skill. `.grok/` mirrors the same content for another agent tool. If you change one copy, keep the other in sync.
