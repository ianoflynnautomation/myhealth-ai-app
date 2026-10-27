# Implementation Plan: local-runtime

## Overview

Run the local profile from [docs/SPEC-local-runtime.md](../docs/SPEC-local-runtime.md). The task list is [tasks/todo.md](todo.md). `tasks/plan.md` stays the closed app-shell plan. `tasks/plan-chat-ui.md` stays the chat-ui plan.

Four pull requests after this plan. Merge each one before cutting the next from `main`.

| PR | Branch | Ids |
| --- | --- | --- |
| 6 | `feature/local-boot` | LR-02–LR-07 |
| 7 | `feature/compose-stack` | LR-08–LR-11 |
| 8 | `feature/gitops-minikube` | LR-12–LR-17 |
| 9 | `feature/gitops-homelab` | LR-18 |

`make check` never starts Docker and never installs the local group. The Compose story and the Minikube story stay manual. Nothing in this plan points the homelab cluster at this repo.

## Architecture decisions

- `PROFILE=local` without injected factories builds the Docling parser, a corpus that implements `StoredCorpus`, and the Ollama chat model. The stub path still does not import `docling` or `qdrant_client`.
- `QdrantCorpus` stays the upsert helper it is today. It does not match `StoredCorpus`: the route calls `add` synchronously and expects `(StoredDocument, created)`, then calls `search`. A new local corpus implements that protocol. It embeds with Ollama and upserts the same camelCase payload the Qdrant tests already lock (`sourceFile`, `sourcePage`, `content`). Point id stays `{document_id}:{page_number}`.
- The local corpus uses a sync HTTP client. The upload route is already async and calls `add` without `await`. `asyncio.run` inside that call would fail.
- Search is the app-shell rule: embed the question, Qdrant hybrid search (BM25 plus the dense vector), and the route still cites `hits[:1]`. The collection is named `pages` and its dense vector size is 768. The query body is a pure function so `make check` does not import `qdrant_client`.
- Chat model `llama3.1`. Embedding model `nomic-embed-text`. `OLLAMA_BASE_URL` includes `/v1`.
- Compose bind-mounts gitignored `./data` at `/data`. The cluster uses a PersistentVolumeClaim named `health-data`. Named Compose volumes are `qdrant-data` and `ollama-models`.
- The web image is nginx. It serves the Vite build and proxies `/documents`, `/chat`, and `/health` to `http://api:8000`. No npm dependency is added.
- Images we build are `myhealth-api:local` and `myhealth-web:local`, with `imagePullPolicy: IfNotPresent`. Upstream image tags and Helm chart versions are pinned in the manifest. `latest` is not used.
- Flux matches the spec. `flux install` does not watch Git. `sync.yaml` is applied once. It is a public `GitRepository` named `flux-system` on `main`, with no secret. The `apps` kustomization then reconciles `./gitops/apps/overlays/myhealth`.
- The Minikube overlay has no Ollama workload. Its API uses `http://host.minikube.internal:11434/v1` and may egress to Qdrant and that host. The homelab overlay adds chart `ollama` from `https://otwld.github.io/ollama-helm`. Its API uses `http://ollama.myhealth.svc.cluster.local:11434/v1`, depends on `ollama`, and may not egress to the host. Qdrant is chart `qdrant` from `https://qdrant.github.io/qdrant-helm`, one replica. The namespace `myhealth` enforces pod security `baseline`, and audits and warns at `restricted`.

## Task list

- [ ] LR-02: Declare the local dependency group
- [ ] LR-03: Build the Docling converter without importing it on the stub path
- [ ] LR-04: Embed a text with the Ollama embeddings route
- [ ] LR-05: Build the hybrid Qdrant query without importing the client
- [ ] LR-06: Store and search pages through the corpus protocol
- [ ] LR-07: Wire the local profile from settings
- [ ] LR-CP2: Local profile boots without Docker
- [ ] LR-08: Build the API image
- [ ] LR-09: Build the web image
- [ ] LR-10: Compose the four services
- [ ] LR-11: Pull both Ollama models before the API starts
- [ ] LR-CP3: Compose file matches the spec
- [ ] LR-12: Watch this repo from the Minikube cluster
- [ ] LR-13: Add the myhealth namespace
- [ ] LR-14: Run the API in the cluster
- [ ] LR-15: Run the web page in the cluster
- [ ] LR-16: Run Qdrant from its Helm chart
- [ ] LR-17: Point the Minikube overlay at api, web, and Qdrant
- [ ] LR-18: Run Ollama on the homelab overlay
- [ ] LR-CP4: GitOps tree matches the spec

## Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| `QdrantCorpus` cannot serve `POST /documents` or `POST /chat` | The live citation check fails after the containers start | LR-06 adds a corpus that matches the route, with fakes, before any image is built |
| Installing Docling in `make check` or CI | The stub gate becomes slow and starts importing native libraries | The group is optional. The test reads the Makefile and the workflow and rejects `--group local` |
| A NetworkPolicy that only allows in-cluster Ollama | Minikube cannot reach the host model | The Minikube API policy allows the host. The homelab policy does not |
| `myhealth-api:local` on a cluster that cannot load the image | The homelab overlay is written and then CrashLooping | LR-18 does not apply the overlay. The images stay local names until a registry is approved |
| Hybrid search needs a current Qdrant query shape | A guessed JSON body does not retrieve the page | LR-05 checks the query against the Qdrant docs when it is written. The unit test asserts the vector and the query text are both present |

## Open questions

None. The live Compose and Minikube checks stay manual until a later session runs them.
