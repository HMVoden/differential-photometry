from typing import List

import numpy as np
import pytest
from hypothesis import given
from hypothesis.strategies import lists
from hypothesis.strategies._internal.numbers import integers
from shutterbug.data.star import Star
from shutterbug.data.db.reader import DBReader
from shutterbug.data.db.writer import DBWriter
from tests.unit.data.db.db_test_tools import sqlalchemy_db, sqlite_memory
from tests.unit.data.hypothesis_stars import star, stars
import string


@given(
    stars(alphabet=string.printable, dataset="test", min_size=1),
    stars(alphabet=string.printable, dataset="other", min_size=1, max_size=1),
)
def test_init(stars, other):
    with sqlite_memory() as engine:
        writer = DBWriter(engine)
        star_names = []
        for star in stars:
            writer.write(star)
            star_names.append(star.name)
        for star in other:
            writer.write(star)
        reader = DBReader(dataset="test", engine=engine, mag_limit=0, distance_limit=0)

        assert all([True if x in reader._stars else False for x in star_names])
        assert len(reader._stars) == len(stars)


@given(
    stars(alphabet=string.printable, dataset="test", min_size=1),
    stars(alphabet=string.printable, dataset="other", min_size=1, max_size=1),
)
def test_reads_all(stars: List[Star], other: List[Star]):
    with sqlite_memory(future=False) as engine:
        writer = DBWriter(engine)
        # load DB for reading
        star_names = []
        for star in stars:
            writer.write(star)
            # we're just going to make sure that the names are there
            star_names.append(star.name)
        for star in other:
            # so we can make sure we're only getting from our dataset
            writer.write(star)

        reader = DBReader(dataset="test", engine=engine, mag_limit=0, distance_limit=0)
        read_names = []
        datasets = []
        for star in reader.all:
            read_names.append(star.index.levels[0][0])
            datasets.append(star["dataset"][0])
        star_set = set(star_names)
        read_set = set(read_names)
        assert star_set == read_set
        assert len(set(datasets)) == 1
        assert len(star_set) == len(stars)


@given(
    stars(alphabet=string.printable, min_size=2, dataset="test"),
    integers(min_value=0, max_value=5),
    integers(min_value=0, max_value=400),
)
def test_similar_to(stars: List[Star], mag_limit, distance_limit):
    if mag_limit == 0:
        mag_limit = np.inf
    if distance_limit == 0:
        distance_limit = np.inf
    with sqlite_memory(future=False) as engine:
        writer = DBWriter(engine)
        target = stars[0]
        target_median = np.nanmedian(target.data.mag)
        for star in stars:
            writer.write(star)

        similar_stars = []
        for star in stars[1:]:
            abs_diff_median = abs(np.nanmedian(star.data.mag) - target_median)
            distance_between = np.sqrt(
                (star.x - target.x) ** 2 + (star.y - target.y) ** 2
            )
            if abs_diff_median <= mag_limit and distance_between <= distance_limit:
                similar_stars.append(star.name)

        reader = DBReader(
            dataset="test",
            engine=engine,
            mag_limit=mag_limit,
            distance_limit=distance_limit,
        )
        similar_stars_frame = reader.similar_to(target.name)
        db_similar = np.unique(similar_stars_frame.index.levels[0])
        assert set(db_similar) == set(similar_stars)
