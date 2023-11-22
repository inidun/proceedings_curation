from typing import Any
import pandas as pd
from loguru import logger
import typer
import xlsxwriter


def compare_excel(old: str, new: str, report: str) -> None:
    """Compare two excel sheets and create a diff sheet

    Args:
        old (str): Path to first sheet
        new (str): Path to second sheet
        report (str): Path to save report
    """

    old = pd.read_excel(old).fillna('NA')
    new = pd.read_excel(new).fillna('NA')

    dropped_rows = list(set(old.index) - set(new.index))
    dropped = old.loc[dropped_rows]
    logger.info('No rows dropped' if dropped.empty else f'Dropped {len(dropped)} row(s):\n{dropped}')

    added_rows = list(set(new.index) - set(old.index))
    added = new.loc[added_rows]
    logger.info('No rows added' if added.empty else f'Added {len(added)} row(s):\n{added}')

    changes = pd.concat([old, new], axis='columns', keys=['old', 'new'], join='inner')

    def report_diff(x: Any) -> str:
        """Function to report the difference between two cells of two columns

        Args:
            x (Any): Cell values

        Returns:
            str: Difference between two cells
        """
        return x.iloc[0] if x.iloc[0] == x.iloc[1] else f'{x.iloc[0]} ---> {x.iloc[1]}'

    changes = changes.swaplevel(axis='columns')[new.columns[0:]]
    changed = changes.groupby(level=0, axis='columns').apply(lambda frame: frame.apply(report_diff, axis='columns'))
    changed_text_columns = changed.select_dtypes(include='object')
    diff = changed_text_columns[changed_text_columns.apply(lambda x: x.str.contains('--->') == True, axis='columns')] # pylint: disable=singleton-comparison
    diff = diff.dropna(how='all').dropna(axis='columns', how='all')

    with pd.ExcelWriter(report, engine='xlsxwriter') as writer: # pylint: disable=abstract-class-instantiated
        changed = changed.reindex(columns=old.columns.to_list())  # Move
        changed.to_excel(writer, index=True, sheet_name='changed')
        diff.to_excel(writer, index=True, sheet_name='diff')
        if not added.empty:
            added.to_excel(writer, index=True, sheet_name='added_rows')
        if not dropped.empty:
            dropped.to_excel(writer, index=True, sheet_name='dropped_rows')

        highlight_style = {'font_color': '#ff0000', 'bg_color': '#ffffe0'}
        workbook = writer.book
        highligt_format = workbook.add_format(highlight_style)
        condition = {'type': 'text', 'criteria': 'containing', 'value': '--->', 'format': highligt_format}

        worksheet = writer.sheets['diff']
        rows = str(len(diff.index) + 1)
        # worksheet.hide_gridlines(2)
        worksheet.conditional_format(f'A1:ZZ{rows}', condition)

        writer.sheets['changed'].conditional_format(f'A1:ZZ{str(len(changed.index) + 1)}', condition)


if __name__ == '__main__':
    typer.run(compare_excel)

