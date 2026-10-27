# Spec: local-runtime

Run the local profile in Docker Compose, and run the same images in a Minikube profile. This is the `local-runtime` module in [capability-map.md](capability-map.md). The HTTP contract stays the one in [SPEC-app-shell.md](SPEC-app-shell.md). This module does not add a route or a field.

The edit loop stays on the host. `make dev` with `PROFILE` unset, and `npm run dev`, do not start Docker. Minikube is not that loop.

## Objective

The person can start Ollama, Qdrant, and the API together and open the built page. A PDF stays on this machine. A question is answered from the stored pages. The same API image and web image run under Compose and under Minikube.

User stories:

1. I run one Compose command. The page opens on this machine. I do not start Qdrant or Ollama by hand.
2. I upload a PDF. The bytes stay in `data/`. Chunks and vectors stay in Qdrant. Ollama embeds and answers. The page shows the answer and the citation.
3. I run the same images in a Minikube profile named `myhealth`. Flux reconciles them from Git. Ollama stays on the host. The API reaches it at `host.minikube.internal:11434`.
4. The same Git tree has a homelab overlay. There, Ollama is its own workload, the way `gitops/apps/base/ai-system/ollama` is its own Flux `Kustomization`. The API does not embed an Ollama chart.
5. `make check` still passes with no Docker daemon and without the local dependency group.

Assumptions that bind this spec:

1. Documents stay on this machine. The stack has no hosted parser, no hosted model, and no hosted vector service.
2. Compose runs three services the person does not already have: `qdrant`, `ollama`, and `api`. A fourth service, `web`, serves the built page. The browser talks only to `web`.
3. The cluster does not take a Deployment from `kubectl apply`. Flux reconciles Git. The first Minikube install applies `sync.yaml` once so Flux can watch this repo. The tree matches the shape of `gitops/apps/base/ai-system`: one directory per component, a `ks.yaml` Flux `Kustomization` beside an `app/` directory, a base, and an overlay per cluster. The namespace is `myhealth`.
4. The Minikube overlay does not run an Ollama container. Model files and the GPU stay on the host. The homelab overlay does run Ollama, as its own Helm release, because that cluster already runs models that way. The overlays differ in that component, in the API `dependsOn` list, in `OLLAMA_BASE_URL`, and in the API egress rule.
5. The API process inside the image uses `PROFILE=local` and the settings names already in [SPEC-app-shell.md](SPEC-app-shell.md). Chat model `llama3.1`. Embedding model `nomic-embed-text`, 768 dimensions. `OLLAMA_BASE_URL` includes the `/v1` prefix because the client posts to `{base}/chat/completions`.
6. The daily edit loop is unchanged: stub API on `127.0.0.1:8000`, Vite on `127.0.0.1:5173`. Compose publishes the page on `127.0.0.1:8080` so the two can run at the same time. Compose is not Flux.
7. Today's process raises `local adapters are required` for `PROFILE=local` unless factories are injected. This module wires those factories when the local group is installed. It does not change route paths or JSON fields.
8. The fixture sentence remains `DemoMarker value is 10 units.`

## Tech stack

No new application library.

- Docker Compose v2. The file is `compose.yaml` at the repo root. This is the local stack, not the cluster.
- Flux. `GitRepository` is `source.toolkit.fluxcd.io/v1`. The app sync is a `Kustomization` of `kustomize.toolkit.fluxcd.io/v1`. A third-party chart uses `HelmRelease` of `helm.toolkit.fluxcd.io/v2`. The source name is `flux-system`.
- Minikube. Profile name `myhealth`. Flux is installed with `flux install`. This repo does not commit a `gotk-components.yaml`.
- The API image is built from `src/backend`. It installs the locked environment with the `local` group (`docling`, `qdrant-client`). It does not install the dev group.
- The web image is built from `src/frontend` (`npm run build`) and serves that build. It proxies `/documents`, `/chat`, and `/health` to `api:8000`. No new npm dependency.
- Qdrant and Ollama use their upstream images. Pin each tag in Compose and in the manifest. Do not use `latest`.
- Image names built here: `myhealth-api:local` and `myhealth-web:local`. Minikube loads those names. It does not pull them from a registry.

