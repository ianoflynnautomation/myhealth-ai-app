# Spec: local-runtime

Run the local profile in Docker Compose, and run the same images in a Minikube profile. This is the `local-runtime` module in [capability-map.md](capability-map.md). The HTTP contract stays the one in [SPEC-app-shell.md](SPEC-app-shell.md). This module does not add a route or a field.

The edit loop stays on the host. `make dev` with `PROFILE` unset, and `npm run dev`, do not start Docker. Minikube is not that loop.

## Objective

The person can start Ollama, Qdrant, and the API together and open the built page. A PDF stays on this machine. A question is answered from the stored pages. The same API image and web image run under Compose and under Minikube.

User stories:

1. I run one Compose command. The page opens on this machine. I do not start Qdrant or Ollama by hand.
2. I upload a PDF. The bytes stay in `data/`. Chunks and vectors stay in Qdrant. Ollama embeds and answers. The page shows the answer and the citation.
3. I run the same images in a Minikube profile named `myhealth`. Ollama stays on the host. The API reaches it at `host.minikube.internal:11434`.
4. `make check` still passes with no Docker daemon and without the local dependency group.

Assumptions that bind this spec:

1. Documents stay on this machine. The stack has no hosted parser, no hosted model, and no hosted vector service.
2. Compose runs three services the person does not already have: `qdrant`, `ollama`, and `api`. A fourth service, `web`, serves the built page. The browser talks only to `web`.
3. Minikube runs the `api`, `qdrant`, and `web` images from Compose. It does not run an Ollama container. Model files and the GPU stay on the host. That is why Ollama is not moved into the cluster.
4. The API process inside the image uses `PROFILE=local` and the settings names already in [SPEC-app-shell.md](SPEC-app-shell.md). Chat model `llama3.1`. Embedding model `nomic-embed-text`, 768 dimensions. `OLLAMA_BASE_URL` includes the `/v1` prefix because the client posts to `{base}/chat/completions`.
5. The daily edit loop is unchanged: stub API on `127.0.0.1:8000`, Vite on `127.0.0.1:5173`. Compose publishes the page on `127.0.0.1:8080` so the two can run at the same time.
6. Today's process raises `local adapters are required` for `PROFILE=local` unless factories are injected. This module wires those factories when the local group is installed. It does not change route paths or JSON fields.
7. The fixture sentence remains `DemoMarker value is 10 units.`

## Tech stack

No new application library.

- Docker Compose v2. The file is `compose.yaml` at the repo root.
- Minikube. Profile name `myhealth`. Manifests under `deploy/minikube/`.
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

Stop and remove the containers with `docker compose down`. Volumes `health-data`, `qdrant-data`, and `ollama-models` stay until `docker compose down -v`.

The Minikube check is separate. It is not part of `make check`.

```sh
minikube start -p myhealth
minikube image load myhealth-api:local -p myhealth
minikube image load myhealth-web:local -p myhealth
kubectl --context myhealth apply -f deploy/minikube/
minikube service web -p myhealth --url
```

The host process `ollama serve` is already running and has pulled the same two models. The API's `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1`.

## Project structure

```text
compose.yaml
src/backend/Dockerfile          # myhealth-api
src/frontend/Dockerfile         # myhealth-web
deploy/minikube/                # same image names, no Ollama workload
```

`data/` stays gitignored. The API bind-mounts it at `DATA_DIR=/data`. Qdrant and Ollama use named volumes. Nothing in those volumes is committed.

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

The Minikube manifest uses the same keys. `QDRANT_URL` is the in-cluster Qdrant service. `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1`. `DATA_DIR` is a volume mounted at `/data`.

Inside the API image the process listens on `0.0.0.0:8000` so `web` and `qdrant` can reach it. The host publish is `127.0.0.1`. The command is `fastapi run`, not `fastapi dev`.

When `PROFILE=local` and the local group is installed, the process builds the Docling parser, the Qdrant corpus, and the Ollama chat model from those settings and passes them into `create_app`. A missing setting still fails in the `Settings` validator. A missing `docling` or `qdrant_client` still fails with the existing local-group message. The stub path still does not import those modules.

## Testing strategy

`make check` is the gate for every commit. It does not start the live stack.

One unit test reads `compose.yaml` and `deploy/minikube/` as text. It asserts the API environment names and values above, including `PROFILE=local`, and it asserts the Minikube manifests contain no Ollama workload. The test does not open a socket and does not start a daemon.

The live check is manual, after that test passes. It is not part of `make check`.

Compose:

1. `docker compose up --build`
2. Open `http://127.0.0.1:8080`. `GET /health` on `127.0.0.1:8000` returns the existing health JSON.
3. Upload a one-page PDF whose text is `DemoMarker value is 10 units.`
4. Ask `What is the DemoMarker value?`
5. The page shows that sentence, the file name, and page 1.
6. The PDF bytes are under `data/` on the host. They are not in the image.

Minikube, with the same images loaded and with Ollama on the host:

1. Open the `web` service URL from `minikube service`.
2. Repeat steps 3 through 5.
3. The API log shows the Ollama host as `host.minikube.internal`, not an in-cluster Ollama service.

## Boundaries

Always:

- Pass `PROFILE=local` and the five settings into the API container.
- Keep the HTTP paths and JSON fields from [SPEC-app-shell.md](SPEC-app-shell.md).
- Bind published ports to `127.0.0.1`.
- Keep Ollama on the host for Minikube.
- Use `myhealth-api:local` and `myhealth-web:local` in both Compose and Minikube.
- Run `make check` before a commit. That command must not need a Docker daemon.

Ask first:

- Moving Ollama into the Minikube cluster.
- A different chat or embedding model.
- Publishing the images to a registry.
- A port bound to `0.0.0.0`.
- A new Python or npm dependency beyond the local group the app-shell spec already names.

Never:

- Change a route, a status code, or a JSON field.
- Run Compose, Minikube, or `uv sync --group local` from `make check` or from GitHub Actions.
- Commit `data/`, a model weight, a secret, or `.venv`.
- Put a real health record, or a realistic patient narrative, in a fixture or a compose file. `DemoMarker value is 10 units.` is the fixture sentence.
- Send a PDF or a chunk to any host other than the configured Ollama and Qdrant URLs.
- Bake a PDF or a model weight into an image.

## Success criteria

1. `docs/SPEC-local-runtime.md` is this file, and [capability-map.md](capability-map.md) links it.
2. Compose starts `web`, `api`, `qdrant`, and `ollama`. The API container has `PROFILE=local` and the five settings in the code style section.
3. The Minikube profile `myhealth` runs `myhealth-api:local`, `myhealth-web:local`, and the same Qdrant image tag. Ollama is not a workload in that profile. `OLLAMA_BASE_URL` is `http://host.minikube.internal:11434/v1`.
4. The page at `127.0.0.1:8080` can upload the fixture PDF and shows it cited on page 1.
5. `make check` passes with no Docker daemon and without the local group. The text check of the compose file and the manifest does not start a daemon.
6. No route or JSON field differs from the app-shell contract.

## Open questions

None. The choices in the assumptions section are the contract for implementation.

## Explicitly later

- Ollama as a container inside Minikube.
- A registry, TLS, auth, and more than one replica.
- GPU scheduling.
- Streaming, speech, and stored chat history.
