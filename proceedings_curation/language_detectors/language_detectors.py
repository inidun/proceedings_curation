from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException

# pylint: disable=useless-parent-delegation

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

        raise ValueError("Invalid language detector")


if __name__ == '__main__':
    pass