## Commands

The edit loop, from the host, is unchanged:

```sh
cd src/backend && uv sync && make dev
cd src/frontend && npm run dev
```

`make check` from `src/backend` is unchanged: ruff, ruff format, pyright, and pytest. It does not start Docker, Compose, or Minikube, and it does not install the local group.

The live check is Compose. It is not part of `make check` and it is not a GitHub Actions job.

```sh
docker compose up --build
```

Published on the host, bound to `127.0.0.1` only:

| Service | Host port | Container |
| --- | --- | --- |
| web | 8080 | serves the built page |
| api | 8000 | FastAPI, `0.0.0.0` inside the network |
| qdrant | 6333 | Qdrant |
| ollama | 11434 | Ollama |

Open `http://127.0.0.1:8080`. The first start pulls `llama3.1` and `nomic-embed-text` into the Ollama volume.

Stop and remove the containers with `docker compose down`. Named volumes `qdrant-data` and `ollama-models` stay until `docker compose down -v`. The API files are a bind mount of `./data`, so that flag does not delete them.

The Minikube check is separate. It is not part of `make check`.

```sh
minikube start -p myhealth
minikube image load myhealth-api:local -p myhealth
minikube image load myhealth-web:local -p myhealth
flux install --context myhealth
kubectl --context myhealth apply -f gitops/clusters/myhealth/sync.yaml
flux reconcile kustomization flux-system --context myhealth --with-source
flux reconcile kustomization apps --context myhealth --with-source
minikube service web -n myhealth -p myhealth --url
```

`flux install` installs the controllers. It does not watch Git. `sync.yaml` is applied once. It holds the `GitRepository` named `flux-system` (public HTTPS URL of this repo, branch `main`, no deploy key) and the `Kustomization` named `flux-system` whose path is `./gitops/clusters/myhealth`. That directory then applies `ks.yaml`. `ks.yaml` is the `Kustomization` named `apps`. Its path is `./gitops/apps/overlays/myhealth`. After that first apply, a push to `main` is how the profile changes. The check does not `kubectl apply` a Deployment, a Service, or a Helm release.

The host process `ollama serve` is already running and has pulled the same two models. The API's `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1`.

## Project structure

```text
compose.yaml
src/backend/Dockerfile                 # myhealth-api
src/frontend/Dockerfile                # myhealth-web
gitops/clusters/myhealth/
  kustomization.yaml                   # lists sync.yaml and ks.yaml
  sync.yaml                            # GitRepository flux-system + Kustomization flux-system
  ks.yaml                              # Kustomization apps -> overlays/myhealth
gitops/apps/base/myhealth/
  namespace.yaml                       # name myhealth, pod-security enforce baseline
  kustomization.yaml                   # namespace only
  api/ks.yaml                          # Flux Kustomization, path api/app
  api/app/                             # Deployment, Service, NetworkPolicy
  web/ks.yaml
  web/app/
  qdrant/ks.yaml
  qdrant/app/                          # HelmRelease, chart qdrant
  ollama/ks.yaml                       # homelab overlay only
  ollama/app/                          # HelmRelease, chart ollama, no model baked in
gitops/apps/overlays/myhealth/         # base plus api, web, qdrant; not ollama
gitops/apps/overlays/homelab/          # those plus ollama
```

The namespace labels match the `ai-system` namespace: `pod-security.kubernetes.io/enforce: baseline`, and `audit` and `warn` set to `restricted`. The base kustomization lists the namespace only. Each component `ks.yaml` is applied by the overlay, the same way `gitops/apps/overlays/homelab` lists `ai-system/ollama/ks.yaml`.

