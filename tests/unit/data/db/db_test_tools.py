from contextlib import contextmanager
from typing import Generator, Tuple

from shutterbug.data.storage.db.model import Base
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session


@contextmanager
def sqlalchemy_session() -> Generator[Tuple[Engine, Session], None, None]:
    engine = create_engine("sqlite:///:memory:", future=True)
    session = Session(bind=engine, future=True, expire_on_commit=False)
    Base.metadata.create_all(engine)
    try:
        yield engine, session
    finally:
        session.close()
