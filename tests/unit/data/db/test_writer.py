import string
from math import isclose
from typing import List

from hypothesis import given
from shutterbug.data.db.model import StarDB, StarDBDataset
from shutterbug.data.db.writer import DBWriter
from shutterbug.data.star import Star
from sqlalchemy import bindparam, select
from sqlalchemy.orm import Session
from tests.unit.data.db.db_test_tools import sqlite_memory
from tests.unit.data.hypothesis_stars import star, stars


@given(star(allow_nan=False))
def test_convert(star: Star):
    with sqlite_memory() as session:
        star_db = DBWriter(dataset="test", session=session)._convert_to_model(star)
        assert len(star_db.timeseries) == len(star.timeseries.magnitude)
        assert len(star_db.timeseries) == len(star.timeseries.error)
        assert len(star_db.timeseries) == len(star.timeseries.data.index.array)
        assert star_db.x == star.x
        assert star_db.y == star.y
        assert star_db.magnitude_median == star.timeseries.magnitude.median()
        assert len(star_db.features) == len(star.timeseries.features)


@given(stars(alphabet=string.printable, min_size=1, max_size=3, allow_nan=False))
def test_write(stars: List[Star]):
    with sqlite_memory() as session:
        writer = DBWriter(dataset="test", session=session)
        # write in
        if len(stars) == 1:
            writer.write(stars[0])
        else:
            writer.write(stars)
        # make sure dataset was made
        ds_stmt = select(StarDBDataset.name)
        assert "test" in session.scalars(ds_stmt).all()
        # make sure all stars are present
        # make sure only stars written are present
        star_stmt = select(StarDB.name)
        read_names = session.scalars(star_stmt).all()
        # make sure everything is written
        ts_stmt = (
            select(StarDB)
            .join(StarDBDataset)
            .where(StarDB.name == bindparam("name"))
            .where(StarDBDataset.name == "test")
        )
        assert len(read_names) == len(stars)
        for star in stars:
            assert star.name in read_names
            db_ts = session.scalar(ts_stmt, {"name": star.name})
            for db_row in db_ts.timeseries:
                db_row.time = db_row.time.replace(
                    tzinfo=star.timeseries.data.index.tzinfo
                )
                star_row = star.timeseries.data.loc[db_row.time]
                # tests produce very close to 0 values that we don't care about
                assert isclose(db_row.mag, star_row["magnitude"], abs_tol=1e4)
                assert isclose(db_row.error, star_row["error"], abs_tol=1e4)


@given(star())
def test_update(star: Star):
    writer = DBWriter(dataset="test", engine=engine)
    writer.write(star)
    star.x = 3
    star.y = 3
    writer.write(star, overwrite=True)
    read_stars = []
    with Session(engine, future=True) as session:
        for dbstar in session.query(StarDB).all():
            read_stars.append(rec_star)
    assert star in read_stars
