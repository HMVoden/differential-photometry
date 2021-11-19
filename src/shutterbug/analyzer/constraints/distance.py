from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy.spatial.kdtree import KDTree
from shutterbug.analyzer.core.interface.constraints import ConstraintInterface


class DistanceConstraint(ConstraintInterface):
    radius: float
    tree: KDTree

    def __init__(self, radius: float, xs: Sequence[float], ys: Sequence[float]):
        if radius < 0:
            raise ValueError("Cannot have a negative radius")
        self.radius = radius
        positions = np.column_stack((xs, ys))
        self.tree = KDTree(data=positions)

    def meets(self, target: pd.Series) -> Iterable[int]:
        radius = self.radius
        tree = self.tree
        target_xy = (target["x"], target["y"])
        met_indices = tree.query_ball_point(x=target_xy, r=radius).sort()

        return met_indices
