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
