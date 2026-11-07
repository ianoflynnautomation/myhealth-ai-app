# Implementation Plan: local-runtime

**Branch**: `003-local-runtime` | **Date**: 2026-10-27 (migrated to spec-kit 2026-11-07) | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-local-runtime/spec.md`

## Summary

Wire the local profile from settings, build two images, run them with Qdrant and Ollama in Compose, then describe the same images as a Flux GitOps tree with a Minikube overlay (Ollama on the host) and a homelab overlay (Ollama in the cluster). An offline text test keeps `compose.yaml` and `gitops/` honest inside `make check`. Live runs stay manual.

## Technical Context

**Language/Version**: Python 3.13 for the wiring and tests. YAML for Compose, Kustomize and Flux.

**Primary Dependencies**: no new application library. Docker Compose v2. Flux (`source.toolkit.fluxcd.io/v1`, `kustomize.toolkit.fluxcd.io/v1`, `helm.toolkit.fluxcd.io/v2`). Minikube. nginx for the web image. Upstream Qdrant and Ollama images and charts, all pinned.

**Storage**: Compose bind-mounts `./data` at `/data` and uses named volumes `qdrant-data` and `ollama-models`. The cluster uses the PersistentVolumeClaim `health-data`.

**Testing**: pytest unit tests that read files as text: tests/test_api_image.py, test_web_image.py, test_compose.py and test_gitops.py. They don't need Docker.

**Target Platform**: macOS or Linux with Docker. Minikube profile `myhealth` with the Calico CNI. Optionally the homelab cluster.

**Project Type**: deployment and runtime configuration for the web app.

**Constraints**: Constitution V, so no Docker in `make check` or CI. Ports bind to `127.0.0.1`. Images are `IfNotPresent`. Upstream tags and charts are pinned, never `latest`.

## Constitution Check

| Principle | Status | How |
| --- | --- | --- |
| I. Health records stay local | Pass | Only local Ollama and Qdrant. `127.0.0.1` binds. `./data` is a gitignored bind mount and nothing is baked into an image. `sync.yaml` has no secret. |
| II. Grounded, cited answers | Pass | Unchanged from app-shell. The route still cites `hits[:1]`. |
| III. One HTTP contract | Pass | No route or field changes (FR-016). The web proxy forwards the three existing paths. |
| IV. Test-first thin slices | Pass | LR-02 to LR-18, one named test each. |
| V. Offline quality gates | Pass | The manifest tests are text-only. Compose and Minikube checks are manual. |
| VI. Modules, ports, simplicity | Pass | It reuses the app-shell ports. The local corpus is a new adapter, not a new port. |

## Project Structure

```text
specs/003-local-runtime/
├── spec.md
├── plan.md
└── tasks.md

compose.yaml
src/backend/Dockerfile                 # myhealth-api
src/frontend/Dockerfile                # myhealth-web
src/frontend/nginx.conf
gitops/clusters/myhealth/
  kustomization.yaml  sync.yaml  ks.yaml
gitops/apps/base/myhealth/
  namespace.yaml  kustomization.yaml   # namespace only
  api/ks.yaml     api/app/             # Deployment (no OLLAMA_BASE_URL), Service, PVC, NetworkPolicy (qdrant + DNS)
  web/ks.yaml     web/app/
  qdrant/ks.yaml  qdrant/app/          # HelmRepository + HelmRelease
  ollama/ks.yaml  ollama/app/          # homelab only: HelmRepository + HelmRelease
gitops/apps/overlays/myhealth/         # api, web, qdrant + api-patch.yaml (host Ollama)
gitops/apps/overlays/homelab/          # those plus ollama + api-patch.yaml (in-cluster Ollama)
```

**Structure Decision**: the GitOps tree follows the homelab repo's `ai-system` shape, so the homelab cluster can adopt it later without a restructure.

## Architecture Decisions

- The original PDF bytes are kept by `DirectoryPdfStore` (`documents/pdf_store.py`) as `DATA_DIR/<id>.pdf`. Only the local profile builds one, so the stub still writes nothing.
- Qdrant point ids are the UUIDv5 of `{documentId}:{pageNumber}` (`qdrant_index.py`). The readable id travels in the payload as `pointId`.
- `QdrantCorpus` stays an upsert helper. A new `local_corpus.py` implements the `StoredCorpus` protocol the routes call. It calls `add` synchronously and returns `(StoredDocument, created)`, and it uses a sync httpx client, because `asyncio.run` inside the async route would fail.
- The hybrid query body is a pure function in `qdrant_query.py`, so `make check` never imports `qdrant_client`.
- `OLLAMA_BASE_URL` includes `/v1`, because the client posts to `{base}/chat/completions`.
- `flux install` installs the controllers but doesn't watch Git. `sync.yaml` is applied once, and after that a push to `main` is the only way to change the profile.
- The overlays differ in four places: the Ollama component, the API `dependsOn` list, `OLLAMA_BASE_URL`, and the API egress rule. The last three are one patch per overlay on the Flux `Kustomization` named `api`. The patch adds `spec.patches` (a Deployment env patch and a NetworkPolicy egress patch) and, on homelab, `spec.dependsOn`. A plain Kustomize patch can't reach the Deployment, because the overlay renders only Flux objects.
- NetworkPolicy egress always allows DNS to `kube-dns`. The host Ollama is an `ipBlock` `/32`, because policies can't match a name. The Minikube CIDR is committed in the overlay and checked during the Minikube check (see below).
- Minikube starts with `--cni=calico`. Its default CNI ignores NetworkPolicy, and then FR-012 would hold only on paper.

## Environment

| Key | Compose | Minikube | Homelab |
| --- | --- | --- | --- |
| `PROFILE` | `local` | `local` | `local` |
| `QDRANT_URL` | `http://qdrant:6333` | `http://qdrant.myhealth.svc.cluster.local:6333` | same as Minikube |
| `OLLAMA_BASE_URL` | `http://ollama:11434/v1` | `http://host.minikube.internal:11434/v1` | `http://ollama.myhealth.svc.cluster.local:11434/v1` |
| `OLLAMA_CHAT_MODEL` | `llama3.1` | `llama3.1` | `llama3.1` |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | `nomic-embed-text` | `nomic-embed-text` |
| `DATA_DIR` | `/data` (bind `./data`) | `/data` (PVC `health-data`) | `/data` (PVC `health-data`) |

