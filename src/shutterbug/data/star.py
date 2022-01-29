from __future__ import annotations
import logging

import numpy as np
import numpy.typing as npt
import pandas as pd
from attr import define, field
import sys

from typing import List

from shutterbug.data.header import KnownHeader


def asfloat(value) -> npt.NDArray[np.float64]:
    return pd.to_numeric(value, errors="coerce")  # type: ignore


def asdatetime(value):
    try:
        # try julian date first
        return pd.to_datetime(
            value, errors="coerce", origin="julian", unit="D", utc=True
        )
    except (ValueError, NameError):
        # let pandas guess
        return pd.to_datetime(value, errors="coerce", utc=True)


@define(slots=True)
class StarTimeseries:
    """Timeseries information for a star"""

    time: pd.DatetimeIndex = field(converter=asdatetime)
    mag: npt.NDArray[np.float64] = field(converter=asfloat)
    error: npt.NDArray[np.float64] = field(converter=asfloat)

    @mag.validator
    def _has_data(self, _, values):
        if np.isnan(values).all():
            raise ValueError("Timeseries must have data, does not have any")

    def _same_length(self):
        """Ensure that all lists are same length"""
        assert len(self.time) == len(self.error)
        assert len(self.mag) == len(self.error)

    def _unique_times(self):
        _, unique_indices = np.unique(self.time, return_index=True)
        if not len(unique_indices) == len(self.time):
            logging.debug("Have duplicate time entries on star")
            self.time = self.time[unique_indices]
            self.mag = self.mag[unique_indices]
            self.error = self.error[unique_indices]
        try:
            self._same_length()
        except AssertionError:
            raise ValueError(
                f"Timeseries entries are incomplete, have length for time:{len(self.time)}, magnitude:{len(self.mag)}, error:{len(self.error)}. Expected equal."
            )

    def _no_empty_rows(self):
        time = self.time
        mag = self.mag
        error = self.error
        bad_indices = []
        for idx, time in enumerate(time):
            if np.isnan(mag[idx]) and np.isnan(error[idx]):
                bad_indices.append(idx)
        bad_indices = np.asarray(bad_indices).tolist()
        self.time = self.time.delete(bad_indices)
        self.mag = np.delete(self.mag, bad_indices)
        self.error = np.delete(self.error, bad_indices)

    def _no_empty_time(self):
        not_a_time = np.argwhere(pd.isna(self.time)).flatten().tolist()
        self.time = self.time.delete(not_a_time)
        self.mag = np.delete(self.mag, not_a_time)
        self.error = np.delete(self.error, not_a_time)

    def __attrs_post_init__(self):
        # Ensure that the data is good
        self._no_empty_time()
        self._no_empty_rows()
        self._unique_times()
        if len(self.time) == 0:
            raise ValueError("Given insufficient information for timeseries")

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        time = self.time.round("1ms").equals(other.time.round("1ms"))
        mag = np.array_equal(self.mag, other.mag, equal_nan=True)
        error = np.array_equal(self.error, other.error, equal_nan=True)
        return all([time, mag, error])

    @property
    def nbytes(self) -> int:
        """Number of bytes the timeseries consumes in memory"""
        return self.time.nbytes + self.mag.nbytes + self.error.nbytes

    @classmethod
    def from_rows(
        cls, rows: List[List[str]], row_headers: KnownHeader
    ) -> StarTimeseries:
        logging.debug(f"Building timeseries, number of rows: {len(rows)}")
        getter = row_headers.timeseries_getters
        timeseries = list(map(getter, rows))
        # so we can get each specific column without fuss
        np_data = np.asarray(timeseries)
        return cls(time=np_data[:, 0], mag=np_data[:, 1], error=np_data[:, 2])


@define(slots=True)
class Star:
    """Dataclass describing a star's information from an image or series of image"""

    name: str = field()
    x: int = field(converter=[float, int])
    y: int = field(converter=[float, int])
    timeseries: StarTimeseries = field()

    # @error.validator
    # def positive_error(self, attribute, value):
    #     if not value >= 0:
    #         raise ValueError("Cannot have negative error")

    @property
    def nbytes(self) -> int:
        """Number of bytes the star consumes in memory"""
        return (
            sys.getsizeof(self.dataset)
            + sys.getsizeof(self.name)
            + sys.getsizeof(self.x)
            + sys.getsizeof(self.y)
            + self.timeseries.nbytes
        )

    @classmethod
    def from_rows(cls, rows: List[List[str]], row_headers: KnownHeader) -> Star:
        name, x, y = row_headers.star_getters(rows[0])
        logging.debug(f"Building star object {name}, number of rows {len(rows)}")
        timeseries = StarTimeseries.from_rows(rows, row_headers)
        return cls(name=name, x=x, y=y, timeseries=timeseries)
