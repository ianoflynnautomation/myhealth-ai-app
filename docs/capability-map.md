# Capability map

The app parses medical PDFs, stores the text, and answers questions from that store. Module ids stay as they are written here. Specs are one module at a time, in build order.

| Module id | Responsibility | Depends on |
| --- | --- | --- |
| app-shell | The pipeline. Upload a PDF, parse it, store the file and the page chunks, answer a question with citations. Stub profile and local profile. | — |
| chat-ui | Connect the existing React page to upload and chat. Show the answer and the citations. | app-shell |
| local-runtime | Compose for Ollama and Qdrant, plus the API. Minikube profile using the same images. Ollama on the host at `host.minikube.internal:11434` unless the model later lives in the cluster. | app-shell |

Build order: app-shell → chat-ui and local-runtime.

`chat-ui` and `local-runtime` can be specified in parallel after app-shell. They do not call each other.

Parser, corpus, and chat model are ports inside app-shell. Later modules do not re-define them.

| Module id | Spec |
| --- | --- |
| app-shell | [SPEC-app-shell.md](SPEC-app-shell.md) |
| chat-ui | [SPEC-chat-ui.md](SPEC-chat-ui.md) |
| local-runtime | Not written yet |
