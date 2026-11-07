# Capability map

The app parses medical PDFs, stores the text, and answers questions from that store. Module ids stay as they are written here. Each module is one spec-kit feature in `specs/NNN-<module id>/`, specified one at a time, in build order. The rules every module follows are in [.specify/memory/constitution.md](../.specify/memory/constitution.md).

| Module id | Responsibility | Depends on |
| --- | --- | --- |
| app-shell | The pipeline. Upload a PDF, parse it, store the file and the page chunks, answer a question with citations. Stub profile and local profile. | — |
| chat-ui | Connect the existing React page to upload and chat. Show the answer and the citations. | app-shell |
| local-runtime | Compose for Ollama and Qdrant, plus the API. The cluster is Flux GitOps under `gitops/`, one `Kustomization` per component. The Minikube overlay keeps Ollama on the host at `host.minikube.internal:11434`. The homelab overlay runs Ollama in the cluster as its own Helm release. | app-shell |

Build order: app-shell → chat-ui and local-runtime.

`chat-ui` and `local-runtime` can be specified in parallel after app-shell. They don't call each other.

`Parser`, `StoredCorpus` and `ChatModel` are ports inside app-shell. Later modules don't redefine them. The HTTP contract is [specs/001-app-shell/contracts/http.md](../specs/001-app-shell/contracts/http.md).

| Module id | Feature | Status |
| --- | --- | --- |
| app-shell | [specs/001-app-shell](../specs/001-app-shell/spec.md) | Implemented |
| chat-ui | [specs/002-chat-ui](../specs/002-chat-ui/spec.md) | Implemented. Manual check open |
| local-runtime | [specs/003-local-runtime](../specs/003-local-runtime/spec.md) | In progress |

A new module gets a row here first, then `/speckit-specify` creates the next `specs/NNN-<module id>/`.
