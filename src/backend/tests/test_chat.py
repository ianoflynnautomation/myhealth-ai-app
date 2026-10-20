import hashlib

import pytest
from fastapi.testclient import TestClient
from fpdf import FPDF

from health_api.documents.memory_corpus import MemoryCorpus, StoredChunk
from health_api.main import create_app

pytestmark = pytest.mark.acceptance


def test_chat_is_off_when_disabled() -> None:
    response = TestClient(create_app(chat_enabled=False)).post(
        "/chat",
        json={"messages": [{"role": "user", "content": "hello"}]},
    )

    assert response.status_code == 404


def test_the_stub_app_should_answer_chat_by_default() -> None:
    # Given
    client = TestClient(create_app())

    # When
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "hello"}]},
    )

    # Then
    assert response.status_code == 200
    assert response.json()["outputText"] == "No stored document answers that."


def _fixture_pdf() -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="DemoMarker value is 10 units.")
    return bytes(pdf.output())


def test_chat_should_cite_the_stored_page() -> None:
    # Given
    pdf = _fixture_pdf()
    client = TestClient(create_app(documents_enabled=True, chat_enabled=True))
    uploaded = client.post(
        "/documents",
        files={"file": ("example.pdf", pdf, "application/pdf")},
    )
    assert uploaded.status_code == 201
    document_id = hashlib.sha256(pdf).hexdigest()

    # When
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "What is the DemoMarker value?"}]},
    )

    # Then
    assert response.status_code == 200
    assert response.json() == {
        "outputText": "DemoMarker value is 10 units.",
        "citations": [
            {
                "id": f"{document_id}:1",
                "sourceFile": "example.pdf",
                "sourcePage": 1,
                "content": "DemoMarker value is 10 units.",
            }
        ],
    }


def test_an_empty_store_should_return_the_fixed_sentence() -> None:
    # Given
    client = TestClient(create_app(chat_enabled=True))

    # When
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "What is the DemoMarker value?"}]},
    )

    # Then
    assert response.status_code == 200
    assert response.json() == {
        "outputText": "No stored document answers that.",
        "citations": [],
    }


def test_an_unmatched_question_should_return_the_fixed_sentence() -> None:
    # Given
    pdf = _fixture_pdf()
    client = TestClient(create_app(documents_enabled=True, chat_enabled=True))
    client.post(
        "/documents",
        files={"file": ("example.pdf", pdf, "application/pdf")},
    )

    # When
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "Where was the zebra?"}]},
    )

    # Then
    assert response.status_code == 200
    assert response.json() == {
        "outputText": "No stored document answers that.",
        "citations": [],
    }


def test_a_non_json_chat_body_should_return_unsupported_media_type() -> None:
    # Given
    client = TestClient(create_app(chat_enabled=True))

    # When
    response = client.post(
        "/chat",
        content=b"hello",
        headers={"content-type": "text/plain"},
    )

    # Then
    assert response.status_code == 415
    assert response.json() == {
        "error": {
            "code": "UNSUPPORTED_MEDIA_TYPE",
            "message": "Chat body must be JSON.",
            "details": {},
        }
    }


def test_empty_messages_should_return_validation_error() -> None:
    # Given
    client = TestClient(create_app(chat_enabled=True))

    # When
    response = client.post("/chat", json={"messages": []})

    # Then
    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "At least one message is required.",
            "details": {},
        }
    }


def test_blank_content_should_return_validation_error() -> None:
    # Given
    client = TestClient(create_app(chat_enabled=True))

    # When
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "   "}]},
    )

    # Then
    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Message content must not be blank.",
            "details": {},
        }
    }


def test_an_unknown_chat_field_should_return_validation_error() -> None:
    # Given
    client = TestClient(create_app(chat_enabled=True))

    # When
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "hello"}], "extra": True},
    )

    # Then
    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Unknown field.",
            "details": {},
        }
    }


def test_an_assistant_last_message_should_return_validation_error() -> None:
    # Given
    client = TestClient(create_app(chat_enabled=True))

    # When
    response = client.post(
        "/chat",
        json={"messages": [{"role": "assistant", "content": "hello"}]},
    )

    # Then
    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Last message must be from the user.",
            "details": {},
        }
    }


class _RaisingCorpus(MemoryCorpus):
    def search(self, query: str) -> list[StoredChunk]:
        raise RuntimeError("secret boom")


def test_a_server_error_should_hide_the_traceback() -> None:
    # Given
    client = TestClient(
        create_app(chat_enabled=True, corpus=_RaisingCorpus()),
        raise_server_exceptions=False,
    )

    # When
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "hello"}]},
    )

    # Then
    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Internal server error.",
            "details": {},
        }
    }
    assert "secret boom" not in response.text
    assert "Traceback" not in response.text
