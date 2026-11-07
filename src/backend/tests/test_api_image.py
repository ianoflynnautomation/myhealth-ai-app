from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_DOCKERFILE = Path(__file__).resolve().parents[1] / "Dockerfile"


def test_the_api_image_should_install_the_local_group() -> None:
    # Given
    dockerfile = _DOCKERFILE.read_text()
    syncs = [line for line in dockerfile.splitlines() if "uv sync" in line]
    launch = [line for line in dockerfile.splitlines() if line.startswith("CMD ")]

    # When
    command = " ".join(line.strip() for line in launch)

    # Then
    assert syncs
    for line in syncs:
        assert "--frozen" in line
        assert "--no-dev" in line
        assert "--group local" in line
    assert "fastapi dev" not in dockerfile
    assert 'fastapi", "run"' in command
    assert "0.0.0.0" in command
    assert "8000" in command
