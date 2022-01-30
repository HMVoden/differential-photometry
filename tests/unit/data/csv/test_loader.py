from pathlib import Path
from typing import Any, Dict
from shutterbug.data.csv.loader import CSVLoader
from shutterbug.data.header import KnownHeader
from shutterbug.data.star import Star
from tests.unit.data.hypothesis_stars import star, stars
import pytest
import string
from hypothesis import given
from hypothesis.strategies import composite, DrawFn
import tempfile
import numpy as np
import csv


def star_to_dict(star: Star) -> Dict[str, Any]:
    size = len(star.timeseries.time)
    names = np.repeat(star.name, size)
    xs = np.repeat(star.x, size)
    ys = np.repeat(star.y, size)

    return {
        "name": names,
        "x": xs,
        "y": ys,
        "jd": star.timeseries.time,
        "mag": star.timeseries.mag,
        "error": star.timeseries.error,
    }


@composite
def star_csv(
    draw: DrawFn,
    min_size=0,
    max_size=None,
):
    random_stars = draw(
        stars(
            alphabet=string.printable,
            min_size=min_size,
            max_size=max_size,
            allow_nan=False,
        )
    )
    as_dict = list(map(star_to_dict, random_stars))
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="rt+", newline="") as csv_file:
        fieldnames = list(as_dict[0].keys())
        with Path(csv_file.name).open(mode="rt+") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(as_dict)
        header = KnownHeader(
            headers=fieldnames,
            header_origin="Test",
            timeseries_names=["jd", "mag", "error"],
            star_data=["name", "x", "y"],
            star_name="name",
        )

        yield [Path(csv_file.name), header, len(as_dict), stars]


@given(star_csv(min_size=1))
def test_csv_loader(data_list):
    path, headers, length, stars = next(data_list)
    loader = CSVLoader(path, headers)
    # must have as many stars in loader as were loaded
    assert len(loader) == length
    # All names must be present
    assert all([True if x in stars else False for x in loader])
