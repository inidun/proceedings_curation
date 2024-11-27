# pylint: disable=redefined-outer-name
import os
from enum import Enum

import loguru
import typer
from typing_extensions import Annotated

from proceedings_curation.language_detectors.language_detectors import LanguageDetectorFactory
from proceedings_curation.language_filters.language_filters import LanguageFilter
from proceedings_curation.tokenizers.tokenizers import TokenizerFactory


def process_files(
    input_folder: str,
    output_folder: str,
    tokenizer: str,
    possible_languages: list[str] | None,
    filter_languages: str | list[str],
    language_detector: str = "langdetect",
    keep_undetected: bool = False,
    force_overwrite: bool = False,
) -> None:
    """Process text files in a folder by tokenizing paragraphs, detecting languages, and filtering paragraphs based on language. Save filtered paragraphs to a new folder with the same filenames. Optionally, keep paragraphs with undetected languages. Optionally, overwrite existing files. Log information about the process.

    Args:
        input_folder (str): Path to folder with text files
        output_folder (str): Path to save filtered text files
        tokenizer (str): Tokenizer to use
        possible_languages (list[str] | None): Possible languages to consider
        filter_languages (str | list[str]): Languages to keep
        language_detector (str, optional): Language detector to use. Defaults to "langdetect".
        keep_undetected (bool, optional): Keep paragraphs with undetected languages. Defaults to False.
        force_overwrite (bool, optional): Overwrite existing files. Defaults to False.
    """
    loguru.logger.info(f"Processing files in {input_folder.replace(os.path.expanduser('~'), '~')}")
    text_files = sorted([filename for filename in os.listdir(input_folder) if filename.endswith('.txt')])
    loguru.logger.info(f"Number of files: {len(text_files)}")

    tokenizer = TokenizerFactory.get_tokenizer(tokenizer)
    loguru.logger.info(f"Using tokenizer: {tokenizer.__class__.__name__}")

    language_detector_options = {"possible_languages": possible_languages, "threshold": None}

    language_detector = LanguageDetectorFactory.get_language_detector(
        detector=language_detector, **language_detector_options
    )

    loguru.logger.info(
        f"Using language detector: {language_detector.__class__.__name__} with options: {language_detector_options}"
    )

    language_filter = LanguageFilter(
        filter_languages, keep_undetected=keep_undetected, language_detector=language_detector
    )
    loguru.logger.info(f"Keeping languages: {filter_languages}")
    loguru.logger.info(f"Keeping undetected paragraphs: {keep_undetected}")

    for filename in text_files:
        input_file = os.path.join(input_folder, filename)
        output_file = os.path.join(output_folder, filename)
        loguru.logger.info(f"Processing {filename}")
        if os.path.exists(output_file) and not force_overwrite:
            loguru.logger.info(f"File already exists. Skipping {filename}")
            continue
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()
        loguru.logger.info(f'Number of lines: {len(text.splitlines())}')
        paragraphs = tokenizer.tokenize(text)
        loguru.logger.info(f'Number of paragraphs: {len(paragraphs)}')
        for i, paragraph in enumerate(paragraphs):
            language = language_detector.detect(paragraph)
            if language is None:
                loguru.logger.warning(f'Unable to detect language for paragraph {i+1}: "{paragraph[:50]}"')
        filtered_paragraphs = language_filter.filter(paragraphs)
        loguru.logger.info(f'Number of paragraphs kept: {len(filtered_paragraphs)}')
        loguru.logger.info(f'Percentage of paragraphs kept: {len(filtered_paragraphs)/len(paragraphs)*100:.2f}%')
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(filtered_paragraphs))
    loguru.logger.success(f"Files saved in {output_folder.replace(os.path.expanduser('~'), '~')}")


class FilterLanguages(str, Enum):
    en = 'en'
    ar = 'ar'
    zh = 'zh'
    fr = 'fr'
    ru = 'ru'
    es = 'es'


def main(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    input_folder: str,
    output_folder: str,
    tokenizer: str = 'nltk',
    possible_languages: list[str] | None = None,
    filter_languages: Annotated[list[str], typer.Option()] | None = None,
    language_detector: str = "langdetect",
    keep_undetected: bool = False,
    force_overwrite: bool = False,
    logging_levels: list[str] | None = None,
) -> None:
    """Process text files in a folder by tokenizing paragraphs, detecting languages, and filtering paragraphs based on language. Save filtered paragraphs to a new folder with the same filenames. Optionally, keep paragraphs with undetected languages. Optionally, overwrite existing files. Log information about the process.

    Args:
        input_folder (str): Folder with text files
        output_folder (str): Folder to save filtered text files
        tokenizer (str, optional): Tokenizer to use. Defaults to 'nltk'.
        possible_languages (list[str] | None, optional): Possible languages to consider. Defaults to None.
        filter_languages (Annotated[list[str], typer.Option()], optional): Languages to keep. Defaults to ['en'].
        language_detector (str, optional): Language detector to use. Defaults to "langdetect".
        keep_undetected (bool, optional): Keep paragraphs with undetected languages. Defaults to False.
        force_overwrite (bool, optional): Overwrite existing files. Defaults to False.
        logging_levels (list[str], optional): Logging levels. Defaults to ['INFO', 'WARNING', 'DEBUG'].
    """

    if filter_languages is None:
        filter_languages = ['en']
    if logging_levels is None:
        logging_levels = ['INFO', 'WARNING', 'DEBUG']

    os.makedirs(output_folder, exist_ok=True)

    for logging_level in logging_levels:
        loguru.logger.add(
            os.path.join(output_folder, f'{logging_level.lower()}.log'),
            level=logging_level,
            format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
        )

    loguru.logger.info(f"Logging levels set to: {logging_levels}")
    loguru.logger.info(f"Log files are saved in: {output_folder.replace(os.path.expanduser('~'), '~')}")

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


if __name__ == "__main__":  # pragma: no cover
    typer.run(main)
