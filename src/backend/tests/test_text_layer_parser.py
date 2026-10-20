import pytest
from fpdf import FPDF

from health_api.documents.text_layer_parser import parse_text_layer

pytestmark = pytest.mark.unit


def _fixture_pdf() -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="DemoMarker value is 10 units.")
    return bytes(pdf.output())


def test_parser_reads_fixture_sentence() -> None:
    pages = parse_text_layer(_fixture_pdf())

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert pages[0].text == "DemoMarker value is 10 units."
