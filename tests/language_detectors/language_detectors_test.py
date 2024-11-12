import pytest

from proceedings_curation.language_detectors.language_detectors import (
    LangDetect,
    LanguageDetector,
    LanguageDetectorFactory,
)


class TestLangDetect:
    @pytest.fixture(name="lang_detect")
    def fixture_lang_detect(self):
        return LangDetect()

    def test_detect_english(self, lang_detect):
        text = "This is a test sentence."
        assert lang_detect.detect(text) == 'en'

    def test_detect_french(self, lang_detect):
        text = "Ceci est une phrase de test."
        assert lang_detect.detect(text) == 'fr'

    def test_detect_with_possible_languages(self):
        lang_detect = LangDetect(possible_languages=['en', 'fr'])
        text = "Ceci est une phrase de test."
        assert lang_detect.detect(text) == 'fr'

    def test_detect_with_threshold(self):
        lang_detect = LangDetect(threshold=0.9)
        text = "This is a test sentence."
        assert lang_detect.detect(text) == 'en'

    def test_detect_with_invalid_text(self, lang_detect):
        text = ""
        assert lang_detect.detect(text) is None

    def test_detect_with_non_supported_language(self):
        lang_detect = LangDetect(possible_languages=['es'])
        text = "Ceci est une phrase de test."
        assert lang_detect.detect(text) is None

    def test_detect_with_low_probability(self):
        lang_detect = LangDetect(threshold=0.99)
        text = "Un kilo de tomates."  # This is a sentence in French and Spanish
        assert lang_detect.detect(text) is None


class TestLanguageDetector:
    def test_detect_not_implemented(self):
        detector = LanguageDetector()
        with pytest.raises(NotImplementedError):
            detector.detect("This is a test sentence.")


class TestLanguageDetectorFactory:
    def test_get_language_detector(self):
        detector = LanguageDetectorFactory.get_language_detector("langdetect")
        assert isinstance(detector, LangDetect)

    def test_get_language_detector_with_invalid_detector(self):
        with pytest.raises(ValueError):
            LanguageDetectorFactory.get_language_detector("invalid")
