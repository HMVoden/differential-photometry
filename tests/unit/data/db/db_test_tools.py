from contextlib import contextmanager
from typing import Generator

from shutterbug.data.db.model import (Base, StarDB, StarDBDataset,
                                      StarDBFeatures, StarDBTimeseries)
from sqlalchemy import create_engine, delete, select
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
def sqlite_memory(
    future: bool = True, autoflush: bool = True
) -> Generator[Session, None, None]:
    global _future_db
    global _db
    if future == True:
        database = _future_db
    else:
        database = _db
    session = Session(database, autoflush=autoflush)
    try:
        yield session
    finally:
        datasets = session.scalars(select(StarDBDataset)).all()
        list(map(session.delete, datasets))
        session.flush()
        session.commit()
        session.close()
