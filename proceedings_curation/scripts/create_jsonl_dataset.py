import os
import re
from typing import Optional

import jsonlines
import pandas as pd
import typer
from dotenv import load_dotenv
from loguru import logger
from typing_extensions import Annotated

load_dotenv()


def create_jsonl_dataset(
    metadata_index: str,
    input_path: str,
    output_path: str,
    dataset_name: Annotated[Optional[str], typer.Argument()] = 'dataset',
    number_of_files: Annotated[Optional[int], typer.Argument()] = None,
    tokens_per_file: Annotated[Optional[int], typer.Argument()] = None,
) -> None:
    """Create a JSONL dataset from a folder of text files using a metadata index. Create a sample of the dataset by specifying the number of files to include and the number of tokens to keep per file.

    The metadata index is a CSV file with the following columns:
    - filename: Name of the PDF file
    - title_meeting: Title of the meeting
    - date_meeting: Date of the meeting
    - conference_date: Year of the meeting
    - language_codes: Language of the meeting
    - first_page: First page of the meeting
    - last_page: Last page of the meeting

    The text files are named using the following convention:
    - {conference_date}_{index}_{title_meeting}.txt

    The JSONL dataset is a file where each line is a JSON object with the following
    keys:
    - text: Text of the meeting
    - meta: a dictionary with the following keys:
        - file: Name of the text file
        - title: Title of the meeting
        - date: Date of the meeting
        - source: {BASE_URL}/{filename}#page={first_page} (where BASE_URL is defined in environment variables)

    Args:
        metadata_index (str): Path to the metadata index
        input_path (str): Path to the folder of text files
        output_path (str): Output path for the JSONL dataset
        dataset_name (str, optional): Name of the dataset. Defaults to 'dataset'.
        number_of_files (int, optional): Number of files to sample. Defaults to None.
        tokens_per_file (int, optional): Number of tokens to keep per file. Defaults to None.
    """
    # Load metadata index
    index = pd.read_csv(
        metadata_index,
        parse_dates=['date_meeting'],
        index_col=0,
        keep_default_na=False,
        na_values='',
        encoding='utf-8-sig',
        sep=';',
    )

    # Create output folder
    os.makedirs(output_path, exist_ok=True)

    # Create JSONL dataset
    with jsonlines.open(os.path.join(output_path, f'{dataset_name}.jsonl'), 'w') as writer:
        if number_of_files is not None:
            index = index.sample(n=number_of_files)
        for i, row in index.iterrows():
            year = row.conference_date if not pd.isna(row.date_meeting) else row.date_meeting.year
            filename = f"{year}_{i}_{'_'.join(row.title_meeting.split()[:3]).lower()}.txt"
            if not os.path.exists(os.path.join(input_path, filename)):
                logger.error(f"File {filename} not found")
                continue
            with open(os.path.join(input_path, filename), 'r', encoding='utf-8') as file:
                text = file.read()
                text = remove_unusual_line_terminators(text)
                if tokens_per_file is not None:
                    text = ' '.join(text.split()[:tokens_per_file])
            meta = {
                'file': filename,
                'title': row.title_meeting,
                'date': row.date_meeting.strftime('%Y-%m-%d') if not pd.isna(row.date_meeting) else None,
                'source': f"{os.getenv('BASE_URL')}{row.filename}#page={row.first_page}",
            }
            writer.write({'text': text, 'meta': meta})


def remove_unusual_line_terminators(text: str) -> str:
    """Remove unusual line terminators from a string including U+0085 Next Line, U+2028 Line Separator, and U+2029 Paragraph Separator

    Args:
        text (str): The string to clean

    Returns:
        str: The string with unusual line terminators removed
    """
    pattern = re.compile(r'[\x00-\x08\x0E-\x1F\u0085\u2028\u2029]')
    cleaned_text = pattern.sub('', text)
    return cleaned_text


if __name__ == "__main__":
    typer.run(create_jsonl_dataset)
