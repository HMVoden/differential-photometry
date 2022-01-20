import logging

import attr
import numpy as np
import pandas as pd
from attr import define, field
from shutterbug.data.core.interface.writer import WriterInterface
from shutterbug.data.core.star import Star
from shutterbug.data.storage.db.model import (StarDB, StarDBLabel,
                                              StarDBTimeseries)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


@define
class DBWriter(WriterInterface):
    """Maintains a SQLAlchemy database engine to write star data into a database
    that's defined by the provided engine

    """

    db_engine: Engine = field(validator=attr.validators.instance_of(Engine))

    def write(self, data: Star):
        """Stores star in database defined by provided engine

        Parameter
        ----------
        data : Star
            Star from dataset

        """
        with Session(self.db_engine) as session:
            logging.debug(f"Writing star {data.name} into database")
            model_star = self._convert_to_model(data)
            session.add(model_star)
            session.commit()

    @staticmethod
    def _convert_to_model(
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
            x=star.x, y=star.y, magnitude_median=np.nanmedian(star.data.mag)
        )
        db_label = StarDBLabel(name=star.name, dataset=star.dataset)
        db_timeseries = []
        time = star.data.time.to_pydatetime()
        time = np.where(pd.isnull(time), None, time)
        timeseries_data = zip(
            time,
            star.data.mag,
            star.data.error,
        )
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
