---
description: "Tasks for local-runtime, migrated from the LR section of tasks/todo.md"
---

# Tasks: local-runtime

**Input**: [spec.md](spec.md), [plan.md](plan.md), [contracts/http.md](../001-app-shell/contracts/http.md)

**Tests**: required. RED → GREEN → `cd src/backend && make check` for every task (Constitution IV). Manifest tests read files as text and never need Docker.

**Ids**: `T###` is the spec-kit order. The stable `LR-` id in parentheses is the one used in commits, and it is never renumbered. Paths are from the repo root.

## Phase 1: Setup

- [X] T001 Write and approve the local-runtime spec in specs/003-local-runtime/spec.md (LR-01, 2026-10-27; approval LR-CP1, 2026-10-27)

## Phase 2: User Story 2 - Local profile boots (P1, PR `feature/local-boot`)

- [X] T002 [US2] Declare the `local` dependency group and keep it out of `make check` in src/backend/pyproject.toml, tested by src/backend/tests/test_local_group.py::test_the_local_group_should_stay_out_of_make_check (LR-02, 2026-10-27)
- [X] T003 [US2] Build the Docling converter without importing it on the stub path in src/backend/src/health_api/documents/docling_factory.py, tested by src/backend/tests/test_docling_factory.py::test_the_docling_factory_should_not_import_docling (LR-03, 2026-10-27)
- [X] T004 [P] [US2] Embed a text with the Ollama embeddings route in src/backend/src/health_api/documents/ollama_embeddings.py, tested by src/backend/tests/test_ollama_embeddings.py::test_the_embed_client_should_post_the_text (LR-04, 2026-10-27)
- [X] T005 [P] [US2] Build the hybrid Qdrant query without importing the client in src/backend/src/health_api/documents/qdrant_query.py, tested by src/backend/tests/test_qdrant_query.py::test_the_hybrid_query_should_carry_the_text_and_the_vector (LR-05, 2026-10-27)
- [X] T006 [US2] Store and search pages through the corpus protocol in src/backend/src/health_api/documents/local_corpus.py, tested by src/backend/tests/test_local_corpus.py::test_the_local_corpus_should_return_the_stored_page (LR-06, 2026-10-27)
- [X] T007 [US2] Wire the local profile from settings in src/backend/src/health_api/main.py, tested by src/backend/tests/test_local_factory.py (LR-07, 2026-10-27)

**Checkpoint** (LR-CP2, 2026-10-27): `make check` passes without Docker or the local group. `POST /documents` and `POST /chat` are unchanged.

## Phase 3: User Story 1 - Compose stack (P1, PR `feature/compose-stack`)

- [X] T008 [US1] Build the API image with the local group in src/backend/Dockerfile, tested by src/backend/tests/test_api_image.py::test_the_api_image_should_install_the_local_group (LR-08, 2026-10-27)
- [X] T009 [P] [US1] Build the web image that proxies the API in src/frontend/Dockerfile and src/frontend/nginx.conf, tested by src/backend/tests/test_web_image.py::test_the_web_image_should_proxy_the_api (LR-09, 2026-10-27)
- [X] T010 [US1] Compose the four services on localhost in compose.yaml, tested by src/backend/tests/test_compose.py::test_compose_should_set_profile_local (LR-10, 2026-10-27)
- [X] T011 [US1] Pull both Ollama models before the API starts in compose.yaml, tested by src/backend/tests/test_compose.py (LR-11, 2026-10-27)
- [ ] T012 [US1] Merge `feature/compose-stack`, confirm `cd src/backend && make check` passes with no Docker daemon, and record the date here (LR-CP3)
- [ ] T013 [US2] Run the Compose manual check in specs/003-local-runtime/plan.md and record the date and result here (SC-001, SC-004)

## Phase 4: User Story 3 - GitOps on Minikube (P2, PR `feature/gitops-minikube`)

