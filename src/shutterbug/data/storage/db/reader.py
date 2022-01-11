from typing import Generator

import pandas as pd
from attr import define, field
from shutterbug.data.interfaces.internal import DataReaderInterface
from shutterbug.data.storage.db.model import StarDB, StarDBTimeseries
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


@define
class DBReader(DataReaderInterface):
    dataset: str = field()
    engine: Engine = field()

    @property
    def all(self) -> Generator[pd.DataFrame, None, None]:

        with Session(self.engine) as session:
            statement = (
                session.query(StarDB, StarDBTimeseries)
                .join(StarDB.timeseries)
                .where(StarDB.dataset == self.dataset)
                .statement
            )

            yield pd.read_sql(
                sql=statement,
                con=session.bind,
            )

    def similar_to(self, star: str) -> pd.DataFrame:
        pass
