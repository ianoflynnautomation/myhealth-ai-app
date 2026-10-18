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


def test_document_upload_is_off_unless_enabled() -> None:
    response = TestClient(create_app()).post("/documents")

    assert response.status_code == 404


def test_post_document_stores_pdf() -> None:
    pdf = _fixture_pdf()
    response = TestClient(create_app(documents_enabled=True)).post(
        "/documents",
        files={"file": ("example.pdf", pdf, "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["pageCount"] == 1
    assert body["chunkCount"] == 1
    assert body["sourceFile"] == "example.pdf"
    assert body["id"] == hashlib.sha256(pdf).hexdigest()


def test_get_documents_lists_file() -> None:
    pdf = _fixture_pdf()
    client = TestClient(create_app(documents_enabled=True))
    client.post(
        "/documents",
        files={"file": ("example.pdf", pdf, "application/pdf")},
    )

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == {
        "documents": [
            {
                "id": hashlib.sha256(pdf).hexdigest(),
                "sourceFile": "example.pdf",
                "pageCount": 1,
                "chunkCount": 1,
            }
        ]
    }
