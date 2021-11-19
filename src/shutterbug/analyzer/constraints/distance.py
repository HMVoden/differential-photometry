from typing import Sequence

import numpy as np
import xarray as xr
from shutterbug.analyzer.core.interface.constraints import ConstraintInterface


class DistanceConstraint(ConstraintInterface):
    radius: float

    def __init__(self, radius):
        if radius < 0:
            raise ValueError("Cannot have a negative radius")
        self.radius = radius

    def meets(self, values: Sequence[xr.Dataset]):
        met_indices = []
        radius = self.radius
        xs = values.x.values
        ys = values.y.values
        met_indices = np.argwhere(np.sqrt(xs ** 2 + ys ** 2) <= radius)
        return met_indices
