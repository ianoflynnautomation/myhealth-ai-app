# MyHealth AI frontend

React 19 + TypeScript + Vite chat UI for the RAG app (see `../../docs/architecture.md`).

**Stack:** shadcn/ui (Radix) on Tailwind CSS v4 · TanStack Query · React Router · zod · react-hook-form · react-markdown
**Tooling:** oxlint + ESLint (type-aware) · Prettier · Vitest + Testing Library + MSW · husky + lint-staged

```sh
npm install
npm run dev          # http://localhost:5173
npm run check        # typecheck + lint + format check + tests (run before pushing)
```

Add shadcn components with `npx shadcn@latest add <name>`. They are generated into `src/components/ui/` and excluded from the strict lint and format rules.
