import logging

import numpy as np
import numpy.typing as npt
import pandas as pd
from attr import define, field
import sys


def asfloat(value) -> npt.NDArray[np.float64]:
    return pd.to_numeric(value, errors="coerce")  # type: ignore


def asdatetime(value):
    try:
        # try julian date first
        floats = asfloat(value)
        return pd.to_datetime(
            floats, errors="coerce", origin="julian", unit="D", utc=True
        ).round("1s")
    except ValueError:
        # let pandas guess
        return pd.to_datetime(floats, errors="coerce", utc=True).round("1s")


@define(slots=True)
class StarTimeseries:
    """Timeseries information for a star"""

    time: pd.DatetimeIndex = field(converter=asdatetime)
    mag: npt.NDArray[np.float64] = field(converter=asfloat)
    error: npt.NDArray[np.float64] = field(converter=asfloat)

    def _same_length(self):
        """Ensure that all lists are same length"""
        assert len(self.time) == len(self.error)
        assert len(self.mag) == len(self.error)

    def __attrs_post_init__(self):
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

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        time = self.time.equals(other.time)
        mag = np.array_equal(self.mag, other.mag, equal_nan=True)
        error = np.array_equal(self.error, other.error, equal_nan=True)
        return all([time, mag, error])

    @property
    def nbytes(self) -> int:
        """Number of bytes the timeseries consumes in memory"""
        return self.time.nbytes + self.mag.nbytes + self.error.nbytes


@define(slots=True)
class Star:
    """Dataclass describing a star's information from an image or series of image"""

    dataset: str = field()
    name: str = field()
    x = field(converter=[float, int])
    y = field(converter=[float, int])
    data: StarTimeseries = field()

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
            + self.data.nbytes
        )
