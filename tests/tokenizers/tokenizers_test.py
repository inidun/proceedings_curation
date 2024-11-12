import pytest

from proceedings_curation.tokenizers.tokenizers import (
    NLTKParagraphTokenizer,
    ParagraphTokenizer,
    SimpleParagraphTokenizer,
    TokenizerFactory,
)


class TestSimpleParagrapghTokenizer:
    @pytest.fixture(name="tokenizer")
    def tokenizer(self):
        return SimpleParagraphTokenizer()

    def test_tokenize_single_paragraph(self, tokenizer):
        text = "1. This is a single paragraph."
        expected = ["1. This is a single paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_multiple_paragraphs(self, tokenizer):
        text = "1. This is the first paragraph.\n2. This is the second paragraph."
        expected = ["1. This is the first paragraph.", "2. This is the second paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_empty_lines(self, tokenizer):
        text = "1. This is the first paragraph.\n\n2. This is the second paragraph."
        expected = ["1. This is the first paragraph.", "2. This is the second paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_continuation_lines(self, tokenizer):
        text = "1. This is the first paragraph.\nThis is still the first paragraph.\n2. This is the second paragraph."
        expected = [
            "1. This is the first paragraph. This is still the first paragraph.",
            "2. This is the second paragraph.",
        ]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_number_in_parenthesis(self, tokenizer):
        text = "(1) This is the first paragraph.\n(2) This is the second paragraph."
        expected = ["(1) This is the first paragraph.", "(2) This is the second paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_mixed_number_formats(self, tokenizer):
        text = "1. This is the first paragraph.\n(2) This is the second paragraph."
        expected = ["1. This is the first paragraph.", "(2) This is the second paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_no_number(self, tokenizer):
        text = "This is a paragraph without a number."
        expected = ["This is a paragraph without a number."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_empty_string(self, tokenizer):
        text = ""
        expected: list[str] = []
        assert tokenizer.tokenize(text) == expected


class TestNLTKParagraphTokenizer:
    @pytest.fixture(name="tokenizer")
    def tokenizer(self):
        return NLTKParagraphTokenizer()

    def test_tokenize_single_paragraph(self, tokenizer):
        text = "1. This is not a single paragraph."
        expected = ["1.", "This is not a single paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_multiple_paragraphs(self, tokenizer):
        text = "1. This is the actually the second paragraph.\n2. This is the fourth paragraph."
        expected = ["1.", "This is the actually the second paragraph.", "2.", "This is the fourth paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_empty_lines(self, tokenizer):
        text = "1. This is the actually the second paragraph.\n\n2. This is the fourth paragraph."
        expected = ["1.", "This is the actually the second paragraph.", "2.", "This is the fourth paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_continuation_lines(self, tokenizer):
        text = "1. This is the first paragraph.\nThis is not still the first paragraph, in this case it is the second.\n2. This is the third paragraph."
        expected = [
            "1.",
            "This is the first paragraph.",
            "This is not still the first paragraph, in this case it is the second.",
            "2.",
            "This is the third paragraph.",
        ]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_number_in_parenthesis(self, tokenizer):
        text = "(1) This is the first paragraph.\n(2) This is the second paragraph."
        expected = ["(1) This is the first paragraph.", "(2) This is the second paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_mixed_number_formats(self, tokenizer):
        text = "1. This is not the first paragraph, it's the second.\n(2) This is the third paragraph."
        expected = ["1.", "This is not the first paragraph, it's the second.", "(2) This is the third paragraph."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_paragraph_with_no_number(self, tokenizer):
        text = "This is a paragraph without a number."
        expected = ["This is a paragraph without a number."]
        assert tokenizer.tokenize(text) == expected

    def test_tokenize_empty_string(self, tokenizer):
        text = ""
        expected: list[str] = []
        assert tokenizer.tokenize(text) == expected


class TestParagraphTokenizer:
    def test_initialize_ParagraphTokenizer(self):
        tokenizer = ParagraphTokenizer()
        assert tokenizer is not None

    def test_ParagraphTokenizer_tokenize_raises_NotImplementedError(self):
        tokenizer = ParagraphTokenizer()
        with pytest.raises(NotImplementedError):
            tokenizer.tokenize("")


class TestTokenizerFactory:
    def test_TokenizerFactory_get_tokenizer_simple(self):
        tokenizer = TokenizerFactory.get_tokenizer("simple")
        assert isinstance(tokenizer, SimpleParagraphTokenizer)

    def test_TokenizerFactory_get_tokenizer_nltk(self):
        tokenizer = TokenizerFactory.get_tokenizer("nltk")
        assert isinstance(tokenizer, NLTKParagraphTokenizer)

    def test_TokenizerFactory_get_tokenizer_invalid(self):
        with pytest.raises(ValueError):
            TokenizerFactory.get_tokenizer("invalid")
