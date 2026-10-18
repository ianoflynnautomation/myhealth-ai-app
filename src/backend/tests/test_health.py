from fastapi import FastAPI

from health_api.main import create_app


def test_create_app_returns_an_app() -> None:
    app = create_app()
    assert isinstance(app, FastAPI)
