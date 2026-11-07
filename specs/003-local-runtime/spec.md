# Feature Specification: local-runtime

**Feature Branch**: `003-local-runtime` (delivered across the PR branches listed in [plan.md](plan.md))

**Created**: 2026-10-27

**Status**: In progress. The local boot and the Compose stack are built. The GitOps tree (User Stories 3 and 4) is open.

**Input**: Module `local-runtime` from [docs/capability-map.md](../../docs/capability-map.md). It runs the local profile in Docker Compose, and runs the same images in a Minikube profile reconciled by Flux. It consumes [the app-shell HTTP contract](../001-app-shell/contracts/http.md) unchanged.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One command starts the whole stack (Priority: P1)

I run one Compose command. The page opens on this machine. I don't start Qdrant or Ollama by hand.

**Why this priority**: It is the simplest way to run the local profile end to end.

**Independent Test**: `docker compose up --build`, then open `http://127.0.0.1:8080`.

**Acceptance Scenarios**:

1. **Given** Docker is running, **When** I run `docker compose up --build`, **Then** `web`, `api`, `qdrant` and `ollama` start, and the API waits until both models are pulled.
2. **Given** the stack is up, **When** I call `GET /health` on `127.0.0.1:8000`, **Then** it returns the existing health JSON.
3. **Given** the stack is up, **When** I list the published ports, **Then** each one is bound to `127.0.0.1`.

---

### User Story 2 - A real upload is answered locally (Priority: P1)

I upload a PDF. The bytes stay in `data/`. Chunks and vectors stay in Qdrant. Ollama embeds and answers. The page shows the answer and the citation.

**Why this priority**: It proves the local profile works, not only the stub.

