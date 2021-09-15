from pathlib import Path
from sys import path
from tests.unit.loader.conftest import existing_file, existing_file_list, existing_dir
import pandas as pd
import xarray as xr
import pytest
from pandas.errors import EmptyDataError

from shutterbug.file_loader.loader import (
    _suffix_to_loader,
    _is_accepted_format,
    _filter_unreadable_paths,
    _get_files_from_paths,
    _load_from_suffix,
    iload,
    load,
    get_readable_file_count,
)

_suffix_to_error = {
    ".xlsx": ValueError,
    ".xls": ValueError,
    ".xlsm": ValueError,
    ".odf": ValueError,
    ".ods": ValueError,
    ".csv": EmptyDataError,
    ".parquet": ValueError,
    ".hd5": ValueError,
    ".nc": ValueError,
}


@pytest.fixture
def files_with_good_count(existing_file_list):
    count = len(
        list(filter(lambda x: x.suffix in _suffix_to_loader.keys(), existing_file_list))
    )
    yield count, existing_file_list


def test_accepted_formats(existing_file: Path):
    if existing_file.suffix in _suffix_to_loader.keys():
        assert _is_accepted_format(existing_file) is True
    else:
        assert _is_accepted_format(existing_file) is False


def test_filter_unreadable_paths(files_with_good_count):
    test_count, test_files = files_with_good_count
    filtered_files = list(_filter_unreadable_paths(test_files))
    filtered_count = len(filtered_files)
    assert test_count == filtered_count


def test_get_file_count(files_with_good_count):
    test_count, test_files = files_with_good_count
    filtered_count = get_readable_file_count(test_files)
    assert test_count == filtered_count


def test_files_from_paths(existing_file_list):
    flat_files = _get_files_from_paths(existing_file_list)
    # all are present
    assert all(map(lambda x: x in existing_file_list, flat_files))
    # all are existing files
    assert all(map(lambda x: x.is_file(), flat_files))


def test_files_from_dir(existing_dir):
    flat_files = _get_files_from_paths([existing_dir])
    assert len(flat_files) == 0


# Testing errors since we don't care about Pandas or Xarray code
def test_load_from_suffix(existing_file: Path):
    if existing_file.suffix in _suffix_to_loader.keys():
        with pytest.raises(_suffix_to_error[existing_file.suffix]):
            _load_from_suffix(existing_file)


@pytest.mark.parametrize("as_type", (("pandas", "xarray")))
def test_load(existing_file: Path, as_type):
    if existing_file.suffix in _suffix_to_loader.keys():
        with pytest.raises(_suffix_to_error[existing_file.suffix]):
            load(existing_file, as_type)
    else:
        with pytest.raises(ValueError):
            load(existing_file, as_type)


def test_iload(files_with_good_count):
    test_count, test_files = files_with_good_count
    i = 0
    with pytest.raises(ValueError):
        for error in iload(test_files):
            i += 1
        assert i == test_count


def test_iload_empty(existing_dir):
    with pytest.raises(ValueError):
        print(iload([existing_dir], "pandas").__next__())
