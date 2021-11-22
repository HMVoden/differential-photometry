from functools import lru_cache
from typing import Iterable, Sequence

import numpy as np
import numpy.typing as npt
import pandas as pd
from shutterbug.analyzer.core.interface.constraints import ConstraintInterface


class MagnitudeConstraint(ConstraintInterface):
    medians: npt.NDArray[np.float64]
    radius: float

    def __init__(self, radius: float, magnitudes: Sequence[float]) -> None:
        if radius < 0:
            raise ValueError("Tolerance cannot be negative")
        self.radius = radius
        medians = []
        for row in magnitudes:
            medians.append(np.median(row))
        medians = np.asarray(medians)
        self.medians = medians

    def meets(self, target: pd.Series):
        return self._find_close_magnitude(np.median(target["mag"]))

    @lru_cache
    def _find_close_magnitude(self, target: float) -> Iterable[int]:
        radius = self.radius
        dist = self._abs_median_difference(target)
        met_indices = np.argwhere(dist <= radius)
        return met_indices

    @lru_cache
    def _abs_median_difference(self, target: float) -> npt.NDArray[np.float64]:
        medians = self.medians
        difference = medians - target
        dist = np.absolute(difference)
        return dist
