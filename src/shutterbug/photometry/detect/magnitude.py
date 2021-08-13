from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import xarray as xr
from shutterbug.photometry.detect.detect import DetectBase


@dataclass
class MagnitudeDetector(DetectBase):

    star_medians: xr.DataArray

    def __init__(self, ds, **kwargs):
        super().__init__(**kwargs)
        self.star_medians = ds["mag"].groupby("star").median(...)

    def detect(self, target_star: str) -> npt.NDArray[np.str_]:
        """Locates all stars that are less than (brighter) a target star's median
        magnitude plus a tolerance

            Parameters
            ----------
            ds : xr.Dataset
                Already cleaned dataset
            tolerance : float
                The amount to add to a star's median
            target : str
                Target star's name

            Returns
            -------
            npt.NDArray
                Numpy array of all the star's names that this found

        """
        tolerance = self.tolerance
        medians = self.star_medians
        target_median = medians.sel(star=target_star).values
        target_median_plus_tolerance = target_median + tolerance
        result_stars = medians.where(
            medians <= target_median_plus_tolerance, drop=True
        ).star.values
        return result_stars
