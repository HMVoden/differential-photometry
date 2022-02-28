from typing import Generator, List, Optional

import attr
import pandas as pd
from attr import define, field
from shutterbug.data.interfaces.internal import Loader, Reader
from shutterbug.data.db.model import StarDB, StarDBLabel, StarDBTimeseries
from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from shutterbug.data.star import Star


@define(slots=True, frozen=True)
class DBReader(Reader):
    dataset: str = field()
    engine: Engine = field()
    mag_limit: Optional[float] = field(
        converter=attr.converters.optional(float), default=0
    )
    distance_limit: Optional[float] = field(
        converter=attr.converters.optional(float), default=0
    )

    @property
    def names(self) -> List[str]:
        with Session(self.engine) as session:
            star_names = (
                session.query(StarDBLabel.name)  # type: ignore
                .filter(StarDBLabel.dataset == self.dataset)
                .all()
            )
            return list(map(lambda x: x[0], star_names))

    def __len__(self) -> int:
        return len(self.names)

    def __iter__(self) -> Generator[Star, None, None]:
        """Connecting to target database, returns a generator of each individual star
        in sequence

        Returns
        -------
        Generator[pd.DataFrame, None, None]
            Dataframe with the star's name and timeseries (time, magnitude,
            error)

        """

        with Session(self.engine) as session:
            for name in self.names:
                statement = self._select_star()
                statement = statement.filter(
                    StarDBLabel.dataset == self.dataset, StarDBLabel.name == name
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
            statement = self._filter_on_constraints(
                statement=self._select_star(), target=target_cte.c
            )
            return pd.read_sql(
                sql=statement,
                con=session.bind,
                parse_dates=["time"],
                columns=["name", "time", "mag", "error"],
                index_col=["name", "time"],
            )

    def _select_star(self):
        """Creates selection statement to find all data for a star in the reader's dataset"""
        return (
            select(StarDB, StarDBTimeseries, StarDBLabel)
            .join(StarDB.timeseries)
            .join(StarDB.label)
            .where(StarDBLabel.dataset == self.dataset)
        )

    def _within_distance(self, target_x, target_y):
        """Returns statement which finds if target is within distance limit, for use with filtering"""
        return (
            func.SQRT(
                (
                    func.POW((StarDB.x - target_x), 2)
                    + func.POW((StarDB.y - target_y), 2)
                )
            )
            <= self.distance_limit
        )

    def _within_mag(self, target_mag):
        """Returns statement which finds if target is within magnitude limit, for use with filtering"""
        return func.ABS(StarDB.magnitude_median - target_mag) <= self.mag_limit

    def _filter_on_constraints(self, statement, target):
        """Appends filters for target"""
        statement = statement.where(StarDBLabel.name != target.name)
        if self.mag_limit != 0:
            statement = statement.where(self._within_mag(target.magnitude_median))
        if self.distance_limit != 0:
            statement = statement.where(
                self._within_distance(target_x=target.x, target_y=target.y)
            )
        return statement
