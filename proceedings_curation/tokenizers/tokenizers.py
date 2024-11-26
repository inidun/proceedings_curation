# pylint: disable=useless-parent-delegation
import nltk


class ParagraphTokenizer:
    """Base class for paragraph tokenizers"""

    def __init__(self) -> None:
        pass

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text into paragraphs

        Args:
            text (str): Text to tokenize

        Raises:
            NotImplementedError: NotImplementedError is raised if the method is not implemented

        Returns:
            list[str]: List of paragraphs
        """
        raise NotImplementedError("Tokenize method must be implemented")


class SimpleParagraphTokenizer(ParagraphTokenizer):
    """Simple paragraph tokenizer that splits text into paragraphs based on newlines"""

    def __init__(self) -> None:
        super().__init__()

    # NOTE: This method is not handling case where paragraph does not start with a number or a number in paranthesis

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text into paragraphs based on newlines

        Args:
            text (str): Text to tokenize

        Returns:
            list[str]: List of paragraphs
        """
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
    """Paragraph tokenizer that uses NLTK to tokenize text into paragraphs"""

    def __init__(self) -> None:
        super().__init__()

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text into paragraphs using NLTK

        Args:
            text (str): Text to tokenize

        Returns:
            list[str]: List of paragraphs
        """
        paragraphs = nltk.sent_tokenize(text)
        paragraphs = [paragraph.replace('\n', ' ') for paragraph in paragraphs]
        return paragraphs


class TokenizerFactory:
    """Factory class for paragraph tokenizers"""

    @staticmethod
    def get_tokenizer(tokenizer: str) -> ParagraphTokenizer:
        """Get paragraph tokenizer based on the name

        Args:
            tokenizer (str): Name of the tokenizer

        Raises:
            ValueError: ValueError is raised if the tokenizer is invalid

        Returns:
            ParagraphTokenizer: Paragraph tokenizer
        """
        if tokenizer == "simple":
            return SimpleParagraphTokenizer()
        if tokenizer == "nltk":
            return NLTKParagraphTokenizer()
        raise ValueError("Invalid tokenizer")


if __name__ == '__main__':  # pragma: no cover
    pass
