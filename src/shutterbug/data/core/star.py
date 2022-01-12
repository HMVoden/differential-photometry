import logging

import numpy as np
import numpy.typing as npt
import pandas as pd
from attr import define, field


def asfloat(value):
    return pd.to_numeric(value, errors="coerce")


def asdatetime(value):
    try:
        # try julian date first
        return pd.to_datetime(
            value, errors="coerce", origin="julian", unit="D", utc=True
        ).round("1s")
    except ValueError:
        # let pandas guess
        return pd.to_datetime(value, errors="coerce", utc=True).round("1s")


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


@define(slots=True)
class Star:
    """Dataclass describing a star's information from an image or series of image"""

    dataset: str = field()
    name: str = field()
    x: int = field(converter=int)
    y: int = field(converter=int)
    data: StarTimeseries = field(init=False)

    # @error.validator
    # def positive_error(self, attribute, value):
    #     if not value >= 0:
    #         raise ValueError("Cannot have negative error")
