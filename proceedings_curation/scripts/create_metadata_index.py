import os

import pandas as pd
import typer
from loguru import logger


def create_metadata_index(
    proceedings_index: str | os.PathLike, proceedings_metadata: str | os.PathLike
) -> pd.DataFrame:
    """Create metadata index by merging and updating `proceedings_index` and `proceedings_metadata`

    Args:
        proceedings_index (str | os.PathLike): Path to proceedings index
        proceedings_metadata (str | os.PathLike): Path to proceedings metadata

    Returns:
        pd.DataFrame: Merged and updated index of `proceedings_index` and `proceedings_metadata`
    """

    # Load proceedings index
    logger.info(f'Loading proceedings index: "{proceedings_index}"')
    idxp = pd.read_excel(
        proceedings_index,
        dtype={
            'Record number': 'uint32',
            'Publication date': 'uint16',
            'Conference date ': 'Int64',
            'Volume': 'Int64',
            'Chapter': 'category',
        },
    )

    # Strip and lowercase column names
    idxp.columns = idxp.columns.str.strip().str.replace(' ', '_').str.lower()

    # Date to datetime
    idxp['date_meeting'] = pd.to_datetime(idxp['date_meeting'], errors='coerce')
    if nat := idxp['date_meeting'].isnull().sum():
        logger.error(
            f"{nat} errors in Proceedings index, 'Date meeting' column\n{idxp[idxp['date_meeting'].isnull()][['record_number', 'title_meeting', 'date_meeting']]}"
        )

    # Check if meeting dates are within conference date range
    if len(
        invalid_dates := idxp.query(
            'date_meeting.dt.year < conference_date.min() | date_meeting.dt.year > conference_date.max()'
        )
    ):
        logger.error(f"Dates out of range\n{invalid_dates[['record_number', 'title_meeting', 'date_meeting']]}")

    # Load proceedings metadata
    logger.info(f'Loading proceedings metadata: "{proceedings_metadata}"')
    idxm = pd.read_excel(
        proceedings_metadata,
        usecols=['record_number', 'year', 'filename', 'columns'],
        dtype={'record_number': 'uint32', 'year': 'uint16', 'columns': 'uint8'},
    )
    idxm['filename'] = idxm['year'].astype(str) + '_' + idxm['filename'].astype(str) + '.pdf'
    idxm.drop(['year'], axis='columns', inplace=True)

    # Merge proceedings index and proceedings metadata
    logger.info('Merging proceedings index and proceedings metadata')
    idx = idxp.merge(idxm.set_index('record_number'), how='left', left_on='record_number', right_index=True)
    # fmt: off
    idx['meeting_name_id'] = idx['record_number'].astype(str) + '_' + idx['title_meeting'].str.replace(' ', '_').str.lower()
    idx['meeting_id'] = idx['record_number'].astype(str) + idx.groupby(['record_number']).cumcount().astype(str).str.pad(4, side='left', fillchar='0')
    # fmt: on

    idx['meeting_id'] = idx['meeting_id'].astype(int)

    idx['pages'] = idx['pages_in_pdf'].astype(str).str.strip().str.rstrip('-')  # NOTE: Errors in index: trailing '-'
    idx['pages'] = idx['pages'].str.split('-').str.get(0) + '-' + idx['pages'].str.split('-').str.get(-1)
    if idx['pages'].isnull().sum() > 0:
        logger.warning("Null values in 'pages' column")
    idx[['first_page', 'last_page']] = idx['pages'].str.split('-', n=1, expand=True).astype('uint16')

    idx['language_codes'] = (
        idx.languages.str.replace('|', ' ')
        .str.strip()
        .str.split()
        .map(lambda x: [y for y in x if not y in ['mul', 'qaa']])
        .str.join('+')
    )

    idx.set_index('meeting_id', inplace=True, drop=True)
    logger.info(f'Created index ({idx.shape[0]} rows)')
    return idx


def save_metadata_index(idx: pd.DataFrame, filename: str | os.PathLike) -> None:
    """Save metadata index as Excel or CSV

    Args:
        idx (pd.DataFrame): Metadata index
        filename (str | os.PathLike): Path to save index
    """
    logger.info(f'Saving index: "{filename}"')
    if str(filename).endswith('.csv'):
        idx.to_csv(filename, sep=';', encoding='utf-8-sig')
    else:
        idx.to_excel(filename)
    logger.info(f'Saved index: "{filename}"')


def main(proceedings_index: str, proceedings_metadata: str, filename: str) -> None:
    """Create metadata index by merging and updating `proceedings_index` and `proceedings_metadata`

    Args:
        proceedings_index (str | os.PathLike): Path to proceedings index
        metadata_index (str | os.PathLike): Path to proceedings metadata
        filename (str | os.PathLike): Path to save metadata index
    """
    idx = create_metadata_index(proceedings_index, proceedings_metadata)
    save_metadata_index(idx, filename)


if __name__ == '__main__':
    typer.run(main)
