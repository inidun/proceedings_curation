import os
from datetime import datetime
from pathlib import Path

import argh
import pandas as pd
from argh import arg
from loguru import logger
from pdf_extract.interface import ITextExtractor

from proceedings_curation.pdfbox_extractor_modified import PDFBoxExtractorMod
from proceedings_curation.tesseract_extractor_modified import TesseractExtractorMod


def extract_meetings(  # pylint: disable=redefined-outer-name
    index: pd.DataFrame,
    input_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    extractor: ITextExtractor,
    page_numbers: bool = False,
    page_sep: str = '',
    force: bool = False,
) -> None:
    """Extract text from PDF files

    Args:
        index (pd.DataFrame): Metadata index
        input_path (str | os.PathLike): Path to PDF files
        output_path (str | os.PathLike): Path to save extracted text
        extractor (ITextExtractor): PDF text extractor
        page_numbers (bool, optional): Extract page numbers. Defaults to False.
        page_sep (str, optional): Page separator. Defaults to ''.
        force (bool, optional): Force overwrite existing files. Defaults to False.
    """

    Path(output_path).mkdir(parents=True, exist_ok=True)

    for i, row in index.iterrows():
        year: int = row.conference_date if row.date_meeting is pd.NaT else row.date_meeting.year
        output_filename: str = f"{year}_{i}_{'_'.join(row.title_meeting.split()[:3]).lower()}.txt"

        if isinstance(extractor, TesseractExtractorMod):
            extractor.language = row.language_codes
            logger.info(f"Using Tesseract with language {row.language_codes} for {row.filename}")

        extractor.extract_text(
            filename=Path(input_path / row.filename),
            output_folder=output_path,
            first_page=row.first_page,
            last_page=row.last_page,
            page_numbers=page_numbers,
            page_sep=page_sep,
            output_filename=output_filename,
            force=force,
        )


@arg(
    '-e',
    '--extractor',
    choices=[
        'pdfbox',
        'tesseract',
    ],
    default='pdfbox',
)
def main(
    metadata_index: str | os.PathLike[str],
    input_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    *,
    extractor: str = 'pdfbox',
    page_numbers: bool = False,
    page_sep: str = '',
    force: bool = False,
) -> None:
    """Extract text from PDF files

    Args:
        proceedings_index (str | os.PathLike): Path to proceedings index
        metadata_index (str | os.PathLike): Path to metadata index
        input_path (str | os.PathLike): Path to PDF files
        output_path (str | os.PathLike): Path to save extracted text
        page_numbers (bool, optional): Extract page numbers. Defaults to False.
        page_sep (str, optional): Page separator. Defaults to ''.
        force (bool, optional): Force overwrite existing files. Defaults to False.

    Raises:
        FileNotFoundError: If any file in the index is not found in the input path
    """

    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    logfile = logger.add(
        output_path / f"extract_{datetime.now().isoformat(timespec='seconds').replace(':', '')}.log",
        format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}',
    )

    index = load_index(metadata_index)

    check_source_files(input_path, index)

    extractor = TesseractExtractorMod() if extractor == 'tesseract' else PDFBoxExtractorMod()
    extract_meetings(index, input_path, output_path, extractor, page_numbers, page_sep, force)

    logger.remove(logfile)


def check_source_files(input_path: str | os.PathLike[str], metadata_index: pd.DataFrame) -> None:
    if len(missing := {file for file in metadata_index.filename.unique() if not (input_path / file).is_file()}) > 0:
        logger.warning(f"{len(missing)} missing source files in {input_path}: {', '.join(missing)}")
    else:
        logger.info(f'Found all source files in {input_path}')


def load_index(metadata_index: str | os.PathLike[str]) -> pd.DataFrame:
    logger.info('Loading index')
    index = pd.read_excel(
        metadata_index,
        index_col='meeting_id',
        dtype={
            'record_number': 'uint32',
            'publication_date': 'uint16',
            'conference_date': 'uint16',
            'columns': 'uint8',
            'first_page': 'uint16',
            'last_page': 'uint16',
        },
    )

    return index


if __name__ == '__main__':  # pragma: no cover
    argh.dispatch_command(main)
