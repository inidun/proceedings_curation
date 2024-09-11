# pylint: disable=redefined-outer-name, useless-parent-delegation
import os
from enum import Enum

import loguru
import nltk
import typer
from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException
from typing_extensions import Annotated


class ParagraphTokenizer:
    def __init__(self) -> None:
        pass

    def tokenize(self, text: str) -> list[str]:
        raise NotImplementedError("Tokenize method must be implemented")


class SimpleParagraphTokenizer(ParagraphTokenizer):
    def __init__(self) -> None:
        super().__init__()

    # NOTE: This method is not handling case where paragraph does not start with a number or a number in paranthesis

    def tokenize(self, text: str) -> list[str]:
        paragraphs = []
        paragraph = ''
        for line in text.split('\n'):
            if line.strip() and (
                line.strip()[0].isdigit()
                or (len(line.strip()) > 1 and line.strip()[0] == '(' and line.strip()[1].isdigit())
            ):
                if paragraph:
                    paragraphs.append(
                        paragraph.strip()
                    )  # Trim whitespaces from the beginning and the end of the paragraph
                paragraph = line
            else:
                paragraph += ' ' + line
        if len(paragraph.strip()) > 0:
            paragraphs.append(paragraph.strip())  # Trim whitespaces from the beginning and the end of the paragraph
        return paragraphs


class NLTKParagraphTokenizer(ParagraphTokenizer):
    def __init__(self) -> None:
        super().__init__()

    def tokenize(self, text: str) -> list[str]:
        paragraphs = nltk.sent_tokenize(text)
        paragraphs = [paragraph.replace('\n', ' ') for paragraph in paragraphs]
        return paragraphs


class TokenizerFactory:
    @staticmethod
    def get_tokenizer(tokenizer: str) -> ParagraphTokenizer:
        if tokenizer == "simple":
            return SimpleParagraphTokenizer()
        elif tokenizer == "nltk":
            return NLTKParagraphTokenizer()
        else:
            raise ValueError("Invalid tokenizer")


# fmt: off
DEFAULT_LANGUAGES = ['af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lt', 'lv', 'mk', 'ml', 'mr', 'ne', 'nl', 'no', 'pa', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw']
# fmt: on

DetectorFactory.seed = 0  # Necessary for deterministic results


class LanguageDetector:
    def __init__(self, possible_languages: list[str]) -> None:
        self.possible_languages = possible_languages or DEFAULT_LANGUAGES

    def detect(self, text: str) -> str | None:
        raise NotImplementedError("Detect method must be implemented")


# FIXME: possible_languages should be optional. If not provided, detect all languages supported by langdetect
class LangDetect(LanguageDetector):
    def __init__(self, possible_languages: list[str]) -> None:
        super().__init__(possible_languages)

    def detect(self, text: str) -> str | None:
        try:
            detections = [d for d in detect_langs(text) if d.lang in self.possible_languages]
        except LangDetectException:
            detections = None
        return str(detections[0].lang) if detections else None  # TODO (optional): Use a threshold to return None


class LanguageDetectorFactory:
    @staticmethod
    def get_language_detector(detector: str, possible_languages: list[str]) -> LanguageDetector:
        if detector == "langdetect":
            return LangDetect(possible_languages)
        else:
            raise ValueError("Invalid language detector")


class LanguageFilter:
    def __init__(
        self,
        languages: str | list[str],
        keep_undetected: bool = False,
        language_detector: LanguageDetector | None = None,
    ) -> None:
        self.languages = languages if isinstance(languages, list) else [languages]
        self.keep_undetected = keep_undetected
        self.language_detector = language_detector or LangDetect(self.languages)

    def filter(self, paragraphs: list[str]) -> list[str]:
        return [
            paragraph
            for paragraph in paragraphs
            if self.language_detector.detect(paragraph) in self.languages
            or (self.keep_undetected and self.language_detector.detect(paragraph) is None)
        ]


def process_files(
    input_folder: str,
    output_folder: str,
    tokenizer: str,
    possible_languages: list[str],
    filter_languages: str | list[str],
    language_detector: str = "langdetect",
    keep_undetected: bool = False,
    force_overwrite: bool = False,
) -> None:
    loguru.logger.info(f"Processing files in {input_folder.replace(os.path.expanduser('~'), '~')}")
    text_files = sorted([filename for filename in os.listdir(input_folder) if filename.endswith('.txt')])
    loguru.logger.info(f"Number of files: {len(text_files)}")

    tokenizer = TokenizerFactory.get_tokenizer(tokenizer)
    loguru.logger.info(f"Using tokenizer: {tokenizer.__class__.__name__}")

    language_detector = LanguageDetectorFactory.get_language_detector(language_detector, possible_languages)
    loguru.logger.info(
        f"Using language detector: {language_detector.__class__.__name__}. Detecting languages: {possible_languages}"
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


def main(  # pylint: disable=too-many-arguments
    input_folder: str,
    output_folder: str,
    tokenizer: str = 'nltk',
    possible_languages: list[str] = ['en', 'ar', 'zh', 'fr', 'ru', 'es'],
    # filter_languages: Annotated[List[FilterLanguages], typer.Option()] = [FilterLanguages.en, FilterLanguages.fr],
    filter_languages: Annotated[list[str], typer.Option()] = ['en'],
    language_detector: str = "langdetect",
    keep_undetected: bool = False,
    force_overwrite: bool = False,
    logging_levels: list[str] = ['INFO', 'WARNING', 'DEBUG'],
) -> None:

    # filter_languages = [lang.value for lang in filter_languages]

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


if __name__ == "__main__":
    typer.run(main)
