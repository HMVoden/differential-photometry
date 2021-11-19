from typing import NoReturn, Sequence

import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy.spatial.kdtree import KDTree
from shutterbug.analyzer.core.interface.constraints import ConstraintInterface


class MagnitudeConstraint(ConstraintInterface):
    magnitudes: npt.NDArray[np.float64]
    radius: float

    def __init__(self, radius: float, magnitudes: Sequence[float]) -> None:
        if radius < 0:
            raise ValueError("Tolerance cannot be negative")
        self.radius = radius
        medians = []
        for row in magnitudes:
            medians.append(np.median(row))
        medians = np.asarray(medians)
        self.magnitudes = medians

    def meets(self, target: pd.Series):
        radius = self.radius
        medians = self.magnitudes
        target_median = np.median(target["mag"])
        dist = np.absolute(medians - target_median)
        met_indices = np.argwhere(dist <= radius)
        return met_indices
