from pathlib import Path

import pytesseract
import pytest
from fpdf import FPDF

from proceedings_curation.extractors.tesseract_extractor_modified import TesseractExtractorMod
from proceedings_curation.extractors.utils import extract_text_from_alto, extract_text_from_hocr


def test_tesseract_language_support():
    assert 'eng' in pytesseract.get_languages()
    assert set(pytesseract.get_languages()) >= {'eng', 'osd'}


def test_tesseract_version():
    assert pytesseract.get_tesseract_version().release >= (5, 5, 0)
    assert pytesseract.get_tesseract_version().public == '5.5.0'


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


def test_extract_text_logs_info_when_output_file_exists_and_force_is_false(pdf_file, text_content, tmpdir, caplog):
    assert pdf_file.exists()
    expected = text_content
    extractor = TesseractExtractorMod()

    output_filename = 'test.txt'
    output_file = tmpdir.join(output_filename)
    output_file.write(text_content)

    extractor.extract_text(pdf_file, output_folder=tmpdir)

    assert tmpdir.join(output_filename).exists()
    assert tmpdir.join(output_filename).read().rstrip() == expected

    assert f'Skipping {output_filename}: Already extracted' in caplog.text


def test_extract_text_overwrites_output_file_when_force_is_true(pdf_file, text_content, tmpdir, caplog):
    assert pdf_file.exists()
    expected = text_content
    extractor = TesseractExtractorMod()

    output_filename = 'test.txt'
    output_file = tmpdir.join(output_filename)
    output_file.write('Some other content')

    extractor.extract_text(pdf_file, output_folder=tmpdir, force=True)

    assert tmpdir.join(output_filename).exists()
    assert tmpdir.join(output_filename).read().rstrip() == expected

    assert f'Overwriting {output_filename}' in caplog.text


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


@pytest.fixture(name='text_content_multiple_lines')
def mock_text_multiple_lines():
    return [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    ]


@pytest.fixture(name='pdf_file_multiple_pages')
def mock_pdf_file_multiple_pages(tmpdir, text_content_multiple_lines):
    # Create a new PDF document
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font and font size
    pdf.set_font("Arial", size=12)

    # Add the text content to the page
    pdf.cell(0, 10, text=text_content_multiple_lines[0], ln=True)

    # Add another page
    pdf.add_page()

    # Add the text content to the page
    pdf.cell(0, 10, text=text_content_multiple_lines[1], ln=True)

    # Path to the mock PDF file
    mock_file_path = tmpdir.join("test.pdf")

    # Save the PDF document to the mock file
    pdf.output(str(mock_file_path))

    return mock_file_path


@pytest.fixture(name='expected_multiple_pages_with_page_numbers')
def mock_expected_multiple_pages_with_page_numbers():
    return """# test


## Page 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit.



## Page 2

Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."""


def test_extract_test_with_page_numbers(pdf_file_multiple_pages, expected_multiple_pages_with_page_numbers, tmpdir):
    assert pdf_file_multiple_pages.exists()
    expected = expected_multiple_pages_with_page_numbers
    extractor = TesseractExtractorMod()

    extractor.extract_text(pdf_file_multiple_pages, output_folder=tmpdir, page_numbers=True)

    assert tmpdir.join('test.txt').exists()
    assert tmpdir.join('test.txt').read().rstrip() == expected
    assert tmpdir.join('test.txt').read().strip().split('\n')[0] == '# ' + Path(pdf_file_multiple_pages).stem
