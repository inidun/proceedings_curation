# pylint: disable=useless-parent-delegation
import nltk


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
        if tokenizer == "nltk":
            return NLTKParagraphTokenizer()
        raise ValueError("Invalid tokenizer")


if __name__ == '__main__':  # pragma: no cover
    pass
