# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Early stage. The frontend foundation is in `src/frontend`. There's no backend or ingestion pipeline yet. `data/` is gitignored. It is meant for local source documents and should never be committed.

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
npx vitest run src/app/App.test.tsx -t "renders"   # single file / single test
```

- **UI**: shadcn/ui (`radix-nova` style) on Tailwind v4. Add components with `npx shadcn@latest add <name>`. Generated code in `src/components/ui/` is vendored. It is excluded from Prettier and the type-aware ESLint rules, so don't hand-reformat it. `cn` comes from shadcn's `cn` package, not clsx/tailwind-merge.
- **Libraries**: TanStack Query (server state), React Router v8 (declarative `<Routes>`), zod (validate API responses), react-hook-form, react-markdown + remark-gfm (render answers, no raw HTML).
- **Imports**: use the `@/` alias for `src/` (set in `tsconfig.json`, `tsconfig.app.json` and `vite.config.ts`).
- **Layout**: `app/` (App, providers, routes), `features/<name>/` (feature code), `components/ui/` (shadcn), `lib/`, `test/`.
- **Linting**: oxlint runs first (correctness, suspicious, jsx-a11y, import, vitest). ESLint adds only typescript-eslint `strictTypeChecked` and react-hooks. `eslint-plugin-oxlint` turns off the overlapping rules. `eslint-plugin-jsx-a11y` is not used, because it doesn't support ESLint 10. a11y comes from oxlint.
- **Tests**: Vitest (jsdom, globals) + Testing Library + MSW 3 (`onUnhandledFrame: 'error'`, so mock every request). Put tests next to the code as `*.test.tsx`. Render with `renderWithProviders` from `@/test/render`, and add network mocks with `server.use(...)` from `@/test/server`.
- **Git hooks**: husky (hooks dir `src/frontend/.husky`, installed by `npm install` via `prepare`) runs lint-staged on commit.

## Intended architecture

The design is in `docs/architecture.md`. It describes a RAG (Retrieval Augmented Generation) chat app over your own documents, running on Azure:

- **Frontend**: a React/TypeScript chat UI with a settings panel and citation display (see above).
- **Backend**: a Java REST API with chat, search, config and document-upload endpoints, plus optional Azure AD auth. Query handling is organised as pluggable "approaches". The first one is `ChatReadRetrieveRead`, which does multi-turn chat with retrieval.
- **Chat query flow**: the frontend sends `POST /chat`. The backend queries Azure AI Search (vector, semantic and full-text) for relevant chunks, sends the query plus that context to Azure OpenAI, and returns the answer with citations. It can optionally log the interaction to Blob Storage.
- **Ingestion flow (PrepDocs pipeline)**: documents go into Blob Storage. Azure Document Intelligence extracts text and layout, the pipeline splits it into chunks, Azure OpenAI generates embeddings, and the result is indexed in Azure AI Search. This pipeline is separate from the request-serving backend.
- **Optional features**: GPT-4 Vision for image-heavy docs, Azure Speech, Cosmos DB chat history, auth, and private endpoints.
- **Hosting**: Azure Container Apps by default, or App Service. Telemetry goes to Application Insights and secrets live in Key Vault. Infrastructure lives in a **separate infra repo**, not here.

Known inconsistencies in `docs/architecture.md` (check with the user before relying on them):
- The backend is labelled both "Java API" and "Flask/Quart", which are Python frameworks. The intended backend language is unresolved.
- It links to `README.md`, `docs/http_protocol.md`, `docs/deploy_features.md` and `docs/appservice.md`, none of which exist yet.

## Agent workflow tooling

`.claude/` holds project skills, slash commands (`/spec`, `/planning`, `/build`, `/test`, `/review`, `/code-simplify`, `/ship`, `/constraints`) and agent personas (code-reviewer, security-auditor, test-engineer, web-performance-auditor). `.claude/skills/using-agent-skills/SKILL.md` maps each development phase to its skill. `.grok/` mirrors the same content for another agent tool. If you change one copy, keep the other in sync.
