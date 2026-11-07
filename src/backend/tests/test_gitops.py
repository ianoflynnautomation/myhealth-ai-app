from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_GITOPS = Path(__file__).resolve().parents[3] / "gitops"


def _text(relative: str) -> str:
    return (_GITOPS / relative).read_text()


def test_sync_should_watch_this_repo_without_a_secret() -> None:
    # Given
    sync = _text("clusters/myhealth/sync.yaml")
    apps = _text("clusters/myhealth/ks.yaml")
    listing = _text("clusters/myhealth/kustomization.yaml")

    # When
    components = _GITOPS / "clusters/myhealth/gotk-components.yaml"

    # Then
    assert "kind: GitRepository" in sync
    assert "name: flux-system" in sync
    assert "url: https://github.com/ianoflynnautomation/myhealth-ai-app" in sync
    assert "branch: main" in sync
    assert "path: ./gitops/clusters/myhealth" in sync
    assert "secretRef" not in sync
    assert "name: apps" in apps
    assert "path: ./gitops/apps/overlays/myhealth" in apps
    assert "prune: true" in apps
    assert "wait: false" in apps
    assert "sync.yaml" in listing
    assert "ks.yaml" in listing
    assert not components.exists()


def test_the_namespace_should_enforce_baseline() -> None:
    # Given
    namespace = _text("apps/base/myhealth/namespace.yaml")

    # When
    listing = _text("apps/base/myhealth/kustomization.yaml")

    # Then
    assert "kind: Namespace" in namespace
    assert "name: myhealth" in namespace
    assert "pod-security.kubernetes.io/enforce: baseline" in namespace
    assert "pod-security.kubernetes.io/audit: restricted" in namespace
    assert "pod-security.kubernetes.io/warn: restricted" in namespace
    assert "namespace.yaml" in listing
    assert "ks.yaml" not in listing


def test_the_base_api_should_allow_qdrant_and_dns_only() -> None:
    # Given
    flux = _text("apps/base/myhealth/api/ks.yaml")
    api = _text("apps/base/myhealth/api/app/api.yaml")
    policy = _text("apps/base/myhealth/api/app/networkpolicy.yaml")

    # When
    listing = _text("apps/base/myhealth/api/app/kustomization.yaml")

    # Then
    assert "path: ./gitops/apps/base/myhealth/api/app" in flux
    assert "targetNamespace: myhealth" in flux
    assert "image: myhealth-api:local" in api
    assert "imagePullPolicy: IfNotPresent" in api
    for setting in (
        "name: PROFILE\n              value: local",
        "name: QDRANT_URL\n              value: http://qdrant.myhealth.svc.cluster.local:6333",
        "name: OLLAMA_CHAT_MODEL\n              value: llama3.1",
        "name: OLLAMA_EMBED_MODEL\n              value: nomic-embed-text",
        "name: DATA_DIR\n              value: /data",
    ):
        assert setting in api
    assert "name: OLLAMA_BASE_URL" not in api
    assert "claimName: health-data" in api
    assert "mountPath: /data" in api
    assert "app.kubernetes.io/name: qdrant" in policy
    assert "port: 6333" in policy
    assert "k8s-app: kube-dns" in policy
    assert "protocol: UDP" in policy
    assert "port: 53" in policy
    assert "ipBlock" not in policy
    assert "ollama" not in policy
    for name in ("api.yaml", "networkpolicy.yaml"):
        assert name in listing


def test_the_web_kustomization_should_depend_on_api() -> None:
    # Given
    flux = _text("apps/base/myhealth/web/ks.yaml")
    web = _text("apps/base/myhealth/web/app/web.yaml")
    policy = _text("apps/base/myhealth/web/app/networkpolicy.yaml")

    # When
    depends_on = flux.split("dependsOn:", 1)[1]

    # Then
    assert "path: ./gitops/apps/base/myhealth/web/app" in flux
    assert "- name: api" in depends_on
    assert "image: myhealth-web:local" in web
    assert "imagePullPolicy: IfNotPresent" in web
    assert "type: NodePort" in web
    assert "app.kubernetes.io/name: api" in policy
    assert "port: 8000" in policy
    assert "k8s-app: kube-dns" in policy
