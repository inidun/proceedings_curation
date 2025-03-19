# pylint: disable=anomalous-backslash-in-string
import zipfile

import typer
from loguru import logger
from nltk.tokenize import regexp_tokenize, word_tokenize


def get_fileinfo(
    input_file: str, language: str = 'english', re_pattern: str = r'\w+|[^\w\s]+'
) -> list[dict[str, object]]:
    """Calculate the number of words in a zipped corpus file. The function reads the text files in the zipped corpus file
    and calculates the number of words using the NLTK word_tokenize and regexp_tokenize functions. The function returns a
    list of dictionaries with the filename, number of words using word_tokenize, number of words using regexp_tokenize,
    and the filesize (in bytes) of the text file.

    Args:
        input_file (str): Path to the zipped corpus file
        language (str, optional): Language of the text. Defaults to 'english'.
        re_pattern (str, optional): Regular expression pattern for tokenization. Defaults to r'\w+|[^\w\s]+'.

    Returns:
        list[dict[str, object]]: List of dictionaries with the filename, number of words using word_tokenize, number of
        words using regexp_tokenize, and the filesize (in bytes) of the text file.
    """
    logger.info(f'Reading file: {input_file}. Using language: {language}. Regular expression pattern: {re_pattern}')

    data = []
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        for filename in zip_ref.namelist():
            filesize = zip_ref.getinfo(filename).file_size
            with zip_ref.open(filename) as file:
                text = file.read().decode('utf-8')
                tokens_wc = word_tokenize(text, language=language, preserve_line=False)
                tokens_re = regexp_tokenize(text, pattern=re_pattern)
                data.append(
                    {
                        'filename': filename,
                        'tokens_wc': len(tokens_wc),
                        'tokens_re': len(tokens_re),
                        'filesize': filesize,
                    }
                )
    return data


def export_csv(data: list[dict[str, object]], output_file: str) -> None:
    """Export the data to a CSV file.

    Args:
        data (list[dict[str, object]]): List of dictionaries with the filename, number of words using word_tokenize,
        number of words using regexp_tokenize, and the filesize (in bytes) of the text file.
        output_file (str): Path to the output CSV file.
    """
    with open(output_file, 'w', encoding="utf-8") as f:
        f.write('filename,tokens_wc,tokens_re,filesize\n')
        for row in data:
            f.write(f"{row['filename']},{row['tokens_wc']},{row['tokens_re']},{row['filesize']}\n")
    print(f'File saved to {output_file}')


def main(input_file: str, output_file: str, language: str = 'english', re_pattern: str = r'\w+|[^\w\s]+') -> None:
    """Calculate the number of words in a zipped corpus file and export the data to a CSV file.

    Args:
        input_file (str): Path to the zipped corpus file
        output_file (str): Path to the output CSV file
        language (str, optional): Language of the text. Defaults to 'english'.
        re_pattern (str, optional): Regular expression pattern for tokenization. Defaults to r'\w+|[^\w\s]+'.
    """
    data = get_fileinfo(input_file, language, re_pattern)
    export_csv(data, output_file)


if __name__ == "__main__":  # pragma: no cover
    typer.run(main)
