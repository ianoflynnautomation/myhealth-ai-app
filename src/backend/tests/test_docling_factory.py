import sys

import pytest

pytestmark = pytest.mark.unit


def test_the_docling_factory_should_not_import_docling() -> None:
    # Given
    sys.modules.pop("docling", None)

    # When
    import health_api.documents.docling_factory as factory

    # Then
    assert "docling" not in sys.modules
    with pytest.raises(RuntimeError, match="uv sync --group local"):
        factory.docling_converter()
    assert "docling" not in sys.modules
