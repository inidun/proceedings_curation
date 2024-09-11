import os

import pandas as pd
import pytest

from proceedings_curation.scripts.compare_excel import compare_excel


@pytest.fixture(name='old_excel')
def fixture_old_excel(tmpdir):
    # Create a temporary old Excel file
    old_data = {'Column1': ['A', 'B', 'C'], 'Column2': [1, 2, 3]}
    old_df = pd.DataFrame(old_data)
    old_path = os.path.join(tmpdir, 'old.xlsx')
    old_df.to_excel(old_path, index=False)
    return old_path


@pytest.fixture(name='new_excel')
def fixture_new_excel(tmpdir):
    # Create a temporary new Excel file
    new_data = {'Column1': ['A', 'B', 'D'], 'Column2': [1, 2, 4]}
    new_df = pd.DataFrame(new_data)
    new_path = os.path.join(tmpdir, 'new.xlsx')
    new_df.to_excel(new_path, index=False)
    return new_path


@pytest.fixture(name='new_excel_dropped_rows')
def fixture_new_excel_dropped_rows(tmpdir):
    # Create a temporary new Excel file with dropped rows
    new_data = {'Column1': ['A', 'B'], 'Column2': [1, 2]}
    new_df = pd.DataFrame(new_data)
    new_path = os.path.join(tmpdir, 'new_dropped_rows.xlsx')
    new_df.to_excel(new_path, index=False)
    return new_path


@pytest.fixture(name='new_excel_added_rows')
def fixture_new_excel_added_rows(tmpdir):
    # Create a temporary new Excel file with added rows
    new_data = {'Column1': ['A', 'B', 'C', 'D'], 'Column2': [1, 2, 3, 4]}
    new_df = pd.DataFrame(new_data)
    new_path = os.path.join(tmpdir, 'new_added_rows.xlsx')
    new_df.to_excel(new_path, index=False)
    return new_path


@pytest.fixture(name='report_path')
def fixture_report_path(tmpdir):
    # Create a temporary path for the report
    return os.path.join(tmpdir, 'report.xlsx')


@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_compare_excel(old_excel, new_excel, report_path):
    # Call the compare_excel function
    compare_excel(old_excel, new_excel, report_path)

    # Check if the report file is created
    assert os.path.exists(report_path)

    # Load the report file and check its content
    with pd.ExcelFile(report_path) as xls:
        assert 'changed' in xls.sheet_names
        assert 'diff' in xls.sheet_names
        assert 'added_rows' not in xls.sheet_names
        assert 'dropped_rows' not in xls.sheet_names

        changed_df = pd.read_excel(xls, sheet_name='changed')
        diff_df = pd.read_excel(xls, sheet_name='diff')

        # Check the content of the 'changed' sheet
        assert not changed_df.empty

        # Check the content of the 'diff' sheet
        assert not diff_df.empty
        assert 'Column1' in diff_df.columns
        assert 'Column2' in diff_df.columns
        assert 'C ---> D' in diff_df['Column1'].values
        assert '3 ---> 4' in diff_df['Column2'].values


@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_compare_excel_when_rows_dropped(old_excel, new_excel_dropped_rows, report_path):
    # Call the compare_excel function
    compare_excel(old_excel, new_excel_dropped_rows, report_path)

    # Check if the report file is created
    assert os.path.exists(report_path)

    # Load the report file and check its content
    with pd.ExcelFile(report_path) as xls:
        assert 'changed' in xls.sheet_names
        assert 'diff' in xls.sheet_names
        assert 'added_rows' not in xls.sheet_names
        assert 'dropped_rows' in xls.sheet_names

        changed_df = pd.read_excel(xls, sheet_name='changed')
        diff_df = pd.read_excel(xls, sheet_name='diff')
        dropped_rows_df = pd.read_excel(xls, sheet_name='dropped_rows')

        # Check the content of the 'changed' sheet
        assert not changed_df.empty

        # Check the content of the 'diff' sheet
        assert diff_df.empty

        # Check the content of the 'dropped_rows' sheet
        assert not dropped_rows_df.empty
        assert 'C' in dropped_rows_df['Column1'].values
        assert 3 in dropped_rows_df['Column2'].values


@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_compeare_excel_when_rows_added(old_excel, new_excel_added_rows, report_path):
    # Call the compare_excel function
    compare_excel(old_excel, new_excel_added_rows, report_path)

    # Check if the report file is created
    assert os.path.exists(report_path)

    # Load the report file and check its content
    with pd.ExcelFile(report_path) as xls:
        assert 'changed' in xls.sheet_names
        assert 'diff' in xls.sheet_names
        assert 'added_rows' in xls.sheet_names
        assert 'dropped_rows' not in xls.sheet_names

        changed_df = pd.read_excel(xls, sheet_name='changed')
        diff_df = pd.read_excel(xls, sheet_name='diff')
        added_rows_df = pd.read_excel(xls, sheet_name='added_rows')

        # Check the content of the 'changed' sheet
        assert not changed_df.empty

        # Check the content of the 'diff' sheet
        assert diff_df.empty

        # Check the content of the 'added_rows' sheet
        assert not added_rows_df.empty
        assert 'D' in added_rows_df['Column1'].values
        assert 4 in added_rows_df['Column2'].values