**Independent Test**: The Compose manual check in [plan.md](plan.md#manual-checks).

**Acceptance Scenarios**:

1. **Given** the Compose stack, **When** I upload the one-page fixture PDF and ask `What is the DemoMarker value?`, **Then** the page shows the sentence, the file name and page 1.
2. **Given** that upload, **When** I look on the host, **Then** the PDF bytes are under `data/` and are not in any image.
3. **Given** `PROFILE=local` with the local group installed, **When** the process starts without injected factories, **Then** it builds the Docling parser, a Qdrant-backed corpus and the Ollama chat model from settings.

---

### User Story 3 - The same images on Minikube through Flux (Priority: P2)

I run the same images in a Minikube profile named `myhealth`. Flux reconciles them from Git. Ollama stays on the host, and the API reaches it at `host.minikube.internal:11434`.

**Why this priority**: It rehearses the cluster shape without moving models or the GPU off the host.

**Independent Test**: The offline manifest test in `make check`, then the Minikube manual check.

**Acceptance Scenarios**:

1. **Given** `flux install` and one `kubectl apply -f gitops/clusters/myhealth/sync.yaml`, **When** Flux reconciles, **Then** `api`, `web` and `qdrant` become ready in namespace `myhealth`, and there is no Ollama workload.
2. **Given** the Minikube overlay, **When** the API runs, **Then** its `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1` and its egress allows only Qdrant and that host.
3. **Given** the profile is running, **When** I change it, **Then** I push to `main` and Flux reconciles. Nobody runs `kubectl apply` on a Deployment.

---

### User Story 4 - A homelab overlay with in-cluster Ollama (Priority: P3)

The same Git tree has a homelab overlay where Ollama is its own Flux `Kustomization` and Helm release, the way `gitops/apps/base/ai-system/ollama` is in the homelab repo.

**Why this priority**: It prepares the homelab cluster, but applying it there is a separate ask.

**Independent Test**: The offline manifest test only. The overlay is not applied to a shared cluster.

**Acceptance Scenarios**:

1. **Given** the homelab overlay, **When** I read it, **Then** it lists the Minikube components plus `ollama/ks.yaml`.
2. **Given** the homelab API, **When** I read its environment, **Then** `OLLAMA_BASE_URL` is `http://ollama.myhealth.svc.cluster.local:11434/v1`, it depends on `ollama`, and no manifest mentions `host.minikube.internal`.

---

### User Story 5 - The gate stays offline (Priority: P1)

`make check` still passes with no Docker daemon and without the local dependency group.

**Independent Test**: Run `make check` with Docker stopped.

### Edge Cases

- `docker compose down` keeps the named volumes `qdrant-data` and `ollama-models`. `down -v` deletes them, but not `./data`, because that is a bind mount.
- On Minikube the images are loaded, never pulled: `imagePullPolicy: IfNotPresent`.
- The homelab cluster can't run `myhealth-*:local` images until a registry exists. That is why the overlay is written but not applied.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The local profile MUST build its parser, corpus and chat model from settings when the local group is installed and no factories are injected. Missing settings and a missing local group MUST still fail as they do in app-shell. The stub path MUST still not import the local modules.
- **FR-002**: The local corpus MUST implement the corpus protocol the routes use. It embeds with Ollama, upserts the camelCase payload (`sourceFile`, `sourcePage`, `content`) with point id `{documentId}:{pageNumber}`, and searches with a hybrid BM25 plus dense query on collection `pages`, with 768 dimensions.
- **FR-003**: An API image `myhealth-api:local` MUST be built from `src/backend` with the locked `local` group and without the dev group. It runs `fastapi run` on `0.0.0.0:8000`.
- **FR-004**: A web image `myhealth-web:local` MUST serve the Vite build and proxy `/documents`, `/chat` and `/health` to `http://api:8000`.
- **FR-005**: `compose.yaml` MUST run `web`, `api`, `qdrant` and `ollama`. It publishes `8080`, `8000`, `6333` and `11434` on `127.0.0.1` only. It bind-mounts `./data` at `/data`, uses named volumes `qdrant-data` and `ollama-models`, and pins upstream tags.
- **FR-006**: The API container MUST get `PROFILE=local`, `QDRANT_URL`, `OLLAMA_BASE_URL` (with `/v1`), `OLLAMA_CHAT_MODEL=llama3.1`, `OLLAMA_EMBED_MODEL=nomic-embed-text` and `DATA_DIR=/data`.
- **FR-007**: Compose MUST pull `llama3.1` and `nomic-embed-text` before the API starts.
- **FR-008**: `gitops/clusters/myhealth/sync.yaml` MUST define the public `GitRepository` `flux-system` on `main` with no secret, and the `Kustomization` `flux-system` for `./gitops/clusters/myhealth`. `ks.yaml` MUST define `apps` for `./gitops/apps/overlays/myhealth` with `prune: true` and `wait: false`. No `gotk-components.yaml` is committed.
- **FR-009**: Namespace `myhealth` MUST enforce pod security `baseline`, and audit and warn at `restricted`.
- **FR-010**: Each component `ks.yaml` MUST be a Flux `Kustomization` with `prune: true`, `wait: true` and `sourceRef.name: flux-system`. `web` depends on `api`. `api` depends on `qdrant`, and on homelab also on `ollama`.
- **FR-011**: The API manifest MUST mount the PersistentVolumeClaim `health-data` at `/data` and set the same environment keys as Compose, with cluster URLs.
- **FR-012**: NetworkPolicies MUST allow `web` → `api`. On Minikube, `api` → `qdrant` and the host Ollama. On homelab, `api` → `qdrant` and in-cluster `ollama`, and not the host.
- **FR-013**: Qdrant MUST be a `HelmRelease` of chart `qdrant` from `https://qdrant.github.io/qdrant-helm`, one replica, with a pinned version.
- **FR-014**: The Minikube overlay MUST list `api`, `web` and `qdrant` and MUST NOT list `ollama`. The homelab overlay MUST add chart `ollama` from `https://otwld.github.io/ollama-helm`, pinned, with no model baked into an image we build.
- **FR-015**: An offline test in `make check` MUST read `compose.yaml` and `gitops/` as text and check FR-006, FR-008, FR-010 and FR-014. It opens no socket and starts no daemon.
- **FR-016**: No route, status code or JSON field may differ from the app-shell contract.

### Key Entities

- **Image**: `myhealth-api:local` or `myhealth-web:local`. They are built locally and loaded into Minikube, never pulled.
- **Component**: one Flux `Kustomization` plus its `app/` directory (`api`, `web`, `qdrant`, `ollama`).
- **Overlay**: a list of components for one cluster (`myhealth` Minikube or `homelab`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Compose starts `web`, `api`, `qdrant` and `ollama`, and the API container has `PROFILE=local` and the five settings.
- **SC-002**: Flux on Minikube profile `myhealth` reconciles `./gitops/apps/overlays/myhealth`, running both images and Qdrant with no Ollama workload, and `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1`.
- **SC-003**: `./gitops/apps/overlays/homelab` adds the Ollama release as its own `Kustomization`, and its API uses `http://ollama.myhealth.svc.cluster.local:11434/v1`.
- **SC-004**: The page at `127.0.0.1:8080` can upload the fixture PDF and shows it cited on page 1.
- **SC-005**: `make check` passes with no Docker daemon and without the local group.
- **SC-006**: No route or JSON field differs from the app-shell contract.

## Assumptions

- Documents stay on this machine (Constitution I). No hosted parser, model or vector store.
- The daily edit loop is unchanged: stub API on `127.0.0.1:8000` and Vite on `127.0.0.1:5173`. Compose publishes the page on `8080`, so both can run at the same time.
- The cluster tree mirrors `gitops/apps/base/ai-system` in the homelab repo: one directory per component, a `ks.yaml` beside `app/`, a base, and one overlay per cluster.
- Model names are not secrets.

## Out of Scope

- Ollama inside the Minikube profile.
- A registry, image automation, TLS, auth, more than one replica, and GPU scheduling.
- Pointing the existing homelab Flux at this repo.
- Streaming, speech and stored chat history.
