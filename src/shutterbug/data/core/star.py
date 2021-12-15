from functools import partial
from typing import Iterable

import numpy as np
import numpy.typing as npt
from attr import define, field

asfloat32 = partial(np.asarray, dtype=np.float32)
asfloat64 = partial(np.asarray, dtype=np.float64)
asdt64 = partial(np.asarray, dtype=np.datetime64)


@define(slots=True)
class StarTimeseries:
    """Timeseries information for a star"""

    time: npt.NDArray[np.datetime64] = field(converter=asdt64)
    mag: npt.NDArray[np.float32] = field(converter=asfloat32)
    error: npt.NDArray[np.float32] = field(converter=asfloat32)

    @error.validator
    def _same_length(self, attribute, value):
        assert len(self.time) == len(value)
        assert len(self.mag) == len(value)


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
