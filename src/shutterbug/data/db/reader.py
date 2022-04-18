from typing import Dict, Generator, List, Optional

import attr
import numpy as np
import pandas as pd
from attr import define, field
from shutterbug.data.db.model import StarDB, StarDBDataset
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
    _star_cache: Dict[str, List[str]] = field(init=False, default={})

    @property
    def names(self) -> List[str]:
        stmt = select(StarDB.name).where(StarDBDataset.name == self.dataset)
        star_names = self.session.scalars(stmt).all()
        return star_names

    @property
    def variable(self) -> Generator[Star, None, None]:
        """Iterable of variable stars in source"""
        statement = self._select_star()
        statement = statement.where(StarDB.variable == True)
        yield from map(self._model_to_star, self.session.scalars(statement))

    def __len__(self) -> int:
        return len(self.names)

    def __iter__(self) -> Generator[Star, None, None]:
        statement = self._select_star()
        yield from map(self._model_to_star, self.session.scalars(statement))

    def similar_to(self, star: Star) -> List[Star]:
        """Returns all stars that are similar to target star"""
        similar_star_names = self._filter_on_constraints(star)
        statement = self._select_star().where(StarDB.name.in_(similar_star_names))
        return list(
            map(self._model_to_star, self.session.scalars(statement).fetchmany(size=50))
        )

    def _select_star(self):
        """Creates selection statement to find all data for a star in the reader's dataset"""
        return (
            select(StarDB).join(StarDBDataset).where(StarDBDataset.name == self.dataset)
        )

    def _within_distance(self, star: Star) -> List[str]:
        session = self.session
        statement = (
            select(StarDB.name)
            .join(StarDBDataset)
            .where(
                (
                    func.SQRT(
                        (
                            func.POW((StarDB.x - star.x), 2)
                            + func.POW((StarDB.y - star.y), 2)
                        )
                    )
                    <= self.distance_limit
                )
            )
            .where(StarDB.name != star.name)
            .where(StarDBDataset.name == self.dataset)
        )
        return session.scalars(statement).all()

    def _within_mag(self, star: Star) -> List[str]:
        session = self.session
        statement = (
            select(StarDB.name)
            .join(StarDBDataset)
            .where(
                (
                    func.ABS(
                        StarDB.magnitude_median - np.median(star.timeseries.magnitude)
                    )
                    <= self.mag_limit
                )
            )
            .where(StarDB.name != star.name)
            .where(StarDBDataset.name == self.dataset)
        )
        return session.scalars(statement).all()

    def _non_variable(self, star: Star) -> List[str]:
        session = self.session
        statement = (
            select(StarDB.name)
            .join(StarDBDataset)
            .where(StarDBDataset.name == self.dataset)
            .where(StarDB.variable == False)
            .where(StarDB.name != star.name)
        )
        return session.scalars(statement).all()

    def _filter_on_constraints(self, star: Star) -> List[str]:

        if star.name not in self._star_cache.keys():
            similar_mag = set(self._within_mag(star))
            similar_dist = set(self._within_distance(star))
            self._star_cache[star.name] = list(similar_mag.intersection(similar_dist))
        return list(
            set(self._non_variable(star)).intersection(self._star_cache[star.name])
        )

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
        if len(star.features) > 0:
            print(star.features)
            rec_timeseries.add_feature(
                name="Inverse Von Neumann", value=star.features.ivn
            )
            rec_timeseries.add_feature(name="IQR", value=star.features.iqr)
        rec_star = Star(
            name=star.name,
            x=star.x,
            y=star.y,
            timeseries=rec_timeseries,
            variable=star.variable,
        )
        return rec_star
