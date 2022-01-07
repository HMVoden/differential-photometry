import logging
from typing import List, Tuple

from attr import define, field
from shutterbug.data.core.interface.storage import StorageInterface
from shutterbug.data.core.star import Star
from shutterbug.data.storage.db.model import StarDB, StarDBTimeseries
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


@define
class DBWriter(StorageInterface):
    """Maintains a database engine to write star data into a database that's
    defined by the provided engine"""

    db_engine: Engine = field()

    def write(self, data: Star):
        """Stores star in database defined by provided engine

        Parameters
        ----------
        data : Star
            Star from dataset

        """
        with Session(self.db_engine, future=True) as session:
            logging.debug(f"Writing star {data.name} into database")
            model_star, model_timeseries = self._convert_to_model(data)
            session.add(model_star)
            session.add_all(model_timeseries)

    @staticmethod
    def _convert_to_model(star: Star) -> Tuple[StarDB, List[StarDBTimeseries]]:
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

        db_star = StarDB(name=star.name, dataset=star.dataset, x=star.x, y=star.y)
        db_timeseries = []
        timeseries_data = zip(star.data.time, star.data.mag, star.data.error)
        for time, mag, error in timeseries_data:
            ts = StarDBTimeseries(
                star_name=star.name,
                star_dataset=star.dataset,
                time=time,
                mag=mag,
                error=error,
            )
            db_timeseries.append(ts)
        return db_star, db_timeseries
