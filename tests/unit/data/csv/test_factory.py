import csv
import string
import tempfile
from functools import partial
from pathlib import Path
from typing import Dict, Iterable, List, Union

import pytest
from hypothesis import given
from hypothesis.strategies import (
    DrawFn,
    composite,
    floats,
    integers,
    lists,
    sampled_from,
    text,
)
from shutterbug.data.csv.loader import CSVLoader
import shutterbug.data.csv.loader_factory as csv_factory
from shutterbug.data.header import KNOWN_HEADERS

CSV_COLUMN_TYPES = [floats, integers, partial(text, alphabet=string.printable)]


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


@composite
def pure_columns(
    draw: DrawFn, min_size: int = 0, max_size: int = None
) -> Union[Iterable[str], Iterable[float], Iterable[int]]:
    column_type = draw(sampled_from(CSV_COLUMN_TYPES))
    return draw(lists(column_type(), min_size=min_size, max_size=max_size))


@composite
def mixed_columns(
    draw: DrawFn, min_size: int = 0, max_size: int = None
) -> Union[Iterable[str], Iterable[float], Iterable[int]]:
    column_type = draw(lists(sampled_from(CSV_COLUMN_TYPES), min_size=1))
    size_used = 0
    result = []
    for sample in column_type:
        if size_used == max_size:
            break
        if max_size is not None:
            result.extend(
                draw(
                    lists(sample(), min_size=min_size, max_size=(max_size - size_used))
                )
            )
        else:
            result.extend(draw(lists(sample(), min_size=min_size, max_size=(max_size))))
            size_used += len(result)
    return result


@composite
def csvs(
    draw: DrawFn,
    csv_headers: List[str] = None,
    min_rows: int = 0,
    max_rows: int = 25,
    min_headers: int = 0,
    max_headers: int = 8,
):
    if csv_headers is None:
        csv_headers = draw(headers(min_size=min_headers, max_size=max_headers))
    num_rows = draw(integers(min_value=min_rows, max_value=max_rows))
    columns = []
    for _ in csv_headers:
        col_type = draw(sampled_from([mixed_columns, pure_columns]))
        col = draw(col_type(min_size=num_rows, max_size=num_rows))
        columns.append(col)
    csv_data = dict(zip(csv_headers, columns))
    return csv_data


@given(csvs())
def test_unknown_headers(csv_data: Dict):
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(csv_data.keys()))
        writer.writeheader()
        writer.writerows([csv_data])
        file_path = Path(csv_file.name)

        with pytest.raises(ValueError):
            csv_factory.make_loader(file_path)


@given(csvs(csv_headers=KNOWN_HEADERS[0].headers, min_rows=1))
def test_known_headers(csv_data: Dict):
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="rt+", newline="") as csv_file:
        known_header = KNOWN_HEADERS[0]
        fieldnames = list(csv_data.keys())
        file_path = Path(csv_file.name)
        with file_path.open(mode="rt+") as f:
            writer = csv.DictWriter(f, dialect="excel", fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([csv_data])
        assert csv_factory._read_file_header(file_path) == known_header.headers
        assert csv_factory._headers_from_file(file_path) == known_header
        assert isinstance(csv_factory.make_loader(file_path), CSVLoader)
