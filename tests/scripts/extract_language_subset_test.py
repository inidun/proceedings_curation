import os

import pytest
import typer
from typer.testing import CliRunner

from proceedings_curation.scripts.extract_language_subset import main, process_files


@pytest.fixture(name="input_folder")
def fixture_input_folder(tmpdir):
    folder = tmpdir.mkdir("input")
    file1 = folder.join("file1.txt")
    file1.write(
        "This is a test file.\nIt contains multiple lines and this one should be one of them.\nSome of them are in English."
    )
    file2 = folder.join("file2.txt")
    file2.write("Este es un archivo de prueba.\nContiene varias líneas.\nAlgunas de ellas están en español.")
    return str(folder)


@pytest.fixture(name="output_folder")
def fixture_output_folder(tmpdir):
    return str(tmpdir.mkdir("output"))


@pytest.fixture(name="tokenizer")
def fixture_tokenizer():
    return "nltk"


@pytest.fixture(name="possible_languages")
def fixture_possible_languages():
    return ["en", "es"]


@pytest.fixture(name="filter_languages")
def fixture_filter_languages():
    return ["en"]


@pytest.fixture(name="language_detector")
def fixture_language_detector():
    return "langdetect"


@pytest.fixture(name="keep_undetected")
def fixture_keep_undetected():
    return False


@pytest.fixture(name="force_overwrite")
def fixture_force_overwrite():
    return False


class TestProcessFiles:
    def test_process_files(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        input_folder,
        output_folder,
        tokenizer,
        possible_languages,
        filter_languages,
        language_detector,
        keep_undetected,
        force_overwrite,
    ):
        process_files(
            input_folder,
            output_folder,
            tokenizer,
            possible_languages,
            filter_languages,
            language_detector,
            keep_undetected,
            force_overwrite,
        )

        # Check if output files are created
        assert os.path.exists(os.path.join(output_folder, "file1.txt"))
        assert os.path.exists(os.path.join(output_folder, "file2.txt"))

        # Check the content of the output files
        with open(os.path.join(output_folder, "file1.txt"), 'r', encoding='utf-8') as file:
            content = file.read()
            assert "This is a test file." in content
            assert "It contains multiple lines" in content
            assert "Some of them are in English." in content

        with open(os.path.join(output_folder, "file2.txt"), 'r', encoding='utf-8') as file:
            content = file.read()
            assert content == ""  # Since filter_languages is ["en"], the Spanish content should be filtered out

    def test_process_files_logging(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        caplog,
        input_folder,
        output_folder,
        tokenizer,
        possible_languages,
        filter_languages,
        language_detector,
        keep_undetected,
        force_overwrite,
    ):
        process_files(
            input_folder,
            output_folder,
            tokenizer,
            possible_languages,
            filter_languages,
            language_detector,
            keep_undetected,
            force_overwrite,
        )

        assert "Processing files in " in caplog.text
        assert "Number of files: " in caplog.text
        assert "Using tokenizer: " in caplog.text
        assert "Using language detector: " in caplog.text
        assert "Keeping languages: " in caplog.text
        assert "Keeping undetected paragraphs: " in caplog.text
        assert "Processing " in caplog.text

        assert "Number of lines: " in caplog.text
        assert "Number of paragraphs: " in caplog.text

        assert "Number of paragraphs kept: " in caplog.text
        assert "Percentage of paragraphs kept: " in caplog.text
        assert "Files saved in " in caplog.text

    def test_process_files_logging_skipping(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        caplog,
        input_folder,
        output_folder,
        tokenizer,
        possible_languages,
        filter_languages,
        language_detector,
        keep_undetected,
        force_overwrite,
    ):
        file1 = os.path.join(output_folder, "file1.txt")
        with open(file1, 'w', encoding='utf-8') as file:
            file.write(
                "This is a test file.\nIt contains multiple lines and this one should be one of them.\nSome of them are in English."
            )

        process_files(
            input_folder,
            output_folder,
            tokenizer,
            possible_languages,
            filter_languages,
            language_detector,
            keep_undetected,
            force_overwrite,
        )

        assert "File already exists. Skipping " in caplog.text

    def test_process_files_logging_undetected(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        caplog,
        input_folder,
        output_folder,
        tokenizer,
        possible_languages,
        filter_languages,
        language_detector,
        keep_undetected,
        force_overwrite,
    ):
        file3 = os.path.join(input_folder, "file3.txt")
        file3_content = "abcdef.\nghijklm."
        with open(file3, 'w', encoding='utf-8') as file:
            file.write(file3_content)

        assert len(os.listdir(input_folder)) == 3
        assert os.path.exists(os.path.join(input_folder, "file3.txt"))

        process_files(
            input_folder,
            output_folder,
            tokenizer,
            possible_languages,
            filter_languages,
            language_detector,
            keep_undetected,
            force_overwrite,
        )

        assert "Unable to detect language for paragraph " in caplog.text


app = typer.Typer()
app.command()(main)

runner = CliRunner()


