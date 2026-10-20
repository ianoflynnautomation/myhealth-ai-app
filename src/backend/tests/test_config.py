import pytest

from health_api.config import Settings

pytestmark = pytest.mark.unit


def test_stub_settings_should_need_no_service_urls() -> None:
    # Given

    # When
    settings = Settings(profile="stub")

    # Then
    assert settings.profile == "stub"
