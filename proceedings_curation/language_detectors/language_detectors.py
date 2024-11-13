# pylint: disable=useless-parent-delegation
from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException

# fmt: off
DEFAULT_LANGUAGES = ['af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lt', 'lv', 'mk', 'ml', 'mr', 'ne', 'nl', 'no', 'pa', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw']
# fmt: on

DetectorFactory.seed = 0  # Necessary for deterministic results


class LanguageDetector:
    """Base class for language detectors."""

    def __init__(self) -> None:
        pass

    def detect(self, text: str) -> str | None:
        raise NotImplementedError("Detect method must be implemented")


class LangDetect(LanguageDetector):
    """Language detector using langdetect library."""

    def __init__(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__()
        self.options = kwargs
        self.possible_languages = kwargs.get("possible_languages", None)
        self.threshold = kwargs.get("threshold", None)

    def detect(self, text: str) -> str | None:
        """Detect language of a text. If possible_languages is set, only those languages will be considered. If threshold is set, only languages with a probability higher than the threshold will be considered. If both possible_languages and threshold are set, both conditions must be met. If no language is detected, None is returned.

        Args:
            text (str): Text to detect language

        Returns:
            str | None: Detected language or None if language could not be detected
        """
        try:
            if self.threshold is None:
                detections = [
                    d
                    for d in detect_langs(text)
                    if self.possible_languages is None or d.lang in self.possible_languages
                ]
            else:
                detections = [
                    d
                    for d in detect_langs(text)
                    if (self.possible_languages is None or d.lang in self.possible_languages)
                    and d.prob >= self.threshold
                ]
        except LangDetectException:
            detections = None
        return str(detections[0].lang) if detections else None


class LanguageDetectorFactory:
    """Factory class for language detectors."""

    @staticmethod
    def get_language_detector(detector: str, **kwargs) -> LanguageDetector:  # type: ignore[no-untyped-def]
        """Get a language detector.

        Raises:
            ValueError: If an invalid language detector is provided

        Returns:
            LanguageDetector: Language detector
        """
        if detector == "langdetect":
            return LangDetect(**kwargs)

        raise ValueError("Invalid language detector")


if __name__ == '__main__':  # pragma: no cover
    pass