class TestMainFunction:
    def test_main_function_with_no_arguments_returns_with_exit_code_2(self):
        result = runner.invoke(app, [])
        assert result.exit_code == 2

    def test_main_function(self, input_folder, output_folder):
        result = runner.invoke(
            app,
            [
                input_folder,
                output_folder,
                "--tokenizer",
                "nltk",
                "--possible-languages",
                "en",
                "--possible-languages",
                "es",
                "--filter-languages",
                "en",
                "--filter-languages",
                "zh",
                "--language-detector",
                "langdetect",
                "--no-keep-undetected",
                "--no-force-overwrite",
                "--logging-levels",
                "INFO",
                "--logging-levels",
                "WARNING",
            ],
        )
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(output_folder, "file1.txt"))
        assert os.path.exists(os.path.join(output_folder, "file2.txt"))

        with open(os.path.join(output_folder, "file1.txt"), 'r', encoding='utf-8') as file:
            content = file.read()
            assert "This is a test file." in content
            assert "It contains multiple lines" in content
            assert "Some of them are in English." in content

        with open(os.path.join(output_folder, "file2.txt"), 'r', encoding='utf-8') as file:
            content = file.read()
            assert content == ""  # Since filter_languages is ["en"], the Spanish content should be filtered out

    def test_main_function_logging(self, input_folder, output_folder, caplog):
        result = runner.invoke(
            app,
            [
                input_folder,
                output_folder,
                "--tokenizer",
                "nltk",
                "--possible-languages",
                "en",
                "--possible-languages",
                "es",
                "--filter-languages",
                "en",
                "--filter-languages",
                "zh",
                "--language-detector",
                "langdetect",
                "--no-keep-undetected",
                "--no-force-overwrite",
                "--logging-levels",
                "INFO",
                "--logging-levels",
                "WARNING",
            ],
        )
        assert result.exit_code == 0
        assert f"Processing files in {input_folder}" in caplog.text
        assert f"Number of files: {len(os.listdir(input_folder))}" in caplog.text
        assert "Using tokenizer: " in caplog.text
        assert "Using language detector: " in caplog.text
        assert "Keeping languages: " in caplog.text
        assert "Keeping undetected paragraphs: " in caplog.text
        assert "Processing " in caplog.text
        assert "Number of lines: " in caplog.text
        assert "Number of paragraphs: " in caplog.text
        assert "Number of paragraphs kept: " in caplog.text
        assert "Percentage of paragraphs kept: " in caplog.text
        assert f"Files saved in {output_folder}" in caplog.text

    def test_main_function_when_filter_languages_is_none_defaults_to_english(self, input_folder, output_folder):
        result = runner.invoke(
            app,
            [
                input_folder,
                output_folder,
                "--tokenizer",
                "nltk",
                "--possible-languages",
                "en",
                "--possible-languages",
                "es",
                "--language-detector",
                "langdetect",
                "--no-keep-undetected",
                "--no-force-overwrite",
                "--logging-levels",
                "INFO",
                "--logging-levels",
                "WARNING",
            ],
        )
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(output_folder, "file1.txt"))
        assert os.path.exists(os.path.join(output_folder, "file2.txt"))

        with open(os.path.join(output_folder, "file1.txt"), 'r', encoding='utf-8') as file:
            content = file.read()
            assert "This is a test file." in content
            assert "It contains multiple lines" in content
            assert "Some of them are in English." in content

        with open(os.path.join(output_folder, "file2.txt"), 'r', encoding='utf-8') as file:
            content = file.read()
            assert content == ""

    def test_main_function_when_logging_levels_is_none_uses_default_levels(self, input_folder, output_folder, caplog):
        result = runner.invoke(
            app,
            [
                input_folder,
                output_folder,
                "--tokenizer",
                "nltk",
                "--possible-languages",
                "en",
                "--possible-languages",
                "es",
                "--filter-languages",
                "en",
                "--filter-languages",
                "zh",
                "--language-detector",
                "langdetect",
                "--no-keep-undetected",
                "--no-force-overwrite",
            ],
        )
        assert result.exit_code == 0
        assert f"Processing files in {input_folder}" in caplog.text
        assert f"Number of files: {len(os.listdir(input_folder))}" in caplog.text
        assert "Using tokenizer: " in caplog.text
        assert "Using language detector: " in caplog.text
        assert "Keeping languages: " in caplog.text
        assert "Keeping undetected paragraphs: " in caplog.text
        assert "Processing " in caplog.text
        assert "Number of lines: " in caplog.text
        assert "Number of paragraphs: " in caplog.text
        assert "Number of paragraphs kept: " in caplog.text
        assert "Percentage of paragraphs kept: " in caplog.text
        assert f"Files saved in {output_folder}" in caplog.text

        assert os.path.exists(os.path.join(output_folder, "info.log"))
        assert os.path.exists(os.path.join(output_folder, "debug.log"))
        assert os.path.exists(os.path.join(output_folder, "warning.log"))
