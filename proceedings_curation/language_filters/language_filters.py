from typing import List

from proceedings_curation.language_detectors.language_detectors import LangDetect, LanguageDetector


class LanguageFilter:
    """Language filter for paragraphs."""

    def __init__(
        self,
        languages: str | List[str],
        keep_undetected: bool = False,
        language_detector: LanguageDetector | None = None,
    ) -> None:
        """Create a language filter for paragraphs.

        Args:
            languages (str | List[str]): List of languages to keep
            keep_undetected (bool, optional): Keep paragraphs with undetected language. Defaults to False.
            language_detector (LanguageDetector | None, optional): Language detector. Defaults to None.
        """
        self.languages = languages if isinstance(languages, list) else [languages]
        self.keep_undetected = keep_undetected

        if isinstance(language_detector, LanguageDetector):
            self.language_detector = language_detector
        else:
            self.language_detector = LangDetect(possible_languages=self.languages)

    def filter(self, paragraphs: List[str]) -> List[str]:
        """Filter paragraphs by language. If keep_undetected is True, paragraphs with undetected language will be kept. If keep_undetected is False, paragraphs with undetected language will be removed. If a language detector is provided, it will be used to detect the language of the paragraphs. If no language detector is provided, a LangDetect language detector will be used. If a paragraph is detected as one of the languages provided in the constructor, it will be kept. If a paragraph is detected as an undetected language and keep_undetected is True, it will be kept. If a paragraph is detected as an undetected language and keep_undetected is False, it will be removed.

        Args:
            paragraphs (List[str]): List of paragraphs

        Returns:
            List[str]: Filtered list of paragraphs
        """
        return [
            paragraph
            for paragraph in paragraphs
            if self.language_detector.detect(paragraph) in self.languages
            or (self.keep_undetected and self.language_detector.detect(paragraph) is None)
        ]


if __name__ == '__main__':  # pragma: no cover
    pass
