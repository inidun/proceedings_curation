import pytest

from proceedings_curation.language_detectors.language_detectors import LanguageDetector
from proceedings_curation.language_filters.language_filters import LanguageFilter


class MockLanguageDetector(LanguageDetector):
    def __init__(self, possible_languages):
        self.possible_languages = possible_languages

    def detect(self, text):
        if "english" in text.lower():
            return "en"
        if "français" in text.lower():
            return "fr"
        return None


@pytest.fixture(name="mock_language_detector")
def fixture_mock_language_detector():
    return MockLanguageDetector(possible_languages=["en", "fr"])


def test_language_filter_with_single_language(mock_language_detector):
    language_filter = LanguageFilter(languages="en", language_detector=mock_language_detector)
    paragraphs = ["This is an English paragraph.", "Ceci est un paragraphe français."]
    filtered_paragraphs = language_filter.filter(paragraphs)
    assert filtered_paragraphs == ["This is an English paragraph."]


def test_language_filter_with_multiple_languages(mock_language_detector):
    language_filter = LanguageFilter(languages=["en", "fr"], language_detector=mock_language_detector)
    paragraphs = ["This is an English paragraph.", "Ceci est un paragraphe français."]
    filtered_paragraphs = language_filter.filter(paragraphs)
    assert filtered_paragraphs == ["This is an English paragraph.", "Ceci est un paragraphe français."]


def test_language_filter_with_keep_undetected(mock_language_detector):
    language_filter = LanguageFilter(languages="en", keep_undetected=True, language_detector=mock_language_detector)
    paragraphs = ["This is an English paragraph.", "Ceci est un paragraphe français.", "Unknown language paragraph."]
    filtered_paragraphs = language_filter.filter(paragraphs)
    assert filtered_paragraphs == ["This is an English paragraph.", "Unknown language paragraph."]


def test_language_filter_without_keep_undetected(mock_language_detector):
    language_filter = LanguageFilter(languages="en", keep_undetected=False, language_detector=mock_language_detector)
    paragraphs = ["This is an English paragraph.", "Ceci est un paragraphe français.", "Unknown language paragraph."]
    filtered_paragraphs = language_filter.filter(paragraphs)
    assert filtered_paragraphs == ["This is an English paragraph."]


def test_language_filter_with_default_language_detector():
    language_filter = LanguageFilter(languages="en")
    paragraphs = ["This is an English paragraph.", "Ceci est un paragraphe français."]
    filtered_paragraphs = language_filter.filter(paragraphs)
    assert filtered_paragraphs == ["This is an English paragraph."]
