from typing import Iterable, List

import pytest
from hypothesis import given
from hypothesis.strategies import lists
from shutterbug.data.core.star import Star, StarTimeseries
from shutterbug.data.storage.db.model import Base, StarDB, StarDBTimeseries
from shutterbug.data.storage.db.writer import DBWriter
from tests.unit.data.db.db_test_tools import sqlalchemy_session
from tests.unit.data.hypothesis_stars import stars


def reconstruct_star_from_db(star: StarDB, timeseries: List[StarDBTimeseries]) -> Star:
    rec_star = Star(name=star.name, dataset=star.dataset, x=star.x, y=star.y)
    db_time = []
    db_mag = []
    db_error = []
    for row in timeseries:
        db_time.append(row.time)
        db_mag.append(row.mag)
        db_error.append(row.error)
    rec_timeseries = StarTimeseries(time=db_time, mag=db_mag, error=db_error)
    rec_star.data = rec_timeseries
    return rec_star


@given(stars())
def test_convert(star: Star):
    star_db, star_db_timeseries = DBWriter._convert_to_model(star)
    reconstructed_star = reconstruct_star_from_db(star_db, star_db_timeseries)
    assert star == reconstructed_star


@given(lists(stars(), unique_by=(lambda x: x.name), min_size=1))
def test_write(stars: Iterable[Star]):
    with sqlalchemy_session() as db:
        engine, sess = db
        writer = DBWriter(engine)
        # write in
        for star in stars:
            writer.write(star)
        # read out and assert
        for star in sess.query(StarDB).all():
            rec_star = reconstruct_star_from_db(star)
            assert rec_star in stars
