import pandas as pd
import pytest

from proceedings_curation.scripts.create_metadata_index import create_metadata_index, main, save_metadata_index


@pytest.fixture(name="proceedings_index_file")
def fixture_proceedings_index_file(tmp_path):
    data = {
        'Record number': [1, 2],
        'Session number': ['3X', '4X'],
        'Pages in doc': ['1-10', '11-20'],
        'Pages in pdf': ['1-10', '11-20'],
        'Date meeting': ['2020-01-01', '2021-01-01'],
        'Session president': ['President 1', 'President 2'],
        'Title meeting': ['Meeting 1', 'Meeting 2'],
        'Chapter': ['A', 'B'],
        'Languages': ['mul|ara eng', 'eng'],
        'Document codes': ['Document code 1', 'Document code 2'],
        'Title': ['Title 1', 'Title 2'],
        'Titles in other languages': ['Title 1', 'Title 2'],
        'Publication date': [2020, 2021],
        'Volume': [1, 2],
        'Physical description': ['Physical description 1', 'Physical description 2'],
        'Conference name': ['Conference name 1', 'Conference name 2'],
        'Conference session': ['Conference session 1', 'Conference session 2'],
        'Conference location': ['Conference location 1', 'Conference location 2'],
        'Conference date ': [2020, 2021],
        'Corporate subject': ['Corporate subject 1', 'Corporate subject 2'],
        'Variant title': ['Variant title 1', 'Variant title 2'],
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "proceedings_index.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture(name="proceedings_metadata_file")
def fixture_proceedings_metadata_file(tmp_path):
    data = {
        'record_number': [1, 2],
        'year': [2020, 2021],
        'filename': ['file1', 'file2'],
        'columns': [2, 2],
        'volume': [1, 2],
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "proceedings_metadata.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


class TestCreateMetadataIndex:
    def test_create_metadata_index(self, proceedings_index_file, proceedings_metadata_file):
        idx = create_metadata_index(proceedings_index_file, proceedings_metadata_file)

        expected_columns = [
            'record_number',
            'session_number',
            'pages_in_doc',
            'pages_in_pdf',
            'date_meeting',
            'session_president',
            'title_meeting',
            'chapter',
            'languages',
            'document_codes',
            'title',
            'titles_in_other_languages',
            'publication_date',
            'volume',
            'physical_description',
            'conference_name',
            'conference_session',
            'conference_location',
            'conference_date',
            'corporate_subject',
            'variant_title',
            'filename',
            'columns',
            'meeting_name_id',
            'pages',
            'first_page',
            'last_page',
            'language_codes',
        ]

        assert isinstance(idx, pd.DataFrame)
        assert not idx.empty
        assert idx.columns.tolist() == expected_columns


@pytest.fixture(name="metadata_index")
def fixture_metadata_index():
    data = {
        'record_number': [1, 2],
        'session_number': ['3X', '4X'],
        'pages_in_doc': ['1-10', '11-20'],
        'pages_in_pdf': ['1-10', '11-20'],
        'date_meeting': ['2020-01-01', '2021-01-01'],
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
        'conference_date ': [2020, 2021],
        'corporate_subject': ['Corporate subject 1', 'Corporate subject 2'],
        'variant_title': ['Variant title 1', 'Variant title 2'],
        'filename': ['file1', 'file2'],
        'columns': [2, 2],
        'meeting_name_id': ['1_meeting_1', '2_meeting_2'],
        'pages': ['1-10', '11-20'],
        'first_page': [1, 11],
        'last_page': [10, 20],
        'language_codes': ['mul ara eng', 'eng'],
    }
    return pd.DataFrame(data)


class TestSaveMetadataIndex:
    def test_save_metadata_index(self, metadata_index, tmp_path):
        file_path = tmp_path / "metadata_index.xlsx"
        save_metadata_index(metadata_index, file_path)

        assert file_path.exists()

        df_read = pd.read_excel(file_path)
        pd.testing.assert_frame_equal(metadata_index, df_read.iloc[:, 1:])


class TestMainFunction:
    def test_main_function(self, proceedings_index_file, proceedings_metadata_file, tmp_path):
        output_file = tmp_path / "metadata_index.xlsx"
        main(proceedings_index_file, proceedings_metadata_file, output_file)

        assert output_file.exists()

        df_read = pd.read_excel(output_file)
        assert not df_read.empty
        assert df_read.columns.tolist()[1:] == [
            'record_number',
            'session_number',
            'pages_in_doc',
            'pages_in_pdf',
            'date_meeting',
            'session_president',
            'title_meeting',
            'chapter',
            'languages',
            'document_codes',
            'title',
            'titles_in_other_languages',
            'publication_date',
            'volume',
            'physical_description',
            'conference_name',
            'conference_session',
            'conference_location',
            'conference_date',
            'corporate_subject',
            'variant_title',
            'filename',
            'columns',
            'meeting_name_id',
            'pages',
            'first_page',
            'last_page',
            'language_codes',
        ]
