from shutterbug.data.db.model import Base, StarDB, StarDBLabel, StarDBTimeseries
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy import delete


def sqlalchemy_db(future: bool = True) -> Engine:
    engine = create_engine("sqlite:///:memory:", future=future)
    Base.metadata.create_all(engine)
    return engine


# to prevent creating hundreds of DBs for testing
_future_db = sqlalchemy_db(future=True)
_db = sqlalchemy_db(future=False)


@contextmanager
def sqlite_memory(future=True):
    global _future_db
    global _db
    if future == True:
        database = _future_db
    else:
        database = _db
    try:
        yield database
    finally:
        with Session(database) as session:
            del_star = delete(StarDB).execution_options(synchronize_sesion=False)
            del_label = delete(StarDBLabel).execution_options(synchronize_session=False)
            del_ts = delete(StarDBTimeseries).execution_options(
                synchronize_session=False
            )
            session.execute(del_star)
            session.execute(del_label)
            session.execute(del_ts)
            session.commit()
            session.expire_all()
