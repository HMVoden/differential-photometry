from contextlib import contextmanager
from typing import Generator

from shutterbug.data.db.model import (Base, StarDB, StarDBDataset,
                                      StarDBFeatures, StarDBTimeseries)
from sqlalchemy import create_engine, delete
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def sqlalchemy_db(future: bool = True) -> Engine:
    engine = create_engine("sqlite:///:memory:", future=future)
    Base.metadata.create_all(engine)
    return engine


# to prevent creating hundreds of DBs for testing
_future_db = sqlalchemy_db(future=True)
_db = sqlalchemy_db(future=False)


@contextmanager
def sqlite_memory(future=True) -> Generator[Session, None, None]:
    global _future_db
    global _db
    if future == True:
        database = _future_db
    else:
        database = _db
    session = Session(database)
    try:
        yield session
    finally:
        del_datasets = delete(StarDBDataset)
        del_stars = delete(StarDB)
        del_timeseries = delete(StarDBTimeseries)
        del_features = delete(StarDBFeatures)
        session.execute(del_stars)
        session.execute(del_datasets)
        session.execute(del_timeseries)
        session.execute(del_features)
        session.commit()
        session.close()
