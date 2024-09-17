import pytesseract
import pytest
from fpdf import FPDF

from proceedings_curation.tesseract_extractor_modified import TesseractExtractorMod
from proceedings_curation.utils import extract_text_from_alto, extract_text_from_hocr


def test_tesseract_language_support():
    assert 'eng' in pytesseract.get_languages()
    assert set(pytesseract.get_languages()) >= {'eng', 'osd'}


def test_tesseract_version():
    assert pytesseract.get_tesseract_version().release >= (5, 4, 0)
    assert pytesseract.get_tesseract_version().public == '5.4.1'


@pytest.fixture(name='text_content')
def mock_text():
    return "Lorem ipsum dolor sit amet, consectetur adipiscing elit."


@pytest.fixture(name='pdf_file')
def mock_pdf_file(tmpdir, text_content):
    # Create a new PDF document
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font and font size
    pdf.set_font("Arial", size=12)

    # Add the text content to the page
    pdf.cell(0, 10, text=text_content, ln=True)

    # Path to the mock PDF file
    mock_file_path = tmpdir.join("test.pdf")

    # Save the PDF document to the mock file
    pdf.output(str(mock_file_path))

    return mock_file_path


def test_tesseract_extractor_mod_returns_expected_output(pdf_file, text_content, tmpdir):
    assert pdf_file.exists()
    expected = text_content
    extractor = TesseractExtractorMod()

    extractor.extract_text(pdf_file, output_folder=tmpdir)

    assert tmpdir.join('test.txt').exists()
    assert tmpdir.join('test.txt').read().rstrip() == expected


def test_pdf_to_txt(pdf_file, text_content, tmpdir):
    assert pdf_file.exists()
    expected = text_content
    extractor = TesseractExtractorMod()
    extractor.set_language('eng')

    extractor.pdf_to_txt(pdf_file, output_folder=tmpdir)

    assert tmpdir.join('test_0001.txt').exists()
    assert tmpdir.join('test_0001.txt').read().rstrip() == expected


def test_pdf_to_alto(pdf_file, text_content, tmpdir):
    assert pdf_file.exists()
    expected = text_content
    extractor = TesseractExtractorMod()

    extractor.pdf_to_alto(pdf_file, output_folder=tmpdir)

    assert tmpdir.join('test_0001.alto').exists()
    assert extract_text_from_alto(tmpdir.join('test_0001.alto')) == expected


def test_pdf_to_hocr(pdf_file, text_content, tmpdir):
    assert pdf_file.exists()
    expected = text_content
    extractor = TesseractExtractorMod()

    extractor.pdf_to_hocr(pdf_file, output_folder=tmpdir)

    assert tmpdir.join('test_0001.hocr').exists()
    assert extract_text_from_hocr(tmpdir.join('test_0001.hocr')) == expected
