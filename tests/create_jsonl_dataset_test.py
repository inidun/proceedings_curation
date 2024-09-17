import logging
import os

import jsonlines
import nltk
import pytest

from proceedings_curation.scripts.create_jsonl_dataset import create_jsonl_dataset, extract_n_consecutive_sentences

os.environ['BASE_URL'] = 'BASE_URL/'


@pytest.fixture(name='metadata_index')
def fixture_metadata_index(tmpdir):
    # Create a temporary metadata index file
    metadata_index_path = os.path.join(tmpdir, 'metadata_index.csv')
    with open(metadata_index_path, 'w', encoding='utf-8') as f:
        f.write("meeting_id;filename;title_meeting;date_meeting;conference_date;language_codes;first_page;last_page\n")
        f.write("100;file1.pdf;First Meeting;2022-01-01;2022;eng;1;10\n")
        f.write("200;file2.pdf;Second Meeting;2022-02-02;2022;eng;1;20\n")
    return metadata_index_path


@pytest.fixture(name='input_path')
def fixture_input_path(tmpdir):
    # Create a temporary input folder with text files
    input_folder = os.path.join(tmpdir, 'input')
    os.makedirs(input_folder, exist_ok=True)
    with open(os.path.join(input_folder, '2022_100_first_meeting.txt'), 'w', encoding='utf-8') as f:
        f.write(
            "This is the text for meeting 1. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."
        )
    with open(os.path.join(input_folder, '2022_200_second_meeting.txt'), 'w', encoding='utf-8') as f:
        f.write(
            "This is the text for meeting 2. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."
        )
    return input_folder


@pytest.fixture(name='output_path')
def fixture_output_path(tmpdir):
    # Create a temporary output folder
    output_folder = os.path.join(tmpdir, 'output')
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


def test_create_jsonl_dataset(metadata_index, input_path, output_path):
    # Call the create_jsonl_dataset function
    create_jsonl_dataset(metadata_index, input_path, output_path)

    # Check if the JSONL dataset file is created
    dataset_file = os.path.join(output_path, 'dataset.jsonl')
    assert os.path.exists(dataset_file)

    # Check the content of the JSONL dataset file
    with jsonlines.open(dataset_file, 'r') as reader:
        lines = list(reader)

    assert len(lines) == 2

    assert (
        lines[0]['text']
        == "This is the text for meeting 1. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."
    )
    assert lines[0]['meta']['file'] == "2022_100_first_meeting.txt"
    assert lines[0]['meta']['title'] == "First Meeting"
    assert lines[0]['meta']['date'] == "2022-01-01"
    assert lines[0]['meta']['source'] == "BASE_URL/file1.pdf#page=1"

    assert (
        lines[1]['text']
        == "This is the text for meeting 2. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."
    )
    assert lines[1]['meta']['file'] == "2022_200_second_meeting.txt"
    assert lines[1]['meta']['title'] == "Second Meeting"
    assert lines[1]['meta']['date'] == "2022-02-02"
    assert lines[1]['meta']['source'] == "BASE_URL/file2.pdf#page=1"


def test_create_jsonl_dataset_sample(metadata_index, input_path, output_path):

    # Call the create_jsonl_dataset function with sample arguments
    create_jsonl_dataset(metadata_index, input_path, output_path, number_of_files=1, sentences_per_file=3, seed=42)

    # Check if the JSONL dataset file is created
    dataset_file = os.path.join(output_path, 'dataset.jsonl')
    assert os.path.exists(dataset_file)

    # Check the content of the JSONL dataset file
    with jsonlines.open(dataset_file, 'r') as reader:
        lines = list(reader)

    assert len(lines) == 1

    assert lines[0]['text'] == "This is the third sentence. This is the fourth sentence. This is the fifth sentence."
    assert lines[0]['meta']['file'] == "2022_200_second_meeting.txt"
    assert lines[0]['meta']['title'] == "Second Meeting"
    assert lines[0]['meta']['date'] == "2022-02-02"
    assert lines[0]['meta']['source'] == "BASE_URL/file2.pdf#page=1"

    # Check if the number of sentences is correct
    assert len(nltk.sent_tokenize(lines[0]['text'])) == 3


def test_create_jsonl_dataset_missing_file(metadata_index, input_path, output_path, caplog):
    # Remove the first input file
    os.remove(os.path.join(input_path, '2022_100_first_meeting.txt'))

    with caplog.at_level(logging.ERROR):
        # Call the create_jsonl_dataset function
        create_jsonl_dataset(metadata_index, input_path, output_path)

    log_messages = [record.message for record in caplog.records]
    assert "File 2022_100_first_meeting.txt not found" in log_messages

    # Check if the JSONL dataset file is created
    dataset_file = os.path.join(output_path, 'dataset.jsonl')
    assert os.path.exists(dataset_file)

    # Check the content of the JSONL dataset file
    with jsonlines.open(dataset_file, 'r') as reader:
        lines = list(reader)

    assert len(lines) == 1

    assert (
        lines[0]['text']
        == "This is the text for meeting 2. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."
    )
    assert lines[0]['meta']['file'] == "2022_200_second_meeting.txt"
    assert lines[0]['meta']['title'] == "Second Meeting"
    assert lines[0]['meta']['date'] == "2022-02-02"
    assert lines[0]['meta']['source'] == "BASE_URL/file2.pdf#page=1"


def test_extract_n_consecutive_sentences():
    text = (
        "This is the first sentence. This is the second sentence. This is the third sentence. "
        "This is the fourth sentence. This is the fifth sentence."
    )

    # Test extracting 3 consecutive sentences with a fixed seed
    result = extract_n_consecutive_sentences(text, 3, seed=42)
    assert result == "This is the third sentence. This is the fourth sentence. This is the fifth sentence."

    # Test extracting more sentences than available
    result = extract_n_consecutive_sentences(text, 10)
    assert result == text

    # Test extracting exactly the number of sentences available
    result = extract_n_consecutive_sentences(text, 5)
    assert result == text

    # Test extracting 1 sentence
    result = extract_n_consecutive_sentences(text, 1, seed=42)
    assert result == "This is the first sentence."

    # Test extracting 0 sentences (should return empty string)
    result = extract_n_consecutive_sentences(text, 0)
    assert result == ""

    # Test extracting sentences without seed (random behavior)
    result = extract_n_consecutive_sentences(text, 2)
    assert len(nltk.sent_tokenize(result)) == 2
