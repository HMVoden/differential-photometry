import string
from typing import List

import numpy as np
from hypothesis import given
from hypothesis.strategies._internal.numbers import integers
from shutterbug.data.db.reader import DBReader
from shutterbug.data.db.writer import DBWriter
from shutterbug.data.star import Star
from tests.unit.data.db.db_test_tools import sqlite_memory
from tests.unit.data.hypothesis_stars import star, stars


@given(star())
def test_convert_to_star(star: Star):
    with sqlite_memory(future=True) as session:
        DBWriter(session=session, dataset="test").write(star)
        reader = DBReader(dataset="test", session=session)
        read_star = next(reader.__iter__())
        print(read_star)
        assert read_star == star


@given(
    stars(alphabet=string.printable, min_size=1),
    stars(alphabet=string.printable, min_size=1, max_size=1),
)
def test_names(stars: List[Star], other: List[Star]):
    with sqlite_memory() as session:
        test_writer = DBWriter(dataset="test", session=session)

        other_writer = DBWriter(dataset="other", session=session)
        star_names = []
        for star in stars:
            test_writer.write(star)
            star_names.append(star.name)
        for star in other:
            other_writer.write(star)
        reader = DBReader(
            dataset="test", session=session, mag_limit=0, distance_limit=0
        )
        assert all([True if x in reader.names else False for x in star_names])
        assert len(reader.names) == len(stars)


@given(
    stars(alphabet=string.printable, min_size=1, max_size=3),
    stars(alphabet=string.printable, min_size=1, max_size=1),
)
def test_multiple_dataset(stars: List[Star], other: List[Star]):
    with sqlite_memory() as session:
        test_writer = DBWriter(dataset="test", session=session)
        other_writer = DBWriter(dataset="other", session=session)
        # load DB for reading
        star_names = []
        for star in stars:
            test_writer.write(star)
            # we're just going to make sure that the names are there
            star_names.append(star.name)
        for star in other:
            # so we can make sure we're only getting from our dataset
            other_writer.write(star)

        reader = DBReader(
            dataset="test", session=session, mag_limit=0, distance_limit=0
        )
        read_names = []
        for star in reader:
            read_names.append(star.name)
        star_set = set(star_names)
        read_set = set(read_names)
        assert star_set == read_set
        assert len(star_set) == len(stars)


@given(
    stars(alphabet=string.printable, min_size=2),
    integers(min_value=1, max_value=5),
    integers(min_value=1, max_value=400),
)
def test_similar_to(stars: List[Star], mag_limit, distance_limit):
    with sqlite_memory(future=False) as session:
        writer = DBWriter(dataset="test", session=session)
        target = stars[0]
        target_median = target.timeseries.magnitude.median()
        for star in stars:
            writer.write(star)

        similar_stars = []
        for star in stars[1:]:
            abs_diff_median = abs(star.timeseries.magnitude.median() - target_median)
            distance_between = np.sqrt(
                (star.x - target.x) ** 2 + (star.y - target.y) ** 2
            )
            if (
                abs_diff_median <= mag_limit
                and distance_between <= distance_limit
                and star.variable == False
            ):
                similar_stars.append(star.name)

        reader = DBReader(
            dataset="test",
            session=session,
            mag_limit=mag_limit,
            distance_limit=distance_limit,
        )
        db_similar = set(map(lambda x: x, reader.similar_to(target)))
        assert all(
            [
                True if x in reader.names else False
                for x in reader._star_cache[target.name]
            ]
        )
        assert db_similar == set(similar_stars)


@given(star())
def test_feature_update(star: Star):
    with sqlite_memory(future=True) as session:
        writer = DBWriter(dataset="test", session=session)
        reader = DBReader(dataset="test", session=session)

        writer.write(star)
        for date in star.timeseries.features:
            star.timeseries.add_feature(
                dt=date, name="Inverse Von Neumann", value=123.0
            )
            star.timeseries.add_feature(dt=date, name="IQR", value=567.0)
        writer.update(star)
        read_star = next(reader.__iter__())
        assert read_star.variable == star.variable
        assert len(star.timeseries.features) == len(read_star.timeseries.features)
        for date in star.timeseries.features.keys():
            assert date in read_star.timeseries.features.keys()
            assert read_star.timeseries.features[date]["Inverse Von Neumann"] == 123.0
            assert read_star.timeseries.features[date]["IQR"] == 567.0

        assert (
            read_star.timeseries.differential_error.array == star.timeseries.error.array
        )

        assert (
            read_star.timeseries.differential_magnitude.array
            == star.timeseries.magnitude.array
        )


@given(star())
def test_variable_update_read(star: Star):
    with sqlite_memory(future=True) as session:
        writer = DBWriter(dataset="test", session=session)
        reader = DBReader(dataset="test", session=session)

        writer.write(star)
        for date in star.timeseries.features:
            star.timeseries.add_feature(
                dt=date, name="Inverse Von Neumann", value=123.0
            )
            star.timeseries.add_feature(dt=date, name="IQR", value=567.0)
        star.timeseries.differential_error = star.timeseries.error
        star.timeseries.differential_magnitude = star.timeseries.magnitude
        star.variable = True
        writer.update(star)
        read_star = next(reader.variable)
        assert read_star.variable == star.variable
        assert len(star.timeseries.features) == len(read_star.timeseries.features)
        for date in star.timeseries.features.keys():
            assert date in read_star.timeseries.features.keys()
            assert read_star.timeseries.features[date]["Inverse Von Neumann"] == 123.0
            assert read_star.timeseries.features[date]["IQR"] == 567.0

        assert (
            read_star.timeseries.differential_error.array == star.timeseries.error.array
        )

        assert (
            read_star.timeseries.differential_magnitude.array
            == star.timeseries.magnitude.array
        )
