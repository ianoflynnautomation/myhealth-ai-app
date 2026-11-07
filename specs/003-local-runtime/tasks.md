---
description: "Tasks for local-runtime, migrated from the LR section of tasks/todo.md"
---

# Tasks: local-runtime

**Input**: [spec.md](spec.md), [plan.md](plan.md), [contracts/http.md](../001-app-shell/contracts/http.md)

**Tests**: required. RED → GREEN → `cd src/backend && make check` for every task (Constitution IV). Manifest tests read files as text and never need Docker. A guard test for behavior that already exists proves its RED by failing against a temporarily broken file. The breakage is then reverted, and the task records that it was done.

**Ids**: `T###` is the spec-kit order. The stable `LR-` id in parentheses is the one used in commits, and it is never renumbered. T-numbers shifted on 2026-11-07 when LR-19 to LR-21 were added after `/speckit-analyze`. Paths are from the repo root.

## Phase 1: Setup

- [X] T001 Write and approve the local-runtime spec in specs/003-local-runtime/spec.md (LR-01, 2026-10-27; approval LR-CP1, 2026-10-27)

## Phase 2: User Story 2 - Local profile boots (P1, PR `feature/local-boot`)

- [X] T002 [US2] Declare the `local` dependency group and keep it out of `make check` in src/backend/pyproject.toml, tested by src/backend/tests/test_local_group.py::test_the_local_group_should_stay_out_of_make_check (LR-02, 2026-10-27)
- [X] T003 [US2] Build the Docling converter without importing it on the stub path in src/backend/src/health_api/documents/docling_factory.py, tested by src/backend/tests/test_docling_factory.py::test_the_docling_factory_should_not_import_docling (LR-03, 2026-10-27)
- [X] T004 [P] [US2] Embed a text with the Ollama embeddings route in src/backend/src/health_api/documents/ollama_embeddings.py, tested by src/backend/tests/test_ollama_embeddings.py::test_the_embed_client_should_post_the_text (LR-04, 2026-10-27)
- [X] T005 [P] [US2] Build the hybrid Qdrant query without importing the client in src/backend/src/health_api/documents/qdrant_query.py, tested by src/backend/tests/test_qdrant_query.py::test_the_hybrid_query_should_carry_the_text_and_the_vector (LR-05, 2026-10-27)
- [X] T006 [US2] Store and search pages through the corpus protocol in src/backend/src/health_api/documents/local_corpus.py, tested by src/backend/tests/test_local_corpus.py::test_the_local_corpus_should_return_the_stored_page (LR-06, 2026-10-27)
- [X] T007 [US2] Wire the local profile from settings in src/backend/src/health_api/main.py and the Qdrant adapter src/backend/src/health_api/documents/qdrant_index.py, tested by src/backend/tests/test_local_factory.py::test_the_local_profile_should_build_adapters_from_settings (LR-07, 2026-10-27)

**Checkpoint** (LR-CP2, 2026-10-27): `make check` passes without Docker or the local group. `POST /documents` and `POST /chat` are unchanged.

## Phase 3: User Story 1 - Compose stack (P1, PR `feature/compose-stack`)

