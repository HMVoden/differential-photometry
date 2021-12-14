import string
from pathlib import Path
from typing import List

import pytest
from hypothesis import given
from hypothesis.strategies import DrawFn, composite, lists, text
from pandas.errors import EmptyDataError
from shutterbug.data.input.csv.loader import CSVLoader
from tests.unit.loader.conftest import (existing_dir, existing_file,
                                        existing_file_list, useable_filename)


@composite
def headers(draw: DrawFn, min_size: int = 0, max_size: int = None) -> List[str]:
    return draw(
        lists(
            text(alphabet=string.printable),
            unique=True,
            min_size=min_size,
            max_size=max_size,
        )
    )


@pytest.fixture
def files_with_good_count(existing_file_list):
    count = len(list(filter(lambda x: x.suffix in READABLE_TYPES, existing_file_list)))
    yield count, existing_file_list


def test_accepted_formats(existing_file: Path):
    if existing_file.suffix in CSVLoader.READABLE_TYPES:
        assert CSVLoader.is_readable(existing_file) is True
    else:
        assert CSVLoader.is_readable(existing_file) is False


@given(lists(text()))
def test_clean_headers(headers):
    cleaned = _clean_headers(headers)
    for item in cleaned:
        assert not item.endswith(("\t", " "))
        assert not item.startswith(("\t", " "))
