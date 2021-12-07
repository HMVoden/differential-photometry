from typing import Iterable

import numpy as np
from attr import define, field


@define(slots=True)
class StarTimeseries:
    """Timeseries information for a star"""

    time: Iterable[float] = field(converter=np.float64)
    mag: Iterable[float] = field(converter=np.float32)
    error: Iterable[float] = field(converter=np.float32)


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