Each component `ks.yaml` sets `prune: true`, `wait: true`, and `sourceRef` to the `GitRepository` named `flux-system`. The root `apps` kustomization sets `wait: false`. `web` depends on `api`. `api` depends on `qdrant`. The homelab `api` also depends on `ollama`.

Qdrant is a `HelmRelease` of chart `qdrant` from `https://qdrant.github.io/qdrant-helm`, one replica, version pinned in the release. The homelab Ollama release is chart `ollama` from `https://otwld.github.io/ollama-helm`, the chart `ai-system` uses, version pinned in the release. Neither chart version floats.

`data/` stays gitignored. Compose bind-mounts `./data` at `DATA_DIR=/data`. The cluster mounts a PersistentVolumeClaim named `health-data` at `/data`. That claim is not a host path, and it is not the Compose bind mount. Qdrant and Ollama in Compose use named volumes. Nothing in those volumes is committed.

A NetworkPolicy allows `web` to call `api`. On the Minikube overlay, `api` may call `qdrant` and the host Ollama address. On the homelab overlay, `api` may call `qdrant` and the in-cluster `ollama` Service, and it may not call the host.

The web server proxies:

```text
/documents  ->  http://api:8000
/chat       ->  http://api:8000
/health     ->  http://api:8000
```

The page keeps the relative URLs it already uses. The browser does not call Qdrant or Ollama.

## Code style

Compose and the manifest set the environment. Python keeps the names in `Settings`.

```yaml
services:
  api:
    image: myhealth-api:local
    environment:
      PROFILE: local
      QDRANT_URL: http://qdrant:6333
      OLLAMA_BASE_URL: http://ollama:11434/v1
      OLLAMA_CHAT_MODEL: llama3.1
      OLLAMA_EMBED_MODEL: nomic-embed-text
      DATA_DIR: /data
```

The Minikube overlay uses the same keys. `QDRANT_URL` is `http://qdrant.myhealth.svc.cluster.local:6333`. `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1`. The homelab overlay sets `OLLAMA_BASE_URL` to `http://ollama.myhealth.svc.cluster.local:11434/v1`. `DATA_DIR` is the `health-data` claim mounted at `/data`. The API and web Deployments set `imagePullPolicy: IfNotPresent` on `myhealth-api:local` and `myhealth-web:local`. They are not Helm charts. Qdrant and the homelab Ollama are.

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: api
  namespace: flux-system
spec:
  interval: 10m
  path: ./gitops/apps/base/myhealth/api/app
  prune: true
  wait: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  dependsOn:
    - name: qdrant
```

Inside the API image the process listens on `0.0.0.0:8000` so `web` and `qdrant` can reach it. The host publish is `127.0.0.1`. The command is `fastapi run`, not `fastapi dev`.

When `PROFILE=local` and the local group is installed, the process builds the Docling parser, the Qdrant corpus, and the Ollama chat model from those settings and passes them into `create_app`. A missing setting still fails in the `Settings` validator. A missing `docling` or `qdrant_client` still fails with the existing local-group message. The stub path still does not import those modules.

## Testing strategy

`make check` is the gate for every commit. It does not start the live stack.

One unit test reads `compose.yaml` and `gitops/` as text. It asserts the API environment names and values above, including `PROFILE=local`. It asserts `overlays/myhealth` does not list `ollama/ks.yaml`, and `overlays/homelab` does. It asserts each component `ks.yaml` is a Flux `Kustomization` with `prune: true` and `sourceRef.name: flux-system`. It asserts `sync.yaml` names the `GitRepository` `flux-system` and contains no secret. The test does not open a socket and does not start a daemon.

The live check is manual, after that test passes. It is not part of `make check`.

Compose:

1. `docker compose up --build`
2. Open `http://127.0.0.1:8080`. `GET /health` on `127.0.0.1:8000` returns the existing health JSON.
3. Upload a one-page PDF whose text is `DemoMarker value is 10 units.`
4. Ask `What is the DemoMarker value?`
5. The page shows that sentence, the file name, and page 1.
6. The PDF bytes are under `data/` on the host. They are not in the image.

