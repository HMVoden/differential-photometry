import logging

import attr
import numpy as np
from attr import define, field
from shutterbug.data.interfaces.internal import Writer
from shutterbug.data.star import Star
from shutterbug.data.db.model import StarDB, StarDBLabel, StarDBTimeseries
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from functools import singledispatchmethod


@define
class DBWriter(Writer):
    """Maintains a SQLAlchemy database engine to write star data into a database
    that's defined by the provided engine

    """

    engine: Engine = field(validator=attr.validators.instance_of(Engine))
    dataset: str = field()

    @singledispatchmethod
    def write(self, data: Star, overwrite: bool = False):
        """Stores star in database defined by provided engine

        Parameter
        ----------
        data : Star
            Star from dataset

        """
        with Session(self.engine) as session:
            self._write_star(session=session, star=data, overwrite=overwrite)
            session.commit()

    @write.register
    def _(self, data: list, overwrite: bool = False):
        # have to use list as type due to bug with singledispatch
        with Session(self.engine) as session:
            for star in data:
                self._write_star(session=session, star=star, overwrite=overwrite)
            session.commit()

    def _write_star(self, session: Session, star: Star, overwrite: bool = False):
        """Writes star with given session

        Parameters
        ----------
        session : Session
            Open database session
        star : Star
            Star to write

        """
        db_star = (
            session.query(StarDBLabel.name)
            .filter(StarDBLabel.name == star.name)
            .filter(StarDBLabel.dataset == self.dataset)
        )
        if not session.query(db_star.exists()).scalar():
            logging.debug(f"Writing star {star.name} into database")
            model_star = self._convert_to_model(star)
            session.add(model_star)
        else:
            if overwrite == False:
                logging.debug(
                    f"Tried to write star {star.name}, already present in database. Overwrite disabled."
                )
            else:
                self._update_star(star, session)

    def _update_star(self, star: Star, session: Session):
        pass

    def _convert_to_model(
        self,
        star: Star,
    ) -> StarDB:
        """Converts a Star datatype into a type writable to the provided database

        Parameters
        ----------
        star : Star
            Star with timeseries

        Returns
        -------
        Tuple[StarDB, List[StarDBTimeseries]]
            Star and timeseries datatypes suitable for writing into a database

        """

        db_star = StarDB(
            x=star.x, y=star.y, magnitude_median=np.nanmedian(star.timeseries.magnitude)
        )
        db_label = StarDBLabel(name=star.name, dataset=self.dataset)
        db_timeseries = []
        mag = star.timeseries.magnitude
        error = star.timeseries.error
        timeseries_data = zip(mag.index.to_pydatetime(), mag, error)
        for time, mag, error in timeseries_data:
            ts = StarDBTimeseries(
                time=time,
                mag=mag,
                error=error,
            )
            db_timeseries.append(ts)
        db_star.label = db_label
        db_star.timeseries = db_timeseries
        return db_star
