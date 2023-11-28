import pytest
from fpdf import FPDF

from proceedings_curation.pdfbox_extractor_modified import PDFBoxExtractorMod


@pytest.fixture(name='text_content')
def mock_text():
    return "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."


@pytest.fixture(name='pdf_file')
def mock_pdf_file(tmpdir, text_content):
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


def test_pdfbox_extractor_mod_returns_expected_output(pdf_file, text_content, tmpdir):
    assert pdf_file.exists()
    expected = text_content
    extractor = PDFBoxExtractorMod()

    extractor.extract_text(pdf_file, output_folder=tmpdir)

    assert tmpdir.join('test.txt').exists()
    assert tmpdir.join('test.txt').read().rstrip() == expected
