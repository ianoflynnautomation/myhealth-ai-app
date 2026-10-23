# Tasks: chat-ui and local-runtime

Finished work: [tasks/app-shell.md](app-shell.md). Map: [docs/capability-map.md](../docs/capability-map.md).

`chat-ui` and `local-runtime` do not have specs yet. These tasks write the specs. Implementation tasks are added only after a human approves the spec for that module. The two modules do not depend on each other, so their branches can be open at the same time.

## How to record completion

- **Id** is stable. `CU-01` and `LR-01` are never renumbered or reused.
- **Completed** is the date of the task commit, `YYYY-MM-DD`. Leave it blank until that commit exists.
- One pull request is one branch from the table. Cut it from `main`.
- Do not add implementation tasks to these branches.

| PR | Branch | Id | Module |
| --- | --- | --- | --- |
| 1 | `docs/chat-ui-spec` | CU-01 | chat-ui |
| 2 | `docs/local-runtime-spec` | LR-01 | local-runtime |

## CU-01: Write the chat-ui spec

**Id:** CU-01
**Completed:**

**Description:** Specify how the existing React page uploads a PDF and shows an answer with citations. The page today is a placeholder. The HTTP contract stays the one in [docs/SPEC-app-shell.md](../docs/SPEC-app-shell.md). This task does not change `src/frontend` or `src/backend`.

**Status:** open

**Acceptance criteria:**

- [ ] `docs/SPEC-chat-ui.md` states the objective, commands, project structure, code style, testing strategy, boundaries, and success criteria.
- [ ] The spec uses `POST /documents` and `POST /chat` as they are. It does not add a backend route.
- [ ] The fixture sentence remains `DemoMarker value is 10 units.`
- [ ] [docs/capability-map.md](../docs/capability-map.md) links this spec.

**Verification:**

- [ ] A human reviews the spec before any chat-ui implementation task is added.

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

## CU-CP1: chat-ui spec approved

**Id:** CU-CP1
**Completed:**

- [ ] CU-01 is merged.
- [ ] A human has approved `docs/SPEC-chat-ui.md`.
- [ ] Implementation tasks for chat-ui are added to this file only after that approval.

## LR-CP1: local-runtime spec approved

**Id:** LR-CP1
**Completed:**

- [ ] LR-01 is merged.
- [ ] A human has approved `docs/SPEC-local-runtime.md`.
- [ ] Implementation tasks for local-runtime are added to this file only after that approval.
