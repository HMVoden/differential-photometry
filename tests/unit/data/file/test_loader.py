from pathlib import Path

import pytest
from hypothesis import given
from hypothesis.strategies import lists, text
from pandas.errors import EmptyDataError
from shutterbug.data.file.loader import (READABLE_TYPES, _clean_headers,
                                         _filter_unreadable_paths,
                                         _get_files_from_paths,
                                         _is_accepted_format,
                                         get_readable_file_count, load)
from tests.unit.loader.conftest import (existing_dir, existing_file,
                                        existing_file_list, useable_filename)


@pytest.fixture
def files_with_good_count(existing_file_list):
    count = len(list(filter(lambda x: x.suffix in READABLE_TYPES, existing_file_list)))
    yield count, existing_file_list


def test_accepted_formats(existing_file: Path):
    if existing_file.suffix in READABLE_TYPES:
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


@given(lists(text()))
def test_clean_headers(headers):
    cleaned = _clean_headers(headers)
    for item in cleaned:
        assert not item.endswith(("\t", " "))
        assert not item.startswith(("\t", " "))