Minikube, with the same images loaded, Flux installed, and Ollama on the host:

1. `flux reconcile kustomization apps --with-source` finishes ready for `api`, `web`, and `qdrant`.
2. Open the `web` service URL from `minikube service`.
3. Repeat the upload and the question.
4. The API log shows the Ollama host as `host.minikube.internal`. The profile has no Ollama workload.

The homelab overlay is not applied to a shared cluster from this check. Pointing that cluster at `./gitops/apps/overlays/homelab` waits until the spec is approved and someone asks for that cluster.

## Boundaries

Always:

- Pass `PROFILE=local` and the five settings into the API container.
- Keep the HTTP paths and JSON fields from [SPEC-app-shell.md](SPEC-app-shell.md).
- Bind published ports to `127.0.0.1`.
- Keep Ollama on the host for the Minikube overlay.
- Change the Minikube profile by pushing Git and letting Flux reconcile. Do not `kubectl apply` the app.
- Use `myhealth-api:local` and `myhealth-web:local` with `imagePullPolicy: IfNotPresent` in Compose, Minikube, and the homelab overlay until a registry exists.
- Run `make check` before a commit. That command must not need a Docker daemon.

Ask first:

- Moving Ollama into the Minikube cluster. The homelab overlay already runs it there.
- Pointing the existing homelab Flux at this repo.
- A different chat or embedding model.
- Publishing the images to a registry.
- A port bound to `0.0.0.0`.
- A new Python or npm dependency beyond the local group the app-shell spec already names.

Never:

- Change a route, a status code, or a JSON field.
- Run Compose, Minikube, or `uv sync --group local` from `make check` or from GitHub Actions.
- Commit `data/`, a model weight, a secret, or `.venv`. A password does not go in a plain manifest. If a secret is required later, it is a SOPS file plus an example file, and the Flux `Kustomization` decrypts it. This module's model names are not secrets.
- Put a real health record, or a realistic patient narrative, in a fixture or a compose file. `DemoMarker value is 10 units.` is the fixture sentence.
- Send a PDF or a chunk to any host other than the configured Ollama and Qdrant URLs.
- Bake a PDF or a model weight into an image.

## Success criteria

1. `docs/SPEC-local-runtime.md` is this file, and [capability-map.md](capability-map.md) links it.
2. Compose starts `web`, `api`, `qdrant`, and `ollama`. The API container has `PROFILE=local` and the five settings in the code style section.
3. Flux on the Minikube profile `myhealth` reconciles `./gitops/apps/overlays/myhealth`. That overlay runs `myhealth-api:local`, `myhealth-web:local`, and the same Qdrant chart. It has no Ollama workload. `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1`.
4. `./gitops/apps/overlays/homelab` adds the Ollama Helm release as its own Flux `Kustomization`. Its API uses `http://ollama.myhealth.svc.cluster.local:11434/v1`. The overlay still names `myhealth-api:local` and `myhealth-web:local`. Applying it to a shared cluster is a separate ask, and that cluster needs those images present.
5. The page at `127.0.0.1:8080` can upload the fixture PDF and shows it cited on page 1.
6. `make check` passes with no Docker daemon and without the local group. The text check of the compose file and `gitops/` does not start a daemon.
7. No route or JSON field differs from the app-shell contract.

## Open questions

None. The choices in the assumptions section are the contract for implementation.

## Explicitly later

- Ollama as a container inside the Minikube profile. The homelab overlay is the in-cluster Ollama.
- A registry, image automation, TLS, auth, and more than one replica.
- GPU scheduling.
- Streaming, speech, and stored chat history.
