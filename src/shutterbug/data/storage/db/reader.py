from typing import Generator, List, Optional

import attr
import pandas as pd
from attr import define, field
from shutterbug.data.interfaces.internal import DataReaderInterface
from shutterbug.data.storage.db.model import (StarDB, StarDBLabel,
                                              StarDBTimeseries)
from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


@define
class DBReader(DataReaderInterface):
    dataset: str = field()
    engine: Engine = field()
    _stars: List[str] = field(init=False)
    mag_limit: Optional[float] = field(converter=attr.converters.optional(float))
    distance_limit: Optional[float] = field(converter=attr.converters.optional(float))

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
        """Connecting to target database, returns a generator of each individual star
        in sequence

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
                )

                yield pd.read_sql(
                    sql=statement,
                    con=session.bind,
                    parse_dates=["time"],
                    columns=["name", "time", "mag", "error"],
                    index_col=["name", "time"],
                )

    def similar_to(self, star_name: str) -> pd.DataFrame:
        """Finds all stars that are within a magnitude and distance tolerance, excluding target star

        Parameters
        ----------
        star_name : str
            Target star name to identify start

        Returns
        -------
        pd.DataFrame
            DataFrame of all qualifying stars containing time and name as
            indexes, with timeseries information (magnitude, error) as columns

        """

        with Session(self.engine) as session:
            target_cte = (
                select(StarDB.x, StarDB.y, StarDB.magnitude_median, StarDBLabel.name)
                .join(StarDB.label)
                .where(
                    StarDBLabel.name == star_name, StarDBLabel.dataset == self.dataset
                )
                .cte()
            )
            statement = (
                select(StarDB, StarDBTimeseries, StarDBLabel)
                .join(StarDB.timeseries)
                .join(StarDB.label)
                .where(
                    StarDBLabel.name != target_cte.c.name,
                    StarDBLabel.dataset == self.dataset,
                    (
                        func.SQRT(
                            (
                                func.POW((StarDB.x - target_cte.c.x), 2)
                                + func.POW((StarDB.y - target_cte.c.y), 2)
                            )
                        )
                        <= self.distance_limit
                    ),
                    (
                        func.ABS(
                            StarDB.magnitude_median - target_cte.c.magnitude_median
                        )
                        <= self.mag_limit
                    ),
                )
            )
            return pd.read_sql(
                sql=statement,
                con=session.bind,
                parse_dates=["time"],
                columns=["name", "time", "mag", "error"],
                index_col=["name", "time"],
            )
