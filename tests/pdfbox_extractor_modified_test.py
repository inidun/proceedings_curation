import logging

import pytest
from fpdf import FPDF

from proceedings_curation.extractors.pdfbox_extractor_modified import PDFBoxExtractorMod


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
    pdf.cell(0, 10, text=text_content, ln=True)

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


def test_pdfbox_extractor_mod_with_page_numbers(pdf_file, text_content, tmpdir):
    assert pdf_file.exists()
    expected = f"# test\n\n## Page 1\n\n{text_content}\n\n"
    extractor = PDFBoxExtractorMod()

    extractor.extract_text(pdf_file, output_folder=tmpdir, page_numbers=True)

    assert tmpdir.join('test.txt').exists()
    assert tmpdir.join('test.txt').read().rstrip() == expected.rstrip()


def test_pdfbox_extractor_mod_with_custom_output_filename(pdf_file, text_content, tmpdir):
    assert pdf_file.exists()
    custom_filename = "custom_output.txt"
    expected = text_content
    extractor = PDFBoxExtractorMod()

    extractor.extract_text(pdf_file, output_folder=tmpdir, output_filename=custom_filename)

    assert tmpdir.join(custom_filename).exists()
    assert tmpdir.join(custom_filename).read().rstrip() == expected


def test_pdfbox_extractor_mod_with_force_overwrite(pdf_file, text_content, tmpdir):
    assert pdf_file.exists()
    expected = text_content
    extractor = PDFBoxExtractorMod()

    # First extraction
    extractor.extract_text(pdf_file, output_folder=tmpdir)
    assert tmpdir.join('test.txt').exists()
    assert tmpdir.join('test.txt').read().rstrip() == expected

    # Modify the content to simulate a change
    modified_content = "Modified content"
    with open(tmpdir.join('test.txt'), 'w', encoding='utf-8') as f:
        f.write(modified_content)

    # Force overwrite
    extractor.extract_text(pdf_file, output_folder=tmpdir, force=True)
    assert tmpdir.join('test.txt').read().rstrip() == expected


def test_pdfbox_extractor_mod_logs_extraction(pdf_file, text_content, tmpdir, caplog):
    assert pdf_file.exists()
    expected = text_content
    extractor = PDFBoxExtractorMod()

    with caplog.at_level(logging.INFO):
        extractor.extract_text(pdf_file, output_folder=tmpdir)

    assert tmpdir.join('test.txt').exists()
    assert tmpdir.join('test.txt').read().rstrip() == expected

    log_messages = [record.message for record in caplog.records]
    assert any("Processing test.txt (test.pdf:1-1)" in message for message in log_messages)
    assert any("Extracted test.txt (test.pdf:1-1)" in message for message in log_messages)


def test_pdfbox_extractor_mod_logs_skip_extraction(pdf_file, text_content, tmpdir, caplog):
    assert pdf_file.exists()
    expected = text_content
    extractor = PDFBoxExtractorMod()

    # First extraction
    extractor.extract_text(pdf_file, output_folder=tmpdir)
    assert tmpdir.join('test.txt').exists()
    assert tmpdir.join('test.txt').read().rstrip() == expected

    with caplog.at_level(logging.INFO):
        # Attempt to extract again without force
        extractor.extract_text(pdf_file, output_folder=tmpdir)

    log_messages = [record.message for record in caplog.records]
    assert any("Skipping test.txt: Already extracted" in message for message in log_messages)
