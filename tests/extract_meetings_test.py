from unittest.mock import patch

import pandas as pd
import pytest

from proceedings_curation.pdfbox_extractor_modified import PDFBoxExtractorMod
from proceedings_curation.scripts.extract_meetings import check_source_files, extract_meetings, load_index, main
from proceedings_curation.tesseract_extractor_modified import TesseractExtractorMod


@pytest.fixture(name="metadata_index")
def fixture_metadata_index():
    data = {
        'record_number': [1, 2],
        'session_number': ['3X', '4X'],
        'pages_in_doc': ['1-10', '11-20'],
        'pages_in_pdf': ['1-10', '11-20'],
        'date_meeting': [pd.Timestamp('2020-01-01'), pd.Timestamp('2021-01-01')],
        'session_president': ['President 1', 'President 2'],
        'title_meeting': ['Meeting 1', 'Meeting 2'],
        'chapter': ['A', 'B'],
        'languages': ['mul|ara eng', 'eng'],
        'document_codes': ['Document code 1', 'Document code 2'],
        'title': ['Title 1', 'Title 2'],
        'titles_in_other_languages': ['Title 1', 'Title 2'],
        'publication_date': [2020, 2021],
        'volume': [1, 2],
        'physical_description': ['Physical description 1', 'Physical description 2'],
        'conference_name': ['Conference name 1', 'Conference name 2'],
        'conference_session': ['Conference session 1', 'Conference session 2'],
        'conference_location': ['Conference location 1', 'Conference location 2'],
        'conference_date': [2020, 2021],
        'corporate_subject': ['Corporate subject 1', 'Corporate subject 2'],
        'variant_title': ['Variant title 1', 'Variant title 2'],
        'filename': ['file1.pdf', 'file2.pdf'],
        'columns': [2, 2],
        'meeting_name_id': ['1_meeting_1', '2_meeting_2'],
        'pages': ['1-10', '11-20'],
        'first_page': [1, 11],
        'last_page': [10, 20],
        'language_codes': ['mul ara eng', 'eng'],
    }
    return pd.DataFrame(data)


@pytest.fixture(name="input_path")
def fixture_input_path(tmp_path):
    path = tmp_path / "input"
    path.mkdir()
    (path / "file1.pdf").touch()
    (path / "file2.pdf").touch()
    return path


@pytest.fixture(name="output_path")
def fixture_output_path(tmp_path):
    path = tmp_path / "output"
    path.mkdir()
    return path


class TestExtractMeetings:
    def test_extract_meetings_with_pdfbox(self, metadata_index, input_path, output_path):
        extractor = PDFBoxExtractorMod()
        with patch.object(extractor, 'extract_text', return_value=None) as mock_extract:
            extract_meetings(metadata_index, input_path, output_path, extractor)
            assert mock_extract.call_count == 2

    def test_extract_meetings_with_tesseract(self, metadata_index, input_path, output_path):
        extractor = TesseractExtractorMod()
        with patch.object(extractor, 'extract_text', return_value=None) as mock_extract:
            extract_meetings(metadata_index, input_path, output_path, extractor)
            assert mock_extract.call_count == 2

    def test_extract_meetings_with_tesseract_logging_is_as_expected(
        self, metadata_index, input_path, output_path, caplog
    ):
        extractor = TesseractExtractorMod()
        with patch.object(extractor, 'extract_text', return_value=None) as mock_extract:
            extract_meetings(metadata_index, input_path, output_path, extractor)
            assert mock_extract.call_count == 2
            assert "Using Tesseract with language mul ara eng for file1.pdf" in caplog.text
            assert "Using Tesseract with language eng for file2.pdf" in caplog.text

    def test_extract_meetings_force_overwrite(self, metadata_index, input_path, output_path):
        extractor = PDFBoxExtractorMod()
        with patch.object(extractor, 'extract_text', return_value=None) as mock_extract:
            extract_meetings(metadata_index, input_path, output_path, extractor, force=True)
            assert mock_extract.call_count == 2

    def test_extract_meetings_with_page_numbers(self, metadata_index, input_path, output_path):
        extractor = PDFBoxExtractorMod()
        with patch.object(extractor, 'extract_text', return_value=None) as mock_extract:
            extract_meetings(metadata_index, input_path, output_path, extractor, page_numbers=True)
            assert mock_extract.call_count == 2

    def test_extract_meetings_with_page_sep(self, metadata_index, input_path, output_path):
        extractor = PDFBoxExtractorMod()
        with patch.object(extractor, 'extract_text', return_value=None) as mock_extract:
            extract_meetings(metadata_index, input_path, output_path, extractor, page_sep='---')
            assert mock_extract.call_count == 2


@pytest.fixture(name="metadata_index_file")
def fixture_metadata_index_file(tmp_path, metadata_index):
    file_path = tmp_path / "metadata_index.xlsx"
    metadata_index.to_excel(file_path, index_label='meeting_id')
    return file_path


class TestCheckSourceFiles:
    def test_check_source_files(self, input_path, metadata_index, caplog):
        check_source_files(input_path, metadata_index)
        assert f'Found all source files in {input_path}' in caplog.text

    def test_check_source_files_with_missing_files(self, input_path, metadata_index, caplog):
        (input_path / "file1.pdf").unlink()
        check_source_files(input_path, metadata_index)
        assert "1 missing source files in" in caplog.text


class TestLoadIndex:
    def test_load_index(self, metadata_index_file):
        index = load_index(metadata_index_file)
        assert not index.empty
        assert 'record_number' in index.columns


class TestMain:
    def test_main(self, metadata_index_file, input_path, output_path):
        with patch('proceedings_curation.scripts.extract_meetings.extract_meetings') as mock_extract_meetings:
            main(
                metadata_index=metadata_index_file,
                input_path=input_path,
                output_path=output_path,
                extractor='pdfbox',
                page_numbers=False,
                page_sep='',
                force=False,
            )
            assert mock_extract_meetings.called

    def test_main_with_tesseract(self, metadata_index_file, input_path, output_path):
        with patch('proceedings_curation.scripts.extract_meetings.extract_meetings') as mock_extract_meetings:
            main(
                metadata_index=metadata_index_file,
                input_path=input_path,
                output_path=output_path,
                extractor='tesseract',
                page_numbers=False,
                page_sep='',
                force=False,
            )
            assert mock_extract_meetings.called
