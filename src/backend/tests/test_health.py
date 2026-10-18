from fastapi import FastAPI
from fastapi.testclient import TestClient

from health_api.main import create_app


def test_create_app_returns_an_app() -> None:
    app = create_app()
    assert isinstance(app, FastAPI)


def test_health_returns_ok() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
