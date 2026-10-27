import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_BACKEND = Path(__file__).resolve().parents[1]
_ROOT = _BACKEND.parents[1]


def _requirement_name(requirement: str) -> str:
    name = requirement.split("[", 1)[0]
    for marker in (">", "=", "<", "~", "!", " "):
        name = name.split(marker, 1)[0]
    return name


def test_the_local_group_should_stay_out_of_make_check() -> None:
    # Given
    project = tomllib.loads((_BACKEND / "pyproject.toml").read_text())
    makefile = (_BACKEND / "Makefile").read_text()
    pull_request = (_ROOT / ".github" / "workflows" / "ci-pr.yml").read_text()
    main = (_ROOT / ".github" / "workflows" / "ci-main.yml").read_text()

    # When
    group = [_requirement_name(item) for item in project["dependency-groups"]["local"]]

    # Then
    assert "docling" in group
    assert "qdrant-client" in group
    assert "--group local" not in makefile
    assert "--group local" not in pull_request
    assert "--group local" not in main
