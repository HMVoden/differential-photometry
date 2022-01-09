from attr import define, field
from shutterbug.data.core.interface.loader import LoaderInterface
from shutterbug.data.core.star import Star
from shutterbug.data.storage.db.model import StarDB
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import func, select


@define
class DBLoader(LoaderInterface):

    db_engine: Engine = field()
    dataset: str = field()

    def __iter__(self) -> Star:
        """Iterable of all stars in dataset"""
        pass

    def __len__(self) -> int:
        """Returns number of stars in dataset"""
        counter = (
            select(func.count())
            .select_from(StarDB)
            .where(StarDB.dataset == self.dataset)
        )
        with Session(self.db_engine) as session:
            return session.execute(counter)
