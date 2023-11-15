import os
import pandas as pd

from loguru import logger
import typer


def create_metadata_index(proceedings_index: str | os.PathLike, metadata_index: str | os.PathLike) -> pd.DataFrame:
    """Combine and update proceedings and metadata indexes

    Args:
        proceedings_index (str | os.PathLike): Path to proceedings index
        metadata_index (str | os.PathLike): Path to metadata index

    Returns:
        pd.DataFrame: Combined and updated index of proceedings and metadata
    """

    # Load proceedings index
    logger.info(f'Loading Proceedings index: "{proceedings_index}"')
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

    # Load metadata index
    logger.info(f'Loading Metadata index: "{metadata_index}"')
    idxm = pd.read_excel(
        metadata_index,
        usecols=['record_number', 'year', 'filename', 'columns'],
        dtype={'record_number': 'uint32', 'year': 'uint16', 'columns': 'uint8'},
    )
    idxm['filename'] = idxm['year'].astype(str) + '_' + idxm['filename'].astype(str) + '.pdf'
    idxm.drop(['year'], axis='columns', inplace=True)

    # Merge proceedings and metadate indexes
    logger.info('Merging Proceedings and Metadata indexes')
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


def main(proceedings_index: str, metadata_index: str, filename: str) -> None:
    """Combine and update proceedings and metadata indexes

    Args:
        proceedings_index (str | os.PathLike): Path to proceedings index
        metadata_index (str | os.PathLike): Path to metadata index
        filename (str | os.PathLike): Path to save index
    """
    idx = create_metadata_index(proceedings_index, metadata_index)
    save_metadata_index(idx, filename)

if __name__ == '__main__':
    typer.run(main)
