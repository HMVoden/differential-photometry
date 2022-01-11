from typing import Generator, List

import pandas as pd
from attr import define, field
from shutterbug.data.interfaces.internal import DataReaderInterface
from shutterbug.data.storage.db.model import (StarDB, StarDBLabel,
                                              StarDBTimeseries)
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


@define
class DBReader(DataReaderInterface):
    dataset: str = field()
    engine: Engine = field()
    _stars: List[str] = field(init=False)

    def __attrs_post_init__(self):
        """Sets up the DBReader to hold all the stars that are currently in the
        database so we're not constantly requesting this information from the
        database"""
        with Session(self.engine) as session:
            db_stars = (
                session.query(StarDBLabel.name)  # type: ignore
                .filter(StarDBLabel.dataset == self.dataset)
                .all()
            )

            self._stars = list(map(lambda x: x[0], db_stars))

    @property
    def all(self) -> Generator[pd.DataFrame, None, None]:
        """Connecting to target database, returns a generator of each individual star in sequence

        Returns
        -------
        Generator[pd.DataFrame, None, None]
            Dataframe with the star's name and timeseries (time, magnitude,
            error)

        """

        with Session(self.engine) as session:
            for name in self._stars:
                statement = (
                    session.query(StarDB, StarDBTimeseries, StarDBLabel)  # type: ignore
                    .join(StarDB.timeseries)
                    .join(StarDB.label)
                    .filter(
                        StarDBLabel.dataset == self.dataset, StarDBLabel.name == name
                    )
                    .statement
                )  # type: ignore

                yield pd.read_sql(
                    sql=statement,
                    con=session.bind,
                    parse_dates=["time"],
                    columns=["name", "time", "mag", "error"],
                    index_col=["name", "time"],
                )

    def similar_to(self, star: str) -> pd.DataFrame:
        pass
