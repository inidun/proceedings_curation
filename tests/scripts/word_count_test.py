from unittest.mock import MagicMock, mock_open, patch

import pytest

from proceedings_curation.scripts.word_count import export_csv, get_fileinfo


@pytest.fixture(name='mock_zipfile')
def fixture_mock_zipfile():
    with patch('zipfile.ZipFile') as mock_zip:
        mock_zip_instance = MagicMock()
        mock_zip.return_value.__enter__.return_value = mock_zip_instance
        yield mock_zip_instance


def test_get_fileinfo(mock_zipfile):
    mock_zipfile.namelist.return_value = ['file1.txt', 'file2.txt']
    mock_zipfile.getinfo.side_effect = lambda name: MagicMock(file_size=100)
    mock_zipfile.open.side_effect = [
        mock_open(read_data=b'This is a test file.').return_value,
        mock_open(read_data=b'Another test file.').return_value,
    ]

    result = get_fileinfo('dummy.zip')

    assert len(result) == 2
    assert result[0]['filename'] == 'file1.txt'
    assert result[0]['tokens_wc'] == 6
    assert result[0]['tokens_re'] == 6
    assert result[0]['filesize'] == 100
    assert result[1]['filename'] == 'file2.txt'
    assert result[1]['tokens_wc'] == 4
    assert result[1]['tokens_re'] == 4
    assert result[1]['filesize'] == 100


def test_export_csv():
    data = [
        {'filename': 'file1.txt', 'tokens_wc': 5, 'tokens_re': 6, 'filesize': 100},
        {'filename': 'file2.txt', 'tokens_wc': 3, 'tokens_re': 4, 'filesize': 100},
    ]
    with patch('builtins.open', mock_open()) as mocked_file:
        export_csv(data, 'output.csv')
        mocked_file().write.assert_any_call('filename,tokens_wc,tokens_re,filesize\n')
        mocked_file().write.assert_any_call('file1.txt,5,6,100\n')
        mocked_file().write.assert_any_call('file2.txt,3,4,100\n')
