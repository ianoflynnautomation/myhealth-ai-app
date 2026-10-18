import hashlib

from fastapi.testclient import TestClient
from fpdf import FPDF

from health_api.main import create_app


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