- [ ] T014 [US3] Watch this repo from the Minikube cluster: `GitRepository` and `Kustomization` `flux-system` with no secret, and `Kustomization` `apps` → `./gitops/apps/overlays/myhealth` with `prune: true` and `wait: false`, in gitops/clusters/myhealth/sync.yaml, gitops/clusters/myhealth/kustomization.yaml and gitops/clusters/myhealth/ks.yaml, tested by src/backend/tests/test_gitops.py::test_sync_should_watch_this_repo_without_a_secret (LR-12)
- [ ] T015 [US3] Add namespace `myhealth` enforcing `baseline` and auditing and warning at `restricted`, with a base kustomization that lists the namespace only, in gitops/apps/base/myhealth/namespace.yaml and gitops/apps/base/myhealth/kustomization.yaml, tested by src/backend/tests/test_gitops.py::test_the_namespace_should_enforce_baseline (LR-13)
- [ ] T016 [US3] Run the API in the cluster: Deployment `myhealth-api:local` with `IfNotPresent` and the Minikube environment, a Service, PVC `health-data` at `/data`, and a NetworkPolicy allowing Qdrant and the host Ollama, in gitops/apps/base/myhealth/api/ks.yaml, gitops/apps/base/myhealth/api/app/kustomization.yaml, gitops/apps/base/myhealth/api/app/api.yaml and gitops/apps/base/myhealth/api/app/networkpolicy.yaml, tested by src/backend/tests/test_gitops.py::test_the_minikube_api_should_keep_ollama_on_the_host (LR-14)
- [ ] T017 [US3] Run the web page in the cluster: Deployment `myhealth-web:local`, a Service, a NetworkPolicy web → api, and a `Kustomization` that depends on `api`, in gitops/apps/base/myhealth/web/ks.yaml, gitops/apps/base/myhealth/web/app/kustomization.yaml, gitops/apps/base/myhealth/web/app/web.yaml and gitops/apps/base/myhealth/web/app/networkpolicy.yaml, tested by src/backend/tests/test_gitops.py::test_the_web_kustomization_should_depend_on_api (LR-15)
- [ ] T018 [US3] Run Qdrant from its Helm chart, one replica, version pinned, with `api` depending on `qdrant`, in gitops/apps/base/myhealth/qdrant/ks.yaml, gitops/apps/base/myhealth/qdrant/app/kustomization.yaml, gitops/apps/base/myhealth/qdrant/app/helmrepository.yaml and gitops/apps/base/myhealth/qdrant/app/helmrelease.yaml, tested by src/backend/tests/test_gitops.py::test_qdrant_should_be_a_pinned_helm_release (LR-16)
- [ ] T019 [US3] Point the Minikube overlay at api, web and Qdrant and not Ollama in gitops/apps/overlays/myhealth/kustomization.yaml, tested by src/backend/tests/test_gitops.py::test_the_myhealth_overlay_should_omit_ollama (LR-17)

## Phase 5: User Story 4 - Homelab overlay (P3, PR `feature/gitops-homelab`)

- [ ] T020 [US4] Run Ollama on the homelab overlay: chart `ollama` from `https://otwld.github.io/ollama-helm`, pinned, pulling `llama3.1` and `nomic-embed-text`, and an API patch with the in-cluster `OLLAMA_BASE_URL`, `dependsOn: ollama` and no host egress, in gitops/apps/base/myhealth/ollama/ks.yaml, gitops/apps/base/myhealth/ollama/app/helmrelease.yaml, gitops/apps/overlays/homelab/kustomization.yaml and gitops/apps/overlays/homelab/api-patch.yaml, tested by src/backend/tests/test_gitops.py::test_the_homelab_overlay_should_run_ollama (LR-18)

## Phase 6: Verification

- [ ] T021 Confirm LR-12–LR-18 are merged and `cd src/backend && make check` passes without Docker, and record the date here (LR-CP4)
- [ ] T022 [US3] Run the Minikube manual check in specs/003-local-runtime/plan.md and record the date here. Do not apply the homelab overlay to a shared cluster (SC-002)

## Dependencies

- T002 → T003. T004 and T005 are independent files. T006 waits for T004 and T005. T007 waits for T003 and T006.
- T008 and T009 are independent. T010 waits for both. T011 waits for T010. T012 and T013 wait for T011.
- T014 → T015 → T016 → T017 → T018 → T019 → T020. The manifests for T017 and T018 are independent, but both tasks add a test to test_gitops.py, so they are not [P].
- T021 waits for T020. T022 waits for T019 and T013.
