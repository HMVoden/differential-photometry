import logging
from functools import singledispatchmethod
from itertools import repeat
from typing import Dict, Generator, Optional

import numpy as np
from attr import define, field
from shutterbug.data.db.model import (StarDB, StarDBDataset, StarDBFeatures,
                                      StarDBTimeseries)
from shutterbug.data.interfaces.internal import Writer
from shutterbug.data.star import Star
from sqlalchemy import DateTime, Float, bindparam, select, update
from sqlalchemy.orm import Session


@define
class DBWriter(Writer):
    """Maintains a SQLAlchemy database engine to write star data into a database
    that's defined by the provided engine

    """

    session: Session = field()
    dataset: str = field()
    _db_dataset: StarDBDataset = field(init=False)

    def __attrs_post_init__(self):
        statement = select(StarDBDataset).where(StarDBDataset.name == self.dataset)
        session = self.session
        db_dataset = session.scalar(statement)
        if db_dataset:
            self._db_dataset = db_dataset
        else:
            self._db_dataset = StarDBDataset(name=self.dataset)
            session.add(self._db_dataset)
            session.commit()

    def _get_star(self, name: str) -> StarDB:
        session = self.session
        star = (
            select(StarDB)
            .join(StarDBDataset)
            .where(StarDBDataset.name == self.dataset)
            .where(StarDB.name == name)
        )
        return session.scalar(star)

    @singledispatchmethod
    def write(self, data: Star, overwrite: bool = False):
        """Stores star in database defined by provided engine

        Parameter
        ----------
        data : Star
            Star from dataset

        """
        self._write_star(star=data, overwrite=overwrite)
        self.session.commit()

    @write.register
    def _(self, data: list, overwrite: bool = False):
        # have to use list as type due to bug with singledispatch
        for star in data:
            self._write_star(star=star, overwrite=overwrite)
        self.session.commit()

    @singledispatchmethod
    def update(self, star: Star):
        self._update_star(star)
        self._update_timeseries(star)
        self._update_features(star)
        self.session.commit()

    @update.register
    def _(self, data: list):
        for star in data:
            self._update_star(star)
            self._update_timeseries(star)
            self._update_features(star)
        self.session.commit()

    def _write_star(self, star: Star, overwrite: bool = False):
        """Writes star with given session

        Parameters
        ----------
        session : Session
            Open database session
        star : Star
            Star to write

        """
        session = self.session
        db_star = self._get_star(star.name)
        if not db_star:
            logging.debug(f"Writing star {star.name} into database")
            model_star = self._convert_to_model(star)
            session.add(model_star)
        else:
            if overwrite == False:
                logging.debug(
                    f"Tried to write star {star.name}, already present in database. Overwrite disabled."
                )
            else:
                model_star = self._convert_to_model(
                    star, median=db_star.magnitude_median
                )
                session.delete(db_star)
                session.commit()

                session.add(model_star)

    def _convert_to_model(self, star: Star, median: Optional[float] = None) -> StarDB:
        """Converts a Star datatype into a type writable to the provided database

        Parameters
        ----------
        star : Star
            Star with timeseries

        Returns
        -------
        StarDB
            Star datatype suitable for writing into a database

        """

        if median is None:
            median = star.timeseries.magnitude.median()

        db_star = StarDB(
            name=star.name,
            x=star.x,
            y=star.y,
            variable=star.variable,
            magnitude_median=median,
        )
        db_timeseries = []
        mag = star.timeseries.magnitude
        error = star.timeseries.error
        if star.timeseries.differential_magnitude is None:
            sadm = repeat(None)
            sade = repeat(None)
        else:
            sadm = star.timeseries.differential_magnitude
            sade = star.timeseries.differential_error
        timeseries_data = zip(mag.index, mag, error, sadm, sade)
        for time, mag, error, adm, ade in timeseries_data:
            ts = StarDBTimeseries(time=time, mag=mag, error=error, adm=adm, ade=ade)
            db_timeseries.append(ts)
        db_star.timeseries = db_timeseries
        db_star.dataset = self._db_dataset
        return db_star

    def _update_star(self, star: Star):
        session = self.session
        statement = (
            update(StarDB)
            .where(StarDB.name == star.name)
            .where(StarDB.dsid_ref == self._db_dataset.id)
            .values(variable=star.variable)
        )
        session.execute(statement)

    def _update_timeseries(self, star: Star):
        if star.timeseries.differential_magnitude is not None:
            session = self.session
            db_star = self._get_star(star.name)
            statement = (
                update(StarDBTimeseries)
                .where(StarDBTimeseries.star_id == db_star.id)
                .where(StarDBTimeseries.time == bindparam("dt", type_=DateTime()))
                .values(adm=bindparam("adm", type_=Float()))
                .values(ade=bindparam("ade", type_=Float()))
                .execution_options(synchronize_session=False)
            )
            session.execute(statement, list(self._time_adm_ade_from_star(star)))

    def _update_features(self, star: Star):
        if len(star.timeseries.features) > 0:
            session = self.session
            db_star = self._get_star(star.name)
            statement = (
                update(StarDBFeatures)
                .where(StarDBFeatures.star_id == db_star.id)
                .values(ivn=star.timeseries.features["Inverse Von Neumann"])
                .values(iqr=star.timeseries.features["IQR"])
                .execution_options(synchronize_session=False)
            )
            session.execute(statement)

    @staticmethod
    def _time_adm_ade_from_star(star: Star) -> Generator[Dict, None, None]:
        star_iter = zip(
            star.timeseries.time.to_pydatetime(),
            star.timeseries.differential_magnitude,
            star.timeseries.differential_error,
        )
        for dt, adm, ade in star_iter:
            yield {"dt": dt, "adm": adm, "ade": ade}
