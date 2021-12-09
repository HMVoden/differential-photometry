import logging
from typing import List, Tuple

import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy.spatial import KDTree
from shutterbug.photometry.detect.detect import DetectBase


class DistanceDetector(DetectBase):
    tree: KDTree
    stars: pd.Series

    def __init__(self, ds: pd.DataFrame, **kwargs):
        super().__init__(**kwargs)

        self.stars = ds[["name", "x", "y"]].groupby("name").mean()
        self.tree = self._build_kd_tree(self.stars["x"].values, self.stars["y"].values)
        self.detector_name = "Distance"
        self.detector_units = "px"
        self.log()

    def detect(self, target_star: str) -> npt.NDArray[np.str_]:
        """Finds stars that are nearby target star, within radius tolerance, using a KDtree"""
        tree = self.tree
        radius = self.tolerance
        target_index = self.stars.index.get_loc(target_star)
        target = self.stars.iloc[target_index]
        target_x = target["x"]
        target_y = target["y"]
        target_xy = np.column_stack((target_x, target_y))[0].tolist()
        result_indices = tree.query_ball_point(x=target_xy, r=radius)
        result_stars = self.stars.iloc[result_indices].index
        logging.debug(f"Found closeby stars {', '.join(result_stars)}")
        return result_stars

    def _build_kd_tree(
        self, xs: npt.NDArray[np.float64], ys: npt.NDArray[np.float64]
    ) -> KDTree:
        """Makes a KDtree from the x-y coordinates of each star

        Parameters
        ----------
        xs : npt.NDArray[np.float64]
        x-coordinates for each star, in order of each star
        ys : npt.NDArray[np.float64]
        y-coordinates of each star, in order of each star

        Returns
        -------
        KDTree
        scipy KDTree of all the x-y coordinates all stars

        """
        # build once and only once
        logging.debug(
            f"Building KD tree with xs and ys of shape: {len(xs)}, {len(ys)} "
        )
        xs = xs.astype(np.int32())
        ys = ys.astype(np.int32())
        xy_coords = np.column_stack((xs, ys))
        logging.debug("x-y coords stacked")
        kd_tree = KDTree(xy_coords)
        logging.debug("KD tree built and cached")
        return kd_tree
