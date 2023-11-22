import pytesseract
import pytest
from fpdf import FPDF

from proceedings_curation.tesseract_extractor_modified import TesseractExtractorMod


def test_tesseract_language_support():
    assert 'eng' in pytesseract.get_languages()
    assert set(pytesseract.get_languages()) >= {'eng', 'osd'}


def test_tesseract_version():
    assert pytesseract.get_tesseract_version().release >= (5, 3, 0)
    assert pytesseract.get_tesseract_version().public == '5.3.3'


@pytest.fixture
def mock_text():
    return "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

@pytest.fixture
def mock_pdf_file(tmpdir, mock_text):
    # Text content for the PDF
    text_content = mock_text

    # Create a new PDF document
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font and font size
    pdf.set_font("Arial", size=12)

    # Add the text content to the page
    pdf.cell(0, 10, txt=text_content, ln=True)

    # Path to the mock PDF file
    mock_file_path = tmpdir.join("test.pdf")

    # Save the PDF document to the mock file
    pdf.output(str(mock_file_path))

    return mock_file_path


def test_tesseract_extractor_mod_returns_expected_output(mock_pdf_file, mock_text, tmpdir):
    assert mock_pdf_file.exists()
    expected = mock_text
    extractor = TesseractExtractorMod()

    extractor.extract_text(mock_pdf_file, output_folder=tmpdir)

    assert tmpdir.join('test.txt').exists()
    assert tmpdir.join('test.txt').read().rstrip() == expected

