from typing import Dict, Generator, List, Optional

import attr
import pandas as pd
from attr import define, field
from shutterbug.data.db.model import StarDB, StarDBDataset
from shutterbug.data.interfaces.internal import Reader
from shutterbug.data.star import Star, StarTimeseries
from sqlalchemy import func, select
from sqlalchemy.orm import Session


@define(slots=True)
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

    def __attrs_post_init__(self):
        if len(self._star_cache) > 0:
            # hard reset cache to deal with
            # persistence bug
            self._star_cache = {}

    @property
    def names(self) -> List[str]:
        stmt = (
            select(StarDB.name)
            .join(StarDBDataset)
            .where(StarDBDataset.name == self.dataset)
        )
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

    def get(self, name: str) -> Star:
        statement = self._select_star().where(StarDB.name == name)
        return self._model_to_star(self.session.scalar(statement))

    def get_many(self, names: List[str]) -> List[Star]:
        statement = self._select_star().where(StarDB.name.in_(names))
        return list(map(self._model_to_star, self.session.scalars(statement)))

    def similar_to(self, star: Star) -> List[str]:
        """Returns all names that are similar to target star"""
        similar_star_names = self._filter_on_constraints(star)
        return similar_star_names

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
                        StarDB.magnitude_median - star.timeseries.magnitude.median()
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

    def _model_to_star(self, stardb: StarDB) -> Star:

        """Converts a db model of a star into a full Star object, with StarTimeseries

        :param star: StarDB from the database model
        :returns: Star

        """
        # this assignment is highly wasteful
        db_time = []
        db_mag = []
        db_error = []
        db_adm = []
        db_ade = []
        for row in stardb.timeseries:
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
        for row in stardb.features:
            rec_timeseries.add_feature(
                dt=row.date, name="Inverse Von Neumann", value=row.ivn
            )
            rec_timeseries.add_feature(dt=row.date, name="IQR", value=row.iqr)
        rec_star = Star(
            name=stardb.name,
            x=stardb.x,
            y=stardb.y,
            timeseries=rec_timeseries,
            variable=stardb.variable,
        )
        return rec_star
