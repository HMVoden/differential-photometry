from functools import partial

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
            value, errors="coerce", origin="julian", unit="D"
        ).to_numpy()
    except ValueError:
        # let pandas guess
        return pd.to_datetime(value).to_numpy()


@define(slots=True)
class StarTimeseries:
    """Timeseries information for a star"""

    time: npt.NDArray[np.datetime64] = field(converter=asdatetime)
    mag: npt.NDArray[np.float32] = field(converter=asfloat)
    error: npt.NDArray[np.float32] = field(converter=asfloat)

    @error.validator
    def _same_length(self, _, value):
        """Ensure that all lists are same length"""
        assert len(self.time) == len(value)
        assert len(self.mag) == len(value)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        time = np.array_equal(self.time, other.time, equal_nan=True)
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