- [X] T008 [US1] Build the API image with the local group in src/backend/Dockerfile, tested by src/backend/tests/test_api_image.py::test_the_api_image_should_install_the_local_group (LR-08, 2026-10-27)
- [X] T009 [P] [US1] Build the web image that proxies the API in src/frontend/Dockerfile and src/frontend/nginx.conf, tested by src/backend/tests/test_web_image.py::test_the_web_image_should_proxy_the_api (LR-09, 2026-10-27)
- [X] T010 [US1] Compose the four services on localhost in compose.yaml, tested by src/backend/tests/test_compose.py::test_compose_should_set_profile_local (LR-10, 2026-10-27)
- [X] T011 [US1] Pull both Ollama models before the API starts in compose.yaml, tested by src/backend/tests/test_compose.py::test_compose_should_pull_the_two_models (LR-11, 2026-10-27)
- [X] T012 [US2] Keep each uploaded PDF as `DATA_DIR/<id>.pdf` in the local profile, once per id, in src/backend/src/health_api/documents/pdf_store.py, src/backend/src/health_api/http/documents.py and src/backend/src/health_api/main.py, tested by src/backend/tests/test_local_factory.py::test_the_local_profile_should_keep_the_pdf_in_data_dir (LR-19, FR-017, 2026-11-07)
- [X] T013 [US1] Guard that every published Compose port binds `127.0.0.1`, not only the four expected ones (the volumes, `./data` and pinned tags were already covered by T010 and T011), in src/backend/tests/test_compose.py::test_compose_should_publish_on_localhost_only (LR-20, FR-005, 2026-11-07; RED shown by unbinding the qdrant port, then reverted)
- [X] T014 [US1] Merge `feature/compose-stack` and confirm `cd src/backend && make check` passes with no Docker daemon (LR-CP3, 2026-11-07, PR #22; LR-19 and LR-20 follow in `feature/local-data-dir`)
- [X] T026 [US2] Declare the `content` text index with BM25 scoring on every start, so an existing `pages` collection is upgraded too, in src/backend/src/health_api/documents/qdrant_index.py, tested by src/backend/tests/test_qdrant_index.py::test_an_existing_collection_should_get_a_bm25_scored_text_index (LR-22, 2026-11-07; found by T015, listed here out of numeric order so the later T-numbers stay stable)
- [X] T027 [US2] Give the Ollama chat call a 300 s read timeout (connect stays 5 s), because a cold `llama3.1` on CPU takes longer than httpx's 5 s default, in src/backend/src/health_api/chat/ollama_chat_model.py, tested by src/backend/tests/test_ollama_chat.py::test_ollama_should_wait_for_a_cold_model (LR-23, 2026-11-07; found by T015 after T026)
- [ ] T015 [US2] Run the Compose manual check in specs/003-local-runtime/plan.md and record the date and result here (SC-001, SC-004). Reopened 2026-11-07: the stack started and an upload was stored, but the first question returned 500 because the Qdrant text index had no BM25 scoring. After T026 the search worked, but the chat call timed out after 5 s while Ollama loaded the model. That is fixed by T027. Re-run after rebuilding the API image.

## Phase 4: User Story 3 - GitOps on Minikube (P2, PR `feature/gitops-minikube`)

- [ ] T016 [US3] Watch this repo from the Minikube cluster: `GitRepository` and `Kustomization` `flux-system` for `https://github.com/ianoflynnautomation/myhealth-ai-app` on `main` with no secret, and `Kustomization` `apps` → `./gitops/apps/overlays/myhealth` with `prune: true` and `wait: false`, in gitops/clusters/myhealth/sync.yaml, gitops/clusters/myhealth/kustomization.yaml and gitops/clusters/myhealth/ks.yaml, tested by src/backend/tests/test_gitops.py::test_sync_should_watch_this_repo_without_a_secret (LR-12)
- [ ] T017 [US3] Add namespace `myhealth` enforcing `baseline` and auditing and warning at `restricted`, with a base kustomization that lists the namespace only, in gitops/apps/base/myhealth/namespace.yaml and gitops/apps/base/myhealth/kustomization.yaml, tested by src/backend/tests/test_gitops.py::test_the_namespace_should_enforce_baseline (LR-13)
- [ ] T018 [US3] Run the API in the cluster with Deployment `myhealth-api:local` (`IfNotPresent`), `PROFILE=local`, `QDRANT_URL`, both model names, `DATA_DIR=/data` and no `OLLAMA_BASE_URL`. Add a Service, PVC `health-data` at `/data`, and a NetworkPolicy allowing egress to `qdrant` on 6333 and to `kube-dns` on UDP and TCP 53. Files: gitops/apps/base/myhealth/api/ks.yaml, gitops/apps/base/myhealth/api/app/kustomization.yaml, gitops/apps/base/myhealth/api/app/api.yaml and gitops/apps/base/myhealth/api/app/networkpolicy.yaml, tested by src/backend/tests/test_gitops.py::test_the_base_api_should_allow_qdrant_and_dns_only (LR-14)
- [ ] T019 [US3] Run the web page in the cluster: Deployment `myhealth-web:local`, a Service, a NetworkPolicy web → api, and a `Kustomization` that depends on `api`, in gitops/apps/base/myhealth/web/ks.yaml, gitops/apps/base/myhealth/web/app/kustomization.yaml, gitops/apps/base/myhealth/web/app/web.yaml and gitops/apps/base/myhealth/web/app/networkpolicy.yaml, tested by src/backend/tests/test_gitops.py::test_the_web_kustomization_should_depend_on_api (LR-15)
- [ ] T020 [US3] Run Qdrant from its Helm chart, one replica, version pinned, with `api` depending on `qdrant`, in gitops/apps/base/myhealth/qdrant/ks.yaml, gitops/apps/base/myhealth/qdrant/app/kustomization.yaml, gitops/apps/base/myhealth/qdrant/app/helmrepository.yaml and gitops/apps/base/myhealth/qdrant/app/helmrelease.yaml, tested by src/backend/tests/test_gitops.py::test_qdrant_should_be_a_pinned_helm_release (LR-16)
- [ ] T021 [US3] Every component `ks.yaml` under gitops/apps/base/myhealth is a Flux `Kustomization` with `prune: true`, `wait: true` and `sourceRef.name: flux-system`, tested by src/backend/tests/test_gitops.py::test_every_component_kustomization_should_prune_wait_and_use_flux_system (LR-21, FR-010)
- [ ] T022 [US3] Point the Minikube overlay at api, web and Qdrant and not Ollama. Patch the Flux `Kustomization` `api` with `spec.patches` that set `OLLAMA_BASE_URL=http://host.minikube.internal:11434/v1` on the Deployment and add an egress `ipBlock` `/32` for the host Ollama on 11434. Files: gitops/apps/overlays/myhealth/kustomization.yaml and gitops/apps/overlays/myhealth/api-patch.yaml, tested by src/backend/tests/test_gitops.py::test_the_myhealth_overlay_should_omit_ollama_and_patch_the_host (LR-17)

## Phase 5: User Story 4 - Homelab overlay (P3, PR `feature/gitops-homelab`)

- [ ] T023 [US4] Run Ollama on the homelab overlay with its own `HelmRepository` `https://otwld.github.io/ollama-helm` and chart `ollama`, pinned, pulling `llama3.1` and `nomic-embed-text`. Patch the Flux `Kustomization` `api` with `dependsOn: ollama` and `spec.patches` setting `OLLAMA_BASE_URL=http://ollama.myhealth.svc.cluster.local:11434/v1` and egress to the `ollama` pods on 11434, with no `ipBlock`. Files: gitops/apps/base/myhealth/ollama/ks.yaml, gitops/apps/base/myhealth/ollama/app/kustomization.yaml, gitops/apps/base/myhealth/ollama/app/helmrepository.yaml, gitops/apps/base/myhealth/ollama/app/helmrelease.yaml, gitops/apps/overlays/homelab/kustomization.yaml and gitops/apps/overlays/homelab/api-patch.yaml, tested by src/backend/tests/test_gitops.py::test_the_homelab_overlay_should_run_ollama (LR-18)

## Phase 6: Verification

- [ ] T024 Confirm LR-12 to LR-18 and LR-21 are merged, and that `cd src/backend && make check` passes without Docker, including the app-shell tests that pin the HTTP contract (FR-016, SC-006). Record the date here (LR-CP4)
- [ ] T025 [US3] Set up Minikube and run the Minikube check in specs/003-local-runtime/plan.md, including the `getent` check of the committed host `/32`. Record the date here. Do not apply the homelab overlay to a shared cluster (SC-002)

## Dependencies

- T002 → T003. T004 and T005 are independent files. T006 waits for T004 and T005. T007 waits for T003 and T006.
- T008 and T009 are independent. T010 waits for both. T011 waits for T010. T012 waits for T007. T013 waits for T011. T014 waits for T012 and T013. T026 waits for T007. T027 waits for T026. T015 waits for T014 and T027.
- T016 → T017 → T018 → T019 → T020 → T021 → T022 → T023. They all add tests to test_gitops.py, so none are [P].
- T024 waits for T023. T025 waits for T022 and T015.
