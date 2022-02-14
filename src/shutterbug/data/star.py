from __future__ import annotations
import logging

import numpy as np
import numpy.typing as npt
import pandas as pd
from attr import define, field
import sys

from typing import List

from shutterbug.data.header import KnownHeader
from shutterbug.data.validate import validate_timeseries


def asfloat(value: List[str]) -> npt.NDArray[np.float32]:
    return pd.to_numeric(value, errors="coerce", downcast="float")  # type: ignore


def asdatetime(value) -> pd.DatetimeIndex:
    try:
        # Try julian date
        fl = pd.to_numeric(value, errors="coerce")
        datetimes = pd.to_datetime(
            fl, errors="coerce", origin="julian", unit="D", utc=True
        )
        if all(pd.isna(datetimes)):
            raise ValueError
    except (ValueError, NameError):
        # Try guessing
        datetimes = pd.to_datetime(value, errors="coerce", utc=True)
    datetimes = datetimes.round("1us")
    return pd.DatetimeIndex(datetimes, name="time", yearfirst=True)


@define(slots=True)
class StarTimeseries:
    """Timeseries information for a star"""

    _data: pd.DataFrame = field()

    @property
    def time(self) -> pd.DatetimeIndex:
        return self._data.index  # type: ignore

    @property
    def magnitude(self) -> npt.NDArray[np.float_]:
        return self._data["magnitude"].to_numpy()

    @property
    def error(self) -> npt.NDArray[np.float_]:
        return self._data["error"].to_numpy()

    @property
    def averaged_differential_magnitude(self) -> npt.NDArray[np.float_]:
        return self._data["adm"].to_numpy()

    @property
    def averaged_differential_error(self) -> npt.NDArray[np.float_]:
        return self._data["ade"].to_numpy()

    def drop_rows(self, rows: List[int]) -> None:
        self._data = self._data.drop(index=rows)  # type: ignore

    def __eq__(self, other: StarTimeseries):
        if other.__class__ is not self.__class__:
            return NotImplemented

        return self._data == other._data

    @property
    def nbytes(self) -> int:
        """Number of bytes the timeseries consumes in memory"""
        return self.time.nbytes + self.magnitude.nbytes + self.error.nbytes

    @classmethod
    def from_rows(
        cls, rows: List[List[str]], row_headers: KnownHeader
    ) -> StarTimeseries:
        logging.debug(f"Building timeseries, number of rows: {len(rows)}")
        getter = row_headers.timeseries_getters
        timeseries = list(map(getter, rows))
        # so we can get each specific column without fuss
        np_data = np.asarray(timeseries)
        df = pd.DataFrame(
            data={"magnitude": asfloat(np_data[:, 1]), "error": asfloat(np_data[:, 2])},
            index=asdatetime(np_data[:, 0]),
        )

        ts = cls(_data=df)
        ts = validate_timeseries(ts)
        logging.debug("Finished building timeseries")
        return ts


@define(slots=True)
class Star:
    """Dataclass describing a star's information from an image or series of image"""

    name: str = field()
    x: int = field(converter=[float, int])
    y: int = field(converter=[float, int])
    timeseries: StarTimeseries = field()

    @property
    def nbytes(self) -> int:
        """Number of bytes the star consumes in memory"""
        return (
            sys.getsizeof(self.name)
            + sys.getsizeof(self.x)
            + sys.getsizeof(self.y)
            + self.timeseries.nbytes
        )

    @classmethod
    def from_rows(cls, rows: List[List[str]], row_headers: KnownHeader) -> Star:
        name, x, y = row_headers.star_getters(rows[0])
        logging.debug(f"Building star object {name}, x: {x}, y: {y}")
        timeseries = StarTimeseries.from_rows(rows, row_headers)
        return cls(name=name, x=x, y=y, timeseries=timeseries)
