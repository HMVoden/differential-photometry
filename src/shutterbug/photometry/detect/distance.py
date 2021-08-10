from typing import List, Tuple

import numpy as np
import numpy.typing as npt
import xarray as xr
from scipy.spatial import KDTree
from shutterbug.photometry.detect.detect import DetectBase


class DistanceDetector(DetectBase):
    tree: KDTree
    stars: xr.DataArray

    def __init__(self, ds: xr.Dataset, **kwargs):
        super().__init__(**kwargs)
        self.tree = self._build_kd_tree(ds["x"].values, ds["y"].values)
        self.stars = ds.star

    def detect(self, target_star: str) -> npt.NDArray[np.str_]:
        """Finds stars that are nearby target star, within radius tolerance, using a KDtree"""
        tree = self.tree
        radius = self.tolerance
        target = self.stars.sel(star=target_star)
        target_x = target["x"].values
        target_y = target["y"].values
        target_xy = np.column_stack((target_x, target_y))
        result_indices = tree.query_ball_point(x=target_xy, r=radius)
        result_stars = self.stars.isel(result_indices).values
        return result_stars

    def _build_kd_tree(
        self, xs: npt.NDArray[np.float64], ys: npt.NDArray[np.float64]
    ) -> KDTree:
        """Makes a KDtree from the x-y coordinates of each star

        Parameters
        ----------
        x : npt.NDArray[np.float64]
        x-coordinates for each star, in order of each star
        y : npt.NDArray[np.float64]
        y-coordinates of each star, in order of each star

        Returns
        -------
        KDTree
        scipy KDTree of all the x-y coordinates all stars

        """
        # build once and only once
        xy_coords = np.column_stack((xs, ys))
        kd_tree = KDTree(xy_coords)
        return kd_tree
