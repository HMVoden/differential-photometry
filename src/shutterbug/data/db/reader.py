from typing import Generator, List, Optional

import attr
import pandas as pd
from attr import define, field
from shutterbug.data.db.model import StarDB, StarDBLabel
from shutterbug.data.interfaces.internal import Reader
from shutterbug.data.star import Star, StarTimeseries
from sqlalchemy import func, select
from sqlalchemy.orm import Session


@define(slots=True, frozen=True)
class DBReader(Reader):
    dataset: str = field()
    session: Session = field()
    mag_limit: Optional[float] = field(
        converter=attr.converters.optional(float), default=0
    )
    distance_limit: Optional[float] = field(
        converter=attr.converters.optional(float), default=0
    )

    @property
    def names(self) -> List[str]:
        stmt = select(StarDBLabel.name).where(StarDBLabel.dataset == self.dataset)
        star_names = self.session.scalars(stmt).all()
        return star_names

    def __len__(self) -> int:
        return len(self.names)

    def __iter__(self) -> Generator[Star, None, None]:
        statement = self._select_star()
        yield from map(self._model_to_star, self.session.scalars(statement))

    def similar_to(self, star_name: str) -> List[Star]:
        """Returns all stars that are similar to target star"""
        target_cte = (
            select(StarDB.x, StarDB.y, StarDB.magnitude_median, StarDBLabel.name)
            .join(StarDB.label)
            .where(StarDBLabel.name == star_name, StarDBLabel.dataset == self.dataset)
            .cte()
        )
        statement = self._filter_on_constraints(
            statement=self._select_star(), target=target_cte.c
        )
        return list(map(self._model_to_star, self.session.scalars(statement).all()))

    def _select_star(self):
        """Creates selection statement to find all data for a star in the reader's dataset"""
        return (
            select(StarDB)
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

    def _model_to_star(self, star: StarDB) -> Star:

        """Converts a db model of a star into a full Star object, with StarTimeseries

        :param star: StarDB from the database model
        :returns: Star

        """
        db_time = []
        db_mag = []
        db_error = []
        db_adm = []
        db_ade = []
        for row in star.timeseries:
            db_time.append(row.time)
            db_mag.append(row.mag)
            db_error.append(row.error)
            db_adm.append(row.adm)
            db_ade.append(row.ade)
        data = pd.DataFrame(
            {"magnitude": db_mag, "error": db_error, "adm": db_adm, "ade": db_ade},
            index=pd.to_datetime(db_time, utc=True),
        )
        data.index.name = "time"
        rec_timeseries = StarTimeseries(data=data)
        rec_star = Star(
            name=star.label.name,
            x=star.x,
            y=star.y,
            timeseries=rec_timeseries,
        )
        return rec_star
