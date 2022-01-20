from shutterbug.data.storage.db.model import Base
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


def sqlalchemy_db(future: bool = True) -> Engine:
    engine = create_engine("sqlite:///:memory:", future=future)
    Base.metadata.create_all(engine)
    return engine
