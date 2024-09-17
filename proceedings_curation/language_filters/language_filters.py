# language_filters/language_filters.py

from typing import List

from proceedings_curation.language_detectors.language_detectors import LangDetect, LanguageDetector


class LanguageFilter:
    def __init__(
        self,
        languages: str | List[str],
        keep_undetected: bool = False,
        language_detector: LanguageDetector | None = None,
    ) -> None:
        self.languages = languages if isinstance(languages, list) else [languages]
        self.keep_undetected = keep_undetected
        self.language_detector = language_detector or LangDetect(self.languages)

    def filter(self, paragraphs: List[str]) -> List[str]:
        return [
            paragraph
            for paragraph in paragraphs
            if self.language_detector.detect(paragraph) in self.languages
            or (self.keep_undetected and self.language_detector.detect(paragraph) is None)
        ]