## Manual Checks

These are not part of `make check` or GitHub Actions.

**Compose**

1. `docker compose up --build`
2. Open `http://127.0.0.1:8080`. `GET http://127.0.0.1:8000/health` returns the health JSON.
3. Upload the one-page fixture PDF (`DemoMarker value is 10 units.`).
4. Ask `What is the DemoMarker value?`
5. The page shows the sentence, the file name and page 1.
6. The PDF bytes are under `data/` on the host.

**Minikube** (not set up on this machine yet)

Prerequisites, done once: install `minikube`, `kubectl` and the `flux` CLI (`brew install minikube kubectl fluxcd/tap/flux`). Run `ollama serve` on the host and pull `llama3.1` and `nomic-embed-text`. Merge the GitOps tree to `main`, because Flux reads `main` from GitHub.

```sh
docker compose build                     # builds myhealth-api:local and myhealth-web:local
minikube start -p myhealth --cni=calico
minikube ssh -p myhealth -- getent hosts host.minikube.internal   # must match the ipBlock in overlays/myhealth/api-patch.yaml
minikube image load myhealth-api:local -p myhealth
minikube image load myhealth-web:local -p myhealth
flux install --context myhealth
kubectl --context myhealth apply -f gitops/clusters/myhealth/sync.yaml
flux reconcile kustomization flux-system --context myhealth --with-source
flux reconcile kustomization apps --context myhealth --with-source
minikube service web -n myhealth -p myhealth --url
```

Then repeat the upload and the question. The API log shows the Ollama host as `host.minikube.internal`. If `getent` printed a different address from the committed `/32`, change the overlay in a commit and push it. Don't patch the cluster by hand.

The homelab overlay is not applied from this check.

## Delivery (pull requests)

| PR | Branch | Tasks |
| --- | --- | --- |
| 1 | `docs/local-runtime-spec` | LR-01 |
| 2 | `feature/local-boot` | LR-02–LR-07 |
| 3 | `feature/compose-stack` | LR-08–LR-11, LR-19, LR-20 |
| 4 | `feature/gitops-minikube` | LR-12–LR-17, LR-21 |
| 5 | `feature/gitops-homelab` | LR-18 |

## Boundaries

- **Ask first**: moving Ollama into Minikube; pointing the homelab Flux at this repo; a different model; publishing images to a registry; a port on `0.0.0.0`; any dependency beyond the app-shell local group.
- **Never**: change a route, status or field; run Compose, Minikube or `uv sync --group local` from `make check` or CI; commit a secret in a plain manifest (use SOPS); bake a PDF or model weight into an image.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Installing Docling in `make check` or CI | Slow gate that imports native libraries | LR-02 test rejects `--group local` in the Makefile and workflows |
| A NetworkPolicy that only allows in-cluster Ollama | Minikube can't reach the host model | The Minikube patch allows the host `/32`. The homelab patch doesn't |
| Default Minikube CNI ignores NetworkPolicy | Policies untested | `--cni=calico` |
| Egress policy without DNS | Every lookup fails, including Qdrant | Base policy allows `kube-dns` on 53 |
| The host address depends on the Minikube driver | Host Ollama blocked | `getent` step in the Minikube check |
| `myhealth-api:local` on a cluster that can't load it | CrashLoop on homelab | LR-18 writes the overlay but does not apply it |
| A guessed Qdrant hybrid query shape | Page not retrieved | LR-05 was checked against the Qdrant docs, and its test asserts both the text and the vector |

## Complexity Tracking

No violations.
